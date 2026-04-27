from xbox_controller import XboxController
import time

# Create controller instance
controller = XboxController()

# Connect to controller
controller.connect()

# Get controller info
info = controller.get_controller_info()
print(f"Connected to: {info['name']}")
print("crap")
# Read controller state
while True:
    state = controller.update_state()
    print(f"Left Stick: {state['left_joystick']}")
    print(f"Right Stick: {state['right_joystick']}")
    print(f"Triggers: {state['triggers']}")
    print(f"Buttons: {state['pressed_buttons']}")
    time.sleep(0.1)

# Disconnect when done
controller.disconnect()
