# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sucond_design.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.text_label = QtWidgets.QLabel(self.centralwidget)
        self.text_label.setGeometry(QtCore.QRect(0, 10, 141, 461))
        self.text_label.setMouseTracking(False)
        self.text_label.setObjectName("text_label")
        self.img_btn = QtWidgets.QPushButton(self.centralwidget)
        self.img_btn.setGeometry(QtCore.QRect(0, 470, 121, 81))
        self.img_btn.setObjectName("img_btn")
        self.img_laebl = QtWidgets.QLabel(self.centralwidget)
        self.img_laebl.setGeometry(QtCore.QRect(156, 6, 641, 541))
        self.img_laebl.setObjectName("img_laebl")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(130, 0, 20, 551))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName("menubar")
        self.menuMenu = QtWidgets.QMenu(self.menubar)
        self.menuMenu.setObjectName("menuMenu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.exit_menu = QtWidgets.QAction(MainWindow)
        self.exit_menu.setObjectName("exit_menu")
        self.change_img_menu = QtWidgets.QAction(MainWindow)
        self.change_img_menu.setObjectName("change_img_menu")
        self.menuMenu.addAction(self.exit_menu)
        self.menuMenu.addSeparator()
        self.menuMenu.addAction(self.change_img_menu)
        self.menubar.addAction(self.menuMenu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.text_label.setText(_translate("MainWindow", "TextLabel"))
        self.img_btn.setText(_translate("MainWindow", "IMG"))
        self.img_laebl.setText(_translate("MainWindow", "TextLabel"))
        self.menuMenu.setTitle(_translate("MainWindow", "menu"))
        self.exit_menu.setText(_translate("MainWindow", "exit"))
        self.change_img_menu.setText(_translate("MainWindow", "change_img"))

