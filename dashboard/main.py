from PyQt5 import QtWidgets, QtCore
from dashboard import Ui_MainWindow
from threading import Thread
import time
import sys

"""
The MainWindow class models a container to create an instance of the 
GUI.
"""


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        # Initialize GUI
        self.dashboard = Ui_MainWindow()
        # self.dashboard.initialize_gps()
        self.dashboard.setupUi(self)

    def closeEvent(self, event):
        """
        Catches the 'X' signal (close) and stops all active
        threads to cleanly exit the GUI.
        """
        self.dashboard.stop()


def main():
    """
    Creates an instance of the GUI and shows the window.
    """
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

# Main script
if __name__ == '__main__':
    main()
