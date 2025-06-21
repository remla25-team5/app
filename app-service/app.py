import os

import requests
from flasgger import Swagger
from flask import Flask, make_response, request, send_from_directory, jsonify
from lib_version.version_util import VersionUtil
import time
from prometheus_client import Gauge, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from flask import Response
from collections import deque

app = Flask(__name__, static_folder="dist", static_url_path="")
swagger = Swagger(app)

APP_SERVICE_HOST = os.getenv('APP_SERVICE_HOST', '0.0.0.0')
APP_SERVICE_PORT = os.getenv('APP_SERVICE_PORT', '8080')
MODEL_SERVICE_HOST = os.getenv('MODEL_SERVICE_HOST', '0.0.0.0')
MODEL_SERVICE_PORT = os.getenv('MODEL_SERVICE_PORT', '5000')
CURRENT_APP_VERSION = os.getenv('APP_VERSION', 'v1')
COOKIE_NAME = "app-version-preference"


# Fix URL construction to handle both formats with and without protocol
if MODEL_SERVICE_HOST.startswith('http://') or MODEL_SERVICE_HOST.startswith('https://'):
    MODEL_URL = f"{MODEL_SERVICE_HOST}:{MODEL_SERVICE_PORT}"
else:
    MODEL_URL = f"http://{MODEL_SERVICE_HOST}:{MODEL_SERVICE_PORT}"

in_memory_data = {}
submission_id_counter = 0

# Metrics
active_submissions_gauge = Gauge(
    'active_submissions',
    'Number of active submissions not yet verified (model-predicted sentiment)',
    ['sentiment']
)

total_submissions_counter = Counter(
    'total_submissions',
    'Total number of submissions received (model-predicted sentiment)',
    ['sentiment']
)

submission_timestamps = {}

submission_verification_delay_seconds = Histogram(
    'submission_verification_delay_seconds',
    'Time between submission and verification',
    ['verified', 'sentiment'],
    buckets=[1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0, float("inf")]
)

# Track active submission IDs to avoid double decrement
active_submission_ids = set()

# Store (timestamp, is_correct) for recent verifications
recent_verifications = deque(maxlen=1000)  # Adjust maxlen as needed
ROLLING_WINDOW_SECONDS = 604800  # 1 week

verification_error_rate_gauge = Gauge(
    'verification_error_rate_last_week',
    'Percentage of incorrect verifications in the last week'
)

# ML Test Score: Monitor 7: The model has not experienced a regression in prediction quality on served data
def update_verification_error_rate():
    """
    Update the verification error rate based on recent verifications.
    This function calculates the error rate over a rolling window of the last week.
    """
    now = time.time()
    # Remove old entries
    while recent_verifications and recent_verifications[0][0] < now - ROLLING_WINDOW_SECONDS:
        recent_verifications.popleft()
    if not recent_verifications:
        verification_error_rate_gauge.set(0)
        return
    total = len(recent_verifications)
    incorrect = sum(1 for t, is_correct in recent_verifications if not is_correct)
    error_rate = incorrect / total
    verification_error_rate_gauge.set(error_rate)

@app.route('/metrics')
def metrics():
    # Expose Prometheus metrics
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/')
def index():
    # Serve the index.html from the dist folder
    response = make_response(send_from_directory(os.path.join(app.static_folder), 'index.html'))
    response.set_cookie(COOKIE_NAME, 
                        value=CURRENT_APP_VERSION, 
                        path='/',      
                        httponly=False, 
                        samesite='Lax'  
                       ) 
    return response


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
    global submission_id_counter

    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' in request data"}), 400

        text = data['text']

        submission_id = str(submission_id_counter)
        submission_id_counter += 1
        submission_timestamps[submission_id] = time.time()

        # Call model service
        headers = {"Content-Type": "application/json"}
        payload = {"text": text}
        response = requests.post(MODEL_URL + "/predict", headers=headers, json=payload)
        response.raise_for_status()
        sentiment = response.json().get('sentiment')
        if sentiment is None:
            return jsonify({"error": "Sentiment not found in response"}), 500

        # sentiment = True if submission_id_counter % 2 == 0 else False

        sentiment_label = str(sentiment).lower()
        in_memory_data[submission_id] = {
            'sentiment': sentiment_label
        }
        total_submissions_counter.labels(sentiment=sentiment_label).inc()
        active_submissions_gauge.labels(sentiment=sentiment_label).inc()
        active_submission_ids.add(submission_id)

        return jsonify({"sentiment": sentiment, "submissionId": submission_id}), 200

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error when calling sentiment analysis service: {e}")
        return jsonify({"error": f"Failed to analyze sentiment: {str(e)}"}), 500

    except Exception as e:
        app.logger.error(f"Error processing request: {e}")
        return jsonify({"error": "An error occurred while processing the request"}), 500

# Fixed

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
        if 'submissionId' not in data or 'isCorrect' not in data:
            return jsonify({"error": "Missing 'submissionId' or 'isCorrect' in request data"}), 400

        submission_id = data['submissionId']
        correct = data['isCorrect']

        # Lookup sentiment associated with this submission
        sentiment_label = in_memory_data.get(submission_id, {}).get('sentiment')
        if not sentiment_label:
            return jsonify({"error": "Sentiment data missing for submission"}), 400

        # Update in-memory store (optional, for logging or audit)
        in_memory_data[submission_id]['verified'] = correct

        # Track verification outcome
        recent_verifications.append((time.time(), correct))
        update_verification_error_rate()

        # Decrement active submissions gauge
        if submission_id in active_submission_ids:
            active_submissions_gauge.labels(sentiment=sentiment_label).dec()
            active_submission_ids.remove(submission_id)

        # Record delay histogram
        created_time = submission_timestamps.pop(submission_id, None)
        if created_time is not None:
            delay = time.time() - created_time
            submission_verification_delay_seconds.labels(
                verified=str(correct), sentiment=sentiment_label
            ).observe(delay)

        return jsonify({"verified": True}), 200

    except Exception as e:
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
        return None

    except requests.exceptions.RequestException as e:
        # Catch any requests-related exception (timeouts, network errors, etc.)
        app.logger.error(f"Error while fetching model version: {e}")
        return jsonify({"error": f"Failed to get model version: {str(e)}"}), 500

@app.route('/api/version/app-release', methods=['GET'])
def version_app_release():
    """
    Get distinction between main release (v1) and feature release (v2) of the app-service
    ---
    responses:
        200:
            description: A JSON object with the release version
            schema:
            type: object
            properties:
                release:
                type: string
    """
    return {"release": CURRENT_APP_VERSION}, 200

app.run(host=APP_SERVICE_HOST, port=int(APP_SERVICE_PORT), debug=True)