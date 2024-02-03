from flask import Flask, render_template, request, session, jsonify
from flask_session import Session
from PIL import Image
import os
import logging
from openai import OpenAI
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask import request
import pytesseract
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import fitz  # PyMuPDF

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=4)
loop = asyncio.get_event_loop()
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for all routes
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "your_secret_key_here")
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

# Initialize Flask-SocketIO
socketio = SocketIO(app, manage_session=False)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp'}

openai_api_key = os.environ.get("OPENAI_API_KEY", "your api-key here")
client = OpenAI(api_key=openai_api_key)

logging.basicConfig(filename='app.log', level=logging.ERROR)

# Reusable function for text extraction from an image
def extract_text_from_image(image):
    """Extract text from an image file and remove HTML tags."""
    try:
        text = pytesseract.image_to_string(image, lang='swe')
        return strip_html_tags(text)
    except Exception as e:
        return handle_extraction_error(e)

# Reusable function for text extraction from a PDF
def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file and remove HTML tags."""
    try:
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            text += page.get_text()
        pdf_document.close()
        return strip_html_tags(text)
    except Exception as e:
        return handle_extraction_error(e)

# Handle extraction errors
def handle_extraction_error(e):
    error_message = f"Error extracting text: {str(e)}"
    logging.error(error_message)
    print(error_message)  # Debugging statement
    return "An error occurred while processing the file."

# Define the strip_html_tags function
def strip_html_tags(text):
    """Remove HTML tags from a string using regex."""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


# Define the route for serving chat updates using Socket.IO
@socketio.on('get_new_messages')
def get_new_messages():
    user_sid = request.sid  # Get the unique session ID of the requester
    chat_history = session.get('chat_history', {})

    # Retrieve the chat history for the requesting user
    user_chat_history = chat_history.get(user_sid, [])

    # Emit the chat history to the requester
    emit('chat history', user_chat_history)

# Define an event for receiving new chat messages via Socket.IO
@socketio.on('chat message')
def handle_message(message):
    user_sid = request.sid  # Get the unique session ID of the sender
    chat_history = session.get('chat_history', {})

    # Append the new message to the user's chat history
    if user_sid in chat_history:
        chat_history[user_sid].append(message)
    else:
        chat_history[user_sid] = [message]

    session['chat_history'] = chat_history

    # Emit the new message back to the sender
    emit('chat message', message)

@app.route('/script.js')
def serve_javascript():
    # Replace this with the actual content of your JavaScript file
    javascript_content = 'console.log("Hello from JavaScript!");'

    # Create a Flask response with the JavaScript content and CORS headers
    response = app.make_response(javascript_content)

    # Set the Access-Control-Allow-Origin header to allow all origins
    response.headers['Access-Control-Allow-Origin'] = '*'

    return response


# Update the Flask route to match the route used in JavaScript
@app.route("/clear_session_history", methods=["POST"])
def clear_session_history():
    session.clear()  # Clear the entire session
    return jsonify({"message": "Chat session has been reset."})

@socketio.on('connect')
def handle_connect():
    # Handle new client connections here
    pass

def process_image_async(image):
    """Asynchronously extract text from an image file and remove HTML tags."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_in_executor(executor, partial(pytesseract.image_to_string, image, lang='swe'))
        text = loop.run_until_complete(result)
        return strip_html_tags(text)
    except Exception as e:
        error_message = f"Error extracting text from image: {e}"
        logging.error(error_message)
        print(error_message)  # Debugging statement
        return "An error occurred while processing the image."


@app.route("/capture_image", methods=["POST"])
def capture_image():
    try:
        uploaded_image = request.files.get("image")

        if uploaded_image:
            # Process the uploaded image here
            # You can use pytesseract or any other library to extract text from the image

            extracted_text = extract_text_from_image(uploaded_image)  # Implement this function to extract text

            if extracted_text:
                # Send the extracted text to ChatGPT or handle it as needed
                # Extend the conversation history, send to ChatGPT, and get a response

                # For demonstration purposes, let's return the extracted text
                return jsonify({"extracted_text": extracted_text})
            else:
                return jsonify({"error": "Text extraction failed."}), 400
        else:
            return jsonify({"error": "No image received."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Modified route for asynchronous file upload with asyncio
@app.route("/upload_file", methods=["POST"])
def upload_file():
    try:
        print("Handling file upload...")  # Debugging statement
        uploaded_file = request.files.get("file")

        if uploaded_file:
            print(f"Received file: {uploaded_file.filename}")  # Debugging statement
            filename = secure_filename(uploaded_file.filename)

            if uploaded_file.mimetype.startswith(('image', 'application/pdf')):
                if uploaded_file.mimetype.startswith('image'):
                    image = Image.open(uploaded_file)
                    extracted_text = process_image_async(image)
                elif uploaded_file.mimetype == 'application/pdf':
                    # Use extract_text_from_pdf directly for PDF files
                    extracted_text = extract_text_from_pdf(uploaded_file)
                else:
                    error_message = "Unsupported file type. Please upload an image (png, jpg, jpeg, gif) or a PDF file."
                    print(error_message)  # Debugging statement
                    return jsonify({"error": error_message}), 400

                try:
                    if extracted_text:
                        # Check if the extracted text has already been added to the chat_history
                        chat_history = session.get('chat_history', [])
                        last_message = chat_history[-1]['content'] if chat_history else ""

                        if extracted_text.strip() != last_message.strip():
                            # Append the extracted text as a message to the chat history
                            user_message = {"role": "user", "content": extracted_text}
                            chat_history.append(user_message)
                            session['chat_history'] = chat_history

                            # Update the last processed message
                            session['last_processed_message'] = extracted_text.strip()  # Update with stripped text

                            # Return only the extracted text as a JSON response
                            return jsonify(extracted_text=extracted_text)
                        else:
                            error_message = "This text has already been processed."
                            print(error_message)  # Debugging statement
                            return jsonify({"message": error_message}), 200
                except Exception as e:
                    error_message = f"Error processing extracted text: {str(e)}"
                    print(error_message)  # Debugging statement
                    return jsonify({"error": error_message})

            else:
                error_message = "Unsupported file type. Please upload an image (png, jpg, jpeg, gif) or a PDF file."
                print(error_message)  # Debugging statement
                return jsonify({"error": error_message}), 400
        else:
            print("No file received.")  # Debugging statement
            return jsonify({"error": "No file received."}), 400

    except Exception as e:
        error_message = f"Error processing file upload: {str(e)}"
        print(error_message)  # Debugging statement
        logging.error(f"Unhandled exception: {e}")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

    return jsonify({"error": "File processing failed."}), 400


# Define the route for the main chat page
@app.route("/", methods=["GET", "POST"])
def index():
    try:
        # Initialize chat_history from the user's session
        chat_history = session.get('chat_history', [])
        user_message = None  # Initialize user_message

        if request.method == "POST":
            uploaded_file = request.files.get("file")
            user_input = request.form.get("user_input")

            if uploaded_file and allowed_file(uploaded_file.filename):
                if uploaded_file.mimetype.startswith('image'):
                    image = Image.open(uploaded_file)
                    extracted_text = extract_text_from_image(image)
                elif uploaded_file.mimetype == 'application/pdf':
                    extracted_text = extract_text_from_pdf(uploaded_file)
                else:
                    error_message = "Unsupported file type. Please upload an image (png, jpg, jpeg, gif) or a PDF file."
                    print(error_message)  # Debugging statement
                    return error_message

                user_message = {"role": "user", "content": extracted_text}
                chat_history.append(user_message)
            elif user_input:
                user_message = {"role": "user", "content": user_input}
                chat_history.append(user_message)  # Append user's message

            conversation = [
                {"role": "system",
                 "content": ""},
            ]
            conversation.extend(chat_history)  # Append chat history to the conversation

            # Check if the extracted text is different from the last processed message
            last_processed_message = session.get('last_processed_message', "")
            if user_message is not None and user_message[
                "content"].strip() != last_processed_message.strip():  # Check for differences
                try:
                    # Append the user's message to the chat history
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo-1106",
                        messages=conversation,
                        max_tokens=512,
                        temperature=0.5,
                    )

                    # Append the model's response to the chat history with the correct role
                    model_response = {"role": "assistant", "content": response.choices[0].message.content}
                    chat_history.append(model_response)
                    session['chat_history'] = chat_history

                    # Update the last processed message
                    session['last_processed_message'] = user_message["content"].strip()  # Update with stripped text
                except Exception as e:
                    error_message = f"Error generating a response: {str(e)}"
                    print(error_message)  # Debugging statement
                    return jsonify({"error": error_message})
            else:
                # If the user's message is the same as the last processed message, do not generate a new response
                model_response = {"role": "assistant",
                                  "content": "Finns det något specifikt du skulle vilja att jag förklarar eller klargör angående den här filen?"}
                chat_history.append(model_response)
                session['chat_history'] = chat_history

        return render_template("chatbox.html", chat_history=chat_history)

    except Exception as e:
        error_message = f"Unhandled exception: {e}"
        print(error_message)  # Debugging statement
        logging.error(error_message)
        return "An unexpected error occurred. Please try again later."


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=os.environ.get("PORT", 5000))
