import json
import logging

import RPi.GPIO as GPIO
from bottle import get, post, request, response, run


logging.basicConfig(
    filename="/home/rover/log/led_controller.log",
    filemode="a",
    format="[%(asctime)s] %(levelname)-8s    %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)


# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# LED Pin definition
leds = [17, 27, 22]

# Set up the pins
for pin in leds:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)
    logging.info("Set up pin {} as GPIO.OUT".format(pin))


def set_led_state(index, state):
    """Sets the state of the LED at the given index."""
    if index >= len(leds):
        return False
    retval = GPIO.output(leds[index], state)
    logging.debug("Set LED {} to state {}".format(index, state))
    return retval


def get_led_state():
    """Returns a list of the states of all LEDs."""
    led_states = [(i, GPIO.input(led)) for i, led in enumerate(leds)]
    logging.debug("Got current LED states: {}".format(led_states))
    return led_states
