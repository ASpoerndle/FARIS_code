
stopCond = False
motorList = [85,78,34]
while (not stopCond):

    for i,motor in enumerate(motorList):
        print(i)
        motorList[i] = int(input("isRotated"))
        isRotated = motorList[i] == 90
        print(isRotated)
        if (isRotated):
            motorList.pop(i)
    stopCond = len(motorList) == 0