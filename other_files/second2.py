#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys  # sys нужен для передачи argv в QApplication
import os  # Отсюда нам понадобятся методы для отображения содержимого директорий

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QByteArray, QEvent, QThread
import numpy as np
from time import sleep
import threading
import mouseEvent  # Это наш конвертированный файл дизайна
from PostHandl import Spawer

import receiver
import cv2

import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer

IP_ROBOT = '10.42.0.154'
RTP_PORT = 5000
CONTROL_PORT = 9000

class ExampleApp(QtWidgets.QWidget, mouseEvent.Ui_Form):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.stopEvent = threading.Event()
        self.check = True
        self.thread = QThread()
        self.thread.start()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.robot = xmlrpc.client.ServerProxy('http://%s:%d' % (IP_ROBOT, CONTROL_PORT))
        self.spawer = Spawer(self.on_recive, self.stopEvent)
        self.spawer.start()

    def on_recive(self, img):
        pixmap = QtGui.QPixmap(img)
        self.label.setPixmap(pixmap)

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Message', "Are you sure to quit?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            _ = self.robot.stopStreaming()
            self.stopEvent.wait()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        if self.check:
            if e.type() == QEvent.KeyPress:
                if e.text() == 'w':
                    _ = self.robot.comRecv('cam/down')
                    #self.check = False
                    e.accept()
                elif e.text() == 'd':
                    _ = self.robot.comRecv('cam/RIGHT')
                    #self.check = False
                    e.accept()
                elif e.text() == 'a':
                    _ = self.robot.comRecv('cam/LEFT')
                    #self.check = False
                    e.accept()
                elif e.text() == 's':
                    _ = self.robot.comRecv('cam/up')
                    #self.check = False
                    e.accept()
                elif e.key() == Qt.Key_Up:
                    _ = self.robot.comRecv('drive/ahead/200')
                    self.check = False
                    e.accept()
                elif e.key() == Qt.Key_Down:
                    _ = self.robot.comRecv('drive/backward/200')
                    self.check = False
                    e.accept()
                elif e.key() == Qt.Key_Left:
                    _ = self.robot.comRecv('drive/left/200')
                    self.check = False
                    e.accept()
                elif e.key() == Qt.Key_Right:
                    _ = self.robot.comRecv('drive/right/200')
                    self.check = False
                    e.accept()
        if e.key() == Qt.Key_Escape:
            self.close()
                


    def keyReleaseEvent(self, e):
        if e.type() == QEvent.KeyRelease:
            if e.key() in [Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right] and not e.isAutoRepeat():
                _ = self.robot.comRecv('drive/ahead/0')
                self.check = True
                e.accept()
        
    
                

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    #window.text_label.setText(window.mainStr)
    #window.img_laebl.setPixmap(window.img.copy(0, 0, window.w/2 , window.h/2))
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
