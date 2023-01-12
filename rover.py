from flask import Flask, render_template, request
from datetime import datetime
import paho.mqtt.client as mqtt


# MQTT setup
mqtt_broker = "localhost"
mqtt_port = 1883

# GPIO setup
num_leds = 3
# State is only modified when an MQTT message is recieved. Otherwise, it should be read-only.
state = {"leds": [0] * num_leds}

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client: mqtt.Client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for topic in state.keys():
        client.subscribe(topic)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Recieved message.\n    Topic [{}] -> {}".format(msg.topic, msg.payload))
    global state

    state[msg.topic] = msg.payload


# Create the client
client = mqtt.Client("GPIO Interface")

client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port)

# Flask app setup
app = Flask(__name__)


@app.route("/")
def index():
    # Get LED status
    # This should be read via a subscription to the rover's rabbitMQ broker
    leds = state["leds"]

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

    if not led.isnumeric():
        return {"message": "Invalid LED index"}
    led = int(led)
    if (led >= num_leds) or (led < 0):
        return {"message": "Invalid LED index"}

    new_led_state = new_led_state.lower()
    if new_led_state not in ["on", "off"] or new_led_state.isnumeric():
        return {"message": "Invalid LED state"}

    if new_led_state == "on":
        new_led_state = 1
    elif new_led_state == "off":
        new_led_state = 0

    # Send request to change state here
    # This should be sent via a publish to the rover's MQTT broker
    new_state = state["leds"]
    new_state[data["led"]] = new_led_state
    client.publish("leds", new_state)

    return {"message": "success", "state": state}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
