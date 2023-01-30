import logging

logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
from typing import Dict

from flask import Flask, render_template, request
from flask_cors import CORS
import os

LOGLOCATION = "/home/pi/rover/log/rover_environment_{}.log"

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

    time = datetime.now()
    monday = time - timedelta(days=time.weekday())
    weekstring = monday.strftime("%Y-%m-%d")
    filename = LOGLOCATION.format(weekstring)

    # The file is transmitted using open(filename, "rb") on the client side.
    logger.debug("Appending recieved file to local logs")
    with open(filename, "a", encoding="utf-8") as f:
        f.write(file.decode("utf-8"))

    # Then, since the file will contain many duplicate entries, it is sorted and duplicates are removed.
    logger.debug("Removing duplicates from local logs")
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    lines = list(set(lines))

    logger.debug("Sorting by timestamp")
    lines = [l.split(",") for l in lines]
    lines.sort(key=lambda x: x[1])

    logger.debug("Saving local logs")
    with open(filename, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(",".join(line))

    logger.debug("OK")

    return "OK"
