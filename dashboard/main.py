from PyQt5 import QtWidgets, QtCore
from dashboard import Ui_MainWindow
from threading import Thread
import time
import sys


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        # Initialize GUI
        self.dashboard = Ui_MainWindow()
        self.dashboard.initialize_gps()
        self.dashboard.setupUi(self)
    
    def closeEvent(self, event):
        self.dashboard.stop()

def main():
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
