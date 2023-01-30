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
