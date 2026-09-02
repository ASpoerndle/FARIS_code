import math
"""
Author: Aidan Spoerndle
Purpose: Allows the user to save and write paths for the robot to automatically take, allowing them to chain commands together to get a desired outcome.
"""
class PathController():
    FILE_NAME = "Path.txt"

    def __init__(self):
        self.file = self.openFile(PathController.FILE_NAME,"r")

    def openFile(self, file, mode):
        file = open("Path.txt", mode)
        return file

    def writePath(self,cords):
        #x,y = cords
        x,y,a = cords
        saveCords = str(x) + "," + str(y) + "," + str(a) +  ";"
        self.file = self.openFile(self.file,'a')
        self.file.write(saveCords)
        self.closeFile(self.file)
    def closeFile(self, file):
        file.close()
    def readPath(self):
        self.file = self.openFile(self.file,'r')
        path = self.file.read()
        p_list = path.split(";") #Now we have a list of [[x,y],[x,y],..]
        p_list = p_list[:-1]
        return p_list #Let MotorController handle turning the big list into smaller movement commands
    def clearPath(self):
        self.openFile(self.file,'w')
        self.closeFile(self.file)

    def test(self):
        for i in range(9):
            cords = [i,i*2]
        
            self.writePath(cords)
            print("Path written!")
        text = self.readPath()
        print(f"The Path read back is: {text}")

    def ticksToMeters(self, ticks, debug=False):

        cir = math.pi * 0.192
        # self.rotatePods(0,.5)
        distance = (ticks / 1425.1) * cir
        if (debug):
            print(f"Tick of WheelMotor 0: {ticks} | distance (m): {distance}")
        return distance
        


