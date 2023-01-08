from flask import Flask, render_template, request
from datetime import datetime
from mulitprocessing.connection import Listener


# Flask app setup
app = Flask(__name__)

@app.route("/")
def index():
	# Read Sensors Status
	

	templateData = {
		'title': 'Rover Server',
		"led1": led1_state,
		"led2": led2_state,
		"led3": led3_state,
		"time": datetime.now().ctime(),
	}

	return render_template('index.html', **templateData)

@app.route("/led_control", methods=["POST"])
def led_instruction():
	"""Recieves a JSON packet in the request form, with two keys: an LED index (1-indexed), and a state to set it to."""
	data = request.get_json()

	led = data["led"]
	state = data["state"]

	if not led in leds.keys():
		return {"message": "Invalid LED index"}

	state = state.lower()
	if state not in ["on", "off"] or state.isnumeric():
		return {"message": "Invalid LED state"}

	if state == "on":
		state = 1
	elif state == "off":
		state = 0

	# Send request to change state here
	

	return {"message": "success"}


if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)
