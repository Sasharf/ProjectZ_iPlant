import sqlite3
import sys
import os as os
import iPlant.profile
import time


class PiDB:
    conn = None
    c = None

    def __init__(self):
        if not os.path.exists('piDB'):
            print('iPlant DB exists? --> Doesnt exist')
            self.create_db()
        else:
            print('iPlant DB exists? --> Exist')

        self.conn = sqlite3.connect('piDB')
        self.c = self.conn.cursor()

    def __del__(self):
        self.c.close()
        self.conn.close()

    # ............................SENSORS...............................................................
    # ................................................................................................

    def insert_sensors_log(self, data):
        light = data['light']
        heat = data['heat']
        moist = data['moist']
        water_lvl = data['water_lvl']

        with self.conn:
            self.c.execute("INSERT INTO sensors_log values (:prob_date,:light,:heat,:moist,:water_lvl)",
                           {'prob_date': time.time(), 'light': light, 'heat': heat, 'moist': moist, 'water_lvl': water_lvl})

    def get_last_sensors_log(self):
        self.c.execute("""SELECT * 
                          FROM sensors_log 
                          WHERE prob_date = (SELECT MAX(prob_date) FROM sensors_log)
                      """)
        return self.c.fetchone()

    def get_many_sensors_logs(self, arg):
        self.c.execute("""SELECT * 
                          FROM sensors_log 
                          ORDER BY prob_date desc
                      """)
        return self.c.fetchmany(arg)

    # ..............................PROFILE...........................................................
    # ................................................................................................

    def set_profile(self, arg_profile):
        with self.conn:
            self.c.execute("INSERT INTO profile values (:name,:light,:heatMin,:heatMax,:moistMin,:moistMax,:location)",
                           {'name': 'profile',
                            'light': arg_profile['light'],
                            'heatMin': arg_profile['heatMin'],
                            'heatMax': arg_profile['heatMax'],
                            'moistMin': arg_profile['moistMin'],
                            'moistMax': arg_profile['moistMax'],
                            'location': arg_profile['location']
                            })

    def get_profile(self):
        self.c.execute("""SELECT * 
                          FROM profile
                      """)
        return self.c.fetchone()

    def update_profile(self, arg_profile):
        with self.conn:
            arg_light = arg_profile['light']
            arg_heatMin = arg_profile['heatMin']
            arg_heatMax = arg_profile['heatMax']
            arg_moistMin = arg_profile['moistMin']
            arg_moistMax = arg_profile['moistMax']
            arg_location = arg_profile['location']

            self.c.execute("""UPDATE profile
                              SET light = ?, heatMin = ?, heatMax = ?,
                                  moistMin = ?, moistMax = ?, location = ?
                              WHERE name='profile';
                          """, (arg_light, arg_heatMin, arg_heatMax, arg_moistMin, arg_moistMax, arg_location))

    # ..............................WATERING............................................................
    # ................................................................................................

    def insert_water(self, arg_val):
        with self.conn:
            self.c.execute("INSERT INTO water values (:wateredTime,:amount)",
                           {'wateredTime': time.time(), 'amount': arg_val})

    def get_last_waterTime(self):
        self.c.execute("""SELECT * 
                          FROM water
                          WHERE wateredTime = (SELECT MAX(wateredTime) FROM water)
                      """)
        return self.c.fetchone()

    def get_many_waterTimes(self, arg):
        self.c.execute("""SELECT * 
                          FROM water 
                          ORDER BY wateredTime desc
                      """)
        return self.c.fetchmany(arg)

    # ..............................CONFIG............................................................
    # ................................................................................................

    def set_config(self, arg_config):
        with self.conn:
            self.c.execute("INSERT INTO pi_config values (:name,:light,:heat,:moist,:rain,:pump,:water_lvl,:door_left,:door_right)",
                           {'name': 'config',
                            'light': arg_config['light'],
                            'heat': arg_config['heat'],
                            'moist': arg_config['moist'],
                            'rain': arg_config['rain'],
                            'pump': arg_config['pump'],
                            'water_lvl': arg_config['water_lvl'],
                            'door_left': arg_config['door_left'],
                            'door_right': arg_config['door_right']
                            })

    def get_config(self):
        self.c.execute("""SELECT * 
                          FROM pi_config
                      """)
        return self.c.fetchone()

    def update_config(self, arg_config):
        with self.conn:
            arg_light = arg_config['light']
            arg_heat = arg_config['heat']
            arg_moist = arg_config['moist']
            arg_rain = arg_config['rain']
            arg_pump = arg_config['pump']
            arg_water_lvl = arg_config['water_lvl']
            arg_door_left = arg_config['door_left']
            arg_door_right = arg_config['door_right']

            self.c.execute("""UPDATE pi_config
                              SET light = ?, heat = ?, moist = ?,
                                  rain = ?, pump = ?, water_lvl = ?, door_left = ?, door_right = ?
                              WHERE name='config';
                          """, (arg_light, arg_heat, arg_moist, arg_rain, arg_pump, arg_water_lvl, arg_door_left, arg_door_right))

    # ................................................................................................

    def create_db(self):

        print("----------Begin DB creation-------------")
        try:
            self.conn = sqlite3.connect('piDB')
            self.c = self.conn.cursor()

            self.c.execute("""CREATE TABLE profile(
                                name text primary key,
                                light INTEGER,
                                heatMin INTEGER,
                                heatMax INTEGER,
                                moistMin INTEGER,
                                moistMax INTEGER,
                                location text
                            )""")
            self.c.execute("""CREATE TABLE sensors_log(
                                prob_date text primary key,
                                light INTEGER,
                                heat INTEGER,
                                moist INTEGER,
                                water_lvl INTEGER
                            )""")
            self.c.execute("""CREATE TABLE water(
                                wateredTime text primary key,
                                amount INTEGER 
                         )""")
            self.c.execute("""CREATE TABLE pi_config(
                                name text primary key,
                                light INTEGER,
                                heat INTEGER,
                                moist INTEGER,
                                rain INTEGER,
                                pump INTEGER,
                                water_lvl INTEGER,
                                door_left text,
                                door_right text
                         )""")

            self.conn.commit()
            self.c.close()
            self.conn.close()
            print('Creation completed successfully without errors!')
        except sqlite3.OperationalError as err:
            print("Error occurred while creating DB: ", err)

        print("----------End DB creation---------------")
