from MotorWithEncoder import MotorWithEncoder

class RotationFocusedMotor():
   def __init__(self, pca, pin, side, enc, fVal,i2c_bus):
       self.motor = MotorWithEncoder(pca, pin, side, enc, fVal,i2c_bus)

   def rotate(self, angle, speed, debug=False):
       current_degrees = self.getCurrentAngle()

       # Calculate shortest directional path (-180 to 180 degrees)
       error = (angle - (current_degrees % 360) + 180) % 360 - 180

       # Target absolute position for the PID
       target = current_degrees + error
       self.motor.pid.setpoint = target

       # Get PID adjustment
       control_signal = self.motor.pid(current_degrees)

       # Check if target is reached (deadband of 4 degrees)
       if abs(error) < 4:
           self.motor.moveMotor(0)
           if debug:
               print(f"Centered at {current_degrees} | kP: {self.motor.pid.Kp}")
           return True

       # Scale PID output by speed magnitude (0.0 to 1.0)
       max_power = abs(speed) * 0.75
       power = max(-max_power, min(max_power, control_signal))

       self.motor.moveMotor(power)

       if debug:
           print(f"Error: {error:.2f} | Target: {target:.2f} | Power: {power:.2f}")

       return False
   def getCurrentAngle(self):
      currentPos = self.motor.encoder.getEncoderPosition()
      currentDeg = (currentPos-1)/1023 * 360
      forward = ((self.motor.forwardValue-1)/1023 * 360) % 360
      currentDeg -= forward
      #currentDeg = ((currentDeg + 180) % 360) - 180
      #print(f"Encoder: {self.encoder} | fVal {forward} | current {currentDeg}")
      return currentDeg
   def setSpeed(self,speed):
      self.motor.setSpeed(speed)
   def killMotor(self):
       self.motor.killMotor()
