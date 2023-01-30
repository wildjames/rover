import logging

logger = logging.getLogger(__name__)

import gpiozero
import os
import threading
from datetime import datetime
import psutil
import requests

LOGFILE = "/home/rover/log/rover_environment.log"
LOG_INTERVAL = 60
LOG_PURGE_INTERVAL = 60 * 60 * 24 * 7  # 1 week
LOG_THREAD: threading.Thread = None

UPLOAD_ADDRESS = "https://wildjames.com/base/receive_data"
UPLOAD_INTERVAL = 300  # seconds
UPLOAD_THREAD: threading.Thread = None


def log_environment():
    """Periodically gather data and log it to a file.

    The file should be of the format:
        <variablename>,<timestamp>,<value>
    """
    global LOG_THREAD

    if not os.path.exists(LOGFILE):
        with open(LOGFILE, "w") as f:
            f.write("variable,timestamp,value\n")

    logger.debug(f"Appending environment data to file: {LOGFILE}")
    with open(LOGFILE, "a") as f:
        # Gather data
        f.write(
            "temperature,{},{}\n".format(
                datetime.now().isoformat(), gpiozero.CPUTemperature().temperature
            )
        )
        f.write(
            "cpu_usage,{},{}\n".format(datetime.now().isoformat(), psutil.cpu_percent())
        )
        f.write(
            "memory_usage,{},{}\n".format(
                datetime.now().isoformat(), psutil.virtual_memory().percent
            )
        )
    logger.debug("Finished appending environment data to file.")

    LOG_THREAD = threading.Timer(LOG_INTERVAL, log_environment)
    LOG_THREAD.daemon = True
    LOG_THREAD.start()


def upload_logs():
    """Upload the logs file to the base station."""
    global UPLOAD_THREAD

    logger.debug("Uploading environment logs file to base station.")
    # The logs get pushed to the base station as a single file.
    # The base station will then parse the file and store it in a database.
    resp = requests.post(UPLOAD_ADDRESS, files={"file": open(LOGFILE, "rb")})
    logger.debug("Response from base station: {}".format(resp.text))

    UPLOAD_THREAD = threading.Timer(UPLOAD_INTERVAL, upload_logs)
    UPLOAD_THREAD.daemon = True
    UPLOAD_THREAD.start()
