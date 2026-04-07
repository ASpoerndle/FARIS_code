import struct
from smbus2 import SMBus
import time
import math
from Motor import WheelMotor

class RotationalMotor():
    I2C_ADDR = 0x30
    I2C_BUS = 1
    positions = [0]*8
    velocities = [0]*8
    
    def __init__(self, pca, pin, side, enc, fVal):
        self.motor = WheelMotor(pca, pin, side)
        self.enc = enc
        self.polarity = -1 if side == "r" else 1
        self.fVal = fVal
        self.currentCount = 0 
        self.is_moving = False
        self.read_octoquad()

    def read_octoquad(self):
        try:
            with SMBus(RotationalMotor.I2C_BUS) as bus:
                all_positions = bus.read_i2c_block_data(RotationalMotor.I2C_ADDR, 0x1C, 32)
                RotationalMotor.positions = list(struct.unpack('<8i', bytes(all_positions)))
        except Exception as e:
            print(f"I2C Read Error: {e}")

    def getCurrentPosition(self):
        return RotationalMotor.positions[self.enc]

    def rotateForward(self, angle, speed):
        """
        The entry point for movement. Captures start position once
        and delegates to the internal directional methods.
        """
        self.read_octoquad()
        
        # Capture the starting point only when a new move begins
        if not self.is_moving:
            self.currentCount = self.getCurrentPosition()
            self.is_moving = True

        # Calculate absolute target in encoder counts
        target_counts = (angle * 1024) / 45
        new_pos = (target_counts * self.polarity) + self.currentCount
        
        # Delegate based on angle sign
        if angle >= 0:
            done = self._rotateRight(new_pos, abs(speed))
        else:
            done = self._rotateLeft(new_pos, abs(speed))
            
        if done:
            self.is_moving = False # Reset for the next command
        return done

    def _rotateRight(self, target, speed):
        current = self.getCurrentPosition()
        tolerance = 15 # Stops the "shaking" jitter

        if abs(current - target) < tolerance:
            self.motor.move_motor(0)
            return True

        if self.polarity > 0:
            if current < target:
                self.motor.move_motor(speed)
                return False
        else:
            # Negative Polarity: Move while current is GREATER (less negative) than target
            if current > target:
                self.motor.move_motor(speed)
                return False

        self.motor.move_motor(0)
        return True

    def _rotateLeft(self, target, speed):
        current = self.getCurrentPosition()
        tolerance = 15

        if abs(current - target) < tolerance:
            self.motor.move_motor(0)
            return True

        if self.polarity > 0:
            if current > target:
                self.motor.move_motor(-speed)
                return False
        else:
            # Negative Polarity: Move while current is LESS (more positive) than target
            if current < target:
                self.motor.move_motor(-speed)
                return False

        self.motor.move_motor(0)
        return True

    def adjustForward(self):
        self.read_octoquad()
        currentPos = self.getCurrentPosition()
        tolerance = 10
        
        if abs(currentPos - self.fVal) < tolerance:
            self.motor.move_motor(0)
            return True
        
        # Simple proportional-ish correction
        speed = 0.1 if currentPos < self.fVal else -0.1
        self.motor.move_motor(speed)
        return False

    def stopMotor(self):
        self.motor.move_motor(0)
        self.is_moving = False
