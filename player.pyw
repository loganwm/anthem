import sys
from PyQt4 import QtGui
from PyQt4.phonon import Phonon

from window import PlayerWindow

def main():
	app = QtGui.QApplication(sys.argv);

	window2 = PlayerWindow()
	
	sys.exit(app.exec_())
	
if __name__ == '__main__':
	main()
