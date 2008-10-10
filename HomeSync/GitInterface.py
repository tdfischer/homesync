from __future__ import with_statement

import os
import logging
from threading import Semaphore
from subprocess import *

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
    self.log = logging.getLogger('GitInterface')
    
  def exists(self):
    return os.path.exists(self.dir)
  
  def open(self,*args):
    args = map(str,args)
    if self.bare:
      args = ["git","--git-dir=%s"%(self.dir),"--bare"]+args
    else:
      args = ["git","--git-dir=%s"%(self.dir),"--work-tree=%s"%(self.work)] + args
    self.log.debug("Running %s"%(args))
    #return Popen(args, stdout=PIPE)
    return Popen(args)
  
  def init(self):
    with self.lock:
      git = self.open("init")
      git.wait()
  
  def push(self,url,branch="--all"):
    with self.lock:
      git = self.open("push",url,branch)
      git.wait()
  
  def pull(self,url):
    with self.lock:
      git = self.open("pull",url)
      git.wait()
  
  def setConfig(self,name,value):
    git = self.open("config",name,str(value))
  
  def files(self,listType=FILES_MODIFIED):
    self.log.debug("Listing...")
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
    git = self.open("ls-files","-"+flags)
    list = []
    while (True):
      file = git.stdout.readline().strip() #FIXME: Just trim the one newline
      if (file == ''):
        break
      self.log.debug("File: %s"%(file))
      list.append(file)
    git.wait()
    return list

  def add(self,*files):
    with self.lock:
      git = self.open("add","-v","--",*files)
      #while(True):
        #file = git.stdout.readline().strip().split()[1:]
        #if (file == []):
          #break
        #callback(''.join(file).strip("'"))
      git.wait()
  
  def update(self,path):
    with self.lock:
      git = self.open("add","-u","--",path)
      git.wait()
  
  def commitAll(self, message):
    self.log.debug("Committing all changes: %s",message)
    with self.lock:
      git = self.open("commit","-a","-m",message)
      #while (True):
        #line=git.stdout.readline().strip().split()[5:]
        #if line == []:
          #break
        #callback(''.join(line))
      git.wait()
      self.log.debug("Commited.")
  
  def commit(self, message, *files):
    self.log.debug("Commiting %s...",message)
    with self.lock:
      git = self.open("commit","-m",message,"--",*files)
      #while (True):
        #line=git.stdout.readline().strip().split()[5:]
        #if line == []:
          #break
        #callback(''.join(line.split()[5:]))
      self.log.debug("Commited.")

  def compact(self):
    self.lock.acquire()
    self.log.debug("Compressing git repo")
    git = self.open("gc","--aggressive")
    git.wait()
    self.lock.release()
  
  def revisionList(self, path):
    self.lock.acquire()
    self.log.debug("Requesting revision history of %s",path)
    git = self.open("rev-list","--timestamp","HEAD",path)
    ret = []
    while(True):
      commit = git.stdout.readline().strip().split()
      if (commit == []):
        break
      commit[0] = int(commit[0])
      #ret.append(commit)
      ret.append([commit[1],commit[0]])
    git.wait()
    self.lock.release()
    return ret