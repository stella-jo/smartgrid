import RPi.GPIO as GPIO

RELAY_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)

def set_relay(state: bool):
		GPIO.output(RELAY_PIN, GPIO.HIGH if state else GPIO.LOW)

def get_relay_state():
		return GPIO.input(RELAY_PIN) == GPIO.HIGH