from flask import Flask, render_template, request
from datetime import datetime


num_leds = 3


# Flask app setup
app = Flask(__name__)

@app.route("/")
def index():
    # Get LED status
	# This should be read via a subscription to the rover's rabbitMQ broker
    leds = [0, 1, 1]

    templateData = {
        "title": "Rover Server",
        "time": datetime.now().ctime(),
    }

    for led, state in enumerate(leds):
        name = "led{}".format(led)
        templateData[name] = state

    return render_template("index.html", **templateData)


@app.route("/led_control", methods=["POST"])
def led_instruction():
    """Recieves a JSON packet in the request form, with two keys: an LED index (1-indexed), and a state to set it to."""
    data = request.get_json()

    led = data["led"]
    state = data["state"]

    if (led >= num_leds) or (led < 0) or (not led.isnumeric()):
        return {"message": "Invalid LED index"}

    state = state.lower()
    if state not in ["on", "off"] or state.isnumeric():
        return {"message": "Invalid LED state"}

    if state == "on":
        state = 1
    elif state == "off":
        state = 0

    # Send request to change state here
	# This should be sent via a publish to the rover's MQTT broker

    return {"message": "success"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
