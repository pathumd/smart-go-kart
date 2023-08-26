# 🏎️💨 Smart Go Kart

## 🤝 Contributors
- 🥇 Pathum Danthanarayana ([@pathum.danthanarayana](https://www.instagram.com/pathum.danthanarayana/))
- 🥇 Pasindu Danthanarayana ([@pasindu.md](https://www.instagram.com/pasindu.md/))

## ⚡Hardware

### Circuit diagram 
<img width="2000" alt="image" src="https://i.imgur.com/LCedBPL.jpg">

### Raspberry Pi 4 Model B
<img width="300" alt="image" src="https://i.imgur.com/WZcQYSI.png">

- Used to run the main dashboard application.
### GPS Receiver
<img width="300" alt="image" src="https://i.imgur.com/11fM2Am.png">

- Used to determine the go-kart's current speed and location.
### HC-SR04 Ultrasonic sensor (x6)
<img width="300" alt="image" src="https://i.imgur.com/I74SUnb.png">

- Used to calculate and determine the proximity of objects surrounding the go-kart
- Three ultrasonic sensors are positioned at the front of the go-kart, and three at the back
    
### DHT11 Temperature and Humidity Sensor (x1)
<img width="300" alt="image" src="https://i.imgur.com/Z3JI73m.png">

- Used to determine the external temperature of the go-kart.
  
### Breadboard (x3)

- Used a half-sized 400 point breadboard to host the temperature sensor
- Used two full-sized 830 point breadboards to host 3 ultrasonic sensors each 

### Resistors
- Used a voltage divider circuit with 1kΩ (x6) and 2kΩ (x6) resistors to lower the sensor output voltage from 5V to 3.3V. Consider the example diagram below (values vary).
<img width="300" alt="image" src="https://i.imgur.com/stbM6ib.png">

### Jumper wires

- Female-to-male jumper wires were used to connect the Raspberry Pi to the breadboards
- Female-to-female jumper wires were used to connect the buzzer to the Raspberry Pi
- Red = VCC
- Blue = Trig
- Yellow = Echo
- Black = Ground 
  
### Wide Angle Camera for Raspberry Pi (Inno-Maker)
<img width="300" alt="image" src="https://i.imgur.com/wooMexV.png">

- Used to provide rear visibility for user
  
### CREATIVE Pebbles USB Speakers (x1)
<img width="300" alt="image" src="https://i.imgur.com/xj3L626.png">

- Used to play the startup sound for the dashboard and to play media.

### 7" IPS Touch Display
<img width="300" alt="image" src="https://i.imgur.com/YXoSuO2.png">

- Used to display the main dashboard application.

## 👨‍💻 Software
### Home Tab
<img width="800" alt="image" src="https://imgur.com/HeDY6sH.png">

- Features a navigation menu at the top to quickly switch between tabs
- Displays the current time using the Raspberry Pi system clock
- Displays the Go-kart's current speed (in km/h) by parsing received GPS packets from GPS receiver
- Displays the Go-kart's current location by comparing its latitude/longitude to a coordinate database
- Displays the tempature outside by polling temperature sensor

### Media Tab
<img width="800" alt="image" src="https://imgur.com/0LTQVar.png">

- Starts playing the media found in `dashboard/music` as a playlist upon startup with automatic shuffling
- Pulls metadata from each track to display the track's album cover, track name, and artist name(s)
- Allows the user to play, pause, skip, or move to previous track
- Media is run in a background thread, allowing the user to freely move between tabs while music plays
- When an obstacle is detected by one of the ultrasonic sensors, the music volume is reduced by 50%

### Reverse Camera Tab
<img width="800" alt="image" src="https://imgur.com/yLzlRXp.png">

- Includes 180 degree collision detection system
- Features a reverse camera when the Go-kart is in reverse 
- Includes parking assistance
- Includes a buzzer with frequency that corresponds to the proximity to obstacles
- Uses distance steps to display colour-coded levels of proximity to obstacles using distance data recieved from Ultrasonic Sensors
-  When one of the sensors turn yellow, the program automatically reduces the music volume, switches to the camera tab, and activates the buzzer


## 📖 Software Dependencies
### Raspberry Pi:
- Raspbian (insert OS version here)
### Python 3.8.2
(add library versions)
- PyQt5
- gpsd
- mutagen
- Adafruit_DHT
- vlc
  
## ⚠️ Problems we ran into
- Many of the online resources supported circuits with 1-2 ultrasonic sensors. Employing 6 ultrasonic sensors was a new obstacle that had to be overcome. 
- Layering images over a video in the camera tab (ex. shapes and parking lines) was difficult as they would replace the video QLabel. The solution to this was to implement a vbox layout that hosts the necessary labels similar to an array.
- Traditional methods for updating the GUI with distances and video frames proved suboptimal. After experimenting with various approaches, a signal-slot connection that utilizes references was settled upon.
- Finding a mathematical approach for a GUI representation of the collision detection and implementing an accurate buzzer frequency was challenging 

## ⏩ Next steps 
- Automatically running the dashboard application upon boot-up
- Engineering the Go-kart frame, mechanics, and dashboard housing
- Soldering the hardware onto a perfboard 

