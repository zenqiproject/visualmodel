

from PyQt5.QtWidgets import QWidget, QStackedWidget, QHBoxLayout, QStyledItemDelegate, \
	QStyle, QLabel, QVBoxLayout, QListWidget
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont
from UI import SeleniumUIButton, SeleniumUILineEdit
import os
from utils import readWindowSettings, createWindowSettings
import resources

class NoFocusDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.state = QStyle.State_None
        super(NoFocusDelegate, self).paint(painter, option, index)


class Settings(QWidget):
	def __init__(self):
		super(Settings, self).__init__()

		self.leftlist = QListWidget()
		self.leftlist.insertItem(0, 'General')
		self.leftlist.insertItem(1, 'Personal')
		self.leftlist.insertItem(2, 'About')
		self.leftlist.setFixedWidth(150 )
		self.leftlist.setSpacing(3)


		self.leftlist.setStyleSheet("""
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
			color: #fff;
			padding: 5px;
			background: transparent;
		}
		QListWidget::item:selected{
			color: #fff;
			background: transparent;
		}
		QListWidget::item:selected:active{
			background: transparent;
			color: #fff;
		}
		
		""")

		self.leftlist.setFont(QFont("Muli"))

		self.generalView = QWidget()
		self.aboutview = QWidget()
		self.personalView = QWidget()

		self.view = QStackedWidget(self)
		self.view.setStyleSheet("background: transparent;")
		self.view.addWidget(self.createGeneralView())
		self.view.addWidget(self.createPersonalView())
		self.view.addWidget(self.createAboutView())


		self.leftlist.setCurrentRow(0)

		hbox = QHBoxLayout(self)
		hbox.addWidget(self.leftlist)
		hbox.addWidget(self.view)

		self.setLayout(hbox)
		self.leftlist.currentItemChanged.connect(self.display)


	def createGeneralView(self):
		vbox = QVBoxLayout()

		defaultpathlayout = QHBoxLayout()

		datasetlbl = QLabel("Dataset Path")
		self.defaultdatasetpath = SeleniumUILineEdit(text=os.getcwd() + "\\checkpoint")
		self.defaultdatasetpath.setReadOnly(True)

		defaultbtn = SeleniumUIButton("DEFAULT")
		defaultbtn.clicked.connect(self.defaultdatasetpathconnect)

		datasetlbl.setFont(QFont("Muli"))

		defaultpathlayout.addWidget(self.defaultdatasetpath)
		defaultpathlayout.addWidget(defaultbtn)
		defaultpathlayout.setAlignment(Qt.AlignLeft)

		outputlbl = QLabel("Output Path")

		self.defaultoutputpathlayout = QHBoxLayout()
		self.defaultoutputpath = SeleniumUILineEdit(text=os.path.expanduser("~\\Documents\\Visual Model"))
		self.defaultoutputpath.setReadOnly(True)
		defaultoutputpathbtn = SeleniumUIButton("DEFAULT")
		defaultoutputpathbtn.clicked.connect(self.defaultoutputpathconnect)

		self.defaultoutputpathlayout.addWidget(self.defaultoutputpath)
		self.defaultoutputpathlayout.addWidget(defaultoutputpathbtn)
		self.defaultoutputpathlayout.setAlignment(Qt.AlignLeft)


		vbox.addWidget(datasetlbl)
		vbox.addLayout(defaultpathlayout)
		vbox.addWidget(outputlbl)
		vbox.addLayout(self.defaultoutputpathlayout)

		vbox.addStretch(0)

		self.generalView.setLayout(vbox)
		return self.generalView

	def defaultoutputpathconnect(self):
		self.defaultoutputpath.setText(os.path.expanduser("~\\Documents"))

	def defaultdatasetpathconnect(self):
		self.defaultdatasetpath.setText(os.getcwd()+"\\dataset")

	def createPersonalView(self):

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignTop)
		lbl = QLabel("Personal")
		layout.addWidget(lbl)
		self.personalView.setLayout(layout)
		return self.personalView

	def createAboutView(self):

		layout = QVBoxLayout()

		layout.setAlignment(Qt.AlignTop)
		version = QLabel("""Visual Model version 0.1

This software is build for creating image animation model powered by first order model.
It creates a image animation in a video input. Visual Model only supports VoxCeleb dataset 
use for creating deepfake animations
		""")
		version.setFont(QFont("Muli"))
		version.setStyleSheet("color: #fff;\nfont-size: 7.5px")

		developerlbl = QLabel("DEVELOPERS")
		developerlbl.setFont(QFont("Muli"))
		developerlbl.setStyleSheet("color: #fff;\nfont-size: 10px;\nfont-weight: bold;")


		urlLink = QLabel("<a href=\"https://github.com/AliaksandrSiarohin/first-order-model/graphs/contributors\" style=\"color: rgb(180,180,180);\">First order model developers</a>")
		urlLink.setFont(QFont("Muli"))
		urlLink.setOpenExternalLinks(True)

		developer = QLabel("<a href=\"http://www.github.com/zenqii\" style=\"color: rgb(180,180,180);\">Zenqi</a>")
		developer.setOpenExternalLinks(True)
		developer.setFont(QFont("Muli"))

		layout.addWidget(version)
		layout.addWidget(developerlbl)
		layout.addWidget(developer)
		layout.addWidget(urlLink)

		self.aboutview.setLayout(layout)

		return self.aboutview

	def writeWindowSettings(self):
		createWindowSettings("dataset_path", self.defaultdatasetpath.text())
		createWindowSettings("output_path", self.defaultoutputpath.text())


	def display(self):
		self.view.setCurrentIndex(self.leftlist.currentRow())