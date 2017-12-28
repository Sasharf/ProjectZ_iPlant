
from . import iPlant_sys
from DB.DB import PiDB
import time

def star_program():
    print("")
    print("-------------------iPlant program STARTED!--------------------------------")

    piDB = PiDB()
    iplant = iPlant_sys.IPlantSys()

    choice = -1
    while choice != "1" and choice != "2":
        print("Commands:")
        print("1) Start main loop")
        print("2) exit program")

        choice = input('Please enter command number:')

    if choice == "1":
        choice = input('Please enter how much time you would like the program to run(-1 for inf, 0 for exit): ')
    if choice == "2" or choice == "0":
        program_ended()
        return

    run_time = 0
    print("-------------------Main loop started:------------------------------------ ")
    while run_time != int(choice):
        print("-------------------", run_time)
        iplant.get_cmd_to_do()
        run_time += 1
        time.sleep(5)

    program_ended()


def program_ended():
    print("-------------------iPlant program ENDED!----------------------------------")
