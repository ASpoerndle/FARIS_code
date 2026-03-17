import time
# Import the official DCL class (assuming it's named octoquad.py in your directory)
from octoquad import OctoQuad 

# Initialize the OctoQuad on I2C bus 1 (standard for Raspberry Pi)
# The default I2C address for the OctoQuad is usually 0x30
oq = OctoQuad(bus=1, address=0x30)

try:
    while True:
        # Read the position from Channel 0
        position = oq.read_position(0)
        velocity = oq.read_velocity(0)
        
        print(f"Encoder 0 - Pos: {position}, Vel: {velocity}")
        time.sleep(0.05) # 20Hz loop

except KeyboardInterrupt:
    print("Exiting...")
