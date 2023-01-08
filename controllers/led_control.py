import RPi.GPIO as GPIO


# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# LED Pin definition
leds = [17, 27, 22]

for pin in leds:
	GPIO.setup(pin, GPIO.OUT)


def set_led_state(index, state):
	if index >= len(leds):
		return
	GPIO.output(leds[index], state)


def get_led_state():
	led_states = []
	for led in leds:
		led_states.append(GPIO.input(led))
	return led_states


if __name__ in "__main__":
	for led in leds:
		set_led_state(led, 0)

	print(get_led_state())
	set_led_state(0, 1)
	print(get_led_state())

	from time import sleep
	sleep(1)
	set_led_state(0, 0)
