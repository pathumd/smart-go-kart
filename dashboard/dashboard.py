import cv2
import csv
import os
from gpiozero.pins.pigpio import PiGPIOPin
from imutils.video import VideoStream
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
from PyQt5.QtGui import QPixmap, QImage
import gpsd
from threading import Thread
import time
from datetime import datetime
import subprocess
from gpiozero import DistanceSensor 
from time import sleep
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen import File
from PIL import Image
from io import BytesIO
import vlc
import random


class SensorThread(QThread):
    SensorUpdate = pyqtSignal(float)
    
    def run(self):
        sensor = DistanceSensor(24, 23)

        self.ThreadActive = True

        while self.ThreadActive:
            total_distance = round(sensor.distance*100)
            self.SensorUpdate.emit(total_distance)

class VideoThread(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def run(self):
        self.ThreadActive = True
        usingPiCamera = True
        frameSize = (1024, 600)
        vs = VideoStream(src=0, usePiCamera=usingPiCamera, resolution=frameSize, framerate=32).start()
        time.sleep(0.5)
        while self.ThreadActive:     
            self.frame = vs.read()  
            self.image = QtGui.QImage(self.frame.data, self.frame.shape[1], self.frame.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
            time.sleep(0.1)
            self.ImageUpdate.emit(self.image)
        cv2.destroyAllWindows()  
        vs.stop()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        
        self.folder_path = os.path.dirname(os.path.abspath(__file__))

        self.setup_fonts()

        self.setup_window(MainWindow)

        self.setup_dashboard_tab(MainWindow)
        
        self.setup_camera_tab(MainWindow)

        self.setup_media_tab(MainWindow)

        self.initialize_ui(MainWindow)

        # Launch the GUI with Tab 1 selected
        self.tabWidget.setCurrentIndex(2)
        self.play_startup_sound()

    def setup_fonts(self):
        # Setup font database
        QtGui.QFontDatabase.addApplicationFont("fonts/RIDGE-LIGHT-OBLIQUE.otf")
        QtGui.QFontDatabase.addApplicationFont("fonts/Ridge-Bold-Oblique.otf")
        
        self.light_30_font = QtGui.QFont("RIDGE-LIGHT-OBLIQUE", 30)
        self.bold_30_font = QtGui.QFont("Ridge-Bold-Oblique", 30)
        self.light_20_font = QtGui.QFont("RIDGE-LIGHT-OBLIQUE", 20)
        self.speed_font = QtGui.QFont("Ridge-Bold-Oblique", 120)
        
    def setup_window(self, MainWindow):
        # Set up the main window
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 600)
        MainWindow.setMinimumSize(QtCore.QSize(1024, 600))
        MainWindow.setMaximumSize(QtCore.QSize(1024, 600))
        MainWindow.setTabletTracking(True)
        MainWindow.setStyleSheet("background-color: rgb(9, 8, 4);")

        # Set up the central widget (main container)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Set up tab widget
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(-10, -30, 1041, 631))
        self.tabWidget.setObjectName("tabWidget")

        # General setup
        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def setup_dashboard_tab(self, MainWindow):
        # Setting up Tab 1: Main dashboard
        self.mainDash = QtWidgets.QWidget()
        self.mainDash.setObjectName("mainDash")
        self.tabWidget.addTab(self.mainDash, "")

        # Location label
        self.locationLabel = QtWidgets.QLabel(self.mainDash)
        self.locationLabel.setGeometry(QtCore.QRect(80, 430, 231, 51))
        self.locationLabel.setFont(self.light_30_font)
        self.locationLabel.setStyleSheet("color:#464646;")
        self.locationLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.locationLabel.setObjectName("locationLabel")

        self.locationValueLabel = QtWidgets.QLabel(self.mainDash)
        self.locationValueLabel.setGeometry(QtCore.QRect(10, 480, 371, 41))
        self.locationValueLabel.setFont(self.light_20_font)
        self.locationValueLabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.locationValueLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.locationValueLabel.setObjectName("locationValueLabel")
        
        # Outside temperature label
        self.outTempLabel = QtWidgets.QLabel(self.mainDash)
        self.outTempLabel.setGeometry(QtCore.QRect(730, 430, 231, 51))
        self.outTempLabel.setFont(self.light_30_font)
        self.outTempLabel.setStyleSheet("color:#464646;")
        self.outTempLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.outTempLabel.setObjectName("outTempLabel")

        self.outTempValLabel = QtWidgets.QLabel(self.mainDash)
        self.outTempValLabel.setGeometry(QtCore.QRect(650, 480, 381, 41))
        self.outTempValLabel.setFont(self.light_20_font)
        self.outTempValLabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.outTempValLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.outTempValLabel.setObjectName("outTempValLabel")

        # Speedometer
        self.speedLabel = QtWidgets.QLabel(self.mainDash)
        self.speedLabel.setGeometry(QtCore.QRect(390, 155, 251, 171))
        self.speedLabel.setFont(self.speed_font)
        self.speedLabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.speedLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.speedLabel.setObjectName("speedLabel")
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
        self.kmhLabel = QtWidgets.QLabel(self.mainDash)
        self.kmhLabel.setGeometry(QtCore.QRect(470, 300, 91, 51))
        self.kmhLabel.setFont(self.light_30_font)
        self.kmhLabel.setStyleSheet("color:white;")
        self.kmhLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.kmhLabel.setObjectName("kmhLabel")
        self.timeLabel = QtWidgets.QLabel(self.mainDash)
        self.timeLabel.setGeometry(QtCore.QRect(390, 0, 261, 71))
        
        # Time label
        self.timeLabel.setFont(self.light_30_font)
        self.timeLabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.timeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.timeLabel.setObjectName("timeLabel")


    def setup_camera_tab(self, MainWindow):
        # Setting up Tab 2: Camera View
        self.cameraView = QtWidgets.QWidget()
        self.cameraView.setObjectName("cameraView")

        #self.cameraFrame = QtWidgets.QLabel(self.cameraView)
        #self.cameraFrame.setStyleSheet("background-color: lightgreen")
        #self.cameraFrame.setGeometry(QtCore.QRect(0, 0, 1024, 600))
        #self.cameraFrame.setObjectName("cameraFrame")

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



        self.overlayLabel.setPixmap(self.overlay)
        self.centerLabel.setPixmap(self.center)



        vboxTab1 = QtWidgets.QGridLayout()

        vboxTab1.addWidget(self.bgLabel)
        vboxTab1.addWidget(self.overlayLabel, 0,0,1,1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.centerLabel, 0,0,1,1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_1a_Label, 0,0,1,1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_1b_Label, 0,0,1,1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_1c_Label, 0,0,1,1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_1d_Label, 0,0,1,1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_2a_Label, 0,0,1,1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_2b_Label, 0,0,1,1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_2c_Label, 0,0,1,1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_2d_Label, 0,0,1,1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_3a_Label, 0,0,1,1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_3b_Label, 0,0,1,1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_3c_Label, 0,0,1,1, QtCore.Qt.AlignHCenter)
        vboxTab1.addWidget(self.front_3d_Label, 0,0,1,1, QtCore.Qt.AlignHCenter)

        self.cameraView.setLayout(vboxTab1)
        self.tabWidget.addTab(self.cameraView, "")

        self.min_dist = 2
        self.max_dist = 100
        self.dist_step_01 = self.min_dist + round((self.max_dist - self.min_dist) / 4 * 1)
        self.dist_step_02 = self.min_dist + round((self.max_dist - self.min_dist) / 4 * 2)#0.1425
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

    def SensorUpdateSlot(self, distance):
        self.front_1a_Label.setPixmap(self.front_1a_ON if distance < self.dist_step_01 else self.front_1a_OFF)
        self.front_1b_Label.setPixmap(self.front_1b_ON if distance < self.dist_step_02 else self.front_1b_OFF)
        self.front_1c_Label.setPixmap(self.front_1c_ON if distance < self.dist_step_03 else self.front_1c_OFF)
        self.front_1d_Label.setPixmap(self.front_1d_ON if distance < self.dist_step_04 else self.front_1d_OFF)  

    
    def closeEvent(self, event):
        self.thread.stop()
        event.accept()
    '''
    @pyqtSlot(QtCore.QModelIndex)
    def update_image(self, cv_img):
        self.bgLabel.setPixmap(QPixmap.fromImage(cv_img))
    '''

    def setup_media_tab(self, MainWindow):
        # Setting up Tab 3: Media player
        self.mediaTab = QtWidgets.QWidget()
        self.mediaTab.setObjectName("mediaTab")
        self.tabWidget.addTab(self.mediaTab, "")

        self.albumCover = QtWidgets.QLabel(self.mediaTab)
        self.albumCover.setGeometry(QtCore.QRect(370, 60, 300, 300))
        self.albumCover.setText("")
        self.albumCover.setObjectName("albumCover")

        self.trackName = QtWidgets.QLabel(self.mediaTab)
        self.trackName.setGeometry(QtCore.QRect(120, 380, 800, 20))
        self.trackName.setAlignment(QtCore.Qt.AlignCenter)
        self.trackName.setObjectName("trackName")
        self.trackName.setText("Track Name")
        self.trackName.setFont(self.bold_30_font)
        self.trackName.setStyleSheet("color: #01CBEE")

        self.artistName = QtWidgets.QLabel(self.mediaTab)
        self.artistName.setGeometry(QtCore.QRect(120, 420, 800, 20))
        self.artistName.setAlignment(QtCore.Qt.AlignCenter)
        self.artistName.setObjectName("artistName")
        self.artistName.setText("Artist Name")
        self.artistName.setFont(self.light_20_font)
        self.artistName.setStyleSheet("color: white")

        self.playPauseButton = QtWidgets.QPushButton(self.mediaTab)
        self.playPauseButton.setGeometry(QtCore.QRect(410, 490, 215, 23))
        self.playPauseButton.setObjectName("playPauseButton")
        self.playPauseButton.setText("Play/Pause")
        self.playPauseButton.setFont(self.light_20_font)
        self.playPauseButton.setStyleSheet("color: #01CBEE")
        self.playPauseButton.clicked.connect(self.play_track)

        self.nextButton = QtWidgets.QPushButton(self.mediaTab)
        self.nextButton.setGeometry(QtCore.QRect(700, 490, 100, 23))
        self.nextButton.setObjectName("nextButton")
        self.nextButton.setText("Next")
        self.nextButton.setFont(self.light_20_font)
        self.nextButton.setStyleSheet("color: #01CBEE")
        self.nextButton.clicked.connect(self.next_track)

        self.prevButton = QtWidgets.QPushButton(self.mediaTab)
        self.prevButton.setGeometry(QtCore.QRect(200, 490, 100, 23))
        self.prevButton.setObjectName("prevButton")
        self.prevButton.setText("Prev")
        self.prevButton.setFont(self.light_20_font)
        self.prevButton.setStyleSheet("color: #01CBEE")
        self.prevButton.clicked.connect(self.prev_track)

        """
        self.horizontalSlider = QtWidgets.QSlider(self.mediaTab)
        self.horizontalSlider.setGeometry(QtCore.QRect(219, 280, 221, 20))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        """

        self.timeLabel_2 = QtWidgets.QLabel(self.mediaTab)
        self.timeLabel_2.setGeometry(QtCore.QRect(390, 0, 261, 71))
        self.timeLabel_2.setFont(self.light_30_font)
        self.timeLabel_2.setStyleSheet("color: rgb(255, 255, 255);")
        self.timeLabel_2.setAlignment(QtCore.Qt.AlignCenter)
        self.timeLabel_2.setObjectName("timeLabel_2")

        # Prepare media player
        self.song_list = os.listdir(f"{self.folder_path}/music")
        random.shuffle(self.song_list)
        self.play_music = True
        self.previous_song = False
        self.next_song = False
        self.curr_song_index = 0
        self.song_index = 0
        self.stop_media_player = False

        self.media_player_thread = Thread(target=self.run_media_player)
        self.media_player_thread.start()


    
    def run_media_player(self):
        self.player = vlc.MediaPlayer()
        while not self.stop_media_player:
            # Reached past last song
            if self.curr_song_index == len(self.song_list):
                self.curr_song_index = 0
            # Reached behind first song
            elif self.curr_song_index == -1:
                self.curr_song_index = len(self.song_list) -1

            print(f"Playing {self.song_list[self.curr_song_index]}")
            # Update track info
            self.load_track_data(self.song_list[self.curr_song_index])
            media = vlc.Media(f"{self.folder_path}/music/{self.song_list[self.curr_song_index]}")
            self.player.set_media(media)
            self.player.play()
            # Wait for the song to play
            time.sleep(3)
            while True:
                # Song is finished, move to next song
                if self.player.is_playing() != 1 and self.play_music:
                    self.curr_song_index += 1
                    break
                # Song is still playing, and next button was pressed
                elif self.player.is_playing() and self.next_song:
                    self.curr_song_index += 1
                    self.next_song = False
                    break
                # Song is still playing, and previous button was pressed
                elif self.player.is_playing() and self.previous_song:
                    self.curr_song_index -= 1
                    self.previous_song = False
                    break
                else:
                    # Song is still playing
                    time.sleep(1)
    
    def load_track_data(self, song):
        track_path = f"{self.folder_path}/music/{song}"
        print(f"Track path: {track_path}")
        mp3_file = File(track_path, easy=True)
        track_name = mp3_file.get('title')[0].replace("&", "and")
        artist_name = mp3_file.get('artist')[0].replace("&", "and")
        self.trackName.setText(f"{track_name[:25]}...")
        self.artistName.setText(artist_name.replace("/", ", "))

        tags = ID3(track_path)
        album_cover = tags.getall("APIC")[0].data
        qImg = QtGui.QImage()
        qImg.loadFromData(album_cover)
        pixmap01 = QtGui.QPixmap.fromImage(qImg)
        pixmap_image = QtGui.QPixmap(pixmap01)
        scaled_res = QtCore.QSize(250, 250)
        pixmap_image = pixmap_image.scaled(scaled_res, aspectRatioMode=QtCore.Qt.KeepAspectRatio, transformMode=QtCore.Qt.SmoothTransformation)
        self.albumCover.setPixmap(pixmap_image)
        self.albumCover.setAlignment(QtCore.Qt.AlignCenter)

    def play_track(self):
        if self.player.is_playing():
            self.play_music = False
            self.player.pause()
        else:
            self.play_music = True
            self.player.play()
    
    def prev_track(self):
        self.previous_song = True
    def next_track(self):
        self.next_song = True
    
    def initialize_ui(self, MainWindow):
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Dashboard"))
        self.speedLabel.setText(_translate("MainWindow", "37"))
        self.kmhLabel.setText(_translate("MainWindow", "KMH"))
        self.timeLabel.setText(_translate("MainWindow", "8:36 PM"))
        self.locationValueLabel.setText(_translate("MainWindow", "SOME STREET"))
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Dashboard"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.mainDash), _translate("MainWindow", "Main Dash"))
        #self.cameraFrame.setText(_translate("MainWindow", "TextLabel"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.cameraView), _translate("MainWindow", "Camera View"))
        self.locationLabel.setText(_translate("MainWindow", "LOCATION"))
        self.outTempLabel.setText(_translate("MainWindow", "OUT TEMP"))
        self.kmhLabel.setText(_translate("MainWindow", "KMH"))
        self.outTempValLabel.setText(_translate("MainWindow", "+ 25 C"))

        # Update speed every second
        self.speed_thread = Thread(target=self.update_speed)
        self.initialize_gps()
        # Update location every 10 seconds
        self.location_thread = Thread(target=self.update_location)
        self.initialize_location_csv()
        # Update time every second
        self.time_thread = Thread(target=self.update_time)
        # Update camera
        #Update sensors

        self.update_speed_started = True
        self.update_location_started = True
        self.update_time_started = True

        self.speed_thread.start()
        self.location_thread.start()
        self.time_thread.start()

    def play_startup_sound(self):
        self.media_player = vlc.MediaPlayer()
        media = vlc.Media(f"{self.folder_path}/sounds/startup_chime.mp3")
        self.media_player.set_media(media)
        self.media_player.play()


    def initialize_gps(self):
        print("Initializing GPS...")
        # TODO: Check for GPS status
        subprocess.run(["systemctl", "enable", "gpsd.socket"])
        gpsd.connect()
    
    def initialize_location_csv(self):
        print("Creating connection to location csv...")
        search_file = open('csv/canadacities.csv', 'r')
        self.location_reader = csv.reader(search_file, delimiter= ',')
        self.location_dict = {}
        for city in self.location_reader:
            if city[0] != 'city':
                self.location_dict[city[0]] = (float(city[4]), float(city[5]))

    def get_time(self):
        """
        # Get gps packet
        gps_packet = gpsd.get_current()
        # Extract time
        date_time = str(gps_packet.time)
    
        split_list = date_time.split("T")
        gps_time = split_list[1]
        hour_minute = gps_time.split(":")
        hour = hour_minute[0]
        minute = hour_minute[1]
        return f"{hour}:{minute} {'PM' if int(hour) > 11 else 'AM'}"
        """
        now = datetime.now()
        curr_time = time.strftime("%I:%M %p")
        return curr_time

    
    def get_speed(self):
        # Get gps packet
        gps_packet = gpsd.get_current()
        # Extract speed
        speed_mph = float(gps_packet.hspeed)
        # Convert speed to int and kmh
        speed_kmh_int = int(speed_mph * 1.609344)
        #print(f"Current speed: {speed_kmh_int}")
        return speed_kmh_int
    
    def get_current_suberb(self):
        # Get gps packet
        gps_packet = gpsd.get_current()
        # Get latitude and longitude
        lat = gps_packet.lat
        long = gps_packet.lon
        #print(f"My coordinates: {lat}, {long}")
        
        curr_match = 100.00
        matched_city = ""
        # Search through location csv
        for city in self.location_dict:
            city_lat = self.location_dict[city][0]
            city_long = self.location_dict[city][1]
            lat_diff = abs(lat) - abs(city_lat)
            long_diff = abs(long) - abs(city_long)
            calc_match = abs(lat_diff) + abs(long_diff)
            if calc_match < curr_match:
                curr_match = calc_match
                matched_city = str(city)
        
        #print(f"Matched city: {matched_city}")
        return matched_city


    def update_speed(self):
        while self.update_speed_started:
            # Set current speed
            self.speedLabel.setText(str(self.get_speed()))
            time.sleep(1)
    
    def update_location(self):
        while self.update_location_started:
            # Set current suburb
            self.locationValueLabel.setText(self.get_current_suberb())
            time.sleep(5)
    
    def update_time(self):
        while self.update_time_started:
            # Set current time
            curr_time = self.get_time()
            self.timeLabel.setText(curr_time)
            self.timeLabel_2.setText(curr_time)
            time.sleep(1)

    def stop(self):
        print("Exiting...")
        self.update_location_started = False
        self.update_speed_started = False
        self.update_time_started = False
        self.stop_media_player = True


        self.speed_thread.join()
        self.time_thread.join()
        self.location_thread.join()
        self.media_player_thread.join()
