import board
import time
import Jetson.GPIO as GPIO
i2c = board.I2C()
from adafruit_ads1x15 import ADS1015, AnalogIn, ads1x15
ads = ADS1015(i2c)
chan = AnalogIn(ads, ads1x15.Pin.A0)
while True:
    print(chan.value, chan.voltage)
    time.sleep(1)
