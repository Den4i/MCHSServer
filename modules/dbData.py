# -*- coding: utf-8 -*-

import time
from core.gDB import AThreadDataBase
from defines.gDefines import SLASH, BufferObjects, Logging


class ThreadDataBaseData(AThreadDataBase):
    def __init__(self):
        AThreadDataBase.__init__(self)
        self.pBase['path'] = 'c:%sscat%sworkbin%sdb%sdata1.fdb' % (SLASH, SLASH, SLASH, SLASH)
        self.commitRecordCount = 25
        self.CountRecord = 0
        self.LogFileName = "Database%sdbData.log" % (SLASH)

    def Work(self):
        global log_dbdata
        log_dbdata = Logging(self.LogFileName, 'dbData')

        self.Worked = True
        while self.Worked:
            if self.dataBaseConnect():
                while len(BufferObjects) > 0:
                    try:
                        if self.dataBaseConnect():
                            self.appendBaseData(BufferObjects[0])
                            if len(BufferObjects) > 0:
                                BufferObjects.pop(0)
                            self.CountRecord += 1
                            if self.CountRecord % self.commitRecordCount == 0:
                                self.dataBaseDisconnect()
                    except Exception as e:
                        log_dbdata.error(self.getName() + ": Ошибка записи буфера в базу: %s; размер буфера = %d"
                                      % (str(e), len(BufferObjects)))
                    finally:
                        log_dbdata.info(self.getName() + ': Объем буфера: %d' % len(BufferObjects))
            self.dataBaseDisconnect()
            time.sleep(1)

    # запись полученной траектории в базу данных
    def appendBaseData(self, obj=None):
        if obj:
            try:
                if obj.Speed is None:
                    log_dbdata.error("Нет Сведений о скорости(%s)" % str(obj.Speed))
                if obj.LastTime is None:
                    log_dbdata.error("Нет Сведений о последнем времени(%s)" % str(obj.LastTime))
                if (obj.LastPoint.LON is None) or (obj.LastPoint.LON < -180) or (obj.LastPoint.LON > 180) or \
                        (obj.LastPoint.LON == 0):
                    log_dbdata.error("Некорректное значение последней координаты широты (%s)" % str(obj.LastPoint.LON))
                if (obj.LastPoint.LAT is None) or (obj.LastPoint.LAT < -90) or (obj.LastPoint.LAT > 90) or \
                        (obj.LastPoint.LAT == 0):
                    log_dbdata.error("Некорректное значение последней координаты долготы (%s)" % str(obj.LastPoint.LAT))

                if self.ExecQuery("EXECUTE PROCEDURE APPEND_BASE_DATA(%d, %d, '%s', %f, %f, %f); "
                                                 %(
                                                     obj.Pid
                                                    ,obj.Oid
                                                    ,str(obj.LastTime)
                                                    ,obj.LastPoint.LON
                                                    ,obj.LastPoint.LAT
                                                    ,obj.Speed
                                                  )):
                    log_dbdata.info("Записана  в архив(%s) траектория объекта %d/%d(%s) : [%s]"
                                    % (self.getName(), int(obj.Oid), int(obj.Pid), str(obj.BlockNumber),
                                       str(obj.LastTime)))

            except Exception as e:
                log_dbdata.error(self.getName() + ': Ошибка записи траектории  %s:%s' % (str(obj.Oid), str(e)))
# ----------------------------------------------------------------------------------------------------------------------
