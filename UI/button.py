"""
                    Copyright (c) 2020 Flatipie
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
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtGui import QIcon, QColor, QPainter, QBrush, QPen, QFont, QFontDatabase
from PyQt5.QtCore import Qt, QRect, QTimer, QPoint


class MaterialButton(QPushButton):

    def __init__(self, parent=None, string="", color=QColor(77, 153, 239), font_color=QColor("#fff")):
        super().__init__(parent)
        self.r = 0
        self.setText(string)



        self.color = color.name()
        self.hover = color.lighter(110).name()
        self.font_color = font_color.name()
        #print(self.hover)

        self.timer = QTimer(interval=25, timeout=self.set_radius)
        self.clicked.connect(self.timer.start)
        #self.setFont(QFont("Roboto"))
        self.setStyleSheet(f"""
        QPushButton {{
            border-radius: 3px;
            color: {self.font_color};
            font-size: 7pt;
            font-family: Open Sans;
            font-weight: bold;
            background-color: {self.color};
            padding: 20px;
            border: none;
        }}
        QPushButton:hover {{
            background-color: {self.hover};
        }}
        QPushButton:pressed {{
            color: #ddd;
        }}
        QPushButton:disabled{{
            background-color: rgb(44, 44, 44);
            color: rgb(122, 122, 122);
        }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(41, 41, 41))
        shadow.setOffset(QPoint(0, 0))
        self.setGraphicsEffect(shadow)

    def set_radius(self):
        if self.r < self.width() / 2:
            self.r += self.width() / 20
        else:
            self.timer.stop()
            self.r = 0
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.r:
            qp = QPainter(self)
            qp.setBrush(QColor(209, 209, 209, 125))
            qp.setPen(Qt.NoPen)
            qp.drawEllipse(self.rect().center(), self.r, self.r)


class Button(QPushButton):
    def __init__(self, parent=None, string="", color=QColor(77, 153, 239),
                 font_color=QColor("#fff"), outline=False, shadow=True):
        super(Button, self).__init__(parent)



        self.color = color
        self.hover = self.color.darker(105).name()
        self.font_color = font_color
        self.shadow_color = self.color.darker(115).name()
        self.outline = outline
        self.shadow = shadow

        self.create_style()

        self.setText(string)

    def create_style(self):

        if self.outline == True and self.shadow == False:
            style = f"""
            QPushButton {{
                color: {self.color.name()};
                font-size: 8;
                font-weight: bold;
                background-color: transparent;
                border: 2px solid {self.color.name()};

            }}
            QPushButton:hover{{
                color: {self.font_color.name()};
                font-weight: bold;
                font-size: 8;
                background-color: {self.color.name()};

            }}
            """


        elif self.outline == False and self.shadow == False:

            style = f"""
            QPushButton {{
                color: {self.font_color.name()};
                font-weight: bold;
                background-color: {self.color.name()};
                border: 2px solid {self.color.name()};
            }}
            QPushButton:hover {{
                color: {self.font_color.name()};
                font-size: 8;
                font-weight: bold;
                background-color: {self.hover};    
            }}
            """
        elif self.outline == False and self.shadow == True:
            pass
        style = f"""
            QPushButton {{
                color: {self.font_color.name()};
                font-size: 8;
                font-weight: bold;
                background-color: {self.color.name()};
                padding: 12px;
                border-radius: 4px;
                border-bottom: 4px solid {self.shadow_color};
            }}
            QPushButton:hover {{
                color: {self.font_color.name()};
                font-size: 8;
                font-weight: bold;
                background-color: {self.hover};                
            }}
            """

        self.setFixedSize(100, 40)
        self.setStyleSheet(style)


class SeleniumUIButton(QPushButton):
	def __init__(self, text, parent=None, width=90, height=20, icon=None):
		super(SeleniumUIButton, self).__init__(parent=None)
		QFontDatabase.addApplicationFont(":/font/Muli-Regular.ttf")
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
		text_with_spaces = " ".join(text)
		self.setFixedSize(width, height)
		self.setText(text_with_spaces)
		self.setFont(QFont("Muli"))
		if icon != None:
			self.setIcon(QIcon(icon))