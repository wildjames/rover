import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
from time import sleep
import json


# MQTT setup
mqtt_broker = "localhost"
mqtt_port = 1883

topics = ["led_command"]

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client: mqtt.Client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for topic in topics:
        client.subscribe(topic, 2)
        print(f"   Subscribed to {topic}")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Recieved message.\n    Topic [{}] -> {}".format(msg.topic, msg.payload))

    topic = msg.topic

    if topic == "led_command":
        states = json.loads(msg.payload)

        print("States: {}".format(states))
        for index, state in enumerate(states):
            set_led_state(index, state)


client = mqtt.Client("GPIO Interface")

client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port)


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


if __name__ in "__main__":
    # Test that LED control works as expected
    for led in leds:
        set_led_state(led, 0)

    client.loop_start()
    while True:
        states = get_led_state()
        payload = json.dumps(states)
        client.publish("led_state", payload)
        sleep(0.05)
