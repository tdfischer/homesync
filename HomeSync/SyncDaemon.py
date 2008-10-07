import os
import logging
import threading

from SyncWatcher import SyncWatcher
from GitInterface import *
from AvahiBrowser import AvahiBrowser
from DeviceWatcher import DeviceWatcher
import dbus.service
from PyQt4 import QtCore

class JobQueue(threading.Thread, dbus.service.Object):
  def __init__(self):
    threading.Thread.__init__(self)
    name = dbus.service.BusName("net.wm161.HomeSync", bus=dbus.SessionBus())
    dbus.service.Object.__init__(self, object_path="/Jobs/Queue", conn=dbus.SessionBus(), bus_name=name)
    self.log = logging.getLogger('SyncDaemon.JobQueue')
    self.queueReady = threading.Condition()
    self.queue = []
    self.active = None
  
  def enqueue(self,*args, **kwargs):
    self.queueReady.acquire()
    if isinstance(args[0], Job):
      self.queue.insert(0,args[0])
    else:
      self.queue.insert(0,Job(*args, **kwargs))
    self.log.info("Queued job %s"%(self.queue[0]))
    self.queueReady.notify()
    self.queueReady.release()

  def run(self):
    while (True):
      self.checkQueue()

  def checkQueue(self):
    self.queueReady.acquire()
    while len(self.queue)==0:
      self.queueReady.wait()
    job = self.queue.pop()
    self.queueReady.release()
    self.log.info("Starting job %s",job)
    job.start()
    job.join()
    self.log.info("Job exited: %s", job)

class Job(threading.Thread, dbus.service.Object):
  id = 0
  def __init__(self,call,*args, **kwargs):
    Job.id += 1
    self.id = Job.id
    name = dbus.service.BusName("net.wm161.HomeSync", bus=dbus.SessionBus())
    dbus.service.Object.__init__(self, object_path="/Jobs/"+str(self.id), conn=dbus.SessionBus(), bus_name=name)
    
    threading.Thread.__init__(self)
    self.call=call
    self.args=args
    self.kwargs=kwargs
    
    #if isinstance(call,instancemethod):
    try:
      self.name = call.im_func.__name__
    except:
      self.name = call.__name__

  def __del__(self):
    Job.id-=1
  
  def __str__(self):
    return "#%i %s %s %s"%(self.id, self.name, self.args, self.kwargs)
    
  def run(self):
    self.call(*self.args,**self.kwargs)

class SyncDaemon(dbus.service.Object):
  def __init__(self):
    self.log = logging.getLogger('SyncDaemon')
    self.log.debug("Created SyncDaemon")
    self.log.debug("Attaching to D-BUS")
    self.name = dbus.service.BusName("net.wm161.HomeSync",bus=dbus.SessionBus())
    dbus.service.Object.__init__(self, object_path="/Server", conn=dbus.SessionBus(), bus_name=self.name)

    self.jobs = JobQueue()
    self.jobs.start()

    home = os.environ["HOME"]
    os.chdir(home)
    self.git = GitInterface(home+"/.home-sync/git",home)
    if (os.path.exists(home+"/.home-sync") == False):
      self.log.info("First-Run init")
      os.mkdir(home+"/.home-sync")

    if (os.path.exists(home+"/.home-sync/ignore") == False):
      self.log.info("Missing ignore file. Creating defaults.")
      defaultIgnores = [
        "/.home-sync",
        "/.local/share/Trash"
      ]
      ignoreFile = open(home+"/.home-sync/ignore","w")
      ignoreFile.writelines(defaultIgnores)
      ignoreFile.close()
      
    #Before we do the big initial import if at all needed, lets sneak away
    os.nice(5)
    if (self.git.exists() == False):
      self.log.info("Missing Git repo. Running git-init.")
      self.jobs.enqueue(self.git.init)
      self.jobs.enqueue(self.git.setConfig,"core.excludesfile",home+"/.home-sync/ignore")
      self.jobs.enqueue(self.git.setConfig,"core.compression",-1)
      self.log.info("Adding Documents to the repository.")
      self.jobs.enqueue(self.git.add,home+"/Documents", self.FileAdded)
      self.log.info("Committing to repository.")
      self.jobs.enqueue(self.git.commit,"Initial Archive", callback=self.FileCommitted)
    
    self.log.info("Commiting changes since last run")
    self.jobs.enqueue(self.git.commitAll,"HomeSync startup", callback=self.FileCommitted)

    self.log.debug("Watching %s"%(home))
    self.watcher = SyncWatcher()
    self.watcher.add(home)
    QtCore.QObject.connect(self.watcher,QtCore.SIGNAL("directoryChanged(QString)"),self.dirUpdate)
    self.Ready()
    
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
    QtCore.QCoreApplication.exit()
  
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
