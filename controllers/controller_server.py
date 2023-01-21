import logging
from typing import List

import led_control
# import motor_control

from flask import Flask, request


logging.basicConfig(
    filename="/home/rover/log/rover_controller.log",
    filemode="a",
    format="[%(asctime)s] %(levelname)-8s    %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)

# Flask app setup
app = Flask(__name__)

# Motor setup
ESC_pins = [18]
motors: List[motor_control.ESCController] = []


@app.route("/ping", methods=["GET"])
def ping():
    """Returns a JSON object containing a message."""
    logging.info("Received ping request")
    return {"message": "pong"}


@app.route("/system_info", methods=["GET"])
def system_info():
    """Returns a JSON object containing system information."""

    info_dict = {
        "led_data": {
            "num_leds": len(led_control.leds),
            "led_states": led_control.get_led_state(),
        }
    }

    logging.info("Returning system info: {}".format(info_dict))

    return info_dict


@app.route("/motor_init", methods=["POST"])
def motor_init():
    global motors

    for pin in ESC_pins:
        # Create an ESC object to control the ESC on pin 18.
        esc = motor_control.ESCController(pin)

        # Start the ESC.
        esc.start()

        motors.append(esc)


@app.route("/motor_command", methods=["POST"])
def motor_command():
    global motors
    
    req_obj = request.json

    logging.info("Received motor command pairs (index, state): {}".format(req_obj))

    for index, state in req_obj:
        if not motors[index]:
            return {"message": "failure: Motor index {} does not exist".format(index)}
        
        if state < 0.0 or state > 1.0:
            return {"message": "failure: motor state must be between 0.0 and 1.0"}
    
    for index, state in req_obj:
        motors[index].set_speed(state)

    return {"message": "success"}


@app.route("/led_command", methods=["POST"])
def led_command():
    req_obj = request.json

    logging.info("Received LED command pairs (index, state): {}".format(req_obj))

    for led, state in req_obj:
        if not led_control.set_led_state(led, state):
            return {"message": "failure: Controller could not set LED state"}

    return {"message": "success"}


if __name__ in "__main__":
    app.run(host="localhost", port=8001, use_reloader=True, threaded=False, debug=True)
