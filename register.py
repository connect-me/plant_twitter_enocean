# -*- coding: utf-8 -*-

"""Parse packet data and register it into the database.

Copyright (c) 2017 Iori Nishida <iori.nishida@connect-me.net>

EnOceanデバイスのパケットデータからセンサー情報を取得してデータベースに登録します。
対応しているデバイスは、STM431J, PTM210J, STM429J です。

Get the measurement data from packet data of EnOcean devices, and register it into the database.
Supported devices are STM431J, PTM210J and STM429J.

"""


import sys
import traceback
import time
from queue import Queue

from config import cmConfig
from logger import cmLogger
from datastore import PlantTwitterDatastore
from parse import EnOceanTelegramParser
from profile import EnOceanEquipmentProfile_A5_10_03
from profile import EnOceanEquipmentProfile_A5_02_05
from profile import EnOceanEquipmentProfile_A5_04_01
from profile import EnOceanEquipmentProfile_D5_00_01
from profile import EnOceanEquipmentProfile_F6_02_04


class PlantTwitterRegister():

    def __init__(self, logger):
        self.logger = logger

        self.config = cmConfig()

    def parsePacket(self, packet):
        """Parse received paket data, and create sensor values.

        受信したパケットデータを解析してセンターの値を取得します。
        IDとデバイスモデルを記載したデバイスリストは config.ini 確認してください。

        Parse received paket data, and create sensor values.
        Device list of Originator ID and device model, please see the config.ini file.
        """

        self.logger.info("parse packet:{0}".format(packet))

        values = ()

        # parse packet data
        eo_parser = EnOceanTelegramParser(self.logger)
        ret = eo_parser.parseTelegramData(packet)
        self.logger.info("parse packet result:{0}".format(ret))
        if ret is not True:
            self.logger.error("Cannnot parse packet.")
            return values

        # get Originator ID, Telegram Type
        id = eo_parser.getOriginatorID()
        type = eo_parser.getTelegramType()

        # check device list. please see the config.ini.
        if len(id) == 12 and id[:4] == b'0000':
          id = id[-8:]

        if id in self.config.device_list:

            device_model = self.config.device_list[id]

            # Target Device: STM431JS(with Soil Moisture Sensor)
            if device_model == 'STM431JS':

                eo_profile = EnOceanEquipmentProfile_A5_10_03(
                    eo_parser, self.logger)
                temp = eo_profile.getTemperature()
                moisture = eo_profile.getPointControl()

                data_dl = eo_parser.getDataDL()
                dbm = eo_parser.getDbm()

                self.logger.info("parse packet:id={0} device={1} type={2} temperature={3:.2f} \
                    soil moisture={4} dbm={5}".format(id, device_model, type, temp, moisture, dbm))

                values = (id, device_model, type, data_dl[0],  data_dl[1],  data_dl[
                          2],  data_dl[3], dbm, temp, moisture, '', '', '')

                self.logger.debug("set datastore values:{0}".format(values))

            # Target Device: STM431J
            elif device_model == 'STM431J':

                eo_profile = EnOceanEquipmentProfile_A5_02_05(
                    eo_parser, self.logger)
                temp = eo_profile.getTemperature()

                data_dl = eo_parser.getDataDL()
                dbm = eo_parser.getDbm()

                self.logger.info("parse packet:id={0} device={1} type={2} temperature={3:.2f} \
                    dbm={4}".format(id, device_model, type, temp, dbm))

                values = (id, device_model, type, data_dl[0],  data_dl[
                          1],  data_dl[2],  data_dl[3], dbm, temp, '', '', '', '')

                self.logger.debug("set datastore values:{0}".format(values))

            # Target Device: STM431JH(with HSM100)
            elif device_model == 'STM431JH':

                eo_profile = EnOceanEquipmentProfile_A5_04_01(
                    eo_parser, self.logger)
                temp = eo_profile.getTemperature()
                humidity = int(round(eo_profile.getHumidity(), 0))

                data_dl = eo_parser.getDataDL()
                dbm = eo_parser.getDbm()

                self.logger.info("parse packet:id={0} device={1} type={2} temperature={3:.2f} \
                    humidity={4} dbm={5}".format(id, device_model, type, temp, humidity, dbm))

                values = (id, device_model, type, data_dl[0],  data_dl[1],  data_dl[
                          2],  data_dl[3], dbm, temp, '', humidity, '', '')

                self.logger.debug("set datastore values:{0}".format(values))

            # Target Device: STM429J
            elif device_model == 'STM429J':

                eo_profile = EnOceanEquipmentProfile_D5_00_01(
                    eo_parser, self.logger)
                contact = eo_profile.getContact()

                data_dl = eo_parser.getDataDL()
                dbm = eo_parser.getDbm()

                self.logger.info("parse packet:id={0} device={1} type={2} contact={3} dbm={4}".format(
                    id, device_model, type, contact, dbm))

                values = (id, device_model, type, data_dl[
                          0],  '',  '',  '', dbm, '', '', '', contact, '')

                self.logger.debug("set datastore values:{0}".format(values))

            # Target Device: PTM210J
            elif device_model == 'PTM210J':

                eo_profile = EnOceanEquipmentProfile_F6_02_04(
                    eo_parser, self.logger)
                rocker = ','.join(eo_profile.getRockerList())

                data_dl = eo_parser.getDataDL()
                dbm = eo_parser.getDbm()

                self.logger.info("parse packet:id={0} device={1} type={2} rocker={3} dbm={4}".format(
                    id, device_model, type, rocker, dbm))

                values = (id, device_model, type, data_dl[
                          0],  '',  '',  '', dbm, '', '', '', '', rocker)

                self.logger.debug("set datastore values:{0}".format(values))

            # Unsupported Device
            else:
                data_dl = eo_parser.getDataDL()
                dbm = eo_parser.getDbm()

                self.logger.error("unsupported device:id={0} device={1} type={2} data_dl={3} \
                    dbm={4}".format(id, device_model, type, data_dl[0], dbm))

        else:
            self.logger.error("Device id is not found in device list:{0}. see config.ini.".format(
                id.decode('utf-8')))

        return values

    def registerPacket(self, eo_queue):
        """register packet data into the database.

        受信したパケットデータを解析して、データベースに登録します。
        この関数は、スレッドとして起動されます。

        Receive packet data, and register it into the database.
        This function is called by thread object.
        """

        time.sleep(0.1)

        # open database
        data_store = PlantTwitterDatastore(self.logger)

        while True:
            if eo_queue.empty() is False:

                # read packet from the thread queue
                item = eo_queue.get()

                # parse packet
                values = self.parsePacket(item)

                # register sensor data to the database
                if values != '':
                    data_store.openConnection()

                    if data_store.insertRecord(*values):
                        self.logger.info(
                            "register sensor data result: Success")
                    else:
                        self.logger.error(
                            "register sensor data result: Failure")

                    data_store.closeConnection()

                eo_queue.task_done()

            # sleep 1.0 msec
            time.sleep(0.001)
