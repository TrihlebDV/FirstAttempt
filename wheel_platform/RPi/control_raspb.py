#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import gi
from gi.repository import GObject
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import cv2

#библиотеки СКТБ
import rpicam
#библиотека для работы с ардуино uart
import serial

#настройки видеопотока
#FORMAT = rpicam.FORMAT_H264
FORMAT = 1 #rpicam.FORMAT_MJPEG
WIDTH, HEIGHT = 640, 360
RESOLUTION = (WIDTH, HEIGHT)
FRAMERATE = 30

#сетевые параметры
#IP = '192.168.42.100'
#IP = '192.168.42.50' #пульт
IP = '10.42.0.1' #пульт
RTP_PORT = 5000
CONTROL_PORT = 9000 #порт XML-RPC управления роботом

readyEvent = threading.Event()
readyEvent.set()


def communicate(direct, retn):
    if direct == 'ahead':
        ser.write(b'A')
        print("AAA")
    elif direct == 'backward':
        ser.write(b'B')
        
    elif direct == 'right':
        ser.write(b'C')
        
    elif direct == 'left':
        ser.write(b'D')
        
    elif direct == 'stop':
        ser.write(b'E')
    response = ser.readline()
    print(response)
    print("______")
    #if(response == b'1\r\n'): readyEvent.set()
    readyEvent.set()

def move(direct):
    print(direct)
    if readyEvent.is_set():
        print("AA") 
        readyEvent.clear()
        t1 = threading.Thread(target=communicate, args=(direct, 0))
        t1.start()
    return 0


print('Start program')

assert rpicam.checkCamera(), 'Raspberry Pi camera not found'
print('Raspberry Pi camera found')

# Получаем свой IP адрес
#ip = rpicam.getIP()
ip = '10.42.0.69'
assert ip != '', 'Invalid IP address'
print('Robot IP address: %s' % ip)

print('OpenCV version: %s' % cv2.__version__)

print('initiating Serial communication with Arduino')
try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    print('--conneced sucsesfuly')
except:
    print('--cant connected to arduino(')

rpiCamStreamer = rpicam.RPiCamStreamer(FORMAT, RESOLUTION, FRAMERATE)
#задаем порт и хост куда шлем видео
rpiCamStreamer.setPort(RTP_PORT)
rpiCamStreamer.setHost(IP)
#robotCamStreamer.setFlip(False, True) #отражаем кадр (вертикальное отражение, горизонтальное отражение)
rpiCamStreamer.setRotation(180) #поворачиваем кадр на 180 град, доступные значения 90, 180, 270
rpiCamStreamer.start() #запускаем тра

#нужно для корректной работы системы
GObject.threads_init()
mainloop = GObject.MainLoop()

# XML-RPC сервер управления в отдельном потоке
serverControl = SimpleXMLRPCServer((ip, CONTROL_PORT)) #запуск XMLRPC сервера
serverControl.logRequests = False #оключаем логирование
print('Control XML-RPC server listening on %s:%d' % (ip, CONTROL_PORT))

# register our functions
serverControl.register_function(move)

#запускаем сервер в отдельном потоке
serverControlThread = threading.Thread(target = serverControl.serve_forever)
serverControlThread.daemon = True
serverControlThread.start()

#главный цикл программы    
try:
    mainloop.run()
except (KeyboardInterrupt, SystemExit):
    print('Ctrl+C pressed')


rpiCamStreamer.stop()    
rpiCamStreamer.close()
           
#останов сервера
serverControl.server_close()

print('End program')


