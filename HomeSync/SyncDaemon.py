# -*- coding: utf-8 -*-
import os, sys
import logging
import threading

from SyncWatcher import SyncWatcher
from AvahiBrowser import AvahiBrowser
from DeviceWatcher import DeviceWatcher
from SyncArchive import SyncArchive
from Jobs import Job
from GitInterface import GitInterface, GitCallback
import dbus.service
import pyinotify

class Crawler:
  def __init__(self,archive):
    self.archive = archive
    self.dirs = []
  
  def start(self):
    self.dive(self.archive.path)
    self.archive.jobs.join()
  
  def dive(self,*paths):
    for path in paths:
      files = os.listdir(path)
      fileList = []
      dirList = []
      for f in files:
        f = os.path.join(path,f)
        if os.path.isfile(f) and not self.archive.isIgnored(f):
          fileList.append(f)
        if os.path.isdir(f):
          dirList.append(f)
      if fileList != []:
        self.archive.addFiles(*fileList).setPriority(-1)
      if dirList != []:
        j = Job(self.dive,args=dirList )
        j.setPriority(-2)
        self.archive.jobs.enqueue(j)

class Watcher(pyinotify.ProcessEvent):
  def __init__(self, archive):
    pyinotify.ProcessEvent.__init__(self)
    self.archive = archive
    self.wm = pyinotify.WatchManager()
    self.notifier = pyinotify.ThreadedNotifier(self.wm, self)
  
  def start(self):
    self.notifier.start()
    self.wm.add_watch(self.archive.path, pyinotify.EventCodes.IN_CREATE | pyinotify.EventCodes.IN_MODIFY, rec=True)
  
  def process_IN_CREATE(self, event):
    print "Created:", os.path.join(event.path, event.name)
    self.archive.addFiles(os.path.join(event.path, event.name))
  
  def process_IN_MODIFY(self, event):
    print "Modified:", os.path.join(event.path, event.name)
    self.archive.addFiles(os.path.join(event.path, event.name))

class DaemonCallback(GitCallback):
  def __init__(self, daemon):
    self.d = daemon
    
  def FilesAdded(self,files):
    for f in files:
      self.d.FileAdded(f)
  
  def FilesCommitted(self,files):
    for f in files:
      self.d.FileCommited(f)

class SyncDaemon:#(dbus.service.Object):
  def __init__(self):
    self.log = logging.getLogger('SyncDaemon')
    self.log.debug("Created SyncDaemon")
    self.log.debug("Attaching to D-BUS")
    self.name = dbus.service.BusName("net.wm161.HomeSync",bus=dbus.SessionBus())
    #dbus.service.Object.__init__(self, object_path="/Server", conn=dbus.SessionBus(), bus_name=self.name)

    home = os.environ["HOME"]
    os.chdir(home)
    self.archiveHandler = DaemonCallback(self)
    self.archive = SyncArchive(home, backup=False, gitHandler = self.archiveHandler)
    self.archive.create()

    #os.nice(5)
    
    self.Ready()
    
    self.log.info("Starting indexing crawler")
    self.crawler = Crawler(self.archive)
    self.crawler.start()
    self.watcher = Watcher(self.archive)
    self.watcher.start()
    
    #self.avahi = AvahiBrowser()
    #self.deviceWatcher = DeviceWatcher()
    self.log.info("Ready for action.")
  
  def dirUpdate(self,path):
    path = unicode(path).replace(os.environ["HOME"]+"/",'./',1)
    self.DirectoryChanged(path)
    
  #@dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', in_signature='s')
  def PushToServer(self, remote):
    pass
  
  #@dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', out_signature='as')
  def DiscoveredHosts(self):
    pass
  
  #@dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', out_signature='as', in_signature='i')
  def ListFiles(self,type):
    self.log.debug("Listing files of type %i"%(type))
    return self.git.files(type)
  
  #@dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', in_signature='s')
  def AddFile(self,file):
    self.log.debug("Adding %s to repository",file)
    self.jobs.enqueue(self.git.add,file,self.FileAdded)
    self.jobs.enqueue(self.git.commit, "%s added"%(file), callback=self.FileCommitted)
  
  #@dbus.service.method(dbus_interface='net.wm161.HomeSync.Server')
  def ArchiveNow(self):
    self.log.info("Requested an immediate archive.")
    self.jobs.enqueue(self.git.commitAll,"On Demand Archive", callback=self.FileCommitted)
  
  #@dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', in_signature='s')
  def CommitFile(self, file):
    self.log.info("Committing %s",file)
    self.jobs.enqueue(self.git.commit,"Requested commit for %s"%(file), path=file, callback=self.FileCommitted)
  
  #@dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', in_signature='s')
  def CreateBackup(self, path):
    self.log.info("Creating backup on %s",path)
    backup = GitInterface(path,bare=True)
    backup.init()
  
  #@dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', in_signature='s')
  def Backup(self, path):
    self.log.info("Pushing backup to %s",path)
    #backup = GitInterface(path,bare=True)
    self.jobs.enqueue(self.git.push,path)
  
  #@dbus.service.method(dbus_interface='net.wm161.HomeSync.Server')
  def ExitDaemon(self):
    self.log.info("Exiting")
    sys.exit()
  
  #@dbus.service.method(dbus_interface='net.wm161.HomeSync.Server', in_signature='s', out_signature="a(si)")
  def FileRevisions(self,path):
    self.log.debug("Requesting revisions of %s"%(path))
    return self.git.revisionList(path)
  
  #@dbus.service.signal(dbus_interface='net.wm161.HomeSync.Server')
  def Ready(self):
    self.log.debug("Ready.")
  
  #@dbus.service.signal(dbus_interface='net.wm161.HomeSync.Server', signature='s')
  def FileAdded(self,file):
    self.log.debug("File added: %s",file)
    
  #@dbus.service.signal(dbus_interface='net.wm161.HomeSync.Server', signature='s')
  def FileCommitted(self, file):
    self.log.debug("File committed: %s",file)
