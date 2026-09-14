import math
import numpy as np
import torch
import pytorch_mr as mr
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

class IK():
    def __init__(self):
        self.MAX_RAD = np.radians([120, 155, 180, 90, 180,180]) #J3 = 250
        self.MIN_RAD = np.radians([-120, 25, -140, -90, -180,-180]) #J3 = -70


    def screw_axis(self,omega, q):
        """Return the 6-vector screw axis [ω, v] for a revolute joint."""
        omega = np.array(omega, dtype=float)
        q = np.array(q, dtype=float)
        v = -np.cross(omega, q)
        return np.concatenate([omega, v])

    def checkSafety(self,theta_sol):
            angles = theta_sol.flatten()
            # Wrap angle to [-pi, pi]
            #theta_sol[0][1] = (theta_sol[0][1] + np.pi) % (2 * np.pi) - np.pi
            #angles = np.arctan2(np.sin(angles), np.cos(angles))
            #angles[1] = (angles[1] + np.pi) % (2*np.pi) - np.pi
            for i in range(len(angles)):

                angles[i] = np.arctan2(np.sin(angles[i]),np.cos(angles[i]))
                print(angles[i], self.MIN_RAD[i], self.MAX_RAD[i])
                print(f"Joint {i} Normalized Rad: {angles[i]:.4f}")
                if angles[i] < self.MIN_RAD[i] or angles[i] > self.MAX_RAD[i]:
                    return False
            return True
    def performIK(self,x,y,z):
        L1 = .08
        L2 = .312
        L3 = .312
        L4 = .01
        L5 = 0.01
        L6= 0.01

        # M = [
        #     [1, 0, 0, L2],
        #     [0, 1, 0, 0],
        #     [0, 0, 1, L1-L3-L4],
        #     [0, 0, 0, 1]
        # ]

        M = [
            [1, 0, 0, L2+L3+L4],
            [0, 1, 0, 0],
            [0, 0, 1, L1],
            [0, 0, 0, 1]
        ]



        # omega | q
        # S1 = torch.tensor(self.screw_axis([0, 0, 1], [0, 0, 0]))
        # S1 = S1.view((6, 1))
        # S2 = torch.tensor(self.screw_axis([0, -1, 0], [0, 0, L1]))
        # S2 = S2.view(6, 1)
        # S3 = torch.tensor(self.screw_axis([0, -1, 0], [L2, 0, L1]))
        # S3 = S3.view(6, 1)
        # S4 = torch.tensor(self.screw_axis([0, -1, 0], [L2, 0, L1-L3]))
        # S4 = S4.view(6, 1)
        # S5 = torch.tensor(self.screw_axis([0, 0, 1], [L2, 0, L1-L3 -L4]))
        # S5 = S5.view(6, 1)
        # S6 = torch.tensor(self.screw_axis([0, 0, -1], [L2, 0, L1-L3 - L4]))
        # S6 = S6.view(6, 1)

        # Home Matrix M (Arm fully extended vertically)
        M = torch.tensor([
            [1.0, 0.0, 0.0, L2 + L3 + L4 + L5],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, L1 ],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=torch.float64)

        # Screw Axes
        # Updated Screw Axes definitions based on vertically stacked home config:
        S1 = torch.tensor(self.screw_axis([0, 0, 1], [0, 0, 0]))  # Base Yaw
        S2 = torch.tensor(self.screw_axis([0, 1, 0], [0, 0, L1]))  # Shoulder Pitch
        S3 = torch.tensor(self.screw_axis([0, 1, 0], [L2, 0, L1]))  # Elbow Pitch
        S4 = torch.tensor(self.screw_axis([0, 0, 1], [L3 + L2, 0, L1]))  # Wrist roll
        S5 = torch.tensor(self.screw_axis([0, 1, 0], [L2 + L3 + L4, 0, L1]))  # Wrist pitch
        S6 = torch.tensor(self.screw_axis([1, 0, 0], [L2 + L3 + L4+L5, 0, L1]))  # Wrist yaw

        Slist = torch.stack([S1, S2, S3, S4, S5,S6], dim=1)  # Shape: (6, 5)



        # Assuming 3-DOF based on S1, S2, S3 definitions
       # Slist = torch.stack([S1, S2, S3, S4, S5]).view(5, 6).T  # Shape: (6, 5)        # print(Slist)
        J1_angle = -133
        J2_angle = 101
        J3_angle = 179
        J4_angle = -46
        J5_angle = 16
        J6_angle = -58


        # Matches the 3 degrees of freedom defined by your screw axes
        #thetaList = torch.tensor([math.radians(J1_angle), math.radians(J2_angle), math.radians(J3_angle),math.radians(J4_angle),math.radians(J5_angle),math.radians(J6_angle) ], dtype=torch.float64)
        thetaList = torch.tensor([math.radians(J1_angle), math.radians(J2_angle), math.radians(J3_angle),math.radians(J4_angle),math.radians(J5_angle),J6_angle ], dtype=torch.float64)

        M = torch.tensor(M, dtype=torch.float64)

        output = mr.FKinSpace(M, Slist, thetaList)
        output = torch.round(output, decimals=4)
        print(output)

        # ---------------------------------------------------------------------------
        # 4.  SANITY CHECK — Forward Kinematics at home (θ = 0)
        # ---------------------------------------------------------------------------
        # FKinSpace with all-zero joint angles should return M exactly.

        theta_home = np.zeros(5)
        # M = torch.from_numpy(M)
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

        #x, y, z = 0.311, -0.01, 0.1  # target coordinates (e.g., in mm)
        pitch_deg = 10  # point gripper downward at 30 degrees

        # 2. Calculate angles in radians
        theta_y = np.arctan2(y, x)  # Base yaw is calculated automatically
        theta_p = np.radians(pitch_deg)
        theta_r = np.radians(pitch_deg)
        # 3. Compute trig values
        cy, sy = np.cos(theta_y), np.sin(theta_y)
        cp, sp = np.cos(theta_p), np.sin(theta_p)
        cr,sr = np.cos(theta_r), np.sin(theta_r)
        # 4. Construct T_des

        # Construct T_desired matching your robot's kinematics
        yaw_matrix = np.array([
            [cy, -sy, 0],
            [sy, cy, 0],
            [0, 0, 1]

        ])

        pitch_matrix = np.array([
            [cp, 0, sp],
            [0, 1, 0],
            [-sp, 0, cp]

        ])
        roll_matrix = np.array([
            [1,0,0],
            [0,cr,-sr],
            [0,sr,cr]
        ])
        # # Roll around Z-axis matching Joint 5
        # roll_matrix = np.array([
        #     [cr, -sr, 0],
        #     [sr, cr, 0],
        #     [0, 0, 1]
        # ])
        # roll_matrix = np.eye(3)
        M_rotation = np.array([[1, 0, 0],
                               [0, 1, 0],
                               [0, 0, 1]])
        # base yaw * wrist pitch * the M matrix which is messy bc of axis of rotation
        T_test = yaw_matrix @ pitch_matrix @ roll_matrix #@ M_rotation
        print(T_test, "test")
        # T_desired = np.array([
        #     [cy * cp, -cy * sp, -sy,  x],
        #     [sy * cp, -sy * sp,  cy,  y],
        #     [-sp,     -cp,       0.0, z],
        #     [0.0,      0.0,      0.0, 1.0]
        # ])

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

        # theta_init = np.array([0.0, 0.3, -0.6, 0.0, 0.3])
        # CHANGE THIS (6 values):
        # theta_init = np.array([0.1, 0.2, -0.2, 0.1, 0.1, 0.1])

        # TO THIS (5 values):
        theta_init = torch.tensor([
            np.arctan2(y, x),
            np.radians(30),  # J2: 30° (above min threshold)
            np.radians(-30),  # J3: -50°
            np.radians(20),  # J4: 20°
            np.radians(0),  # J5: 0°
            np.radians(0)
        ], dtype=torch.float64)

        # ---------------------------------------------------------------------------
        # 7.  SOLVE INVERSE KINEMATICS
        # ---------------------------------------------------------------------------
        eomg = 1e-3  # Angular convergence tolerance (rad)
        ev = 1e-4  # Linear convergence tolerance (m = 1 micrometer)
        T_desired = torch.from_numpy(T_desired)
        #theta_init = torch.from_numpy(theta_init)

        theta_sol, success = mr.IKinSpace(  # calls from file w/ 200 iterations rather than default 20
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

        maxAttempts = 50
        while (self.checkSafety(theta_sol.numpy()) == False or success == False):

            print("Bad Solution: trying again.")

            theta_init = torch.tensor(
                np.random.uniform(self.MIN_RAD, self.MAX_RAD, size=6),
                dtype=torch.float64
            )
            print(f"Theta_init: {theta_init}")

            theta_sol, success = mr.IKinSpace(  # calls from file w/ 200 iterations rather than default 20
                Slist,
                M,
                T_desired,
                theta_init,
                eomg,
                ev
            )

            if (maxAttempts <= 0):
                theta_deg = theta_sol * 180 / math.pi
                theta_deg = np.round(theta_deg, 2)
                theta_deg = theta_deg % 180
                print(theta_deg)
                raise ValueError("CANNOT REACH SPOT")
            maxAttempts -= 1



        theta_sol_rad = theta_sol.flatten()

        # Sanity Check FK directly in Radians
        T_check = mr.FKinSpace(M, Slist, theta_sol_rad)
        achieved_pos = T_check[:3, 3].numpy()

        #pos_error_mm = np.linalg.norm(achieved_pos - np.array([x, y, z])) * 1000

        # Convert to degrees only for final human-readable display
        theta_deg = np.degrees(theta_sol_rad.numpy())
        theta_deg = np.round(((theta_deg + 180) % 360) - 180, 4)
        J1, J2, J3, J4, J5,J6 = theta_deg[:6]
        print("=== Precision Kinematics Results ===")
        print(f"Target Position (m)   : {[x, y, z]}")
        print(f"Achieved Position (m) : {T_check[0][0][3],T_check[0][1][3],T_check[0][2][3]}")
        #print(f"Position Error        : {pos_error_mm:.4f} mm")
        print(f"Joint Angles (deg)    : {theta_deg.tolist()}")
        return([J1,J2,J3,J4,J5])


ik = IK()
# #[-0.01043669693171978, -0.0668681189417839, 0.37400001287460327]
x,y,z = 0.31,.083,.105
# #x,y,z = x*1.11,y*1.11,z*1.11
# #x * 1.08673, y * 1.0885333333333333333333333333333, z * 1.1000416666666666666666666666667
# #Real: 8.516057,38.450123,56.927524,34.767765,-0.322585
joints = ik.performIK(x,y,z)
print(joints)
