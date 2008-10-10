#!/usr/bin/env python
import sys
import logging
from HomeSync.SyncDaemon import SyncDaemon

try:
  from dbus.mainloop.glib import DBusGMainLoop
  import gobject
  glibLoop = True
except:
  try:
    from dbus.mainloop.qt import DBusQtMainLoop
    from PyQt4 import QtCore
    glibLoop = False
  except:
    print "No D-BUS main loops found."
    sys.exit()

if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)
  if glibLoop:
    DBusGMainLoop(set_as_default=True)
    server = SyncDaemon()
    loop = gobject.MainLoop()
    loop.run()
  else:
    DBusQtMainLoop(set_as_default=True)
    server = SyncDaemon()
    loop = QtCore.QEventLoop()
    sys.exit(loop._exec())
