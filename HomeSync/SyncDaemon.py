import os, sys
import logging
import threading

from SyncWatcher import SyncWatcher
from AvahiBrowser import AvahiBrowser
from DeviceWatcher import DeviceWatcher
from SyncArchive import SyncArchive
from Jobs import Job
import dbus.service

class Crawler:
  def __init__(self,archive):
    self.archive = archive
    self.dirs = []
  
  def start(self):
    self.dive(self.archive.path)
  
  def dive(self,path):
    files = os.listdir(path)
    list = []
    for f in files:
      if os.path.isfile(os.path.join(path,f)) and not self.archive.isIgnored(os.path.join(path,f)):
        list.append(os.path.join(path,f))
      if os.path.isdir(os.path.join(path,f)):
        self.archive.jobs.enqueue( Job(self.dive,args=(os.path.join(path, f),)) ).setPriority(-2)
    if list != []:
      self.archive.addFiles(*list).setPriority(-1)

class SyncDaemon(dbus.service.Object):
  def __init__(self):
    self.log = logging.getLogger('SyncDaemon')
    self.log.debug("Created SyncDaemon")
    self.log.debug("Attaching to D-BUS")
    self.name = dbus.service.BusName("net.wm161.HomeSync",bus=dbus.SessionBus())
    dbus.service.Object.__init__(self, object_path="/Server", conn=dbus.SessionBus(), bus_name=self.name)

    home = os.environ["HOME"]
    os.chdir(home)
    self.archive = SyncArchive(home, backup=False)
    self.archive.create()

    os.nice(5)
    #if (self.git.exists() == False):
      #self.log.info("Missing Git repo. Running git-init.")
      #self.jobs.enqueue(self.git.init)
      #self.jobs.enqueue(self.git.setConfig,"core.excludesfile",home+"/.home-sync/ignore")
      #self.jobs.enqueue(self.git.setConfig,"core.compression",-1)

    #self.log.debug("Watching %s"%(home))
    #self.watcher = SyncWatcher()
    #self.watcher.add(home)
    #QtCore.QObject.connect(self.watcher,QtCore.SIGNAL("directoryChanged(QString)"),self.dirUpdate)
    self.Ready()
    
    self.log.info("Starting index crawler")
    self.crawler = Crawler(self.archive)
    self.crawler.start()
    
    self.avahi = AvahiBrowser()
    self.deviceWatcher = DeviceWatcher()
  
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
    self.log.debug("Listing files of type %i"%(type))
    return self.git.files(type)
  
  @dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', in_signature='s')
  def AddFile(self,file):
    self.log.debug("Adding %s to repository",file)
    self.jobs.enqueue(self.git.add,file,self.FileAdded)
    self.jobs.enqueue(self.git.commit, "%s added"%(file), callback=self.FileCommitted)
  
  @dbus.service.method(dbus_interface='net.wm161.HomeSync.Server')
  def ArchiveNow(self):
    self.log.info("Requested an immediate archive.")
    self.jobs.enqueue(self.git.commitAll,"On Demand Archive", callback=self.FileCommitted)
  
  @dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', in_signature='s')
  def CommitFile(self, file):
    self.log.info("Committing %s",file)
    self.jobs.enqueue(self.git.commit,"Requested commit for %s"%(file), path=file, callback=self.FileCommitted)
  
  @dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', in_signature='s')
  def CreateBackup(self, path):
    self.log.info("Creating backup on %s",path)
    backup = GitInterface(path,bare=True)
    backup.init()
  
  @dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', in_signature='s')
  def Backup(self, path):
    self.log.info("Pushing backup to %s",path)
    #backup = GitInterface(path,bare=True)
    self.jobs.enqueue(self.git.push,path)
  
  @dbus.service.method(dbus_interface='net.wm161.HomeSync.Server')
  def ExitDaemon(self):
    self.log.info("Exiting")
    sys.exit()
  
  @dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', in_signature='s', out_signature="a(si)")
  def FileRevisions(self,path):
    self.log.debug("Requesting revisions of %s"%(path))
    return self.git.revisionList(path)
  
  @dbus.service.signal(dbus_interface='net.wm161.HomeSync.Server')
  def Ready(self):
    self.log.debug("Ready.")
  
  @dbus.service.signal(dbus_interface='net.wm161.HomeSync.Server', signature='s')
  def FileAdded(self,file):
    self.log.debug("File added: %s",file)
    
  @dbus.service.signal(dbus_interface='net.wm161.HomeSync.Server', signature='s')
  def FileCommitted(self, file):
    self.log.debug("File committed: %s",file)
  
  @dbus.service.signal(dbus_interface='net.wm161.HomeSync.Server', signature='s')
  def FileChanged(self,path):
    #TODO: Detect batch updates
    self.log.debug("Detected change in file %s"%(path))
    self.jobs.enqueue(self.git.commit,"%s modification"%(path), path=path, callback=self.FileCommitted)
  
  @dbus.service.signal(dbus_interface='net.wm161.HomeSync.Server', signature='s')
  def DirectoryChanged(self,path):
    self.log.debug("Detected change in directory %s"%(path))
    self.jobs.enqueue(self.git.commit,"%s modification"%(file), path=path, callback=self.FileCommitted)
