import ikpy.chain
import numpy as np

# Load your robot from URDF or construct chain programmatically
#my_chain = ikpy.chain.Chain.from_urdf_file("Robot(1).urdf")
my_chain = ikpy.chain.Chain.from_urdf_file(
    "Robot(1).urdf",
    base_elements=["ground"],
    active_links_mask=[False, True, True, True, True, True]
)
print("Total links in ikpy chain:", len(my_chain.links))
for i, link in enumerate(my_chain.links):
    print(f"Index {i}: {link.name}")
safe_guess = [0.0] * len(my_chain.links)

for i, link in enumerate(my_chain.links):
    if link.has_rotation and link.bounds != (None, None):
        safe_guess[i] = (link.bounds[0] + link.bounds[1]) / 2.0
target_position = [0.016298,-0.004150,0.111847]

# target_mask=[True, True, True, False, False, False] forces Position-Only IK
# Instead of passing a full 3x3 orientation matrix,
# you can use orientation_mode to target just XYZ and one axis (like Z)
ik_solution = my_chain.inverse_kinematics(
    target_position=target_position,
    target_orientation=[0, 0, -1], # e.g., point the tool straight down or forward
    orientation_mode=None ,          # Tell the solver: "Align the tool's Z axis, ignore its X/Y spin"
    initial_position = safe_guess
)

print("Joint Angles (rad):", np.degrees(ik_solution))

real_position = my_chain.forward_kinematics(ik_solution)[:3, 3]

print("Target position:", target_position)
print("Reached position:", real_position)
print("Position error (meters):", np.linalg.norm(real_position - target_position))