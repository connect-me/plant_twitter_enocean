# -*- coding: utf-8 -*-

"""Get the measurement data of EnOcean module the STM431J.

Copyright (c) 2017 Iori Nishida <iori.nishida@connect-me.net>

profileモジュールはセンサーデータからセンサー情報を取得するためのモジュールで、
EnOcean Equipment Profiles毎にクラスを格納しています。
対応しているEnOcean Equipment Profilesは以下のとおりです。

A5-10-03: STM 431J + 土壌湿度センサー
A5-02-05: STM 431Jのみ
A5-04-01: STM 431J + HSM 100
F6-02-04: PTM 210J
D5-00-01: STM 429J

EnOceanTelegramParserクラスで解析したパケットデータを対応している
EnOceanEquipmentProfilesクラスに渡すことでセンサー情報を取得することができます。

EnOcean Equipment Profilesの仕様は、以下のドキュメントを参照してください。
    EnOcean Equipment Profiles(EEP) Version: 2.6.3
    URL: https://www.enocean.com/en/knowledge-base/

Get the measurement data from packet data of EnOcean devices.
Supported EnOcean Equipment Profiles is as follows.

A5-10-03: Temperature Sensor Range 0°C to +40°C, Set Point Control Range 0 to 255
A5-02-05: Temperature Sensor Range 0°C to +40°C
A5-04-01: Temperature Sensor Range 0°C to +40°C, Humidity Sensor Range 0% to 100%
F6-02-04: Rocker Switch, 2 Rocker, Light and blind control ERP2
D5-00-01: Contacts and Switches, Single Input Contact

To create instance of the EnOceanEquipmentProfile_A5_10_03 class, passes an argument
of an object that was parsed the packet data by EnOceanTelegramParser class.

The specification of EnOcean Equipment Profiles, refer to the following document.
    EnOcean Equipment Profiles(EEP) Version: 2.6.3
    URL: https://www.enocean.com/en/knowledge-base/

"""

import binascii
import struct

from logger import cmLogger


class EnOceanEquipmentProfile_A5_10_03():
    """Read EnOcean Equipment Profile: A5-10-03

    Target Device: STM431JS(with Soil Moisture)
        SEN0114: Soil Moisture Sensor

    RORG: A5: 4BS Telegram
    FUNC: 10: Room Operating Panel
    TYPE: 03: Temperature Sensor, Set Point Control
    """

    EEP_SET_POINT_CONTROL = 1
    EEP_TEMPERATURE_SENSOR = 2

    def __init__(self, enocean_data, logger):
        self.logger = logger
        self.enocean_data = enocean_data

        s_temp_bin = self.enocean_data.getDataDL()[self.EEP_TEMPERATURE_SENSOR]
        s_temp_val = struct.unpack('>B', binascii.unhexlify(s_temp_bin))[0]
        self.temperature = (255 - s_temp_val) * 40 / 255
        self.logger.debug("set temperature:{0:.2f}".format(self.temperature))

        s_point_bin = self.enocean_data.getDataDL()[self.EEP_SET_POINT_CONTROL]
        self.point_control = struct.unpack(
            '>B', binascii.unhexlify(s_point_bin))[0]
        self.logger.debug("set point control:{0}".format(self.point_control))

    def getTemperature(self):
        return self.temperature

    def getPointControl(self):
        return self.point_control


class EnOceanEquipmentProfile_A5_02_05():
    """Read EnOcean Equipment Profile: A5-02-05

    Target Device: STM431J

    RORG: A5: 4BS Telegram
    FUNC: 02: Temperature Sensors
    TYPE: 05: Temperature Sensor Range 0°C to +40°C
    """

    EEP_TEMPERATURE_SENSOR = 2

    def __init__(self, enocean_data, logger):
        self.logger = logger
        self.enocean_data = enocean_data

        s_temp_bin = self.enocean_data.getDataDL()[self.EEP_TEMPERATURE_SENSOR]
        s_temp_val = struct.unpack('>B', binascii.unhexlify(s_temp_bin))[0]
        self.temperature = (255 - s_temp_val) * 40 / 255
        self.logger.debug("set temperature:{0:.2f}".format(self.temperature))

    def getTemperature(self):
        return self.temperature


class EnOceanEquipmentProfile_A5_04_01():
    """Read EnOcean Equipment Profile: A5-04-01

    Target Device: STM431JH(with HSM100)

    RORG: A5: 4BS Telegram
    FUNC: 04: Temperature and Humidity Sensor
    TYPE: 01: Range 0°C to +40°C and 0% to 100%
    """

    EEP_HUMIDITY_SENSOR = 1
    EEP_TEMPERATURE_SENSOR = 2

    def __init__(self, enocean_data, logger):
        self.logger = logger
        self.enocean_data = enocean_data

        s_temp_bin = self.enocean_data.getDataDL()[self.EEP_TEMPERATURE_SENSOR]
        s_temp_val = struct.unpack('>B', binascii.unhexlify(s_temp_bin))[0]
        self.temperature = s_temp_val / 250 * 40
        self.logger.debug("set temperature:{0:.2f}".format(self.temperature))

        s_hum_bin = self.enocean_data.getDataDL()[self.EEP_HUMIDITY_SENSOR]
        s_hum_val = struct.unpack('>B', binascii.unhexlify(s_hum_bin))[0]
        self.humidity = s_hum_val / 250 * 100
        self.logger.debug("set humidity:{0:.2f}".format(self.humidity))

    def getTemperature(self):
        return self.temperature

    def getHumidity(self):
        return self.humidity


class EnOceanEquipmentProfile_D5_00_01():
    """Read EnOcean Equipment Profile: D5-00-01

    Target Device: STM429J

    RORG: D5: 1BS Telegram
    FUNC: 00: Contacts and Switches
    TYPE: 01: Single Input Contact
    """

    EEP_CONTACT_SWITCH = 0
    EEP_CONTACT_VALUE_OPEN = 0b00001000
    EEP_CONTACT_VALUE_CLOSE = 0b00001001

    def __init__(self, enocean_data, logger):
        self.logger = logger
        self.enocean_data = enocean_data

        s_con_bin = self.enocean_data.getDataDL()[self.EEP_CONTACT_SWITCH]
        s_con_val = struct.unpack('>B', binascii.unhexlify(s_con_bin))[0]

        if s_con_val == self.EEP_CONTACT_VALUE_OPEN:
            self.contact = 'open'
        else:
            self.contact = 'closed'

        self.logger.debug("set contact:{0}".format(self.contact))

    def getContact(self):
        return self.contact


class EnOceanEquipmentProfile_F6_02_04():
    """Read EnOcean Equipment Profile: F6-02-04

    Target Device: PTM210J

    RORG: F6: RBS Telegram
    FUNC: 02: Rocker Switch, 2 Rocker
    TYPE: 04: Light and blind control ERP2
    """

    EEP_ROCKER_SWITCH = 0
    EEP_ROCKER_BI_PRESSED = 0b10001000
    EEP_ROCKER_BO_PRESSED = 0b10000100
    EEP_ROCKER_AI_PRESSED = 0b10000010
    EEP_ROCKER_AO_PRESSED = 0b10000001

    def __init__(self, enocean_data, logger):
        self.logger = logger
        self.enocean_data = enocean_data

        self.s_roc_val = 0

        s_roc_bin = self.enocean_data.getDataDL()[self.EEP_ROCKER_SWITCH]
        self.s_roc_val = struct.unpack('>B', binascii.unhexlify(s_roc_bin))[0]

        self.roc_list = []
        if (self.s_roc_val & self.EEP_ROCKER_BI_PRESSED) == self.EEP_ROCKER_BI_PRESSED:
            self.roc_list.append('BI')
        if (self.s_roc_val & self.EEP_ROCKER_BO_PRESSED) == self.EEP_ROCKER_BO_PRESSED:
            self.roc_list.append('BO')
        if (self.s_roc_val & self.EEP_ROCKER_AI_PRESSED) == self.EEP_ROCKER_AI_PRESSED:
            self.roc_list.append('AI')
        if (self.s_roc_val & self.EEP_ROCKER_AO_PRESSED) == self.EEP_ROCKER_AO_PRESSED:
            self.roc_list.append('AO')

        self.logger.debug("set rocker pressed status:{0}".format(
            str(self.roc_list)))

    def getRockerList(self):
        return tuple(self.roc_list)
