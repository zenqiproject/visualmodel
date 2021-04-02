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

from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont


class IconLineEdit(QLineEdit):
    def __init__(self, parent=None, color=QColor(77, 153, 239), background=True, icon=""):
        super(IconLineEdit, self).__init__(parent)
        self.icon = icon
        self.color = color.name()
        self.hover = color.darker(115).name()
        self._color = QColor(207, 207, 207).name()

        self.isbackground = background

        if self.isbackground == True:
            self.background = QColor(71, 71, 71).name()
        elif self.isbackground == False:
            self.background = "transparent"

        self.create_style()

    def create_style(self):

        style = f"""
		QLineEdit {{
            background-color: transparent;
		    background-image: url({self.icon}); /* actual size, e.g. 16x16 */
			background-repeat: no-repeat;
			background-position: left;
			color: rgb(180, 180, 180);
			padding: 2 2 2 20; /* left padding (last number) must be more than the icon's width */
			font-size: 8pt;
			border: none;
			border-top-left-radius: 4px;
			border-top-right-radius: 4px;
			border-bottom: 2px solid {self._color};
			background-color: {self.background};
			selection-background-color: rgba(255, 255, 255, 1);
		}}
		QLineEdit:hover {{
			font-size: 8pt;
			border: none;
			border-top-left-radius: 4px;
			border-top-right-radius: 4px;
			border-bottom: 2px solid {self.color};
			background-color: {self.background};
			selection-background-color: rgba(255, 255, 255, 1);
		}}
		"""

        self.setStyleSheet(style)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.setStyleSheet(f"""
		QLineEdit {{
		    background-color: transparent;
		    background-image: url({self.icon}); /* actual size, e.g. 16x16 */
			background-repeat: no-repeat;
			background-position: left;
			color: rgb(180, 180, 180);
			padding: 2 2 2 20; /* left padding (last number) must be more than the icon's width */
			font-size: 8pt;
			border: none;
			border-top-left-radius: 4px;
			border-top-right-radius: 4px;
			border-bottom: 2px solid {self.color};
			background-color: {self.background};
			selection-background-color: rgba(255, 255, 255, 1);
		}}
		""")

    def focusOutEvent(self, event):
        super().focusInEvent(event)
        self.setStyleSheet(f"""		
		QLineEdit {{
		    background-color: transparent;
		    background-image: url({self.icon}); /* actual size, e.g. 16x16 */
			background-repeat: no-repeat;
			background-position: left;
			color: rgb(180, 180, 180);
			padding: 2 2 2 20; /* left padding (last number) must be more than the icon's width */
			font-size: 8pt;
			border: none;
			border-top-left-radius: 4px;
			border-top-right-radius: 4px;
			border-bottom: 2px solid {self._color};
			background-color: {self.background};
			selection-background-color: rgba(255, 255, 255, 1);
		}}
		""")


class LineEdit(QLineEdit):
    def __init__(self, parent=None, color=QColor(77, 153, 239), background=True):
        super(LineEdit, self).__init__(parent)
        self.color = color.name()
        self.hover = color.darker(115).name()
        self._color = QColor(207, 207, 207).name()

        self.isbackground = background

        if self.isbackground == True:
            self.background = QColor(71, 71, 71).name()
        elif self.isbackground == False:
            self.background = "transparent"

        self.create_style()

    def create_style(self):

        style = f"""
		QLineEdit {{
		    color: rgb(180, 180, 180);
			font-size: 8pt;
			border: none;
			border-top-left-radius: 4px;
			border-top-right-radius: 4px;
			border-bottom: 2px solid {self._color};
			background-color: {self.background};
			selection-background-color: rgba(255, 255, 255, 1);
		}}
		QLineEdit:hover {{
		    color: rgb(180, 180, 180);
			font-size: 8pt;
			border: none;
			border-top-left-radius: 4px;
			border-top-right-radius: 4px;
			border-bottom: 2px solid {self.color};
			background-color: {self.background};
			selection-background-color: rgba(255, 255, 255, 1);
		}}
		"""

        self.setStyleSheet(style)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.setStyleSheet(f"""
		QLineEdit {{
            color: rgb(180, 180, 180);
			font-size: 8pt;
			border: none;
			border-top-left-radius: 4px;
			border-top-right-radius: 4px;
			border-bottom: 2px solid {self.color};
			background-color: {self.background};
			selection-background-color: rgba(255, 255, 255, 1);
		}}
		""")

    def focusOutEvent(self, event):
        super().focusInEvent(event)
        self.setStyleSheet(f"""		
		QLineEdit {{
		    color: rgb(180, 180, 180);
			font-size: 8pt;
			border: none;
			border-top-left-radius: 4px;
			border-top-right-radius: 4px;
			border-bottom: 2px solid {self._color};
			background-color: {self.background};
			selection-background-color: rgba(255, 255, 255, 1);
		}}
		""")


class SeleniumUILineEdit(QLineEdit):
	def __init__(self, text, parent=None, font=None, width=None, height=None):
		super(SeleniumUILineEdit, self).__init__(parent=None)

		if font != None:
			self.setFont(font)

		self.setStyleSheet("""
		QLineEdit{
			background-color: rgb(20,20,20);
			color: palette(Text);
			border: none;
			padding: 5px;
		}
		QLineEdit::text{
			background-color: rgba(118,118,118, 0.5);
		}
		""")
		self.setText(text)
		if height != None and width != None:
			self.setFixedSize(width, height)