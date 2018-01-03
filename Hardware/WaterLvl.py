#import RPi.GPIO as GPIO
from random import randint
#GPIO.setmode(GPIO.BCM)


class WaterLvl:
    pin_num = None

    def __init__(self, pin):
        self.pin_num = pin

    def get_status(self):
        return randint(0, 1000)

    def get_water_lvl(selfs):
        return randint(0, 1000)