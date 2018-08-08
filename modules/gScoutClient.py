# -*- coding: utf-8 -*-/

from core.nClient import netClient
from defines.gDefines import SCOUT_RECIVE_BUFFER_SIZE, DBObjectsList, BufferObjects, tz, utc, fmt
from datetime import datetime


def getGeo(coord):
    coord = str(coord)
    grad = coord[0:2]
    minut = format(int(coord[2:4]), "02d")
    second = float('0.'+coord[4:])*60
    drob = ((float(minut) + (second/60))*60)/3600
    res = float(grad)+drob
    return res


class talktoScoutClient(netClient):
    def __init__(self, clientsock, addr):
        self.clientSock = clientsock
        self.addr = addr
        self.recvData = b''
        self.recvDecodeData = []
        self.lastBlockData = []
        self.countPackages = 0
        self.Worked = False
        self.ReciveBufferSize = SCOUT_RECIVE_BUFFER_SIZE
        netClient.__init__(self, clientsock, addr)
        self.typeofPackages = None
        self.BlockNumber = None

    def processing(self):
        try:
            self.recvDecodeData = self.decodeInputPackage(self.recvData)
            if self.recvDecodeData[0] == 64 and len(self.recvDecodeData) > 27:
                self.recvDecodeData = self.recvDecodeData[27:]
                self.typeofPackages = '40'                                      # первое сообщение после коннекта
            elif self.recvDecodeData[0] == 255:
                self.recvDecodeData = self.recvDecodeData
                self.typeofPackages = 'FF'                                      # передача нескольки сообщений
            elif self.recvDecodeData[0] == 8:
                self.recvDecodeData = self.recvDecodeData
                self.typeofPackages = '08'                                      # одиночный пакет
            if self.typeofPackages is not None:
                self.lastBlockData = self.parsingPackage(self.recvDecodeData)
                self.countPackages += 1
        except:
            self.Worked = False

    # разбор полученного пакета
    def parsingPackage(self, datas):
        try:
            result = {}
            data = ''
            for i in datas:
                x = str('%X' % i).rjust(2, '0')
                data += x

            pkg_size = 44
            if self.typeofPackages in ('40', 'FF'):
                self.BlockNumber = int(data[2:6], 16)
                info = data[10:]
                answer = (data[4:6]+data[2:4]).encode()
                self.clientSock.send(b'\xF2'+answer+b'\x00\x00')                    # отклик сервера на одиночный пакет
            else:
                info = data
                answer_prepare = hex(self.BlockNumber)
                st = answer_prepare[2:4]
                ml = answer_prepare[4:6]
                answer = (ml+st).encode()
                self.clientSock.send(b'\xF0'+answer+b'\x00\x00')                    # отклик сервера на FF-пакет

            list_pkg = []
            while (len(info) / pkg_size) > 0:
                pkg = info[:pkg_size]
                if len(pkg) == pkg_size:
                    info = info[pkg_size:]
                    if pkg[0:2] == '08' and pkg[2:4] != '00' and pkg[16:18] != '00':
                        list_pkg.append(pkg)

            for i in list_pkg:
                day = int(i[2:4], 16)
                month = int(i[4:6], 16)
                year = int('20'+str(int(i[6:8], 16)))
                hour = int(i[8:10], 16)
                minut = int(i[10:12], 16)
                second = int(i[12:14], 16)

                lon_pre = int(i[20:22]+i[18:20]+i[16:18]+i[14:16], 16)
                lat_pre = int(i[28:30]+i[26:28]+i[24:26]+i[22:24], 16)

                speed = float(int(i[42:44]+i[40:42], 16)*0.1852)

                utc_dt = datetime(year, month, day, hour, minut, second, tzinfo=utc)
                loc_dt = utc_dt.astimezone(tz).strftime(fmt)

                if lon_pre != 0 and lat_pre != 0 and loc_dt > '01.01.2000 00:00:01':
                    LON = getGeo(lon_pre)
                    LAT = getGeo(lat_pre)

                    result['BLOCK_NUMBER'] = self.BlockNumber
                    result['TIME'] = loc_dt
                    result['SPEED'] = speed
                    result['LON'] = LON
                    result['LAT'] = LAT

                    block_exist = False
                    for o in DBObjectsList:
                        if o.BlockNumber == int(result['BLOCK_NUMBER']):
                            block_exist = True
                            o.Update(result['TIME'], result['LON'], result['LAT'], result['SPEED'])
                            BufferObjects.append(o)
                    if not block_exist:
                        raise Exception("Блок %d не зарегистрирован!" % int(result['BLOCK_NUMBER']))
        except Exception as e:
            raise("Ошибка разбора пакета:" + str(e))
        return result
# ----------------------------------------------------------------------------------------------------------------------
