# """ TEST CAMERA """
# from Controllers.CameraController import CameraController
#
# camera = CameraController()
# print(camera.record_video(3))

###

# """ TEST MOTION DETECTOR """
# from Controllers.MotionSensorController import MotionSensorController
# import time
#
#
# def motion_detected_callback():
#     print("Motion detected :)")
#
# msc = MotionSensorController(motion_detected_callback)
# msc.activate()
#
# print("The sensor is going to be deactivated in 10 seconds.")
# time.sleep(10)
#
# print("The sensor is being deactivated...")
# msc.deactivate()
#
# print("The sensor has been deactivated.")
# print("Good bye!")

###

""" TEST HIT DETECTOR """
from Objects.HitDetector import HitDetector
import time


def hit_detected_callback():
    print("{0} \t Hit detected!".format(int(time.time())))

hit_detector = HitDetector(hit_detected_callback)
hit_detector.activate()

duration = 40
print("The hit detector will be deactivated in {0} seconds...".format(duration))
time.sleep(duration)

# print("Dump file is being created...")
# dump_file_path = hit_detector.dump_sensor_data()
# print("Dump file has been created: {0}".format(dump_file_path))

print("The hit detector is being deactivated...")
hit_detector.deactivate()
print("The hit detector has been deactivated...")
print("Sensor data length is {0}".format(len(hit_detector.get_sensor_data())))

###

""" TEST HIT DETECTOR - LOAD FROM DUMP """
# from Objects.HitDetector import HitDetector
#
# hit_detector = HitDetector()
# dump_file_name = "accelerometer-dump-1514621218.pickle"
# dump_file_name = None
# hit_detector.load_sensor_data_from_dump(dump_file_name)
#
# print(hit_detector.get_sensor_data())

###

# """ TEST TIMER """
# from Objects.Timer import Timer
# import time
#
#
# def timeout_callback(duration):
#     print("Timeout! {0} seconds have passed.".format(duration))
#     print("End epoch is {0}".format(int(time.time())))
#
# timer = Timer(timeout_callback)
# print("Start epoch is {0}".format(int(time.time())))
# timer.initialize(20)



