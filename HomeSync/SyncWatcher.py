from PyQt4 import QtCore
class SyncWatcher(QtCore.QFileSystemWatcher):
  def __init__(self):
    QtCore.QFileSystemWatcher.__init__(self)

  def add(self,path):
    self.addPath(path)
    qDir=QtCore.QDir(path)
    
    subdirs = qDir.entryList(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.NoSymLinks)
    for subdir in subdirs:
      self.addPath(path+"/"+subdir)
    
    for subdir in subdirs:
      self.add(path+"/"+subdir)