from random import randint
import time

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Pump:
    pin_num = None
    def_pump_amount = 100

    def __init__(self, pin):
        self.pin_num = int(pin)
        GPIO.setup(self.pin_num, GPIO.OUT)
        GPIO.output(self.pin_num, GPIO.HIGH)

    def get_status(self):
        return randint(0, 1000)

    # need to finish
    def pump_now(self):
        return True

    def pump_now_real(self):
        GPIO.output(self.pin_num, GPIO.LOW)
        time.sleep(3)
        GPIO.output(self.pin_num, GPIO.HIGH)

