import time
import gpiozero
from typing import List

# Interface for controlling an ESC (Electronic Speed Controller) using a Raspberry Pi
# and a PWM (Pulse Width Modulation) signal.

ESC_control_pins = [12]


class ESCController:
    """Class for controlling an ESC using a Raspberry Pi and a PWM signal."""

    armed = False

    def __init__(
        self,
        pin,
        frequency: int = 50,
        min_pulse_width: int = 1000,
        max_pulse_width: int = 2000,
    ):
        """The constructor for the ESC class.
        
        Frequency is the frequency of the PWM signal in Hz.
        min/max pulse width is the minimum and maximum pulse widths, in microseconds
        """

        # Create a PWMOutputDevice object to control the ESC.
        self.pwm = gpiozero.PWMOutputDevice(pin, frequency=frequency, initial_value=0)

        # calculate the duty cycle that corresponds to the minumum and maximum pulse widths, from the frequency
        self.min_pulse_width = frequency * min_pulse_width / 1000000
        self.max_pulse_width = frequency * max_pulse_width / 1000000

    def arm(self):
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
        self.armed = True

    def stop(self):
        """Stop the ESC."""

        # Set the pulse width to 0.
        self.pwm.off()

    def set_speed(self, speed: float):
        """Set the speed of the ESC, as a percentage of the maximum speed."""
        if not self.armed:
            self.arm()

        # Set the pulse width to the given speed.
        pwm_value = (self.max_pulse_width - self.min_pulse_width) * (speed / 100.0)
        pwm_value += self.min_pulse_width

        self.pwm.value = pwm_value
