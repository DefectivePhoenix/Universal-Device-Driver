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
    data = {}
    with open(FILEPATH, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data[row[COLUMN_KEY]] = row
    return data

# Create the event handler
my_event_handler = PatternMatchingEventHandler(["*.csv"], None, False, True)

# Define the Observer
go_recursively = False
my_observer = Observer()
my_observer.schedule(my_event_handler, FILEPATH, recursive=go_recursively)

# Start the Observer
my_observer.start()

# Create the TCP server to listen for incoming connections
server = socketserver.TCPServer((UDDIP, UDDPORT), DataTransmissionHandler)
print(f"-- Server started on {UDDIP}:{UDDPORT}")

try:
    # Run the server indefinitely
    server.serve_forever()
except KeyboardInterrupt:
    # Stop the Observer and server when interrupted
    my_observer.stop()
    my_observer.join()
    server.shutdown()
