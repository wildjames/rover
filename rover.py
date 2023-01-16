import json
import logging
from datetime import datetime
from time import time

import cv2
import requests
from auth_middleware import token_required
from flask import Flask, render_template, request, Response

logging.basicConfig(
    filename="/home/rover/log/rover_flask.log",
    filemode="a",
    format="[%(asctime)s] %(levelname)-8s    %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)

controller_address_base = "http://localhost:1001/{}"

# API token secret
with open("/home/rover/rover_api_token.txt", "r") as f:
    SECRET_KEY = f.read().strip()


# system configuration information gathering
system_state = requests.get(controller_address_base.format("system_info")).json()
num_leds = system_state["led_data"]["num_leds"]


# Flask app setup
app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY


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


def gen_frames(camera):
    """Video streaming generator function."""
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            logging.error("Rover failed to read camera frame")
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )  # concat


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    # Hook into openCV to get the camera feed
    camera = cv2.VideoCapture(0)
    logging.info("Camera initialized: {}".format(camera.isOpened()))
    logging.info("Rover received video feed request")
    return Response(gen_frames(camera), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/system_info")
# @token_required
def system_info():
    """Returns a JSON object containing system information."""

    logging.debug(f"Rover received system info request. Headers: \n{request.headers}")

    system_state = requests.get(controller_address_base.format("system_info")).json()
    return system_state


@app.route("/led_control", methods=["POST"])
@token_required
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
    data = json.loads(request.json)
    logging.debug(f"Rover received LED command: {data}")

    led_command = json.dumps(data["states"])

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
    app.run(host="0.0.0.0", port=80, use_reloader=True, threaded=True, debug=True)
