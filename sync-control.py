#!/usr/bin/env python
from PyQt4 import QtCore, QtGui
from Ui_MainWindow import Ui_MainWindow
import os, sys
from GitInterface import GitInterface

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
	def __init__(self):
		home = os.environ['HOME']
		self.git = GitInterface(home+"/.home-sync/git",home,home+"/.home-sync/ignore")
		
		QtGui.QMainWindow.__init__(self)
		self.setupUi(self)
		self.connect(self.actionBackup_Now,QtCore.SIGNAL('triggered()'), self.showSettings)
		return
		self.statusList = QtGui.QStandardItemModel(self)
		for file in self.git.files():
			self.statusList.append(file)
		self.revisionView.setModel(self.statusList)
	
	def showSettings(self):
		print "Yep!"

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	mw = MainWindow()
	mw.show()
	sys.exit(app.exec_())