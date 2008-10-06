import os
import logging
import threading

from SyncWatcher import SyncWatcher
from GitInterface import GitInterface
from AvahiBrowser import AvahiBrowser
import dbus.service
from PyQt4 import QtCore

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
        "/.home-sync",
        "/.local/share/Trash"
      ]
      ignoreFile = open(home+"/.home-sync/ignore","w")
      ignoreFile.writelines(defaultIgnores)
      ignoreFile.close()
      
    if (self.git.exists() == False):
      logging.info("Missing Git repo. Running git-init.")
      self.git.init()
      self.git.setConfig("core.excludesfile",home+"/.home-sync/ignore")
      self.git.setConfig("core.compression",-1)
      logging.info("Adding Projects to the repository.")
      self.git.add(home+"/Projects")
      self.git.commit("Initial Archive")
    
    logging.debug("Watching %s"%(home))
    self.watcher = SyncWatcher()
    for path in self.git.files(GitInterface.FILES_CACHED):
      if os.path.isdir(path):
        logging.debug("Watching %s for changes",path)
        self.watcher.add(path)
    QtCore.QObject.connect(self.watcher,QtCore.SIGNAL("directoryChanged(QString)"),self.dirUpdate)
    
    dbus.service.Object.__init__(self, object_path="/Server", conn=dbus.SessionBus(), bus_name=self.name)
    self.Ready()
    
    #self.avahi = AvahiBrowser();
  
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
    threading.Thread(target=GitInterface.commit,args=(self.git,"%s added"%(file)),kwargs={'path':file}).start()
  
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
    #TODO: Queue batch updates
    logging.debug("Detected change in file %s"%(path))
    threading.Thread(target=GitInterface.commit,args=(self.git,"%s modification"%(path)),kwargs={'path':path}).start()
  
  @dbus.service.signal(dbus_interface='net.wm161.HomeSync.Server', signature='s')
  def DirectoryChanged(self,path):
    logging.debug("Detected change in directory %s"%(path))
    threading.Thread(target=GitInterface.commit,args=(self.git,"%s modification"%(path)),kwargs={'path':path}).start()