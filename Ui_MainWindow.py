# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created: Sun Oct  5 20:38:06 2008
#      by: PyQt4 UI code generator 4.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(749,626)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.vboxlayout = QtGui.QVBoxLayout(self.centralwidget)
        self.vboxlayout.setObjectName("vboxlayout")
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.vboxlayout1 = QtGui.QVBoxLayout(self.layoutWidget)
        self.vboxlayout1.setObjectName("vboxlayout1")
        self.groupBox = QtGui.QGroupBox(self.layoutWidget)
        self.groupBox.setObjectName("groupBox")
        self.vboxlayout2 = QtGui.QVBoxLayout(self.groupBox)
        self.vboxlayout2.setObjectName("vboxlayout2")
        self.lineEdit = QtGui.QLineEdit(self.groupBox)
        self.lineEdit.setObjectName("lineEdit")
        self.vboxlayout2.addWidget(self.lineEdit)
        self.fileView = QtGui.QListView(self.groupBox)
        self.fileView.setObjectName("fileView")
        self.vboxlayout2.addWidget(self.fileView)
        self.vboxlayout1.addWidget(self.groupBox)
        self.tabWidget = QtGui.QTabWidget(self.layoutWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")
        self.hboxlayout = QtGui.QHBoxLayout(self.tab)
        self.hboxlayout.setObjectName("hboxlayout")
        self.vboxlayout3 = QtGui.QVBoxLayout()
        self.vboxlayout3.setObjectName("vboxlayout3")
        self.lineEdit_2 = QtGui.QLineEdit(self.tab)
        self.lineEdit_2.setFrame(True)
        self.lineEdit_2.setReadOnly(True)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.vboxlayout3.addWidget(self.lineEdit_2)
        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout3.addItem(spacerItem)
        self.gridlayout = QtGui.QGridLayout()
        self.gridlayout.setObjectName("gridlayout")
        self.label = QtGui.QLabel(self.tab)
        self.label.setObjectName("label")
        self.gridlayout.addWidget(self.label,0,0,1,1)
        self.lbl_modstamp = QtGui.QLabel(self.tab)
        self.lbl_modstamp.setObjectName("lbl_modstamp")
        self.gridlayout.addWidget(self.lbl_modstamp,0,1,1,1)
        self.label_3 = QtGui.QLabel(self.tab)
        self.label_3.setObjectName("label_3")
        self.gridlayout.addWidget(self.label_3,1,0,1,1)
        self.lbl_archiveStamp = QtGui.QLabel(self.tab)
        self.lbl_archiveStamp.setObjectName("lbl_archiveStamp")
        self.gridlayout.addWidget(self.lbl_archiveStamp,1,1,1,1)
        self.label_2 = QtGui.QLabel(self.tab)
        self.label_2.setObjectName("label_2")
        self.gridlayout.addWidget(self.label_2,2,0,1,1)
        self.lbl_status = QtGui.QLabel(self.tab)
        self.lbl_status.setObjectName("lbl_status")
        self.gridlayout.addWidget(self.lbl_status,2,1,1,1)
        self.vboxlayout3.addLayout(self.gridlayout)
        self.hboxlayout.addLayout(self.vboxlayout3)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName("hboxlayout1")
        self.line = QtGui.QFrame(self.tab)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.hboxlayout1.addWidget(self.line)
        self.vboxlayout4 = QtGui.QVBoxLayout()
        self.vboxlayout4.setObjectName("vboxlayout4")
        self.btn_archiveFile = QtGui.QPushButton(self.tab)
        self.btn_archiveFile.setObjectName("btn_archiveFile")
        self.vboxlayout4.addWidget(self.btn_archiveFile)
        self.chk_ignoreFile = QtGui.QCheckBox(self.tab)
        self.chk_ignoreFile.setObjectName("chk_ignoreFile")
        self.vboxlayout4.addWidget(self.chk_ignoreFile)
        spacerItem1 = QtGui.QSpacerItem(20,71,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout4.addItem(spacerItem1)
        self.hboxlayout1.addLayout(self.vboxlayout4)
        self.hboxlayout.addLayout(self.hboxlayout1)
        self.tabWidget.addTab(self.tab,"")
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.vboxlayout5 = QtGui.QVBoxLayout(self.tab_2)
        self.vboxlayout5.setObjectName("vboxlayout5")
        self.revisionView = QtGui.QListView(self.tab_2)
        self.revisionView.setObjectName("revisionView")
        self.vboxlayout5.addWidget(self.revisionView)
        self.btnRestore = QtGui.QPushButton(self.tab_2)
        self.btnRestore.setObjectName("btnRestore")
        self.vboxlayout5.addWidget(self.btnRestore)
        self.tabWidget.addTab(self.tab_2,"")
        self.vboxlayout1.addWidget(self.tabWidget)
        self.toolBox = QtGui.QToolBox(self.splitter)
        self.toolBox.setObjectName("toolBox")
        self.page = QtGui.QWidget()
        self.page.setGeometry(QtCore.QRect(0,0,209,464))
        self.page.setObjectName("page")
        self.vboxlayout6 = QtGui.QVBoxLayout(self.page)
        self.vboxlayout6.setObjectName("vboxlayout6")
        self.btn_archiveNow = QtGui.QPushButton(self.page)
        self.btn_archiveNow.setObjectName("btn_archiveNow")
        self.vboxlayout6.addWidget(self.btn_archiveNow)
        self.btn_archiveMore = QtGui.QPushButton(self.page)
        self.btn_archiveMore.setObjectName("btn_archiveMore")
        self.vboxlayout6.addWidget(self.btn_archiveMore)
        self.pushButton = QtGui.QPushButton(self.page)
        self.pushButton.setObjectName("pushButton")
        self.vboxlayout6.addWidget(self.pushButton)
        spacerItem2 = QtGui.QSpacerItem(133,181,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout6.addItem(spacerItem2)
        self.toolBox.addItem(self.page,"")
        self.page_2 = QtGui.QWidget()
        self.page_2.setGeometry(QtCore.QRect(0,0,209,464))
        self.page_2.setObjectName("page_2")
        self.vboxlayout7 = QtGui.QVBoxLayout(self.page_2)
        self.vboxlayout7.setObjectName("vboxlayout7")
        self.groupBox_2 = QtGui.QGroupBox(self.page_2)
        self.groupBox_2.setObjectName("groupBox_2")
        self.vboxlayout8 = QtGui.QVBoxLayout(self.groupBox_2)
        self.vboxlayout8.setObjectName("vboxlayout8")
        self.checkBox = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox.setObjectName("checkBox")
        self.vboxlayout8.addWidget(self.checkBox)
        self.line_2 = QtGui.QFrame(self.groupBox_2)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.vboxlayout8.addWidget(self.line_2)
        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setObjectName("hboxlayout2")
        self.label_4 = QtGui.QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")
        self.hboxlayout2.addWidget(self.label_4)
        self.spinBox = QtGui.QSpinBox(self.groupBox_2)
        self.spinBox.setObjectName("spinBox")
        self.hboxlayout2.addWidget(self.spinBox)
        self.label_5 = QtGui.QLabel(self.groupBox_2)
        self.label_5.setObjectName("label_5")
        self.hboxlayout2.addWidget(self.label_5)
        self.vboxlayout8.addLayout(self.hboxlayout2)
        self.timeEdit = QtGui.QTimeEdit(self.groupBox_2)
        self.timeEdit.setObjectName("timeEdit")
        self.vboxlayout8.addWidget(self.timeEdit)
        self.vboxlayout7.addWidget(self.groupBox_2)
        self.groupBox_3 = QtGui.QGroupBox(self.page_2)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkBox_2 = QtGui.QCheckBox(self.groupBox_3)
        self.checkBox_2.setObjectName("checkBox_2")
        self.verticalLayout.addWidget(self.checkBox_2)
        self.vboxlayout7.addWidget(self.groupBox_3)
        spacerItem3 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout7.addItem(spacerItem3)
        self.toolBox.addItem(self.page_2,"")
        self.page_3 = QtGui.QWidget()
        self.page_3.setGeometry(QtCore.QRect(0,0,209,464))
        self.page_3.setObjectName("page_3")
        self.toolBox.addItem(self.page_3,"")
        self.vboxlayout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,749,27))
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
        self.tabWidget.setCurrentIndex(0)
        self.toolBox.setCurrentIndex(2)
        QtCore.QObject.connect(self.btn_archiveNow,QtCore.SIGNAL("clicked()"),self.actionBackup_Now.trigger)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Files", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Modification date:", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_modstamp.setText(QtGui.QApplication.translate("MainWindow", "Today", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MainWindow", "Last archive date:", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_archiveStamp.setText(QtGui.QApplication.translate("MainWindow", "Never", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Status:", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_status.setText(QtGui.QApplication.translate("MainWindow", "Not in archive", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_archiveFile.setText(QtGui.QApplication.translate("MainWindow", "Archive Now", None, QtGui.QApplication.UnicodeUTF8))
        self.chk_ignoreFile.setText(QtGui.QApplication.translate("MainWindow", "Ignore", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("MainWindow", "Status", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRestore.setText(QtGui.QApplication.translate("MainWindow", "Restore...", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("MainWindow", "History", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_archiveNow.setText(QtGui.QApplication.translate("MainWindow", "Archive All", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_archiveMore.setText(QtGui.QApplication.translate("MainWindow", "Archive...", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("MainWindow", "Restore...", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), QtGui.QApplication.translate("MainWindow", "Archive", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setWhatsThis(QtGui.QApplication.translate("MainWindow", "If enabled, HomeSync will create a revision for all your files at this given time", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("MainWindow", "Daily Archive", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("MainWindow", "Enable", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("MainWindow", "Every ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("MainWindow", "days at", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setWhatsThis(QtGui.QApplication.translate("MainWindow", "If enabled, HomeSync will monitor your files for any changes and create revisions automatically.", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("MainWindow", "Update Monitoring", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_2.setText(QtGui.QApplication.translate("MainWindow", "Enable", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), QtGui.QApplication.translate("MainWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_3), QtGui.QApplication.translate("MainWindow", "Preview", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSettings.setText(QtGui.QApplication.translate("MainWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBackup_Now.setText(QtGui.QApplication.translate("MainWindow", "Backup Now", None, QtGui.QApplication.UnicodeUTF8))

