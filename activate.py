from Controllers.CameraController import CameraController
from Controllers.MotionSensorController import MotionSensorController
import time

from Objects.HitDetector import HitDetector
from Objects.Timer import Timer


class HitAndRunDetector:
    motion_sensor_controller = None  # type: MotionSensorController
    camera_controller = None  # type: CameraController
    hit_detector = None  # type: HitDetector
    timer = None  # type: Timer

    is_motion_detected = False
    is_hit_detected = False
    is_timeout = False

    # For how many seconds a hit should be waited
    timeout_in_seconds = 10

    # How many seconds more the camera should keep recording after a hit is detected
    record_duration_after_hit_in_seconds = 5

    shut_down = False

    def __init__(self):
        super().__init__()

        self.camera_controller          = CameraController()
        self.motion_sensor_controller   = MotionSensorController(self.motion_detected_callback)
        self.hit_detector               = HitDetector(self.hit_detected_callback)
        self.timer                      = Timer(self.timeout_callback)

        self.motion_sensor_controller.activate()

        while not self.shut_down:
            continue

        self.hit_detector.deactivate()
        print("The hit detector has been deactivated.")

        self.motion_sensor_controller.deactivate()
        print("The motion sensor has been deactivated.")

        self.timer.cancel()
        print("The timer has been canceled.")

    def motion_detected_callback(self):
        # Do not proceed if this was called once.
        if self.is_motion_detected:
            return

        self.is_motion_detected = True
        self.is_hit_detected = False
        self.is_timeout = False

        print("Motion detected.")

        self.camera_controller.start_recording()
        print("Video recording has been started...")

        self.timer.initialize(self.timeout_in_seconds)
        print("Timer has been initialized with {0} seconds".format(self.timeout_in_seconds))

        self.hit_detector.activate()
        print("Waiting for a hit...")

    def timeout_callback(self, duration_in_seconds):
        # Do not proceed if this was called once.
        if self.is_timeout:
            return

        self.is_timeout = True

        # Cancel the timer so that it joins its thread to the main thread.
        self.timer.cancel()

        print("Timeout! Hit detected: {0}".format("Yes" if self.is_hit_detected else "No"))

        if not self.is_hit_detected:
            self.is_motion_detected = False

            self.camera_controller.stop_recording()
            self.camera_controller.delete_last_recorded_video()
            print("The last recording has been deleted.")

            self.hit_detector.deactivate()
            print("The hit detector has been deactivated.")

    def hit_detected_callback(self):
        # Do not proceed if this was called once.
        if self.is_hit_detected:
            return

        self.is_hit_detected = True
        print("{0} - Hit detected!".format(int(time.time())))

        # Cancel the timer
        self.timer.cancel()

        # Wait for a while for the camera to keep recording
        print("Recording for an additional {0} seconds".format(self.record_duration_after_hit_in_seconds))
        time.sleep(self.record_duration_after_hit_in_seconds)

        self.camera_controller.stop_recording()
        print("Recording has been stopped.")

        # If the timer still keeps counting down, end it.
        if not self.is_timeout:
            self.timeout_callback(self.timeout_in_seconds)

        # Send the file via email
        self.send_email()

        self.shut_down = True

    def send_email(self):
        # TODO: Implement this
        pass


hit_and_run_detector = HitAndRunDetector()
