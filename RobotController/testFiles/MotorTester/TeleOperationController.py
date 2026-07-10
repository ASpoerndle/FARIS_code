from PodController import PodController
from WheelController import WheelController
from Servo import Servo


class TeleOperationController:
    def __init__(self, podController,wheelController, servoList):
        self.podController = podController
        self.wheelController = wheelController
        self.servoList = servoList


    """
       ===TELE-OPERATION METHODS===
       """

    """
    Method: teleforward(speed)
    Purpose: For the TeleOp controller, allows for the controller to move the robot forward and backward
    """

    def teleForward(self, speed):
        self.wheelController.teleForward(speed)

    """
    Method: teleTurn()
    Purpose: For the TeleOp controller, sets the robot to "Turn Mode", allowing it to turn in place
    """

    def teleTurn(self):
        self.podController.teleTurn()

    """
    Method: teleMoveTurn(Speed)
    Purpose: For the TeleOp controller, allows for the robot to turn in place in "Turn Mode"
    """

    def teleMoveTurn(self, speed):
        self.wheelController.teleMoveTurn(speed)

    def teleSideways(self, speed):
        self.wheelController.teleSideways(speed)

    """
    Method: teleRotate(speed)
    Purpose: For the TeleOp controller, allows the pod motors to rotate together while maintaining the same heading
    """

    def teleRotate(self, speed):
        self.podController.teleRotate(speed)

    """
    Method: teleServoIn()
    Purpose: Closes gripper as long as the specific button is pressed
    """

    def teleServoIn(self):
        self.servoList[0].setAngle(60)

    """
    Method: teleServoOut()
    Purpose: Opens gripper
    """

    def teleServoOut(self):
        self.servoList[0].setAngle(120)


    """
    Method: horizontalMode(debug)
    Purpose: sends a command to the podController to rotate the pods so that the robot can crab
             walk
    """
    def horizontalMode(self,debug=False):
        self.podController.rotateXMotors(90,[0,2])
        self.podController.rotateXMotors(-90, [1, 3])

        # self.podController.rotatePods(-90,debug)
    def adjustForward(self,debug=False):
        self.podController.adjustForward()
