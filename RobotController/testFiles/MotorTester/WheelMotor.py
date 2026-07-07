from RotationalMotor import RotationalMotor

class WheelMotor():

    def __init__(self, pca, pin, side, enc, fVal):
        self.motor = RotationalMotor(pca, pin, side, enc, fVal)

    """
      Method: driveForward(angle {degrees} ,speed)
      Purpose: handles the logic for moving the wheel motors forward and backward    
      """

    def driveForward(self, position, speed, isBack, debug=False):

        if (debug):
            print(f"Encoder: {self.motor.encoder.encoder} | Tick Position: {position} | Polar: {self.motor.polarity} | Back?: {isBack}")
        if (isBack):
            print("!!!!!!DRIVETONEGATIVEVALUE!!!!!!!:")
            return self.driveToNegative(self.motor.polarity * position, speed, debug)
        self.motor.pid.Kp = 0.06
        self.motor.pid.Kd = 0.0002
        self.motor.pid.Ki = 0.0002
        return self.driveToPositive(self.motor.polarity * position, speed, debug)

    """
      Method: drive(target {Quadrature}, speed)
      Purpose: the logic that tells the motor to keep running until it reaches its desired location
      """

    def driveToPositive(self, target, speed, debug=False):
        current = self.motor.encoder.getEncoderPosition()
        self.motor.pid.setpoint = target
        motor_speed = self.motor.pid(current)
        motor_speed *= speed
        if (self.motor.polarity == 1):

            bool = current >= target
            if (bool):
                if (debug):
                    print(f"===Encoder: {self.motor.encoder} Stopped=== Target: {target} | Current: {current}")
                self.motor.moveMotor(0)

            else:
                if (debug):
                    print(f"Target: {target} | Current: {current} Encoder: {self.motor.encoder} |  Speed: {motor_speed}")
                self.motor.moveMotor(motor_speed)
        else:
            bool = current <= -target
            if (bool):
                if (debug):
                    print(f"Encoder: {self.motor.encoder} Stopped=== Current: {current} Target: {target}")
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
                print(f"===Encoder: {self.motor.encoder} Stopped=== Current {current} | Target: {target}")
            self.motor.moveMotor(0)

        else:
            if (debug):
                print(f"Target: {target} | Current: {current} Encoder: {self.motor.encoder} |  Speed: {motorSpeed}")
            self.motor.moveMotor(motorSpeed)
        return bool
    def setSpeed(self,speed):
        self.motor.setSpeed(speed)
