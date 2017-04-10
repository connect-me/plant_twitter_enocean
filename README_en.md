# Shokubutsutter(植物ったー) for EnOcean

    version: 1.0.0
    update: 2017.1.2
    written by: Iori Nishida

### Overview

Shokubutsutter for EnOcean is an IoT(Internet of Things) application which can tweet the status of a plant using a temperature sensor module STM 431J of EnOcean Gmbh and a moisture sensor SEN0114.
For example, it tweets "The ground is drying. Give me water." when the soil humidity becomes low and tweets "Thank you for your watering." after you water it.

## Components

| File | Detail |
|---|---|
| .gitignore | setting file for GitHub |
| LICENSE | license of this application|
| README.md | this file(written by Japanese) |
| README_en.md | this file |
| config.ini | configuration information of this application |
| config.py | module loading configuration information |
| datastore.py | module reading/writing database|
| logger.py | module outputting log |
| message.py | module creating messages to tweet |
| parse.py | module analyzing data from EnOcean device |
| profile.py | module receiving sensor information from each EnOcean Equipment Profiles |
| receiver.py | application receiving data from EnOcean device |
| register.py | module registering data from EnOcean device on database |
| setup_db.sh | script creating database file |
| test_receiver.py | test program receiving packets from EnOcean device |
| test_tweet.py | test program tweeting sensor data restored database |
| tweet.py | application tweeting sensor data stored database |
| debug.log | log file of Shokubutsutter, which is created automatically when the program runs |
| sensorlogs.db | database file of Shokubutsutter, which is created by setup_db.sh |

## Requirements

### Language
    Python: version 3.x (we have tested with Python3.4.2)

### Application Outline

| item | content |
|---|---|
| Type | STM431JS:temperature and soil moisture(default)<br> STM431J:only temperature<br> STM431JH:temperature and moisture |
| EnOcean-capable module | STM 431J, USB 400J, HSM 100, PTM 210J, STM 429J<br> ※ PTM 210J and STM 429J are capable only of receiving sensor data |
| EnOcean-capable Equipment Profiles | STM 431J + soil moisture sensor (default): A5-10-03<br> STM 431J: A5-02-05<br> STM 431J + HSM 100: A5-04-01<br> PTM 210J: F6-02-04<br> STM 429J: D5-00-01 |
| sensor specifications | temperature sensor(0℃-40℃), soil mosture sensor(0-255), moisture sensor(0％-100％)<br> ※ Either a soil moisture sensor or a moisture sensor can be used |
| condition to tweet | receive sensor data in 60 minutes |
| time to tweet | from 4:00 to 21:00 |
| tweet interval | every 30 minutes |
| watering detection | tweet when it rises in moisture in 30 minutes |
| variety of messages | 12 messages(7 messages about temperature, 4 messages of soil moisture and a message of humidity) |

## Installation
* install this application

    $ git clone https://github.com/connect-me/plant_twitter_enocean.git

* install sqlite3 and twitter modules

    $ sudo apt-get install sqlite3  
    $ sudo pip3 install twitter

* create database

    $ ./setup_db.sh 

* set a Twitter access token and consumer key

In order to use Twitter API, you need a token of Twitter account and a consumer key.
Create them on the Twitter site for developers(https://dev.twitter.com/) and write them on config.ini.

    TWITTER_ACCESS_TOKEN : Access Token
    TWITTER_ACCESS_SECRET : Access Token Secret
    TWITTER_CONSUMER_KEY : Consumer Key (API Key)
    TWITTER_CONSUMER_SECRET : Consumer Secret (API Secret)

* setting of an EnOcean device

Write device ID and device model of your EnOcean device on config.ini.
You can see device ID of your EnOcean device on the DolphinView Advanced.
Device model corresponds to each device as below:

| device model | capable device | capable EnOcean Equipment Profiles |
|---|---|---|
| STM431J | STM431J | A5-02-05 |
| STM431JS | STM431J + SEN0114(Soil Moisture) | A5-10-03 |
| STM431JH | STM431J + HSM100 | A5-04-01 |
| PTM210J | PTM210J | F6-02-04 |
| STM429J | STM429J | D5-00-01 |

Punctuate device ID and device model with a colon(:) and use a comma between the multiple IDs.  

    ENOCEAN_DEVICE_LIST:  {originator id}:{device model}
    ex) ENOCEAN_DEVICE_LIST:  040154f1:STM431JS,002b93c6:PTM210J

    DolphinView Advanced -  EnOcean Development Tools
    https://www.enocean.com/en/download/

## How to test
* packet receiving test from an EnOcean device

    $ python3 ./test_receiver.py

* test of tweeting sensor data

    $ python3 ./test_tweet.py

The results of testing mentioned above are outputted on debug.log.
If you want to check detailed log, alter DEBUG_LOG_LEVEL on config.ini to "DEBUG".

## execute application

    $ python3 ./receiver.py &
    $ python3 ./tweet.py &


## License
This appplication is distributed under the MIT LICENSE.  
Your can see detail at [LICENSE](https://github.com/connect-me/plant_twitter_enocean/blob/master/LICENSE).

Shokubutsutter(植物ったー) is a plant communication application developed by connect-me.
You can learn more at http://connect-me-net.tumblr.com/

EnOcean is a technology of energy harvesting wireless sensor by EnOcean GmbH.
You can see detail at https://www.enocean.com/jp/

## Author

Copyright (c) 2017 Iori Nishida <iori.nishida@connect-me.net>
