
from Sensors import Heat, Light, Moist, Rain, WaterLvl

class IPlant_sys:


    def __init__(self):
        self.mac = None
        self.heat = Heat()
        self.light = Light()
        self.moist = Moist()
        self.rain = Rain()
        self.water_lvl = WaterLvl()


