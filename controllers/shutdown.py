import logging
logger = logging.getLogger(__name__)

# Easy way
from subprocess import call

def shutdown():
    logger.critical("Shutting down the computer.")
    call("sudo shutdown -P now", shell=True)


    # TODO: Send a signal to the sleepypi to shutdown the raspberry pi.
