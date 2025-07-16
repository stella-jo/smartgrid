import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

print("relay off")
GPIO.output(17, GPIO.HIGH)
time.sleep(2)

print("relay on")
GPIO.output(17, GPIO.LOW)
time.sleep(2)

print("relay off")
GPIO.output(17, GPIO.HIGH)
time.sleep(2)

GPIO.cleanup()
print("GPIO")