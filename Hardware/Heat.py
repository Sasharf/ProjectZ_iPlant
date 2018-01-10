#import RPi.GPIO as GPIO
from random import randint
import Adafruit_ADS1x15
#GPIO.setmode(GPIO.BCM)


class Heat:
    pin_num = None
    adc = Adafruit_ADS1x15.ADS1015()

    def __init__(self, pin):
        self.pin_num = pin

    def get_real_status(self):
        return self.adc.read_adc(self.pin_num, gain=1)

    def get_status(self):
        return randint(0, 1000)
