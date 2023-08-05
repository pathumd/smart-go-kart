# Import libraries
import csv
import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
import gpsd
from threading import Thread
import time
from datetime import datetime
import subprocess
from gpiozero import Buzzer
from statistics import mean
from mutagen.id3 import ID3
from mutagen import File
import Adafruit_DHT
import vlc
import random
import signal

# Import custom thread classes
from threads.threads import SensorThread, VideoThread, ClickableLabel

"""
The Ui_MainWindow class models the main GUI window.
"""


class Ui_MainWindow(object):

    ##### GENERAL FUNCTIONS #####
    def play_startup_sound(self):
        """
        Plays the startup sound for the GUI (Audi startup sound).
        """
        self.media_player = vlc.MediaPlayer()
        media = vlc.Media(f"{self.folder_path}/sounds/startup_chime.mp3")
        self.media_player.set_media(media)
        self.media_player.play()

    ##### SET UP FUNCTIONS #####
    def setupUi(self, MainWindow):
        """
        Initializes all the tabs (main dashboard, camera, media tab),
        and sets up the fonts to be used in the GUI.
        """
        # Set up signal (for CTRL+C exiting)
        signal.signal(signal.SIGINT, self.handler)
        # Keep reference to folder path
        self.folder_path = os.path.dirname(os.path.abspath(__file__))
        # Set up the fonts for the GUI
        self.setup_fonts()

        self.setup_window(MainWindow)
        # Perform initial setup of tabs
        self.setup_dashboard_tab(MainWindow)
        self.setup_camera_tab(MainWindow)
        self.setup_media_tab(MainWindow)
        self.initialize_ui(MainWindow)

        # Launch the GUI with Tab 1 selected
        self.tabWidget.setCurrentIndex(0)
        self.play_startup_sound()

    def setup_fonts(self):
        """
        Initializes all the necessary fonts for the GUI.
        (Font family: RIDGE)
        """
        # Setup font database
        QtGui.QFontDatabase.addApplicationFont("fonts/RIDGE-LIGHT-OBLIQUE.otf")
        QtGui.QFontDatabase.addApplicationFont("fonts/Ridge-Bold-Oblique.otf")

        self.light_30_font = QtGui.QFont("RIDGE-LIGHT-OBLIQUE", 30)
        self.bold_30_font = QtGui.QFont("Ridge-Bold-Oblique", 30)
        self.light_20_font = QtGui.QFont("RIDGE-LIGHT-OBLIQUE", 20)
        self.speed_font = QtGui.QFont("Ridge-Bold-Oblique", 120)

    def setup_window(self, MainWindow):
        """
        Initializes the main parent window for the GUI.
        """
        # Set up the main window
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 600)
        MainWindow.setMinimumSize(QtCore.QSize(1024, 600))
        MainWindow.setMaximumSize(QtCore.QSize(1024, 600))
        MainWindow.setTabletTracking(True)
        MainWindow.setStyleSheet("background-color: rgb(9, 8, 4);")

        # Set up the central widget (main container for the GUI)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Set up tab widget (will contain all the tabs)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(-10, -30, 1041, 631))
        self.tabWidget.setObjectName("tabWidget")

        # General setup
        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def setup_dashboard_tab(self, MainWindow):
        """
        Sets up the Tab #1: The main dashboard tab
        (contains info like the kart's speed, location, temperature, etc.)
        """
        self.mainDash = QtWidgets.QWidget()
        self.mainDash.setObjectName("mainDash")
        # Add the home tab to the tab widget
        self.tabWidget.addTab(self.mainDash, "")

        # Nav button #1: Home
        self.homeButton_1 = ClickableLabel(f"{self.folder_path}/graphics/home.jpg", self.mainDash)
        self.homeButton_1.setGeometry(100, 18, 40, 40)
        self.homeButton_1.clicked.connect(self.select_home_tab)

        # Nav button #2: Media
        self.musicButton_1 = ClickableLabel(f"{self.folder_path}/graphics/music.jpg", self.mainDash)
        self.musicButton_1.setGeometry(250, 18, 40, 40)
        self.musicButton_1.clicked.connect(self.select_media_tab)

        # Nav button #3: Camera
        self.cameraButton_1 = ClickableLabel(f"{self.folder_path}/graphics/camera.jpg", self.mainDash)
        self.cameraButton_1.setGeometry(750, 18, 40, 40)
        self.cameraButton_1.clicked.connect(self.select_camera_tab)

        # Nav button #4: Settings
        self.settingsButton_1 = ClickableLabel(f"{self.folder_path}/graphics/settings.jpg", self.mainDash)
        self.settingsButton_1.setGeometry(900, 18, 40, 40)
        self.settingsButton_1.clicked.connect(self.select_settings_tab)

        # Set up location header label ("LOCATION")
        self.locationLabel = QtWidgets.QLabel(self.mainDash)
        self.locationLabel.setGeometry(QtCore.QRect(80, 430, 231, 51))
        self.locationLabel.setFont(self.light_30_font)
        self.locationLabel.setStyleSheet("color:#464646;")
        self.locationLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.locationLabel.setObjectName("locationLabel")

        # Set up location value label (displays the location of the kart)
        self.locationValueLabel = QtWidgets.QLabel(self.mainDash)
        self.locationValueLabel.setGeometry(QtCore.QRect(10, 480, 371, 41))
        self.locationValueLabel.setFont(self.light_20_font)
        self.locationValueLabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.locationValueLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.locationValueLabel.setObjectName("locationValueLabel")

        # Set up outside temperature header label ("OUTSIDE TEMP")
        self.outTempLabel = QtWidgets.QLabel(self.mainDash)
        self.outTempLabel.setGeometry(QtCore.QRect(730, 430, 231, 51))
        self.outTempLabel.setFont(self.light_30_font)
        self.outTempLabel.setStyleSheet("color:#464646;")
        self.outTempLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.outTempLabel.setObjectName("outTempLabel")

        # Set up outside temperature value label (displays the outside temperature value)
        self.outTempValLabel = QtWidgets.QLabel(self.mainDash)
        self.outTempValLabel.setGeometry(QtCore.QRect(650, 480, 381, 41))
        self.outTempValLabel.setFont(self.light_20_font)
        self.outTempValLabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.outTempValLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.outTempValLabel.setObjectName("outTempValLabel")

        # Set up speed value label (displays the speed of the kart as an integer)
        self.speedLabel = QtWidgets.QLabel(self.mainDash)
        self.speedLabel.setGeometry(QtCore.QRect(390, 155, 251, 171))
        self.speedLabel.setFont(self.speed_font)
        self.speedLabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.speedLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.speedLabel.setObjectName("speedLabel")

        # Set up the circle for the speedometer
        self.speedCircle = QtWidgets.QFrame(self.mainDash)
        self.speedCircle.setGeometry(QtCore.QRect(360, 110, 311, 311))
        self.speedCircle.setStyleSheet("QFrame{\n"
                                       "    border: 5px solid rgb(1, 203, 238);\n"
                                       "    background-color: none;\n"
                                       "    border-radius: 150px;\n"
                                       "}")
        self.speedCircle.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.speedCircle.setFrameShadow(QtWidgets.QFrame.Raised)
        self.speedCircle.setObjectName("speedCircle")

        # Set up the km/h header label ("KMH/H")
        self.kmhLabel = QtWidgets.QLabel(self.mainDash)
        self.kmhLabel.setGeometry(QtCore.QRect(470, 300, 91, 51))
        self.kmhLabel.setFont(self.light_30_font)
        self.kmhLabel.setStyleSheet("color:white;")
        self.kmhLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.kmhLabel.setObjectName("kmhLabel")

        # Set up the time value label (displays the current time using RPI system clock)
        self.timeLabel = QtWidgets.QLabel(self.mainDash)
        self.timeLabel.setGeometry(QtCore.QRect(390, 0, 261, 71))
        self.timeLabel.setFont(self.light_30_font)
        self.timeLabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.timeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.timeLabel.setObjectName("timeLabel")

    def setup_camera_tab(self, MainWindow):
        """
        Sets up the Tab #2: The camera tab
        (displays the live camera feed as well as the status of the 6 ultrasonic sensors)
        """
        # Setting up Tab 2: Camera View
        self.cameraView = QtWidgets.QWidget()
        self.cameraView.setObjectName("cameraView")

        # self.cameraFrame = QtWidgets.QLabel(self.cameraView)
        # self.cameraFrame.setStyleSheet("background-color: lightgreen")
        # self.cameraFrame.setGeometry(QtCore.QRect(0, 0, 1024, 600))
        # self.cameraFrame.setObjectName("cameraFrame")

        self.bgLabel = QtWidgets.QLabel(MainWindow)
        self.bgLabel.setStyleSheet("background-color: lightgreen")
        self.bgLabel.setGeometry(QtCore.QRect(0, 0, 1024, 600))
        self.bgLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.bgLabel.setLineWidth(3)
        self.bgLabel.setText("")
        self.bgLabel.setObjectName("bgLabel")

        self.overlayLabel = QtWidgets.QLabel(MainWindow)
        self.overlayLabel.setGeometry(QtCore.QRect(0, 0, 1024, 600))
        self.overlayLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.overlayLabel.setLineWidth(3)
        self.overlayLabel.setText("")
        self.overlayLabel.setObjectName("overlayLabel")
        self.overlayLabel.setStyleSheet("background:transparent;")

        self.centerLabel = QtWidgets.QLabel(MainWindow)
        self.centerLabel.setGeometry(QtCore.QRect(822, 105, 122, 160))
        self.centerLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.centerLabel.setText("")
        self.centerLabel.setObjectName("centerLabel")
        self.centerLabel.setStyleSheet("background:transparent;")

        self.front_1a_Label = QtWidgets.QLabel(MainWindow)
        self.front_1a_Label.setGeometry(QtCore.QRect(819, 93, 44, 32))
        self.front_1a_Label.setText("")
        self.front_1a_Label.setObjectName("front_1a_Label")
        self.front_1a_Label.setStyleSheet("background:transparent;")

        self.front_1b_Label = QtWidgets.QLabel(MainWindow)
        self.front_1b_Label.setGeometry(QtCore.QRect(804, 72, 55, 43))
        self.front_1b_Label.setText("")
        self.front_1b_Label.setObjectName("front_1b_Label")
        self.front_1b_Label.setStyleSheet("background:transparent;")

        self.front_1c_Label = QtWidgets.QLabel(MainWindow)
        self.front_1c_Label.setGeometry(QtCore.QRect(789, 51, 65, 48))
        self.front_1c_Label.setText("")
        self.front_1c_Label.setObjectName("front_1c_Label")
        self.front_1c_Label.setStyleSheet("background:transparent;")

        self.front_1d_Label = QtWidgets.QLabel(MainWindow)
        self.front_1d_Label.setGeometry(QtCore.QRect(774, 30, 74, 54))
        self.front_1d_Label.setText("")
        self.front_1d_Label.setObjectName("front_1d_Label")
        self.front_1d_Label.setStyleSheet("background:transparent;")

        self.front_2a_Label = QtWidgets.QLabel(MainWindow)
        self.front_2a_Label.setGeometry(QtCore.QRect(860, 89, 46, 16))
        self.front_2a_Label.setText("")
        self.front_2a_Label.setObjectName("front_2a_Label")
        self.front_2a_Label.setStyleSheet("background:transparent;")

        self.front_2b_Label = QtWidgets.QLabel(MainWindow)
        self.front_2b_Label.setGeometry(QtCore.QRect(855, 68, 56, 23))
        self.front_2b_Label.setText("")
        self.front_2b_Label.setObjectName("front_2b_Label")
        self.front_2b_Label.setStyleSheet("background:transparent;")

        self.front_2c_Label = QtWidgets.QLabel(MainWindow)
        self.front_2c_Label.setGeometry(QtCore.QRect(849, 46, 67, 24))
        self.front_2c_Label.setText("")
        self.front_2c_Label.setObjectName("front_2c_Label")
        self.front_2c_Label.setStyleSheet("background:transparent;")

        self.front_2d_Label = QtWidgets.QLabel(MainWindow)
        self.front_2d_Label.setGeometry(QtCore.QRect(844, 25, 78, 24))
        self.front_2d_Label.setText("")
        self.front_2d_Label.setObjectName("front_2d_Label")
        self.front_2d_Label.setStyleSheet("background:transparent;")

        self.front_3a_Label = QtWidgets.QLabel(MainWindow)
        self.front_3a_Label.setGeometry(QtCore.QRect(903, 92, 44, 32))
        self.front_3a_Label.setText("")
        self.front_3a_Label.setObjectName("front_3a_Label")
        self.front_3a_Label.setStyleSheet("background:transparent;")

        self.front_3b_Label = QtWidgets.QLabel(MainWindow)
        self.front_3b_Label.setGeometry(QtCore.QRect(907, 72, 55, 43))
        self.front_3b_Label.setText("")
        self.front_3b_Label.setObjectName("front_3b_Label")
        self.front_3b_Label.setStyleSheet("background:transparent;")

        self.front_3c_Label = QtWidgets.QLabel(MainWindow)
        self.front_3c_Label.setGeometry(QtCore.QRect(912, 51, 65, 48))
        self.front_3c_Label.setText("")
        self.front_3c_Label.setObjectName("front_3c_Label")
        self.front_3c_Label.setStyleSheet("background:transparent;")

        self.front_3d_Label = QtWidgets.QLabel(MainWindow)
        self.front_3d_Label.setGeometry(QtCore.QRect(918, 30, 74, 54))
        self.front_3d_Label.setText("")
        self.front_3d_Label.setObjectName("front_3d_Label")
        self.front_3d_Label.setStyleSheet("background:transparent;")
        ##############################################################################
        self.back_1a_Label = QtWidgets.QLabel(MainWindow)
        self.back_1a_Label.setGeometry(QtCore.QRect(819, 93, 44, 32))
        self.back_1a_Label.setText("")
        self.back_1a_Label.setObjectName("back_1a_Label")
        self.back_1a_Label.setStyleSheet("background:transparent;")

        self.back_1b_Label = QtWidgets.QLabel(MainWindow)
        self.back_1b_Label.setGeometry(QtCore.QRect(804, 72, 55, 43))
        self.back_1b_Label.setText("")
        self.back_1b_Label.setObjectName("back_1b_Label")
        self.back_1b_Label.setStyleSheet("background:transparent;")

        self.back_1c_Label = QtWidgets.QLabel(MainWindow)
        self.back_1c_Label.setGeometry(QtCore.QRect(789, 51, 65, 48))
        self.back_1c_Label.setText("")
        self.back_1c_Label.setObjectName("back_1c_Label")
        self.back_1c_Label.setStyleSheet("background:transparent;")

        self.back_1d_Label = QtWidgets.QLabel(MainWindow)
        self.back_1d_Label.setGeometry(QtCore.QRect(774, 30, 74, 54))
        self.back_1d_Label.setText("")
        self.back_1d_Label.setObjectName("back_1d_Label")
        self.back_1d_Label.setStyleSheet("background:transparent;")

        self.back_2a_Label = QtWidgets.QLabel(MainWindow)
        self.back_2a_Label.setGeometry(QtCore.QRect(860, 89, 46, 16))
        self.back_2a_Label.setText("")
        self.back_2a_Label.setObjectName("back_2a_Label")
        self.back_2a_Label.setStyleSheet("background:transparent;")

        self.back_2b_Label = QtWidgets.QLabel(MainWindow)
        self.back_2b_Label.setGeometry(QtCore.QRect(855, 68, 56, 23))
        self.back_2b_Label.setText("")
        self.back_2b_Label.setObjectName("back_2b_Label")
        self.back_2b_Label.setStyleSheet("background:transparent;")

        self.back_2c_Label = QtWidgets.QLabel(MainWindow)
        self.back_2c_Label.setGeometry(QtCore.QRect(849, 46, 67, 24))
        self.back_2c_Label.setText("")
        self.back_2c_Label.setObjectName("back_2c_Label")
        self.back_2c_Label.setStyleSheet("background:transparent;")

        self.back_2d_Label = QtWidgets.QLabel(MainWindow)
        self.back_2d_Label.setGeometry(QtCore.QRect(844, 25, 78, 24))
        self.back_2d_Label.setText("")
        self.back_2d_Label.setObjectName("back_2d_Label")
        self.back_2d_Label.setStyleSheet("background:transparent;")

        self.back_3a_Label = QtWidgets.QLabel(MainWindow)
        self.back_3a_Label.setGeometry(QtCore.QRect(903, 92, 44, 32))
        self.back_3a_Label.setText("")
        self.back_3a_Label.setObjectName("back_3a_Label")
        self.back_3a_Label.setStyleSheet("background:transparent;")

        self.back_3b_Label = QtWidgets.QLabel(MainWindow)
        self.back_3b_Label.setGeometry(QtCore.QRect(907, 72, 55, 43))
        self.back_3b_Label.setText("")
        self.back_3b_Label.setObjectName("back_3b_Label")
        self.back_3b_Label.setStyleSheet("background:transparent;")

        self.back_3c_Label = QtWidgets.QLabel(MainWindow)
        self.back_3c_Label.setGeometry(QtCore.QRect(912, 51, 65, 48))
        self.back_3c_Label.setText("")
        self.back_3c_Label.setObjectName("back_3c_Label")
        self.back_3c_Label.setStyleSheet("background:transparent;")

        self.back_3d_Label = QtWidgets.QLabel(MainWindow)
        self.back_3d_Label.setGeometry(QtCore.QRect(918, 30, 74, 54))
        self.back_3d_Label.setText("")
        self.back_3d_Label.setObjectName("back_3d_Label")
        self.back_3d_Label.setStyleSheet("background:transparent;")

        self.overlay = QPixmap("graphics/parking_overlay.png")
        self.center = QPixmap("graphics/go_kart_center.png")
        self.front_1a_ON = QPixmap("graphics/front_1a_ON.png")
        self.front_1b_ON = QPixmap("graphics/front_1b_ON.png")
        self.front_1c_ON = QPixmap("graphics/front_1c_ON.png")
        self.front_1d_ON = QPixmap("graphics/front_1d_ON.png")

        self.front_1a_OFF = QPixmap("graphics/front_1a_OFF.png")
        self.front_1b_OFF = QPixmap("graphics/front_1b_OFF.png")
        self.front_1c_OFF = QPixmap("graphics/front_1c_OFF.png")
        self.front_1d_OFF = QPixmap("graphics/front_1d_OFF.png")

        self.front_2a_ON = QPixmap("graphics/front_2a_ON.png")
        self.front_2b_ON = QPixmap("graphics/front_2b_ON.png")
        self.front_2c_ON = QPixmap("graphics/front_2c_ON.png")
        self.front_2d_ON = QPixmap("graphics/front_2d_ON.png")

        self.front_2a_OFF = QPixmap("graphics/front_2a_OFF.png")
        self.front_2b_OFF = QPixmap("graphics/front_2b_OFF.png")
        self.front_2c_OFF = QPixmap("graphics/front_2c_OFF.png")
        self.front_2d_OFF = QPixmap("graphics/front_2d_OFF.png")

        self.front_3a_ON = QPixmap("graphics/front_3a_ON.png")
        self.front_3b_ON = QPixmap("graphics/front_3b_ON.png")
        self.front_3c_ON = QPixmap("graphics/front_3c_ON.png")
        self.front_3d_ON = QPixmap("graphics/front_3d_ON.png")

        self.front_3a_OFF = QPixmap("graphics/front_3a_OFF.png")
        self.front_3b_OFF = QPixmap("graphics/front_3b_OFF.png")
        self.front_3c_OFF = QPixmap("graphics/front_3c_OFF.png")
        self.front_3d_OFF = QPixmap("graphics/front_3d_OFF.png")

        self.back_1a_ON = QPixmap("graphics/back_1a_ON.png")
        self.back_1b_ON = QPixmap("graphics/back_1b_ON.png")
        self.back_1c_ON = QPixmap("graphics/back_1c_ON.png")
        self.back_1d_ON = QPixmap("graphics/back_1d_ON.png")

        self.back_1a_OFF = QPixmap("graphics/back_1a_OFF.png")
        self.back_1b_OFF = QPixmap("graphics/back_1b_OFF.png")
        self.back_1c_OFF = QPixmap("graphics/back_1c_OFF.png")
        self.back_1d_OFF = QPixmap("graphics/back_1d_OFF.png")

        self.back_2a_ON = QPixmap("graphics/back_2a_ON.png")
        self.back_2b_ON = QPixmap("graphics/back_2b_ON.png")
        self.back_2c_ON = QPixmap("graphics/back_2c_ON.png")
        self.back_2d_ON = QPixmap("graphics/back_2d_ON.png")

        self.back_2a_OFF = QPixmap("graphics/back_2a_OFF.png")
        self.back_2b_OFF = QPixmap("graphics/back_2b_OFF.png")
        self.back_2c_OFF = QPixmap("graphics/back_2c_OFF.png")
        self.back_2d_OFF = QPixmap("graphics/back_2d_OFF.png")

        self.back_3a_ON = QPixmap("graphics/back_3a_ON.png")
        self.back_3b_ON = QPixmap("graphics/back_3b_ON.png")
        self.back_3c_ON = QPixmap("graphics/back_3c_ON.png")
        self.back_3d_ON = QPixmap("graphics/back_3d_ON.png")

        self.back_3a_OFF = QPixmap("graphics/back_3a_OFF.png")
        self.back_3b_OFF = QPixmap("graphics/back_3b_OFF.png")
        self.back_3c_OFF = QPixmap("graphics/back_3c_OFF.png")
        self.back_3d_OFF = QPixmap("graphics/back_3d_OFF.png")

        self.overlayLabel.setPixmap(self.overlay)
        self.centerLabel.setPixmap(self.center)

        vboxTab1 = QtWidgets.QGridLayout()

        vboxTab1.addWidget(self.bgLabel)
        vboxTab1.addWidget(self.overlayLabel, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.centerLabel, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_1a_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_1b_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_1c_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_1d_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_2a_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_2b_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_2c_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_2d_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_3a_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_3b_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_3c_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_3d_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)

        vboxTab1.addWidget(self.back_1a_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.back_1b_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.back_1c_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.back_1d_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.back_2a_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.back_2b_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.back_2c_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.back_2d_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.back_3a_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.back_3b_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.back_3c_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.back_3d_Label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)

        self.cameraView.setLayout(vboxTab1)
        self.tabWidget.addTab(self.cameraView, "")

        self.min_dist = 2
        self.max_dist = 100
        self.dist_step_01 = self.min_dist + round((self.max_dist - self.min_dist) / 4 * 1)
        self.dist_step_02 = self.min_dist + round((self.max_dist - self.min_dist) / 4 * 2)  # 0.1425
        self.dist_step_03 = self.min_dist + round((self.max_dist - self.min_dist) / 4 * 3)
        self.dist_step_04 = self.min_dist + round((self.max_dist - self.min_dist) / 4 * 4)

        self.VideoThread = VideoThread()
        self.VideoThread.start()
        self.VideoThread.ImageUpdate.connect(self.ImageUpdateSlot)

        self.SensorThread = SensorThread()
        self.SensorThread.start()
        self.SensorThread.SensorUpdate.connect(self.SensorUpdateSlot)

    def ImageUpdateSlot(self, Image):
        self.bgLabel.setPixmap(QPixmap.fromImage(Image))

    def SensorUpdateSlot(self, distances):
        self.front_1a_Label.setPixmap(self.front_1a_ON if distances[0] < self.dist_step_01 else self.front_1a_OFF)
        self.front_1b_Label.setPixmap(self.front_1b_ON if distances[0] < self.dist_step_02 else self.front_1b_OFF)
        self.front_1c_Label.setPixmap(self.front_1c_ON if distances[0] < self.dist_step_03 else self.front_1c_OFF)
        self.front_1d_Label.setPixmap(self.front_1d_ON if distances[0] < self.dist_step_04 else self.front_1d_OFF)

        self.front_2a_Label.setPixmap(self.front_2a_ON if distances[1] < self.dist_step_01 else self.front_2a_OFF)
        self.front_2b_Label.setPixmap(self.front_2b_ON if distances[1] < self.dist_step_02 else self.front_2b_OFF)
        self.front_2c_Label.setPixmap(self.front_2c_ON if distances[1] < self.dist_step_03 else self.front_2c_OFF)
        self.front_2d_Label.setPixmap(self.front_2d_ON if distances[1] < self.dist_step_04 else self.front_2d_OFF)

        self.front_3a_Label.setPixmap(self.front_3a_ON if distances[2] < self.dist_step_01 else self.front_3a_OFF)
        self.front_3b_Label.setPixmap(self.front_3b_ON if distances[2] < self.dist_step_02 else self.front_3b_OFF)
        self.front_3c_Label.setPixmap(self.front_3c_ON if distances[2] < self.dist_step_03 else self.front_3c_OFF)
        self.front_3d_Label.setPixmap(self.front_3d_ON if distances[2] < self.dist_step_04 else self.front_3d_OFF)

        self.back_1a_Label.setPixmap(self.back_1a_ON if distances[3] < self.dist_step_01 else self.back_1a_OFF)
        self.back_1b_Label.setPixmap(self.back_1b_ON if distances[3] < self.dist_step_02 else self.back_1b_OFF)
        self.back_1c_Label.setPixmap(self.back_1c_ON if distances[3] < self.dist_step_03 else self.back_1c_OFF)
        self.back_1d_Label.setPixmap(self.back_1d_ON if distances[3] < self.dist_step_04 else self.back_1d_OFF)

        self.back_2a_Label.setPixmap(self.back_2a_ON if distances[4] < self.dist_step_01 else self.back_2a_OFF)
        self.back_2b_Label.setPixmap(self.back_2b_ON if distances[4] < self.dist_step_02 else self.back_2b_OFF)
        self.back_2c_Label.setPixmap(self.back_2c_ON if distances[4] < self.dist_step_03 else self.back_2c_OFF)
        self.back_2d_Label.setPixmap(self.back_2d_ON if distances[4] < self.dist_step_04 else self.back_2d_OFF)

        self.back_3a_Label.setPixmap(self.back_3a_ON if distances[5] < self.dist_step_01 else self.back_3a_OFF)
        self.back_3b_Label.setPixmap(self.back_3b_ON if distances[5] < self.dist_step_02 else self.back_3b_OFF)
        self.back_3c_Label.setPixmap(self.back_3c_ON if distances[5] < self.dist_step_03 else self.back_3c_OFF)
        self.back_3d_Label.setPixmap(self.back_3d_ON if distances[5] < self.dist_step_04 else self.back_3d_OFF)

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    '''
    @pyqtSlot(QtCore.QModelIndex)
    def update_image(self, cv_img):
        self.bgLabel.setPixmap(QPixmap.fromImage(cv_img))
    '''

    def setup_media_tab(self, MainWindow):
        """
        Sets up the Tab #1: The main dashboard tab
        (contains the controls to play, pause, previous, and skip tracks)
        """
        self.mediaTab = QtWidgets.QWidget()
        self.mediaTab.setObjectName("mediaTab")
        self.tabWidget.addTab(self.mediaTab, "")

        # Nav button #1: Home
        self.homeButton_2 = ClickableLabel(f"{self.folder_path}/graphics/home.jpg", self.mediaTab)
        self.homeButton_2.setGeometry(100, 18, 40, 40)
        self.homeButton_2.clicked.connect(self.select_home_tab)

        # Nav button #2: Media
        self.musicButton_2 = ClickableLabel(f"{self.folder_path}/graphics/music.jpg", self.mediaTab)
        self.musicButton_2.setGeometry(250, 18, 40, 40)
        self.musicButton_2.clicked.connect(self.select_media_tab)

        # Nav button #3: Camera
        self.cameraButton_2 = ClickableLabel(f"{self.folder_path}/graphics/camera.jpg", self.mediaTab)
        self.cameraButton_2.setGeometry(750, 18, 40, 40)
        self.cameraButton_2.clicked.connect(self.select_camera_tab)

        # Nav button #4: Settings
        self.settingsButton_2 = ClickableLabel(f"{self.folder_path}/graphics/settings.jpg", self.mediaTab)
        self.settingsButton_2.setGeometry(900, 18, 40, 40)
        self.settingsButton_2.clicked.connect(self.select_settings_tab)

        # Initialize label to display album cover
        self.albumCover = QtWidgets.QLabel(self.mediaTab)
        self.albumCover.setGeometry(QtCore.QRect(370, 60, 300, 300))
        self.albumCover.setText("")
        self.albumCover.setObjectName("albumCover")

        # Initialize label to display track name
        self.trackName = QtWidgets.QLabel(self.mediaTab)
        self.trackName.setGeometry(QtCore.QRect(120, 360, 800, 20))
        self.trackName.setAlignment(QtCore.Qt.AlignCenter)
        self.trackName.setObjectName("trackName")
        self.trackName.setText("Loading...")
        self.trackName.setFont(self.bold_30_font)
        self.trackName.setStyleSheet("color: #01CBEE")

        # Initialize label to display artist name
        self.artistName = QtWidgets.QLabel(self.mediaTab)
        self.artistName.setGeometry(QtCore.QRect(120, 400, 800, 20))
        self.artistName.setAlignment(QtCore.Qt.AlignCenter)
        self.artistName.setObjectName("artistName")
        self.artistName.setFont(self.light_20_font)
        self.artistName.setStyleSheet("color: white")

        # Initialize button to play/pause track
        self.playPauseButton = ClickableLabel(f"{self.folder_path}/graphics/pause.jpg", self.mediaTab)
        self.playPauseButton.setGeometry(472, 435, 96, 96)
        self.playPauseButton.clicked.connect(self.play_track)

        # Initialize button to go to previous track
        self.prevButton = ClickableLabel(f"{self.folder_path}/graphics/previous.jpg", self.mediaTab)
        self.prevButton.setGeometry(390, 455, 54, 54)
        self.prevButton.clicked.connect(self.prev_track)

        # Initialize button to go to next track
        self.nextButton = ClickableLabel(f"{self.folder_path}/graphics/skip.jpg", self.mediaTab)
        self.nextButton.setGeometry(600, 455, 54, 54)
        self.nextButton.clicked.connect(self.next_track)

        # Initialize label to display the current time (using RPI system clock)
        self.timeLabel_2 = QtWidgets.QLabel(self.mediaTab)
        self.timeLabel_2.setGeometry(QtCore.QRect(390, 0, 261, 71))
        self.timeLabel_2.setFont(self.light_30_font)
        self.timeLabel_2.setStyleSheet("color: rgb(255, 255, 255);")
        self.timeLabel_2.setAlignment(QtCore.Qt.AlignCenter)
        self.timeLabel_2.setObjectName("timeLabel_2")

        # Initialize media player
        # TODO: Consider making a class called MediaPlayer?

        self.song_list = os.listdir(f"{self.folder_path}/music")
        # Randomly shuffle order of music list
        random.shuffle(self.song_list)
        # Initialize flags for media player
        self.play_music = True
        self.previous_song = False
        self.next_song = False
        self.curr_song_index = 0
        self.song_index = 0
        self.stop_media_player = False

        # Start media player thread
        self.media_player_thread = Thread(target=self.run_media_player)
        self.media_player_thread.start()

    def initialize_ui(self, MainWindow):
        """
        Initializes the UI by setting default text to all the necessary elements,
        and starts all the data-related threads (e.g. speed, location, time, temperature, buzzer, etc.)
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Dashboard"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.mainDash), _translate("MainWindow", "Main Dash"))
        # self.cameraFrame.setText(_translate("MainWindow", "TextLabel"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.cameraView), _translate("MainWindow", "Camera View"))
        self.locationLabel.setText(_translate("MainWindow", "LOCATION"))
        self.outTempLabel.setText(_translate("MainWindow", "OUT TEMP"))
        self.kmhLabel.setText(_translate("MainWindow", "KMH"))
        self.outTempValLabel.setText(_translate("MainWindow", "+ 25 C"))

        # Start all data-related threads
        self._start_data_threads()

    def _start_data_threads(self):
        """
        Helper function to start all the data-related threads.
        Starts the following threads:
        - Speed thread (retrieves current speed from GPS sensor every 1 s)
        - Location thread (retrieves current location from GPS data every 10 s)
        - Time thread (retrieves current time from RPI system clock every 1 s)
        - Temp thread (retrieves outside temperature from temperature sensor every 1 s)
        - Buzzer thread (retrieves ultrasonic sensor distance data every 1 s)
        """
        # Initialize speed thread
        self.speed_thread = Thread(target=self.update_speed)
        self._initialize_gps()

        # Initialize location thread
        self.location_thread = Thread(target=self.update_location)
        self._initialize_location_csv()

        # Initialize time thread
        self.time_thread = Thread(target=self.update_time)

        # Initialize temperature thread
        self.temp_thread = Thread(target=self.update_temp)

        # Initialize buzzer thread
        self.buzzer_thread = Thread(target=self.update_buzzer)

        # Initialize flags to continuously poll within the threads
        self.update_speed_started = True
        self.update_location_started = True
        self.update_time_started = True
        self.update_temp_started = True
        self.update_buzzer_started = True

        # Start all the threads
        self.speed_thread.start()
        self.location_thread.start()
        self.time_thread.start()
        self.temp_thread.start()
        self.buzzer_thread.start()

    def _initialize_gps(self):
        """
        Initializes the GPS sensor so that receives data.
        """
        print("Initializing GPS...")
        # TODO: Check for GPS status
        subprocess.run(["systemctl", "enable", "gpsd.socket"])
        gpsd.connect()

    def _initialize_location_csv(self):
        """
        Initializes the CSV file containing suburb-latitude/longitude data pairs,
        which will be used to match the kart's current coordinates to a suburb.
        """
        print("Creating connection to location csv...")
        search_file = open('csv/canadacities.csv', 'r')
        self.location_reader = csv.reader(search_file, delimiter=',')
        self.location_dict = {}
        for city in self.location_reader:
            if city[0] != 'city':
                self.location_dict[city[0]] = (float(city[4]), float(city[5]))

    ##### MEDIA PLAYER FUNCTIONS #####
    def run_media_player(self):
        """
        Thread function that runs the media player in an endless loop.
        """
        # Create instance of VLC Media Player
        self.player = vlc.MediaPlayer()
        # Pause for 7.5 seconds (wait for GUI startup sound to finish playing)
        time.sleep(7.5)

        # Continuously play music until the thread should be stopped
        while not self.stop_media_player:
            # Check 1: Reached past last song
            if self.curr_song_index == len(self.song_list):
                self.curr_song_index = 0
            # Check 2: Went behind first song
            elif self.curr_song_index == -1:
                self.curr_song_index = len(self.song_list) - 1

            # print(f"Playing {self.song_list[self.curr_song_index]}")
            # Load the current track's data (album cover, track name, artist name, etc.)
            self.load_track_data(self.song_list[self.curr_song_index])
            # Set current song to be played
            media = vlc.Media(f"{self.folder_path}/music/{self.song_list[self.curr_song_index]}")
            self.player.set_media(media)
            self.player.play()
            # Wait for the song to play
            time.sleep(3)

            # Continuously poll play/pause, skip, and previous controls
            while not self.stop_media_player:
                # Check #1: Song is finished, move to next song
                if self.player.is_playing() != 1 and self.play_music:
                    self.curr_song_index += 1
                    break
                # Check #2: Song is still playing, and next button was pressed
                elif self.player.is_playing() and self.next_song:
                    self.curr_song_index += 1
                    self.next_song = False
                    break
                # Check #3: Song is still playing, and previous button was pressed
                elif self.player.is_playing() and self.previous_song:
                    self.curr_song_index -= 1
                    self.previous_song = False
                    break
                else:
                    # Song is still playing, so do nothing (sleep)
                    time.sleep(1)

    def load_track_data(self, song):
        """
        Loads the current track's data to the GUI, including the album cover,
        track name, and artist name.
        """
        # Get current track path
        track_path = f"{self.folder_path}/music/{song}"
        # print(f"Track path: {track_path}")

        # Get metadata from MP3 file
        mp3_file = File(track_path, easy=True)
        track_name = mp3_file.get('title')[0].replace("&", "and")
        artist_name = mp3_file.get('artist')[0].replace("&", "and")

        # Display the artist name and track name on the GUI
        self.artistName.setText(artist_name.replace("/", ", "))
        if len(track_name) < 25:
            self.trackName.setText(track_name)
        else:
            self.trackName.setText(f"{track_name[:25]}...")

        # Generate image from album cover metadata
        tags = ID3(track_path)
        album_cover = tags.getall("APIC")[0].data
        qImg = QtGui.QImage()
        qImg.loadFromData(album_cover)
        pixmap01 = QtGui.QPixmap.fromImage(qImg)
        pixmap_image = QtGui.QPixmap(pixmap01)
        scaled_res = QtCore.QSize(250, 250)
        pixmap_image = pixmap_image.scaled(scaled_res, aspectRatioMode=QtCore.Qt.KeepAspectRatio,
                                           transformMode=QtCore.Qt.SmoothTransformation)

        # Display the album cover on the GUI
        self.albumCover.setPixmap(pixmap_image)
        self.albumCover.setAlignment(QtCore.Qt.AlignCenter)

    def play_track(self):
        """
        Plays or pauses the current track.
        """
        # Check #1: The media player is currently playing
        if self.player.is_playing():
            # If so, this means media player needs to be paused
            self.play_music = False
            self.player.pause()
            self.playPauseButton.update_image(f"{self.folder_path}/graphics/play.jpg")
        else:
            # Otherwise, this means the media player needs to be resumed/played
            self.play_music = True
            self.player.play()
            self.playPauseButton.update_image(f"{self.folder_path}/graphics/pause.jpg")

    def prev_track(self):
        """
        Sets the flag to move to the previous track in the player.
        """
        self.previous_song = True

    def next_track(self):
        """
        Sets the flag to move to the next track in the player.
        """
        self.next_song = True

    ##### NAVIGATION MENU FUNCTIONS #####
    def select_home_tab(self):
        """
        Switches the GUI to the home tab (containing the speed, location, temp).
        """
        self.tabWidget.setCurrentIndex(0)

    def select_camera_tab(self):
        self.tabWidget.setCurrentIndex(1)

    def select_media_tab(self):
        """
        Switches the GUI to the media tab (for controlling music).
        """
        self.tabWidget.setCurrentIndex(2)

    def select_settings_tab(self):
        """
        Switches the GUI to the setting tab (to be implemented).
        """
        # TODO: Settings tab should be index 3 (should contain controls like turning on/off buzzer)
        self.tabWidget.setCurrentIndex(0)

    ##### FUNCTIONS TO GET DATA FROM SENSORS / SYSTEM #####
    def get_time(self):
        """
        Returns the current time from the RPI's system clock.
        """
        now = datetime.now()
        curr_time = time.strftime("%I:%M %p")
        return curr_time

    def get_temp(self):
        """
        Returns the current outside temperature from the temperature sensor.
        """
        # Get reference to temperature sensor
        DHT_SENSOR = Adafruit_DHT.DHT11
        DHT_PIN = 26

        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
        # print(f"Temperature is: {temperature}")
        # print(f"Humidity is: {humidity}")
        # Check if temperature data is valid
        if temperature is not None:
            return int(temperature)
        else:
            return 0

    def get_speed(self):
        """
        Returns the current speed of the kart by retrieving the current GPS packet
        from the GPS sensor.
        """
        # Get gps packet
        gps_packet = gpsd.get_current()
        # Extract speed
        speed_mph = float(gps_packet.hspeed)
        # Convert speed to int and kmh
        speed_kmh_int = int(speed_mph * 1.609344)
        # print(f"Current speed: {speed_kmh_int}")
        return speed_kmh_int

    def get_current_suburb(self):
        """
        Returns the closest suburb based on the kart's current
        latitude + longitude coordinates.
        """
        # Get gps packet
        gps_packet = gpsd.get_current()
        # Get latitude and longitude of kart
        lat = gps_packet.lat
        long = gps_packet.lon
        # print(f"My coordinates: {lat}, {long}")

        curr_match = 100.00
        matched_city = ""
        # Traverse through each entry in the database, and save which city/suburb
        # has the lowest difference.
        for city in self.location_dict:
            # Get city's latitude and longitude
            city_lat = self.location_dict[city][0]
            city_long = self.location_dict[city][1]
            # Calculate difference between city's coordinates and kart's coordinates
            lat_diff = abs(lat) - abs(city_lat)
            long_diff = abs(long) - abs(city_long)
            calc_match = abs(lat_diff) + abs(long_diff)
            # Save the city as the current match if its difference is lower than
            # the previously saved city
            if calc_match < curr_match:
                curr_match = calc_match
                matched_city = str(city)
        # print(f"Matched city: {matched_city}")
        return matched_city

    ##### THREAD FUNCTIONS TO UPDATE DATA FOR GUI #####
    def update_speed(self):
        """
        Retrieves the kart's current speed every second and
        updates the GUI.
        """
        while self.update_speed_started:
            # Set current speed
            self.speedLabel.setText(str(self.get_speed()))
            time.sleep(1)

    def update_location(self):
        """
        Retrieves the kart's current location every 5 seconds and
        updates the GUI.
        """
        while self.update_location_started:
            # Set current suburb
            self.locationValueLabel.setText(self.get_current_suburb())
            time.sleep(5)

    def update_temp(self):
        """
        Retrieves the current temperature every 10 seconds and
        updates the GUI.
        """
        while self.update_temp_started:
            # Set current temp
            self.outTempValLabel.setText(f"{self.get_temp()} C")
            time.sleep(10)

    def update_time(self):
        """
        Retrieves the current time from the RPI system clock and
        updates the GUI.
        """
        while self.update_time_started:
            # Set current time
            curr_time = self.get_time()
            self.timeLabel.setText(curr_time)
            self.timeLabel_2.setText(curr_time)
            time.sleep(1)

    def update_buzzer(self):
        """
        Retrieves the distances from the 6 ultrasonic sensors every 0.0001 seconds
        and buzzes at the appropriate frequency.
        """
        buz = Buzzer(21)
        while self.update_buzzer_started:
            distances = self.SensorThread.get_distances()
            time.sleep(0.001)
            if all(distance is not None for distance in distances):
                distance_avg = mean(distances) / 110
                # print(f"Distance is {distance_avg}")
                buz.on()
                time.sleep(distance_avg)
                buz.off()
                time.sleep(distance_avg)

    ##### FUNCTIONS TO HANDLE EXITING #####
    def handler(self, signum, frame):
        """
        Catches the CTRL+C signal and stops all threads to
        cleanly exit the GUI.
        """
        self.stop()

    def stop(self):
        """
        Sets each thread's flag and joins all threads to
        cleanly exit the GUI.
        """
        print("Exiting...")
        # Set the thread flags
        self.update_location_started = False
        self.update_speed_started = False
        self.update_time_started = False
        self.update_temp_started = False
        self.update_buzzer_started = False
        self.stop_media_player = True

        # Join all threads
        self.speed_thread.join()
        print("Speed thread stopped.")
        self.time_thread.join()
        print("Time thread stopped.")
        self.location_thread.join()
        print("Location thread stopped.")
        self.temp_thread.join()
        print("Temp thread stopped.")
        self.media_player_thread.join()
        print("Media thread stopped.")
        self.buzzer_thread.join()
        print("Buzzer thread stopped.")

        # Exit the application
        sys.exit(0)
