from Servo import Servo

import board
import Jetson.GPIO as GPIO
from adafruit_pca9685 import PCA9685
from ArmMotor import ArmMotor
from ArmController import ArmController
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
i2c = board.I2C()
pca = PCA9685(i2c)
pca.frequency = 50
motorList = [
    [8,"l",4,1,0,0,0], #sholder
    [9,"l",5,1,-410,-280,90], #upper arm
    [10,"l",6,1,-243,80,0] #fore arm
        ]
motorObj = []
servoList = [2,3,6]
servoObj = []
for i in servoList:
    servo = Servo(pca,i)
    servoObj.append(servo)
for i in motorList:
    motor = ArmMotor(i[4],i[5],i[6],pca,i[0],i[1],i[2],i[3],7)
    motorObj.append(motor)
arm = ArmController(motorObj,servoObj)


try:

    input("Pause")
    arm.armMotors[1].motor.motor.moveMotor(0)

    #Set J2 to 45 degrees and J3 to -30 degrees
    #arm.setRotationArm([0,124.1,104.7312,0,0],True)

    # Set J2 to -45 degrees and J3 to -30 degrees
    #arm.setRotationArm([-45,-30],True)

    #input("Pause")
    # Set J2 to 45 degrees and J3 to -65 degrees (this can be used as a "default" position)
    #arm.setRotationArm([45,-65],True)

    arm.travelArm(0.4,-0.02,0.3,False)


except KeyboardInterrupt:
    arm.killMotors()

arm.killMotors()

