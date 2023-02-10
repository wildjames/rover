import logging

logger = logging.getLogger(__name__)

import time
import serial
import threading
from typing import List, Dict, Any


# motor_controller_address = "/dev/ttyACM0"
motor_controller_address = "/dev/ttyACM0"
motor_controller_baudrate = 115200

motor_conn = None
motor_listener_thread = None
stop_listener = False

MOTOR_KEYS = ["fr"]

motor_actual_speeds = [0] * len(MOTOR_KEYS)
motor_target_speeds = [0] * len(MOTOR_KEYS)
motor_throttles = [0] * len(MOTOR_KEYS)


def watch_motor_responses():
    """Listen to, and parse, messages from the motor controller"""

    if motor_conn is None or stop_listener:
        return

    try:
        response = motor_conn.readline().decode("utf-8")
        logger.info(f"Motor: {response}")
        # TODO: Do something with this

    except Exception as e:
        logger.error(f"Error reading motor controller response: {e}")
    
    threading.Timer(interval=0.1, target=watch_motor_responses).start()


def init_motor_controller():
    """Initialize the serial connection to the motor controller"""

    global motor_conn
    global motor_listener_thread
    global stop_listener

    logger.info(f"Initializing motor controller on serial address: {motor_controller_address}")

    motor_conn = serial.Serial(motor_controller_address, motor_controller_baudrate)

    logger.info("OK")

    # Check if the connection is open
    if not motor_conn.is_open:
        return {"message": "Motor controller connection failed"}

    # Open a watchdog that will parse incoming data from the motor controller
    motor_listener_thread = threading.Timer(interval=0.1, target=watch_motor_responses)
    motor_listener_thread.daemon = True

    # Ensure it doesn't immediately terminate
    stop_listener = False
    motor_listener_thread.start()

    return {"message": "Motor controller communication initialized"}


def close_motor_controller():
    """Close the serial connection to the motor controller"""

    global motor_conn
    global motor_listener_thread
    global stop_listener

    logger.info("Closing motor controller")

    if motor_conn is None:
        return {"message": "Motor controller not initialized"}

    if not motor_conn.is_open:
        return {"message": "Motor controller connection already closed"}

    # Kill the listener thread
    stop_listener = True

    motor_conn.close()
    motor_conn = None

    return {"message": "Motor controller connection closed"}


def set_motor_speed(payload: Dict[str, Any]):
    """Set the throttle for the motors"""

    if motor_conn is None:
        return {"message": "Motor controller not initialized"}

    if not motor_conn.is_open:
        return {"message": "Motor controller connection failed"}

    cmd = ""
    for key, value in payload.items():
        if key not in MOTOR_KEYS:
            continue

        cmd += f"{MOTOR_KEYS.index(key)}:{value}&"

    motor_conn.write(cmd.encode("utf-8"))

    return {"message": "Motor speed set"}


def execute_command(data: Dict[str, Any]):
    """Execute a command for the motors. Takes a dict with two keys:
        - command: The command to execute.
        - payload: The payload for the command.

    Returns a response message for the command, something like:
        {
            "command": str,
            "message": str,
        }

    Command options:

    - init_motors: Initialize the motors, using the set configuration.
        Structure:
        {
            "command": "init_motors",
        }

    - close_motors: Close the serial connection to the motor controller
        Structure:
        {
            "command": "close_motors",
        }

    - set_motor_throttle: Set the throttle for the motors.
        Structure:
        {
            "command": "set_speed",
            "payload": {
                "fr": <speed, cm/s>,
            },
        }

    """

    command = data["command"]
    payload = data.get("payload", {})

    logger.info(f"Executing motor command: {command}")
    logger.info(f"Payload: {payload}")

    if command == "init_motors":
        status = init_motor_controller()
        status["command"] = command
        return status

    elif command == "close_motors":
        status = close_motor_controller()
        status["command"] = command
        return status

    elif command == "set_speed":
        status = set_motor_speed(payload)
        status["command"] = command
        return status

    else:
        return {"command": command, "message": "Unknown command"}
