from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import re

class Main(QWidget):
	def __init__(self):
		self.hours, self.minutes, self.seconds, self.miliseconds = 0, 0, 0, 0
		super().__init__()
		self.setFixedSize(400, 200)
		self.setWindowTitle("Simple SRT synchronizer")
		self.iniUI()
		self.path = ""
	def iniUI(self):
		layout = QGridLayout()
		self.pathText = QLabel(self)
		self.pathText.setText("")
		self.pathText.setFixedSize(300, 30)
		self.pathText.move(10, 20)
		self.pathText.setStyleSheet("background-color: white; border-style: outset; border-width: 1px; border-color: black" )
		self.browseButton = QPushButton(self)
		self.browseButton.setText("Browse")
		self.browseButton.setFixedSize(80, 30)
		self.browseButton.move(315, 20)
		self.browseButton.setStyleSheet("background-color: green")
		self.browseButton.clicked.connect(self.fileView)
		self.hourSpin = QSpinBox(self)
		self.hourSpin.setRange(0,60)
		self.hourSpin.move(10, 60)
		self.hourSpin.valueChanged.connect(self.hourChange)
		self.hourSpin.setSuffix("h")
		self.minuteSpin = QSpinBox(self)
		self.minuteSpin.setRange(0, 60)
		self.minuteSpin.move(70, 60)
		self.minuteSpin.valueChanged.connect(self.minuteChange)
		self.minuteSpin.setSuffix("m")
		self.secondSpin = QSpinBox(self)
		self.secondSpin.setRange(0, 60)
		self.secondSpin.move(135, 60)
		self.secondSpin.valueChanged.connect(self.secondChange)
		self.secondSpin.setSuffix("s")
		self.milisecondSpin = QSpinBox(self)
		self.milisecondSpin.setRange(0,1000)
		self.milisecondSpin.move(193, 60)
		self.milisecondSpin.valueChanged.connect(self.milisecondChange)
		self.milisecondSpin.setSuffix("ms")
		self.backwardCheck = QCheckBox("Backward", self)
		self.backwardCheck.move(10, 90)
		self.backwardCheck.stateChanged.connect(self.checkBackward)
		self.forwardCheck = QCheckBox("Forward", self)
		self.forwardCheck.move(120, 90)
		self.forwardCheck.stateChanged.connect(self.checkForward)
		self.synchButton = QPushButton(self)
		self.synchButton.move(10, 120)
		self.synchButton.clicked.connect(self.synchSRT)
		self.synchButton.setStyleSheet("background-color: red")
		self.synchButton.setText("Synchronize")
		self.errorLabel = QLabel(self)
		self.errorLabel.setStyleSheet("color: red")
		self.errorLabel.move(10, 160)
		self.errorLabel.setFixedSize(200, 30)
	def fileView(self):
		fileDialog = QFileDialog(self)
		fileDialog.setNameFilter("*.srt");
		fileDialog.setDirectory('')
		fileDialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
		fileDialog.setViewMode(QFileDialog.ViewMode.List)
		if fileDialog.exec():
			self.path = fileDialog.selectedFiles()
			self.path = self.path[0]
			self.pathText.setText(self.path) if len(self.path) < 30 else self.pathText.setText(self.path[0:11] + "..." + self.path[-20:])   
	def hourChange(self):
		self.hours = self.hourSpin.value()
	def minuteChange(self):
		self.minutes = self.minuteSpin.value()
	def secondChange(self):
		self.seconds = self.secondSpin.value()
	def milisecondChange(self):
		self.miliseconds = self.milisecondSpin.value()
	def checkBackward(self):
		if(self.forwardCheck.isChecked() and self.backwardCheck.isChecked()):
			self.forwardCheck.setChecked(0)
	def checkForward(self):
		if(self.forwardCheck.isChecked() and self.backwardCheck.isChecked()):
			self.backwardCheck.setChecked(0)
	def synchSRT(self):
		if(self.pathText.text() and (self.forwardCheck.isChecked() or self.backwardCheck.isChecked())):
			file = open(self.path, "r+")
			buffer = ""
			is_first = 1 #check, whether the iteration of time line is first so the program doesn't check if the user's input is out of range every time
			while(1):
				line = file.readline()
				if(not line):
					break
				if(re.match("[0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3} --> [0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3}", line)):
					if(is_first and self.backwardCheck.isChecked()):
						if((int(line[0:2]) * 3600000 + int(line[3:5]) * 60000 + int(line[6:8]) * 1000 + int(line[9:12])) < (int(self.hours) * 3600000 + int(self.minutes) * 60000 + int(self.seconds) * 1000 + int(self.miliseconds)) ):
							self.errorLabel.setText("Out of range")
							file.close()
							return
					time_from = timeObject(line[0:2], line[3:5], line[6:8], line[9:12])
					time_from.add(self.hours, self.minutes, self.seconds, self.miliseconds) if self.forwardCheck.isChecked() else time_from.substract(self.hours, self.minutes, self.seconds, self.miliseconds)
					time_from.convertToString()
					time_to = timeObject(line[17:19], line[20:22], line[23:25], line[26:29])
					time_to.add(self.hours, self.minutes, self.seconds, self.miliseconds) if self.forwardCheck.isChecked() else time_to.substract(self.hours, self.minutes, self.seconds, self.miliseconds)
					time_to.convertToString()
					time_listed = time_from.toList()
					time_listed.extend(time_to.toList())
					line = list(line)
					line[0:2], line[3:5], line[6:8], line[9:12], line[17:19], line[20:22], line[23:25], line[26:29] = time_listed[0], time_listed[1], time_listed[2], time_listed[3], time_listed[4], time_listed[5], time_listed[6], time_listed[7]  
					line = "".join(line)
					buffer = buffer + line
					is_first = 0
				else:
					buffer = buffer + line 
			file.truncate(0)
			file.write(buffer)		
			file.close()
			self.errorLabel.setText("Success!")


class timeObject:
	def __init__(self, h, m, s, ml):
		self.hours = int(h)
		self.minutes = int(m)
		self.seconds = int(s)
		self.miliseconds = int(ml)
	def add(self, h, m, s, ml):
		h, m, s, ml = int(h), int(m), int(s), int(ml)
		if(ml + self.miliseconds>=1000):
			self.seconds = self.seconds + 1
			self.miliseconds = ml + self.miliseconds - 1000
		else:
			self.miliseconds = ml + self.miliseconds
		if(s + self.seconds >= 60):
			self.minutes = self.minutes + 1
			self.seconds = s + self.seconds - 60
		else:
			self.seconds = s + self.seconds
		if(m + self.minutes> 60):
			self.hours = self.hours + 1
			self.minutes = self.minutes + m - 60
		else:
			self.minutes = self.minutes + m
		self.hours = self.hours + h
	def substract(self, h, m, s, ml):
		h, m, s, ml = int(h), int(m), int(s), int(ml)
		if(self.miliseconds - ml <0):
			self.seconds = self.seconds - 1
			self.miliseconds = 1000 + self.miliseconds - ml
		else:
			self.miliseconds = self.miliseconds - ml
		if(self.seconds - s < 0):
			self.minutes = self.minutes - 1
			self.seconds = self.seconds + 60 - s
		else: 
			self.seconds = self.seconds - s
		if(self.minutes - m < 0):
			self.hours = self.hours - 1
			self.minutes = self.minutes + 60 - m
		else:
			self.minutes = self.minutes - m
		self.hours = self.hours - h
	def convertToString(self):
		if(not isinstance(self.hours, str)):
			self.hours = str(self.hours) if self.hours > 9 else "0" + str(self.hours)
			self.minutes = str(self.minutes) if self.minutes > 9 else "0" + str(self.minutes)
			self.seconds = str(self.seconds) if self.seconds > 9 else "0" + str(self.seconds)
			self.miliseconds = str(self.miliseconds) if self.miliseconds > 99 else "0" + str(self.miliseconds) if self.miliseconds > 9 else "00" + str(self.miliseconds)
	def toList(self):
		return [self.hours, self.minutes, self.seconds, self.miliseconds]




instance = QApplication([])
window = Main()
window.show()
instance.exec_()