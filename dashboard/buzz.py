from gpiozero import Buzzer
from time import sleep

buz = Buzzer(26)

while True:
	buz.on()
	sleep(1)
	buz.off()
