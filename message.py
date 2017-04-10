# -*- coding: utf-8 -*-

"""Create a message from sensor data.

Copyright (c) 2017 Iori Nishida <iori.nishida@connect-me.net>

センサーデータをデータベースから取得を行い、センサーデータの条件から
メッセージを作成します。対応しているデバイスは、以下の通りです。

STM431JS(with Soil Moisture): A5-10-03
STM431J: A5-02-05
STM431JH(with HSM100): A5-04-01

Get sensor data from the database, and create a message from the
condition of the sensor data.
Operating check devices are as follows.

STM431JS(with Soil Moisture): A5-10-03
STM431J: A5-02-05
STM431JH(with HSM100): A5-04-01

"""

import time
import datetime

from config import cmConfig
from logger import cmLogger
from datastore import PlantTwitterDatastore


class PlantTwitterMessage():

    SUPPORTED_DEVICES = ('STM431J', 'STM431JS', 'STM431JH')

    sensor_logs = []

    def __init__(self, logger):
        self.logger = logger
        self.config = cmConfig()

        self.soil_moisture_dry = int(self.config.option_list['Message'][
                                     'MESSAGE_CONDITION_SOIL_MOISTURE_DRY'])
        self.soil_moisture_a_little_dry = int(self.config.option_list['Message'][
                                              'MESSAGE_CONDITION_SOIL_MOISTURE_A_LITLE_DRY'])

    def createMessage(self, sensor_id, device_model):

        message = ''
        message_opt = ''
        message_hashtag = ''
        now_watering = False

        # Check supported devices
        if device_model not in self.SUPPORTED_DEVICES:
            self.logger.debug("Unsupported device model.: sensor_id = {0}: device_model = {1}".format(
                sensor_id, device_model))
            return (message, now_watering)

        # Get sensor data from the database
        sensor_rows = self.readSensorLogs(sensor_id, device_model)
        if sensor_rows == 0:
            self.logger.debug("createMessage: no sensor logs.")
            return (message, now_watering)

        data_store = PlantTwitterDatastore(self.logger)
        sensor_time = time.strptime(
            self.sensor_logs[0][data_store.ROW_INDEX_CREATE_AT], '%Y-%m-%d %H:%M:%S')
        sensor_datetime = datetime.datetime(sensor_time.tm_year, sensor_time.tm_mon,
                                            sensor_time.tm_mday, sensor_time.tm_hour,
                                            sensor_time.tm_min, sensor_time.tm_sec)

        # Create a hash hag of Twitter
        now_datetime = datetime.datetime.today()
        message_hashtag = now_datetime.strftime(
            " %m/%d %H:%M ") + self.config.option_list['Message']['MESSAGE_TABLE_HASH_TAG']

        # Create a message for soil moisture condition.
        if device_model == 'STM431JS':

            sensor_soilmoisture = self.sensor_logs[
                0][data_store.ROW_INDEX_SOIL_MOISTURE]

            # Soil moisture conditions. : water the plant within 30 minutes
            for sensor_row in self.sensor_logs:

                past_sensor_soilmoisture = sensor_row[
                    data_store.ROW_INDEX_SOIL_MOISTURE]

                past_time = time.strptime(
                    sensor_row[data_store.ROW_INDEX_CREATE_AT], '%Y-%m-%d %H:%M:%S')
                past_datetime = datetime.datetime(past_time.tm_year, past_time.tm_mon,
                                                  past_time.tm_mday, past_time.tm_hour,
                                                  past_time.tm_min, past_time.tm_sec)

                if now_datetime - past_datetime > datetime.timedelta(minutes=30):
                    break

                if (sensor_soilmoisture - past_sensor_soilmoisture) > 10 and \
                        sensor_soilmoisture >= self.soil_moisture_dry:

                    message_opt = self.config.option_list['Message'][
                        'MESSAGE_TABLE_SOILMOISTURE_THANKYOU']
                    message_opt = message_opt.replace(
                        '{0}', str(sensor_soilmoisture))
                    now_watering = True

            # Soil moisture conditions. : no water the plant within 30 minutes
            if message_opt == '':

                # Soil moisture conditions. : dry condition
                if sensor_soilmoisture < self.soil_moisture_dry:
                    message_opt = self.config.option_list['Message'][
                        'MESSAGE_TABLE_SOILMOISTURE_DRY']
                    message_opt = message_opt.replace(
                        '{0}', str(sensor_soilmoisture))

                # Soil moisture conditions. : a little :dry condition
                elif sensor_soilmoisture < self.soil_moisture_a_little_dry:
                    message_opt = self.config.option_list['Message'][
                        'MESSAGE_TABLE_SOILMOISTURE_A_LITTLE_DRY']
                    message_opt = message_opt.replace(
                        '{0}', str(sensor_soilmoisture))

                # Soil moisture conditions. : wet condition
                else:
                    message_opt = self.config.option_list[
                        'Message']['MESSAGE_TABLE_SOILMOISTURE_WET']
                    message_opt = message_opt.replace(
                        '{0}', str(sensor_soilmoisture))

            self.logger.debug("message opt:{0}".format(message_opt))

        # Create a message for humidity condition.
        if device_model == 'STM431JH':
            sensor_humidity = self.sensor_logs[
                0][data_store.ROW_INDEX_HUMIDITY]

            message_opt = self.config.option_list[
                'Message']['MESSAGE_TABLE_HUMIDITY']
            message_opt = message_opt.replace('{0}', str(sensor_humidity))

            self.logger.debug("message opt:{0}".format(message_opt))

        # Create a message for each temperature condition.
        sensor_temperature = self.sensor_logs[
            0][data_store.ROW_INDEX_TEMPERATURE]

        if sensor_temperature < 10:
            message = self.config.option_list[
                'Message']['MESSAGE_TABLE_TEMPERATURE_0']
        elif sensor_temperature < 15:
            message = self.config.option_list['Message'][
                'MESSAGE_TABLE_TEMPERATURE_10']
        elif sensor_temperature < 20:
            message = self.config.option_list['Message'][
                'MESSAGE_TABLE_TEMPERATURE_15']
        elif sensor_temperature < 25:
            message = self.config.option_list['Message'][
                'MESSAGE_TABLE_TEMPERATURE_20']
        elif sensor_temperature < 30:
            message = self.config.option_list['Message'][
                'MESSAGE_TABLE_TEMPERATURE_25']
        elif sensor_temperature < 35:
            message = self.config.option_list['Message'][
                'MESSAGE_TABLE_TEMPERATURE_30']
        else:
            message = self.config.option_list['Message'][
                'MESSAGE_TABLE_TEMPERATURE_35']

        message = message.replace('{0}', str(round(sensor_temperature, 1)))
        message = message.replace('{1}', message_opt)
        message += message_hashtag

        self.logger.debug("create message:{0} watering:{1}".format(
            message, str(now_watering)))

        return (message, now_watering)

    def readSensorLogs(self, sensor_id, device_model):

        rows_count = 0

        data_store = PlantTwitterDatastore(self.logger)
        data_store.openConnection()

        self.sensor_logs = data_store.selectRecord(sensor_id, device_model)
        rows_count = len(self.sensor_logs)

        self.logger.debug("readSensorLogs: rows={0}".format(rows_count))
        for r in self.sensor_logs:
            id = r[data_store.ROW_INDEX_ORIGINATOR_ID]
            create_at = r[data_store.ROW_INDEX_CREATE_AT]
            temp = r[data_store.ROW_INDEX_TEMPERATURE]
            soil = r[data_store.ROW_INDEX_SOIL_MOISTURE]

        data_store.closeConnection()

        return rows_count
