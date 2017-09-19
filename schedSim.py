#!/usr/bin/python
# PyQT4 Interface for The Dynamic Scheduler
# Assumes Linux and Python 2.7.5
# Tyler Simon

import sys
import time 
import ctypes
import matplotlib.pyplot as plt
import numpy as np
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import subprocess
from subprocess import call


#We can put all C function in our library like this 
#libsched = ctypes.CDLL('./SchedSim.so')
#libsched.SchedSim.restype = ctypes.c_int
#libsched.SchedSim.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.c_int)

qtCreatorFile = "mainwindow.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
    	QtGui.QMainWindow.__init__(self)
       	Ui_MainWindow.__init__(self)
       	self.setupUi(self)
	self.setWindowIcon(QtGui.QIcon('Knight-white.ico'))
	self.commandLinkButton.clicked.connect(self.Calculate)

	# if someone clicks on the upper menu bar
        self.menuBar.triggered[QAction].connect(self.processtrigger)
	# set defaults
	self.listWidget_2.setCurrentRow(0)
	self.listWidget.setCurrentRow(0)

# process the menu bar items
    def processtrigger(self,msg):

	if msg.text() == "Save":
		file_save(self)
	elif msg.text() == "Quit":
		close_application(self)		
	elif msg.text() == "HowTo":
		howto()
	elif msg.text() == "Open":
		file_open(self)
		pass

# the main function
    def Calculate(self):
	jobs = self.lineEdit.text() # Number of jobs to simulate 300 is good
	syssize = self.lineEdit_2.text() # system Size
	mttf = self.lineEdit_3.text() #mttf
	
	# Checks to see if user selected a policy
	if self.listWidget.currentRow() < 0:
		showdialog_p()
	else:	
		schedule = self.listWidget.currentItem().text()

	
	# Lets get our fault model 
	if self.listWidget_2.currentRow() < 0:
		showdialog_f()
	else:	
		faultmodel = self.listWidget_2.currentItem().text()


	#  Let's check is we are permitting faults
	if self.checkBox_2.isChecked():
		allowfaults = "true" 
	else:
		allowfaults = "false" 
        
	# below will auto generate an input file or not
	if self.checkBox.isChecked():
		generate = "true" 
	else:
		generate = "false" 
        	file = open('input.txt','w')
        	#text = self.textEdit.toPlainText()
        	text = self.textBrowser_3.toPlainText()
        	file.write(text)
        	file.close()

	# execute the actual scheduler	
	p1 = subprocess.Popen(['./SchedSim', jobs,syssize,mttf, generate, schedule, allowfaults, faultmodel ])
	p1.wait();

	# now  put the files in place in the GUI
	file = open("summary.txt",'r')
	text = file.read()
	self.textBrowser_2.setText(text)

	
	file2 = open("SchedOutput.txt",'r')
	text2 = file2.read()
	self.textBrowser.setText(text2)

	file3 = open("input.txt",'r')
	text3 = file3.read()
	self.textBrowser_3.setText(text3)

    # Here's where the plotting starts     

	#plot the utilization and jobs 
	a, b, c, d, e = np.loadtxt('utilization.txt', delimiter=' ', unpack=True)
	mytitle = 'Jobs(' +jobs +') and System Utilization for ' + syssize +' nodes'

	fig = plt.figure(1)
	fig.canvas.set_window_title('Utilization and Number of Jobs')

	plt.subplot(2, 1, 1)
	plt.title(mytitle)
	plt.plot(a,d, label='Utilization ' + schedule)
	plt.xlabel('Time')
	plt.ylabel('Percentage of System Utilization')
	plt.legend().draggable()
	#plt.title('Jobs and System Utilization vs. Time')
	plt.grid(True)


	plt.subplot(2, 1, 2)
	plt.plot(a,e, label='Jobs ' + schedule)
	plt.xlabel('Time')
	plt.ylabel('Number of Jobs Running')
	plt.legend()
	plt.grid(True)
	plt.legend().draggable()

#	plt.savefig("test.png")
#	plt.show()
#	fig.canvas.draw()
	if allowfaults == 'true':
		mytitle2 = 'Probability of failure vs. time on ' + syssize +' nodes'
		y,z = np.loadtxt('failure.txt', delimiter=' ', unpack=True)
		fig2 = plt.figure(2)
		fig2.canvas.set_window_title('CDF vs. time')
		plt.title(mytitle2)
		plt.plot(y,z, label= faultmodel + ' model ' + mttf + '(h)')
		plt.xlabel('Time(seconds)')
		plt.ylabel('probability of failure (CDF)')
		plt.legend()
		plt.grid(True)
		plt.legend().draggable()
		fig2.canvas.draw()


	plt.show()
	fig.canvas.draw()



def howto():
   msg = QMessageBox()
   msg.setWindowTitle("How To Run the Simualator")
   msg.setIcon(QMessageBox.Information)
   msg.setText("1.) Click on a Schedule policy, " +'\n'+
   	       "2.) Open a workload file or autogenerate one, " +'\n'+
   	       "3.) Enter the number of jobs to simulate if you are autogenerating, " +'\n'+
	       "4.) Enter the system size and failure rate of the system then click Run!" +'\n\n'+
   	       "Note: You can save the \"results\" text from the menubar, File->Save" +'\n'+
   	       "Note: Mouse over the labels to get input advice." +'\n'+
   	       "Note: Select a new schedule and unselect the autogenerate box.")
		
   msg.setStandardButtons(QMessageBox.Ok)
   msg.buttonClicked.connect(msgbtn)
   retval = msg.exec_()

#if they don't click on a fault model
def showdialog_f():
   msg = QMessageBox()
   msg.setIcon(QMessageBox.Warning)
   msg.setText("Please select a Failure Mode")
   #msg.setInformativeText("This is additional information")
   msg.setWindowTitle("Warning")
   #msg.setDetailedText("The details are as follows:")
   msg.setStandardButtons(QMessageBox.Ok)
   retval= 1
   msg.buttonClicked.connect(msgbtn)
   retval = msg.exec_()

#if they don't click on a schedule policy
def showdialog_p():
   msg = QMessageBox()
   msg.setIcon(QMessageBox.Warning)
   msg.setText("Please select a Scheduler Policy")
  # msg.setInformativeText("This is additional information")
   msg.setWindowTitle("Warning")
 #  msg.setDetailedText("The details are as follows:")
   msg.setStandardButtons(QMessageBox.Ok)
   retval= 1
   msg.buttonClicked.connect(msgbtn)
   retval = msg.exec_()

def msgbtn(i):
   print "Button pressed is:",i.text()

def file_save(self):
        name = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        file = open(name,'w')
        #text = self.textEdit.toPlainText()
        text = self.textBrowser_2.toPlainText()
        file.write(text)
        file.close()

def file_open(self):
        name = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
        file = open(name,'r')

       # self.editor()

        with file:
            text = file.read()
            #self.textEdit.setText(text)
            self.textBrowser_3.setText(text)


#for the future 
def editor(self):
        self.textEdit = QtGui.QTextEdit()
        self.setCentralWidget(self.textEdit)


#shut er down
def close_application(self):
        choice = QtGui.QMessageBox.question(self, 'Close App',
                                            "Do you want to Quit?",
                   QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            sys.exit()
        else:
            pass

 

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    #QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
    QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('plastique'))
    window.show()
    sys.exit(app.exec_())
