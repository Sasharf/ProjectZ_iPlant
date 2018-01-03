
from . import iPlant_sys
import time
import sys


def star_program():
    program_starter()

    iplant = iPlant_sys.IPlantSys()
    run_choice = print_choices()

    run_time = 0
    print("-------------------Main loop started:------------------------------------ ")
    while run_time != int(run_choice):
        print("-------------------", run_time)

        # -----------------------------
        iplant.get_cmd_to_do()          # getting commands to do from server
        check_water_lvl(iplant)         # checking if water lvl is normal, else sending report to server
        check_if_to_water(iplant)       # checking if the plant need water, and water it if the water lvl high enough
        check_if_whole_hour(iplant)     # checking if whole hour, if so then sending sensors status to server
        # -----------------------------

        run_time += 1
        time.sleep(5)

    program_ended()

# Finished
def print_choices():
    choice = -1
    while choice != "1" and choice != "2":
        print("Commands:")
        print("1) Start main loop")
        print("2) exit program")

        choice = input('Please enter command number:')

    if choice == "1":
        run_choice = input('Please enter how much time you would like the program to run(-1 for inf, 0 for exit): ')
    if choice == "2" or run_choice == "0":
        program_ended()
        sys.exit()

    return run_choice

# Fnished
def check_if_whole_hour(iplant):
    timestamp = time.time()
    if timestamp % 3600 == 0:
        print("sending sensors status to server")
        iplant.send_sensors_status()

# TODO: - need to finish
def check_water_lvl(iplant):
    water_lvl = iplant.water_lvl.get_water_lvl()
    somelimit = 123

    if water_lvl < somelimit:
        print("Critical Water level in reservoir ", water_lvl, "L. Sending reminders to server.")
        send_reminders_to_server(water_lvl)

    else:
        print("Water level in reservoir ", water_lvl, "L, enough for now.")

# TODO: Not started - need to do
def send_reminders_to_server(water_lvl):
    return True

# TODO: Started - need to finish
def check_if_to_water(iplant):
    print("Checking if need to water the plant:")
    if iplant.check_if_need_water():
        iplant.water_now()
    else:
        print("No need to water the plant for now.")

# Fnished
def program_starter():
    print("")
    print("-------------------iPlant program STARTED!--------------------------------")

# Fnished
def program_ended():
    print("-------------------iPlant program ENDED!----------------------------------")
