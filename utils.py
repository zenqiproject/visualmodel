from PyQt5.QtCore import QSettings

def readWindowSettings(key):
	settings = QSettings("Visual Model", "Settings")
	value = settings.value(key, type=str)
	return value


def createWindowSettings(key, value):
	settings = QSettings("Visual Model", "Settings")
	print("adding %s with value of %s" %(key, value))
	settings.setValue(key, value)
