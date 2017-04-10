# -*- coding: utf-8 -*-

"""Register and get the sensor data to the database.

Copyright (c) 2017 Iori Nishida <iori.nishida@connect-me.net>

EnOceanのセンサーデータをデータベースに登録と取得を行います。
初めて利用する時は、setup_db.shを実行してテーブルを作成してください。
'SENSORLOGS'テーブルの定義は以下のとおりです。

The sensor data of EnOcean get and registered in the database.
The first time you use, please create a table by running the setup_db.sh.
The definition of the 'SENSORLOGS' table are as follows.

SENSORLOGS:
    ID INTEGER PRIMARY KEY AUTOINCREMENT
    ORIGINATOR_ID TEXT
    DEVICE_MODEL TEXT
    TELEGRAM_TYPE TEXT
    DB_0 TEXT
    DB_1 TEXT
    DB_2 TEXT
    DB_3 TEXT
    DBM INTEGER
    TEMPERATURE INTEGER
    SOIL_MOISTURE INTEGER
    HUMIDITY INTEGER
    CONTACT_SWITCH TEXT
    ROCKER_SWITCH TEXT
    CREATE_AT TIMESTAMP DEFAULT (DATETIME('now','localtime'))
"""

import time
import datetime
import sqlite3

from config import cmConfig
from logger import cmLogger


class PlantTwitterDatastore():

    DATA_STORE_FILE = '/sensorlogs.db'

    ROW_INDEX_ORIGINATOR_ID = 0
    ROW_INDEX_DEVICE_MODEL = 1
    ROW_INDEX_TELEGRAM_TYPE = 2
    ROW_INDEX_DB_0 = 3
    ROW_INDEX_DB_1 = 4
    ROW_INDEX_DB_2 = 5
    ROW_INDEX_DB_3 = 6
    ROW_INDEX_DBM = 7
    ROW_INDEX_TEMPERATURE = 8
    ROW_INDEX_SOIL_MOISTURE = 9
    ROW_INDEX_HUMIDITY = 10
    ROW_INDEX_CONTACT_SWITCH = 11
    ROW_INDEX_ROCKER_SWITCH = 12
    ROW_INDEX_CREATE_AT = 13

    def __init__(self, logger):
        self.logger = logger

        config = cmConfig()
        self.db_file = config.option_list['DEFAULT'][
            'DATA_FILE_PATH'] + self.DATA_STORE_FILE

    def openConnection(self):
        self.logger.debug(
            "sqlite3: open connection:{0}".format(self.db_file))
        self.conn = sqlite3.connect(self.db_file)
        if isinstance(self.conn, sqlite3.Connection) is not True:
            self.logger.error(
                "sqlite3: Cannot open connection:{0}".format(self.db_file))
            return

    def closeConnection(self):
        if isinstance(self.conn, sqlite3.Connection):
            self.logger.debug(
                "sqlite3: close connection:{0}".format(self.db_file))
            self.conn.close()

    def insertRecord(self, *values):
        self.logger.info("insert values:{0}".format(values))

        # check value items
        values_length = len(values)
        if values_length != 13:
            self.logger.error(
                "Invalid value items.:{0}".format(values_length))
            return False

        sql = "INSERT INTO SENSORLOGS (ORIGINATOR_ID, DEVICE_MODEL, " + \
            "TELEGRAM_TYPE, DB_0, DB_1, DB_2, DB_3, DBM, TEMPERATURE, " + \
            "SOIL_MOISTURE, HUMIDITY, CONTACT_SWITCH, ROCKER_SWITCH) " + \
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

        try:
            self.conn.execute(sql, values)
            self.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(
                "sqlite3: Execute sql error:{0}".format(e.args[0]))
            return False

        return True

    def selectRecord(self, originator_id, device_model, rowcount=60):

        cur = self.conn.cursor()
        cur.arraysize = rowcount
        begin_date = (datetime.datetime.today() -
                      datetime.timedelta(minutes=60)).strftime('%Y-%m-%d %H:%M:%S')

        sql = "SELECT ORIGINATOR_ID, DEVICE_MODEL, TELEGRAM_TYPE, DB_0, " + \
            "DB_1, DB_2, DB_3, DBM, TEMPERATURE, SOIL_MOISTURE, HUMIDITY, " + \
            "CONTACT_SWITCH, ROCKER_SWITCH, CREATE_AT FROM SENSORLOGS " + \
            "WHERE ORIGINATOR_ID like '" + originator_id + "' and " + \
            "DEVICE_MODEL like '" + device_model + "' and " + \
            "DATETIME(CREATE_AT,'LOCALTIME') > DATETIME('" + begin_date + "','LOCALTIME')" + \
            "ORDER BY ID DESC LIMIT " + str(rowcount)

        self.logger.debug("select values :{0}".format(sql))

        try:
            cur.execute(sql)
            sensor_list = cur.fetchmany()
            cur.close()
        except sqlite3.Error as e:
            self.logger.error(
                "sqlite3: Execute sql error:{0}".format(e.args[0]))
            return ''

        return sensor_list
