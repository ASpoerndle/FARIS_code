from xbox import Joystick

joy = Joystick()

while True:
    print(f"Joy Left X: {joy.leftX} | Joy Left Y: {joy.leftY}")