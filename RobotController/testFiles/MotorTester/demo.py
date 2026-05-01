from MotorController import MotorController
import os
mc = MotorController()
_class = "MOTORCONTROLLER"
print(f"===Welcome to the Demo code file for {_class} class")
input("Press enter to continue")
mc.adjustForward(False)
def run_command(inp):
    os.system('cls' if os.name == 'nt' else 'clear')
    input(inp)
def demo1():
    run_command("Move Forward")
    mc.moveCord([0,1],True)
    input("Complete")

    run_command("Move Left")
    mc.moveCord([-1,0], True)
    input("Complete")

    run_command("Move diagonal")
    mc.moveCord([1,1], True)

    input("Complete")
    run_command("Rotate in place")
    mc.turn(90,False)
    mc.adjustForward(False)

    input("Complete")

    run_command("Change heading while moving")
    mc.rotateXMotors(45,[2,3],False)
    mc.moveDistance(1,False,False)

    input("Complete")

def demo2():
    input(".")
    mc.rotatePods(45,False)
    input("..")
    mc.adjustForward(False)

ind = input("Which demo?")
if(int(ind) == 1):
    demo1()
else:
    demo2()

