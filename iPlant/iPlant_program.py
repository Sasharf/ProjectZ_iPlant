import requests
import os as os
from . import iPlant_sys, utility
from DB import DB
import time
import sys

url = 'http://localhost:3000/'
plant = {}
db = {}
heat_sample = {}
server_timeout = 0.5
main_loop_time = 3


def start_program():
    program_starter()

    global db
    global plant
    
    interrupt_flag = False
    db = DB.PiDB()
    pi_config = db.get_config()

    print('Device mac address: ', utility.get_mac())
    if pi_config is None:
        print('Please enter Pi pins config')
        pi_config = config_device()

    plant = iPlant_sys.IPlantSys(utility.get_mac(), pi_config)
    last_sensor_log = db.get_last_sensors_log()
    print('Last sensor log: ', last_sensor_log)

    if last_sensor_log is not None and last_sensor_log[5] is not None:
        print('Door status has been changed to last sensor record: ', last_sensor_log[5])
        plant.doors.is_open = last_sensor_log[5]

    profile = get_profile_from_db()
    if profile is not None:
        print('Profile: ', profile)
        plant.set_profile_from_db(profile)
    else:
        print('Profile:  Not set yet')
        change_profile()

    run_time = 0
    run_choice = print_choices()
    print("-------------------Main loop started:------------------------------------ ")
    try:
        while run_time != int(run_choice):
            print("--------------------------------------", run_time, '--------------------------------------')

            # -----------------------------
            get_cmd_to_do()                             # getting commands to do from server
            if plant.profile is not None:
                sensors_status = do_sensor_check()      # Doing sensor check and saving it
                doors_based_on_weather(sensors_status)  # closing doors if raining/to hot
                check_if_to_water()                     # checking if the plant need water, and water it if the water lvl high enough
            # -----------------------------

            run_time += 1
            print('Sleeping ', main_loop_time, ' seconds...')
            time.sleep(main_loop_time)

    except KeyboardInterrupt:
            interrupt_flag = True
            program_ended()

    if not interrupt_flag:
        program_ended()


# Finished
def get_cmd_to_do():
    print("Getting commands to do from server:")
    params = {
        "mac": plant.mac,
    }
    try:
        resp = requests.post(url+'deviceCommands/getCommands', timeout=server_timeout, json=params)
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


def print_commands(commands):
    str_commands = ""
    for cmd in commands:
        str_commands += cmd['command']+', '


# TODO: Not finished - depends on what commands we will have
def do_commands(arg_commands):
    print('-' * 20)
    print_commands(arg_commands)
    print('|', '-' * 18, '|')
    for cmd in arg_commands:
        print("Doing command:", cmd['command'])
        if cmd['command'] == "init_device" and os.path.exists('piDB'):
            init_db()
        elif cmd['command'] == "set_profile":
            change_profile()
        elif cmd['command'] == "activate_doors":
            activate_doors()
        # elif cmd['command'] == "get_sensors_status":
        #     send_sensors_status()
        elif cmd['command'] == "water_now":
            water_now()
        print('|', '-' * 18, '|')
    return True


# Finished
def do_sensor_check():
    sensors_log = get_sensors_log()
    save_sensors_log(sensors_log)
    print_sensors_log(sensors_log)
    send_sensors_log(sensors_log)

    return sensors_log


# Finished
def get_sensors_log():
    return plant.get_sensors_status()


# Finished
def save_sensors_log(sensors_log):
    db.remove_last_sensors_log()
    db.insert_last_sensors_log(sensors_log)


# ToDO: in progress
def send_sensors_log(sensors_log):
    whole_hour = check_if_whole_hour()
    if whole_hour:
        print("Whole hour, saving log...")
        save_whole_hour_log(sensors_log)

    print('Sending sensor log to server...')

    sensors_log['whole_hour'] = whole_hour
    try:
        resp = requests.post(url+'lastSensorRecords/add', timeout=server_timeout, json=sensors_log)
        answer = resp.json()

        print("Server got answer? --> ", answer['success'])
    except Exception as err:
        print("Cant reach server")

    return True


# Finished
def print_sensors_log(sensors_log):
    arr_sensors = []
    arr_sensors.append(sensors_log['light'])
    arr_sensors.append(sensors_log['heat'])
    arr_sensors.append(sensors_log['moist'])
    arr_sensors.append(sensors_log['water_lvl'])
    arr_sensors.append(sensors_log['doors'])
    arr_sensors.append(sensors_log['rain'])
    cur_time = time.strftime("%H:%M:%S", time.localtime())

    print('Current sensors status:')
    print('-' * 86)
    print('|   Time   |   Light   |   Moist   |   Heat   |   Water lvl   |   Doors   |   Rain   |')
    print('-' * 86)
    print('|', cur_time, '| {0:>9} | {1:>9} | {2:>8} | {3:>13} | {4:>9} | {5:>8} |'.format(*arr_sensors))
    print('-' * 86)


# Finished
def check_if_whole_hour():
    timestamp = time.time()
    if timestamp % 3600 == 0:
        return True
    else:
        return False


# Finished
def save_whole_hour_log(sensors_log):
    db.insert_sensors_log(sensors_log)


# Finished
def activate_doors():
    plant.doors.doors()
    last_sensor_record = plant.get_sensors_status()
    db.insert_sensors_log(last_sensor_record)


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
        resp = requests.post(url + 'user_devices/getDeviceProfileByMac', timeout=server_timeout, json=data)
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


# TODO: Started - need to finish
def check_if_to_water():
    print("Checking if need to water the plant:")
    need_to_water = plant.check_if_need_water()
    enough_water = plant.check_if_enough_water_lvl()

    if need_to_water and enough_water:

        send_start_water_session()
        pump_amount = plant.water_now()
        send_end_water_session()

        if pump_amount > 0:
            print('Watering session ended, watered for - ', pump_amount)
            db.insert_water(pump_amount)
            send_water_log(pump_amount)
    elif need_to_water and not enough_water:
        print('Need to water but not enough water in reservoir')
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
def doors_based_on_weather(sensors_status):
    if plant.check_fix_door():  # if fixed doors enabled
        print("Doors fixed, doing nothing ;)")
        return

    profile_max_heat = plant.profile.heatMax
    profile_min_heat = plant.profile.heatMin

    current_heat = sensors_status['heat']
    rain_status = sensors_status['rain']
    doors_status = sensors_status['doors']

    if rain_status and doors_status:  # if rainy & doors open
        print('Rainy outside, closing doors...')
        plant.doors.doors()

    elif current_heat - 2 > profile_max_heat and not doors_status:  # if hot and door closed
        print('Opening doors, too hot , current heat: ', current_heat,'(-2) max heat: ', profile_max_heat)
        plant.doors.doors()

    elif current_heat + 2 < profile_min_heat and doors_status:  # if cold and opened doors
        print('Opening doors,too cold ,  current heat ', current_heat, '(+2) min heat: ', profile_min_heat)
        plant.doors.doors()


# ToDo: in progress
def check_better_state():
    current_heat = plant.check_heat()
    logged_heat = None 
    current_time = time.time()


# Finished
def send_start_water_session():
    print('Sending to server that water session started...')
    data = {'mac': plant.mac}
    try:
        resp = requests.post(url + 'waterSessions/start', timeout=server_timeout, json=data)
        answer = resp.json()

        print("Server got answer? --> ", answer['success'])
    except Exception as err:
        print("Cant reach server")


# Finished
def send_end_water_session():
    print('Sending to server that water session ended...')
    data = {'mac': plant.mac}
    try:
        resp = requests.post(url + 'waterSessions/end', timeout=server_timeout, json=data)
        answer = resp.json()

        print("Server got answer? --> ", answer['success'])
    except Exception as err:
        print("Cant reach server")


# Finished
def send_water_log(amount):
    print('Sending water log to server...')
    data = {'amount': amount, 'mac': plant.mac}
    try:
        resp = requests.post(url + 'waterRecords/add', timeout=server_timeout, json=data)
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
        print("6) Functions check")
        print("7) Change  profile")
        print("8) Check current sensor log")
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
                    last_sensor_record = plant.get_sensors_status()
                    db.insert_sensors_log(last_sensor_record)
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
                print('(-) 6 to check pump, not yet')
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

        if choice == 6:
            while True:
                print("(-) 1 to check door based on weather and fix status for once")
                print('(-) 2 same as 1 but for infinity')
                print('(-) 0 to main menu')
                func_choice = int(input('Please enter command number:'))
                if func_choice == 1:
                    doors_based_on_weather()
                if func_choice == 2:
                    while True:
                        try:
                            doors_based_on_weather()
                            print("cooling down 10s")
                            time.sleep(10)
                        except KeyboardInterrupt:
                            break

                if func_choice == 0:
                    break

        if choice == 7:
            while True:
                if plant.profile:  
                    cur_profile_loop = plant.profile.get_profile()
                else:
                    cur_profile_loop = None
                print('Current profile: ', cur_profile_loop)
                print("(-) 1 Change profile")
                print("(-) 2 Delete profile")
                print('(-) 3 Change fix doors')
                print('(-) 0 To main menu')
                profile_choice = int(input('Please enter command number:'))
                if profile_choice == 1: 
                    dummy_profile = {}
                    dummy_profile['light'] = int(input("Enter wanted light:"))
                    dummy_profile['heatMin'] = int(input("Enter wanted heat min:"))
                    dummy_profile['heatMax'] = int(input("Enter wanted heat max:"))
                    dummy_profile['moistMin'] = int(input("Enter wanted moist min:"))
                    dummy_profile['moistMax'] = int(input("Enter wanted moist max:"))
                    dummy_profile['location'] = input("Enter wanted location:")
                    dummy_profile['fix_doors'] = int(input("Enter wanted fix_doors:"))
                    set_profile(dummy_profile)
                if profile_choice == 2:
                    print('Deleting profile...')
                    db.delete_profile()
                    plant.profile = None
                    print('Profile has been deleted')
                if profile_choice == 3:
                    if cur_profile_loop is None:
                        print('Profile not set yet, cant change fix door state')
                    else:
                        fix_doors_state = int(input('Enter fix door state(0/1):'))
                        cur_profile_loop['fix_doors'] = fix_doors_state
                        set_profile(cur_profile_loop)
                if profile_choice == 0:
                    break
        if choice == 8:
            last_log = plant.get_sensors_status()
            print_sensors_log(last_log)
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
