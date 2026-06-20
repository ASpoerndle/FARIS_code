
"""
Author: Aidan Spoerndle
Purpose: Allows the user to save and write paths for the robot to automatically take, allowing them to chain commands together to get a desired outcome.
"""
class PathController():
    FILE_NAME = "Path.txt"

    def __init__(self):
        self.file = self.openFile(PathController.FILE_NAME,"r")

    def openFile(self,file,mode):
        file = open(PathController.FILE_NAME,mode)
        return file

    def writePath(self,cords):
        #x,y = cords
        x,y = cords
        saveCords = str(x) + "," + str(y) + ";"
        self.file = self.openFile(self.file,"a")
        self.file.write(saveCords)
        self.file.close()
    
    def readPath(self):
        self.file = self.openFile(self.file,"r")
        path = self.file.read()
        p_list = path.split(";") #Now we have a list of [[x,y],[x,y],..]
        p_list = p_list[:-1]
        return p_list #Let MotorController handle turning the big list into smaller movement commands
    def clearPath(self):
        self.openFile(self.file,"w")
        self.file.close()

    def test(self):
        for i in range(9):
            cords = [i,i*2]
        
            self.writePath(cords)
            print("Path written!")
        text = self.readPath()
        print(f"The Path read back is: {text}")
        


