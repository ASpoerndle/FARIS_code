from MotorController import MotorController
import os
mc = MotorController()
_class = "MOTORCONTROLLER"
print(f"===Welcome to the Demo code file for {_class} class")
input("Press enter to continue")
mc.adjustForward(False)
#mc.moveOne()
#mc.faceForward(False)
def run_command(inp):
    os.system('cls' if os.name == 'nt' else 'clear')
    input(inp)
def demo1():
    run_command("Move Forward")
    mc.moveCord([0,3],True)
    input("Complete")

    run_command("Move Left")
    mc.moveCord([-1,0], True)
    input("Complete")

    run_command("Move diagonal")
    mc.moveCord([1,-1], True)

    input("Complete")
    run_command("Rotate in place")
    mc.turn(90,True)
    mc.adjustForward(True)

    input("Complete")

    run_command("Change heading while moving")
    mc.rotateXMotors(45,[2,3],False)
    mc.moveDistance(1,False,False)

    input("Complete")

def demo2():
    print(mc.getHeading())
    input(".")
    mc.turn(45,True)
    print(mc.getHeading())
    input("..")
    mc.turn(-45,True)
def demo3():
    while(True):
        mc.moveCord([0,1],True)
        input("Pause.")
        mc.moveCord([0,-1], True)
        input("Pause.")
        mc.moveCord([1,0], True)
        input("Pause.")
def demo4():
    while(True):
        mc.moveCord([0,1],True)
        mc.moveCord([1,0],True)
        mc.moveCord([0,-1],True)
        mc.moveCord([-1,0],True)
        input("Pause.")
def demoFree():
    mc.moveCord([-1,-1], False)
ind = input("Which demo?")
ind = int(ind)

if(ind == 1):
    demo1()
if(ind == 2):
    demo2()
if(ind == 3):
    demo3()
if(ind==4):
    demo4()
else:
    demoFree()
