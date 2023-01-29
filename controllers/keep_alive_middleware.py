import logging
logger = logging.getLogger(__name__)


from functools import wraps
import time

import threading


# Time in seconds to go to sleep after inactivity.
SLEEP_THRESHOLD = 300
# Enable variable
ENABLE_SLEEP = True

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
    global last_message

    delta_time = time.time() - last_message
    time_to_next_check = SLEEP_THRESHOLD - delta_time

    logger.info("Checking last activity... It has been {:.3f} seconds since a command".format(delta_time))
    if delta_time > SLEEP_THRESHOLD:
        if ENABLE_SLEEP:
            # Easy way
            from subprocess import call
            call("sudo shutdown -P now", shell=True)
        else:
            logger.info("Would have sent the computer to sleep")
            last_message = time.time()
            
        # TODO: Send a signal to the sleepypi to shutdown the raspberry pi.

    logger.info("Will check for inactivity again in {:.3f} seconds".format(time_to_next_check))
    
    threading.Timer(time_to_next_check, check_inactivity).start()
