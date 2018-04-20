#!/usr/bin/python3

import time
import RTCjoystick
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import cv2
import numpy as np
import sys
import queue
import threading
import subprocess
import receiver


#IP_ROBOT = '192.168.42.10'
IP_ROBOT = '10.42.0.135'
CONTROL_PORT = 9000
DEBUG_PORT = 8000
RTP_PORT = 5000
BASE_SPEED = 100

#переменная для переключения автоматического управления
automat = True

#названия кнопок и осей
#кнопки
speedUp = 'y'         #trigger
speedDown = 'a'       #thumb2
sensUp = 'b'          #thumb
sensDown = 'x'        #top
setAutomat = 'mode'   #base3 (9)
debug = 'start'       #base4 (10)
changeAxes = 'select' #отсутствует аналоговая ось
#оси
axesX = 'hat0x'       #всегда оси -- x & --y 
axesY = 'hat0y'       #
valAxes = True



class ShowDebugFrame(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self._running = False
        self._frameCount = 0 #счетчик кадров
        self.frameQueue = queue.Queue() #очередь приема кадров
        cv2.startWindowThread() #инициализация вывода cv2
        #cv2.namedWindow('debug')

    def run(self):
        self._running = True
        while self._running:
            try:
                # запрашиваем из очереди объект, ждем 1 сек
                img = self.frameQueue.get(True, 1)
                cv2.imshow('debug', img) #отображаем кадр
                if cv2.waitKey(1) == 32: #нажали 'пробел', сохранили кадр
                    imgFileName = "frame-" + str(self._frameCount) + ".jpg"
                    print('Save frame: %s' % imgFileName)
                    cv2.imwrite(imgFileName, img) #записали кадр
                self._frameCount += 1
                self.frameQueue.task_done() #сообщили очереди, что "задание выполнено"
            except queue.Empty:
                #print('Empty')
                cv2.destroyAllWindows() #
                pass
        cv2.destroyAllWindows()
        
    def stop(self):
        self._running = False
        self.join() #ждем завершения потока

    def setDebugFrame(self, frame):
        self.frameQueue.put_nowait(frame) #передаем кадр в очередь 

def SpeedDown():
    global BASE_SPEED
    BASE_SPEED = BASE_SPEED -10
    if(BASE_SPEED < -100):
        BASE_SPEED = -100
    print("SpeedDown  " + str(BASE_SPEED))


def SpeedUp():
    global BASE_SPEED
    BASE_SPEED = BASE_SPEED +10
    if(BASE_SPEED > 200):
        BASE_SPEED = 100
    print("SpeedUp  "+ str(BASE_SPEED))

def Automat():
    print(" automat: %d" % robot.setAutoMode())

def SensUp():
    print("Sensivity: %d " % robot.changeSens(True))
    
def SensDown():
    print("Sensivity: %d " % robot.changeSens(False))

def ChengeCamPos():
    robot.changeCameraPos()

def Debug():
    robot.Debug()
    print('---debug')

def ChengeCheck():
    print(robot.CangeCheck())

def ChangeAxes():
    global axesX
    global axsesY
    global valAxes
    valAxes = not valAxes
    if valAxes:
        axesX = 'hat0x'
        axesY = 'hat0y'
        print("---digital mode turn on")
    else:
        axesX = 'x'
        axesY = 'y'
        print("---analog mode turn on")
    print(axesX + ' ' + axesY)


#прием кадра с результатами обработки алгоритма поиска линии
def drawCvFrame(frame):
    imgArray = np.frombuffer(frame.data, dtype=np.uint8) #преобразуем в массив np
    img = cv2.imdecode(imgArray, cv2.IMREAD_COLOR) #декодируем
    #print(img)
    showDebugFrame.setDebugFrame(img) #передаем кадр в очередь
    return 0

#Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
cmd = 'hostname -I | cut -d\' \' -f1'
ip = subprocess.check_output(cmd, shell = True) #получаем IP
ip = ip.rstrip().decode("utf-8") #удаляем \n, переводим в текст

J = RTCjoystick.Joystick()
J.connect("/dev/input/js0")
J.info()
time.sleep(2)
J.start()

robot = xmlrpc.client.ServerProxy('http://%s:%d' % (IP_ROBOT, CONTROL_PORT))

# set up the server
debugServer = SimpleXMLRPCServer((ip, DEBUG_PORT)) #XMLRPC сервер
debugServer.logRequests = False
print('Listening on %s:%d' % (ip, DEBUG_PORT))

# регистрируем функции
debugServer.register_function(drawCvFrame)

#запускаем сервер в отдельном потоке
debugServerThread = threading.Thread(target=debugServer.serve_forever)
debugServerThread.daemon = True
debugServerThread.start()

#прописываем функции к кнопкам джойстика    
J.connectButton(speedDown, SpeedDown)
J.connectButton(speedUp, SpeedUp)
J.connectButton(setAutomat, Automat)
J.connectButton(sensDown, SensDown)
J.connectButton(sensUp, SensUp)
J.connectButton(debug, Debug)
J.connectButton(changeAxes, ChangeAxes)
J.connectButton('tl', ChengeCamPos)
J.connectButton('tr', ChengeCheck)


hatXOld = 0.0
hatYOld = 0.0

leftSpeed = 0
rightSpeed = 0

speedChange = False

showDebugFrame = ShowDebugFrame()
showDebugFrame.start()

#recv = receiver.StreamReceiver(receiver.FORMAT_H264, (IP_ROBOT, RTP_PORT))
recv = receiver.StreamReceiver(receiver.FORMAT_MJPEG, (IP_ROBOT, RTP_PORT))
recv.play_pipeline()

try:
    while True:
        hatX, hatY = J.Axis.get(axesX), J.Axis.get(axesY)
        if hatX != hatXOld:
            #состояние крестовины изменилось
            if hatX != 0:
                leftSpeed = round(int(hatX*float(BASE_SPEED/2)))
                rightSpeed = round(int(hatX*float(BASE_SPEED/2)))
            else:
                leftSpeed = 0
                rightSpeed = 0
            speedChange = True
            hatXOld = hatX

        if hatY != hatYOld:            
            if hatY != 0:
                leftSpeed = round(int(hatY*float(BASE_SPEED/2)))
                rightSpeed = round(-int(hatY*float(BASE_SPEED/2)))
            else:
                leftSpeed = 0
                rightSpeed = 0
            speedChange = True
            hatYOld = hatY

        if speedChange:
            robot.setSpeed(leftSpeed, rightSpeed)
            speedChange = False

        #print (hatX, hatY)
        time.sleep(0.1)

except(KeyboardInterrupt, SystemExit):
    print('Ctrl+C pressed')
    J.exit()
    debugServer.server_close()
    showDebugFrame.stop()
    recv.null_pipeline()
    recv.stop_pipeline()
    

