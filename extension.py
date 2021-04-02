
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from  PyQt5.QtGui import QFont

class ExtensionView(QWidget):
	def __init__(self):
		super(ExtensionView, self).__init__()
		self.lbl = QLabel("No extension is installed. (Coming Soon)")
		self.lbl.setFont(QFont("Muli"))

		vbox = QVBoxLayout()
		vbox.addWidget(self.lbl, alignment=Qt.AlignCenter)

		self.setLayout(vbox)