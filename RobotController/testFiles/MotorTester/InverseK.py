# file import -- MR code code from Github (able to change max iterations for IK)
#import MR_coreCode


# ---------------------------------------------------------------------------
# 1.  LINK LENGTHS  (metres)
# ---------------------------------------------------------------------------
L1 = 0.211       # base      → J2  (211.00 mm)
L2 = 0.22112     # J2        → J3  (221.12 mm)
L3 = 0.1725      # J3        → J4  (172.50 mm)
L4 = 0.095       # J4        → J5  ( 95.00 mm)
L5 = 0.180 #for pen -- 0.045 for 4M w/o EE # 0.140 for 4M w/ EE       # J5        → EE  (140.00 mm)

# Cumulative heights along Z at home config
z1 = 0.0                          # J1  at origin
z2 = z1 + L1                      # J2  = 0.211   m
z3 = z2 + L2                      # J3  = 0.43212 m
z4 = z3 + L3                      # J4  = 0.60462 m
z5 = z4 + L4                      # J5  = 0.69962 m
z_ee = z5 + L5                    # EE  = 0.83962 m


# ---------------------------------------------------------------------------
# 2.  HOME CONFIGURATION MATRIX  M
# ---------------------------------------------------------------------------
# M is the 4x4 SE(3) pose of the EE in the space frame when θ = [0,0,0,0,0].
#
# At home the arm is vertical, so the EE sits directly above the origin:
#   position = (0, 0, z_ee)
#   orientation = identity  (EE frame aligned with space frame)

M = np.array([
    [1, 0, 0, 0     ],
    [0, 1, 0, 0     ],
    [0, 0, 1, z_ee  ],
    [0, 0, 0, 1     ]
], dtype=float)



# ---------------------------------------------------------------------------
# 3.  SCREW AXES  Slist  (space frame)
# ---------------------------------------------------------------------------
# For a revolute joint:  S = [ω,  v]  where  v = −ω × q
#   ω = unit rotation axis (in space frame, at home config)
#   q = any point on the joint axis (in space frame, at home config)
#
# Because every joint axis passes through (0, 0, zN) and the arm is vertical:
#   − J1 rotates about world Z through the origin  →  ω=[0,0,1], q=(0,0,0)  →  v=[0,0,0]
#   − J2, J3, J5 all pitch about Y                →  ω=[0,1,0], q=(0,0,zN) →  v=[zN,0,0]
#     (−ω × q = −[0,1,0] × [0,0,zN] = −[−zN,0,0] = [zN,0,0])
#   − J4 rolls about Z (forearm spin, same as J1 axis at home) →  v=[0,0,0]
#
# Note: J4 and J1 have the same screw axis at home — that is expected and
# correct. Their effect differs once the arm has moved away from home,
# because the Newton-Raphson solver works in the CURRENT (not home) config.

def screw_axis(omega, q):
    """Return the 6-vector screw axis [ω, v] for a revolute joint."""
    omega = np.array(omega, dtype=float)
    q     = np.array(q,     dtype=float)
    v     = -np.cross(omega, q)
    return np.concatenate([omega, v])

S1 = screw_axis([0, 0, 1], [0, 0, z1])   # base yaw      (about Z, origin)
S2 = screw_axis([0, 1, 0], [0, 0, z2])   # shoulder pitch (about Y, z=z2)
S3 = screw_axis([0, 1, 0], [0, 0, z3])   # elbow pitch    (about Y, z=z3)
S4 = screw_axis([0, 0, 1], [0, 0, z4])   # forearm roll   (about Z, z=z4)
S5 = screw_axis([0, 1, 0], [0, 0, z5])   # wrist pitch    (about Y, z=z5)

# Slist: shape (6, 5) — each column is one joint's screw axis

Slist = np.column_stack([S1, S2, S3, S4, S5])
Slist = torch.from_numpy(Slist)
print("=== Robot Definition ===")
print(f"\nEE height at home config: {z_ee*1000:.2f} mm ({z_ee:.5f} m)")
# print("\nM (home config of EE in space frame):\n", np.round(M, 5))
# print("\nSlist (columns = screw axes S1..S5):\n", np.round(Slist, 5))


# ---------------------------------------------------------------------------
# 4.  SANITY CHECK — Forward Kinematics at home (θ = 0)
# ---------------------------------------------------------------------------
# FKinSpace with all-zero joint angles should return M exactly.

theta_home = np.zeros(5)
M = torch.from_numpy(M)
theta_home = torch.from_numpy(theta_home)
T_home_check = mr.FKinSpace(M, Slist, theta_home)
print("\n=== FK at home (all θ=0, should equal M) ===")
print("Check is good")
# print(np.round(T_home_check, 5))


# ---------------------------------------------------------------------------
# 5.  DEFINE A TARGET POSE  T_desired
# ---------------------------------------------------------------------------
# Example: move EE 400 mm forward (along X) and 300 mm up from origin,
# tilted 45° forward (pitch −45° about Y, i.e. pointing diagonally).
#
# Build the rotation matrix for 180° about X:

angle = np.radians(179) # avoiding singularity of 180°
c, s = np.cos(angle), np.sin(angle)

T_desired = np.array([
    [c,  0,  -s, -0.35],
    [0,  1, 0, 0.25],
    [s,  0,  c, 0.05],
    [0,  0,  0, 1.00]
])

print("\n=== Target pose T_desired ===")
print(np.round(T_desired, 4))


# ---------------------------------------------------------------------------
# 6.  INITIAL JOINT ANGLE GUESS
# ---------------------------------------------------------------------------
# Starting from a slightly bent pose gives Newton-Raphson a better chance
# of finding the physically meaningful solution (avoids the degenerate
# straight-up singularity for this particular target).

# theta_init = np.array([0.0, 0.3, -0.6, 0.0, 0.3])
theta_init = np.zeros(5)

# ---------------------------------------------------------------------------
# 7.  SOLVE INVERSE KINEMATICS
# ---------------------------------------------------------------------------
eomg = 0.005   # angular convergence tolerance (rad)
ev   = 0.005 # 1e-4   # linear  convergence tolerance (m)
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
theta_deg = np.degrees(theta_sol)
theta_deg = np.round(theta_deg, 2)

# theta_deg = (theta_deg + 180) % 360 - 180

print(f"θ (deg)   : {np.round(theta_deg, 2)}") # np can do math within list easier than list comprehension

# ---------------------------------------------------------------------------
# 8.  VERIFY — FK with IK solution should reproduce T_desired
# ---------------------------------------------------------------------------
T_achieved = mr.FKinSpace(M, Slist, theta_sol)
print("\n=== FK verification (should match T_desired) ===")
print(np.round(T_achieved, 5))

pos_err = np.linalg.norm(T_achieved[:3, 3] - T_desired[:3, 3])
print(f"\nPosition error : {pos_err*1000:.4f} mm")

# ---------------------------------------------------------------------------
# USAGE NOTES
# ---------------------------------------------------------------------------
# • All lengths and positions are in METRES.
# • T_desired must be a valid SE(3) matrix:
#     − top-left 3×3 must be a rotation matrix (det = +1, columns orthonormal)
#     − bottom row must be [0, 0, 0, 1]
# • If IK returns success=False, try:
#     1. A different theta_init (the solver is sensitive to starting guess)
#     2. Check the target is actually reachable (within the arm's workspace)
#     3. Tighten eomg / ev slightly (1e-3 is usually sufficient)
# • J4 (forearm roll) does not affect EE position, only orientation.
#   For a pure position target you can fix theta[3] = 0 and solve a 4-DOF
#   sub-problem, or let the solver use it to satisfy orientation constraints.




# ---------------------------------------------------------------------------
# Now for sending to Arduino:
# sending over serial
# ---------------------------------------------------------------------------


GEAR_RATIO = [8.84, 5.1046, 4.0585774*5.0, 5.0, 8.066] # 9.05mm, 80mm diameter ---- 23.9mm, 122mm diameter ---- 23.9mm, 97mm diameter --radial unimportant-- 9.05mm, 73mm

MICROSTEPS = [16, 32, 4, 16, 8]

correctionFactor = [1.13, 1.05, 1.1, 1.055, 1.1]

STEPS_PER_DEG = [
    200 * MICROSTEPS[i] * GEAR_RATIO[i] / 360 * correctionFactor[i]
    for i in range(5)
]

step_targets = [
    round(theta_deg[i] * STEPS_PER_DEG[i])
    for i in range(5)
]


PORT = r'\\.\COM10'
BAUD = 115200

#ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

print(theta_deg)
print(type(theta_deg))

def send_steps(step_targets):
    msg = ",".join(str(x) for x in step_targets) + "\n"
   # ser.write(msg.encode())
    print(msg.strip())

# Send once
send_steps(step_targets)

time.sleep(10)

# Home is absolute position 0, not -step_targets
home = [0, 0, 0, 0, 0]
send_steps(home)

