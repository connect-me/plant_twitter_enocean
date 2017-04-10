# -*- coding: utf-8 -*-

"""Configuration settings

Copyright (c) 2017 Iori Nishida <iori.nishida@connect-me.net>

config.ini から設定情報を読み込みます。
option_list: config.iniを読み込んだconfigparserオブジェクトです。
device_list: 使用するEnOceanデバイスのデバイスIDとデバイス名のデバイスリスト
をディクショナリ形式で格納します。

Read the configuration information from the config.ini file.
option_list:The ConfigParser class object which was read a configuration
    files (config.ini).
device_list: The dictionary type object  of device list that was configured
    the device ID and the device model name.

"""


import configparser


class cmConfig():

    DATA_CONFIG_PATH = '.'
    DATA_CONFIG_FILE = '/config.ini'

    device_list = {}
    option_list = ''

    def __init__(self):
        cf_file = self.DATA_CONFIG_PATH + self.DATA_CONFIG_FILE
        self.option_list = configparser.ConfigParser()
        self.option_list.read(cf_file)

        devices = self.option_list['DEFAULT'][
            'ENOCEAN_DEVICE_LIST'].translate(str.maketrans('', '', ' '))
        for d in devices.split(','):
            self.device_list[d.split(':')[0].encode('utf-8').lower()] = d.split(':')[1].upper()
