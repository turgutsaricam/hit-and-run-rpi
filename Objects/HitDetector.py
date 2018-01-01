from Controllers.AccelerometerController import AccelerometerController
import os, glob, errno
from constants import APP_DIR
import time
import pickle


class HitDetector:
    # Callback function that will be called when the sensor detects motion
    cb = None

    # This is a list of arrays. Each array has 3 items, which are x, y, and z axes readings from the accelerometer,
    # respectively.
    sensor_data = []

    accelerometer_controller = None  # type: AccelerometerController

    DUMP_DIR = 'storage/file/accelerometer-dump'

    dump_file_name_format = 'accelerometer-dump-{0}.pickle'

    # A threshold value that is used to determine if a change in an axis of the accelerometer is a hit.
    hit_threshold = 0.1

    # How many items should be checked to detect a hit.
    window_length = 5

    # At max, how many sensor entries should be kept in self.sensor_data
    max_sensor_data_count = 200

    def __init__(self, callback=None):
        # Make sure the callback is callable
        if callback is not None and not callable(callback):
            callback = None

        self.cb = callback

        # Initialize the accelerometer controller which will add the sensor readings
        self.accelerometer_controller = AccelerometerController(self._add_and_analyze_data)

    def activate(self):
        self.accelerometer_controller.activate()

    def deactivate(self):
        self.accelerometer_controller.deactivate()

    def _add_and_analyze_data(self, axes):
        """Adds accelerometer readings to a list and analyzes the list to detect a hit.

        :param axes: A dictionary with 'x', 'y', and 'z' keys, each storing the corresponding accelerometer axis reading.
        :return:
        """

        # Add the data to the list
        self.sensor_data.append([axes['x'], axes['y'], axes['z']])

        # Remove redundant sensor data entries
        if len(self.sensor_data) > self.max_sensor_data_count:
            self.sensor_data = self.sensor_data[(-1 * self.window_length):]

        # Detect the hit if there is any
        self._detect_hit()

    def _detect_hit(self):
        """Analyzes the sensor data and detects hits

        :return:
        """

        l = len(self.sensor_data)

        # We need at least 2 entries in sensor data.
        if l < self.window_length:
            return

        # Loop over the sensor data starting from the last one.
        for i in range(l - 2, max(-1, l - self.window_length), -1):
            curr = self.sensor_data[i]
            nxt = self.sensor_data[i + 1]

            current_x = curr[0]
            current_y = curr[1]
            current_z = curr[2]

            next_x = nxt[0]
            next_y = nxt[1]
            next_z = nxt[2]

            # Get the derivative for every axis. If the change is greater than the threshold, it is a hit.
            if (abs(current_x - next_x) > self.hit_threshold or
                        abs(current_y - next_y) > self.hit_threshold or
                        abs(current_z - next_z) > self.hit_threshold):

                # This is a hit. Call the callback.
                if self.cb:
                    self.cb()

                # No need to check other entries.
                return

    def get_sensor_data(self):
        return self.sensor_data

    def set_sensor_data(self, sensor_data):
        self.sensor_data = sensor_data

    #
    # DUMP-RELATED STUFF
    #

    def dump_sensor_data(self):
        """Dumps the sensor data to a pickle file.

        :return: Path of the dump file
        """
        dump_dir = self.get_dump_dir()

        epoch = int(time.time())
        dump_file_name = self.dump_file_name_format.format(str(epoch))
        dump_file_path = os.path.join(dump_dir, dump_file_name)

        with open(dump_file_path, 'wb') as fp:
            pickle.dump(self.sensor_data, fp)

        return dump_file_path

    def load_sensor_data_from_dump(self, dump_file_name=None):
        """Loads the sensor data from a dump file.

        :param dump_file_name: If none, the latest dump file will be used. Otherwise, that file will be loaded.
        :return:
        """

        dump_dir = self.get_dump_dir()

        dump_file_path = None
        if dump_file_name is not None:
            dump_file_path = os.path.join(dump_dir, dump_file_name)

        else:
            # Get the last created file in the dump dir. The line below finds all files whose name is in the right dump
            # file name format
            file_list = glob.glob(os.path.join(dump_dir, self.dump_file_name_format.format("*")))

            if file_list:
                dump_file_path = max(file_list, key=os.path.getctime)

        # Do not proceed if there is no file
        if dump_file_path is None or not os.path.isfile(dump_file_path):
            return

        # Read the file and set the sensor data
        with open(dump_file_path, 'rb') as fp:
            self.sensor_data = pickle.load(fp)

    def get_dump_dir(self):
        """
        Get the dump directory path. This also creates the directories if they do not exist.

        :return: Path of the dump directory
        """

        # Create the dump dir path
        dump_dir = os.path.join(APP_DIR, self.DUMP_DIR)

        # Create the directories if they do not exist
        try:
            if not os.path.exists(dump_dir):
                os.makedirs(dump_dir)

        except OSError as e:
            # Raise an error if the dir does not exist. Although we are checking the existence of the dir in the try
            # statement, the dir might have been created just after we check it and found out it does not exist. So,
            # this handles that situation.
            if e.errno != errno.EEXIST:
                raise

        return dump_dir
