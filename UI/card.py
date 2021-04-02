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

from PyQt5.QtWidgets import QGroupBox, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QPoint
from PyQt5.QtGui import QColor

class MaterialCard(QGroupBox):
    clicked = pyqtSignal()
    def __init__(self, parent=None, shadow=True, background_color="rgb(20,20,20)", hover="rgb(118,118,118)"):
        super(MaterialCard, self).__init__(parent)
        self.background = background_color
        self.hover = hover
        self._is_shadow = shadow
        self.setStyleSheet(f"""
		QGroupBox{{
			background: {self.background};
			border: none;
		}}
		QGroupBox:hover{{
			background: {self.hover};
		}}
		""")
        self.setFixedSize(250, 200)

    @property
    def is_shadow(self):
        return self._is_shadow

    def enterEvent(self, event):
        if self.is_shadow:
            shadow_effect = QGraphicsDropShadowEffect(self)
            shadow_effect.setBlurRadius(5)
            shadow_effect.setOffset(QPoint(0, 0))
            shadow_effect.setColor(QColor(0, 0, 0))
            self.setGraphicsEffect(shadow_effect)

    def leaveEvent(self, event):
        if self.is_shadow:
            self.setGraphicsEffect(None)

    def mousePressEvent(self, event):
        self.clicked.emit()