from PyQt5.QtCore import QObject, QSize, QPointF, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSlot, Qt
from PyQt5.QtGui import  QPainter, QPalette, QLinearGradient, QGradient, QColor
from PyQt5.QtWidgets import QAbstractButton, QWidget, QHBoxLayout, QLabel


class SwitchPrivate(QObject):
	def __init__(self, q, parent=None, isOn=False):
		self.isOn = isOn
		QObject.__init__(self, parent=parent)
		self.mPointer = q
		if self.isOn:
			self.mPosition = 1.0
		else:
			self.mPosition = 0.0

		self.mGradient = QLinearGradient()
		self.mGradient.setSpread(QGradient.PadSpread)

		self.animation = QPropertyAnimation(self)
		self.animation.setTargetObject(self)
		self.animation.setPropertyName(b'position')
		self.animation.setStartValue(0.0)
		self.animation.setEndValue(1.0)
		self.animation.setDuration(200)
		self.animation.setEasingCurve(QEasingCurve.InOutExpo)

		self.animation.finished.connect(self.mPointer.update)

	@pyqtProperty(float)
	def position(self):
		return self.mPosition

	@position.setter
	def position(self, value):
		self.mPosition = value
		self.mPointer.update()

	def draw(self, painter):
		r = self.mPointer.rect()
		margin = r.height()/10

		painter.setPen(Qt.NoPen)

		self.background_color = QColor(118, 118, 118)
		painter.setBrush(self.background_color)
		painter.drawRoundedRect(r, r.height()/2, r.height()/2)


		self.mGradient = QColor(35, 35, 35)

		painter.setBrush(self.mGradient)

		x = r.height()/2.0 + self.mPosition*(r.width()-r.height())
		painter.drawEllipse(QPointF(x, r.height()/2), r.height()/2-margin, r.height()/2-margin)

	@pyqtSlot(bool, name='animate')
	def animate(self, checked):
		self.animation.setDirection(QPropertyAnimation.Forward if checked else QPropertyAnimation.Backward)
		self.animation.start()


class ToggleSwitch(QAbstractButton):
	def __init__(self, parent=None, width=42, height=16, isOn=False):
		self.width = width
		self.height = height
		QAbstractButton.__init__(self, parent=parent)
		self.dPtr = SwitchPrivate(self, isOn=isOn)
		self.setCheckable(True)
		self.setChecked(True)
		self.clicked.connect(self.dPtr.animate)
		self.setFixedSize(self.width, self.height)

	#def sizeHint(self):
		#return QSize(self.width, self.height)

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.Antialiasing)
		self.dPtr.draw(painter)

	def resizeEvent(self, event):
		self.update()