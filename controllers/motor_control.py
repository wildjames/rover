import logging

logger = logging.getLogger(__name__)

import time
import gpiozero
from typing import List, Dict, Any

# Interface for controlling an ESC (Electronic Speed Controller) using a Raspberry Pi
# and a PWM (Pulse Width Modulation) signal.

# Motor configuration
ESC_CONFIGURATIONS: Dict[str, Dict[str, Any]] = {
    # "fr": {
    #     "pin": 12,
    #     "min_pulse_width": 1000,
    #     "max_pulse_width": 2000,
    #     "start_now": True,
    #     "frequency": 50,
    # },
}

ESC_CONTROLLERS: Dict[str, "ESCController"] = {}


class ESCController:
    """Class for controlling an ESC using a Raspberry Pi and a PWM signal."""

    pin: int

    frequency: int = 50

    # Pulse width in microseconds
    min_pulse_width: int = 1000
    max_pulse_width: int = 2000

    armed: bool = True
    started: bool = False
    throttle: float = 0.0

    pwm: gpiozero.PWMOutputDevice = None

    def __init__(
        self,
        start_now=True,
    ):
        """The constructor for the ESC class.

        Frequency is the frequency of the PWM signal in Hz.
        min/max pulse width is the minimum and maximum pulse widths, in microseconds
        """

        if start_now:
            self.init()

    @property
    def min_pulse_width(self):
        return self._min_pulse_width

    @min_pulse_width.setter
    def min_pulse_width(self, value):
        self._min_pulse_width = self.frequency * value / 1000000

    @property
    def max_pulse_width(self):
        return self._max_pulse_width

    @max_pulse_width.setter
    def max_pulse_width(self, value):
        self._max_pulse_width = self.frequency * value / 1000000

    def init(self):
        """Initialize the ESC GPIO connection. Sets the throttle to zero."""
        logger.debug("Initializing ESC on pin {}".format(self.pin))
        if self.started:
            logger.warning("ESC already started, re-initialising!")
            self.close()

        self.pwm = gpiozero.PWMOutputDevice(
            self.pin, frequency=self.frequency, initial_value=0.0
        )
        self.started = True
        self.stop()

    def close(self):
        """Release the GPIO connection. Sets the throttle to zero first, then disables the PWM signal."""
        logger.debug(f"Closing ESC on pin {self.pin}")
        self.stop()
        self.pwm.off()
        self.pwm.close()
        self.started = False

    def calibrate(self):
        """Calibrate the ESC. Interactive, as it requires the user to disconnect and reconnect the battery.

        Should only be run once per hardware setup.
        """
        logger.critical("Disconnect the battery, hit enter when done")
        input("> ")

        logger.critical("Sending maximum pulse width")
        self.pwm.value = self.max_pulse_width

        logger.critical("Connect the battery, hit enter when done")
        input("> ")

        time.sleep(2)
        logger.critical("Sending minimum pulse width")
        self.pwm.value = self.min_pulse_width

        logger.critical("OK")

    def arm(self):
        """Start the ESC wakeup handshake. Sometimes seems un-necessary?

        Each step is separated by a 2 second delay:
            1. Set the pulse width to the minimum.
            2. Set the pulse width to the maximum.
            3. Set the pulse width to the minimum.

        After the handshake, the ESC will be ready to receive a throttle 0 signal.
        """
        logger.info("Arming ESC...")

        # Re-init, so we are in a known state.
        self.init()

        # Set the pulse width to the minimum.
        logger.info("Sending minimum pulse width")
        self.pwm.value = self.min_pulse_width
        time.sleep(3)

        # Set the pulse width to the maximum.
        logger.info("Sending maximum pulse width")
        self.pwm.value = self.max_pulse_width
        time.sleep(5)

        # Set the pulse width to the minimum
        logger.info("Sending minimum pulse width")
        self.pwm.value = self.min_pulse_width
        time.sleep(2)

        # Then we're done
        logger.info("ESC armed")
        self.armed = True
        self.stop()

    def stop(self):
        """Stop the motor, setting throttle to zero."""
        # Set the throttle to 0.
        self.set_speed(0)

    def estop(self):
        """Emergency stop the ESC. Bypass calculations, set PWM duty cycle to 0.

        Does not close connection to the ESC, so keeps reservation of the GPIO pin.
        """
        logger.info("Emergency stopping ESC")
        self.pwm.off()
        self.throttle = 0.0

    def set_speed(self, speed: float):
        """Set the speed of the ESC, as a fraction of the maximum speed.

        Cna only be called after ESCController.init() has been called."""
        if not self.started:
            logger.warning("Cannot set speed - ESC not started!")
            return

        # Set the pulse width to the given speed.
        pwm_value = (self.max_pulse_width - self.min_pulse_width) * speed
        pwm_value += self.min_pulse_width

        logger.info(
            "Setting ESC speed to {:.1f}% (duty cycle {:.3f})".format(
                speed * 100.0, pwm_value
            )
        )
        if not self.armed:
            logger.warn("ESC not armed!")

        self.pwm.value = pwm_value
        self.throttle = speed


def init_motors(which_motors: List[str] = None):
    """Initialize the ESCs, using the set configuration"""
    global ESC_CONTROLLERS

    for name, config in ESC_CONFIGURATIONS.items():
        if name not in which_motors:
            continue

        logger.info("Initializing ESC: {}".format(name))

        pin = config["pin"]
        frequency = config["frequency"]
        min_pulse_width = config["min_pulse_width"]
        max_pulse_width = config["max_pulse_width"]
        start_now = config["start_now"]

        ESC_CONTROLLERS[name] = ESCController(
            pin,
            frequency=frequency,
            min_pulse_width=min_pulse_width,
            max_pulse_width=max_pulse_width,
            start_now=start_now,
        )


def set_motor_config(config: Dict[str, Dict[str, Any]]):
    """Set the configuration for the ESCs. If an ESC is already started, it will be re-initialized.

    Example config:
    {
        "fr": {
            "pin": 12,
            "frequency": 50,
            "min_pulse_width": 1000,
            "max_pulse_width": 2000,
            "start_now": True,
        },
    }

    Ommitted values will be unchanged.
    """
    global ESC_CONTROLLERS, ESC_CONFIGURATIONS

    # First, check that the config only addresses existing ESCs.
    for motor_idex, motor_config in config.items():
        for key, value in motor_config.items():
            if key not in ESC_CONFIGURATIONS[motor_idex].keys():
                return {"message": f"Unknown key {key} for motor {motor_idex}"}

    # Then, update the config.
    for motor_idex, motor_config in config.items():
        for key, value in motor_config.items():
            ESC_CONFIGURATIONS[motor_idex][key] = value

    # If a motor has already been started with a configuration, close and reopen it with the new config.
    for motor_idex, motor_config in config.items():
        if motor_idex in ESC_CONTROLLERS.keys():
            logger.info(
                "ESC {} already exists - I will close and re-open it.".format(
                    motor_idex
                )
            )
            ESC_CONTROLLERS[motor_idex].init()

    return {"message": "success"}


def set_motor_throttle(cmd: Dict[str, float]):
    """Set the throttle for the motors"""
    global ESC_CONTROLLERS

    # It is important to check the throttle configuration BEFORE we start to execute the command
    for motor_idex, throttle in cmd.items():
        # Check for bad motor indexes
        if motor_idex not in ESC_CONTROLLERS.keys():
            return {"message": f"Unknown motor {motor_idex}"}

        # Check for bad throttle values
        try:
            throttle = float(throttle)
            assert 0.0 <= throttle <= 1.0
        except:
            return {
                "message": f"Throttle for {motor_idex} is not a valid float between 0 and 1"
            }

        # Check that each requested motor exists, and able to throttle
        if not ESC_CONTROLLERS[motor_idex].started:
            return {
                "message": f"Motor {motor_idex} not yet started - must call init_motors first"
            }

    # Then, execute the command
    for motor_idex, throttle in cmd.items():
        ESC_CONTROLLERS[motor_idex].set_speed(throttle)


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
        status = init_motors(payload)
        status["command"] = command
        return status

    elif command == "set_motor_config":
        status = set_motor_config(payload)
        status["command"] = command
        return status

    elif command == "set_motor_throttle":
        status = set_motor_throttle(payload)
        status["command"] = command
        return status

    else:
        return {"command": command, "message": "Unknown command"}
