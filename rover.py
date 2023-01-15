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
    leds = system_state["led_data"]["led_states"]

    templateData = {
        "title": "Rover Server",
        "time": datetime.now().ctime(),
    }

    for led, led_state in enumerate(leds):
        name = "led{}".format(led)
        templateData[name] = led_state

    return render_template("index.html", **templateData)


@app.route("/led_control", methods=["POST"])
def led_instruction():
    """Recieves a JSON packet in the request form, with two keys: an LED index (1-indexed), and a state to set it to."""
    data = request.get_json()

    led = data["led"]
    new_led_state = data["state"]

    try:
        led = int(led)
    except:
        return {"message": "Invalid LED index"}

    if (led >= num_leds) or (led < 0):
        return {"message": "Invalid LED index"}

    if type(new_led_state) not in [int, float, bool]:
        logging.info("Invalid LED state: {} (type {})".format(new_led_state, type(new_led_state)))
        return {"message": "Invalid LED state"}

    logging.info("Altering led {} to state {}".format(led, new_led_state))
    state_pair = [(led, new_led_state)]

    payload = json.dumps(state_pair)
    logging.info("Publishing payload: {}".format(payload))

    response = requests.post(controller_address_base.format("led_command"), json=payload)

    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, use_reloader=False, debug=True)
