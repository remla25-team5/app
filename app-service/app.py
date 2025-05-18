import os

import requests
from flasgger import Swagger
from flask import Flask, request, send_from_directory, jsonify
from lib_version.version_util import VersionUtil

app = Flask(__name__, static_folder="dist", static_url_path="")
swagger = Swagger(app)

APP_SERVICE_HOST = os.getenv('APP_SERVICE_HOST', '0.0.0.0')
APP_SERVICE_PORT = os.getenv('APP_SERVICE_PORT', '8080')
MODEL_SERVICE_HOST = os.getenv('MODEL_SERVICE_HOST', '0.0.0.0')
MODEL_SERVICE_PORT = os.getenv('MODEL_SERVICE_PORT', '5000')

# Fix URL construction to handle both formats with and without protocol
if MODEL_SERVICE_HOST.startswith('http://') or MODEL_SERVICE_HOST.startswith('https://'):
    MODEL_URL = f"{MODEL_SERVICE_HOST}:{MODEL_SERVICE_PORT}"
else:
    MODEL_URL = f"http://{MODEL_SERVICE_HOST}:{MODEL_SERVICE_PORT}"

in_memory_data = {}
submission_id_counter = 0


# /submit  - POST frontend sends a string, receives back a boolean (negative/positive) + submissionId
# /verify - POST frontend sends submissionId + if the sentiment rating was correct or not
# /version/app - GET the version of the app (app-frontend and app-service)
# /version/model - GET the version of the model-service

@app.route('/')
def index():
    # Serve the index.html from the dist folder
    return send_from_directory(os.path.join(app.static_folder), 'index.html')


@app.route('/api/submit', methods=['POST'])
def submit():
    """
    Submit a string for sentiment analysis
    ---
    parameters:
      - name: text
        in: body
        required: true
        type: string
        description: The text to analyze
    responses:
        200:
            description: A JSON object with the sentiment and submissionId
            schema:
            type: object
            properties:
                sentiment:
                type: boolean
                enum: [true, false]
                submissionId:
                type: string
        500:
            description: Failed to analyze sentiment
            schema:
            type: object
            properties:
                error:
                type: string
                description: Error message
        """
    try:
        # Retrieve JSON data from the request
        data = request.get_json()

        # Check if 'text' exists in the incoming data
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' in request data"}), 400

        text = data['text']

        # Generate a new submission ID
        global submission_id_counter
        submission_id = str(submission_id_counter)
        submission_id_counter += 1

        # Prepare the payload to send to the model service
        headers = {"Content-Type": "application/json"}
        payload = {"text": text}

        # Make the request to the sentiment analysis service
        try:
            response = requests.post(MODEL_URL + "/predict", headers=headers, json=payload)
            response.raise_for_status()  # Will raise an error for non-2xx responses

            # Attempt to extract the sentiment from the response
            sentiment = response.json().get('sentiment')

            # Check if the sentiment key exists
            if sentiment is None:
                return jsonify({"error": "Sentiment not found in response"}), 500

            # Return the sentiment and the submission ID
            return jsonify({"sentiment": sentiment, "submissionId": submission_id}), 200

        except requests.exceptions.RequestException as e:
            # Handle request-related errors (e.g., network issues, timeouts, 5xx errors)
            app.logger.error(f"Error when calling sentiment analysis service: {e}")
            return jsonify({"error": f"Failed to analyze sentiment: {str(e)}"}), 500

    except Exception as e:
        # Handle any general errors, such as issues with the incoming JSON or other unexpected errors
        app.logger.error(f"Error processing request: {e}")
        return jsonify({"error": "An error occurred while processing the request"}), 500


@app.route('/api/verify', methods=['POST'])
def verify():
    """
    Verify the sentiment analysis result
    ---
    parameters:
      - name: submissionId
        in: body
        required: true
        type: string
        description: The submission ID to verify
      - name: isCorrect
        in: body
        required: true
        type: boolean
        description: Whether the sentiment analysis result was correct or not
    responses:
        200:
            description: A JSON object with the verification result
            schema:
            type: object
            properties:
                verified:
                type: boolean
        """
    try:
        data = request.get_json()

        # Check if 'submissionId' and 'isCorrect' are in the JSON payload
        if 'submissionId' not in data or 'isCorrect' not in data:
            return jsonify({"error": "Missing 'submissionId' or 'isCorrect' in request data"}), 400

        submission_id = data['submissionId']
        correct = data['isCorrect']

        # Store the verification result in memory
        in_memory_data[submission_id] = correct

        return jsonify({"verified": True}), 200

    except Exception as e:
        # Catch any general errors and return a 500 server error with the error message
        app.logger.error(f"Error processing request: {e}")
        return jsonify({"error": "An error occurred while processing the request"}), 500


@app.route('/api/version/app', methods=['GET'])
def version_app():
    """
    Get the version of the app
    ---
    responses:
        200:
            description: A JSON object with the version of the app
            schema:
            type: object
            properties:
                version:
                type: string
        """
    version = VersionUtil.get_version()
    return {"version": version}, 200


@app.route('/api/version/model', methods=['GET'])
def version_model():
    """
    Get the version of the model
    ---
    responses:
        200:
            description: A JSON object with the version of the model
            schema:
            type: object
            properties:
                version:
                type: string
        """
    try:
        response = requests.get(MODEL_URL + "/version")
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)

        if response.status_code == 200:
            version = response.json().get('version')
            return jsonify({"version": version}), 200

    except requests.exceptions.RequestException as e:
        # Catch any requests-related exception (timeouts, network errors, etc.)
        app.logger.error(f"Error while fetching model version: {e}")
        return jsonify({"error": f"Failed to get model version: {str(e)}"}), 500


app.run(host=APP_SERVICE_HOST, port=int(APP_SERVICE_PORT), debug=True)
