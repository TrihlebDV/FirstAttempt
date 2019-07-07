#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys  # sys нужен для передачи argv в QApplication
import os  # Отсюда нам понадобятся методы для отображения содержимого директорий

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QByteArray, QEvent
import numpy as np
from time import sleep
import threading
#import second_design_2603  # Это наш конвертированный файл дизайна
import second_design  # Это наш конвертированный файл дизайна

import receiver
import cv2
from time import sleep

import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer

IP_ROBOT = '10.42.0.69'
RTP_PORT = 5000
CONTROL_PORT = 9000

    
class ExampleApp(QtWidgets.QMainWindow, second_design.Ui_MainWindow):
    def __init__(self, onCallback = None):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.img_btn.clicked.connect(self.img_event)
        self.btn_power_up.clicked.connect(lambda:self.buttonCallback(self.btn_power_up))
        self.btn_power_down.clicked.connect(lambda:self.buttonCallback(self.btn_power_down))
        self.actionExit.triggered.connect(self.closeEvent)



        self.d_w = 0
        self.mainStr = "Hello World!"
        self.pixmap = None
        self.e1 = threading.Event()
        self.stopped = False
        self.t1 = threading.Thread(target=self.delText, args=(5, self.e1))
        self.daemon = True
        self.t1.start()
        self.btncheck = True
        #gcc
        self._onCallback = None
        if (not onCallback is None) and callable(onCallback):
            self._onCallback = onCallback
        self.recv = receiver.StreamReceiver(receiver.VIDEO_MJPEG, self.onFrameCallback)
        self.resiverInit()
        self.check = True
        

    def resiverInit(self):
        self.recv.setPort(RTP_PORT)
        self.recv.setHost(IP_ROBOT)
        self.recv.play_pipeline()

    def onFrameCallback(self, data, width, heigh):
        cvimg = np.ndarray((heigh, width, 3), buffer = data, dtype = np.uint8)
        cvimg = cv2.cvtColor(cvimg, cv2.COLOR_RGB2BGR)
        byteValue = 3*width
        self.mQImage = QtGui.QImage(cvimg, width, heigh, byteValue, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(self.mQImage.rgbSwapped())
        self.img_laebl.setPixmap(pixmap)

    def buttonCallback(self, btn):
        self.setText(btn.text())
        if 'UP' in btn.text():
            self._onCallback(True)
            #return 1 #power UP
        elif 'DOWN' in btn.text():
            self._onCallback(False)
            #return 0 # power DOWN


    def setText(self, stringToPrint):
        self.btncheck = not self.btncheck
        self.mainStr = self.mainStr + '\n' + stringToPrint
        self.text_label.setText(self.mainStr)
        self.e1.set()
        

    def delText(self, time_for_sleep, event_for_wait):
        while not self.stopped:
            event_for_wait.wait()
            sleep(time_for_sleep)
            self.mainStr = "deleted :)"
            self.text_label.setText(self.mainStr)
        print("Stopped(")


    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Message', "Are you sure to quit?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.stopped = True
            print("stop pipeline")
            self.recv.stop_pipeline()
            self.recv.null_pipeline()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

#def funcFromClient(self):
#    print('funcFromClient')
#    self.setText('its a func from client!')


def funcFromClient(psw, wait):
    sleep(3)
    wait.hide()
    print("it's [OK]")
    psw()

#def wrt(psw, wait):
#    sleep(3)
#    wait.hide()
#    print("it's [OK]")
#    psw()

def main(log):
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp(funcFromClient)  # Создаём объект класса ExampleApp
    window.text_label.setText(window.mainStr)
    window.img_laebl.setPixmap(window.img.copy(0, 0, window.w/2 , window.h/2))
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
