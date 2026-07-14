#from RotationFocusedMotor import RotationFocusedMotor
import torch


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

    def teleServoIn(self):
        self.armServos[0].setAngle(60)

    """
    Method: teleServoOut()
    Purpose: Opens gripper
    """

    def teleServoOut(self):
        self.armServos[0].setAngle(120)

"""
Inverse Kinematics — 5-DOF Robot Arm
Using the Modern Robotics library (Screw Theory / Space Frame formulation)

Arm geometry (home config = all joints at 0°, arm pointing straight up):

    EE tip  ← 140 mm ← J5 (wrist, pitch about Y)
                        ← 95  mm ← J4 (forearm roll, about Z)
                                    ← 172.5 mm ← J3 (elbow pitch, about Y)
                                                   ← 221.12 mm ← J2 (shoulder pitch, about Y)
                                                                   ← 211 mm ← J1 (base yaw, about Z)
                                                                               ← origin (0,0,0)

All joints lie on the world Z-axis at home config (arm fully vertical).
Units: METRES throughout (mm values divided by 1000).

Install:
    pip install modern-robotics numpy
"""

import numpy as np
#import modern_robotics as mr
import pytorch_mr as mr
#import pandas as pd
#import serial
import time
def screw_axis(omega, q):
    """Return the 6-vector screw axis [ω, v] for a revolute joint."""
    omega = np.array(omega, dtype=float)
    q     = np.array(q,     dtype=float)
    v     = -np.cross(omega, q)
    return np.concatenate([omega, v])
L1 = 2
L2 = 3
L3 = 1.5


M= [
    [1,0,0,L1+L2+L3],
    [0,1,0,0],
    [0,0,1,0],
    [0,0,0,1]
    ]
#omega | q
S1 = torch.tensor(screw_axis([1,0,0],[0,0,0]))
S1 = S1.view((6,1))
S2 = torch.tensor(screw_axis([1,0,0],[L1,0,0]))
S2 = S2.view(6,1)
S3 = torch.tensor(screw_axis([1,0,0],[L1+L2,0,0]))
S3 = S3.view(6,1)
S4 = torch.tensor(screw_axis([0,1,0],[L1+L2+L3,0,0]))
S4 = S4.view(6,1)

# Assuming 3-DOF based on S1, S2, S3 definitions
Slist = torch.stack([S4,S3, S2, S1]).view(4, 6).T  # Transpose to shape (6, 3)

# Matches the 3 degrees of freedom defined by your screw axes
thetaList = torch.tensor([90, 0, 0],dtype=torch.float64)
M = torch.tensor(M, dtype=torch.float64)


#output = mr.FKinSpace(M, Slist, thetaList)
#print(output)


