#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys  # sys нужен для передачи argv в QApplication
import os  # Отсюда нам понадобятся методы для отображения содержимого директорий

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QObject
import numpy as np
from time import sleep
import threading
import second_design  # Это наш конвертированный файл дизайна
    

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
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()



def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.text_label.setText(window.mainStr)
    window.img_laebl.setPixmap(window.img.copy(0, 0, window.w/2 , window.h/2))
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
