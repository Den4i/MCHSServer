# -*- coding: utf-8 -*-

from core.gDB import AThreadDataBase
from defines.gDefines import Logging, SLASH, TObject, DBObjectsList


class ThreadGetDBObjects(AThreadDataBase):
    def __init__(self):
        AThreadDataBase.__init__(self)
        self.pBase['path'] = 'c:%sscat%sworkbin%sdb%smchs.fdb' % (SLASH, SLASH, SLASH, SLASH)
        self.pBase['alias'] = 'mchs'
        self.GetCountObjects = 0
        self.LogFileName = "Database%sdbObjects.log" % (SLASH)

    def Work(self):
        log_dbobj = Logging(self.LogFileName, 'dbObjects')
        self.Worked = True
        OList = []
        try:
            if self.dataBaseConnect():
                log_dbobj.info(self.getName() + ':Получение списка зарегистрированных объектов...')
                self.ExecQuery(""" SELECT
                                                o.IDS_,
                                                o.OBJ_ID_,
                                                o.PROJ_ID_,
                                                o.PHONE_,
                                                o.NUMBLOCK
                                            FROM OBJECTS o;
                                       """
                                       , True
                                       , OList
                                       )

                for j in DBObjectsList:
                    j.isDB = False

                #синхронизируем буфер с данными из базы
                for i in OList:
                    OL_exist = False
                    for j in DBObjectsList:
                        if j.BlockNumber == i[4]:
                            OL_exist = True
                            j.isDB = True
                    if not OL_exist:
                        DBObjectsList.append(TObject(i[0], i[1], i[2], i[3], i[4]))

                log_dbobj.info(self.getName() + ': Список загруженных объектов:')
                for d in OList:
                    log_dbobj.info(self.getName() + str(d))

                self.GetCountObjects = int(len(DBObjectsList))
                log_dbobj.info('Объекты получены. Количество = %d.' % self.GetCountObjects)

            self.dataBaseDisconnect()
        except Exception as e:
            log_dbobj.error(self.getName() + ':Ошибка получения списка зарегистрированных объектов :%s' % (str(e)))
# ----------------------------------------------------------------------------------------------------------------------
