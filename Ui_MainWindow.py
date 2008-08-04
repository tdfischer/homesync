# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created: Sun Apr 27 23:51:01 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(QtCore.QSize(QtCore.QRect(0,0,486,367).size()).expandedTo(MainWindow.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.hboxlayout = QtGui.QHBoxLayout(self.centralwidget)
        self.hboxlayout.setObjectName("hboxlayout")

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setObjectName("vboxlayout")

        self.revisionView = QtGui.QColumnView(self.centralwidget)
        self.revisionView.setObjectName("revisionView")
        self.vboxlayout.addWidget(self.revisionView)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.btnDetails = QtGui.QPushButton(self.centralwidget)
        self.btnDetails.setObjectName("btnDetails")
        self.hboxlayout1.addWidget(self.btnDetails)

        self.btnRestore = QtGui.QPushButton(self.centralwidget)
        self.btnRestore.setObjectName("btnRestore")
        self.hboxlayout1.addWidget(self.btnRestore)
        self.vboxlayout.addLayout(self.hboxlayout1)
        self.hboxlayout.addLayout(self.vboxlayout)

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.btnBackup = QtGui.QPushButton(self.centralwidget)
        self.btnBackup.setObjectName("btnBackup")
        self.vboxlayout1.addWidget(self.btnBackup)

        self.btnSettings = QtGui.QPushButton(self.centralwidget)
        self.btnSettings.setObjectName("btnSettings")
        self.vboxlayout1.addWidget(self.btnSettings)
        self.hboxlayout.addLayout(self.vboxlayout1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,486,24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.actionSettings = QtGui.QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")

        self.actionBackup_Now = QtGui.QAction(MainWindow)
        self.actionBackup_Now.setObjectName("actionBackup_Now")

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.btnBackup,QtCore.SIGNAL("clicked()"),self.actionBackup_Now.trigger)
        QtCore.QObject.connect(self.btnSettings,QtCore.SIGNAL("clicked()"),self.actionSettings.trigger)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDetails.setText(QtGui.QApplication.translate("MainWindow", "Details...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRestore.setText(QtGui.QApplication.translate("MainWindow", "Restore...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnBackup.setText(QtGui.QApplication.translate("MainWindow", "Backup Now", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSettings.setText(QtGui.QApplication.translate("MainWindow", "Settings...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSettings.setText(QtGui.QApplication.translate("MainWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBackup_Now.setText(QtGui.QApplication.translate("MainWindow", "Backup Now", None, QtGui.QApplication.UnicodeUTF8))

