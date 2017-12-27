import RPi.GPIO as GPIO
from random import randint
GPIO.setmode(GPIO.BCM)


class Rain:
    pin_num = None

    def __init__(self, pin):
        self.pin_num = pin

    def get_status(self):
        return randint(0, 1000)
