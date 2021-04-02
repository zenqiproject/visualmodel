
"""
                    Copyright (c) 2020 Zenqi
				This project was created by Flatipie.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from PyQt5.QtWidgets import (QApplication, QMainWindow, QDesktopWidget, QLabel, QDialog, \
                             QHBoxLayout, QVBoxLayout, QPushButton, QListView, QWidget, QFontDialog)

from PyQt5.QtGui import QColor, QFont, QIcon, QPainter
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal
from UI import TabControl, SeleniumUIButton
from model import ModelBase, MyModel
from extension import ExtensionView
from settings import Settings
from datasetview import DatasetView
import shutil
import requests
import os


class TranslucentWidgetSignals(QObject):
    # SIGNALS
    CLOSE = pyqtSignal()

class TranslucentWidget(QWidget):
    def __init__(self, parent=None):
        super(TranslucentWidget, self).__init__(parent)

        # make the window frameless
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.fillColor = QColor(20, 20, 20, 120)
        self.penColor = QColor("#333333")

        self.popup_fillColor = QColor(38, 38, 38)
        self.popup_penColor = QColor(38, 38, 38)

        self.close_btn = QPushButton(self)
        self.close_btn.setIcon(QIcon(":icon/close.png"))

        self.cancel = QPushButton("CANCEL", self)
        self.updatebtn = QPushButton("UPDATE", self)

        self.cancel.setFixedSize(70, 20)
        self.updatebtn.setFixedSize(70,20)

        self.setStyleSheet("""
		QPushButton{
			border-radius: 10px;
			background-color: transparent;
			border: 1px solid rgb(224, 224, 224);
			font-size: 7pt;
			letter-spacing: 10pt;
		}
		QPushButton:hover{
			background-color: rgb(118, 118, 118);
			border: none;
		}
		QPushButton:pressed{
			background-color: rgb(106, 106, 106);
			border: none;
		}
		""")

        r = requests.get("https://raw.githubusercontent.com/zenqii/visualmodel/main/version.json").json()
        version = r["version"]
        title = r["title"]

        self.updatelbl = QLabel(f"New version {version} is available!\n{title}", self)
        self.updatelbl.setFont(QFont("Muli"))
        self.close_btn.setStyleSheet("background-color: transparent;\nborder: none;")

        self.close_btn.setFixedSize(30, 30)
        self.cancel.clicked.connect(self._onclose)
        self.close_btn.clicked.connect(self._onclose)

        self.SIGNALS = TranslucentWidgetSignals()

    def resizeEvent(self, event):
        s = self.size()
        popup_width = 300
        popup_height = 120
        ow = int(s.width() / 2 - popup_width / 2)
        oh = int(s.height() / 2 - popup_height / 2)

        self.cancel.move(ow + 120, oh + 85)
        self.updatebtn.move(ow + 200, oh + 85)
        self.updatelbl.move(ow + 20, oh + 20)

        self.close_btn.move(ow + 265, oh + 5)
        tolw, tolh = 80, -5


    def paintEvent(self, event):
        # This method is, in practice, drawing the contents of
        # your window.

        # get current window size
        s = self.size()
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.setPen(self.penColor)
        qp.setBrush(self.fillColor)
        qp.drawRect(0, 0, s.width(), s.height())

        # drawpopup
        qp.setPen(self.popup_penColor)
        qp.setBrush(self.popup_fillColor)
        popup_width = 300
        popup_height = 120
        ow = int(s.width()/2-popup_width/2)
        oh = int(s.height()/2-popup_height/2)
        qp.drawRoundedRect(ow, oh, popup_width, popup_height, 5, 5)

        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        qp.setFont(font)
        qp.setPen(QColor(70, 70, 70))


        qp.end()

    def _onclose(self):
        print("Close")
        self.SIGNALS.CLOSE.emit()




class App(QMainWindow):
	is_queue_active = False
	def __init__(self):
		super(App, self).__init__()
		self.setContentsMargins(10,0,0,10)
		self.setWindowTitle("Visual Model")
		self.setFont(QFont("Open Sans"))
		# This specific code moves the window always in the middle of the screen

		self._popflag = False
		self._popframe = None

		self.move(0,0)
		self.setGeometry(0, 0, 800, 500)
		resolution = QDesktopWidget().screenGeometry()
		self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
			(resolution.height() / 2) - (self.frameSize().height() / 2))


		#self.setFixedSize(800, 550)

		self.modelbase = ModelBase()
		self.datasetview = DatasetView()
		self.settings = Settings()
		self.extensionview = ExtensionView()
		self.mymodel = MyModel()

		self.tab = TabControl(self)
		self.tab.addTab(self.mymodel, "My Models")
		self.tab.addTab(self.modelbase, "Model")
		self.tab.addTab(self.datasetview, "Dataset")
		self.tab.addTab(self.extensionview, "Extension")
		self.tab.addTab(self.settings, "Settings")

		self.tab.setCurrentIndex(1)

		self.setCentralWidget(self.tab)


		try:
			r = requests.get("https://raw.githubusercontent.com/zenqii/visualmodel/main/version.json").json()
			update = r["update"]


		except:

			update = False

		if update == True:
			self._onpopup()

	def closeEvent(self, event):
		print("Closing App")
		print("saving settings")
		self.settings.writeWindowSettings()

		tmpfolder = os.getcwd() + "\\tmp"
		if os.path.isdir(tmpfolder):
			print("Deleting temporary files")
			shutil.rmtree(tmpfolder)



	def resizeEvent(self, event):
		if self._popflag:
			self._popframe.move(0, 0)
			self._popframe.resize(self.width(), self.height())

	def _onpopup(self):
		self._popframe = TranslucentWidget(self)
		self._popframe.move(0, 0)
		self._popframe.resize(self.width(), self.height())
		self._popframe.SIGNALS.CLOSE.connect(self._closepopup)
		self._popflag = True
		self._popframe.show()

	def _closepopup(self):
		self._popframe.close()
		self._popflag = False