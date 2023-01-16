import json
import logging

import camera_control
import cv2
import led_control
from flask import Flask, Response, render_template, request


logging.basicConfig(
    filename="/home/rover/log/rover_controller.log",
    filemode="a",
    format="[%(asctime)s] %(levelname)-8s    %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)

camera = cv2.VideoCapture(0)
logging.info("Camera initialized? {}".format(camera.isOpened()))

# Flask app setup
app = Flask(__name__)

def gen_frames():
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


@app.route("/video_feed")
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    # Hook into openCV to get the camera feed
    logging.info("Rover received video feed request")
    return Response(
        camera_control.gen_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/led_command", methods=["POST"])
def led_command():
    req_obj = json.loads(request.json)

    logging.info("Received LED command pairs (index, state): {}".format(req_obj))

    for led, state in req_obj:
        if not led_control.set_led_state(led, state):
            return {"message": "failure"}

    return {"message": "success"}


@app.route("/system_info", methods=["GET"])
def system_info():
    """Returns a JSON object containing system information."""

    info_dict = {
        "led_data": {
            "num_leds": len(led_control.leds),
            "led_states": led_control.get_led_state(),
        }
    }

    logging.info("Returning system info: {}".format(info_dict))

    return info_dict


if __name__ in "__main__":
    app.run(host="roverpi.local", port=1001, debug=False, reloader=False)
