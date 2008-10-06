#!/usr/bin/env python
import sys
import os
import logging
import threading

from PyQt4 import QtCore
from dbus.mainloop.qt import DBusQtMainLoop
#from dbus.bus import BusConnection
import dbus.service
import avahi

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
    self.name = dbus.service.BusName("net.wm161.HomeSync",bus=dbus.SessionBus())
    
    home = os.environ["HOME"]
    os.chdir(home)
    self.git = GitInterface(home+"/.home-sync/git",home)
    if (os.path.exists(home+"/.home-sync") == False):
      logging.info("First-Run init")
      os.mkdir(home+"/.home-sync")
    
    if (os.path.exists(home+"/.home-sync/ignore") == False):
      logging.info("Missing ignore file. Creating defaults.")
      defaultIgnores = [
        ".home-sync",
        ".local/share/Trash"
        #".kde/share/
      ]
      ignoreFile = open(home+"/.home-sync/ignore","w")
      ignoreFile.writelines(defaultIgnores)
      ignoreFile.close()
      
    if (self.git.exists() == False):
      logging.info("Missing Git repo. Running git-init.")
      self.git.init()
      self.git.setConfig("core.excludesfile",home+"/.home-sync/ignore")
      self.git.setConfig("core.compression",-1)
      logging.info("Adding HOME to the repository.")
    
    logging.debug("Watching %s"%(home))
    self.watcher = SyncWatcher(home)
    self.watcher.removePaths(self.watcher.directories())
    self.watcher.removePaths(self.watcher.files())
    QtCore.QObject.connect(self.watcher,QtCore.SIGNAL("directoryChanged(QString)"),self.dirUpdate)
    
    dbus.service.Object.__init__(self, object_path="/Server", conn=dbus.SessionBus(), bus_name=self.name)
    self.Ready()
    
    bus = dbus.SystemBus()
    self.avahi = dbus.Interface(bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER), avahi.DBUS_INTERFACE_SERVER)
    
    self.avahiGroup = dbus.Interface(bus.get_object(avahi.DBUS_NAME, self.avahi.EntryGroupNew()), avahi.DBUS_INTERFACE_ENTRY_GROUP)
    
    self.avahiGroup.AddService(
      avahi.IF_UNSPEC,
      avahi.PROTO_UNSPEC,
      dbus.UInt32(0),
      "HomeSync Server",
      "_git._tcp",
      "","",
      dbus.UInt16(9418),
      avahi.dict_to_txt_array({"HomeSync":1,"UID":500}))
    self.avahiGroup.Commit()
    
    self.browser = dbus.Interface(bus.get_object(avahi.DBUS_NAME,
      self.avahi.ServiceBrowserNew(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, '_git._tcp', 'local', dbus.UInt32(0))),
      avahi.DBUS_INTERFACE_SERVICE_BROWSER)
    self.browser.connect_to_signal("ItemNew", self.discoveredServer)
    
  def discoveredServer(self, interface, protocol, name, stype, domain, flags):
    print "Found service '%s' type '%s' domain '%s' " % (name, stype, domain)
    if flags & avahi.LOOKUP_RESULT_LOCAL:
      # local service, skip
      pass
    self.avahi.ResolveService(interface, protocol, name, stype, 
      domain, avahi.PROTO_UNSPEC, dbus.UInt32(0), 
      reply_handler=self.resolvedServer, error_handler=self.resolveFailed)
  
  def resolveFailed(self, *args):
    print args[0]

  def resolvedServer(self, *args):
    print 'service resolved'
    print 'name:', args[2]
    print 'address:', args[7]
    print 'port:', args[8]
  
  def dirUpdate(self,path):
    path = unicode(path).replace(os.environ["HOME"]+"/",'./',1)
    self.DirectoryChanged(path)
    
  @dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', in_signature='s')
  def PushToServer(self, remote):
    pass
  
  @dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', out_signature='as')
  def DiscoveredHosts(self):
    pass
  
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
  
  @dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', in_signature='s', out_signature="a(si)")
  def FileRevisions(self,path):
    logging.debug("Requesting revisions of %s"%(path))
    return self.git.revisionList(path)
  
  @dbus.service.signal(dbus_interface='net.wm161.HomeSync.Server')
  def Ready(self):
    logging.debug("Ready.")
  
  @dbus.service.signal(dbus_interface='net.wm161.HomeSync.Server', signature='s')
  def FileChanged(self,path):
    logging.debug("Detected change in file %s"%(path))
    #threading.Thread(target=GitInterface.update,args=(self.git,path)).start()
    threading.Thread(target=GitInterface.commit,args=(self.git,path,"%s modification"%(path))).start()
  
  @dbus.service.signal(dbus_interface='net.wm161.HomeSync.Server', signature='s')
  def DirectoryChanged(self,path):
    logging.debug("Detected change in directory %s"%(path))
    #threading.Thread(target=GitInterface.update,args=(self.git,path)).start()
    threading.Thread(target=GitInterface.commit,args=(self.git,path,"%s modification"%(path))).start()

if __name__ == "__main__":
  DBusQtMainLoop(set_as_default=True)
  app = QtCore.QCoreApplication(sys.argv)
  server = SyncDaemon()
  sys.exit(app.exec_())