#!/usr/bin/env python
from PyQt4 import QtCore, QtGui
from Ui_MainWindow import Ui_MainWindow
import os, sys
from dbus.mainloop.qt import DBusQtMainLoop
import dbus

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
  def __init__(self):
    QtGui.QMainWindow.__init__(self)
    self.setupUi(self)
    self.connect(self.actionBackup_Now,QtCore.SIGNAL('triggered()'), self.showSettings)
    bus = dbus.SessionBus()
    serverObj = bus.get_object('net.wm161.HomeSync', '/Server');
    self.server = dbus.Interface(serverObj, dbus_interface='net.wm161.HomeSync.Server')
    self.statusList = QtGui.QStringListModel(self)
    self.statusList.setStringList(self.server.ListFiles(2))
    #for file in self.server.ListFiles(2):
    #  self.statusList.append(file)
    self.fileView.setModel(self.statusList)

  def showSettings(self):
    print "Yep!"

if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  mw = MainWindow()
  mw.show()
  sys.exit(app.exec_())