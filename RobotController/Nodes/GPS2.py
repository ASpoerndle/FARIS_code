import math

import serial
import time
import adafruit_gps
 
start = [0,0]
def GPStoCords(GPS):
    lat1,long1 = GPS
    lat2,long2 = start
    list = [lat1,long1,lat2,long2]
    for i in range(len(list)):
        list[i] = toRadians(list[i])
    lat1,long1,lat2,long2 = list
    distance = GPStoDistance(lat1,long1,lat2,long2)
    x = GPSWestEast([lat1,long1], [lat2,long2]) * 1000 #in m
    y = GPSNorthSouth([lat1,long1], [lat2,long2]) * 1000 #in m
    return x,y,distance
def GPSWestEast(GPS_cords, start_cords):
    lat1, long1 = GPS_cords
    lat2,long2 = start_cords
    r = 6371 #approx radius of world
    delta_long = long2 - long1
    dis_west_east = delta_long * r * math.cos((lat1+lat2)/2)
    return dis_west_east

def GPSNorthSouth(GPS_cords,start_cords):
    lat1,_ = GPS_cords
    lat2,_ = start_cords
    lat1 *= (180)/math.pi
    lat2 *= (180)/math.pi
    r = 111.32 #distance in km per degree of lat
    dis_north_south = (lat2 - lat1) * r
    return dis_north_south


def GPStoDistance(lat1,long1,lat2,long2):
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
def toRadians(num):
    num /=180
    num *= math.pi
    return num

PORT = "/dev/ttyUSB0"      # change on mac/linux: e.g. "/dev/ttyUSB0" or "/dev/ttyACM0"
BAUD = 9600         # common for NMEA on Adafruit Ultimate GPS

#uart = busio.UART(TX, RX, baudrate=9600, timeout=30)
uart = serial.Serial(PORT, baudrate=9600, timeout=3000)
gps = adafruit_gps.GPS(uart, debug=False)
while True:
    gps.update()  # Update the GPS data
    if gps.has_fix:  # Check if a fix is available
        if(start[0] == 0):
            start = gps.latitude,gps.longitude
        cords= [gps.latitude,gps.longitude]
        x,y,dis = GPStoCords(cords)
        print(f"X: {x}, Y: {y}, Dis: {dis}, check: {math.sqrt(x ** 2 + y ** 2)}")
        # print(f'Latitude: {gps.latitude:.6f} degrees')
        # print(f'Longitude: {gps.longitude:.6f} degrees')
    else:
        print('Waiting for fix...')
    time.sleep(1)  # Wait for a second before the next update

