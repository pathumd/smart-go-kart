import cv2
import csv
from imutils.video import VideoStream
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
import gpsd
import vlc
from threading import Thread
import time
from datetime import datetime
import subprocess
from gpiozero import DistanceSensor 
from time import sleep

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        self.setup_fonts()

        self.setup_window(MainWindow)

        self.setup_dashboard_tab(MainWindow)
        
        self.setup_camera_tab(MainWindow)

        self.setup_media_tab(MainWindow)

        self.initialize_ui(MainWindow)

        # Launch the GUI with Tab 1 selected
        self.tabWidget.setCurrentIndex(1)
        self.play_startup_sound()

    def setup_fonts(self):
        # Setup font database
        QtGui.QFontDatabase.addApplicationFont("fonts/RIDGE-LIGHT-OBLIQUE.otf")
        QtGui.QFontDatabase.addApplicationFont("fonts/Ridge-Bold-Oblique.otf")
        
        self.light_30_font = QtGui.QFont("RIDGE-LIGHT-OBLIQUE", 30)
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
        self.timeLabel.setGeometry(QtCore.QRect(410, 0, 211, 71))
        
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


        self.vs = VideoStream(src=0, usePiCamera=True, resolution=(1024, 600), framerate=32).start()



        self.sensor = DistanceSensor(24, 23)
        min_dist = 2
        max_dist = 100
        self.dist_step_01 = min_dist + round((max_dist - min_dist) / 4 * 1)
        self.dist_step_02 = min_dist + round((max_dist - min_dist) / 4 * 2)#0.1425
        self.dist_step_03 = min_dist + round((max_dist - min_dist) / 4 * 3)
        self.dist_step_04 = min_dist + round((max_dist - min_dist) / 4 * 4)
        print(self.dist_step_01)

        self.timer1=QTimer()
        self.timer1.timeout.connect(self.update_camera)
        self.timer1.start()

        self.timer2=QTimer()
        self.timer2.timeout.connect(self.update_sensors)
        self.timer2.start()


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

    def setup_media_tab(self, MainWindow):
        pass

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
        player = vlc.MediaPlayer("sounds/startup_chime.mp3")
        player.play()

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
        military_hour = now.strftime("%H")
        hour = (int(military_hour) - 2) % 10
        minute = now.strftime("%M")
        return f"{hour}:{minute} {'PM' if int(military_hour) > 11 else 'AM'}"

    
    def get_speed(self):
        # Get gps packet
        gps_packet = gpsd.get_current()
        # Extract speed
        speed_mph = float(gps_packet.hspeed)
        # Convert speed to int and kmh
        speed_kmh_int = int(speed_mph * 1.609344)
        print(f"Current speed: {speed_kmh_int}")
        return speed_kmh_int
    
    def get_current_suberb(self):
        # Get gps packet
        gps_packet = gpsd.get_current()
        # Get latitude and longitude
        lat = gps_packet.lat
        long = gps_packet.lon
        print(f"My coordinates: {lat}, {long}")
        
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
        
        print(f"Matched city: {matched_city}")
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
            self.timeLabel.setText(self.get_time())
            time.sleep(1)


    def update_camera(self):
        self.frame = self.vs.read()  
        self.image = QtGui.QImage(self.frame.data, self.frame.shape[1], self.frame.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
        self.bgLabel.setPixmap(QPixmap.fromImage(self.image))
        #cv2.destroyAllWindows()  
        #self.vs.stop()
        
    def update_sensors(self):
        total_distance = round(self.sensor.distance*100)
        self.front_1a_Label.setPixmap(self.front_1a_ON if total_distance < self.dist_step_01 else self.front_1a_OFF)
        self.front_1b_Label.setPixmap(self.front_1b_ON if total_distance < self.dist_step_02 else self.front_1b_OFF)
        self.front_1c_Label.setPixmap(self.front_1c_ON if total_distance < self.dist_step_03 else self.front_1c_OFF)
        self.front_1d_Label.setPixmap(self.front_1d_ON if total_distance < self.dist_step_04 else self.front_1d_OFF)  
        print('Distance to nearest object is', total_distance, 'cm')

    def stop(self):
        print("Exiting...")
        self.update_location_started = False
        self.update_speed_started = False
        self.update_time_started = False


        self.speed_thread.join()
        self.time_thread.join()
        self.location_thread.join()
