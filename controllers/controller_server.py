import json
import logging

import led_control
from bottle import get, post, request, response, run

logging.basicConfig(
    filename="/home/rover/log/rover_controller.log",
    filemode="a",
    format="[%(asctime)s] %(levelname)-8s    %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)


@post("/led_command")
def led_command():
    req_obj = json.loads(request.json)

    logging.info("Received LED command pairs (index, state): {}".format(req_obj))
    logging.info("This is type: {}".format(type(req_obj)))

    for led, state in req_obj:
        if not led_control.set_led_state(led, state):
            return {"message": "failure"}

    return {"message": "success"}


@get("/system_info")
def system_info():
    """Returns a JSON object containing system information."""
    response.content_type = "application/json"

    info_dict = {
        "led_data": {
            "num_leds": len(led_control.leds),
            "led_states": led_control.get_led_state(),
        }
    }

    logging.info("Returning system info: {}".format(info_dict))

    return info_dict


if __name__ in "__main__":
    run(host="localhost", port=1001, debug=True, reloader=True)
