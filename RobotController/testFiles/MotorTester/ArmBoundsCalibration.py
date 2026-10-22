from ArmController import ArmController
import Jetson.GPIO as GPIO
import board
from adafruit_pca9685 import PCA9685
pinListArm = [
    [8, 'l', 4, 0],  # Shoulder
    [9, 'l', 5, 0],  # Upper arm
    [10, 'l', 6, 0]  # Fore arm

]
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
i2c = board.I2C()
pca = PCA9685(i2c)
pca.frequency = 50

pin_list_servos = [2, 3, 6]  # Servo 0, Servo 1, Gripper

armController = ArmController(pinListArm, pin_list_servos,pca)
while True:
    for motor in armController.armMotors:
        print(f"Encoder: {motor.encoder.encoder}\tAngle Rotation:{motor.encoder.getCurrentAngle()}\tEncoder Position: {motor.encoder.getEncoderPosition()}")