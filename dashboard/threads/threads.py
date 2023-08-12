from PyQt5.QtCore import pyqtSignal, QThread
from gpiozero import DistanceSensor
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QPixmap, QImage
from imutils.video import VideoStream
import cv2
import time

"""
The SensorThread class initializes a list of 6 ultrasonic sensor distances
and emits it as a signal.
"""
class SensorThread(QThread):
    def __init__(self):
        super().__init__()
        self.distances = [None] * 6

    #Create the signal
    SensorUpdate = pyqtSignal(list)

    def run(self):
        #Define 6 ultrasonic sensors on rpi gpio
        sensor1 = DistanceSensor(15, 14)
        sensor2 = DistanceSensor(24,23)
        sensor3 = DistanceSensor(20,16)
        sensor4 = DistanceSensor(27,17)
        sensor5 = DistanceSensor(6,5)
        sensor6 = DistanceSensor(19,13)
        self.ThreadActive = True

        while self.ThreadActive:
            #Set each rounded distances (converted to cm)
            self.distances[0] = round(sensor1.distance*100)
            self.distances[1] = round(sensor2.distance*100)
            self.distances[2] = round(sensor3.distance*100)
            self.distances[3] = round(sensor4.distance*100)
            self.distances[4] = round(sensor5.distance*100)
            self.distances[5] = round(sensor6.distance*100)
            #Emit the signal
            self.SensorUpdate.emit(self.distances)
    
    def get_distances(self):
        """
        Returns the distances so that it can be accessible in the buzzer thread.
        """
        return self.distances


"""
The VideoThread class creates the PiCamera VideoStream; it converts 
the PiCamera frame to a QImage to make it visible on the GUI.
"""
class VideoThread(QThread):
    def __init__(self):
        super().__init__()

    #Create the signal
    ImageUpdate = pyqtSignal(QImage)

    def run(self):
        self.ThreadActive = True
        usingPiCamera = True
        frameSize = (1024, 600)
        vs = VideoStream(src=0, usePiCamera=usingPiCamera, resolution=frameSize, framerate=32).start()
        time.sleep(2)
        while self.ThreadActive:     
            self.frame = vs.read()
            self.image = QtGui.QImage(self.frame.data, self.frame.shape[1], self.frame.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
            time.sleep(0.1)
            self.ImageUpdate.emit(self.image)
        cv2.destroyAllWindows()  
        vs.stop()

"""
The ClickableLabel class models an image that acts as a button.
E.g. Clicking an image has an action event.
"""
class ClickableLabel(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal(str)

    def __init__(self, path, parent, no_mask=False):
        super(ClickableLabel, self).__init__(parent)
        pixmap = QtGui.QPixmap(path)
        self.setPixmap(pixmap)
        if not no_mask:
            self.setMask(pixmap.mask())
    
    def update_image(self, path):
        pixmap = QtGui.QPixmap(path)
        self.setPixmap(pixmap)
        self.setMask(pixmap.mask())
    
    def mousePressEvent(self, event):
        self.clicked.emit(self.objectName())
