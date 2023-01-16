import logging
import cv2

camera = cv2.VideoCapture(0)
logging.info("Camera initialized? {}".format(camera.isOpened()))


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

