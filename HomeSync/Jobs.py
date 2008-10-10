import threading
import logging

class JobQueue(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.log = logging.getLogger('JobQueue')
    self.queue = []
    self.queueReady = threading.Condition()
    self.running = threading.Event()
    self.running.set()
    self.active = None
  
  def enqueue(self,job):
    self.queueReady.acquire()

    self.queue.insert(0,job)
    self.queue = sorted(self.queue)
    self.log.debug("Queued job %s"%(job))
    self.log.debug("Arguments: %s %s",job.args, job.kwargs)
    self.queueReady.notify()
    self.queueReady.release()
    self.NewJob(job.id)
    return job

  def run(self):
    while (True):
      self.processJobs()
   
  def processJobs(self):
    self.running.wait()
    self.queueReady.acquire()
    while self.haveJobs() == False:
      self.queueReady.wait()
    self.queue = sorted(self.queue)
    self.active= self.queue.pop()
    self.queueReady.release()
    self.log.info("Starting job %s",self.active)
    self.log.debug("Arguments: %s %s",self.active.args, self.active.kwargs)
    self.active.start()
    self.active.join()
    self.log.info("Job complete: %s", self.active)
    self.JobComplete(self.active.id)
    del self.active
    self.active = None
    
  def haveJobs(self):
    return len(self.queue)>0
  
  #@dbus.service.signal(dbus_interface='net.wm161.HomeSync.JobQueue', signature='i')
  def NewJob(self,id):
    pass
  
  #@dbus.service.signal(dbus_interface='net.wm161.HomeSync.JobQueue', signature='i')
  def JobComplete(self,id):
    pass
  
  #@dbus.service.method(dbus_interface='net.wm161.HomeSync.JobQueue')
  def Pause(self):
    self.running.clear()
  
  #@dbus.service.method(dbus_interface='net.wm161.HomeSync.JobQueue')
  def Run(self):
    self.running.set()

class Job(threading.Thread):
  id = 0
  def __init__(self,call, args=[], kwargs={}):
    Job.id += 1
    self.prio = 0
    self.id = Job.id
    
    threading.Thread.__init__(self)
    self.call=call
    self.args=args
    self.kwargs=kwargs
    
    try:
      self.name = call.im_func.__name__
    except:
      self.name = call.__name__

  def setPriority(self,p):
    self.prio = p
    
  def __cmp__(self,other):
    if other.prio == self.prio:
      return 0
    if other.prio > self.prio:
      return -1
    return 1

  def __del__(self):
    Job.id-=1
  
  def __str__(self):
    return "#%i (%i) %s"%(self.id, self.prio, self.name)
    
  def run(self):
    self.call(*self.args,**self.kwargs)
    
class JobGroup(Job, JobQueue):
  def __init__(self):
    Job.__init__(self, self.runJobs)
    JobQueue.__init__(self)
    self.name=''

  def __str__(self):
    return Job.__str__(self)+str(map(str,self.queue))
  
  def runJobs(self):
    while self.haveJobs():
      self.processJobs()