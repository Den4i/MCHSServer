# -*- coding: utf-8 -*-/

import threading
import datetime
import time
from defines.gDefines import SLASH, Logging


class netClient (threading.Thread):
    clientSock = None                                   # сокет
    addr = None                                         # данные адреса
    recvData = None                                     # полученные данные
    recvDecodeData = None                               # декодированные полученные данные
    ReciveBufferSize = None                             # размер входного буфера
    TimeStartClient = None                              # время запуска клиента(подключения)
    LastTimeReciveData = None                           # время последнего получения данных
    LogPath = ""

    def __init__(self, clientSock, addr):
        self.clientSock = clientSock
        self.addr = addr
        self.recvData = ''
        self.recvDecodeData = []
        self.TimeStartClient = datetime.datetime.now()
        self.LastTimeReciveData = datetime.datetime.now()
        self.sizeReciveData = 0
        threading.Thread.__init__(self)

    def run(self):
        self.LogFileName = self.LogPath + SLASH + str(self.addr[0]).replace('.', '_')+'.log'
        global log_nClient
        log_nClient = Logging(self.LogFileName, 'nclient')

        if self.ReciveBufferSize:
            self.Worked = True

            log_nClient.info('Входящее подключение: '.ljust(30, '.') + str(self.addr).rjust(30, '.')+'\r\n')

        while self.Worked:
            try:
                self.recvData = self.clientSock.recv(self.ReciveBufferSize)

                log_nClient.info("Получены данные:\r\n[" + str(self.recvData) + "] - %d байт(а)." % len(self.recvData))

                if self.recvData:
                    self.LastTimeReciveData = datetime.datetime.now()
                    self.sizeReciveData += len(self.recvData)

                    try:
                        self.processing()
                    except Exception as pr_ex:
                        raise Exception("ошибка внутреннего обработчика <%s>" % str(pr_ex))
                else:
                    self.Worked = False

            except Exception as err:
                self.Worked = False
                if err.args[0] == 10053:
                    log_nClient.error("Клиент инициировал отключение.")
                elif err.args[0] == 10054:
                    raise Exception("нет возможности работать с подключением: [ %s ] сокет: %s"
                                        % (str(err), str(self.clientSock)))
                else:
                    raise Exception("другая ошибка: [%s] сокет: %s" % (str(err), str(self.clientSock)))

        self.kill()
        log_nClient.info("Подключение закрыто.")

    # проверка полученного значения времени
    def checkValidDateTime(self, _sdatetime, _parse_mask):
        try:
            valid = False
            if _sdatetime:
                try:
                    curr_dt = datetime.datetime.now()
                    pkg_dt = time.strptime(_sdatetime, _parse_mask)
                except:
                    raise Exception('Ошибка приведения к формату[%s] :%s' % (str(_parse_mask), str(_sdatetime)))

                pkg_dt = datetime.datetime(pkg_dt.tm_year, pkg_dt.tm_mon, pkg_dt.tm_mday, pkg_dt.tm_hour,
                                           pkg_dt.tm_min, pkg_dt.tm_sec)

                valid = (pkg_dt < (curr_dt + datetime.timedelta(seconds=600)))
                if not valid:
                    raise Exception('Некорректное значение времени-из будущего: текущее :%s; получено :%s'
                                    % (str(curr_dt), str(pkg_dt)))
        except Exception as e:
            valid = False
            log_nClient.error("Ошибка проверки даты-времени(%s):%s" % (_sdatetime, str(e)))
        return valid

    def processing(self):                               # переопределяется в наследниках
        pass

    # декодирование полученного пакета
    def decodeInputPackage(self, data):
        result = None
        try:
            result = []
            for i in data:
                result.append(i)
        except Exception as e:
            log_nClient.error("Ошибка декодирования входных данных %s" % str(e))
        return result

    # закрыть сокета после работы с ним
    def kill(self):
        try:
            self.Worked = False
            self.clientSock.close()
        except Exception as kill_ex:
            log_nClient.error('Ошибка закрытия подключения:' + str(kill_ex))
# ----------------------------------------------------------------------------------------------------------------------
