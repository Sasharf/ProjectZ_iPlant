from Hardware import Heat, Light, Moist, Rain, WaterLvl, Pump, Doors
from . import profile
import time


class IPlantSys:
    profile = None
    num_of_forced_pumps = 2

    def __init__(self, mac, arg_config):
        print('Current config: ', arg_config)
        self.mac = mac
        self.light = Light.Light(arg_config[1])
        self.water_lvl = WaterLvl.WaterLvl(arg_config[2])
        self.moist = Moist.Moist(arg_config[3])
        self.heat = Heat.Heat(arg_config[4])
        self.rain = Rain.Rain(arg_config[5])
        self.pump = Pump.Pump(arg_config[6])
        self.doors = Doors.Doors(arg_config[7], arg_config[8], False)

    def set_pins_config(self, arg_config):
        self.light = Light.Light(arg_config[1])
        self.water_lvl = WaterLvl.WaterLvl(arg_config[2])
        self.moist = Moist.Moist(arg_config[3])
        self.heat = Heat.Heat(arg_config[4])
        self.rain = Rain.Rain(arg_config[5])
        self.pump = Pump.Pump(arg_config[6])
        self.doors = Doors.Doors(arg_config[7], arg_config[8], False)

    # Finished
    def set_profile_from_db(self, newProfile):
        self.profile = profile.Profile(newProfile)

    # Finished
    def set_profile_from_server(self, newProfile):
        arr_sensors = []
        arr_sensors.append('profile')
        arr_sensors.append(int(newProfile['light']))
        arr_sensors.append(int(newProfile['heatMin']))
        arr_sensors.append(int(newProfile['heatMax']))
        arr_sensors.append(int(newProfile['moistMin']))
        arr_sensors.append(int(newProfile['moistMax']))
        arr_sensors.append(newProfile['location'])
        arr_sensors.append(newProfile['fix_doors'])
        self.profile = profile.Profile(arr_sensors)

    # TODO: Not finished, change get_status to get_real_status
    def get_sensors_status(self):
        arr_sensors = {
            'mac': self.mac,
            'heat': self.heat.get_status(),
            'light': self.light.get_status(),
            'moist': self.moist.get_status(),
            'water_lvl': self.water_lvl.get_status(),
            'doors': self.doors.isDoorsOpen()
        }
        return arr_sensors

    # TODO: Started - need to finish
    def return_def_pump_amount(self):
        return self.pump.def_pump_amount

    # Finished Sts
    def check_rain(self):
        return self.rain.get_status()

    # Finished Sts
    def check_heat(self):
        return self.heat.get_status()

    # Finished Sts
    def check_light(self):
        return self.light.get_status()

    # TODO: Started - need to finish
    def water_now(self):
        water_lvl = self.water_lvl.get_water_lvl()
        somenumber = 0
        num_of_pumps = 0
        curMoist = self.moist.get_status()
        # curMoist = 57
        print("Watering in progress!")
        while self.profile.moistMin >= curMoist and water_lvl > somenumber:
            self.pump.pump_now()
            num_of_pumps = num_of_pumps + 1
            # curMoist = curMoist - 1
            print('Pump number - ', num_of_pumps)
            time.sleep(5)
            water_lvl = self.water_lvl.get_water_lvl()
            curMoist = self.moist.get_status()

        pump_amount = num_of_pumps * self.pump.def_pump_amount
        return pump_amount

    def water_now_forced(self):
        print("Forced Watering in progress!")
        for i in range(self.num_of_forced_pumps):
            self.pump.pump_now()

        pump_amount = self.num_of_forced_pumps*self.pump.def_pump_amount
        return pump_amount

    # TODO: Started - need to do
    def check_if_need_water(self):
        curMoist = self.moist.get_status()
        print('Current moist: ', curMoist, '| Self profile moistMin: ', self.profile.moistMin)

        if self.profile.moistMin <= curMoist:
            return False
        return True

    #Finished Sts
    def check_water_level(self):
        return self.water_lvl.get_water_lvl()

    #Finished Sts
    def check_moist(self):
        return self.moist.get_status()

    # Finished Sts
    def check_fix_door(self):
        return self.profile.fix_doors
