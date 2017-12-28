import requests, json
from Sensors import Heat, Light, Moist, Rain, WaterLvl
from . import utility
import time


class IPlantSys:
    profile = None

    def __init__(self):
        self.mac = None
        self.heat = Heat.Heat(1)
        self.light = Light.Light(2)
        self.moist = Moist.Moist(3)
        self.rain = Rain.Rain(4)
        self.water_lvl = WaterLvl.WaterLvl(5)

    def set_profile(self, profile):
        self.profile = profile

    def get_sensors_status(self):
        arr_sensors = []
        for attr, value in self.__dict__.items():

            if attr == 'mac':
                continue
            sensor = {
                'name': attr,
                'value': value.get_status()
            }
            arr_sensors.append(sensor)

        return arr_sensors

    def get_cmd_to_do(self):
        print("Getting commands to do from server:")
        params = {
            "pi_mac": utility.get_mac(),
        }

        resp = requests.get('http://127.0.0.1:8000/get_commands', params=params)
        answer = resp.json()

        if answer['success']:
            print("There are commands to execute!")
            print(answer['commands'])
            self.do_commands(answer['commands'])

        else:
            print("No commands to execute!")
        return True

    def do_commands(self, arg_commands):

        for cmd in arg_commands:
            print("Doing command:", cmd['name'])
            if cmd['name'] == "get_sensors_status":
                self.send_sensors_status()

        return True

    def send_sensors_status(self):
        data = {
            "pi_mac": utility.get_mac(),
            "arr_sensors": self.get_sensors_status()
        }
        resp = requests.get('http://127.0.0.1:8000/receive_and_save_sensors', params=data)
        answer = resp.json()

        print(answer['success'])

        return True
