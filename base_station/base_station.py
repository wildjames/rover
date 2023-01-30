import logging

logger = logging.getLogger(__name__)


from typing import Dict

from flask import Flask, render_template, request
from flask_cors import CORS
import os


logger.info("Loading flask script")

# Flask app setup
app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/receive_data", methods=["POST"])
def receive_data():
    """Recieve an uploaded log file and save it to the server."""
    logger.info("Received a request: {}".format(request))
    file = request.get_data()

    # The file is uploaded using the request.files dictionary
    logger.info("Received file: {}".format(file))

    return "OK"
