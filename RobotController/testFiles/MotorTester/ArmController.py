#from RotationFocusedMotor import RotationFocusedMotor
import math
from Servo import Servo
import torch
import numpy as np
#import modern_robotics as mr
import pytorch_mr as mr
import board
import Jetson.GPIO as GPIO
from adafruit_pca9685 import PCA9685
#import pandas as pd
#import serial
import time
from Motor import Motor
class ArmController():
    def __init__(self, armMotors, armServos):
        self.armMotors = armMotors
        """
        Motor 0 = Shoulder
        Motor 1 = Arm
        Motor 2 = Forearm
        """

        self.armServos = armServos
        """
        Servo 0 = Tilt (pitch)
        Servo 1 = Twist (roll)
        Servo 2 = Grab
        """
        self.wristPitchValues = [0,45,90,135,180,225]
        self.wristRollValues = [0,45,90,135,180,225]
        self.graspValues = [60,120]
        self.wristPitchIndex = 0
        self.wristRollIndex = 0
        self.graspIndex = 0
    def teleWristPitch(self):
        if(self.wristPitchIndex + 1 > len(self.wristPitchValues)):
            self.wristPitchIndex = 0
        print(self.wristPitchValues[self.wristPitchIndex])
        self.armServos[0].setAngle(self.wristPitchValues[self.wristPitchIndex])
        self.wristPitchIndex +=1
    def teleWristRoll(self):
        if(self.wristRollIndex + 1 > len(self.wristRollValues)):
            self.wristRollIndex = 0
        self.armServos[1].setAngle(self.wristRollValues[self.wristRollIndex])
        self.wristRollIndex += 1
    def teleGrasp(self):
        if(self.graspIndex + 1 > len(self.graspValues)):
            self.graspIndex = 0
        self.armServos[2].setAngle(self.graspValues[self.graspIndex])
        self.graspIndex += 1
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
        self.armServos[2].setAngle(60)

    """
    Method: teleServoOut()
    Purpose: Opens gripper
    """

    def teleServoOut(self):
        self.armServos[2].setAngle(120)

    def setServoAngles(self,Joint):
        for servo in range(len(self.armServos)):
            self.armServos[servo].setAngle(Joint[servo])
        time.sleep(i)
        for servo in self.armServos:
            servo.killServo()
    def setMotorSpeed(self,motor,speed):
        try:
            if(motor > 2):
                return
            self.armMotors[motor].moveMotor(speed)
        except:
            print("ERR finding motor")
    def motorSpeeds(self):
        mo1 = self.armMotors[0]
        mo2 = self.armMotors[1]
        mo3 = self.armMotors[2]
        print("ready")
        """
        mo1.moveMotor(0.01)
        time.sleep(1)
        mo1.moveMotor(-0.01)
        time.sleep(1)
        mo1.moveMotor(0)
        print("mo2")
        """
        mo2.moveMotor(0.4)
        mo3.moveMotor(-0.2)
        time.sleep(1)
        mo2.moveMotor(-0.5)
        mo3.moveMotor(0.1)
        time.sleep(1)
        mo2.moveMotor(0)
        mo3.moveMotor(0)
        mo1.moveMotor(0.01)
        time.sleep(1)
        mo1.moveMotor(-0.01)
        time.sleep(1)
        mo1.moveMotor(0)
        print("done")
    def throwaway(self):
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

        def screw_axis(omega, q):
            """Return the 6-vector screw axis [ω, v] for a revolute joint."""
            omega = np.array(omega, dtype=float)
            q     = np.array(q,     dtype=float)
            v     = -np.cross(omega, q)
            return np.concatenate([omega, v])
        L1 = .08
        L2 = .312
        L3 = .312


        M= [
            [1,0,0,L2+L3],
            [0,0,1,0],
            [0,-1,0,L1],
            [0,0,0,1]
            ]
        #omega | q
        S1 = torch.tensor(screw_axis([0,0,1],[0,0,0]))
        S1 = S1.view((6,1))
        S2 = torch.tensor(screw_axis([0,-1,0],[0,0,L1]))
        S2 = S2.view(6,1)
        S3 = torch.tensor(screw_axis([0,-1,0],[L2,0,L1]))
        S3 = S3.view(6,1)
        S4 = torch.tensor(screw_axis([0,1,0],[L2+L3,0,L1]))
        S4 = S4.view(6,1)


        # S3 = torch.tensor(screw_axis([1,0,0],[L1+L2,0,0]))
        # S3 = S3.view(6,1)
        # S4 = torch.tensor(screw_axis([0,1,0],[L1+L2+L3,0,0]))
        # S4 = S4.view(6,1)
        #Slist = torch.stack([S1.squeeze(), S2.squeeze(), S3.squeeze(), S4.squeeze()], dim=1)
        # Assuming 3-DOF based on S1, S2, S3 definitions
        Slist = torch.stack([S1, S2,S3,S4]).view(4, 6).T  # Transpose to shape (6, 3)
        #print(Slist)
        x_angle = 0
        y_angle = 0
        z_angle = 0
        # Matches the 3 degrees of freedom defined by your screw axes
        thetaList = torch.tensor([math.radians(x_angle),math.radians(y_angle),math.radians(z_angle),0],dtype=torch.float64)
        M = torch.tensor(M, dtype=torch.float64)


        output = mr.FKinSpace(M, Slist, thetaList)
        output = torch.round(output,decimals=4)
        print(output)

        # ---------------------------------------------------------------------------
        # 4.  SANITY CHECK — Forward Kinematics at home (θ = 0)
        # ---------------------------------------------------------------------------
        # FKinSpace with all-zero joint angles should return M exactly.

        theta_home = np.zeros(4)
        #M = torch.from_numpy(M)
        theta_home = torch.from_numpy(theta_home)
        T_home_check = mr.FKinSpace(M, Slist, theta_home)
        print("\n=== FK at home (all θ=0, should equal M) ===")
        print("Check is good")
        print(np.round(T_home_check, 5))


        # ---------------------------------------------------------------------------
        # 5.  DEFINE A TARGET POSE  T_desired
        # ---------------------------------------------------------------------------
        # Example: move EE 400 mm forward (along X) and 300 mm up from origin,
        # tilted 45° forward (pitch −45° about Y, i.e. pointing diagonally).
        #
        # Build the rotation matrix for 180° about X:

        x, y, z = 0.3676, -0.2122,0.2261  # target coordinates (e.g., in mm)
        pitch_deg = 10            # point gripper downward at 30 degrees

        # 2. Calculate angles in radians
        theta_y = np.arctan2(y, x)   # Base yaw is calculated automatically
        theta_p = np.radians(pitch_deg)

        # 3. Compute trig values
        cy, sy = np.cos(theta_y), np.sin(theta_y)
        cp, sp = np.cos(theta_p), np.sin(theta_p)

        # 4. Construct T_des

        # Construct T_desired matching your robot's kinematics
        yaw_matrix = np.array([
            [cy,-sy,0],
            [sy,cy,0],
            [0,0,1]

        ])

        pitch_matrix = np.array([
            [cp,0,sp],
            [0,1,0],
            [-sp,0,cp]

        ])
        M_rotation = np.array([[1,0,0],
                                [0,0,1],
                                [0,-1,0]])
        #base yaw * wrist pitch * the M matrix which is messy bc of axis of rotation
        T_test = yaw_matrix @ pitch_matrix @ M_rotation
        print(T_test, "test")
        # T_desired = np.array([
        #     [cy * cp, -cy * sp, -sy,  x],
        #     [sy * cp, -sy * sp,  cy,  y],
        #     [-sp,     -cp,       0.0, z],
        #     [0.0,      0.0,      0.0, 1.0]
        # ])
        # print(T_desired)
        # input("wait...")
        angle = np.radians(179) # avoiding singularity of 180°
        c, s = np.cos(angle), np.sin(angle)

        # T_desired = np.array([
        #     [c,  0,  -s, 0.2],
        #     [0,  1, 0, 0.2],
        #     [s,  0,  c, -.1],
        #     [0,  0,  0, 1.00]
        # ])

        print("\n=== Target pose T_desired ===")
        print(np.round(T_test, 4))
        T_desired = np.eye(4)
        T_desired[:3, :3] = T_test
        T_desired[:3, 3] = [x, y, z]
        print(T_desired)
        # ---------------------------------------------------------------------------
        # 6.  INITIAL JOINT ANGLE GUESS
        # ---------------------------------------------------------------------------
        # Starting from a slightly bent pose gives Newton-Raphson a better chance
        # of finding the physically meaningful solution (avoids the degenerate
        # straight-up singularity for this particular target).
        MAX_RAD = np.radians([70, 65, 0, 0])
        MIN_RAD = np.radians([-70, 0, -80, -80])
        def checkSafety(theta_sol):
            angles = theta_sol.flatten()
            angles = angles % np.pi/4 - np.pi/8

            for i in range(len(angles)-1):
                print(f"Joint {i} Normalized Rad: {angles[i]:.4f}")
                if angles[i] < MIN_RAD[i] or angles[i] > MAX_RAD[i]:
                    return False
            return True
        # theta_init = np.array([0.0, 0.3, -0.6, 0.0, 0.3])
        theta_init = np.array([0.1, 0.2, -0.2, 0.1])

        # ---------------------------------------------------------------------------
        # 7.  SOLVE INVERSE KINEMATICS
        # ---------------------------------------------------------------------------
        eomg = 0.0005   # angular convergence tolerance (rad)
        ev   = 0.0005 # 1e-4   # linear  convergence tolerance (m)
        T_desired = torch.from_numpy(T_desired)
        theta_init = torch.from_numpy(theta_init)

        theta_sol, success = mr.IKinSpace( # calls from file w/ 200 iterations rather than default 20
            Slist,
            M,
            T_desired,
            theta_init,
            eomg,
            ev
        )



        print("\n=== IK Result ===")
        print(f"Converged : {success}")
        print(f"θ (rad)   : {np.round(theta_sol, 5)}")

        maxAttempts = 20
        while(checkSafety(theta_sol.numpy())==False or success == False):

            print("Bad Solution: trying again.")

            theta_init = torch.tensor(np.random.uniform(MIN_RAD, MAX_RAD))

            theta_sol, success = mr.IKinSpace(  # calls from file w/ 200 iterations rather than default 20
                Slist,
                M,
                T_desired,
                theta_init,
                eomg,
                ev
            )

            if(maxAttempts <= 0):
                theta_deg = theta_sol * 180 / math.pi
                theta_deg = np.round(theta_deg, 2)
                theta_deg = theta_deg % 180
                print(theta_deg)
                raise ValueError("CANNOT REACH SPOT")
            maxAttempts -= 1
        theta_deg = theta_sol * 180/math.pi
        theta_deg = np.round(theta_deg, 2)
        theta_deg = (theta_deg+90)%180 - 90
        pot_x,pot_y,pot_z = theta_deg[0][:3]
        pot_x,pot_y,pot_z = float(pot_x),float(pot_y),float(pot_z)


        """
        ===CHECK THE POT VALUES
        """
        print(pot_x,pot_y,pot_z)
        theta_home = torch.tensor([pot_x,pot_y,pot_z,108])
        T_home_check = mr.FKinSpace(M, Slist, theta_home)
        print(T_home_check[0])
        print(x,y,z)



        print(f"θ (deg)   : {np.round(theta_deg, 2)}") # np can do math within list easier than list comprehension

        # ---------------------------------------------------------------------------
        # 8.  VERIFY — FK with IK solution should reproduce T_desired
        # ---------------------------------------------------------------------------
        # T_achieved = mr.FKinSpace(M, Slist, theta_sol)
        # print("\n=== FK verification (should match T_desired) ===")
        # print(np.round(T_achieved, 5))
        #
        # pos_err = np.linalg.norm(T_achieved[:3, 3] - T_desired[:3, 3])
        # print(f"\nPosition error : {pos_err*1000:.4f} mm")
    def killMotors(self):
        for motor in self.armMotors:
            motor.killMotor()
    def stopMotors(self):
        for motor in self.armMotors:
            motor.moveMotor(0)
"""
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
i2c = board.I2C()
pca = PCA9685(i2c)
pca.frequency = 50
motorList = [
    [12,"l",0,0],
    [13,"l",1,0],
    [14,"l",2,0]
        ]
motorObj = []
servoList = [8,9,10]
servoObj = []
for i in servoList:
    servo = Servo(pca,i)
    servoObj.append(servo)
for i in motorList:
    motor = Motor(pca,i[0],i[1])
    motorObj.append(motor)
arm = ArmController(motorObj,servoObj)
#arm.setServoAngles([30,30,30])
#time.sleep(3)
#arm.setServoAngles([0,0,0])
try:
    arm.motorSpeeds()
except KeyboardInterrupt:
    arm.killMotors()
"""
