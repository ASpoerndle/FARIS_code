
stopCond = False
motorList = [85,78,34]
while (not stopCond):

    for motor, i in enumerate(motorList):
        print(i)
        motorList[i] = input("isRotated")
        isRotated = motorList[i] == 90
        if (isRotated):
            list.pop(i)
    stopCond = len(motorList) == 0