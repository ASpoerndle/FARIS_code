from MotorWithEncoder import MotorWithEncoder

class DriveFocusedMotor():

    def __init__(self, pca, pin, side, enc, fVal,i2c_bus):
        self.enc = enc
        self.motor = MotorWithEncoder(pca, pin, side, enc, fVal,i2c_bus)

    """
      Method: driveForward(angle {degrees} ,speed)
      Purpose: handles the logic for moving the wheel motors forward and backward    
      """

    def driveForward(self, position, speed, isBack, debug=False):

        if (debug):
            print(f"Encoder: {self.enc} | Tick Position: {position} | Polar: {self.motor.polarity} | Back?: {isBack}")
        if (isBack):
            print("!!!!!!DRIVETONEGATIVEVALUE!!!!!!!:")
            return self.driveToNegative(position, speed, debug)
        self.motor.pid.Kp = 0.06
        self.motor.pid.Kd = 0.0002
        self.motor.pid.Ki = 0.0002
        return self.driveToPositive(position, speed, debug)

    """
      Method: drive(target {Quadrature}, speed)
      Purpose: the logic that tells the motor to keep running until it reaches its desired location
      """

    def driveToPositive(self, target, speed, debug=False):
        current = self.motor.encoder.getEncoderPosition()
        self.motor.pid.setpoint = target
        motor_speed = self.motor.pid(current)
        motor_speed *= speed
        motor_speed = abs(motor_speed)
        if (self.motor.polarity == 1):

            bool = current >= target
            if (bool):
                if (debug):
                    print(f"===Encoder: {self.motor.encoder.encoder} Stopped=== Target: {target} | Current: {current}")
                self.motor.moveMotor(0)

            else:
                if (debug):
                    print(f"Target: {target} | Current: {current} Encoder: {self.motor.encoder.encoder} |  Speed: {motor_speed}")
                self.motor.moveMotor(motor_speed)
        else:
            bool = current <= -target
            if (bool):
                if (debug):
                    print(f"Encoder: {self.motor.encoder.encoder} Stopped=== Current: {current} Target: {target}")
                self.motor.moveMotor(0)
            else:
                self.motor.moveMotor(motor_speed)
        return bool


    """
    Method: drive_neg(target {quadrature}, speed)
    Purpose: allows the motors that need to drive towards negative quadrature values to be able to move with the other motors
    """

    def driveToNegative(self, target, speed, debug=False):
        current = self.motor.encoder.getEncoderPosition()
        self.motor.pid.setpoint = target
        motorSpeed = self.motor.pid(current)
        motorSpeed *= speed
        if(motorSpeed > 0):
            motorSpeed *= -1

        bool = abs(current) >= abs(target)
        if (bool):
            if (debug):
                print(f"===Encoder: {self.motor.encoder.encoder} Stopped=== Current {current} | Target: {target}")
            self.motor.moveMotor(0)

        else:
            if (debug):
                print(f"Target: {target} | Current: {current} Encoder: {self.motor.encoder.encoder} |  Speed: {motorSpeed}")
            self.motor.moveMotor(motorSpeed)
        return bool
    def setSpeed(self,speed):
        self.motor.setSpeed(speed)
