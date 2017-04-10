# -*- coding: utf-8 -*-

"""Receive packet data of EnOcean devices via serial port, and register it into the database.

Copyright (c) 2017 Iori Nishida <iori.nishida@connect-me.net>

シリアルポートからEnOceanデバイスのパケットデータを受信します。
receiver.py は単独で動作するアプリケーションです。以下のように実行してください。

$ python3 ./receiver.py

使用するシリアルポートを変更したい場合は、config.ini の SERIAL_PORT を変更してください。
対応しているデバイスは、STM431J, PTM210J, STM429J です。
STM431J は、EEPのA5-10-03のプロファイルを使用しています。


Receive packet data of EnOcean devices via serial port.
This application works standalone. you can run as follows.

$ python3 ./receiver.py

If you want to change the devvice of serial port, change the SERIAL_PORT in the config.ini file.
Supported devices are STM431J, PTM210J and STM429J.
STM431J is used EEP A5-10-03.

"""


import sys
import traceback
import serial
import binascii
import struct
import time
import threading
from queue import Queue

from config import cmConfig
from logger import cmLogger
from register import PlantTwitterRegister
from parse import EnOceanTelegramParser


class PlantTwitterReceiver():

    def __init__(self, logger):
        self.logger = logger

        self.config = cmConfig()

    def receivePacket(self, eo_queue):
        """Receive packet data via serial port.

        シリアルポートからパケットを受信します。

        Receive packet data via serial port.
        """

        # open serial port
        config = cmConfig()
        serialport = config.option_list['DEFAULT']['SERIAL_PORT']

        eo_serial = serial.Serial(serialport, 57600,
                                  timeout=0.01, bytesize=8, parity='N', stopbits=1)

        if eo_serial.isOpen():
            self.logger.info("close serial port:{0}".format(serialport))
            eo_serial.close()

        self.logger.info("open serial port:{0}".format(serialport))
        eo_serial.open()

        if eo_serial.isOpen():
            self.logger.info("opened serial port:{0}".format(serialport))

        # read packet
        p_dat = b''
        p_dat_pre = b''
        p_list = []
        p_list_offset = 0
        p_list_length = 0
        eo_parser = EnOceanTelegramParser(self.logger)

        while True:

            # read packet 1 byte
            p_dat = binascii.hexlify(eo_serial.read(1))

            if p_dat == b'':
                continue

            # read sync packet b'55'
            if p_list_offset == 0:
                if p_dat == eo_parser.ESP3_HEADER_SYNC_BYTE:
                    p_list.append(p_dat)
                    p_list_offset += 1

            # read data length
            elif p_list_offset == 1:
                p_list.append(p_dat)
                p_list_offset += 1
                p_dat_pre = p_dat

            elif p_list_offset == 2:
                p_list.append(p_dat)
                p_list_offset += 1
                p_list_length = struct.unpack(
                    '>H', binascii.unhexlify(p_dat_pre + p_dat))[0]

            # read option length
            elif p_list_offset == 3:
                p_list.append(p_dat)
                p_list_offset += 1
                p_list_length += struct.unpack('>B', binascii.unhexlify(p_dat))[
                    0] + eo_parser.ESP3_HEADER_SIZE + 1
                self.logger.debug(
                    "receive packet length:{0}".format(p_list_length))

                # check max packet length
                if p_list_length > eo_parser.ESP3_MAX_PACKET_SIZE:
                    self.logger.error(
                        "receive packet exceeded max packet length:{0}".format(p_list_length))
                    p_dat_pre = b''
                    p_list = []
                    p_list_offset = 0
                    p_list_length = 0

            # read packet data
            elif p_list_offset < (p_list_length - 1):
                p_list.append(p_dat)
                p_list_offset += 1

            # set packet data to the thread queue
            elif p_list_offset >= (p_list_length - 1):
                p_list.append(p_dat)
                eo_queue.put(p_list)
                self.logger.info("receive packet data:{0}".format(p_list))
                p_dat_pre = b''
                p_list = []
                p_list_offset = 0
                p_list_length = 0

            # sleep 0.1 msec
            time.sleep(0.0001)


if __name__ == '__main__':

    # set logger handler
    logger = cmLogger().getLogger()
    logger.debug("--- start: {0} ----".format(__file__))

    # recieve packet data queue
    eo_queue = Queue()

    eo_receiver = PlantTwitterReceiver(logger)
    eo_register = PlantTwitterRegister(logger)

    # start thread data register
    try:
        logger.info("start thread: registerPacket")
        eo_thread = threading.Thread(
            target=eo_register.registerPacket, args=(eo_queue,))
        eo_thread.setDaemon(True)
        eo_thread.start()
    except:
        e_type, e_value, e_traceback = sys.exc_info()
        logger.error("Exception serial reading.:{0}".format(
            traceback.format_exception(e_type, e_value, e_traceback)))

    # start receiver packet
    logger.info("start: receivePacket")
    eo_receiver.receivePacket(eo_queue)

    logger.debug("--- end: {0} ----".format(__file__))
