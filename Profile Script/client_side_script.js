// Establish WebSocket connection to your Python server
const socket = new WebSocket('ws://10.35.96.129:59580');

// Global variable for LoggingLevel tag address
const LOGGING_LEVEL_TAG_ADDRESS = "LoggingLevel";

// Handle connection open event
socket.addEventListener('open', function (event) {
    console.log('WebSocket connection established');
});

// Handle messages received from the server
socket.addEventListener('message', function (event) {
    const message = JSON.parse(event.data);
    console.log('Message from server:', message);
    // Handle the received data as needed
    processData(message);
});

// Handle connection close event
socket.addEventListener('close', function (event) {
    console.log('WebSocket connection closed');
});

// Handle connection error event
socket.addEventListener('error', function (event) {
    console.error('WebSocket error:', event);
});

// Function to process the received data
function processData(data) {
    // Implement your logic to process the received data here
    // For example:
    // if (data.type === 'Read') {
    //     // Handle read operation
    // } else if (data.type === 'Write') {
    //     // Handle write operation
    // }
}

// Function to send data to the server
function sendData(data) {
    // Convert data to JSON string
    const jsonData = JSON.stringify(data);
    // Send data to the server
    socket.send(jsonData);
}

// Function to update the LoggingLevel tag
function updateLoggingLevel(level) {
    const data = {
        address: LOGGING_LEVEL_TAG_ADDRESS,
        value: level
    };
    // Send data to update the LoggingLevel tag
    sendData(data);
}
