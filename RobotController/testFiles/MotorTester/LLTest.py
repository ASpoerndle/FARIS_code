import limelight
import limelightresults
import json
import time
from MotorController import MotorController
def init_LL():
    limelight_address = "172.29.0.1"
    ll = limelight.Limelight(limelight_address)
    ll.enable_websocket()
    return ll
mc = MotorController()
mc.adjustForward(False)
ll = init_LL()
o_heading = mc.getHeading()
pos1 = 0
pos2 = 0
checkAlign = True
stopCond = False
def check5(ll,mc):
    seen = False
    while seen == False:
        result = ll.get_latest_results()
        parsed_result = limelightresults.parse_results(result)
        if(parsed_result is not None):
            for tag in parsed_result.fiducialResults:
                if(tag.fiducial_id != 5 and seen == False):
                    mc.turn(5,False)
                    mc.moveCord([.5,0],False)
                else:
                    seen = True
        else:
            mc.moveCord([0,-.5],False)
def check3(ll,mc):
    seen = False
    while seen == False:
        result = ll.get_latest_results()
        parsed_result = limelightresults.parse_results(result)
        if(parsed_result is not None):
            for tag in parsed_result.fiducialResults:
                if(tag.fiducial_id != 3 and seen == False):
                    mc.turn(-5,False)
                else:
                    seen = True
         

while True:
            #check5(ll,mc)
            #check3(ll,mc)
            #mc.forceNewHeading()
            result = ll.get_latest_results()
            parsed_result = limelightresults.parse_results(result)
            if parsed_result is not None:
                print("valid targets: ", parsed_result.validity, ", pipelineIndex: ", parsed_result.pipeline_id,
                      ", Targeting Latency: ", parsed_result.targeting_latency)
                for tag in parsed_result.fiducialResults:
                   #print(tag.robot_pose_target_space, tag.fiducial_id)
                   if(checkAlign):
                    if(tag.fiducial_id == 5):
                        
                       #time.sleep(1)
                        RPTS = tag.target_pose_camera_space
                        print(f"Marker 5 Relativity: tx:{RPTS[0]} | ty {RPTS[1]} | tz: {RPTS[2]}") 
                        print(f"Moving {RPTS[2]} m towards April Tag {tag.fiducial_id}")
                        pos1 = -RPTS[0]
                        pos1 = abs(pos1)
                        #mc.moveDistance(RPTS[2],False,False)
                        mc.moveCord([-RPTS[2],-RPTS[0]], False)
                        print(f"Succesfully moved {RPTS[2]} m towards April Tag {tag.fiducial_id}")
                    if(tag.fiducial_id == 3 and stopCond):
                        RPTS = tag.target_pose_camera_space
                        
                        print(f"Marker 3 Relativity: tx:{RPTS[0]} | ty {RPTS[1]} | tz: {RPTS[2]}") 
                        pos2 = -RPTS[0]
                        if(pos2 > 0):
                            pos2 = -pos2
                   if(checkAlign and pos1 != 0 and pos2 != 0 and stopCond):
                        print(f"Pos1: {pos1} | Pos2: {pos2}")
                        horizontal_pos = (pos2 + pos1)
                        print(f"Difference horizontally: {horizontal_pos}")
                        mc.moveCord([horizontal_pos,0], False)
                        pos1 = 0
                        pos2 = 0
                        checkAlign = False
                   if(not checkAlign):
                       RPTS = tag.target_pose_camera_space
                       print("Z value: " + str(RPTS[2]))
                       time.sleep(1)
                       mc.moveCord([0,2*RPTS[2]], False)

                       mc.faceForward(False)

                time.sleep(1)  # Set this to 0 for max fps


