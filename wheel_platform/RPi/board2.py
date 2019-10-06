#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import cv2
import numpy as np
import threading
import gi
from gi.repository import GObject
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import psutil
import os
import math
import io
import argparse
import datetime
import imutils
import serial


#библиотеки СКТБ
import rpicam
import RPiPWM

#настройки видеопотока
FORMAT = rpicam.FORMAT_H264
#FORMAT = rpicam.FORMAT_MJPEG
WIDTH, HEIGHT = 640, 360
RESOLUTION = (WIDTH, HEIGHT)
FRAMERATE = 30

#сетевые параметры
#IP = '192.168.42.100'
#IP = '192.168.42.50' #пульт
IP = '10.42.0.1' #пульт
RTP_PORT = 5000 #порт отправки RTP видео
DEBUG_PORT = 8000 #порт отправки отладочных кадров XML-RPC
CONTROL_PORT = 9000 #порт XML-RPC управления роботом

#Чувтвительность алгоритма определения линии
SENSITIVITY = 70
BASE_SPEED = 30

class LineFollow(threading.Thread):
    #камера источник кадров, ширина фрейма в кадре, выстота фрейма в кадре, привязка по нижней границе
    def __init__(self, camera, width, height, debugClient):
        threading.Thread.__init__(self)
        self.daemon = True
        self.speedCount = 0
        self._stopped = threading.Event() #событие для остановки потока
        self.camera = camera
        self._frame = None
        self.width = width      #width should be less then WIDTH
        self.height = height    #height should be less then HEIGHT
        self._newFrameEvent = threading.Event() #событие для контроля поступления кадров
        #отладочный сервер
        self.debugClient = debugClient
    
    def run(self):
        while not self._stopped.is_set():
            self.camera.frameRequest() #отправил запрос на новый кадр
            self._newFrameEvent.wait() #ждем появления нового кадра
            if not (self._frame is None): #если кадр есть
                self._frame = self._frame[0:self.height, 0:self.width]
                res, imgJpg = cv2.imencode('.jpg', resImg) #преобразовал картинку в массив
                if res:
                    try:
                        self.debugClient.drawCvFrame(imgJpg.tobytes()) #заслал картинку
                    except Exception as err:
                        print('Fault code:', err.faultCode)
                        print('Message   :', err.faultString)    
            self._newFrameEvent.clear() #сбрасываем событие
            
        print('Line follow stopped')

    def stop(self): #остановка потока
        self._stopped.set()
        if not self._newFrameEvent.is_set(): #если кадр не обрабатывается
            self._frame = None
            self._newFrameEvent.set() 
        self.join()

    def setFrame(self, frame): #задание нового кадра для обработки
        if not self._newFrameEvent.is_set(): #если обработчик готов принять новый кадр
            self._frame = frame
            self._newFrameEvent.set() #задали событие
        return self._newFrameEvent.is_set()


class CpuInfo(threading.Thread):
    def __init__(self, interval, adc):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interval = interval
        self.stopped = threading.Event()
        self.adc = adc

    def run(self):
        while not self.stopped.wait(self.interval):
            print ('CPU temp: %.2f°C. CPU use: %.2f%% .Battery: %.2fV' % (rpicam.getCPUtemperature(), psutil.cpu_percent(), self.adc.GetVoltageFiltered()))
            
    def stop(self):
        self.stopped.set()
        
def onFrameCallback(frame): #обработчик события 'получен кадр'
    lineFollow.setFrame(frame) #задали новый кадр

def setSpeed(direction): # драйверы иногда проседают, поэтому пришлось написать костыль
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
    return 0              

print('Start program')

assert rpicam.checkCamera(), 'Raspberry Pi camera not found'
print('Raspberry Pi camera found')

# Получаем свой IP адрес
ip = rpicam.getIP()
assert ip != '', 'Invalid IP address'
print('Robot IP address: %s' % ip)

print('OpenCV version: %s' % cv2.__version__)

print('initiating Serial communication with Arduino')
try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    print('--conneced sucsesfuly')
except:
    print('--cant connected to arduino(')

# создаем объект, который будет работать с АЦП
# указываем опорное напряжение, оно замеряется на первом пине Raspberry (обведено квадратом на шелкографии)
adc = RPiPWM.Battery(vRef=3.28)
adc.start()  # запускаем измерения

#нужно для корректной работы системы
GObject.threads_init()
mainloop = GObject.MainLoop()

#видеопоток с камеры робота    
robotCamStreamer = rpicam.RPiCamStreamer(FORMAT, RESOLUTION, FRAMERATE, (IP, RTP_PORT), onFrameCallback)
#robotCamStreamer = rpicam.RPiCamStreamer(FORMAT, RESOLUTION, FRAMERATE, (IP, RTP_PORT))
#robotCamStreamer.setFlip(False, True)
robotCamStreamer.setRotation(180)
robotCamStreamer.start()

#XML-RPC клиент для запуска отладочных процедур
debugClient = xmlrpc.client.ServerProxy('http://%s:%d' % (IP, DEBUG_PORT))

function = easy.Function((int(HEIGHT), int(WIDTH)))

#контроль линии    
lineFollow = LineFollow(robotCamStreamer, int(WIDTH), int(HEIGHT), debugClient)
lineFollow.debug = False
lineFollow.sensitivity = SENSITIVITY
lineFollow.start()

# XML-RPC сервер управления в отдельном потоке
serverControl = SimpleXMLRPCServer((ip, CONTROL_PORT)) #запуск XMLRPC сервера
serverControl.logRequests = False #оключаем логирование
print('Control XML-RPC server listening on %s:%d' % (ip, CONTROL_PORT))

# register our functions
serverControl.register_function(setSpeed)

#запускаем сервер в отдельном потоке
serverControlThread = threading.Thread(target = serverControl.serve_forever)
serverControlThread.daemon = True
serverControlThread.start()

#pапускаем поток выдачи информации о процессоре 1 раз в сек
cpuInfo = CpuInfo(1, adc)
cpuInfo.start()

#главный цикл программы    
try:
    mainloop.run()
except (KeyboardInterrupt, SystemExit):
    print('Ctrl+C pressed')


#останов потока выдачи информации о состоянии процессора
cpuInfo.stop()
           
#останов сервера
serverControl.server_close()

#останов контроля линии
lineFollow.stop()

#останов трансляции камеры
robotCamStreamer.stop()    
robotCamStreamer.close()

#поток по батарее
adc.stop()
   
print('Program over...')


