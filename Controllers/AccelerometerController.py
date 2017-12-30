import time
from libs.adxl345 import ADXL345
import threading


class AccelerometerController:

    adxl345 = None
    is_active = False

    # Callback function that will be called when the sensor data is read
    cb = None

    # The thread
    thr = None

    def __init__(self, callback=None):
        # Make sure the callback is callable
        if callback is not None and not callable(callback):
            callback = None

        self.cb = callback

    def activate(self):
        self.thr = threading.Thread(target=self._activate)
        self.is_active = True
        self.thr.start()

    def deactivate(self):
        self.is_active = False
        self.thr.join()

    def _activate(self):
        print("Accelerometer readings are activated...")

        if self.adxl345 is None:
            self.adxl345 = ADXL345()

        i = 0
        while self.is_active:
            # Read the sensor data
            axes = self.adxl345.getAxes(True)

            if self.cb is not None:
                self.cb(axes)

            # # Print the sensor data
            # print("%d ADXL345 on address 0x%x:\tx = %.3fG\ty = %.3fG\tz = %.3fG" % (i, self.adxl345.address, axes['x'], axes['y'], axes['z']))

            # Wait for a while
            time.sleep(0.1)

            i += 1
