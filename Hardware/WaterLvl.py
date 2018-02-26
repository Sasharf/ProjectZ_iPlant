from random import randint
import Adafruit_ADS1x15


class WaterLvl:
    pin_num = None
    try:
        adc = Adafruit_ADS1x15.ADS1015()
    except Exception as err:
        print(err)

    def __init__(self, pin):
        self.pin_num = int(pin)

    def get_water_lvl(self):
        try:
            raw_data = self.adc.read_adc(self.pin_num, gain=1)
            if raw_data > 23000:
                return 100
            return raw_data * 100 / 2300
        except Exception as err:
            return 0

    def get_real_water_lvl(selfs):
        return randint(0, 100)