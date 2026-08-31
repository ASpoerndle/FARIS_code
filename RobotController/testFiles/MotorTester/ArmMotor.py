from RotationFocusedMotor import RotationFocusedMotor

class ArmMotor():
    def __init__(self,low,high,offset,pca,pin,side,enc,fval,i2c_bus):
        self.motor = RotationFocusedMotor(pca,pin,side,enc,fval,i2c_bus)
        self.low = low
        self.high = high
        self.offset = offset
    def rotate(self, angle,speed, debug=False):
                mid = (self.low + self.high)//2
                angle = mid  + (self.offset-angle)
                if(abs(angle) > abs(self.high) or abs(angle) < abs(self.low)):
                    print("ERR: Angle too high or too low")
                    self.motor.motor.moveMotor(0)
                    return True
                current_degrees = self.motor.motor.encoder.getCurrentAngle()

                # Calculate shortest directional path (-180 to 180 degrees)
                error = angle - current_degrees

                # Target absolute position for the PID
                target = current_degrees + error
                self.motor.motor.pid.setpoint = target

                # Get PID adjustment
                control_signal = self.motor.motor.pid(current_degrees)

                # Check if target is reached (deadband of 4 degrees)
                if abs(error) < 2:
                    self.motor.motor.moveMotor(0)
                    if debug:
                        print(f"Centered at {current_degrees} | kP: {self.motor.motor.pid.Kp}")
                    return True

                # Scale PID output by speed magnitude (0.0 to 1.0)
                max_power = abs(speed) * 0.75
                power = max(-max_power, min(max_power, control_signal))

                self.motor.motor.moveMotor(power)

                if debug:
                    print(f"Error: {error:.2f} | Target: {target:.2f} | Power: {power:.2f}")

                return False
    def killMotor(self):
        self.motor.motor.killMotor()
