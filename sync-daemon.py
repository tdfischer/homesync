#!/usr/bin/env python
import sys
import logging
from HomeSync.SyncDaemon import SyncDaemon

from PyQt4 import QtCore
from dbus.mainloop.qt import DBusQtMainLoop

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  DBusQtMainLoop(set_as_default=True)
  app = QtCore.QCoreApplication(sys.argv)
  server = SyncDaemon()
  sys.exit(app.exec_())
