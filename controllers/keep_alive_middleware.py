import logging
logger = logging.getLogger(__name__)


from functools import wraps
import time

import threading


# Time in seconds to go to sleep after inactivity.
SLEEP_THRESHOLD = 30

last_message = time.time()


def keep_alive(f):
    """When the call is triggered, update the last activity to the current time."""
    @wraps(f)
    def decorated(*args, **kwargs):
        global last_message
        
        delta_time = time.time() - last_message
        logger.debug("It has been {:.3f} seconds since the last message".format(delta_time))
        last_message = time.time()

        return f(*args, **kwargs)

    return decorated


def check_inactivity():
    """Check how long its been since the last activity. 
    If it's been more than SLEEP_THRESHOLD seconds, send the computer to sleep."""
    delta_time = time.time() - last_message
    
    logger.info("Checking last activity... It has been {:.3f} seconds.")
    if delta_time > SLEEP_THRESHOLD:
        logger.warning("I NEED TO SLEEP")
    
    threading.Timer(10, check_inactivity).start()
