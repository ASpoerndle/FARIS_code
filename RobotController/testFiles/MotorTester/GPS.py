import time
import board
import adafruit_gps

# Create a serial connection
import serial
RX = board.RX
TX = board.TX

uart = busio.UART(TX, RX, baudrate=9600, timeout=30)


#uart = serial.Serial("/dev/ttyTHS1", baudrate=9600, timeout=3000)
# Create a GPS module instance
gps = adafruit_gps.GPS(uart, debug=False)
while True:
    gps.update()  # Update the GPS data
    if gps.has_fix:  # Check if a fix is available
        print(f'Latitude: {gps.latitude:.6f} degrees')
        print(f'Longitude: {gps.longitude:.6f} degrees')
    else:
        print('Waiting for fix...')
    time.sleep(1)  # Wait for a second before the next update

