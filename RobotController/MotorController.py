import board
from adafruit_pca9685 import PCA9685
import Jetson.GPIO as GPIO
import time

class MotorController():
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        # PCA9685 Setup
        i2c = board.I2C()
        self.pca = PCA9685(i2c)
        self.pca.frequency = 50

        # Define motors: [PCA_Pin, Side, Encoder_Ch, forward_offset]
        # Using your provided indices
        self.rotational_motors = []
        setup_data = [
            [2,"l",0,0], [3,"l",1,0], [4,"l",2,0], [6,"l",3,0], # Front/Aux
            [11,'l',6,0], [10,'l',5,0], [13,'r',4,0], [15,'r',7,0] # Main Drive Group
        ]

        print("Initializing Rotational Motors...")
        for data in setup_data:
            m = RotationalMotor(self.pca, data[0], data[1], data[2], data[3])
            self.rotational_motors.append(m)

    def calculateRelativeAngle(self, target, current):
        """Finds the shortest distance between two angles on a 360 circle."""
        relative = (target - current + 180) % 360 - 180
        return relative

    def rotate(self, target_angle, speed, group="w"):
        """
        Rotates a group of motors to a global target angle.
        'w' for drive wheels (4-7), else (0-3).
        """
        if group == "w":
            motors = self.rotational_motors[4:8]
        else:
            motors = self.rotational_motors[0:4]

        # Calculate individual relative steps needed for each wheel
        relative_angles = []
        for m in motors:
            current_global = (m.getCurrentPosition() / 8192) * 360
            rel = self.calculateRelativeAngle(target_angle, current_global)
            relative_angles.append(rel)

        # Main Control Loop
        while True:
            all_aligned = True
            for i, motor in enumerate(motors):
                # We pass the relative angle once; internal logic handles the rest
                is_done = motor.rotateForward(relative_angles[i], speed)
                if not is_done:
                    all_aligned = False
            
            if all_aligned:
                break
            
            time.sleep(0.01) # Yield for I2C bus

        self.stopMotors()

    def stopMotors(self):
        for motor in self.rotational_motors:
            motor.stopMotor()

    def __del__(self):
        self.stopMotors()
        GPIO.cleanup()
mc = MotorController()
mc.rotate(10,0.3,"w")
