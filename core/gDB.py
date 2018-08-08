# -*- coding: utf-8 -*-

import threading
import firebirdsql
from defines.gDefines import conf


# Класс работы с базой данных
class AThreadDataBase(threading.Thread):
    def __init__(self):
        self.pBase = {'host': conf['BASE']['HOST'], 'path': conf['BASE']['HOST'], 'port': conf['BASE']['PORT'],
                      'login': conf['BASE']['LOGIN'], 'password': conf['BASE']['PASSWORD'], 'charset': 'UTF8'}
        self.commitRecordCount = 1
        self.dbConnect = None
        self.Worked = False
        threading.Thread.__init__(self)

    def run(self):
        if self.dataBaseConnect():
            self.Work()
            self.dataBaseDisconnect()

    # Функция подключения к базе данных
    def dataBaseConnect(self):
        if self.dbConnect is None:
            try:
                self.dbConnect = firebirdsql.connect(host=self.pBase['host'], database=self.pBase['path'],
                                                     user=self.pBase['login'], password=self.pBase['password'])
                return True
            except:
                return False
        else:
            return True

    # Функция отключения от базы данных
    def dataBaseDisconnect(self):
        if self.dbConnect:
            try:
                self.dbConnect.close()
                self.dbConnect = None
                return True
            except:
                return False
        else:
            return True

    # функция выполнения запроса
    def ExecQuery(self, _sql, _fetchall=False, resultdata=None):
        try:
            if not self.dataBaseConnect():
                raise Exception("Нет подключения к базе данных.")

            cursor = self.dbConnect.cursor()
            cursor.execute(_sql)

            if _fetchall:                                       # если необходимо вернуть полученные данные
                result = cursor.fetchall()
                for rows in result:
                    if resultdata != None:
                        resultdata.append(rows)

            self.dbConnect.commit()
            result = True
        except:
            result = False
        return result

    # переопределяется в наследниках
    def Work(self):
        pass
# ----------------------------------------------------------------------------------------------------------------------
