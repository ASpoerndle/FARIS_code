from MotorController import MotorController
import os
mc = MotorController()
_class = "MOTORCONTROLLER"
print("===Welcome to the Demo code file for {_class} class")
input("Press enter to continue")
def run_command(inp):
    os.system('cls' if os.name == 'nt' else 'clear')
    input(inp)

run_command("Move Forward")
mc.moveCord([0,1],False)
print("Complete")

run_command("Move Left")
mc.moveCord([-1,0], False)
print("Complete")

run_command("Move diagonal")
mc.moveCord([1,-1], False)
print("Complete")
run_command("Rotate in place")
mc.turn(90,False)
mc.adjustForward(False)
print("Complete")

run_command("Change heading while moving")
mc.rotateXMotors(45,[2,4],False)
mc.moveDistacne(1,False,False)
print("Complete")

