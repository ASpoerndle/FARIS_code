import struct
import smbus2
from smbus2 import i2c_msg
import math



class Encoder():
    I2C_ADDR = 0x30



    def __init__(self,enc, forwardVal, bus):
        self.encoder = enc
        self.initHardware()
        self.forwardValue = forwardVal
        self.I2C_BUS = bus
        self.bus = smbus2.SMBus(self.I2C_BUS)
    def initHardware(self):
            # ===Format for manipulating registers===
            """
            I2C Address:               0x30
            Access a command register: 0x04
            Set parameter:             0x01

            Example: set the command register to allow wrapping of abs encoders
            bus.write_i2c_block_data(0x30,0x04,[0x01,0x05,0xF0])

            """
            # Allow wrapping (0x05) of all absolute encoders (0xF0)
            self.bus.write_i2c_block_data(0x30, 0x04, [0x01, 0x05, 0xF0])

            # Set bank mode for encoders to 2 to allow ports 4-7 to be abs and 0-3 to be quadrature
            self.bus.write_i2c_block_data(0x30, 0x04, [0x01, 0x02, 2])

            # set min and max values for abs encoders (from 1-1024 based on REV ThroughBore encoder specs)
            if (self.encoder >= 4):
                # [Cmd, ParamID, Channel, Min_L, Min_H, Max_L, Max_H]
                self.bus.write_i2c_block_data(0x30, 0x04, [0x01, 0x04, self.encoder, 1, 0, 0, 4])
                self.bus.write_i2c_block_data(0x30, 0x04, [0x01, 0x05, 0xF0])
                # bus.write_i2c_block_data(0x30, 0x04, [0x01, 0x05, self.encoder, 0])



            print(f"Encoder Port {self.encoder} Ready!")

    """
    Method: readOctoquad()
    Purpose: returns a list of all of the current positions of the absolute and relative encoders
    """

    def getEncoderPosition(self):
        """Uses atomic I2C transactions to prevent data byte-shifting"""
        # Read 32 bytes (8 channels * 4 bytes each)
        write = i2c_msg.write(0x30, [0x1C])
        read = i2c_msg.read(0x30, 32)
        self.bus.i2c_rdwr(write, read)

        # Unpack as 8 signed 32-bit integers
        positions = struct.unpack('<8i', bytes(list(read)))
        return positions[self.encoder]

    def getCurrentAngle(self):
        currentPos = self.getEncoderPosition()
        currentDeg = (self.forwardValue-currentPos - 1) / 1023 * 360
        #forward = (self.forwardValue - 1) / 1023 * 360 % 360
        #currentDeg -= forward
        print(f"Encoder: {self.encoder} | fVal {self.forwardValue} | current {currentDeg}")
        return currentDeg

    def getCurrentHeading(self):
        data = self.bus.read_i2c_block_data(0x30, 0x18, 2)
        raw_heading = struct.unpack('<h', bytes(data))[0]
        headingRad = raw_heading / 5000.0
        headingDeg = headingRad * 180 / math.pi
        return headingDeg
    """
    Method: resetEncoder()
    Purpose: resets the relative quadrature encoder values for the wheel motors
    """
    def resetEncoder(self):
        self.bus.write_i2c_block_data(0x30, 0x04, [0x15, 0x0F])
