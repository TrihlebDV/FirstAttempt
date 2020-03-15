#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#necessary libraries
import threading
import multiprocessing as mp
from time import sleep #it's need to control time delay
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QByteArray, QEvent

#design
import wait
import starter_desgn  #This is our converted design file
import test_form
import menu

class MainMenu(QtWidgets.QWidget, menu.Ui_Form):
    def __init__(self, psw, wait, main1, main2, main3):
        #Names and other information you can see in starter_desgn.py file
        super().__init__()
        self.setupUi(self)  #This is necessary to initialize our design
        self._wait = wait
        if (not psw is None) and callable(psw):
            self._psw = psw #обработчик события получен
        if (not main1 is None) and callable(main1):
            self._main1 = main1 #обработчик события получен
        if (not main2 is None) and callable(main2):
            self._main3 = main3 #обработчик события получен 
        if (not main3 is None) and callable(main3):
            self._main3 = main3 #обработчик события получен 
        self.pushButton.clicked.connect(self.first_way)
        #self.pushButton_2.clicked.connect(self.second_way)
        #self.pushButton_3.clicked.connect(self.theird_way)

    def first_way(self):
        self.hide()
        self._wait.show()
        self._main1(self._psw, self._wait)
        #mt1 = mp.Process(target=self._main1, args=(self._psw, self._wait))
        #self.daemon = True
        #self.hide()
        #self._wait.show()
        #mt1.start()
        #mt1.join()
        #print("ARR1")

class Password(QtWidgets.QWidget, starter_desgn.Ui_Dialog):
    def __init__(self, menu):
        #Names and other information you can see in starter_desgn.py file
        super().__init__()
        self.setupUi(self)  #This is necessary to initialize our design
        self._menu = menu
        self.entrButn.clicked.connect(self.pswdNickCheck)
        self.setWindowFlags(Qt.FramelessWindowHint) #nessesary to hide main bar
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
        #if(name == "papaRobot" or pswd == "creator"):
        if True:
            self.nameLine.setPlaceholderText("  correct")
            self.pswdLine.setPlaceholderText("  correct")
            self.hide()
            self._menu.show()
            
            
        else:
            self.nameLine.setPlaceholderText("  wrong nickname  ")
            self.pswdLine.setPlaceholderText("  wrong password")
            self.t1 = threading.Thread(target=self.textSetter)
            self.daemon = True
            self.t1.start()

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Message', "Do you want to close APP?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
            
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        if e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return:
            self.pswdNickCheck()

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

class WaitWindow(QtWidgets.QWidget, wait.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(500, 300, 400, 300)
