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


def screw_axis(omega, q):
    """Return the 6-vector screw axis [ω, v] for a revolute joint."""
    omega = np.array(omega, dtype=float)
    q = np.array(q, dtype=float)
    v = -np.cross(omega, q)
    return np.concatenate([omega, v])


L1 = .08
L2 = .312
L3 = .312
L4 = .01

M = [
    [1, 0, 0, L2],
    [0, 1, 0, 0],
    [0, 0, 1, L1-L3-L4],
    [0, 0, 0, 1]
]
# omega | q
S1 = torch.tensor(screw_axis([0, 0, 1], [0, 0, 0]))
S1 = S1.view((6, 1))
S2 = torch.tensor(screw_axis([0, -1, 0], [0, 0, L1]))
S2 = S2.view(6, 1)
S3 = torch.tensor(screw_axis([0, -1, 0], [L2, 0, L1]))
S3 = S3.view(6, 1)
S4 = torch.tensor(screw_axis([0, 0, -1], [L2, 0, L1-L3]))
S4 = S4.view(6, 1)
S5 = torch.tensor(screw_axis([0, -1, 0], [L2, 0, L1-L3]))
S5 = S5.view(6, 1)
S6 = torch.tensor(screw_axis([0, 0, -1], [L2, 0, L1-L3 - L4]))
S6 = S6.view(6, 1)

# S3 = torch.tensor(screw_axis([1,0,0],[L1+L2,0,0]))
# S3 = S3.view(6,1)
# S4 = torch.tensor(screw_axis([0,1,0],[L1+L2+L3,0,0]))
# S4 = S4.view(6,1)
# Slist = torch.stack([S1.squeeze(), S2.squeeze(), S3.squeeze(), S4.squeeze()], dim=1)
# Assuming 3-DOF based on S1, S2, S3 definitions
Slist = torch.stack([S1, S2, S3, S4, S5, S6]).view(6, 6).T  # Transpose to shape (6, 3)
# print(Slist)
J1_angle = -133
J2_angle = 101
J3_angle = 179
J4_angle = -46
J5_angle = 16
J6_angle = -58


# Matches the 3 degrees of freedom defined by your screw axes
thetaList = torch.tensor([math.radians(J1_angle), math.radians(J2_angle), math.radians(J3_angle),math.radians(J4_angle),math.radians(J5_angle),math.radians(J6_angle) ], dtype=torch.float64)
M = torch.tensor(M, dtype=torch.float64)

output = mr.FKinSpace(M, Slist, thetaList)
output = torch.round(output, decimals=4)
print(output)

# ---------------------------------------------------------------------------
# 4.  SANITY CHECK — Forward Kinematics at home (θ = 0)
# ---------------------------------------------------------------------------
# FKinSpace with all-zero joint angles should return M exactly.

theta_home = np.zeros(6)
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

x, y, z = 0.232, -0.214, 0.099  # target coordinates (e.g., in mm)
pitch_deg = 10  # point gripper downward at 30 degrees

# 2. Calculate angles in radians
theta_y = np.arctan2(y, x)  # Base yaw is calculated automatically
theta_p = np.radians(pitch_deg)

# 3. Compute trig values
cy, sy = np.cos(theta_y), np.sin(theta_y)
cp, sp = np.cos(theta_p), np.sin(theta_p)
cr,sr = np.cos(np.radians(45)), np.sin(np.radians(45))
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

M_rotation = np.array([[1, 0, 0],
                       [0, 1, 0],
                       [0, 0, 1]])
# base yaw * wrist pitch * the M matrix which is messy bc of axis of rotation
T_test = yaw_matrix @ pitch_matrix @ roll_matrix @ M_rotation
print(T_test, "test")
# T_desired = np.array([
#     [cy * cp, -cy * sp, -sy,  x],
#     [sy * cp, -sy * sp,  cy,  y],
#     [-sp,     -cp,       0.0, z],
#     [0.0,      0.0,      0.0, 1.0]
# ])
# print(T_desired)
# input("wait...")
angle = np.radians(179)  # avoiding singularity of 180°
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
MAX_RAD = np.radians([70, 180, 90, 0,90,60])
MIN_RAD = np.radians([-70, -10, -40, -30,-45,120])


def checkSafety(theta_sol):
    angles = theta_sol.flatten()
    angles = angles % np.pi / 4 - np.pi / 8

    for i in range(len(angles) - 1):
        print(f"Joint {i} Normalized Rad: {angles[i]:.4f}")
        if angles[i] < MIN_RAD[i] or angles[i] > MAX_RAD[i]:
            return False
    return True


# theta_init = np.array([0.0, 0.3, -0.6, 0.0, 0.3])
theta_init = np.array([0.1, 0.2, -0.2, 0.1,0.1,0.1])

# ---------------------------------------------------------------------------
# 7.  SOLVE INVERSE KINEMATICS
# ---------------------------------------------------------------------------
eomg = 0.0005  # angular convergence tolerance (rad)
ev = 0.0005  # 1e-4   # linear  convergence tolerance (m)
T_desired = torch.from_numpy(T_desired)
theta_init = torch.from_numpy(theta_init)

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

maxAttempts = 20
while (checkSafety(theta_sol.numpy()) == False or success == False):

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

    if (maxAttempts <= 0):
        theta_deg = theta_sol * 180 / math.pi
        theta_deg = np.round(theta_deg, 2)
        theta_deg = theta_deg % 180
        print(theta_deg)
        raise ValueError("CANNOT REACH SPOT")
    maxAttempts -= 1
theta_deg = theta_sol * 180 / math.pi
theta_deg = np.round(theta_deg, 2)
# theta_deg = theta_deg % 180
for i in range(len(theta_deg[0])):
    theta_deg[0][i] = ((theta_deg[0][i] + 180) %360) - 180
    theta_deg[0][i] = float(theta_deg[0][i])
J1,J2,J3,J4,J5,J6 = theta_deg[0][:6]

#J1,J2,J3,J4,J5,J6 = float(J1),float(J2),float(J3),float(J4),float(J5),float(J6)
"""
===CHECK THE POT VALUES
"""
print(J1,J2,J3,J4,J5,J6)
theta_home = torch.tensor([J1,J2,J3,J4,J5,J6])
T_home_check = mr.FKinSpace(M, Slist, theta_home)
print(T_home_check[0])
print(x, y, z)

print(f"θ (deg)   : {np.round(theta_deg, 2)}")  # np can do math within list easier than list comprehension

# ---------------------------------------------------------------------------
# 8.  VERIFY — FK with IK solution should reproduce T_desired
# ---------------------------------------------------------------------------
# T_achieved = mr.FKinSpace(M, Slist, theta_sol)
# print("\n=== FK verification (should match T_desired) ===")
# print(np.round(T_achieved, 5))
#
# pos_err = np.linalg.norm(T_achieved[:3, 3] - T_desired[:3, 3])
# print(f"\nPosition error : {pos_err*1000:.4f} mm")
