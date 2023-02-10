import logging

logger = logging.getLogger(__name__)

import time
import serial
import threading
from typing import List, Dict, Any


# motor_controller_address = "/dev/ttyACM0"
motor_controller_address = "/dev/tty.usbmodem1101"
motor_controller_baudrate = 115200

motor_conn = None

MOTOR_KEYS = ["fr", "fl", "br", "bl"]


def watch_motor_responses():
    if motor_conn is None:
        return

    while motor_conn.is_open:
        try:
            response = motor_conn.readline().decode("utf-8")
            print(f"Motor controller response: {response}")
            # TODO: Do something with this

        except Exception as e:
            logger.error(f"Error reading motor controller response: {e}")
            break


def init_motor_controller():
    """Initialize the motor controller"""

    global motor_conn

    logger.info("Initializing motor controller")

    motor_conn = serial.Serial(motor_controller_address, motor_controller_baudrate)

    # Wait for the motor controller to boot up
    time.sleep(2)

    # Check if the connection is open
    if not motor_conn.is_open:
        return {"message": "Motor controller connection failed"}

    # Open a watchdog that will parse incoming data from the motor controller
    threading.Thread(target=watch_motor_responses).start()

    return {"message": "Motor controller communication initialized"}


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
            "payload:" ["fr", "fl", "br", "bl"],
        }

    - set_motor_config: Set the configuration for the motors.
        Structure:
        {
            "command": "set_motor_config",
            "payload": {
                "fr": {...},
            },
        }

    - set_motor_throttle: Set the throttle for the motors.
        Structure:
        {
            "command": "set_motor_throttle",
            "payload": {
                "fr": 0.5,
            },
        }

    """

    command = data["command"]
    payload = data.get("payload", {})

    if command == "init_motors":
        status = init_motor_controller()
        status["command"] = command
        return status

    elif command == "set_speed":
        status = set_motor_speed(payload)
        status["command"] = command
        return status

    else:
        return {"command": command, "message": "Unknown command"}
