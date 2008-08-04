#!/usr/bin/env python
import sys
import os
import logging
import threading

from PyQt4 import QtCore
from dbus.mainloop.qt import DBusQtMainLoop
import dbus.service

from GitInterface import GitInterface


class SyncWatcher(QtCore.QFileSystemWatcher):
  def __init__(self,path):
    QtCore.QFileSystemWatcher.__init__(self)
    self.add(path)

  def add(self,path):
    self.addPath(path)
    qDir=QtCore.QDir(path)
    
    for subdir in qDir.entryList(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.NoSymLinks):
      self.addPath(path+"/"+subdir)
      self.add(path+"/"+subdir)

class SyncDaemon(dbus.service.Object):
  def __init__(self):
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Created SyncDaemon")
    logging.debug("Attaching to D-BUS")
    self.name = dbus.service.BusName("net.wm161.HomeSync")
    
    home = os.environ["HOME"]
    os.chdir(home)
    self.git = GitInterface(home+"/.home-sync/git",home)
    if (os.path.exists(home+"/.home-sync") == False):
      logging.info("First-Run init")
      os.mkdir(home+"/.home-sync")
    
    if (self.git.exists() == False):
      logging.info("Missing Git repo. Running git-init.")
      self.git.init()
      self.git.setConfig("core.excludesfile",home+"/.home-sync/ignore")
      self.git.setConfig("core.compression",-1)
    
    if (os.path.exists(home+"/.home-sync/ignore") == False):
      
      logging.info("Missing ignore file. Creating defaults.")
    
    logging.debug("Watching %s"%(home))
    self.watcher = SyncWatcher(home)
    QtCore.QObject.connect(self.watcher,QtCore.SIGNAL("directoryChanged(QString)"),self.dirUpdate)
    
    dbus.service.Object.__init__(self, object_path="/net/wm161/HomeSync", conn=dbus.SessionBus(), bus_name=self.name)
    logging.debug("Ready.")
  
  def dirUpdate(self,path):
    path = unicode(path).replace(os.environ["HOME"]+"/",'./',1)
    self.DirectoryChanged(path)
    
  @dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', out_signature='as', in_signature='i')
  def ListFiles(self,type):
    logging.debug("Listing files of type %i"%(type))
    return self.git.files(type)
  
  @dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', in_signature='s')
  def AddFile(self,file):
    logging.debug("Adding %s to repository",file)
    threading.Thread(target=GitInterface.add,args=(self.git,file)).start()
    threading.Thread(target=GitInterface.commit,args=(self.git,file,"%s added"%(file))).start()
  
  @dbus.service.method(dbus_interface='net.wm161.HomeSync.Server')
  def ExitDaemon(self):
    logging.info("Exiting")
    QtCore.QCoreApplication.exit()
    
  @dbus.service.signal(dbus_interface='net.wm161.HomeSync.Server')
  def Ready(self):
    pass
  
  @dbus.service.signal(dbus_interface='net.wm161.HomeSync.Server', signature='s')
  def FileChanged(self,path):
    logging.debug("Detected change in file %s"%(path))
    threading.Thread(target=GitInterface.update,args=(self.git,path)).start()
    threading.Thread(target=GitInterface.commit,args=(self.git,path,"%s modification"%(path))).start()
  
  @dbus.service.signal(dbus_interface='net.wm161.HomeSync.Server', signature='s')
  def DirectoryChanged(self,path):
    logging.debug("Detected change in directory %s"%(path))
    threading.Thread(target=GitInterface.update,args=(self.git,path)).start()
    threading.Thread(target=GitInterface.commit,args=(self.git,path,"%s modification"%(path))).start()

if __name__ == "__main__":
  DBusQtMainLoop(set_as_default=True)
  app = QtCore.QCoreApplication(sys.argv)
  server = SyncDaemon()
  sys.exit(app.exec_())