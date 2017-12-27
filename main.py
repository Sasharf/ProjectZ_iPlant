from DB import DB


def __main__():

    piDB = DB.PiDB()
    piDB.create_db()
    piDB.insert_light(0.01, "sensor_light")


__main__()
