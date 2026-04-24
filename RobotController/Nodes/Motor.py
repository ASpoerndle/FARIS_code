import board
import time
from adafruit_pca9685 import PCA9685


class WheelMotor:
    default_f = 5400
    default_r = 5000
    current_duty = 5200

    """
    Method: forward_motion(speed)
    Purpose: Adjusts the motors duty cycle proportionally to an inputted float speed so that the 
             robot can move forward
    """
    def forward_motion(self, speed):
        
        new_speed = WheelMotor.default_f + (1300 * speed)
        self.motor.duty_cycle = int(new_speed)
        WheelMotor.current_duty = int(new_speed)
    """
    Method: backward_motion(speed)
    Purpose: Adjusts the motors duty cycle proportionally to an inputted float speed so that
             the robot can move backward
    """
    def backward_motion(self,speed):
        
        new_speed = WheelMotor.default_r + (1300 * speed)
        self.motor.duty_cycle = int(new_speed)
        WheelMotor.current_duty = int(new_speed)
    """
    Method: zero_motion()
    Purpose: sets the motor duty cycle to a motionless speed (5200 mHz)
    """
    def zero_motion(self):
        self.motor.duty_cycle = 5200
        WheelMotor.current_duty = 5200

    
    def __init__(self,pca, pin,side):
        self.motor = pca.channels[pin]
        self.motor.duty_cycle = 5200
        self.side = side
       
    """
    Method: move_motor(speed)
    Purpose: takes a float input {speed} and calls the proper method depending on which side the motor is on
             and whether the inputted speed is positive or negative
    """
    def move_motor(self, speed):
        if(speed > 0 and speed <= 1):
            if(self.side == 'r'):
                speed *= -1
                self.backward_motion(speed)
                return
            self.forward_motion(speed)
            
        elif(speed < 0 and speed >= -1):
            if(self.side == 'r'):
                speed *=-1
                self.forward_motion(speed)
                return
            self.backward_motion(speed)
            current_speed = speed
        elif(speed == 0):
            self.zero_motion()

