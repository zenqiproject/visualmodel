

from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtGui import QFontDatabase, QFont
import resources

class TabControl(QTabWidget):
	def __init__(self, parent=None):
		super(TabControl, self).__init__(parent)
		self.setFont(QFont("Muli"))
		self.setStyleSheet("""
		QTabWidget::pane{
			border: 1px;
			background-color: transparent;
			
		} 
		QTabBar::tab {
			background-color: transparent;			
			font-size: 8pt;
			width: 70px;
			height: 50px;
		} 
		
		QTabBar::tab:hover{ color: #fff; }     
		QTabBar::tab:selected{ color: #fff; }
		""")
