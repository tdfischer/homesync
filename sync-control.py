#!/usr/bin/env python
from PyQt4 import QtCore, QtGui
from Ui_MainWindow import Ui_MainWindow
import os, sys
from dbus.mainloop.qt import DBusQtMainLoop
import dbus
from datetime import datetime
import HomeSync

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
  def __init__(self):
    QtGui.QMainWindow.__init__(self)
    self.setupUi(self)
    #self.connect(self.actionBackup_Now,QtCore.SIGNAL('triggered()'), self.showSettings)
    bus = dbus.SessionBus()
    serverObj = bus.get_object(HomeSync.DBUS_SERVER_NAME, HomeSync.DBUS_SERVER_PATH);
    self.server = dbus.Interface(serverObj, dbus_interface=HomeSync.DBUS_SERVER_INTERFACE)
    self.statusList = QtGui.QStringListModel(self)
    self.statusList.setStringList(self.server.ListFiles(2))
    self.fileView.setModel(self.statusList)
    selection = self.fileView.selectionModel()
    self.connect(selection, QtCore.SIGNAL('currentChanged(QModelIndex, QModelIndex)'), self.showDetails)

  def showDetails(self, current, previous):
    revisions = self.server.FileRevisions(str(current.data().toString()))
    stamp = datetime.fromtimestamp(revisions[0][1])
    self.lbl_archiveStamp.setText(stamp.strftime('%c'))
    if os.path.exists(str(current.data().toString())):
      stamp = datetime.fromtimestamp(str(os.path.getmtime(current.data().toString())))
      self.lbl_modstamp.setText(stamp.strftime('%c'))
      self.lbl_status.setText("Archived");
    else:
      self.lbl_status.setText("Deleted");
    revisionList = QtGui.QStringListModel(self)
    strList = QtCore.QStringList();
    now = datetime.now()
    for rev in revisions:
      stamp = datetime.fromtimestamp(rev[1])
      #diff = now-stamp
      strList.append(stamp.strftime('%c'))
    revisionList.setStringList(strList)
    self.revisionView.setModel(revisionList)

if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  mw = MainWindow()
  mw.show()
  sys.exit(app.exec_())
