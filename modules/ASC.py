# -*- coding: utf-8 -*-/

from core.nClient import netClient
from defines.gDefines import ASC_RECIVE_BUFFER_SIZE, ASC_PKG_SIZE_TYPE_6, tz, utc, fmt, DBObjectsList, BufferObjects

from datetime import datetime


def getGeo(s):
    result = None
    mantissaString = s[9:32]
    exponent = int(s[1:9], 2)-127
    mantissa = 1
    for i in range(len(mantissaString)):
        for m in mantissaString[i]:
            mantissa += float(int(m)*pow(2, int(-i-1)))
            result = mantissa*pow(2, exponent)
    return result


class TASC6 (netClient):
    def __init__(self, clientSock, addr):
        self.clientSock = clientSock
        self.addr = addr
        self.recvData = ''
        self.recvDecodeData = []
        self.lastBlockData = {}
        self.countPackages = 0
        self.Worked = False
        self.LastRecivedDateTime = None
        self.ReciveBufferSize = ASC_RECIVE_BUFFER_SIZE
        netClient.__init__(self, clientSock, addr)

    def processing(self):
        try:
            pkg = None
            pkg_size = ASC_PKG_SIZE_TYPE_6
            self.recvDecodeData = self.decodeInputPackage(self.recvData)

            if self.recvDecodeData:
                """True, если полученные декодированные данные кратны размеру пакета"""
                self.Worked = (len(self.recvDecodeData) % pkg_size == 0)

                if not self.Worked:
                    print("Получены несоответствующие данному протоколу данные")

            if self.recvDecodeData and self.Worked:
                if pkg_size and self.Worked:
                    while int(len(self.recvDecodeData) / pkg_size) > 0 and self.Worked:
                        if len(self.recvDecodeData) < pkg_size:
                            print("Короткий пакет %s длина = %d..." % (str(pkg), len(pkg)))
                        if pkg_size and self.Worked:
                            pkg = self.recvDecodeData[:pkg_size]
                            print("Обработка пакета %s длина = %d..." % (str(pkg), len(pkg)))
                            if len(pkg) == pkg_size and self.Worked:
                                self.lastBlockData = self.parsingPackage(pkg)
                                self.appendBlockToBuffers()
                                self.countPackages += 1

                        self.recvDecodeData = self.recvDecodeData[pkg_size:]
                        if len(self.recvDecodeData) == 0 or self.recvDecodeData is None or not self.Worked:
                            break
            else:
                self.Worked = False
        except Exception as pr_ex:
            raise ("Ошибка обработки данных: <"+str(pr_ex)+'>')

    def parsingPackage(self, data):
        result = {}
        lat = ''
        lon = ''
        dataList = []

        for i in data:
            dataList.append(i)

        try:
            blockNumber = int(str('%X' % dataList[1])+str('%X' % dataList[0]), 16)
        except Exception as e1:
            raise Exception("Ошибка определения номера блока: " + str(e1))

        try:
            pkgSize = int(str('%X' % dataList[2]), 16)
        except Exception as e1:
            raise Exception("Ошибка определения размера пакета: " + str(e1))

        try:
            pkgType = int(str('%X' % dataList[3]), 16)
        except Exception as e1:
            raise Exception("Ошибка определения типа пакета: " + str(e1))
        print("Получен пакет от блока %d, размер = %d байт" % (blockNumber, pkgSize))

        if pkgType == 76:
            try:
                _time = int(str('%X' % dataList[29]) + str('%X' % dataList[28]) + str('%X' % dataList[27]) +
                            str('%X' % dataList[26]), 16)
                utc_dt = utc.localize(datetime.utcfromtimestamp(_time))
                loc_dt = (tz.normalize(utc_dt.astimezone(tz))).strftime(fmt)
            except Exception as e1:
                raise Exception('Ошибка получения даты/времени от блока %d:%s' % (blockNumber, str(e1)))

            speed = (int(str('%X' % dataList[20])+str('%X' % dataList[19]), 16))/10   # полученную скорость делим на 10

            if speed is None:
                raise Exception('Ошибка получения скорости от блока %d.' % blockNumber)

            for i in dataList[12], dataList[11], dataList[10], dataList[9]:
                x = bin(i).replace('0b', '').rjust(8, '0')
                lat += x

            for i in dataList[16], dataList[15], dataList[14], dataList[13]:
                x = bin(i).replace('0b', '').rjust(8, '0')
                lon += x

            if lat != 0 and lon != 0 and loc_dt > '01.01.1970 00:00:01':   # широта и долгота не должны быть равными 0
                result['BLOCK_NUMBER'] = blockNumber
                result['TIME'] = loc_dt
                result['SPEED'] = speed
                result['LON'] = getGeo(lon)
                result['LAT'] = getGeo(lat)

        return result

    # добавление распарсенного пакета в буфер
    def appendBlockToBuffers(self):
        try:
            rec = self.lastBlockData
            if 'BLOCK_NUMBER' in rec:
                block_exist = False
                for o in DBObjectsList:
                    if o.BlockNumber == int(rec['BLOCK_NUMBER']):
                        block_exist = True
                        o.Update(rec['TIME'], rec['LON'], rec['LAT'], rec['SPEED'])
                        BufferObjects.append(o)
                if not block_exist:
                    raise Exception("Блок %d не зарегистрирован!" % int(rec['BLOCK_NUMBER']))
        except Exception as emess:
            raise ("Ошибка занесения данных в буфер:" + str(emess))
# ----------------------------------------------------------------------------------------------------------------------
