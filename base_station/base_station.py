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
    data = request.get_json()
    logger.info("Received data: {}".format(data))
    
    # TODO: Write a script on the rover that will post updates to this endpoint.
    # Then, make sure it's logged to file.

    return "OK"
