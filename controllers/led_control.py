import logging
logger = logging.getLogger(__name__)


from typing import List
import gpiozero


# LED Pin definition
led_pins = []

# Set up the pins
leds: List[gpiozero.LED] = []
for pin in led_pins:
    led = gpiozero.LED(pin, initial_value=False)
    leds.append(led)
    logger.info("Set up pin {} as GPIO.OUT".format(pin))


def set_led_state(index, state):
    """Sets the state of the LED at the given index."""
    if index >= len(leds):
        return False
    try:
        leds[index].value = state
    except:
        return False
    logger.debug("Set LED {} to state {}".format(index, state))
    return True


def get_led_state():
    """Returns a list of the states of all LEDs."""
    led_states = [(i, led.value) for i, led in enumerate(leds)]
    logger.debug("Got current LED states: {}".format(led_states))
    return led_states
