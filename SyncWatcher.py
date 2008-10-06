from PyQt4 import QtCore
class SyncWatcher(QtCore.QFileSystemWatcher):
  def __init__(self):
    QtCore.QFileSystemWatcher.__init__(self)

  def add(self,path):
    self.addPath(path)
    qDir=QtCore.QDir(path)
    
    for subdir in qDir.entryList(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.NoSymLinks):
      self.addPath(path+"/"+subdir)
    for subdir in qDir.entryList(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.NoSymLinks):
      self.add(path+"/"+subdir)