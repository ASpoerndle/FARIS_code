import math
import numpy as np


class AnalyticalIK5DOF:
    def __init__(self):
        # Link lengths in meters based on your URDF and script
        self.L1 = 0.08  # Base to Shoulder Pitch height
        self.L2 = 0.312  # Upper Arm length
        self.L3 = 0.312  # Forearm length


        # Wrist and Gripper combined length (L4 + L5)
        # This is the distance from the WristPitch joint to the end of the tool
        self.L_EE = 0.01 + 0.01

        # Joint limits for safety verification (in radians)
        self.limits = [
            (-2.094, 2.094),  # J1: Shoulder Yaw
            (0.471, 2.617),  # J2: Upper Arm Pitch
            (-2.967, 2.967),  # J3: Forearm Pitch
            (-1.570, 1.570),  # J4: Wrist Pitch
            (-3.141, 3.141)  # J5: Wrist Roll
        ]

    def solve(self, x, y, z, target_pitch_deg=0.0, elbow_up=True):
        """
        Solves 5-DOF IK analytically.

        :param x, y, z: Target coordinates of the gripper tip (meters).
        :param target_pitch_deg: The angle of the gripper relative to the horizontal floor.
                                 (0 = pointing straight forward, -90 = pointing straight down)
        :param elbow_up: Boolean to choose between the two valid kinematic solutions.
        :return: Array of 5 joint angles in radians.
        """
        # -----------------------------------------------------------
        # 1. Base Yaw (J1)
        # -----------------------------------------------------------
        J1 = math.atan2(y, x)

        # -----------------------------------------------------------
        # 2. Planar Projection
        # -----------------------------------------------------------
        # Convert the 3D problem into a 2D planar problem (R, Z) aligned with the arm
        R_target = math.sqrt(x ** 2 + y ** 2)
        Z_target = z - self.L1  # Shift Z axis to the shoulder joint

        # -----------------------------------------------------------
        # 3. Kinematic Decoupling (Find the Wrist Center)
        # -----------------------------------------------------------
        pitch_rad = math.radians(target_pitch_deg)

        # Calculate where the wrist joint MUST be to allow the gripper
        # to reach the target point at the specified angle
        R_wrist = R_target - self.L_EE * math.cos(pitch_rad)
        Z_wrist = Z_target - self.L_EE * math.sin(pitch_rad)

        # -----------------------------------------------------------
        # 4. Law of Cosines for Shoulder (J2) and Elbow (J3)
        # -----------------------------------------------------------
        # Distance squared from shoulder to wrist
        D_sq = R_wrist ** 2 + Z_wrist ** 2
        D = math.sqrt(D_sq)

        # Check for physical reachability (cannot stretch further than L2+L3)
        if D > (self.L2 + self.L3) or D < abs(self.L2 - self.L3):
            raise ValueError(f"Target {x}, {y}, {z} is physically out of reach!")

        # Calculate Elbow Angle using Law of Cosines
        cos_j3 = (D_sq - self.L2 ** 2 - self.L3 ** 2) / (2 * self.L2 * self.L3)
        # Clamp to avoid floating point errors slightly exceeding [-1, 1]
        cos_j3 = max(-1.0, min(1.0, cos_j3))

        if elbow_up:
            J3 = -math.acos(cos_j3)
        else:
            J3 = math.acos(cos_j3)

        # Calculate Shoulder Angle
        alpha = math.atan2(Z_wrist, R_wrist)
        beta = math.atan2(self.L3 * math.sin(J3), self.L2 + self.L3 * math.cos(J3))
        J2 = alpha - beta

        # -----------------------------------------------------------
        # 5. Wrist Pitch (J4)
        # -----------------------------------------------------------
        # In a planar chain, the sum of all joint angles equals the final global pitch
        # Target Pitch = J2 + J3 + J4
        J4 = pitch_rad - (J2 + J3)

        # -----------------------------------------------------------
        # 6. Wrist Roll (J5)
        # -----------------------------------------------------------
        # Since crop-picking is rotationally symmetric, we default to 0
        J5 = 0.0

        # Compile solution
        solution = [J1, J2, J3, J4, J5]

        # Safety Check against URDF limits
        for i, (angle, (lower, upper)) in enumerate(zip(solution, self.limits)):
            if not (lower <= angle <= upper):
                print(
                    f"Warning: Joint {i + 1} angle {math.degrees(angle):.2f}° is outside bounds [{math.degrees(lower):.2f}°, {math.degrees(upper):.2f}°]")

        return solution


# --- Example Usage ---
if __name__ == "__main__":
    ik_solver = AnalyticalIK5DOF()

    # Target: 30cm forward, 10cm left, 5cm down (relative to base)
    target_x = 0.3
    target_y = 0.3
    target_z = .3

    # We want the gripper to point downward at a 30-degree angle to grab the crop
    target_pitch = 45

    try:
        angles_rad = ik_solver.solve(target_x, target_y, target_z, target_pitch, elbow_up=True)
        angles_deg = [math.degrees(a) for a in angles_rad]

        print(f"Target (X, Y, Z): {target_x}, {target_y}, {target_z}")
        print(f"Target Pitch: {target_pitch}°")
        print(f"Calculated Angles (deg): {[round(a, 2) for a in angles_deg]}")

    except ValueError as e:
        print(f"IK Failed: {e}")