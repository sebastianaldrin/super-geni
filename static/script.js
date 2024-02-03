document.addEventListener("DOMContentLoaded", () => {
    const chatbox = document.getElementById("chatbox");
    const errorContainer = document.getElementById("error-container");
    const loadingMessage = "Uploading file..."; // Message for the loading animation
    let lastMessageId = 0;
    let isExtractionInProgress = false; // Flag to prevent multiple extractions

    // To hide the video element
    const videoElement = document.getElementById('videoElement');
    hideVideo();

// Function to scroll to the bottom of the chatbox
    function scrollToBottom() {
        const chatbox = document.getElementById('chatbox'); // Replace 'chatbox' with the actual ID of your chatbox element
        chatbox.scrollTop = chatbox.scrollHeight - chatbox.clientHeight;
    }

// Call the scrollToBottom function when the page is refreshed
    window.onload = scrollToBottom;

    document.getElementById('camera').addEventListener('click', accessCamera);

    // Add an event listener to the "Take Picture" button
    const takePictureButton = document.getElementById('captureButton');
    takePictureButton.addEventListener('click', captureImage);

    // Camera elements
    const video = document.getElementById('videoElement');
    const canvas = document.getElementById('canvasElement');
    const uploadButton = document.getElementById('uploadButton');
    // Welcome message
    const welcomeMessage = [
        "Welcome to Teacher - Your School Learning Assistant!",
        "",
        "How to Use Teacher for School Teaching and Homework:",
        "",
        "1. Ask School-Related Questions: Whether you're stuck on a math problem, need help with a science concept, or have questions about your history assignment, just ask Teacher. It's here to assist with your schoolwork.",
        "",
        "2. Homework Help: If you have specific homework questions, provide details about the assignment or question, and Teacher will guide you through the solution step-by-step.",
        "",
        "3. Specify the Subject: Mention the subject you need help with in your query. For instance, say, 'I need help with my English essay,' or 'Explain the Pythagorean theorem in math.'",
        "",
        "4. Study Tips: Ask for study tips or strategies to help you prepare for tests and exams.",
        "",
        "5. Practice Problems: Request practice problems or exercises to reinforce your understanding of a topic.",
        "",
        "6. Clarify Your Doubts: If an explanation is unclear, ask Teacher to clarify or rephrase it. Learning is all about understanding."
    ].join("\n");
    let stream = null;

    // Function to capture an image
    function captureImage() {
        // Ensure the video stream is still playing
        if (video.srcObject) {
            // Create a canvas element to capture the image
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const context = canvas.getContext('2d');


            // Draw the current frame from the video onto the canvas
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            // Create an image element to display the captured image
            const capturedImage = new Image();
            capturedImage.src = canvas.toDataURL('image/png'); // You can specify the format ('image/jpeg', 'image/png', etc.)

            // Append the captured image to the DOM or process it as needed
            // For example, you can display it in a specific container
            const imageContainer = document.getElementById('capturedImageContainer');
            imageContainer.appendChild(capturedImage);
        }
    }

// Function to access the camera and create an overlay with "Coming soon" message and close button
    function accessCamera() {
        // Create a camera overlay container
        const overlayContainer = document.createElement('div');
        overlayContainer.id = 'camera-overlay-container';
        overlayContainer.style.position = 'fixed';
        overlayContainer.style.top = '0';
        overlayContainer.style.left = '0';
        overlayContainer.style.width = '100%';
        overlayContainer.style.height = '100%';
        overlayContainer.style.zIndex = '3';

        // Create the camera overlay
        const overlay = document.createElement('div');
        overlay.id = 'camera-overlay';
        overlay.style.position = 'relative';
        overlay.style.width = '300px'; // Set the width of the overlay box as needed
        overlay.style.padding = '20px';
        overlay.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
        overlay.style.borderRadius = '10px';
        overlay.style.margin = '0 auto';
        overlay.style.top = '50%';
        overlay.style.transform = 'translateY(-50%)';
        overlay.style.textAlign = 'center';

        // Append the "Coming soon" message to the overlay
        const comingSoonMessage = document.createElement('div');
        comingSoonMessage.textContent = 'Coming soon\n';
        overlay.appendChild(comingSoonMessage);

        // Create a close button
        const closeButton = document.createElement('button');
        closeButton.textContent = 'Close';
        closeButton.style.marginTop = '10px'; // Adjust the margin as needed
        closeButton.addEventListener('click', function () {
            document.body.removeChild(overlayContainer);
        });
        overlay.appendChild(closeButton);

        // Append the overlay to the container
        overlayContainer.appendChild(overlay);

        // Append the container to the body
        document.body.appendChild(overlayContainer);
    }



    // Function to start the video and make it visible
    function startVideo() {
        if (navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(function (mediaStream) {
                    videoElement.srcObject = mediaStream;
                    videoElement.style.display = 'block'; // Show the video element
                    videoElement.play();
                })
                .catch(function (error) {
                    console.log("Error accessing the camera: ", error);
                });
        }
    }


    function stopVideo() {
        const stream = videoElement.srcObject;
        if (stream) {
            const tracks = stream.getTracks();
            console.log("Number of tracks to stop:", tracks.length);
            tracks.forEach(track => {
                console.log("Stopping track:", track);
                track.stop();
            });
            videoElement.srcObject = null;
            videoElement.style.display = 'none'; // Hide the video element
            console.log("Video stopped and hidden.");
        }
    }


    // Function to show the video element
    function showVideo() {
        videoElement.style.display = 'block';
        videoElement.style.width = '100%';  // Set the width to occupy the full width
        videoElement.style.height = '100%'; // Set the height to occupy the full height
        videoElement.style.zIndex = '2';
    }

    // Function to hide the video element
    function hideVideo() {
        videoElement.style.display = 'none';
        videoElement.style.width = '0';     // Set the width to zero
        videoElement.style.height = '0';    // Set the height to zero
        videoElement.style.zIndex = '0';    // Set z-index to zero
    }

    // Capture the image
    takePictureButton.addEventListener('click', function () {
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
        video.style.display = 'none';
        canvas.style.display = 'block';
        takePictureButton.style.display = 'none';
        uploadButton.style.display = 'block';
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }

        // Remove the overlay if it exists
        const overlay = document.getElementById('camera-overlay');
        if (overlay) {
            document.body.removeChild(overlay);
            hideVideo();
            stopVideo();
        }
    });

    // Function to append a message to the chatbox
    // Upload stops working when changing this code to use socket.IO
    function appendMessage(message) {
        const messageElement = document.createElement("div");
        messageElement.className = `message ${message.role}-message`;
        const contentParagraph = document.createElement("p");
        contentParagraph.textContent = message.content;
        messageElement.appendChild(contentParagraph);
        chatbox.appendChild(messageElement);

        // Scroll to the bottom only if the message is from the assistant
        if (message.role === "assistant") {
            scrollToBottom();
        }
    }

    // Function to send a user message
    async function sendUserMessage(messageContent) {
        try {
            const response = await fetch("/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ user_input: messageContent }),
            });

            if (!response.ok) {
                throw new Error("Failed to send user message");
            }

            const responseData = await response.json();

            if (responseData && responseData.chat_history) {
                responseData.chat_history.forEach(message => {
                    if (message.id > lastMessageId) {
                        appendMessage(message);
                        lastMessageId = message.id;
                    }
                });
                errorContainer.textContent = "";
                scrollToBottom();
            } else {
                errorContainer.textContent = "Invalid server response format.";
            }
        } catch (error) {
            errorContainer.textContent = `Error: ${error.message}`;
        }
    }

    // Function to handle file upload asynchronously using AJAX
    async function handleFileUpload() {
        if (isExtractionInProgress) {
            return;
        }

        isExtractionInProgress = true;
        const formData = new FormData();
        const fileInput = document.getElementById("file");

        if (fileInput && fileInput.files.length > 0) {
            formData.append("file", fileInput.files[0]);
        }

        chatbox.innerHTML += `<div class="message system-message">${loadingMessage}</div>`;

        try {
            const response = await fetch("/upload_file", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Failed to upload file");
            }

            const responseData = await response.json();

            if (responseData && responseData.extracted_text) {
                // Handle the extracted text as needed
                const extractedText = responseData.extracted_text;
                // If you want to do something with the extracted text, do it here
                await sendUserMessage(extractedText);
                // Wait for 5 seconds before reloading the page
                setTimeout(() => {
                    location.reload();
                }, 5000); // 5000 milliseconds = 5 seconds
            } else {
                errorContainer.textContent = "No extracted text received from the server."
            }
        } catch (error) {
            errorContainer.textContent = `Error: ${error.message}`;
        } finally {
            isExtractionInProgress = false;
        }
    }

    // Function to reset the chat
    async function resetChat() {
        try {
            const response = await fetch("/clear_session_history", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                throw new Error("Failed to clear session history");
            }

            // Clear the chatbox by removing all its child elements
            chatbox.innerHTML = '';
            lastMessageId = 0;

            // Display a welcome message after resetting
            appendMessage({ role: "model", content: "Welcome! Ask me anything related to school learning or upload your homework." });
            scrollToBottom();
        } catch (error) {
            errorContainer.textContent = `Error: ${error.message}`;
        }
    }

    // Add event listeners
    document.getElementById("upload-file-btn").addEventListener("click", () => {
        // Trigger the file input when the label is clicked
        document.getElementById("file").click();
    });

    document.getElementById("file").addEventListener("change", () => {
        // Automatically submit the file upload form when a file is selected
        handleFileUpload();
    });

    document.getElementById("reset-btn").addEventListener("click", resetChat);

    // Add an event listener to the "Send" button for text input
    document.getElementById("submit-text-btn").addEventListener("click", async () => {
        // Get the user's input from the input field
        const userInput = document.getElementById("user-input").value;

        // Call the function to send the user's message asynchronously
        await sendUserMessage(userInput);
    });
});
