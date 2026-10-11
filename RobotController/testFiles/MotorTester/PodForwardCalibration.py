from PodController import PodController
import Jetson.GPIO as GPIO
import board
from adafruit_pca9685 import PCA9685
from RotationFocusedMotor import RotationFocusedMotor

# Code for Jetson/adafruit breakout board
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
i2c = board.I2C()
pca = PCA9685(i2c)
pca.frequency = 50
def checkAngleChange(i):
    try:
        while (True):
            angles = podController.getAllPodAngles()[0]
            print(f"{angles[i]}")
    except KeyboardInterrupt:
        pods[i]
        print("moving on...")

pods =  [[0, "l", 4, 0] , #BL - Pod-0
         [1, "l", 5, 0], #BR - Pod-1
         [2, "l", 6, 0], #FR - Pod-2
         [3, "l", 7, 0], #FL - Pod-3
         ]

podController = PodController(pods[0:4])
for i in range(4):
    checkAngleChange(i)

try:
    while(True):
        angles = podController.getAllPodAngles(True)
        for i,pod in podController.rotMotors:
            print(f"{i}|{pod.motor.encoder.getEncoderPosition()}")
except KeyboardInterrupt:
    print("FINISHED")