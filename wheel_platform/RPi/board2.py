#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import threading
import gi
from gi.repository import GObject ,GLib#, Gtk 
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import os

from multiprocessing import Process, Queue
import cv2


import numpy as np
import base64
import zmq

import serial

#FORMAT = rpicam.FORMAT_MJPEG
WIDTH, HEIGHT = 640, 360
RESOLUTION = (WIDTH, HEIGHT)
FRAMERATE = 10

IP = '10.42.0.1' #пульт
RTP_PORT = 5000 #порт отправки RTP видео
DEBUG_PORT = 8000 #порт отправки отладочных кадров XML-RPC
CONTROL_PORT = 9000 #порт XML-RPC управления роботом

class ArdHandler():
    def __init__(self, func=None):
        self._setter = func
        #self.ser = serial.Serial('/dev/ttyACM0', 9600)
        self.ser = serial.Serial('/dev/ttyACM0', 9600)
        self.queue = Queue()
        self.mainLoop = GLib.MainLoop()
        self.config()

    def config(self):
        buff = ser.readline()

    def writeCommand(self, data1, data2, data3):
        count_1 = int(data3 / 100)
        count_2 = int(data3 % 100 / 10)
        count_3 = data3 % 10
        self.ser.write(bytes(str(data1), encoding = 'UTF-8'))
        self.ser.write(bytes(str(data2), encoding = 'UTF-8'))
        self.ser.write(bytes(str(count_1), encoding = 'UTF-8'))
        self.ser.write(bytes(str(count_2), encoding = 'UTF-8'))
        self.ser.write(bytes(str(count_3), encoding = 'UTF-8'))

def VideoStreaming(queue):
    cap = cv2.VideoCapture(0)
    _stopped = False
    context = zmq.Context()
    footage_socket = context.socket(zmq.PUB)
    footage_socket.connect('tcp://10.42.0.1:60000')
    recv_sock = context.socket(zmq.SUB)
    recv_sock.bind('tcp://10.42.0.154:6000')
    recv_sock.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
    
    while not _stopped:
        if not queue.empty():
            _stopped = True
            footage_socket.send(b'0123456789')
            _ = recv_sock.recv_string()
        else:    
            ret, frame = cap.read()
            if ret:
                encoded, buffer = cv2.imencode('.jpg', frame)
                jpg_as_text = base64.b64encode(buffer)
                footage_socket.send(jpg_as_text)

                _ = recv_sock.recv_string()
    print("VideoStreaming stopped")

# проверка доступности камеры, возвращает True, если камера доступна в системе
def checkCamera():
    res = os.popen('vcgencmd get_camera').readline().replace('\n','') #читаем результат, удаляем \n
    dct = {}
    for param in res.split(' '): #разбираем параметры
        tmp = param.split('=')
        dct.update({tmp[0]: tmp[1]}) #помещаем в словарь
    return (dct['supported'] and dct['detected'])

def getIP():
    #cmd = 'hostname -I | cut -d\' \' -f1'
    #ip = subprocess.check_output(cmd, shell = True) #получаем IP
    res = os.popen('hostname -I | cut -d\' \' -f1').readline().replace('\n','') #получаем IP, удаляем \n
    return res
 
ardHandler = None

def comRecv(command): # драйверы иногда проседают, поэтому пришлось написаткостыль
    data1 = 1
    data2 = 0
    data3 = 0
    for com in command.split("/"):
        if com  ==  "drive": data1 = 1
        elif com == "cam":   data1 = 0
        elif com == "ahead":    data2 = 1
        elif com == "backward": data2 = 2
        elif com == "left":     data2 = 3
        elif com == "right":    data2 = 4
        elif com == "LEFT":     data2 = 2
        elif com == "RIGHT":    data2 = 1
        elif com == "up":   data3 = 1
        elif com == "down": data3 = 2
        elif com.isdigit(): data3 = int(com)
    print(data3)
    ardHandler.writeCommand(data1, data2, data3)
    return 0

def stopStreaming():
    ardHandler.queue.put(1)
    ardHandler.mainLoop.quit()
    return 0

print('Start program')

assert checkCamera(), 'Raspberry Pi camera not found'
print('Raspberry Pi camera found')

# Получаем свой IP адрес
ip = getIP()
assert ip != '', 'Invalid IP address'
print('Robot IP address: %s' % ip)

print('OpenCV version: %s' % cv2.__version__)

print('initiating Serial communication with Arduino')
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    print('--conneced sucsesfuly')
except:
    print('--cant connected to arduino(')


#нужно для корректной работы системы

ardHandler = ArdHandler()
pr = Process(target=VideoStreaming, args=(ardHandler.queue,))
pr.start()

# XML-RPC сервер управления в отдельном потоке
serverControl = SimpleXMLRPCServer((ip, CONTROL_PORT)) #запуск XMLRPC сервера
serverControl.logRequests = False #оключаем логирование
print('Control XML-RPC server listening on %s:%d' % (ip, CONTROL_PORT))

# register our functions
serverControl.register_function(comRecv)
serverControl.register_function(stopStreaming)

#запускаем сервер в отдельном потоке
serverControlThread = threading.Thread(target = serverControl.serve_forever)
serverControlThread.daemon = True
serverControlThread.start()

#главный цикл программы    
#
try:
    ardHandler.mainLoop.run()
except (KeyboardInterrupt, SystemExit):
    print('Ctrl+C pressed')
           
#останов сервера
serverControl.server_close()

   
print('Program over...')


