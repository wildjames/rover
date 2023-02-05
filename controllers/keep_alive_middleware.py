import logging

logger = logging.getLogger(__name__)

from shutdown import shutdown
from functools import wraps
import time

import threading


# Time in seconds to go to sleep after inactivity.
SLEEP_THRESHOLD = 300
# Enable variable
ENABLE_SLEEP = True

# This will track which thread is the next timer.
SLEEP_THREAD = None

last_message = time.time()


def keep_alive(f):
    """When the call is triggered, update the last activity to the current time."""

    @wraps(f)
    def decorated(*args, **kwargs):
        global last_message
        logger.debug("Recieved a message that registers as keepalive activity.")
        last_message = time.time()
        return f(*args, **kwargs)

    return decorated


def check_inactivity():
    """Check how long its been since the last activity.
    If it's been more than SLEEP_THRESHOLD seconds, send the computer to sleep."""
    global last_message
    global SLEEP_THREAD

    delta_time = time.time() - last_message

    logger.info(
        "Checking last activity...")
    logger.info("It has been {:.3f} seconds since a command".format(
            delta_time
        )
    )
    logger.info("My inactivity threshold is {:.1f} seconds".format(SLEEP_THRESHOLD))
    logger.info("My enable_sleep variable is {}".format(ENABLE_SLEEP))

    if delta_time > SLEEP_THRESHOLD:
        logger.critical("Inactivity threshold reached.")
        if ENABLE_SLEEP:
            shutdown()

        else:
            last_message = time.time() - 10
            delta_time = time.time() - last_message
            logger.critical(
                "Would have sent the computer to sleep. Set last message time to {:.3f} seconds ago.".format(
                    delta_time
                )
            )

    # Add 10 seconds to the earliest time I would sleep.
    time_to_next_check = (SLEEP_THRESHOLD - delta_time) + 10
    logger.info(
        "Will check for inactivity again in {:.3f} seconds".format(time_to_next_check)
    )

    if SLEEP_THREAD is not None:
        SLEEP_THREAD.cancel()

    SLEEP_THREAD = threading.Timer(time_to_next_check, check_inactivity)
    SLEEP_THREAD.daemon = True
    SLEEP_THREAD.start()
