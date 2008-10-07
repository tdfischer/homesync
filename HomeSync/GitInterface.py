import os
import logging
from threading import Semaphore

#Creating a backup repo:
# mkdir /tmp/hs-test/
# git --git-dir=/tmp/hs-test --bare init
#Pushing to a backup repo:
# git --git-dir=/home/trever/.home-sync/git --work-tree=/home/trever push /tmp/hs-test --all
#Pulling from a backup:
# mkdir -p /tmp/hs-test2/.home-sync/git
# git --git-dir=/tmp/hs-test2/.home-sync/git --work-tree=/tmp/hs-test2 init
# git --git-dir=/tmp/hs-test2/.home-sync/git --work-tree=/tmp/hs-test2 pull /tmp/hs-test
#Pushing to a remote machine:
# git --git-dir=/home/trever/.home-sync/git --work-tree=/home/trever push localhost:/tmp/hs-test/.home-sync/git master
# on remote machine: git --git-dir=/tmp/hs-test/.home-sync/git --work-tree=/tmp/hs-test checkout master
#Pulling from a remote machine:
# cd /tmp/hs-test
# git --git-dir=/tmp/hs-test/.home-sync/git --work-tree=/tmp/hs-test pull localhost:/home/trever/.home-sync/git

class GitInterface:
  FILES_MODIFIED = 1
  FILES_CACHED = 2
  FILES_DELETED = 4
  FILES_OTHER = 8
  FILES_IGNORED = 16
  FILES_STAGE = 32

  def __init__(self,gitDir,workTree='',bare=False):
    self.dir = gitDir
    self.work = workTree
    self.lock = Semaphore()
    self.bare = bare
    
  def exists(self):
    return os.path.exists(self.dir)
  
  def open(self,args):
    if self.bare:
      logging.debug("Running \"git --git-dir=%s --bare %s\""%(self.dir,args))
      return os.popen("git --git-dir=%s --bare %s"%(self.dir,args))
    else:
      logging.debug("Running \"git --git-dir=%s --work-tree=%s %s\""%(self.dir,self.work,args))
      return os.popen("git --git-dir=%s --work-tree=%s %s"%(self.dir,self.work,args))
  
  def init(self):
    self.lock.acquire()
    git = self.open("init")
    git.close()
    self.lock.release()
  
  def push(self,url,branch="--all"):
    self.lock.acquire()
    git = self.open("push %s %s"%(url,branch))
    git.close()
    self.lock.release()
  
  def pull(self,url):
    self.lock.acquire()
    git = self.open("pull %s"%(url))
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
  
  def add(self,file,callback=0):
    if callback==0:
      callback=lambda x:x
    self.lock.acquire()
    git = self.open("add -v -- %s"%(file))
    while(True):
      file = git.readline().strip()
      if (file == ""):
        break
      callback(file)
    git.close()
    self.lock.release()
  
  def update(self,path):
    self.lock.acquire()
    git = self.open("add -u -- %s"%(path))
    git.close()
    self.lock.release()
  
  def commitAll(self, message):
    self.lock.acquire()
    logging.debug("Committing all changes: %s",message)
    git = self.open("commit -a -m '%s'"%(message))
    git.close()
    self.lock.release()
  
  def commit(self, message, path=''):
    self.lock.acquire()
    logging.debug("Commiting %s",message)
    git = self.open("commit -m '%s' -- %s"%(message,path))
    git.close()
    self.lock.release()

  def compact(self):
    self.lock.acquire()
    logging.debug("Compressing git repo")
    git = self.open("gc --aggressive")
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