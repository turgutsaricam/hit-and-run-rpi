import datetime
import smtplib

from Controllers.CameraController import CameraController
from Controllers.MotionSensorController import MotionSensorController
import time

from Objects.HitDetector import HitDetector
from Objects.Timer import Timer
from Objects.DropboxHandler import DropboxHandler


class HitAndRunDetector:
    # Set this to True if you want the system to be shut down after one hit detection. Setting this false will make
    # the system stay on forever.
    RUN_ONCE = False

    # For how many seconds a hit should be waited
    timeout_in_seconds = 10

    # How many seconds more the camera should keep recording after a hit is detected
    record_duration_after_hit_in_seconds = 5

    SMTP_USER       = 'turgutsaricam.raspberrypi@gmail.com'     # Email address from which the emails will be sent
    SMTP_PASS       = 'raspberry'                               # Password of the email address
    TO_ADDRESS      = 'turgutsaricam@gmail.com'                 # Target email. The emails will be sent to this address.
    MAIL_SUBJECT    = 'Your car has been hit!'                  # Subject of the email.

    SMTP_HOST = 'smtp.gmail.com'
    SMTP_PORT = 587

    # No need to make changes in below variables.

    motion_sensor_controller = None  # type: MotionSensorController
    camera_controller = None  # type: CameraController
    hit_detector = None  # type: HitDetector
    timer = None  # type: Timer

    is_motion_detected = False
    is_hit_detected = False
    is_timeout = False
    video_urls = None

    shut_down = False

    def __init__(self):
        super().__init__()

        self.camera_controller = CameraController()
        self.motion_sensor_controller = MotionSensorController(self.motion_detected_callback)
        self.hit_detector = HitDetector(self.hit_detected_callback)
        self.timer = Timer(self.timeout_callback)

    def activate(self):
        print("-- Hit and run detector has been activated!")

        self.is_motion_detected = False
        self.is_hit_detected = False
        self.is_timeout = False
        self.video_urls = None
        self.shut_down = False

        self.motion_sensor_controller.activate()

        while not self.shut_down:
            if self.video_urls is not None:
                # Send video URLs to the car's owner. We are sending the email in the main thread, because it caused
                # a few exceptions to send it in a worker thread.
                print("Sending email...")

                self.send_email(self.video_urls)
                print("Email has just been sent.")

                # Invalidate video URLs
                self.video_urls = None

                # That's enough.
                self.shut_down = True

            continue

        self.hit_detector.deactivate()
        print("The hit detector has been deactivated.")

        self.motion_sensor_controller.deactivate()
        print("The motion sensor has been deactivated.")

        self.timer.cancel()
        print("The timer has been canceled.")

        print("Done.")

        # Keep it on!
        if not self.RUN_ONCE:
            self.activate()

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

        # Upload the recording
        file_path = self.camera_controller.get_last_recorded_file_path()
        print("Uploading the video to Dropbox: {0}".format(file_path))

        dbx_handler = DropboxHandler()
        file_dropbox_url = dbx_handler.upload_file(file_path)
        print('File uploaded: {0}'.format(file_dropbox_url))

        # Store the video URLs in the instance variable
        self.video_urls = [file_dropbox_url]

    def send_email(self, urls):
        """ Sends an email to the car's owner, which includes the provided URLs.

        :param list urls: A list of URLs that will be attached to the email.
        :return:
        """
        current_time_str = datetime.datetime.now().strftime("%I:%M %p on %B %d, %Y")

        body = 'Your car has been hit at {0}. A video of the car that hit your car can be found in the links below.\n\n{1}'.format(
            current_time_str, '\n'.join(urls))

        header = 'To: {0}\nFrom: {1}\nSubject: {2}'.format(self.TO_ADDRESS, self.SMTP_USER, self.MAIL_SUBJECT)

        print(header + '\n' + body)

        s = smtplib.SMTP(self.SMTP_HOST, self.SMTP_PORT)

        s.ehlo()
        s.starttls()
        s.ehlo()

        s.login(self.SMTP_USER, self.SMTP_PASS)
        s.sendmail(self.SMTP_USER, self.TO_ADDRESS, header + '\n\n' + body)

        s.quit()
