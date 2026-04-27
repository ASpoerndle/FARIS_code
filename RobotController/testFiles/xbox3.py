import pygame
import os

# Hide the "XDG_RUNTIME_DIR" error if you are on SSH
os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()
pygame.joystick.init()

def get_default(obj,num):
    return obj.get_axis(num)

joysticks_def = []
joysticks_def.append(get_default(pygame.joystick.Joystick(0),0))

joysticks_def.append(get_default(pygame.joystick.Joystick(0),1))

#joysticks_def.append(get_default(pygame.joystick.Joystick(-1),0))

#joysticks_def.append(get_default(pygame.joystick.Joystick(-1),1))


if pygame.joystick.get_count() == 0:
    print("No controller found! Check the X/D switch on the back.")
else:
    joy = pygame.joystick.Joystick(0)
    joy.init()
    print(f"Detected: {joy.get_name()}")
    default = joy.get_axis(0)
    try:
        while True:
            pygame.event.pump() # Internal pygame update
            
            # Button 0 is usually 'A' on the F310 in X-mode
            if(joy.get_axis(0) != joysticks_def[0]):
                print(f"left and right {joy.get_axis(0)}")
            if(joy.get_axis(1) != joysticks_def[1]):
                print(f" up and down {joy.get_axis(1)}")


            pygame.time.wait(10) # Prevent 100% CPU usage
    except KeyboardInterrupt:
        pygame.quit()
