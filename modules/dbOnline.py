# -*- coding: utf-8 -*-

import datetime
from core.gDB import AThreadDataBase
from defines.gDefines import SLASH, DBObjectsList


class ThreadDataBasePj(AThreadDataBase):
    def __init__(self):
        AThreadDataBase.__init__(self)
        self.pBase['path'] = 'c:%sscat%sworkbin%sdb%smchs.fdb' % (SLASH, SLASH, SLASH, SLASH)
        self.pBase['alias'] = 'mchs'
        self.CountRecord = 0
        self.onlineCount = 0

    def Work(self):
        self.Worked = True
        while self.Worked:
            if self.dataBaseConnect():
                for i in DBObjectsList:
                    try:
                        # запись траектории
                        is_update = not (i.LastReciveTime is None)
                        if is_update:
                            if i.LastReciveTime >= (datetime.datetime.now() - datetime.timedelta(seconds=600)):
                                self.onlineCount += 1

                            self.ExecQuery("""  UPDATE OBJECTS O
                                                SET
                                                    O.LAST_TIME_ = '%s'
                                                    ,O.LAST_LON_ = %f
                                                    ,O.LAST_LAT_ = %f
                                                    ,O.LAST_SPEED_ = %f
                                                WHERE O.IDS_ = %d; """
                                            % (
                                                i.LastTime
                                                ,i.LastPoint.LON
                                                ,i.LastPoint.LAT
                                                ,i.Speed
                                                ,i.Ids
                                              )
                                        )
                            self.CountRecord += 1
                    except Exception as e:
                        raise Exception("Не возможно записать траекторию" + str(e))

            self.dataBaseDisconnect()
# ----------------------------------------------------------------------------------------------------------------------
