import logging

logger = logging.getLogger(__name__)

import gpiozero
import os
import threading
from datetime import datetime
import psutil
import requests

LOGFILE = "/home/rover/rover/rover_environment.log"
LOG_INTERVAL = 60
LOG_PURGE_INTERVAL = 60 * 60 * 24 * 7  # 1 week
LOG_THREAD: threading.Thread = None

UPLOAD_ADDRESS = "http://wildjames.com/rover/receive_data"
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

    with open(LOGFILE, "a") as f:
        # Gather data
        f.write(
            "temperature,{},{}\n".format(
                datetime.isoformat(), gpiozero.CPUTemperature().temperature
            )
        )
        f.write("cpu_usage,{},{}\n".format(datetime.isoformat(), psutil.cpu_percent()))
        f.write(
            "memory_usage,{},{}\n".format(
                datetime.isoformat(), psutil.virtual_memory().percent
            )
        )

    # Schedule the next run
    if LOG_THREAD is not None:
        logger.debug("Existing log thread found. Cancelling.")
        LOG_THREAD.cancel()

    LOG_THREAD = threading.Timer(LOG_INTERVAL, log_environment)
    LOG_THREAD.start()


def upload_logs():
    """Upload the logs file to the base station."""
    global UPLOAD_THREAD

    logger.debug("Uploading environment logs file to base station.")
    # The logs get pushed to the base station as a single file.
    # The base station will then parse the file and store it in a database.
    resp = requests.post(UPLOAD_ADDRESS, files={"file": open(LOGFILE, "rb")})

    # Schedule the next run
    if UPLOAD_THREAD is not None:
        logger.debug("Existing upload thread found. Cancelling.")
        UPLOAD_THREAD.cancel()

    UPLOAD_THREAD = threading.Timer(UPLOAD_INTERVAL, upload_logs)
    UPLOAD_THREAD.start()