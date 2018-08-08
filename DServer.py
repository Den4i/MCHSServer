# -*- coding: utf-8 -*-

import datetime
import time
from defines.gDefines import ThreadDBWriteOnLineName, ThreadDBWriteBuffer, PKG_TYPE_ASC, PKG_TYPE_SCOUT, conf
from core.gListener import Alistener
from modules.dbObjects import ThreadGetDBObjects
from modules.dbOnline import ThreadDataBasePj
from modules.dbData import ThreadDataBaseData


class TDataServer:
    modules = None
    Worked = False
    DateTimeStart = None

    def __init__(self):
        try:
            tpl_mess_init_module_err = "Ошибка инициализации модуля \"%s\" : %s"
            count_init_errors = 0
            self.DateTimeStart = datetime.datetime.now()
            print('Инициализация ...')
            self.modules = []

            try:
                m_name = 'GetDBObjects'
                m_caption = 'Модуль чтения списка зарегистрированных объектов'
                self.modules.append({'module': ThreadGetDBObjects(), 'name': m_name, 'caption': m_caption})
            except Exception as m_ex:
                print(tpl_mess_init_module_err % (m_name, m_ex))
                count_init_errors += 1

            try:
                m_name = ThreadDBWriteOnLineName
                m_caption = 'Модуль обработки данных "реального времени"'
                self.modules.append({'module': ThreadDataBasePj(), 'name': m_name, 'caption': m_caption})
            except Exception as m_ex:
                print(tpl_mess_init_module_err % (m_name, m_ex))
                count_init_errors += 1

            try:
                m_name = ThreadDBWriteBuffer
                m_caption = 'Модуль обработки буфера данных'
                self.modules.append({'module': ThreadDataBaseData(), 'name': m_name, 'caption': m_caption})
            except Exception as m_ex:
                print(tpl_mess_init_module_err % (m_name, m_ex))
                count_init_errors += 1

            try:
                m_name = 'ASC-Server'
                m_caption = 'Модуль обработки ASC'
                self.modules.append({'module': Alistener(conf['BASE']['HOST'], 9998, PKG_TYPE_ASC, 999), 'name': m_name,
                                     'caption': m_caption})
            except Exception as m_ex:
                print(tpl_mess_init_module_err % (m_name, m_ex))
                count_init_errors += 1

            try:
                m_name = 'Scout-Server'
                m_caption = 'Модуль обработки Scout'
                self.modules.append({'module': Alistener(conf['BASE']['HOST'], 9997, PKG_TYPE_SCOUT, 100),
                                     'name': m_name, 'caption': m_caption})
            except Exception as m_ex:
                print(tpl_mess_init_module_err % (m_name, m_ex))
                count_init_errors += 1

            print("Инициализация модулей %d выполнена, ошибок %d." % (len(self.modules), count_init_errors))

        except Exception as e:
            print("Ошибка инициализации модулей [%s]." % str(e))

    def start(self):
        startingErrors = 0
        print('Запуск модулей:')
        for m in self.modules:
            try:
                m['module'].setName(m['name'])
                print("Запуск модуля \"%s\" ..." % m['caption'])
                m['module'].start()
                print("Модуль \"%s\" запущен ." % m['caption'])
                time.sleep(0.05)
            except Exception as e:
                print("Ошибка запуска модуля [%s] %s." % (str(m['name']), str(e)))
                startingErrors += 1
        print("Запуск модулей выполнен, ошибок - %d." % startingErrors)
        self.Worked = True


DataServer = TDataServer()
DataServer.start()
