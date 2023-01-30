import logging

logger = logging.getLogger(__name__)


from typing import Dict

from flask import Flask, render_template, request
from flask_cors import CORS
import os

LOGLOCATION = "/home/pi/rover/log/rover_environment.log"

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
    logger.info("Received log file update")
    file = request.get_data()

    # The file is uploaded using the request.files dictionary

    # The file is transmitted using open(filename, "rb") on the client side.
    # This means that the file is transmitted as a byte stream.
    # The file is received as a byte stream, and must be decoded.
    # The file is decoded using the utf-8 encoding.
    # The file is then saved to the server.
    logger.debug("Appending recieved file to local logs")
    with open(LOGLOCATION, "a", encoding="utf-8") as f:
        f.write(file.decode("utf-8"))

    # Then, since the file will contain many duplicate entries, it is sorted and duplicates are removed.
    logger.debug("Removing duplicates from local logs")
    with open(LOGLOCATION, "r", encoding="utf-8") as f:
        lines = [line.split(",") for line in f.readlines()]

    lines = list(set(lines))
    lines.sort(key=lambda x: x[1])

    logger.debug("Saving local logs")
    with open(LOGLOCATION, "w", encoding="utf-8") as f:
        f.writelines(lines)

    logger.debug("OK")

    return "OK"
