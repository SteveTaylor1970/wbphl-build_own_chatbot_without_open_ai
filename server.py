import logging
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import worker  # Import the worker module
import argparse
import logging


# Initialize Flask app and CORS
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.logger.setLevel(logging.ERROR)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the route for the index page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')  # Render the index.html template

# Define the route for processing messages
@app.route('/process-message', methods=['POST'])
def process_message_route():
    user_message = request.json['userMessage']  # Extract the user's message from the request
    print('user_message', user_message)

    bot_response = worker.process_prompt(user_message)  # Process the user's message using the worker module

    # Return the bot's response as JSON
    return jsonify({
        "botResponse": bot_response
    }), 200

# Define the route for processing documents
@app.route('/process-document', methods=['POST'])
def process_document_route():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({
            "botResponse": "It seems like the file was not uploaded correctly, can you try "
                           "again. If the problem persists, try using a different file"
        }), 400

    file = request.files['file']  # Extract the uploaded file from the request

    file_path = file.filename  # Define the path where the file will be saved
    file.save(file_path)  # Save the file

    worker.process_document(file_path)  # Process the document using the worker module

    # Return a success message as JSON
    return jsonify({
        "botResponse": "Thank you for providing your PDF document. I have analyzed it, so now you can ask me any "
                       "questions regarding it!"
    }), 200

# Run the Flask app
#if __name__ == "__main__":
#    app.run(debug=True, port=8000, host='0.0.0.0')

# python server.py --hf_api_key "your_hugging_face_api_key_here"
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the Chatbot Flask Server")
    parser.add_argument(
        "--hf_api_key", 
        type=str, 
        required=True, 
        help="Hugging Face API key"
    )
    args = parser.parse_args()

    # Initialize LLM with the provided API key
    worker.init_llm(hf_api_key=args.hf_api_key)
    logger.info("LLM and embeddings initialization complete.")

    # Start Flask application
    app.run(host="0.0.0.0", port=8010)