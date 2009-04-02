# -*- coding: utf-8 -*-
from GitInterface import GitInterface, GitCallback
from Jobs import JobQueue, Job, JobGroup
import logging
import os
from fnmatch import fnmatch
#from git import *

DEFAULT_IGNORES=[
  "/.home-sync",
  "/.local/share/Trash",
  "/.macromedia/Flash_Player",
  "*~",
  ".svn",
  "/.Xauthority",
  "/.DCOPserver*",
  "/.xsession-errors*",
  "*.iso",
  "*.tar.*",
  "*.tar",
  "/.*/*cache*",
  "/.*/*Cache*"
]

class SyncArchive:
  def __init__(self, path, backup=False, gitHandler=None):
    self.backup = backup
    self.path = path
    if gitHandler == None:
      gitHandler=GitCallback()
    self.handler = gitHandler
    
    if backup:
      bare = True
      workTree = ''
      self.gitDir = path
    else:
      bare = False
      workTree = path
      self.syncDir=path+"/.home-sync"

    self.git = GitInterface(self.syncDir+"/git", workTree, bare)
    self.jobs = JobQueue()
    self.log = logging.getLogger('SyncArchive')
    self.jobs.log = logging.getLogger('SyncArchive.Jobs')
    self.jobs.start()
    
    self.commits = 0
  
  def ignoreList(self):
    return DEFAULT_IGNORES
    
  def isIgnored(self, file):
    file = file.lstrip(self.path)
    for pattern in self.ignoreList():
      if fnmatch(file, "*/"+pattern):
        return True
    return False
  
  def create(self):
    if self.backup:
      if os.path.exists(self.syncDir+"index"):
        self.log.debug("%s already exists, skipping creation.",self.syncDir)
        return False
      else:
        self.log.info("Creating new SyncArchive backup in %s"%(self.syncDir))
        initJob = JobGroup()
        initJob.enqueue( Job(self.git.init) )
        initJob.enqueue( Job(self.git.setConfig, args=("core.compression", -1)) )
    else:
      if os.path.exists(self.syncDir):
        self.log.debug("%s already exists, skipping creation.",self.syncDir)
        return False
      else:
        os.mkdir(self.syncDir)
        self.log.info("Creating new SyncArchive in %s"%(self.syncDir))
        initJob = JobGroup()
        initJob.enqueue( Job(self.git.init) )
        initJob.enqueue( Job(self.git.setConfig, args=("core.excludesfile", self.syncDir+"/ignore")) )
        initJob.enqueue( Job(self.git.setConfig, args=("core.compression", -1)) )
        initJob.setPriority(10)
        ignoreFile = open(self.syncDir+"/ignore","w")
        ignoreFile.writelines(map(lambda x:x+"\n",DEFAULT_IGNORES))
        ignoreFile.close()
    self.jobs.enqueue(initJob)
  
  def addFiles(self, *files):
    self.commits+=1
    j = JobGroup()
    j.enqueue( Job(self.git.addToIndex, args=files) )
    j.enqueue( Job(self.git.commitIndex, args=("%i files added"%(len(files)),)) )
    if self.commits>100:
      #j.enqueue( Job(self.git.compact) ) #Make sure we compact after we commit and add
      self.commits=0
    self.jobs.enqueue(j)
    return j
  
  #def updateFile(self, path):
    #j = Job(self.git.commit,args=(path))
    #self.jobs.enqueue(j)
    #return j
  
  def listFiles(self, type):
    return self.git.files(type)
  
  def pauseJobs(self):
    self.jobs.Pause()
  
  def resumeJobs(self):
    self.jobs.Resume()