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
import yaml
import io

#библиотеки СКТБ
import rpicam
import RPiPWM

#работа с моторами
MotorLeftChannel = 14    #каналы к которым подключены моторы
MotorRightChannel = 15
cameraServoCannel = 3
AUTOMAT_CAMERA_ANGLE = 44
MANUAL_CAMERA_ANGLE = 10

#настройки видеопотока
#FORMAT = rpicam.FORMAT_H264
FORMAT = rpicam.FORMAT_MJPEG
WIDTH, HEIGHT = 640, 360
RESOLUTION = (WIDTH, HEIGHT)
FRAMERATE = 30

#сетевые параметры
#IP = '192.168.42.50' #пульт
IP = '10.42.0.1' #пульт
RTP_PORT = 5000 #порт отправки RTP видео
DEBUG_PORT = 8000 #порт отправки отладочных кадров XML-RPC
CONTROL_PORT = 9000 #порт XML-RPC управления роботом

#Чувтвительность алгоритма определения линии
SENSITIVITY = 65

#
BASE_SPEED = 50

dirkof = 40 #кэфицент при изменении курса.

cameraPos = False #False - смотрим прямо, True - смотрим вниз

D = np.zeros((4))
K = np.zeros((3, 3))
#K=np.array([312.12837404700826, 0.0, 305.7373776912714], [0.0, 312.1160716398593, 175.39947207737023], [0.0, 0.0, 1.0]])
#D=np.array([-0.05923006233886738, 0.13273783139898743, -0.3144426393271996, 0.23237501822988305])
#основные точки
top_left = [0,0] #520, 
top_right = [520, 0]
bottom_right = [520, 320]
bottom_left = [0,320]
#pts = np.array([bottom_left,bottom_right,top_right,top_left])

#-----------
bottom_left_dst = [50, 276]
bottom_right_dst = [618, 283]
top_right_dst = [458, 161]
top_left_dst = [181, 160]
#dst_pts = np.array([bottom_left_dst, bottom_right_dst, top_right_dst, top_left_dst])

#pts = np.float32(pts.tolist())
#dst_pts = np.float32(dst_pts.tolist())
#h, mask = cv2.findHomography(dst_pts, pts) 

class LineFollow(threading.Thread):
    #камера источник кадров, ширина фрейма в кадре, выстота фрейма в кадре, привязка по нижней границе
    def __init__(self, camera, width, height, debugClient):
        threading.Thread.__init__(self)
        self.oldDirection = True #True - видел линию справа, False - видел линию слева
        self.lineLost = False
        self.h = None
        self.map1 = None
        self.map2 = None
        self.checkAutoMode = [0,0]
        self.daemon = True
        self.speedCount = 0
        self._stopped = threading.Event() #событие для остановки потока
        self.camera = camera
        self._frame = None
        self.automat = False
        self.debug = False
        self.sensitivity = 127 #чувствительность алгоритма определения линии (0..255)
        self.width = width
        if width > WIDTH:
            self.width = WIDTH
        self.height = height
        if height > HEIGHT:
            self.height = HEIGHT
        self._top = HEIGHT - height #верхняя точка среза
        self._left = (WIDTH - width)//2 #левая точка среза
        self._right = self._left + width #правая точка среза
        self._bottom = HEIGHT #нижняя точка среза
        self._newFrameEvent = threading.Event() #событие для контроля поступления кадров
        #отладочный сервер
        self.debugClient = debugClient

    def detectLine(self, frame):
        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  #преобразуем в чернобелое
        #blur = cv2.GaussianBlur(gray, (5, 5), 0)   # размываем изображение blur
        #ret, thresh = cv2.threshold(blur, self.sensitivity, 255, cv2.THRESH_BINARY_INV)
        
        img = cv2.remap(frame, self.map1, self.map2, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)
        warped = cv2.warpPerspective(img, self.h, (520, 320), cv2.INTER_LINEAR)
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        frame = gray
        #gray = cv2.GaussianBlur(gray, (3, 3), 0)
        _ , thresh = cv2.threshold(gray, self.sensitivity, 255, cv2.THRESH_BINARY_INV)
        #бинаризация в ч/б (исходное изобр, порог, максимальное знач., тип бинаризации)
        #_, contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE) #нахождение контуров
        _, contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        direction = 0.0 #курс нашей посудины
        cx = frame.shape[0] #на случай если не удастся вычислить cx
        cy = frame.shape[1]
        lineFound = False
        if contours:   # если есть хоть один контур
            lineFound = True
            mainContour = max(contours, key = cv2.contourArea)    # берем максимальный
            M = cv2.moments(mainContour)  # берем его
            if M['m00'] != 0:   # если нет деления на ноль
                cx = int(M['m10']/M['m00'])     # смотрим координаты центра наибольшего черного пятна
                cy = int(M['m01']/M['m00'])     # они получаются в пикселях кадра

                if self.debug:
                    cv2.line(frame, (cx, 0), (cx, frame.shape[0]), (255, 0, 0), 1)    # рисуем перекрестье на контуре
                    cv2.line(frame, (0, cy), (frame.shape[1], cy), (255, 0, 0), 1)
            if self.debug:
                cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1) #отрисовываем центральную точку
                cv2.drawContours(frame, mainContour, -1, (0, 255, 0), 2, cv2.FILLED) #отображаем контуры на изображении
            direction = cx / (frame.shape[0]/2) - 1  # преобразуем координаты от 0 до ширина кадра -> от -1 до 1
        return lineFound, direction, frame
        
    def run(self):
        global sideCheck
        print('Line follow started, sensitivity: %d' % self.sensitivity)
        while not self._stopped.is_set():
            self.camera.frameRequest() #отправил запрос на новый кадр
            self._newFrameEvent.wait() #ждем появления нового кадра
            if not (self._frame is None): #если кадр есть
                if self.debug:
                    
                    # берем нижнюю часть кадра
                    #crop = self._frame[self._top:self._bottom, self._left:self._right]    #обрезаем кадр
                    crop = self._frame
                    #вызываем функцию определения линии
                    lineFound, direction, resImg = self.detectLine(crop)
                    
                    if self.automat:
                        if lineFound: # если линия была обнаружена, задем скорости
                            MOMENT_BASE_SPEED = BASE_SPEED-int(30.0*math.fabs(direction))
                            leftSpeed = round(-MOMENT_BASE_SPEED + direction*dirkof)
                            rightSpeed = round(MOMENT_BASE_SPEED + direction*dirkof)
                            if self.lineLost:
                                self.lineLost = False
                            self.oldDirection = direction > 0 #запомнили где видели линию
                        else:
                            if not self.lineLost:
                                print("LINE LOST")
                                self.lineLost = True
                                if self.oldDirection:
                                    print("Right")
                                    leftSpeed = round(BASE_SPEED/2)
                                    rightSpeed = round(BASE_SPEED/2)
                                
                                else:
                                    print("Left")
                                    leftSpeed = round(-BASE_SPEED/2)
                                    rightSpeed = round(-BASE_SPEED/2)
                            
                        setSpeed(leftSpeed, rightSpeed)
                            
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

def setSpeed(leftSpeed, rightSpeed):
    if lineFollow.automat:
        a = lineFollow.speedCount
        a += 1
        if(a == 7):
            if(lineFollow.checkAutoMode[0] ==  leftSpeed and lineFollow.checkAutoMode[1] == rightSpeed):
                rightMotor.SetValue(0)
                leftMotor.SetValue(0)
                time.sleep(0.5)
                print("AAA")
            lineFollow.checkAutoMode[0] = leftSpeed
            lineFollow.checkAutoMode[1] = rightSpeed
            a = 0
        lineFollow.speedCount = a
        rightMotor.SetValue(rightSpeed)
        leftMotor.SetValue(leftSpeed)
    else:
        rightMotor.SetValue(rightSpeed)
        leftMotor.SetValue(leftSpeed)
    print('left: %d, right: %d' %(leftSpeed, rightSpeed))
    return 0

def initPar():
    global D
    global K
    with open("/home/pi/D.yaml", 'r') as stream:
        a = yaml.load(stream)
    D[0] = a['D0']
    D[1] = a['D1']
    D[2] = a['D2']
    D[3] = a['D3']
    K[0, 0] = a['K00']
    K[0, 1] = a['K01']
    K[0, 2] = a['K02']
    K[1, 0] = a['K10']
    K[1, 1] = a['K11']
    K[1, 2] = a['K12']
    K[2, 0] = a['K20']
    K[2, 1] = a['K21']
    K[2, 2] = a['K22']
    pts = np.array([bottom_left,bottom_right,top_right,top_left])
    dst_pts = np.array([bottom_left_dst, bottom_right_dst, top_right_dst, top_left_dst])
    pts = np.float32(pts.tolist())
    dst_pts = np.float32(dst_pts.tolist())
    h, mask = cv2.findHomography(dst_pts, pts)
    lineFollow.map1, lineFollow.map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, RESOLUTION, cv2.CV_16SC2)
    lineFollow.h = h
    print("parametrs are inited")

def changeCameraPos():
    global cameraPos
    if cameraPos:
        cameraServo.SetValue(MANUAL_CAMERA_ANGLE)
    else:
        cameraServo.SetValue(AUTOMAT_CAMERA_ANGLE)
    cameraPos = not cameraPos
    print("Canged")
    return 0

def changeSens(value):
    global SENSITIVITY
    if(value):
        SENSITIVITY += 1
    else:
        SENSITIVITY -= 1
    lineFollow.sensitivity = SENSITIVITY
    return SENSITIVITY

def setAutoMode():
    lineFollow.automat = not lineFollow.automat
    print ('Auto mode: %s' % str(lineFollow.automat))
    if not lineFollow.automat:
        #останов робота
        rightMotor.SetValue(0)
        leftMotor.SetValue(0)
        cameraServo.SetValue(MANUAL_CAMERA_ANGLE)
        print("sent up")

    else:
        cameraServo.SetValue(AUTOMAT_CAMERA_ANGLE)
        print("sent down")
        
    return lineFollow.automat

def Debug():
    lineFollow.debug =  not lineFollow.debug
    if(lineFollow.debug == False):
        return 1
    else:
        return 0

print('Start program')



assert rpicam.checkCamera(), 'Raspberry Pi camera not found'
print('Raspberry Pi camera found')

# Получаем свой IP адрес
ip = rpicam.getIP()
assert ip != '', 'Invalid IP address'
print('Robot IP address: %s' % ip)

print('OpenCV version: %s' % cv2.__version__)

#создание объектов для работы с шилдом
rightMotor = RPiPWM.ReverseMotor(MotorLeftChannel)   # мотор с реверсом
leftMotor = RPiPWM.ReverseMotor(MotorRightChannel)   # мотор с реверсом
print("Initing channels:  %d - Reverse Motor, %d - Reverse Motor"
      % (MotorLeftChannel, MotorRightChannel))
rightMotor.SetValue(0)
leftMotor.SetValue(0)

cameraServo = RPiPWM.Servo90(cameraServoCannel, extended=False)
cameraServo.SetValue(10)

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

#контроль линии    
lineFollow = LineFollow(robotCamStreamer, int(WIDTH/7*4), int(HEIGHT/2), debugClient)
lineFollow.debug = False
lineFollow.sensitivity = SENSITIVITY
lineFollow.start()
#инициализируем параметри из ямла и прогружаем warp
initPar()
        
# XML-RPC сервер управления в отдельном потоке
serverControl = SimpleXMLRPCServer((ip, CONTROL_PORT)) #запуск XMLRPC сервера
serverControl.logRequests = False #оключаем логирование
print('Control XML-RPC server listening on %s:%d' % (ip, CONTROL_PORT))

# register our functions
serverControl.register_function(setSpeed)
serverControl.register_function(setAutoMode)
serverControl.register_function(changeSens)
serverControl.register_function(Debug)
serverControl.register_function(changeCameraPos)


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

#останов робота
rightMotor.SetValue(0)
leftMotor.SetValue(0)

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
   
print('End program')

