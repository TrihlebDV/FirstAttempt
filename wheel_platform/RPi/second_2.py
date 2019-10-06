#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys  # sys нужен для передачи argv в QApplication
import os  # Отсюда нам понадобятся методы для отображения содержимого директорий

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QByteArray, QEvent
import numpy as np
from time import sleep
import threading
import second_design  # Это наш конвертированный файл дизайна

import receiver
import cv2

import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer

IP_ROBOT = '10.42.0.69'
RTP_PORT = 5000
CONTROL_PORT = 9000

class ExampleApp(QtWidgets.QMainWindow, second_design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.img = QtGui.QPixmap("image.jpg")
        self.img1 = QtGui.QPixmap("test.jpg")
        self.w, self.h  = QtGui.QPixmap.width(self.img), QtGui.QPixmap.height(self.img)
        self.img_btn.clicked.connect(self.setText)
        self.d_w = 0
        self.mainStr = "Hello World!"
        self.pixmap = None
        self.e1 = threading.Event()
        self.stopped = False
        self.t1 = threading.Thread(target=self.delText, args=(5, self.e1))
        self.daemon = True
        self.t1.start()
        self.btncheck = True
        self.recv = receiver.StreamReceiver(receiver.VIDEO_MJPEG, self.onFrameCallback)
        self.resiverInit()
        self.robot = xmlrpc.client.ServerProxy('http://%s:%d' % (IP_ROBOT, CONTROL_PORT))
        self.check = True
        self.psw = None
        self.psw_check = False
        

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

    def setText(self):
        self.btncheck = not self.btncheck
        self.mainStr = self.mainStr + "\nButton have pressed!"
        self.text_label.setText(self.mainStr)
        self.e1.set()
        if self.btncheck:
            self.img_laebl.setPixmap(self.img)
        else:
            self.img_laebl.setPixmap(self.img1)
        

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
            if self.psw_check: psw()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        if self.check:
            if e.type() == QEvent.KeyPress:
                if e.text() == 'w':
                    self.text_label.setText("w pressed")
                    print("PRESSED")
                    _ = self.robot.move('ahead')
                    self.check = not self.check
                    e.accept()
                elif e.text() == 'd':
                    self.text_label.setText("d pressed")
                    self.robot.move('right')
                    print("PRESSED")
                    self.check = not self.check
                    e.accept()
                elif e.text() == 'a':
                    self.text_label.setText("a pressed")
                    self.robot.move('left')
                    print("PRESSED")
                    self.check = not self.check
                    e.accept()
                elif e.text() == 's':
                    self.text_label.setText("s pressed")
                    self.robot.move('backward')
                    print("PRESSED")
                    self.check = not self.check
                    e.accept()
        if e.key() == Qt.Key_Escape:
            self.close()
                


    def keyReleaseEvent(self, e):
        if e.type() == QEvent.KeyRelease:
            if e.text() in ['w', 'd', 'a' , 's'] and not e.isAutoRepeat():
                self.robot.move('stop')
                self.text_label.setText("released")
                print("RELEASED")
                self.check = not self.check
                e.accept()

    def write_pswd(self, psw):
        self.psw = psw
    


def start(psw, wait):
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.text_label.setText(window.mainStr)
    window.img_laebl.setPixmap(window.img.copy(0, 0, window.w/2 , window.h/2))
    window.write_pswd(psw)
    wait.hide()
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
    
                

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.text_label.setText(window.mainStr)
    window.img_laebl.setPixmap(window.img.copy(0, 0, window.w/2 , window.h/2))
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
