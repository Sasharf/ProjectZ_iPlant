import sqlite3
import sys


def create_db():

    print("----------------------BGN DB---------------------------------")
    try:
        conn = sqlite3.connect('piDB')
        c = conn.cursor()

        c.execute("drop table sensor_light")

        c.execute("""CREATE TABLE sensor_light(
                    date text,
                    value integer
             )""")

        c.execute("""CREATE TABLE sensor_heat(
                            date text,
                            value integer
                        )""")

        c.execute("""CREATE TABLE sensor_moist(
                                    date text,
                                    value integer
                                )""")

        c.execute("""CREATE TABLE sensor_rain(
                                    date text,
                                    value integer
                                )""")

        c.execute("""CREATE TABLE sensor_water_lvl(
                                    date text,
                                    value integer
                                )""")
        conn.commit()
        conn.close()
    except sqlite3.OperationalError as err:
        print(err)

    print("----------------------END DB---------------------------------")
