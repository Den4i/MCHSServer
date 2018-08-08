# -*- coding: utf-8 -*-

import threading
import socket
import datetime
from defines.gDefines import SLASH, Logging, PKG_TYPE_ASC, PKG_TYPE_SCOUT


class Alistener(threading.Thread):
    def __init__(self, _host, _port, _sType,_maxClient):
        self.host = _host
        self.port = _port
        self.maxClients = _maxClient
        self.type = _sType
        self.sServer = None
        self.Worked = False
        self.Connections = []
        self.LogFileName = "Network%sListening.log" % (SLASH)
        threading.Thread.__init__(self)

    def __del__(self):
        if not self.sServer is None:
            self._Stop()
        log_listening.info('Сервер %s остановлен' % str(self.getName()))

    def run(self):
        global log_listening
        log_listening = Logging(self.LogFileName, 'listening')
        try:
            log_listening.info("Запуск сервера %s ..." % str(self.getName()))
            self.sServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            self.sServer = None

        if not self.sServer is None:
            try:
                self.sServer.bind((str(self.host), int(self.port)))
                self.sServer.listen(int(self.maxClients))
            except socket.error as e:
                self.sServer = None
                log_listening.error("Ошибка открытия порта %d для прослушивания %s: %s"
                                    % (self.port, str(self.host), str(e)))

            if not self.sServer is None:
                self.Worked = True
                log_listening.info("Сервер %s запущен." % str(self.getName()))
                while self.Worked:
                    log_listening.info("Ожидание водящих подключений %s:%d" % (str(self.host), int(self.port)))

                    channel, details = self.sServer.accept()
                    log_listening.info("Новое входящее подключение %s:%s ..." % (str(details[0]), str(details[1])))

                    try:
                        if self.type == PKG_TYPE_ASC:
                            from modules.ASC import TASC6
                            self.Connections.append(TASC6(channel, details))

                        elif self.type == PKG_TYPE_SCOUT:
                            from modules.gScoutClient import talktoScoutClient
                            self.Connections.append(talktoScoutClient(channel, details))

                        self.Connections[len(self.Connections)-1].setName('TCP_%s_%s'
                                                                          % (str(details[0]).replace('.','_'),
                                                                             str(details[1])))
                        if self.LogFileName.find(SLASH) > 0:
                            s = self.LogFileName
                            s = s.split(SLASH)
                            s.pop()

                            for i in s:
                                self.Connections[len(self.Connections)-1].LogPath = \
                                    self.Connections[len(self.Connections)-1].LogPath + SLASH + str(i)

                        self.Connections[len(self.Connections)-1].start()

                    except Exception as ec:
                        log_listening.error("Ошибка открытия входящего подключения на интерфейсе %s:%s : %s"
                                            % (str(self.host), str(self.port), str(ec)))

                    self.SweepConnections()
            self._Stop()

    def _Stop(self):
        try:
            self.Worked = False
            log_listening.info(self.getName()+" Остановка сервера ... ")
            if not self.sServer is None:
                self.sServer.close()
                log_listening.info(self.getName()+"Слушающий сокет закрыт.")
                self.CloseConnections()
                self.sServer = None
            else:
                raise Exception("Сервер не работает или уже остановлен.")
        except Exception as ex:
            log_listening.error("Некорректная остановка модуля: %s " % str(ex))

    def CloseConnections(self):
        try:
            log_listening.info(self.getName()+": Закрытие %d подключений ..." % len(self.Connections))
            while len(self.Connections) > 0:
                try:
                    self.Connections[len(self.Connections)-1].Worked = False
                    self.Connections[len(self.Connections)-1].kill()
                    self.Connections.pop()
                except Exception as ex1:
                    log_listening.error("Ошибка закрытия подключения: %s " % str(ex1))
            del self.Connections
        except Exception as ex:
            log_listening.error("Ошибка закрытия подключений: %s " % str(ex))

    def SweepConnections(self):
        try:
            log_listening.info("Запуск чистки подключений...")
            # ищем неактивные и залипшие (по которым давно нет передачи данных) подключения
            try:
                log_listening.info("Определение мертвых подключений(всего подключений:%d)..." % (len(self.Connections)))
                idxs = []
                i = 0
                x1 = 0
                x2 = 0
                x3 = 0
                for c in self.Connections:
                    if i < len(self.Connections) - 1:
                        if not c.Worked:
                            idxs.append(i)
                            x1 += 1
                        elif c.LastTimeReciveData < (datetime.datetime.now() - datetime.timedelta(seconds=600)):
                            idxs.append(i)
                            x2 += 1
                        elif not c.isAlive():
                            idxs.append(i)
                            x3 += 1
                    i += 1

                log_listening.info("Определение мертвых подключений выполнено(выключенных-%d/залипших-%d/неактивных-%d)"
                                   % (x1, x2, x3))
            except Exception as e1:
                raise Exception("Ошибка определения мертвых подключений: %s" % str(e1))

            # удаляем неактивные и залипшие(по которым давно нет передачи данных) подключения
            if (not idxs is None) and (len(idxs)) > 0:
                try:
                    log_listening.info("Уничтожение мертвых %d подключений(всего подключений:%d)..."
                                       % (len(idxs), len(self.Connections)))
                    idxs.reverse()

                    for i in idxs:
                        if self.Connections[i].Worked:
                            self.Connections[i].Worked = False
                        log_listening.info("Уничтожение мертвого подключения %s" % str(self.Connections[i].getName()))
                        self.Connections[i].kill()
                        del self.Connections[i]
                        self.Connections.pop(i)

                    log_listening.info("Уничтожение мертвых подключений выполнено(всего подключений:%d)."
                                       % len(self.Connections))

                except Exception as e1:
                    raise Exception("Ошибка удаления мертвых подключений[%s]: %s" % (str(idxs), str(e1)))
            else:
                log_listening.info("Все подключения живы.")

            log_listening.info("Чистка подключений выполнена.")
        except Exception as e:
            log_listening.error("Ошибка чистки подключений: %s" % str(e))
# ----------------------------------------------------------------------------------------------------------------------
