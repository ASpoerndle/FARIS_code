import board
import time
from adafruit_pca9685 import PCA9685
'''
i2c = board.I2C()
pca = PCA9685(i2c)
pca.frequency = 50

# Use the CHANNEL, not the servo object
motor_channel = pca.channels[15]
motor_channel2 = pca.channels[14]
print("readying device")

motor_channel.duty_cycle = 5400
motor_channel2.duty_cycle = 5400
time.sleep(1)

for i in range(5000,6050,5):
    motor_channel.duty_cycle = i
    motor_channel2.duty_cycle = i
    print(i)
    time.sleep(0.05)

for x in range(6050,5000,-5):
    motor_channel2.duty_cycle = x
    motor_channel.duty_cycle = x
    print(x)
    time.sleep(0.05)
'''


class WheelMotor:
    default_f = 5400
    default_r = 5000
    current_duty = 5200
    def forward_motion(self, speed):
        print("f")
        new_speed = WheelMotor.default_f + (1300 * speed)
        #for i in range(WheelMotor.default_f, int(new_speed),5):
         #   self.motor.duty_cycle = i
          #  time.sleep(0.05)
        print("new FC: ", new_speed)
        self.motor.duty_cycle = int(new_speed)
        WheelMotor.current_duty = int(new_speed)
    def backward_motion(self,speed):
        print("r")
        new_speed = WheelMotor.default_r + (1300 * speed)
        #for i in range(WheelMotor.default_r, int(new_speed), -5):
         #   self.motor.duty_cycle = i
          #  time.sleep(0.05)
        print("new DC: ", new_speed)
        self.motor.duty_cycle = int(new_speed)
        WheelMotor.current_duty = int(new_speed)
    def zero_from_forward(self):
        #for i in range(WheelMotor.current_duty, WheelMotor.default_f,-5):
         #   self.motor.duty_cycle = i
          #  time.sleep(0.05)
        self.motor.duty_cycle = WheelMotor.default_f
        WheelMotor.current_duty = WheelMotor.default_f

    def zero_from_backward(self):
        #for i in range(WheelMotor.current_duty, WheelMotor.default_r,5):
         #   self.motor.duty_cycle = i
          #  time.sleep(0.05)
        self.motor.duty_cycle = WheelMotor.default_r
        WheelMotor.current_duty = WheelMotor.default_r

    def __init__(self,pca, pin,side):
        self.motor = pca.channels[pin]
        self.motor.duty_cycle = 5200
        self.side = side
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
            if(WheelMotor.current_duty > WheelMotor.default_f):
                self.zero_from_forward()
            else:
                self.zero_from_backward()

