

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from UI import SeleniumUILineEdit
import os

class DatasetView(QWidget):
	def __init__(self):
		super(DatasetView, self).__init__()

		#vbox = QVBoxLayout()

		#for file in os.listdir("dataset"):
		#	vbox.addWidget(QLabel(file.split(".")[0]))

		#vbox.setAlignment(Qt.AlignTop)
		#self.setLayout(vbox)

		list = QListWidget(self)
		list.setStyleSheet("""
		QListWidget{
			background: transparent;
			border: none;
			font-size: 8pt;
			
		}
		
		QListView{
			outline: none;
		}
		QListWidget::item{
			background: transparent;
		}
		QListWidget::item:hover{
			padding: 5px;
			background: rgba(118,118,118,0.75);
		}
	
		""")

		for file in os.listdir(os.getcwd() + "\\checkpoint"):
			list.addItem(file.split(".")[0])

		vbox = QVBoxLayout()
		vbox.addWidget(list)
		self.setLayout(vbox)