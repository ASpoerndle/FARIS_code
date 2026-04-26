import pygame
import os
import time
from MotorController import MotorController
# Hide the "XDG_RUNTIME_DIR" error if you are on SSH
os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()
pygame.joystick.init()
time.sleep(3)
def get_default(obj,num):
    return obj.get_axis(num)
mc = MotorController()
#joysticks_def = []
#joysticks_def.append(get_default(pygame.joystick.Joystick(0),0))

#joysticks_def.append(get_default(pygame.joystick.Joystick(0),1))

#joysticks_def.append(get_default(pygame.joystick.Joystick(-1),0))

#joysticks_def.append(get_default(pygame.joystick.Joystick(-1),1))

isSideways = False
if pygame.joystick.get_count() == 0:
    print("No controller found! Check the X/D switch on the back.")
else:

    joy = pygame.joystick.Joystick(0)
    #joy2 = pygame.joystick.Joystick(1)
    joy.init()
    #joy2.init()
    isTurn = False
    print(f"Detected: {joy.get_name()} | count {pygame.joystick.get_count()}")
    default = joy.get_axis(0)
    try:
        while True:
            pygame.event.pump() # Internal pygame update

            # Button 0 is usually 'A' on the F310 in X-mode
            if(abs(joy.get_axis(0)) >= 0.2 and isSideways and not isTurn):
                #print(f"left and right {joy.get_axis(0)}")
                mc.teleForward(joy.get_axis(0)/2)
            elif(abs(joy.get_axis(1)) >= 0.2 and not isSideways and not isTurn):
                mc.teleForward(-joy.get_axis(1)/2)
                #print(f" up and down {joy.get_axis(1)}")
            elif(joy.get_button(0) and not isSideways):
                mc.horizontalMode(False)
                isSideways = True
            elif(joy.get_button(1) and (isSideways or isTurn)):
                mc.adjustForward(False)
                isSideways = False
                isTurn = False
            elif(joy.get_button(3)):
                mc.rotatePods(-45,False)
                mc.adjustForward(False)
                break
            elif(joy.get_button(2) and not isTurn):
                isTurn = True
                mc.teleTurn()
                continue
            elif(abs(joy.get_axis(2)) >= 0.2 and isTurn and not isSideways):
                mc.teleMoveTurn(joy.get_axis(2)/2)
            else:
                mc.teleForward(0)
            pygame.time.wait(10) # Prevent 100% CPU usage
    except KeyboardInterrupt:
        pygame.quit()
