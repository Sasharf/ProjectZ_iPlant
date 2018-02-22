from random import randint
import Adafruit_ADS1x15


class Light:
    pin_num = None
    try:
        adc = Adafruit_ADS1x15.ADS1015()
    except Exception as err:
        print(err)

    def __init__(self, pin):
        self.pin_num = pin

    def get_real_status(self):
        try:
            return self.adc.read_adc(self.pin_num, gain=1)
        except Exception as err:
            return randint(0, 100)

    def get_status(self):
        return randint(0, 100)

# ToDO:
# write on each sensor the range of the signal given.
# F.E: light goes approx from 7 to 24k
#      moist goes approx from 7 ( dry ), then jumps straight to 7k, then, depends on water lvl untill 15k