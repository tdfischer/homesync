# -*- coding: utf-8 -*-
import threading
import logging
import time

class JobException(Exception):
  def __init__(self, status=-1, message=""):
    self.status = status
    self.message = message
    self.job = None
  
  def __str__(self):
    return "%s exited with non-zero status of %s (%s)" % (self.job, self.status, self.message)

class JobQueue(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.log = logging.getLogger('JobQueue')
    self.queue = []
    self.queueReady = threading.Condition(threading.Lock())
    self.running = threading.Event()
    self.running.set()
    self.active = None
  
  def enqueue(self,job):
    self.queueReady.acquire()

    self.queue.insert(0,job)
    self.queue = sorted(self.queue)
    #self.log.debug("Queued job %s", repr(job))
    #self.log.debug("Arguments: %s %s", job.args, job.kwargs)
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
      self.log.debug("Waiting for a new job")
      self.queueReady.wait()
    self.queue = sorted(self.queue)
    self.active = self.queue.pop()
    self.queueReady.release()
    self.log.info("Starting job %s",repr(self.active))
    self.active.start()
    self.active.join()
    self.log.info("Job complete: %s", repr(self.active))
    if (self.active.exception):
      self.log.error("Exception thrown in job. Passing up.")
      raise self.active.exception
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
  def __init__(self, call, args=[], kwargs={}):
    Job.id += 1
    self.prio = 0
    self.id = Job.id
    self.exception = None
    
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
    return self.name
  
  def __repr__(self):
    if (self.exception == None):
      status = "OK"
    else:
      status = "EXCEPTION"
    return "<ID:%i Priority:%i Status:%s Name:%s>"%(self.id, self.prio, status, self.name)
    
  def run(self):
    try:
      self.call(*self.args,**self.kwargs)
    except JobException, e:
      e.job = self
      self.exception = e
      raise e
    
class JobGroup(Job, JobQueue):
  def __init__(self):
    Job.__init__(self, self.runJobs)
    JobQueue.__init__(self)
    self.name="JobGroup"

  def __repr__(self):
    return Job.__repr__(self)+str(map(str,self.queue))
  
  def runJobs(self):
    while self.haveJobs():
      self.processJobs()