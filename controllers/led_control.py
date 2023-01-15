import json
import logging
from time import sleep

import RPi.GPIO as GPIO
from bottle import get, post, request, response, run

logging.basicConfig(level=logging.DEBUG)

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
        return
    GPIO.output(leds[index], state)
    logging.debug("Set LED {} to state {}".format(index, state))


def get_led_state():
    """Returns a list of the states of all LEDs."""
    led_states = [GPIO.input(led) for led in leds]
    logging.debug("Got current LED states: {}".format(led_states))
    return led_states


@post("/led_command")
def my_process():
    req_obj = json.loads(request.json)
    data = json.loads(req_obj)
    print(data)
    print(type(data))

    logging.info("Received LED command pairs (index, state): {}".format(req_obj))
    logging.info("This is type: {}".format(type(req_obj)))
    for led, state in req_obj:
        set_led_state(led, state)

    return {"message": "success"}


@get("/system_info")
def system_info():
    """Returns a JSON object containing system information."""
    response.content_type = "application/json"

    info_dict = {
        "led_data": {
            "num_leds": len(leds),
            "led_states": get_led_state(),
        }
    }

    return info_dict


if __name__ in "__main__":
    # Test that LED control works as expected
    for led in leds:
        set_led_state(led, 0)

    run(host="localhost", port=1001, debug=True, reloader=True)
