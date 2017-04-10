# -*- coding: utf-8 -*-

"""Parse the packet data received from the EnOcean device.

Copyright (c) 2017 Iori Nishida <iori.nishida@connect-me.net>

EnOceanデバイスから受信したパケットデータを解析してデータを抽出します。
動作確認しているデバイスは、STM431J, PTM210J, STM429J です。
パケットデータの解析の仕様は、以下のドキュメントを参照してください。
    EnOcean Serial Protocol 3 (ESP3) Version 1.27
    EnOcean Radio Protocol 2(ERP2)   Version 1.0
    URL: https://www.enocean.com/en/knowledge-base/

解析可能なパケットタイプは、Radio ERP2 のみです。
詳しくは、ESP3ドキュメントの'1.14 Packet Type 10: RADIO_ERP2'を参照してください。

パケットデータを解析するには、parseTelegramData()の引数に受信したパケットデータ
を渡してください。
取得できるデータは、OriginatorID, TelegramType, DataDL, Dbm です。
センサーの測定データを取得したい場合は、profileモジュールを使用してください。
ヘッダーサイズが6バイト以下のパケットデータは対応してません。

Parse the packet data received from the EnOcean device, and get the sensor data.
Operating check devices are STM431J, PTM210J and STM429J.
Specification of analysis of packet data, please refer to the following documents.
    EnOcean Serial Protocol 3 (ESP3) Version 1.27
    EnOcean Radio Protocol 2(ERP2)   Version 1.0
    URL: https://www.enocean.com/en/knowledge-base/

The avairable packet type is Radio ERP2.
Refer to the '1.14 Packet Type 10: RADIO_ERP2' of ESP3 documents.

To parse the packet data, passes an received packet data to a argument of
parseTelegramData().
Available data are OriginatorID, TelegramType, DataDL and Dbm.
To get the measured data of the sensor, use the profile module.
NOTE: Not supported the packet data header size is less than 6 bytes.

"""

import binascii
import struct

from logger import cmLogger


class EnOceanTelegramParser():

    # ESP3 header structure
    ESP3_HEADER_SIZE = 6
    ESP3_HEADER_SYNC_BYTE = b'55'

    # ESP3 Packet Type 10: RADIO_ERP2
    ESP3_PACKET_TYPE_RADIO_ERP2 = 10

    # ESP3 Max. size of transferred data
    ESP3_MAX_PACKET_SIZE = 65535

    # ERP2 header structure: 4.5 Data contents for Length > 6 Bytes
    ERP2_HEADER_ADDCTRL_ID24_NODIST = 0b00000000
    ERP2_HEADER_ADDCTRL_ID32_NODIST = 0b00100000
    ERP2_HEADER_ADDCTRL_ID32_DIST32 = 0b01000000
    ERP2_HEADER_ADDCTRL_ID48_NODIST = 0b01100000
    ERP2_HEADER_ADDCTRL = 0b11100000
    ERP2_HEADER_EXTENDED_HEADER_NOEXTENDED = 0b00000000
    ERP2_HEADER_EXTENDED_HEADER_AVAILABLE = 0b00010000
    ERP2_HEADER_EXTENDED_HEADER = 0b00010000
    ERP2_HEADER_TELEGRAM_TYPE_RPS = 0b00000000
    ERP2_HEADER_TELEGRAM_TYPE_1BS = 0b00000001
    ERP2_HEADER_TELEGRAM_TYPE_4BS = 0b00000010
    ERP2_HEADER_TELEGRAM_TYPE = 0b00001111

    def __init__(self, logger):
        self.logger = logger

        # receive packet data
        self.packet_data = []
        self.packet_length = 0

        # ESP3 data structure
        self.sync_byte = b''
        self.data_length = 0
        self.optional_length = 0
        self.packet_types = 0
        self.header_crc8h = b''
        self.optional_subtelnum = 0
        self.optional_dbm = 0
        self.header_crd8d = b''

        # ERP2 data structure
        self.addctrl = 0b11100000
        self.extended = 0b00010000
        self.telegram_type = 0b00001111
        self.ext_header = 0b00000000
        self.ext_telegram_type = 0b00000000
        self.originator_id = b''
        self.destination_id = b''
        self.data_dl = []
        self.data_crc8 = b''

    def getOriginatorID(self):
        return self.originator_id

    def getDestinationID(self):
        return self.destination_id

    def getTelegramType(self):
        type = ''
        if self.telegram_type == self.ERP2_HEADER_TELEGRAM_TYPE_RPS:
            type = 'RPS'
        elif self.telegram_type == self.ERP2_HEADER_TELEGRAM_TYPE_1BS:
            type = '1BS'
        elif self.telegram_type == self.ERP2_HEADER_TELEGRAM_TYPE_4BS:
            type = '4BS'
        return type

    def getDataDL(self):
        return self.data_dl

    def getDbm(self):
        return self.optional_dbm

    def parseTelegramData(self, packet_data):
        self.packet_data = packet_data
        packet_offset = 0

        calc_crc8 = CalcCRC8(self.logger)

        # check header size > 6
        self.packet_length = len(self.packet_data)
        if self.packet_length < self.ESP3_HEADER_SIZE:
            self.logger.error(
                "ESP3: Invalid packet length:{0}".format(self.packet_length))
            return False
        self.logger.debug("ESP3: packet length:{0}".format(self.packet_length))

        # check sync byte
        self.sync_byte = self.packet_data[packet_offset]
        if self.sync_byte != self.ESP3_HEADER_SYNC_BYTE:
            self.logger.error(
                "ESP3: Invalid packet header sync byte:{0}".format(self.sync_byte))
            return False
        self.logger.debug("ESP3: header sync:{0}".format(self.sync_byte))

        # parse packet data length
        packet_offset += 1
        self.data_length = struct.unpack('>H', binascii.unhexlify(
            self.packet_data[packet_offset] + self.packet_data[packet_offset + 1]))[0]
        self.logger.debug("ESP3: data length:{0}".format(self.data_length))

        # parse packet optional length
        packet_offset += 2
        self.optional_length = struct.unpack(
            '>B', binascii.unhexlify(self.packet_data[packet_offset]))[0]
        self.logger.debug(
            "ESP3: optional length:{0}".format(self.optional_length))

        # parse Packet types
        packet_offset += 1
        self.packet_types = struct.unpack(
            '>B', binascii.unhexlify(self.packet_data[packet_offset]))[0]

        # supported Packet Type: Radio ERP2 only
        if self.packet_types != self.ESP3_PACKET_TYPE_RADIO_ERP2:
            self.logger.error(
                "ESP3: Unsupported packet type:{0}".format(self.packet_types))
            return False
        self.logger.debug("ESP3: packet types:{0}".format(self.packet_types))

        # parse CRC8 Header
        packet_offset += 1
        self.header_crc8h = self.packet_data[packet_offset]
        self.logger.debug("ESP3: header crc8h:{0}".format(self.header_crc8h))

        # check CRC8 Header
        d_data = self.packet_data[1:self.ESP3_HEADER_SIZE - 1]
        self.logger.debug("ESP3: crc8 header data:{0}".format(d_data))
        if calc_crc8.calcCRC8(d_data, self.header_crc8h) is not True:
            self.logger.error("ESP3: Invalid packet header CRC8 check error")
            return False

        # check packet length
        if self.packet_length != (self.ESP3_HEADER_SIZE + self.data_length + self.optional_length + 1):
            self.logger.error("ESP3: invalid packet length")
            return False
        if self.packet_length > self.ESP3_MAX_PACKET_SIZE:
            self.logger.error("ESP3: exceeded max packet length")
            return False
        self.logger.debug("ESP3: check packet length:ok")

        # parse ERP2 data contents for Length > 6 Bytes
        if self.data_length > 6:
            packet_offset += 1
            # parse Address Control
            self.addctrl = struct.unpack('>B', binascii.unhexlify(
                self.packet_data[packet_offset]))[0] & self.ERP2_HEADER_ADDCTRL
            self.logger.debug(
                "ERP2: address control:{0}".format(bin(self.addctrl)))

            # parse Extended header available
            self.extended = struct.unpack('>B', binascii.unhexlify(
                self.packet_data[packet_offset]))[0] & self.ERP2_HEADER_EXTENDED_HEADER
            self.logger.debug(
                "ERP2: extended header available:{0}".format(bin(self.extended)))

            # parse Telegram type (R-ORG)
            self.telegram_type = struct.unpack('>B', binascii.unhexlify(
                self.packet_data[packet_offset]))[0] & self.ERP2_HEADER_TELEGRAM_TYPE
            self.logger.debug("ERP2: telegram type:{0}".format(
                bin(self.telegram_type)))

            # parse Extended Header
            if self.extended == self.ERP2_HEADER_EXTENDED_HEADER_AVAILABLE:
                packet_offset += 1
                self.ext_header = struct.unpack(
                    '>B', binascii.unhexlify(self.packet_data[packet_offset]))[0]
                self.logger.debug(
                    "ERP2: extended header:{0}".format(bin(self.ext_header)))

            # parse Extended Telegram type
            if self.telegram_type == self.ERP2_HEADER_TELEGRAM_TYPE:
                packet_offset += 1
                self.ext_telegram_type = struct.unpack(
                    '>B', binascii.unhexlify(self.packet_data[packet_offset]))[0]
                self.logger.debug("ERP2: ext telegram type:{0}".format(
                    bin(self.ext_telegram_type)))

            # parse Originator ID, Destination ID
            if self.addctrl == self.ERP2_HEADER_ADDCTRL_ID24_NODIST:
                packet_offset += 1
                self.originator_id = self.packet_data[packet_offset] + \
                    self.packet_data[packet_offset + 1] + \
                    self.packet_data[packet_offset + 2]
                self.logger.debug(
                    "ERP2: originator id:{0}".format(self.originator_id))
                packet_offset += 2

            elif self.addctrl == self.ERP2_HEADER_ADDCTRL_ID32_NODIST:
                packet_offset += 1
                self.originator_id = self.packet_data[packet_offset] + \
                    self.packet_data[packet_offset + 1] + self.packet_data[packet_offset + 2] + \
                    self.packet_data[packet_offset + 3]
                self.logger.debug(
                    "ERP2: originator id:{0}".format(self.originator_id))
                packet_offset += 3

            elif self.addctrl == self.ERP2_HEADER_ADDCTRL_ID32_DIST32:
                packet_offset += 1
                self.originator_id = self.packet_data[packet_offset] + \
                    self.packet_data[packet_offset + 1] + self.packet_data[packet_offset + 2] + \
                    self.packet_data[packet_offset + 3]
                self.logger.debug(
                    "ERP2: originator id:{0}".format(self.originator_id))
                packet_offset += 3

                packet_offset += 1
                self.destination_id = self.packet_data[packet_offset] + \
                    self.packet_data[packet_offset + 1] + self.packet_data[packet_offset + 2] + \
                    self.packet_data[packet_offset + 3]
                self.logger.debug(
                    "ERP2: destination id:{0}".format(self.destination_id))
                packet_offset += 3

            elif self.addctrl == self.ERP2_HEADER_ADDCTRL_ID48_NODIST:
                packet_offset += 1
                self.originator_id = self.packet_data[packet_offset] + \
                    self.packet_data[packet_offset + 1] + self.packet_data[packet_offset + 2] + \
                    self.packet_data[packet_offset + 3] + self.packet_data[packet_offset + 4] + \
                    self.packet_data[packet_offset + 5]
                self.logger.debug(
                    "ERP2: originator id:{0}".format(self.originator_id))
                packet_offset += 5

            # parse Data DL
            if self.telegram_type == self.ERP2_HEADER_TELEGRAM_TYPE_RPS:
                packet_offset += 1
                self.data_dl.append(self.packet_data[packet_offset])
                self.logger.debug("ERP2: RPS DATA DL:{0}".format(self.data_dl))

            elif self.telegram_type == self.ERP2_HEADER_TELEGRAM_TYPE_1BS:
                packet_offset += 1
                self.data_dl.append(self.packet_data[packet_offset])
                self.logger.debug(
                    "ERP2: 1BS DATA DL :{0}".format(self.data_dl))

            elif self.telegram_type == self.ERP2_HEADER_TELEGRAM_TYPE_4BS:
                packet_offset += 1
                self.data_dl.append(self.packet_data[packet_offset])
                self.data_dl.append(self.packet_data[packet_offset + 1])
                self.data_dl.append(self.packet_data[packet_offset + 2])
                self.data_dl.append(self.packet_data[packet_offset + 3])
                self.logger.debug("ERP2: 4BS DATA DL:{0}".format(self.data_dl))
                packet_offset += 3

            # parse optional data (unsupported)

            # parse CRC8 DATA
            packet_offset += 1
            self.data_crc8 = self.packet_data[packet_offset]
            self.logger.debug("ERP2: data crc8:{0}".format(self.data_crc8))

            # check CRC8 DATA
            d_data = self.packet_data[
                self.ESP3_HEADER_SIZE:self.ESP3_HEADER_SIZE + self.data_length - 1]
            self.logger.debug("ERP2: crc8 data:{0}".format(d_data))
            if calc_crc8.calcCRC8(d_data, self.data_crc8) is not True:
                self.logger.error("ERP2: Invalid packet data CRC8 check error")
                return False

            # parse optional Data: Number of sub telegram
            packet_offset += 1
            self.optional_subtelnum = struct.unpack(
                '>B', binascii.unhexlify(self.packet_data[packet_offset]))[0]
            self.logger.debug("ESP3: optional SubTelNum:{0}".format(
                self.optional_subtelnum))

            # parse optional Data: dBm
            packet_offset += 1
            self.optional_dbm = struct.unpack(
                '>B', binascii.unhexlify(self.packet_data[packet_offset]))[0] * -1
            self.logger.debug(
                "ESP3: optional dBm:{0}".format(self.optional_dbm))

            # parse CRC8 DATA and OPTIONAL_DATA
            packet_offset += 1
            self.header_crc8d = self.packet_data[packet_offset]
            self.logger.debug(
                "ESP3: header crc8d:{0}".format(self.header_crc8d))

            # check CRC8 DATA and OPTIONAL_DATA
            d_data = self.packet_data[
                self.ESP3_HEADER_SIZE:self.ESP3_HEADER_SIZE + self.data_length + self.optional_length]
            self.logger.debug(
                "ESP3: crc8 data + optional data:{0}".format(d_data))
            if calc_crc8.calcCRC8(d_data, self.header_crc8d) is not True:
                self.logger.error(
                    "ESP3: Invalid packet data and optonal data CRC8 check error")
                return False

        else:
            self.logger.error("ERP2: Unsupported ERP2 Data contents")
            return False

        return True


class CalcCRC8():

    CRC8_TABLE = (
        0x00, 0x07, 0x0e, 0x09, 0x1c, 0x1b, 0x12, 0x15,
        0x38, 0x3f, 0x36, 0x31, 0x24, 0x23, 0x2a, 0x2d,
        0x70, 0x77, 0x7e, 0x79, 0x6c, 0x6b, 0x62, 0x65,
        0x48, 0x4f, 0x46, 0x41, 0x54, 0x53, 0x5a, 0x5d,
        0xe0, 0xe7, 0xee, 0xe9, 0xfc, 0xfb, 0xf2, 0xf5,
        0xd8, 0xdf, 0xd6, 0xd1, 0xc4, 0xc3, 0xca, 0xcd,
        0x90, 0x97, 0x9e, 0x99, 0x8c, 0x8b, 0x82, 0x85,
        0xa8, 0xaf, 0xa6, 0xa1, 0xb4, 0xb3, 0xba, 0xbd,
        0xc7, 0xc0, 0xc9, 0xce, 0xdb, 0xdc, 0xd5, 0xd2,
        0xff, 0xf8, 0xf1, 0xf6, 0xe3, 0xe4, 0xed, 0xea,
        0xb7, 0xb0, 0xb9, 0xbe, 0xab, 0xac, 0xa5, 0xa2,
        0x8f, 0x88, 0x81, 0x86, 0x93, 0x94, 0x9d, 0x9a,
        0x27, 0x20, 0x29, 0x2e, 0x3b, 0x3c, 0x35, 0x32,
        0x1f, 0x18, 0x11, 0x16, 0x03, 0x04, 0x0d, 0x0a,
        0x57, 0x50, 0x59, 0x5e, 0x4b, 0x4c, 0x45, 0x42,
        0x6f, 0x68, 0x61, 0x66, 0x73, 0x74, 0x7d, 0x7a,
        0x89, 0x8e, 0x87, 0x80, 0x95, 0x92, 0x9b, 0x9c,
        0xb1, 0xb6, 0xbf, 0xb8, 0xad, 0xaa, 0xa3, 0xa4,
        0xf9, 0xfe, 0xf7, 0xf0, 0xe5, 0xe2, 0xeb, 0xec,
        0xc1, 0xc6, 0xcf, 0xc8, 0xdd, 0xda, 0xd3, 0xd4,
        0x69, 0x6e, 0x67, 0x60, 0x75, 0x72, 0x7b, 0x7c,
        0x51, 0x56, 0x5f, 0x58, 0x4d, 0x4a, 0x43, 0x44,
        0x19, 0x1e, 0x17, 0x10, 0x05, 0x02, 0x0b, 0x0c,
        0x21, 0x26, 0x2f, 0x28, 0x3d, 0x3a, 0x33, 0x34,
        0x4e, 0x49, 0x40, 0x47, 0x52, 0x55, 0x5c, 0x5b,
        0x76, 0x71, 0x78, 0x7f, 0x6A, 0x6d, 0x64, 0x63,
        0x3e, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2c, 0x2b,
        0x06, 0x01, 0x08, 0x0f, 0x1a, 0x1d, 0x14, 0x13,
        0xae, 0xa9, 0xa0, 0xa7, 0xb2, 0xb5, 0xbc, 0xbb,
        0x96, 0x91, 0x98, 0x9f, 0x8a, 0x8D, 0x84, 0x83,
        0xde, 0xd9, 0xd0, 0xd7, 0xc2, 0xc5, 0xcc, 0xcb,
        0xe6, 0xe1, 0xe8, 0xef, 0xfa, 0xfd, 0xf4, 0xf3
    )

    def __init__(self, logger):
        self.logger = logger

    def procCRC8(self, crc, data):
        return self.CRC8_TABLE[crc ^ data]

    def calcCRC8(self, data_byte, data_crc8):

        calc_crc8 = 0x00
        for d in data_byte:
            calc_crc8 = self.procCRC8(calc_crc8, struct.unpack(
                '>B', binascii.unhexlify(d))[0])

        if calc_crc8 == struct.unpack('>B', binascii.unhexlify(data_crc8))[0]:
            ret = True
        else:
            ret = False

        self.logger.debug("calcCRC8:{0} :data_crc8={1} calc_crc8={2}".format(
            ret, data_crc8, calc_crc8))

        return ret
