import logging
logger = logging.getLogger(__name__)


from typing import List
import gpiozero


# LED Pin definition
relay_pins = [16, 20, 21]

# Set up the pins
relays: List[gpiozero.DigitalOutputDevice] = []
for pin in relay_pins:
    relay = gpiozero.DigitalOutputDevice(pin, initial_value=False)
    relays.append(relay)
    logger.info("Set up pin {} as GPIO.OUT".format(pin))


def set_relay_state(index, state):
    """Sets the state of the relay at the given index."""
    global relays
    
    if index >= len(relays):
        return False
    try:
        relays[index].value = state
    except:
        return False
    logger.debug("Set relay {} to state {}".format(index, state))
    return True


def get_relay_state():
    """Returns a list of the states of all relays."""
    relay_states = [(i, relay.value) for i, relay in enumerate(relays)]
    logger.debug("Got current relay states: {}".format(relay_states))
    return relay_states
