import serial
import time
import adafruit_gps
 
PORT = "/dev/ttyUSB0"      # change on mac/linux: e.g. "/dev/ttyUSB0" or "/dev/ttyACM0"
BAUD = 9600         # common for NMEA on Adafruit Ultimate GPS

#uart = busio.UART(TX, RX, baudrate=9600, timeout=30)
uart = serial.Serial(PORT, baudrate=9600, timeout=3000)
gps = adafruit_gps.GPS(uart, debug=False)
while True:
    gps.update()  # Update the GPS data
    if gps.has_fix:  # Check if a fix is available
        print(f'Latitude: {gps.latitude:.6f} degrees')
        print(f'Longitude: {gps.longitude:.6f} degrees')
    else:
        print('Waiting for fix...')
    time.sleep(1)  # Wait for a second before the next update
with serial.Serial(PORT, BAUD, timeout=1) as ser:
    print("Reading NMEA from GPS... Ctrl+C to stop")
    while True:
        line = ser.readline().decode("ascii", errors="ignore").strip()
        if line.startswith(("$GPRMC", "$GNRMC", "$GPGGA", "$GNGGA")):
            print(line)
        time.sleep(0.01)
