import requests
import os as os
from . import iPlant_sys, utility
from DB import DB
import time
import sys

url = 'http://localhost:3000/'
plant = {}
db = {}


def start_program():
    program_starter()

    global db
    global plant

    db = DB.PiDB()
    pi_config = db.get_config()

    if pi_config is None:
        print('Please enter Pi pins config')
        pi_config = config_device()

    plant = iPlant_sys.IPlantSys(utility.get_mac(), pi_config)

    print('Device mac address: ', utility.get_mac())
    profile = get_profile_from_db()
    if profile is not None:
        print('Profile: ', profile)
        plant.set_profile_from_db(profile)
    else:
        change_profile()

    run_time = 0
    run_choice = print_choices()
    print("-------------------Main loop started:------------------------------------ ")
    while run_time != int(run_choice):
        print("--------------------------------------", run_time, '--------------------------------------')

        # -----------------------------
        get_cmd_to_do()            # getting commands to do from server
        if plant.profile is not None:
            doors_based_on_weather()  # closing doors if raining
            check_water_lvl()         # checking if water lvl is normal, else sending report to server
            check_if_to_water()       # checking if the plant need water, and water it if the water lvl high enough
            check_if_whole_hour()     # checking if whole hour, if so then sending sensors status to server
        # -----------------------------

        run_time += 1
        print('Sleeping 5 seconds...')
        time.sleep(5)

    program_ended()


# Finished
def get_cmd_to_do():
    print("Getting commands to do from server:")
    params = {
        "mac": plant.mac,
    }
    try:
        resp = requests.post(url+'deviceCommands/getCommands', timeout=0.05, json=params)
        answer = resp.json()
    except Exception as err:
        print("Cant reach server")
        return

    if answer['success']:
        print("There are commands to execute!")
        print(answer['answer'])
        do_commands(answer['answer'])

    else:
        print("No commands to execute!")


# TODO: Not finished - depends on what commands we will have
def do_commands(arg_commands):
    for cmd in arg_commands:
        print("Doing command:", cmd['command'])
        if cmd['command'] == "init_device" and os.path.exists('piDB'):
            init_db()
        elif cmd['command'] == "set_profile":
            change_profile()
        elif cmd['command'] == "get_sensors_status":
            send_sensors_status()
        elif cmd['command'] == "water_now":
            water_now()
    return True


# Finished
def send_sensors_status():
    data = plant.get_sensors_status()
    db.insert_sensors_log(data)
    try:
        resp = requests.post(url+'sensorRecords/add', timeout=0.05, json=data)
        answer = resp.json()

        print("Server got answer? --> ", answer['success'])
    except Exception as err:
        print("Cant reach server")

    return True


# Finished
def change_profile():
    answer = get_profile_from_server()
    print(answer)
    if answer['success']:
        if answer['device']:
            set_profile(answer['answer'])
        else:
            print(answer['msg'])
    elif answer['success'] is False:
        print("Cant reach server")


# Finished
def get_profile_from_server():
    data = {"mac": plant.mac}
    print('Trying to get profile from server...')

    try:
        resp = requests.post(url + 'user_devices/getDeviceProfileByMac', timeout=0.05, json=data)
        answer = resp.json()

        print("Server got answer? --> ", answer['success'])
    except Exception as err:
        answer = {'success': False}

    return answer


# Finished
def get_profile_from_db():
    return db.get_profile()


# Finished
def set_profile(profile):
    print('Setting profile: ')
    print(profile)
    if plant.profile is None:
        db.set_profile(profile)
        print('New profile been set')
    else:
        db.update_profile(profile)
        print('Profile been updated')

    plant.set_profile_from_server(profile)


# Finished
def init_db():
    global db
    print('DB init started...')
    db = None
    os.remove('piDB')
    db = DB.PiDB()
    print('DB init finished...')


# Finished
def config_device():
    print('Pi config in progress:')
    pi_config = []
    pi_config.append("Stss")
    pi_config.append(input("Enter light sensor pin number(In adc): "))
    pi_config.append(input("Enter water_lvl sensor pin number(adc): "))
    pi_config.append(input("Enter moist sensor pin number(In adc): "))
    pi_config.append(input("Enter heat sensor pin number: "))
    pi_config.append(input("Enter rain sensor pin number: "))
    pi_config.append(input("Enter pump sensor pin number: "))
    pi_config.append(input("Enter door_left sensor pin number: "))
    pi_config.append(input("Enter door_right sensor pin number: "))

    config = db.get_config()

    if config is not None:
        db.update_config(pi_config)
    else:
        db.set_config(pi_config)

    return pi_config


# Finished
def set_config(pi_config):
    plant.set_pins_config(pi_config)


# Finished
def check_if_whole_hour():
    timestamp = time.time()
    if timestamp % 3600 == 0:
        print("sending sensors status to server")
        send_sensors_status()


# TODO: - need to finish
def check_water_lvl():
    water_lvl = plant.water_lvl.get_water_lvl()
    somelimit = 20

    if water_lvl < somelimit:
        print("Critical Water level in reservoir ", water_lvl, "L. Sending reminders to server.")
        send_reminders_to_server(water_lvl)

    else:
        print("Water level in reservoir ", water_lvl, "L, enough for now.")


# TODO: Not started - need to do
def send_reminders_to_server(water_lvl):
    return True


# TODO: Started - need to finish
def check_if_to_water():
    num_of_pumps = 0
    print("Checking if need to water the plant:")
    if plant.check_if_need_water():

        send_start_water_session()
        pump_amount = plant.water_now()
        send_end_water_session()

        if pump_amount > 0:
            print('Watering session ended, watered for - ', pump_amount)
            db.insert_water(pump_amount)
            send_water_log(pump_amount)
    else:
        print("No need to water the plant for now.")


# Finished
def water_now():
    send_start_water_session()
    pump_amount = plant.water_now()
    send_end_water_session()
    db.insert_water(pump_amount)
    send_water_log(pump_amount)

    print('Forced Watering session ended, watered for - ', pump_amount)


# Finished Sts
def doors_based_on_weather():
    if plant.check_fix_door():  # if fixed doors enabled
        return

    profile_max_heat = plant.profile.heatMax
    profile_min_heat = plant.profile.heatMin
    current_heat = plant.check_heat()
    rain_status = plant.check_rain()
    doors_status = plant.doors.isDoorsOpen()

    print('Checking heat....', current_heat, ' C')
    if rain_status and doors_status:  # if rainy & doors open
        print('Rainy outside, closing doors...')
        plant.doors.doors()
    elif current_heat - 2 > profile_max_heat and not doors_status:  # if hot and door closed
        print('Opening doors, current heat ', current_heat, ' is above needed heat ', profile_max_heat)
        plant.doors.doors()
    elif current_heat + 2 < profile_min_heat and doors_status:  # if cold and opened
        print('Opening doors, current heat ', current_heat, ' is below needed heat ', profile_min_heat)
        plant.doors.doors()


# Finished
def send_start_water_session():
    print('Sending to server that water session started...')
    data = {'mac': plant.mac}
    try:
        resp = requests.post(url + 'waterSessions/start', timeout=0.05, json=data)
        answer = resp.json()

        print("Server got answer? --> ", answer['success'])
    except Exception as err:
        print("Cant reach server")


# Finished
def send_end_water_session():
    print('Sending to server that water session ended...')
    data = {'mac': plant.mac}
    try:
        resp = requests.post(url + 'waterSessions/end', timeout=0.05, json=data)
        answer = resp.json()

        print("Server got answer? --> ", answer['success'])
    except Exception as err:
        print("Cant reach server")


# Finished
def send_water_log(amount):
    print('Sending water log to server...')
    data = {'amount': amount, 'mac': plant.mac}
    try:
        resp = requests.post(url + 'waterRecords/add', timeout=0.05, json=data)
        answer = resp.json()

        print("Server got answer? --> ", answer['success'])
    except Exception as err:
        print("Cant reach server")

    return True


# Finished
def print_choices():
    global plant
    choice = -1

    while True:
        print("Commands:")
        print("1) Start main loop")
        print("2) Configure Pi pins")
        print("3) Init DB")
        print("4) Doors check")
        print("5) Sensor check")
        print("0) Exit program")

        choice = int(input('Please enter command number:'))

        if choice == 1:
            run_choice = int(input('Please enter how much time you would like the program to run(-1 for inf, 0 for back):'))
            if run_choice == 0:
                continue
            else:
                break
        if choice == 2:
            pi_config = config_device()
            set_config(pi_config)
        if choice == 3:
            init_db()
            pi_config = config_device()
            set_config(pi_config)
        if choice == 4:
            while True:
                print("Door status:", plant.doors.isDoorsOpen())
                print("(-) 1 to open the doors")
                print('(-) 2 for doors calibrations')
                print('(-) 3 Change door status')
                print('(-) 0 for back')
                door_choice = int(input('Please enter command number:'))
                if door_choice == 1:
                    plant.doors.doors()
                if door_choice == 2:
                    while True:
                        print('(--) Door calibrations:')
                        print("(--)  1 For up")
                        print('(--) -1 For down')
                        print('(--)  0 Back')
                        side = int(input('Enter command'))
                        if side == 1:
                            plant.doors.calibrateUp()
                        elif side == -1:
                            plant.doors.calibrateDown()
                        elif side == 0:
                            break
                if door_choice == 3:
                    plant.doors.changeDoorStatus()
                if door_choice == 0:
                    break
                if choice == 5:
                    while True:
                        print("(-) 1 to check light")
                        print('(-) 2 to check water level')
                        print('(-) 3 to check moist')
                        print('(-) 4 to check heat')
                        print("(-) 5 to check rain")
                        print('(-) 6 to check pump, not ready yet to check')
                        print('(-) 0 to main menu')

                        sensor_choice = int(input('Please enter command number:'))
                        if sensor_choice == 1:
                            print('light: ', plant.check_light(), '%')
                        if sensor_choice == 2:
                            print('water level: ', plant.check_water_lvl(), '%')
                        if sensor_choice == 3:
                            print('moist level: ', plant.check_moist(), '%')
                        if sensor_choice == 4:
                            print('heat level: ', plant.check_heat(), 'C')
                        if sensor_choice == 5:
                            print('is it raining?: ', plant.check_rain(), ' ||"1" for rain "0" otherwise')
                        if sensor_choice == 6:
                            print('force pump: ', plant.water_now())
                        if sensor_choice == 0:
                            break

        if choice == 0:
            program_ended()
            sys.exit()

    return run_choice


# Finished
def program_starter():
    print("")
    print("-------------------iPlant program STARTED!--------------------------------")


# Finished
def program_ended():
    print("-------------------iPlant program ENDED!----------------------------------")
