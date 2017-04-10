# -*- coding: utf-8 -*-

"""Test tweet to Twitter.com

Copyright (c) 2017 Iori Nishida <iori.nishida@connect-me.net>

センサーデータをデータベースから取得してツイートします。
テストしたいデータは、test_sensorを書き換えてください。
以下のコマンドを実行してください。

$ python3 ./test_tweet.py

Create a message from the stored sensor data, and tweet it on Twitter.
To change a tweet message, change a test_sensor.
This test program works standalone. you can run as follows.

$ python3 ./test_tweet.py


"""

import time

from config import cmConfig
from logger import cmLogger
from datastore import PlantTwitterDatastore
from tweet import PlantTwitterTweet

# test sensor data list
test_sensor = (
    # STM431JS: Wet condition
    [b'040154f1', 'STM431JS', '4BS', b'00', b'98', b'c1',
        b'08', -65, 9.72549019607843, 152, '', '', ''],

    # STM431JS: A liite dry condition
    [b'040154f1', 'STM431JS', '4BS', b'00', b'6e', b'40',
        b'0a', -68, 29.9607843137255, 110, '', '', ''],

    # STM431JS: Dry condition
    [b'040154f1', 'STM431JS', '4BS', b'00', b'5a', b'50',
        b'0a', -68, 27.4509803921569, 90, '', '', ''],

    # STM431JS: Thanks
    [b'040154f1', 'STM431JS', '4BS', b'00', b'98', b'b2',
        b'08', -65, 12.078431372549, 152, '', '', ''],

    # STM431JH: Humidity
    [b'040154f1', 'STM431JH', '4BS', b'00', b'6a',
        b'44', b'0a', -65, 10.88, '', 42, '', ''],

    # STM431J: Temperature
    [b'040154f1', 'STM431J', '4BS', b'00', b'00', b'8b',
        b'08', -61, 18.1960784313725, '', '', '', '']
)

if __name__ == '__main__':

    # set logger handler
    logger = cmLogger().getLogger()
    logger.info("--- start: {0} ----".format(__file__))

    # read device list
    config = cmConfig()

    # set clock check False
    eo_tweet = PlantTwitterTweet(logger)
    eo_tweet.clock_check = False

    # insert test value
    data_store = PlantTwitterDatastore(logger)
    data_store.openConnection()
    for b_sensor_id, device_model in config.device_list.items():
        for values in test_sensor:
            if device_model == values[1]:
                values[0] = b_sensor_id
                data_store.insertRecord(*values)
    data_store.closeConnection()

    # tweet message
    eo_tweet.tweetMessage()

    logger.info("--- end: {0} ----".format(__file__))
