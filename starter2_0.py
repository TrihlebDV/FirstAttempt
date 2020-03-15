#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#add path with necessary files to python
import sys, os
#curdir = os.path.abspath(os.curdir)
path = os.path.abspath(__file__)
curdir = os.path.dirname(path)
sys.path.insert(0, curdir + '/other_files')
sys.path.insert(0, curdir + '/wheel_platform/RPi')

#import necessary libraries for initiating Qt_object
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QByteArray, QEvent

import threading #library for implementing multithreading


#design
import forms

#lib for testing
import second


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('MainWindow')
        self.wt = forms.WaitWindow()
        self.menu = forms.MainMenu(self.show_psw, self.wt, second.start,
                                   second.start, second.start)
        self.psw = forms.Password(self.menu)
        self.psw.show()

    def show_psw(self):
        self.psw.nameLine.setPlaceholderText("  write nickname  ")
        self.psw.pswdLine.setPlaceholderText("  write password")
        self.psw.show()

    def show_window_2(self):
        self.w1.hide()
        self.w2 = forms.ExampleApp2(self.sleeping)
        self.w2.show()

    def sleeping(self):
        self.w2.hide()
        self.w1.nameLine.setPlaceholderText("  write nickname  ")
        self.w1.pswdLine.setPlaceholderText("  write password")
        self.w1.show()
        
        
    

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp
    #window.show()  # Показываем окно
    sys.exit(app.exec_())
    #app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
