import os
import logging
from threading import Semaphore

class GitInterface:
  FILES_MODIFIED = 1
  FILES_CACHED = 2
  FILES_DELETED = 4
  FILES_OTHER = 8
  FILES_IGNORED = 16
  FILES_STAGE = 32
  def __init__(self,gitDir,workTree):
    self.dir = gitDir
    self.work = workTree
    self.lock = Semaphore()
    
  def exists(self):
    return os.path.exists(self.dir)
  
  def open(self,args):
    logging.debug("Running \"git --git-dir=%s --work-tree=%s %s\""%(self.dir,self.work,args))
    return os.popen("git --git-dir=%s --work-tree=%s %s"%(self.dir,self.work,args))
  
  def init(self):
    self.lock.acquire()
    git = self.open("init")
    git.close()
    self.lock.release()
  
  def setConfig(self,name,value):
    git = self.open("config %s %s"%(name,value))
    git.close()
  
  def files(self,listType=FILES_MODIFIED):
    logging.debug("Listing...")
    flags = ""
    if (listType & GitInterface.FILES_MODIFIED):
      flags+="m"
    if (listType & GitInterface.FILES_CACHED):
      flags+="c"
    if (listType & GitInterface.FILES_DELETED):
      flags+="d"
    if (listType & GitInterface.FILES_OTHER):
      flags+="o"
    if (listType & GitInterface.FILES_IGNORED):
      flags+="i"
    if (listType & GitInterface.FILES_STAGE):
      flags+="s"
    if (flags==""):
      flags="m"
    git = self.open("ls-files -%s"%(flags))
    list = []
    while (True):
      file = git.readline().strip() #FIXME: Just trim the one newline
      if (file == ''):
        break
      logging.debug("File: %s"%(file))
      list.append(file)
    git.close()
    return list
  
  def add(self,file):
    self.lock.acquire()
    git = self.open("add -- %s"%(file))
    git.close()
    self.lock.release()
  
  def update(self,path):
    self.lock.acquire()
    git = self.open("add -u -- %s"%(path))
    git.close()
    self.lock.release()
  
  def commit(self, path, message):
    self.lock.acquire()
    logging.debug("Commiting %s",message)
    git = self.open("commit -m '%s' -- %s"%(message,path))
    git.close()
    self.lock.release()
  
  def revisionList(self, path):
    self.lock.acquire()
    logging.debug("Requesting revision history of %s",path)
    git = self.open("rev-list --timestamp HEAD %s"%(path))
    ret = []
    while(True):
      commit = git.readline().strip().split()
      if (commit == []):
        break
      commit[0] = int(commit[0])
      #ret.append(commit)
      ret.append([commit[1],commit[0]])
    git.close()
    self.lock.release()
    return ret
