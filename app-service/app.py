import os

import requests
from flasgger import Swagger
from flask import Flask, request
from lib_version.version_util import VersionUtil

app = Flask(__name__)
swagger = Swagger(app)

HOST = os.getenv('HOST', '0.0.0.0')
PORT = os.getenv('PORT', '8080')
MODEL_URL = os.getenv('MODEL_URL', 'http://model-service:8080')

IN_MEMORY_DATA = {}
submission_id_counter = 0


# /submit  - POST frontend sends a string, receives back a boolean (negative/positive) + submissionId
# /verify - POST frontend sends submissionId + if the sentiment rating was correct or not
# /version/app - GET the version of the app (app-frontend and app-service)
# /version/model - GET the version of the model-service

@app.route('/')
def index():
    # make it nicer with HTML
    # center it!
    return_html = """
    <html>
    <head>
        <title>Sentiment Analysis Service</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 20px;
            }
            h1 {
                color: #333;
            }
            p {
                color: #555;
            }
            a {
                color: #007BFF;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            </style>
            </head>
            <body>
            <div style="text-align: center;background-color: linear-gradient(to right, pink, orange, pink);">
            <h1>Sentiment Analysis Service</h1>
            <p>Welcome to the Sentiment Analysis Service!</p>
            <p>Use the following endpoints:</p>
            <ul>
                <li><a href="/version/app">App Version</a></li>
                <li><a href="/version/model">Model Version</a></li>
                <li><a href="/submit">Submit Text for Analysis</a></li>
                <li><a href="/verify">Verify Sentiment Analysis</a></li>
            </ul>
            <p>Powered by Flask and Swagger.</p>
            </div>
            </body>
            </html>
    """
    return return_html


@app.route('/submit', methods=['POST'])
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
    data = request.get_json()
    text = data['text']

    global submission_id_counter
    submission_id = str(submission_id_counter)
    submission_id_counter += 1

    # get sentiment analysis from REST api from a different service
    headers = {"Content-Type": "application/json"}
    payload = {"text": text}
    response = requests.post(MODEL_URL + "/predict", headers=headers, json=payload)

    if response.status_code == 200:
        sentiment = response.json().get('sentiment')
        return {"sentiment": sentiment, "submissionId": submission_id}, 200

    return {"error": "Failed to analyze sentiment"}, 500


@app.route('/verify', methods=['POST'])
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
      - name: correct
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
    data = request.get_json()
    submission_id = data['submissionId']
    correct = data['correct']

    IN_MEMORY_DATA[submission_id] = correct

    return {"verified": True}, 200


@app.route('/version/app', methods=['GET'])
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


@app.route('/version/model', methods=['GET'])
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
    response = requests.get(MODEL_URL + "/version")

    if response.status_code == 200:
        version = response.json().get('version')
        return {"version": version}, 200

    return {"error": "Failed to get model version"}, 500


app.run(host=HOST, port=int(PORT), debug=True)
