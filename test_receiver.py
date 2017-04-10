# -*- coding: utf-8 -*-

"""Test receive a packet data of EnOcean devices via serial port

Copyright (c) 2017 Iori Nishida <iori.nishida@connect-me.net>

シリアルポートからEnOceanデバイスのパケットデータを受信するテストプログラムです。
シリアルポートの設定は、config.ini のSERIAL_PORTを確認してください。
以下のコマンドを実行してください。

$ python3 ./test_receiver.py

This is the test program that receive a packet data of EnOcean devices via serial port.
To setup the serial port, confirm a 'SERIAL_PORT' in a config.ini file.
This application works standalone. you can run as follows.

$ python3 ./test_receiver.py

"""


from queue import Queue

from logger import cmLogger
from receiver import PlantTwitterReceiver

if __name__ == '__main__':

    # set logger handler
    logger = cmLogger().getLogger()
    logger.debug("--- start: {0} ----".format(__file__))

    # recieve packet data queue
    eo_queue = Queue()

    eo_receiver = PlantTwitterReceiver(logger)

    # start receiver packet
    logger.info("start: receivePacket")
    eo_receiver.receivePacket(eo_queue)

    logger.debug("--- end: {0} ----".format(__file__))
