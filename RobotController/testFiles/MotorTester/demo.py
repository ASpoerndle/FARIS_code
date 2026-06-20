from MotorController import MotorController
import os
mc = MotorController()
_class = "MOTORCONTROLLER"
print(f"===Welcome to the Demo code file for {_class} class")
input("Press enter to continue")
mc.adjustForward(True)
#mc.moveOne()
#mc.faceForward(False)
def run_command(inp):
    os.system('cls' if os.name == 'nt' else 'clear')
    input(inp)
def demo1():
    run_command("Move Forward")
    mc.moveCord([0,3],True)
    input("Complete")
    
    run_command("Move back")
    mc.moveCord([0,-3],False)
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
    path = [[.3,.3],[-.6,.3],[-.3,-.3], [.3,-.3]]
    mc.telePathClear()
    mc.writePath(path)
    mc.readPath()
    
def tele():
    while True:
        i = input("what do?")
        if(i == "f"):
            i = input("dis")
            mc.moveCord([0,float(i)], True)
        if(i=="l"):
            i = input("dis")
            mc.moveCord([float(i),0], True)
ind = input("Which demo?")
ind = int(ind)

if(ind == 1):
    demo1()
elif(ind == 2):
    demo2()
elif(ind == 3):
    demo3()
elif(ind==4):
    demo4()
elif(ind == 99):
    tele()
else:
    demoFree()
