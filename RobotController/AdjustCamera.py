class AdjustCamera:
    def __init__(self,resX, resY):
        
        self.resX = resX #848
        self.resY = resY  #480
    def setX1(self,x1):
        self.X1 = x1
    def isGoingLeft(self):
        return(self.X1 < 3/4 * (self.resX/2))
    def isGoingRight(self):
        return(self.X1 > 5/4 * (self.resX/2))
    def adjustDir(self):
           if(self.isGoingLeft()):
             print("Adjust right")
             #pass
           elif(self.isGoingRight()):
             #pass
             print("Adjust left")
           else:
               print("all good")
    