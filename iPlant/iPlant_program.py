
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

        iplant.get_cmd_to_do()
        check_if_whole_hour(iplant)
        run_time += 1

        time.sleep(5)

    program_ended()


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


def check_if_whole_hour(iplant):
    timestamp = time.time()
    if timestamp % 3600 == 0:
        print("sending sensors status to server")
        iplant.send_sensors_status()


def program_starter():
    print("")
    print("-------------------iPlant program STARTED!--------------------------------")


def program_ended():
    print("-------------------iPlant program ENDED!----------------------------------")
