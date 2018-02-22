import sys
# import Adafruit_DHT
from random import randint


class Heat:
    pin_num = None

    def __init__(self, pin):
        self.pin_num = pin

    # def get_real_status(self):
    #     try:
    #         humidity, temperature = Adafruit_DHT.read_retry(11, 1)
    #         return temperature
    #         # print('Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format)
    #     except Exception as err:
    #         return randint(0, 100)

    def get_status(self):
        return randint(0, 100)





