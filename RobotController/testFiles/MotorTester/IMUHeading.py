from MotorController import MotorController

mc = MotorController()
start_heading = mc.getHeading()
while(True):
    head = mc.getHeading()
    diff = head - start_heading
    print(f"Current Heading: {head} | Start Heading: {start_heading} | Difference: {diff}")
