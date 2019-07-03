#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#add path with necessary files to python
import sys, os
curdir = os.path.abspath(os.curdir)
sys.path.insert(0, curdir + '/other_files')

#import necessary libraries for initiating Qt_object
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QByteArray, QEvent

import starter_desgn  #This is our converted design file

import threading #library for implementing multithreading
from time import sleep #it's need to control time delay

import test_form
    
    

class ExampleApp2(QtWidgets.QWidget, test_form.Ui_Form):
    def __init__(self, sleeping):
        #Names and other information you can see in starter_desgn.py file
        super().__init__()
        self.setupUi(self)  #This is necessary to initialize our design
        self.sleeping = sleeping
        self.pushButton.clicked.connect(self.closing)
        self.pushButton_2.clicked.connect(self.resizes)
        self.sizeFlag = True
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(550, 350, 300, 200)
        

    def closing(self):
        self.sleeping()

    def resizes(self):
        if self.sizeFlag:
            self.setGeometry(500, 300, 600, 400)
            self.sizeFlag = False
            self.pushButton.setEnabled(False)
        else:
            self.pushButton.setEnabled(True)
            self.setGeometry(500, 300, 300, 200)
            self.sizeFlag = True

class ExampleApp1(QtWidgets.QWidget, starter_desgn.Ui_Dialog):
    def __init__(self, voidWindow):
        #Names and other information you can see in starter_desgn.py file
        super().__init__()
        self.setupUi(self)  #This is necessary to initialize our design
        self.voidWindow = voidWindow
        self.entrButn.clicked.connect(self.pswdNickCheck)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(500, 300, 400, 300)
        

    def textSetter(self):
        sleep(2)
        self.nameLine.setPlaceholderText("  write nickname  ")
        self.pswdLine.setPlaceholderText("  write password")

    def pswdNickCheck(self):
        name = self.nameLine.text()
        pswd = self.pswdLine.text()
        self.nameLine.setText("")
        self.pswdLine.setText("")
        if(name == "papaRobot" or pswd == "creator"):
            self.nameLine.setPlaceholderText("  correct")
            self.pswdLine.setPlaceholderText("  correct")
            self.voidWindow()
            
            
        else:
            self.nameLine.setPlaceholderText("  wrong nickname  ")
            self.pswdLine.setPlaceholderText("  wrong password")
            self.t1 = threading.Thread(target=self.textSetter)
            self.daemon = True
            self.t1.start()

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Message', "Are you fucking crazy?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
            
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        if e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return:
            self.pswdNickCheck()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('MainWindow')
        self.show_window_1()

    def show_window_1(self):
        self.w1 = ExampleApp1(self.show_window_2)
        self.w1.show()

    def show_window_2(self):
        self.w1.hide()
        self.w2 = ExampleApp2(self.sleeping)
        self.w2.show()

    def sleeping(self):
        self.w2.hide()
        self.w1.show()
        
    

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp
    #window.show()  # Показываем окно
    sys.exit(app.exec_())
    #app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
