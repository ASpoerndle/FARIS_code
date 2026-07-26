from MotorWithEncoder import MotorWithEncoder

class RotationFocusedMotor():
   def __init__(self, pca, pin, side, enc, fVal):
       self.motor = MotorWithEncoder(pca, pin, side, enc, fVal)
   def rotate(self, angle, speed, debug=False):
       speed = abs(speed)
       current = self.motor.encoder.getEncoderPosition()

       forward = ((self.motor.forwardValue - 1) / 1023) * 360 % 360

       # current_degrees = ((current-1)/1023) * 360
       current_degrees = ((current - 1) / 1023) * 360 % 360

       target = (forward + angle) % 360

       speed *= 0.75
       error = (target - current_degrees + 180) % 360 - 180
       if (error > 90):
           error -= 180
           speed *= -1
       if (error < -90):
           error += 180
           speed *= -1
       target = current_degrees + error
       speed *= -1
       self.motor.pid.setpoint = target
       control_signal = self.motor.pid(current_degrees)

       # Absolute safety check
       if angle > 91  or angle < -91:
           self.motor.moveMotor(0)
           print("ERR: Cord limit reached!")
           return True
       if abs(error) < 4:
           self.motor.moveMotor(0)
           if (debug or True):
                print(f"Centered at {current} kP: {self.motor.pid.Kp} kI: {self.motor.pid.Ki} kD: {self.motor.pid.Kd}")
                return True
       else:
            self.motor.moveMotor(control_signal * speed)

       if (debug):
            print(f"Enc: {self.motor.encoder.encoder} | Error {error} Target: {target} | Current: {current_degrees} | Power: {control_signal}")
            return False
   def getCurrentAngle(self):
      currentPos = self.motor.encoder.getEncoderPosition()
      currentDeg = (currentPos-1)/1023 * 360
      forward = ((self.motor.forwardValue-1)/1023 * 360) % 360
      currentDeg -= forward
      #print(f"Encoder: {self.encoder} | fVal {forward} | current {currentDeg}")
      return currentDeg
   def setSpeed(self,speed):
      self.motor.setSpeed(speed)
   def killMotor(self):
       self.motor.killMotor()
