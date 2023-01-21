import time
import gpiozero
from typing import List

# Interface for controlling an ESC (Electronic Speed Controller) using a Raspberry Pi
# and a PWM (Pulse Width Modulation) signal.

ESC_control_pins = [18]


class ESCController:
    """Class for controlling an ESC using a Raspberry Pi and a PWM signal."""

    started = False

    def __init__(
        self,
        pin,
        frequency: int = 100,
        min_pulse_width: int = 0.0,
        max_pulse_width: int = 1.0,
    ):
        """The constructor for the ESC class."""

        # Create a PWMOutputDevice object to control the ESC.
        self.pwm = gpiozero.PWMOutputDevice(pin, frequency=frequency, initial_value=0)

        # Set the minimum and maximum pulse widths.
        self.min_pulse_width = min_pulse_width
        self.max_pulse_width = max_pulse_width

    def start(self):
        """Start the ESC wakeup handshake.

        Each step is separated by a 2 second delay:
            1. Set the pulse width to the minimum.
            2. Set the pulse width to the maximum.
            3. Set the pulse width to the minimum.

        After the handshake, the ESC will be ready to receive a throttle signal.
        """
        self.pwm.on()
        time.sleep(5)

        # Set the pulse width to the minimum.
        self.pwm.value = self.min_pulse_width
        time.sleep(3)

        # Set the pulse width to the maximum.
        self.pwm.value = self.max_pulse_width
        time.sleep(5)

        # Set the pulse width to the minimum
        self.pwm.value = self.min_pulse_width
        time.sleep(2)

        # Then we're done
        self.pwm.value = 0.0
        self.started = True

    def stop(self):
        """Stop the ESC."""

        # Set the pulse width to 0.
        self.pwm.value = 0

    def set_speed(self, speed: float):
        """Set the speed of the ESC, as a percentage of the maximum speed."""
        if not self.started:
            self.start()

        # Set the pulse width to the given speed.
        pwm_value = (self.max_pulse_width - self.min_pulse_width) * (speed / 100.0)
        pwm_value += self.min_pulse_width

        self.pwm.value = pwm_value


motors: List[ESCController] = []
for pin in ESC_control_pins:
    # Create an ESC object to control the ESC on pin 18.
    esc = ESCController(pin)

    # Start the ESC.
    esc.start()

    motors.append(esc)
