# super-geni
A gpt for homework. The user can upload images &amp; pdf.



# Flask Chat Application with JavaScript Integration

This project is a Flask-based chat application that integrates with a JavaScript script for various functionalities. The Flask application serves as a chat interface, allowing users to interact with the chat, upload files, and receive responses from an AI model. The JavaScript script handles client-side actions such as image capturing, message display, and file uploads.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Flask App](#flask-app)
  - [Installation](#installation)
  - [Usage](#usage)
- [JavaScript Script](#javascript-script)
  - [Functions](#functions)
- [Contributing](#contributing)
- [Author](#author)
- [License](#license)

---

## Prerequisites

Before you begin, ensure you have the following prerequisites:

- Python 3.x
- pip
- Virtual environment (recommended)
- A web browser with JavaScript support
- Access to the Flask Chat Application

---

## Flask App

### Installation

1. Clone the Flask Chat Application repository to your local machine:

   ```bash
   git clone https://github.com/sebastianaldrin/super-geni.git
   cd your-repo
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```

4. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:

   - Create a `.env` file in the project directory.
   - Add the following environment variables with your API keys and configuration:

   ```dotenv
   FLASK_SECRET_KEY=your_secret_key_here
   OPENAI_API_KEY= 'your api-key'
   PORT=5000
   ```

6. Run the Flask application:

   ```bash
   python app.py
   ```

### Usage

1. Access the chat interface by visiting `http://localhost:5000` in your web browser.

2. Interact with the chat interface, send messages, and upload images or PDF files for text extraction.

3. The application integrates with the OpenAI API for conversation responses.

---

## JavaScript Script

### Functions

- `scrollToBottom()`: Scrolls the chatbox to the bottom.

- `captureImage()`: Captures an image from the video stream.

- `accessCamera()`: Creates a camera overlay with a "Coming soon" message and close button.

- `startVideo()`: Starts the video stream.

- `stopVideo()`: Stops the video stream.

- `showVideo()`: Makes the video element visible.

- `hideVideo()`: Hides the video element.

- `appendMessage(message)`: Appends a message to the chatbox.

- `sendUserMessage(messageContent)`: Sends a user message to the server.

- `handleFileUpload()`: Handles file uploads asynchronously.

- `resetChat()`: Resets the chat.

---

## TODO
Split the code, make it easier to read.
Clean up the code.
Websockets are not working correctly, the page refreshes when sending messages.
The camera button is supposed to open the camera where the user can take a picture of the homework and then upload it, flask extracts the text and sends it to chatgpt.

---

## Contributing

Contributions to this project are welcome! If you have improvements, bug fixes, or new features to contribute to either the Flask App or the JavaScript script, please feel free to contribute by opening a pull request or submitting an issue.

---

## Author

- Sebastian Aldrin, Sweden

---

## License

This project is provided under the MIT License. See the [LICENSE](LICENSE) file for details.
