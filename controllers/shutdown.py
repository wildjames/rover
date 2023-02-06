import logging
logger = logging.getLogger(__name__)

# Easy way
from subprocess import call
import gpiozero


# The raspberry pi must send an "i'm alive" message by setting pin 25 to high.
logger.debug("Setting up the 'i'm alive' pin.")
isalive = gpiozero.DigitalOutputDevice(25, initial_value=True)


def shutdown():
    logger.critical("Shutting down the computer.")
    call("sudo shutdown -P now", shell=True)

