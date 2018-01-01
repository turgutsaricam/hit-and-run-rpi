import picamera
import time
import os
import threading
from constants import APP_DIR
from Objects.Timer import Timer


class CameraController():

    # CONSTANTS
    VIDEO_DIR = 'storage/video'
    PHOTO_DIR = 'storage/photo'

    # PRIVATE INSTANCE VARIABLES

    _camera = None

    # Stores the state of the camera for video recording. True if the camera is recording currently. Otherwise, false.
    _is_recording = False

    # Stores last recorded video file's path
    _last_recorded_file_path = None

    _video_file_path = None

    def __init__(self):
        pass

    def record_video(self, duration_in_seconds=5):
        """
        Records a video for specified duration
        :param duration_in_seconds: Duration of video in seconds
        :return:
        """

        # Start recording
        self.start_recording()

        # Record for specified duration
        time.sleep(duration_in_seconds)

        # Stop the recording and return the video file path
        return self.stop_recording()

    def start_recording(self):
        """
        Start recording a video
        :return:
        """

        # Create the camera object
        if self._camera is None:
            self._camera = picamera.PiCamera()

        # If we are currently recording, do not start another recording.
        if self._is_recording:
            return

        self._is_recording = True

        epoch = int(time.time())
        video_file_name = 'vid-' + str(epoch) + '.h264'

        self._video_file_path = os.path.join(APP_DIR, self.VIDEO_DIR, video_file_name)

        self._camera.start_recording(self._video_file_path)

    def stop_recording(self):
        """
        Stop recording
        :return: Path of the video file
        """

        if not self._is_recording:
            return None

        # First, stop the recording.
        self._camera.stop_recording()

        # Deactivate the camera.
        self._camera.close()
        self._camera = None

        # We are not recording from now on.
        self._is_recording = False

        # Get the video file name
        file_path = self._video_file_path

        # Invalidate the file path
        self._video_file_path = None

        self._last_recorded_file_path = file_path

        # Return the file path
        return file_path

    def delete_last_recorded_video(self):
        """
        Deletes last recorded video file
        :return:
        """

        if self._last_recorded_file_path is None or not os.path.isfile(self._last_recorded_file_path):
            return

        os.remove(self._last_recorded_file_path)

    def get_last_recorded_file_path(self):
        return self._last_recorded_file_path
