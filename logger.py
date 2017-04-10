# -*- coding: utf-8 -*-

"""Logging facility

Copyright (c) 2017 Iori Nishida <iori.nishida@connect-me.net>

loggingライブラリを使用してログをファイル(debug.log)に出力します。
プログラムのイベントやエラーに応じてloggingメソッドを以下のように使い分けてください。
    logging.debug() : デバッグ用の詳細情報を出力。
    logging.info() : 主要なイベントや情報を出力。
    logging.error() : エラーや例外を出力。ファイルに加えて標準出力にも出力します。
config.ini のDEBUG_LOG_LEVELを変更するとログファイルに出力するレベルが変更できます。

Create the Logger object and write the debug information to the logfile (debug.log).
Select to used as follows logging methods.
    logging.debug (): write the detail information for debugging.
    logging.info (): write the major events and information.
    logging.error (): write the error or exception, and also display to the
                          standard output.
If you change the DEBUG_LOG_LEVEL of the config.ini file. You can change the
level to be output to the log file.

"""

import logging

from config import cmConfig


class cmLogger():

    LOGGER_DEBUG_FILE = '/debug.log'

    def __init__(self):
        config = cmConfig()

        self.logger = logging.getLogger(__name__)
        formatter = logging.Formatter(
            '%(asctime)s - %(module)s - %(funcName)s - %(levelname)s - %(message)s')

        # setup debug level
        if config.option_list['DEFAULT']['DEBUG_LOG_LEVEL'] == 'DEBUG':
            self.logger.setLevel(logging.DEBUG)
        elif config.option_list['DEFAULT']['DEBUG_LOG_LEVEL'] == 'INFO':
            self.logger.setLevel(logging.INFO)
        elif config.option_list['DEFAULT']['DEBUG_LOG_LEVEL'] == 'ERROR':
            self.logger.setLevel(logging.ERROR)
        else:
            self.logger.setLevel(logging.DEBUG)

        # set File Handler DEBUG
        logger_file = config.option_list['DEFAULT'][
            'DATA_FILE_PATH'] + self.LOGGER_DEBUG_FILE
        self.fh = logging.FileHandler(logger_file)
        self.fh.setLevel(logging.DEBUG)
        self.fh.setFormatter(formatter)
        self.logger.addHandler(self.fh)

        # set Stream Handler ERROR
        self.sh = logging.StreamHandler()
        self.sh.setLevel(logging.ERROR)
        self.sh.setFormatter(formatter)
        self.logger.addHandler(self.sh)

    def getLogger(self):
        return self.logger
