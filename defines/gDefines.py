# -*- coding: utf-8 -*-

import configparser
import os
import pytz
import sys

conf = configparser.RawConfigParser()
conf.read(os.path.join(os.path.dirname(__file__), r'config.cfg'))

tz = pytz.timezone('Europe/Moscow')                 # устанавливаем тайм-зону
utc = pytz.utc                                      # время utc в секундах
fmt = '%d.%m.%Y %H:%M:%S'                           # формат даты/времени

# типы принимаемых пакетов --------------------------------------------------------------------------------------- #
PKG_TYPE_ASC = 900                                  # формат ASC
PKG_TYPE_SCOUT = 2

# системные параметры -------------------------------------------------------------------------------------------- #
if sys.platform == 'win32':
    SLASH = "\\"                                    # разделитель каталогов дял win
else:
    SLASH = "/"                                     # разделитель каталогов для других ос

LOG_DIR = "logs"                                    # каталог для логов

ASC_RECIVE_BUFFER_SIZE = 1024                       # размер принимаемого буфера для протокола ASC - 6 - 1Mb = 1048576
ASC_PKG_SIZE_TYPE_6 = 66                            # размер пакета ASC - 66

SCOUT_RECIVE_BUFFER_SIZE = 1024


# названия потоков ----------------------------------------------------------------------------------------------- #
ThreadDBWriteOnLineName = 'DBWriteOnLine'           # имя потока для записи ON-LINE данных в базу PROJECTS
ThreadDBWriteBuffer = 'DBWriteBuffer'               # имя потока для записи буфера данных в базу DATA


# буфера данных -------------------------------------------------------------------------------------------------- #
global DBObjectsList                                # список зарегистрированных в базе объектов
DBObjectsList = []
global BufferObjects                                # буфер данных
BufferObjects = []

global TGeoCoors


class TGeoCoors:                                    # класс для описания координат
    LAT = None                                      # широта
    LON = None                                      # долгота

    def __init__(self, _lat=0.0, _lon=0.0):
        self.LAT = _lat
        self.LON = _lon


class TObject:                                  # класс для описания объекта
    Ids = None                                  # ids
    Oid = None                                  # код объекта
    Pid = None                                  # код проекта
    Phone = None                                # номер телефона
    BlockNumber = None                          # номер блока, если данных нет то -1
    Speed = None                                # последняя скорость движения
    LastPoint = None                            # последняя точка
    LastTime = None                             # последенее время из пакета
    LastReciveTime = None                       # время последнего обновления состояния объекта
    isDB = True                                 # наличие в базе( для удаления из буфера объектов удаленных из базы)

    def __init__(self, ids_, oid_, pid_, phone_, blocknumber_):
        self.Ids = ids_
        self.Oid = oid_
        self.Pid = pid_
        self.Phone = phone_
        self.BlockNumber = blocknumber_
        self.LastPoint = TGeoCoors()

    def Update(self, _LastTime=None, _LastLon=None, _LastLat=None, _LastSpeed=None):
        import time
        import datetime
        if _LastTime is None:
            raise Exception("Получена пустая дата-время")
        _lt = time.strptime(_LastTime, fmt)

        to_up = (self.LastTime is None)
        if not to_up:
            _slt = time.strptime(self.LastTime, fmt)
            to_up = (_lt > _slt)

        if to_up:
            self.LastTime = _LastTime
            self.LastPoint.LON = _LastLon
            self.LastPoint.LAT = _LastLat
            self.Speed = _LastSpeed
            self.LastReciveTime = datetime.datetime.now()
# ----------------------------------------------------------------------------------------------------------------------

# функция, осуществляющая создание и запись файла логгирования
def Logging(filename, logger):
    import datetime
    import os
    import logging
    log_nClient = logging.getLogger(logger)
    log_dir = str(datetime.datetime.now())
    log_dir = log_dir[8:10]+log_dir[5:7]+log_dir[:4]
    log_dir = os.getcwd() + SLASH + LOG_DIR + SLASH + log_dir
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    if filename.find(SLASH) > -1:
        s = filename
        s = s.split(SLASH)

        logFileName = s[len(s)-1]
        s.pop()
        for i in s:
            try:
                log_dir = log_dir + SLASH + str(i)
                if not os.path.exists(log_dir):
                    os.mkdir(log_dir)
            except:
                print('Ошибка создания каталога для логов: ')

        log_file_name = log_dir + SLASH + logFileName

        if os.path.exists(log_file_name):
            f = open(log_file_name, 'a+')
        else:
            f = open(log_file_name, 'w+')
        f.close()

        log_nClient.setLevel(logging.DEBUG)
        handler = logging.FileHandler(log_file_name, 'a')
        formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        log_nClient.addHandler(handler)

    return log_nClient
