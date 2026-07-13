from RotationFocusedMotor import RotationFocusedMotor

class ArmController():
    def __init__(self, armMotors, armServos):
        self.armMotors = armMotors
        """
        Motor 0 = Shoulder
        Motor 1 = Arm
        Motor 2 = Forearm
        """

        self. armServos = armServos
        """
        Servo 0 = Twist (roll)
        Servo 1 = Tilt (pitch)
        Servo 2 = Grab
        """

    def beginIK(self, intendedDestination):
        x = intendedDestination[0]
        y = intendedDestination[1]
        z = intendedDestination[2]
    """
    Method: setRotationArm(List<List<float>> rotationMatrix)
    Purpose: the matrix tells the motors how far they should rotate. This should rotate all of the motors
             to the correct position
    """
    def setRotationArm(self, rotationMatrix,debug=False):
        motorList = self.armMotors.copy()
        #rotation matrix = 3 x 4
        matrix = [
            [1,0,0,0], #motor 0
            [0,1,0,0], #motor 1
            [0,0,1,0]  #motor 2
        ]
        angleList = []
        for i in range(len(matrix)):
            for j in matrix[i]:
                if(j != 0):
                    angleList.append(j)
                    break
        stopCond = len(motorList) == 0
        speed = 0.5
        while(stopCond):
            for i, motor in enumerate(motorList):
                isAligned = self.checkRotate(motor, angleList[i], speed, debug)
                if (isAligned):
                    motorList.pop(i)
        for motor in motorList:
            motor.stopMotor()


    def checkRotate(self, motor, angle, speed, debug=False):
            return motor.rotate(angle, speed, debug)