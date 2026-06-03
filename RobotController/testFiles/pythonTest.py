import limelight
import limelightresults
import json
import time

discovered_limelights = limelight.discover_limelights(debug=True)
print("discovered limelights:", discovered_limelights)
discovered_limelights = True
if discovered_limelights:
    #limelight_address = discovered_limelights[0]
    limelight_address = "172.28.0.1"
    ll = limelight.Limelight(limelight_address)

    ll.enable_websocket()


    try:
        while True:
            result = ll.get_latest_results()
            parsed_result = limelightresults.parse_results(result)
            if parsed_result is not None:
                print("valid targets: ", parsed_result.validity, ", pipelineIndex: ", parsed_result.pipeline_id,
                      ", Targeting Latency: ", parsed_result.targeting_latency)
                for tag in parsed_result.fiducialResults:
                   print(tag.robot_pose_target_space, tag.fiducial_id)
            time.sleep(1)  # Set this to 0 for max fps


    except KeyboardInterrupt:
        print("Program interrupted by user, shutting down.")
    finally:
        ll.disable_websocket()
