# -*- coding: utf-8 -*-

"""Create a message, and tweet it on Twitter.

Copyright (c) 2017 Iori Nishida <iori.nishida@connect-me.net>

蓄積したセンサーデータをもとにツイートするメッセージを作成してTwitterでツイートします。
tweet.py は単独で動作するアプリケーションです。以下のように実行してください。

$ python3 ./tweet.py

tweetモジュールはTwitter APIを利用します。
Twitter APIの利用するためには、Twitterアカウントのアクセストークン、コンシューマーキー
が必要です。
Twitterのデベロッパーサイト https://dev.twitter.com/ で作成して、config.ini の以下に
記載してください。

    TWITTER_ACCESS_TOKEN : Access Token
    TWITTER_ACCESS_SECRET : Access Token Secret
    TWITTER_CONSUMER_KEY : Consumer Key (API Key)
    TWITTER_CONSUMER_SECRET : Consumer Secret (API Secret)


Create a message from the stored sensor data, and tweet it on Twitter.
This application works standalone. you can run as follows.

$ python3 ./tweet.py

The tweet module makes use of the Twitter API.
To the use of the Twitter API, requires the access token and the consumer key of
your twitter account.
You will create the keys from the twitter developers site: https://dev.twitter.com/,
and write them to the following the config.ini file.

    TWITTER_ACCESS_TOKEN : Access Token
    TWITTER_ACCESS_SECRET : Access Token Secret
    TWITTER_CONSUMER_KEY : Consumer Key (API Key)
    TWITTER_CONSUMER_SECRET : Consumer Secret (API Secret)

"""


import sys
import traceback
import time
import datetime

from twitter import Twitter, OAuth

from config import cmConfig
from logger import cmLogger
from message import PlantTwitterMessage


class PlantTwitterTweet():

    def __init__(self, logger):
        self.logger = logger

        self.config = cmConfig()

        # Set next tweet time.
        self.next_datetime = datetime.datetime.today() - datetime.timedelta(minutes=20)

        # Tweet a message quickly, if watering.
        self.state_watering = False

        # set twitter.com OAuth key
        self.access_token = self.config.option_list[
            'Twitter']['TWITTER_ACCESS_TOKEN']
        self.access_secret = self.config.option_list[
            'Twitter']['TWITTER_ACCESS_SECRET']
        self.consumer_key = self.config.option_list[
            'Twitter']['TWITTER_CONSUMER_KEY']
        self.consumer_secret = self.config.option_list[
            'Twitter']['TWITTER_CONSUMER_SECRET']

        # Ignore time condition, if clock_check is flase.
        if self.config.option_list['Twitter']['MESSAGE_CLOCK_CHECK'] == 'True':
            self.clock_check = True
        else:
            self.clock_check = False

    def tweetMessage(self):

        now_datetime = datetime.datetime.today()
        eo_message = PlantTwitterMessage(self.logger)
        tweet_update = False

        # Tweet time conditions. : only between 20:00 from 4:00.
        if self.clock_check:
            if now_datetime.hour < 4 or now_datetime.hour > 20:
                self.logger.debug("tweetMessage: don't tweet time(20:00-4:00).:{0}".format(
                    now_datetime.strftime('%Y-%m-%d %H:%M:%S')))
                return

        # EnOcean devices tweet a message individually.
        for b_sensor_id, device_model in self.config.device_list.items():

            message = ''

            # create message
            (message, now_watering) = eo_message.createMessage(
                b_sensor_id.decode('utf-8'), device_model)

            # Skip no message
            if message == '':
                continue

            # Tweet a message quickly, if watering.
            if self.state_watering is False and now_watering is True:
                # Send message
                tweet_update = self.sendMessage(message)

                # Ignore a watering status for 30 minutes.
                self.state_watering = True

            else:
                # Tweet time conditions. : Ignore the tweet for 30 minutes.
                if self.clock_check and (now_datetime < self.next_datetime):
                    self.logger.debug("tweetMessage: tweet every 30 minutes.:next tweet time {0}".format(
                        self.next_datetime.strftime('%Y-%m-%d %H:%M:%S')))

                else:
                    # Send message
                    tweet_update = self.sendMessage(message)

                    # Available a watering status.
                    self.state_watering = False

        if tweet_update:
            # Set next tweet time after 30 minutes.
            self.next_datetime = now_datetime + datetime.timedelta(minutes=30)

    def sendMessage(self, message):

        # Create instance of twitter
        eo_twitter = Twitter(auth=OAuth(
            self.access_token, self.access_secret, self.consumer_key, self.consumer_secret))

        self.logger.info("sendMessage:'{0}'".format(message))

        # Tweet message
        try:
            eo_twitter.statuses.update(status=message)

            # tweet interval 1.0 sec
            time.sleep(1)

        except:
            e_type, e_value, e_traceback = sys.exc_info()
            self.logger.error("Exception serial reading.:{0}".format(
                traceback.format_exception(e_type, e_value, e_traceback)))
            return False

        return True


if __name__ == '__main__':

    # set logger handler
    logger = cmLogger().getLogger()

    logger.debug("--- start: {0} ----".format(__file__))

    eo_tweet = PlantTwitterTweet(logger)

    while True:
        eo_tweet.tweetMessage()
        time.sleep(60)

    logger.debug("--- end: {0} ----".format(__file__))
