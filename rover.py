from flask import Flask, render_template, request
from datetime import datetime
from flask_mqtt import Mqtt
import json
import logging

logging.basicConfig(filename="/home/rover/rover_app.log", level=logging.DEBUG)

# MQTT setup
mqtt_broker = "localhost"
mqtt_port = 1883

# GPIO setup
num_leds = 3
# State is only modified when an MQTT message is recieved. Otherwise, it should be read-only.
state = {"led_state": [0] * num_leds}


# Flask app setup
app = Flask(__name__)

# Set up the MQTT client
client = Mqtt(app, mqtt_logging=True)
app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''  # Set this item when you need to verify username and password
app.config['MQTT_PASSWORD'] = ''  # Set this item when you need to verify username and password
app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
app.config['MQTT_TLS_ENABLED'] = False  # If your server supports TLS, set it True
app.config['MQTT_REFRESH_TIME'] = 0.1  # refresh time in seconds


# The callback for when the client receives a CONNACK response from the server.
@client.on_connect()
def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for topic in state.keys():
        client.subscribe(topic, 2)


# The callback for when a PUBLISH message is received from the server.
@client.on_message()
def on_message(client, userdata, message):
    logging.info("Recieved message.\n    Topic [{}] -> {}".format(message.topic, message.payload))
    
    global state
    state[message.topic] = json.loads(message.payload)


@app.route("/")
def index():
    # Get LED status
    # This should be read via a subscription to the rover's rabbitMQ broker
    leds = state["led_state"]

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

    logging.debug("Recieved data: {}".format(data))

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

    # Send request to change state here
    # This should be sent via a publish to the rover's MQTT broker
    modified_state = state["led_state"]
    modified_state[data["led"]] = new_led_state
    
    payload = json.dumps(modified_state)
    logging.info("Publishing payload: {}".format(payload))

    client.publish("led_command", payload)

    return {"message": "success", "state": state}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, use_reloader=False, debug=True)
