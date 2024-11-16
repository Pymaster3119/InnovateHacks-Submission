// Check if browser supports speech recognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

// Enable continuous recognition and interim results
recognition.continuous = true;
recognition.interimResults = true;

const voiceBtn = document.getElementById("voiceBtn");
const voiceTextbox = document.getElementById("voiceTextbox");

let isListening = false; // Tracks if recognition is active
let finalTranscript = ''; // Store final transcript

// Toggle speech recognition on button click
voiceBtn.addEventListener("click", () => {
    if (isListening) {
        recognition.stop();
        voiceBtn.textContent = "Start Voice Input";
        isListening = false;
    } else {
        recognition.start();
        voiceBtn.textContent = "Stop Voice Input";
        isListening = true;
    }
});

// Handle speech recognition result
recognition.onresult = (event) => {
    let interimTranscript = ''; // Temporarily store interim results

    // Loop through the results
    for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
            // Append final result to finalTranscript
            finalTranscript += event.results[i][0].transcript + ' ';
        } else {
            // Append interim results to interimTranscript
            interimTranscript += event.results[i][0].transcript;
        }
    }

    // Display both final and interim transcripts, but keep finalTranscript intact
    voiceTextbox.value = finalTranscript + interimTranscript;
};

// Error handling
recognition.onerror = (event) => {
    console.error("Speech recognition error detected: " + event.error);
};

// Function to refresh the image every 5 seconds
function refreshImage() {
    const timestamp = new Date().getTime(); // Cache-busting timestamp
    webPortal.src = `/result.png?t=${timestamp}`;
}

// Refresh the image every 5 seconds
setInterval(refreshImage, 1000);

let lastModifiedTime = null; // Variable to store the last modified time

// Function to check if messages.txt has changed
function hasMessagesChanged() {
    const timestamp = new Date().getTime(); // Cache-busting timestamp to avoid fetching cached results
    return fetch(`messages.txt?t=${timestamp}`, { method: 'HEAD' }) // Use 'HEAD' to get metadata
        .then(response => {
            const newModifiedTime = new Date(response.headers.get('Last-Modified')).getTime();

            // Check if this is the first call or if the file has been updated since the last call
            if (!lastModifiedTime || newModifiedTime > lastModifiedTime) {
                lastModifiedTime = newModifiedTime; // Update the stored modified time
                return true; // File has been changed
            }
            return false; // No changes
        })
        .catch(error => {
            console.error("Error checking messages.txt:", error);
            return false; // In case of error, assume no change
        });
}

const conversationLog = document.getElementById("conversationLog");

let lastModified = null; // Variable to store the last modified time

// Function to check if messages.txt has changed
function hasMessagesChanged() {
    const timestamp = new Date().getTime(); // Cache-busting timestamp to avoid fetching cached results
    return fetch(`messages.txt?t=${timestamp}`, { method: 'HEAD' }) // Use 'HEAD' to get metadata
        .then(response => {
            const newModifiedTime = new Date(response.headers.get('Last-Modified')).getTime();

            // Check if this is the first call or if the file has been updated since the last call
            if (!lastModifiedTime || newModifiedTime > lastModifiedTime) {
                lastModifiedTime = newModifiedTime; // Update the stored modified time
                return true; // File has been changed
            }
            return false; // No changes
        })
        .catch(error => {
            console.error("Error checking messages.txt:", error);
            return false; // In case of error, assume no change
        });
}

function refreshConversation() {
    if (hasMessagesChanged())
    {
        const timestamp = new Date().getTime(); // Use a timestamp to prevent caching

        fetch(`conversation.txt?t=${timestamp}`) // Append timestamp to avoid caching
            .then(response => response.text())
            .then(data => {
                try {
                    // Clear previous messages
                    conversationLog.innerHTML = '';

                    // Split the data by line and parse each line as JSON
                    const messages = data.split('\n').map(line => {
                        try {
                            return JSON.parse(line);
                        } catch (e) {
                            return null; // Ignore invalid JSON lines
                        }
                    }).filter(msg => msg !== null); // Filter out any null values

                    // Create message elements
                    messages.forEach(msg => {
                        const messageDiv = document.createElement('div');
                        messageDiv.classList.add('message');

                        if (msg.role === 'user') {
                            messageDiv.classList.add('user-message');
                        } else if (msg.role === 'assistant') {
                            messageDiv.classList.add('assistant-message');
                        } else if (msg.role == 'interjection') {
                            messageDiv.classList.add('inter-message');
                        }

                        // messageDiv.textContent = JSON.stringify(msg.content).replaceAll('"',''); // Set the message content
                        const messageContent = JSON.stringify(msg.content).replaceAll('"',"").split('<br>').map(line => {
                            const lineElement = document.createElement('p');
                            lineElement.textContent = line; // Add the message text
                            return lineElement;
                        });

                        // Append each part of the message as a new line
                        messageContent.forEach(lineElement => messageDiv.appendChild(lineElement));

                        // Append the messageDiv to the conversationLog
                        conversationLog.appendChild(messageDiv); // Append to the log
                    });
                } catch (error) {
                    console.error("Error processing conversation log: " + error);
                }
            })
            .catch(error => console.error("Error fetching conversation log: " + error));
        conversationLog.scroll({
            top: conversationLog.scrollHeight,
            behavior: 'smooth'
        });
    }
}

// Refresh the conversation log every second
setInterval(refreshConversation, 1000);

// Get reference to the send button
const sendBtn = document.getElementById("sendBtn");

// Add event listener for the send button
sendBtn.addEventListener("click", () => {
    const contentToWrite = document.getElementById("voiceTextbox").value;

    // Simulate the file write using fetch to the action.txt file
    fetch("/action.txt", {
        method: "POST",  // Typically POST is used to send data to a server
        headers: {
            "Content-Type": "text/plain"
        },
        body: contentToWrite   // The content to be sent to action.txt
    })
    .then(response => {
        if (response.ok) {
            console.log("Successfully sent the prompt to action.txt");
        } else {
            console.error("Failed to send the prompt to action.txt");
        }
    })
    .catch(error => console.error("Error during fetch: ", error));
    document.getElementById("voiceTextbox").value = "";
});

const resetBtn = document.getElementById("resetBtn");

    resetBtn.addEventListener("click", () => {
    const timestamp = new Date().getTime(); // Use a timestamp to prevent caching

    fetch(`reset.txt?t=${timestamp}`);
})