# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\usbHidTool.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.comboBox_hid_devices = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_hid_devices.setGeometry(QtCore.QRect(40, 40, 171, 41))
        self.comboBox_hid_devices.setObjectName("comboBox_hid_devices")
        self.lineEdit_input = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_input.setGeometry(QtCore.QRect(10, 140, 641, 31))
        self.lineEdit_input.setObjectName("lineEdit_input")
        self.textEdit_output_hex = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_output_hex.setGeometry(QtCore.QRect(10, 360, 461, 181))
        self.textEdit_output_hex.setObjectName("textEdit_output_hex")
        self.textEdit_output_str = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_output_str.setGeometry(QtCore.QRect(490, 360, 291, 181))
        self.textEdit_output_str.setObjectName("textEdit_output_str")
        self.pushButton_send = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_send.setGeometry(QtCore.QRect(670, 140, 93, 28))
        self.pushButton_send.setObjectName("pushButton_send")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.comboBox_hid_devices.activated['QString'].connect(MainWindow.hid_devices_actived)
        self.pushButton_send.clicked.connect(MainWindow.data_send)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_send.setText(_translate("MainWindow", "Send"))

