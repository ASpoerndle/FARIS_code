import time
import os
import pygame
from MotorController import MotorController
# Hide the "XDG_RUNTIME_DIR" error if you are on SSH
os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()
pygame.joystick.init()
def get_default(obj,num):
    return obj.get_axis(num)
#joysticks_def = []
#joysticks_def.append(get_default(pygame.joystick.Joystick(0),0))

#joysticks_def.append(get_default(pygame.joystick.Joystick(0),1))

#joysticks_def.append(get_default(pygame.joystick.Joystick(-1),0))

#joysticks_def.append(get_default(pygame.joystick.Joystick(-1),1))

isSideways = False
if pygame.joystick.get_count() == 0:
    print("No controller found! Check the X/D switch on the back.")
else:
    
    pygame.event.pump() # Internal pygame update
    joy = pygame.joystick.Joystick(0)
    #joy2 = pygame.joystick.Joystick(1)
    joy.init()
    #joy2.init()
    print(f"Detected: {joy.get_name()} | count {pygame.joystick.get_count()} | button num | {joy.get_numbuttons()}")
    while True:
        if(joy.get_button(3)):
            print(f"This is button")
        pygame.time.wait(10) # Prevent 100% CPU usage
