import sqlite3
import sys
import os.path as path
import DB.Profile
import time


class PiDB:
    conn = sqlite3.connect('piDB')
    c = conn.cursor()

    def __init__(self):
        if not path.exists('piDB'):
            self.create_db(self)

        self.conn = sqlite3.connect('piDB')
        self.c = self.conn.cursor()

    def __del__(self):
        self.c.close()
        self.conn.close()

    # ............................LIGHT...............................................................
    # ................................................................................................

    def insert_light(self, arg_val):
        with self.conn:
            self.c.execute("INSERT INTO sensor_light values (:prob_date,:prob_val)",
                           {'prob_date': time.time(), 'prob_val': arg_val})

    def get_last_prob_light(self):
        self.c.execute("""SELECT * 
                          FROM sensor_light 
                          WHERE prob_date = (SELECT MAX(prob_date) FROM sensor_light)
                      """)
        return self.c.fetchone()

    def get_many_prob_light(self, arg):
        self.c.execute("""SELECT * 
                          FROM sensor_light 
                          ORDER BY prob_date desc
                      """)
        return self.c.fetchmany(arg)

    # ............................HEAT................................................................
    # ................................................................................................

    def insert_heat(self, arg_val):
        with self.conn:
            self.c.execute("INSERT INTO sensor_heat values (:prob_date,:prob_val)",
                           {'prob_date': time.time(), 'prob_val': arg_val})

    def get_last_prob_heat(self):
        self.c.execute("""SELECT * 
                          FROM sensor_heat 
                          WHERE prob_date = (SELECT MAX(prob_date) FROM sensor_heat)
                      """)
        return self.c.fetchone()

    def get_many_prob_heat(self, arg):
        self.c.execute("""SELECT * 
                          FROM sensor_heat 
                          ORDER BY prob_date desc
                      """)
        return self.c.fetchmany(arg)

    # ............................MOIST...............................................................
    # ................................................................................................

    def insert_moist(self, arg_val):
        with self.conn:
            self.c.execute("INSERT INTO sensor_moist values (:prob_date,:prob_val)",
                           {'prob_date': time.time(), 'prob_val': arg_val})

    def get_last_prob_moist(self):
        self.c.execute("""SELECT * 
                          FROM sensor_moist 
                          WHERE prob_date = (SELECT MAX(prob_date) FROM sensor_moist)
                      """)
        return self.c.fetchone()

    def get_many_prob_moist(self, arg):
        self.c.execute("""SELECT * 
                          FROM sensor_moist 
                          ORDER BY prob_date desc
                      """)
        return self.c.fetchmany(arg)

    # ............................RAIN................................................................
    # ................................................................................................

    def insert_rain(self, arg_val):
        with self.conn:
            self.c.execute("INSERT INTO sensor_rain values (:prob_date,:prob_val)",
                           {'prob_date': time.time(), 'prob_val': arg_val})

    def get_last_prob_rain(self):
        self.c.execute("""SELECT * 
                          FROM sensor_rain 
                          WHERE prob_date = (SELECT MAX(prob_date) FROM sensor_rain)
                      """)
        return self.c.fetchone()

    def get_many_prob_rain(self, arg):
        self.c.execute("""SELECT * 
                          FROM sensor_rain
                          ORDER BY prob_date desc
                      """)
        return self.c.fetchmany(arg)

    # ............................WATER_LVL...........................................................
    # ................................................................................................

    def insert_water_lvl(self, arg_val):
        with self.conn:
            self.c.execute("INSERT INTO sensor_water_lvl values (:prob_date,:prob_val)",
                           {'prob_date': time.time(), 'prob_val': arg_val})

    def get_last_prob_water_lvl(self):
        self.c.execute("""SELECT * 
                          FROM sensor_water_lvl
                          WHERE prob_date = (SELECT MAX(prob_date) FROM sensor_water_lvl)
                      """)
        return self.c.fetchone()

    def get_many_prob_water_lvl(self, arg):
        self.c.execute("""SELECT * 
                          FROM sensor_water_lvl 
                          ORDER BY prob_date desc
                      """)
        return self.c.fetchmany(arg)

    # ..............................PROFILE...........................................................
    # ................................................................................................

    def insert_profile(self, arg_profile):
        with self.conn:
            self.c.execute("INSERT INTO profiles values (:name,:light,:heat,:moist,:rain,:outside,:last_changed)",
                           {'name': arg_profile.name,
                            'light': arg_profile.light,
                            'heat': arg_profile.heat,
                            'moist': arg_profile.moist,
                            'outside': arg_profile.outside,
                            'last_changed': arg_profile.last_changed,
                            })

    def get_last_profile(self): # get last modified profile
        self.c.execute("""SELECT * 
                          FROM profiles
                          WHERE last_changed = (SELECT MAX(last_changed) FROM profiles)
                      """)
        return self.c.fetchone()

    # ..............................WATER............................................................
    # ................................................................................................

    def insert_water(self, arg_val):
        with self.conn:
            self.c.execute("INSERT INTO water values (:wateredTime)",
                           {'wateredTime': arg_val})

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

    # ................................................................................................

    def create_db(self):

        print("----------------------BGN DB---------------------------------")
        try:

            self.c.execute("""CREATE TABLE sensor_light(
                                prob_date text as primary key,
                                prob_val integer
                         )""")

            self.c.execute("""CREATE TABLE sensor_heat(
                                prob_date text as primary key,
                                prob_val integer
                            )""")

            self.c.execute("""CREATE TABLE sensor_moist(
                                prob_date text as primary key,
                                prob_val integer
                            )""")

            self.c.execute("""CREATE TABLE sensor_rain(
                                prob_date text as primary key,
                                prob_val integer
                            )""")

            self.c.execute("""CREATE TABLE sensor_water_lvl(
                                prob_date text as primary key,
                                prob_val integer
                            )""")

            self.c.execute("""CREATE TABLE profiles(
                                name text as primary key,
                                light INTEGER,
                                heat INTEGER,
                                moist INTEGER,
                                rain INTEGER,
                                last_changed text
                            )""")

            # ----------------
            # the next table will remember the last time it used the pump.
            # ----------------
            self.c.execute("""CREATE TABLE water(
                          wateredTime text as primary key
                         )""")

            self.conn.commit()
            self.conn.close()
        except sqlite3.OperationalError as err:
            print(err)

        print("----------------------END DB---------------------------------")
