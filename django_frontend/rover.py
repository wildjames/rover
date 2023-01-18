import logging
from datetime import datetime
from time import time

import requests
from auth_middleware import token_required
from flask import Flask, Response, render_template, request

logging.basicConfig(
    filename="/home/rover/log/rover_flask.log",
    filemode="a",
    format="[%(asctime)s] %(levelname)-8s    %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)

controller_address_base = "http://localhost:1001/{}"

# Flask app setup
app = Flask(__name__)

# system configuration information gathering
system_state = requests.get(controller_address_base.format("system_info")).json()
num_leds = system_state["led_data"]["num_leds"]


@app.route("/")
def index():
    # Get LED status
    system_state = requests.get(controller_address_base.format("system_info")).json()
    led_states = system_state["led_data"]["led_states"]
    leds = [state[1] for state in led_states]

    template_data = {
        "title": "Rover Server",
        "time": datetime.now().ctime(),
    }

    for led, led_state in enumerate(leds):
        name = "led{}".format(led)
        template_data[name] = led_state

    return render_template("index.html", **template_data)


@app.route("/system_info")
# @token_required
def system_info():
    """Returns a JSON object containing system information."""

    logging.debug(f"Rover received system info request. Headers: \n{request.headers}")

    system_state = requests.get(controller_address_base.format("system_info")).json()
    return system_state


@app.route("/led_control", methods=["POST"])
# @token_required
def led_control():
    """Set the LED states to the defined states in the request JSON

    Request JSON format:
    {
        "states": list of pairs, (index, state)
    }

    Response JSON format:
    {
        "message": "success" | "failure"
    }
    """
    data = request.json
    logging.debug(f"Rover received LED command: {data}")

    led_command = data["states"]

    t0 = time()
    response = requests.post(
        controller_address_base.format("led_command"), json=led_command
    ).json()
    t1 = time()
    logging.info(
        "Rover sent LED command and received response in {:.0f} ms".format(
            (t1 - t0) * 1000.0
        )
    )

    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, use_reloader=False, threaded=True, debug=False)
