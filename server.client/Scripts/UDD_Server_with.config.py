import os
import csv
import configparser
import socketserver
import time
import json
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

# Read configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Get settings from the configuration file
UDDIP = config.get('Settings', 'UDDIP')
UDDPORT = int(config.get('Settings', 'UDDPORT'))
COLUMN_KEY = config.get('Settings', 'COLUMN_KEY')
FILEPATH = config.get('Settings', 'FILEPATH')

def get_newest_csv_file():
    # Get a list of CSV files in the directory
    csv_files = [file for file in os.listdir(FILEPATH) if file.endswith('.csv')]

    # Sort files by modification time and get the most recent CSV file
    newest_file = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(FILEPATH, f)))
    newest_file_path = os.path.join(FILEPATH, newest_file)
    return newest_file_path

FILENAME = get_newest_csv_file()

# Create a variable to store file modification time; this will be used while detecting real modification events
last_time_modified = 0

# Define any file name patterns using regex syntax to include or ignore
patterns = ["*"]
ignore_patterns = None
ignore_directories = False
case_sensitive = True

def process(header, value, record):
        key, other = header.partition('/')[::2]
        if other:
                process(other, value, record.setdefault(key, {}))
        else:
                record[key] = value

class DataTransmissionHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print(f"-- Connection established with {self.client_address}")
        fileData = file_reader()
        data = json.dumps(fileData)
        self.request.sendall(data.encode())
        print("-- Data sent")
        print("-- Closing connection")

def file_reader():
    time.sleep(.25)
    FilePath = FILENAME
    data = {}
    with open(FilePath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Choose a column to group the data 
            data[row[COLUMN_KEY]] = record = {}
            for header, value in row.items():
                process(header, value, record)
    return data

def on_created(event):
        global FILENAME
        FILENAME = get_newest_csv_file()
        print(f"-- {event.src_path} has been created")
        fileData = file_reader()
        print(fileData)

        # Update last modify time tracker
        global last_time_modified
        statbuf = os.stat(FILENAME)
        last_time_modified = statbuf.st_mtime
        
def on_deleted(event):
        print(f"-- {event.src_path} has been deleted")
 
def on_modified(event):
        global last_time_modified
        statbuf = os.stat(FILENAME)
        modify_time = statbuf.st_mtime
        # If the second modification event happens and the file modification time hasn't changed by more than .1 seconds, ignore it
        if (modify_time - last_time_modified) > 0.05:
                print(f"-- {event.src_path} has been modified")
                fileData = file_reader()
                print(fileData)
        # Update the global variable with the current file access time for comparison during the second unexpected modificiation event
        last_time_modified = modify_time

def on_moved(event):
        print(f"{event.src_path} has moved to {event.dest_path}")


# Create the TCP server to listen for incoming connections
server = socketserver.TCPServer((UDDIP, UDDPORT), DataTransmissionHandler)
print(f"-- Server started on {UDDIP}:{UDDPORT}")

# Create the event handler
my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_modified = on_modified
my_event_handler.on_moved = on_moved

# Define the Observer
go_recursively = True
my_observer = Observer()
my_observer.schedule(my_event_handler, FILEPATH, recursive=go_recursively)

# Start the Observer
my_observer.start()
time.sleep(.5)
print('')
print('Watching for file..')

try:
    # Run the server indefinitely
    server.serve_forever()
except KeyboardInterrupt:
    # Stop the Observer and server when interrupted
    my_observer.stop()
    my_observer.join()
    server.shutdown()