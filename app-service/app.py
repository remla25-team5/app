from flask import Flask, request
from flasgger import Swagger
from lib_version.version_util import VersionUtil

app = Flask(__name__)
swagger = Swagger(app)

@app.route("/", methods=["POST"])
def predict():
    """
    Submit some JSON data to be processed
    ---
    parameters:
        - name: input_data
          in: body
          description: JSON to be processed
    responses:
        200:
            description: Some processing output
    """
    msg = request.get_json()
    print(VersionUtil.get_version())
    return "Provided content was: " + str(msg)

app.run(host="0.0.0.0", port=8080, debug=True)