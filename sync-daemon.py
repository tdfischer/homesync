#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
from HomeSync.SyncDaemon import SyncDaemon

from dbus.mainloop.glib import DBusGMainLoop
import gobject


if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)
  #DBusGMainLoop(set_as_default=True)
  server = SyncDaemon()
  #loop = gobject.MainLoop()
  #try:
    #loop.run()
  #except KeyboardInterrupt:
    #server.ExitDaemon()