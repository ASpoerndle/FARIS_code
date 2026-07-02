import math

import serial
import time
import adafruit_gps

start = [0, 0]

class WaypointController():
    PORT = "/dev/ttyUSB0"  # change on mac/linux: e.g. "/dev/ttyUSB0" or "/dev/ttyACM0"


    def __init__(self):
        uart = serial.Serial(WaypointController.PORT, baudrate=9600, timeout=3000)
        self.gps = adafruit_gps.GPS(uart, debug=False)
        self.waypoints = []
    def GPStoCords(self,waypoint, current):
        lat1, long1 = waypoint
        lat2, long2 = current
        list = [lat1, long1, lat2, long2]
        for i in range(len(list)):
            list[i] = self.toRadians(list[i])
        lat1, long1, lat2, long2 = list
        distance = self.GPStoDistance(lat1, long1, lat2, long2)
        x = self.GPSWestEast([lat1, long1], [lat2, long2]) * 1000  # in m
        y = self.GPSNorthSouth([lat1, long1], [lat2, long2]) * 1000  # in m
        return x, y


    def GPSWestEast(self,waypoint_cords, current_cords):
        lat1, long1 = waypoint_cords
        lat2, long2 = current_cords
        r = 6371  # approx radius of world
        delta_long = long2 - long1
        dis_west_east = delta_long * r * math.cos((lat1 + lat2) / 2)
        return dis_west_east


    def GPSNorthSouth(self,waypoint_cords, current_cords):
        lat1, _ = waypoint_cords
        lat2, _ = current_cords
        lat1 *= (180) / math.pi
        lat2 *= (180) / math.pi
        r = 111.32  # distance in km per degree of lat
        dis_north_south = (lat2 - lat1) * r
        return dis_north_south


    def GPStoDistance(self,lat1, long1, lat2, long2):
        # Formula d=2*[7] radius_of_world * [6] arcsin( [5]sqrt( [1] sin**2(lat2-lat1/2) + [2] cos(lat1) * [3] cos(lat2) * [4] sin**2( long2-long1 / 2) )  )
        lat_diff = lat2 - lat1
        long_diff = long2 - long1
        radius_of_world = 6371  # in km
        a_1 = math.sin(lat_diff / 2) ** 2
        a_2 = a_1 + math.cos(lat1)
        a_3 = a_2 * math.cos(lat2)
        a_4 = a_3 * math.sin(long_diff / 2) ** 2
        a_5 = math.sqrt(a_4)
        a_6 = math.asin(a_5)
        a_7 = a_6 * radius_of_world
        distance = 2 * a_7
        return distance


    def toRadians(self,num):
        num /= 180
        num *= math.pi
        return num
    def getCurrentCords(self):
        gps = self.gps

        if(self.gps.has_fix):
            return [gps.latitude,gps.longitude]
        else:
            print("ERR: GPS does not have a fix on a satellite, please try again in a bit")
    def setWaypoint(self):
        currentCords = self.getCurrentCords()
        if(currentCords != None):
            self.waypoints.append(currentCords)
            print(self.waypoints)

    def travelToWaypoint(self,num):
        if(len(self.waypoints) > num + 1):
            current_cords = self.getCurrentCords()
            waypoint_cords = self.waypoints[num]
            x,y = self.GPStoCords(waypoint_cords,current_cords)
            return x,y
        else:
            print("ERR: number of waypoints is lower than the number input. Please try again.")
            return None
    def printWaypointCords(self):
        for i in range(len(self.waypoints)):
            x = self.waypoints[i][0]
            y = self.waypoints[i][1]
            print(f"Waypoint {i} X: {x} | Y: {y}")
    def updateGPS(self):
        while True:
            self.gps.update()
            time.sleep(1)



