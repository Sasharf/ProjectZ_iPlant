from random import randint
import Adafruit_ADS1x15


class WaterLvl:
    pin_num = None
    try:
        adc = Adafruit_ADS1x15.ADS1115()
    except Exception as err:
        print(err)

    def __init__(self, pin):
        self.pin_num = int(pin)

    def get_water_lvl(self):
        try:
            raw_data = self.adc.read_adc(self.pin_num, gain=1)
            real_data = raw_data - 19500
            if real_data > 2200:
                return 100
            elif real_data < 1:
                return 0
            else:
                return int(real_data * 100 / 2200)
        except Exception as err:
            return 0

    def get_real_water_lvl(selfs):
        return randint(0, 100)