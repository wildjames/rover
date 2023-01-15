from flask import Flask, render_template, request
from datetime import datetime
import json
import requests
import logging

logging.basicConfig(filename="/home/rover/rover_app.log", level=logging.DEBUG)

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
    leds = [state[1] for state in sorted(led_states, key=lambda x: x[0])]

    templateData = {
        "title": "Rover Server",
        "time": datetime.now().ctime(),
    }

    for led, led_state in enumerate(leds):
        name = "led{}".format(led)
        templateData[name] = led_state

    return render_template("index.html", **templateData)


@app.route("/system_info")
def system_info():
    system_state = requests.get(controller_address_base.format("system_info")).json()
    return system_state


@app.route("/led_control", methods=["POST"])
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
    logging.debug("Rover received LED command:")
    logging.debug(data)

    led_command = data["states"]

    response = requests.post(
        controller_address_base.format("led_command"), json=led_command
    ).json()

    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, use_reloader=False, debug=True)
