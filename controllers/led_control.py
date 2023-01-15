import RPi.GPIO as GPIO
from time import sleep
import json
from bottle import run, post, get, request, response


# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# LED Pin definition
leds = [17, 27, 22]

for pin in leds:
    GPIO.setup(pin, GPIO.OUT)


def set_led_state(index, state):
    """Sets the state of the LED at the given index."""
    if index >= len(leds):
        return
    GPIO.output(leds[index], state)


def get_led_state():
    """Returns a list of the states of all LEDs."""
    led_states = [GPIO.input(led) for led in leds]
    return led_states


@post("/led_command")
def my_process():
    req_obj = json.loads(request.json)

    # do something with req_obj
    print(req_obj)

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

    run(host="localhost", port=1001, debug=True)
