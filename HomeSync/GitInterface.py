# -*- coding: utf-8 -*-
from __future__ import with_statement

import os
import logging
from threading import Semaphore
import threading
from subprocess import *
import Jobs
import time

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

class GitCallback:
  def FilesAdded(self,files):
    pass
  
  def FilesCommitted(self,files):
    pass

class GitProcessException(Jobs.JobException):
  pass

class GitInterface:
  FILES_MODIFIED = 1
  FILES_CACHED = 2
  FILES_DELETED = 4
  FILES_OTHER = 8
  FILES_IGNORED = 16
  FILES_STAGE = 32

  def __init__(self,gitDir,workTree='', bare=False, callback=GitCallback()):
    self.dir = gitDir
    self.work = workTree
    self.lock = Semaphore()
    self.bare = bare
    self.log = logging.getLogger('GitInterface')
    self.callback = callback
  
  def exists(self):
    return os.path.exists(self.dir)
  
  def writeHead(self):
    with self.lock:
      git = self.open("update-ref","HEAD", self.head)
      ret = git.wait()
  
  def readHead(self):
    with self.lock:
      git = self.open("rev-parse", "HEAD",stdout=PIPE)
      try:
        git.wait()
      except GitProcessException:
        pass
      self.head = git.stdout.readline().strip()
      git.stdout.close()
      if self.head == "HEAD": #Returns the revision name for a bad name
         self.head = ""
  
  def open(self, *args, **kwargs):
    if ("stdout" in kwargs):
      stdout = kwargs["stdout"]
    else:
      stdout = None
    if ("stdin" in kwargs):
      stdin = kwargs["stdin"]
    else:
      stdin = None
    args = map(str,args)
    if self.bare:
      args = ["git","--git-dir=%s"%(self.dir),"--bare"]+args
    else:
      args = ["git","--git-dir=%s"%(self.dir),"--work-tree=%s"%(self.work)] + args
    self.log.debug("Running %s in %s"%(args, repr(threading.currentThread())))
    time.sleep(0.0001)
    proc = Popen(args, stdout=stdout, stdin=stdin)
    time.sleep(0.0001)
    def waitForGit(message="", fatal=True):
      ret = proc.popen_wait()
      if (ret != 0 and fatal):
        raise GitProcessException(ret, message)
      return ret
    
    proc.popen_wait = proc.wait
    proc.wait = waitForGit
    self.log.debug("Process started as PID %i", proc.pid)
    return proc
  
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
    with self.lock:
      git = self.open("config",name,str(value))
      git.wait()
  
  def files(self,listType=FILES_MODIFIED):
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
    git = self.open("ls-files","-"+flags, stdout=PIPE)
    list = []
    while (True):
      file = git.stdout.readline().strip() #FIXME: Just trim the one newline
      if (file == ''):
        break
      self.log.debug("File: %s"%(file))
      list.append(file)
    git.wait()
    return list

  def addToIndex(self,*files):
    with self.lock:
      git = self.open("update-index","--add","-z","--stdin", stdin=PIPE, stdout=PIPE)
      #i = 0
      for f in files:
          #i+=1
          git.stdin.write(f+"\0")
          #self.log.debug("Wrote %i/%i files: %s", i, len(files), f)
      git.stdin.close()
      self.callback.FilesAdded(files)
      git.wait()
      git.stdout.close()
      self.log.debug("Done")
  
  def commitIndex(self, message):
    self.log.debug("Commiting %s...",message)
    self.readHead()
    with self.lock:
      git = self.open("write-tree", stdout=PIPE)
      tree = git.stdout.readline().strip()
      git.wait()
      git.stdout.close()
      if self.head == "":
        git = self.open("commit-tree", tree, stdin=PIPE, stdout=PIPE)
      else:
        git = self.open("commit-tree",tree,"-p",self.head, stdin=PIPE, stdout=PIPE)
      git.stdin.write(message)
      git.stdin.close()
      git.wait()
      self.head = git.stdout.read().strip()
      git.stdout.close()
    self.writeHead()
    self.log.debug("Commited.")

  #def compact(self):
  #  self.lock.acquire()
  #  self.log.debug("Compressing git repo")
  #  git = self.open("gc","--aggressive")
  #  git.wait()
  #  self.lock.release()
  
  def revisionList(self, path):
    with self.lock:
      self.log.debug("Requesting revision history of %s",path)
      git = self.open("rev-list","--timestamp","HEAD",path, stdout=PIPE)
      ret = []
      while(True):
        commit = git.stdout.readline().strip().split()
        if (commit == []):
          break
        commit[0] = int(commit[0])
        ret.append([commit[1],commit[0]])
      git.wait()
      return ret