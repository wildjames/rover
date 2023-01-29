import logging
logger = logging.getLogger(__name__)

import time
import gpiozero
from typing import List

# Interface for controlling an ESC (Electronic Speed Controller) using a Raspberry Pi
# and a PWM (Pulse Width Modulation) signal.


class ESCController:
    """Class for controlling an ESC using a Raspberry Pi and a PWM signal."""
    armed = True
    started = False
    throttle = 0.0

    def __init__(
        self,
        pin,
        frequency: int = 50,
        min_pulse_width: int = 1000,
        max_pulse_width: int = 2000,
        start_now = True
    ):
        """The constructor for the ESC class.

        Frequency is the frequency of the PWM signal in Hz.
        min/max pulse width is the minimum and maximum pulse widths, in microseconds
        """

        self.frequency = frequency

        # Create a PWMOutputDevice object to control the ESC.
        self.pin = pin
        self.frequency = frequency

        if start_now:
            self.init()

        # calculate the duty cycle that corresponds to the minumum and maximum pulse widths, from the frequency

        self.min_pulse_width = min_pulse_width
        self.max_pulse_width = max_pulse_width

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
        self.pwm = gpiozero.PWMOutputDevice(self.pin, frequency=self.frequency, initial_value=0.0)
        self.stop()
        self.started = True

    def close(self):
        """Release the GPIO connection. Sets the throttle to zero first, then disables the PWM signal."""
        logger.debug(f"Closing ESC on pin {self.pin}")
        self.stop()
        self.pwm.off()
        self.pwm.close()
        self.started = False

    def calibrate(self):
        """Calibrate the ESC. Interactive, as it requires the user to disconnect and reconnect the battery."""
        logger.info("Disconnect the battery, hit enter when done")
        input("> ")

        logger.info("Sending maximum pulse width")
        self.pwm.value = self.max_pulse_width

        logger.info("Connect the battery, hit enter when done")
        input("> ")

        time.sleep(2)
        logger.info("Sending minimum pulse width")
        self.pwm.value = self.min_pulse_width

        logger.info("OK")

    def arm(self):
        """Start the ESC wakeup handshake.

        Each step is separated by a 2 second delay:
            1. Set the pulse width to the minimum.
            2. Set the pulse width to the maximum.
            3. Set the pulse width to the minimum.

        After the handshake, the ESC will be ready to receive a throttle 0 signal.
        """
        logger.info("Arming ESC")

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
        """Emergency stop the ESC. Bypass calculations, set PWM duty cycle to 0."""
        logger.info("Emergency stopping ESC")
        self.pwm.off()
        self.throttle = 0.0

    def set_speed(self, speed: float):
        """Set the speed of the ESC, as a fraction of the maximum speed."""
        # Set the pulse width to the given speed.
        pwm_value = (self.max_pulse_width - self.min_pulse_width) * speed
        pwm_value += self.min_pulse_width

        logger.info(
            "Setting ESC speed to {:.1f}% (duty cycle {:.3f})".format(speed*100.0, pwm_value)
        )
        if not self.armed:
            logger.warn("ESC not armed!")
        self.pwm.value = pwm_value
        self.throttle = speed
