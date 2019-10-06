#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import gi
from gi.repository import GObject
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer

#библиотеки СКТБ
import rpicam

#библиотеки для отправки видео и работы с драйвером
import driver
import station_send
#библиотека бля работы с ардуино
import serial

#настройки видеопотока
FORMAT = rpicam.FORMAT_H264
#FORMAT = rpicam.FORMAT_MJPEG
WIDTH, HEIGHT = 640, 360
RESOLUTION = (WIDTH, HEIGHT)
FRAMERATE = 30

#сетевые параметры
IP = '192.168.42.100'
#IP = '192.168.42.50' #пульт
#IP = '10.42.0.1' #пульт
HOST = "tcp://192.168.42.100:5000" #порт отправки RTP видео
CONTROL_PORT = 9000 #порт XML-RPC управления роботом

class CpuInfo(threading.Thread):
    def __init__(self, interval):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interval = interval
        self.stopped = threading.Event()

    def run(self):
        while not self.stopped.wait(self.interval):
            print ('CPU temp: %.2f°C. CPU use: %.2f%% ' % (rpicam.getCPUtemperature(), psutil.cpu_percent()))
            
    def stop(self):
        self.stopped.set()

def move(mnStr):
    driver.write(mnStr)
    return(0)

print('Start program')

assert rpicam.checkCamera(), 'Raspberry Pi camera not found'
print('Raspberry Pi camera found')

# Получаем свой IP адрес
ip = rpicam.getIP()
assert ip != '', 'Invalid IP address'
print('Robot IP address: %s' % ip)

print('OpenCV version: %s' % cv2.__version__)

driver = driver.Driver((13, 19, 20, 21))

#нужно для корректной работы системы
GObject.threads_init()
mainloop = GObject.MainLoop()

camSender = station_send.CamSender(HOST)
camSender.run()

# XML-RPC сервер управления в отдельном потоке
serverControl = SimpleXMLRPCServer((ip, CONTROL_PORT)) #запуск XMLRPC сервера
serverControl.logRequests = False #оключаем логирование
print('Control XML-RPC server listening on %s:%d' % (ip, CONTROL_PORT))

# register our functions
serverControl.register_function(write)

#запускаем сервер в отдельном потоке
serverControlThread = threading.Thread(target = serverControl.serve_forever)
serverControlThread.daemon = True
serverControlThread.start()

#pапускаем поток выдачи информации о процессоре 1 раз в сек
cpuInfo = CpuInfo(1)
cpuInfo.start()

#главный цикл программы    
try:
    mainloop.run()
except (KeyboardInterrupt, SystemExit):
    print('Ctrl+C pressed')

#останов потока выдачи информации о состоянии процессора
cpuInfo.stop()

camSender.stop()
           
#останов сервера
serverControl.server_close()

print('End program')


