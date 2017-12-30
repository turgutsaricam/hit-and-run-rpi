import time
import threading
import RPi.GPIO as GPIO


class MotionSensorController(threading.Thread):

    # CONSTANTS
    INPUT_PIN_NUMBER = 18

    is_active = False

    # Callback function that will be called when the sensor detects motion
    cb = None

    def __init__(self, callback=None):
        """
        :param callback: A callback that will be called when the sensor detects motion. Takes no parameters.
        :return:
        """

        super().__init__(target=self._activate)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.INPUT_PIN_NUMBER, GPIO.IN)

        # Make sure the callback is callable
        if callback is not None and not callable(callback):
            callback = None

        self.cb = callback

    def activate(self):
        """
        Activates the sensor in a separate thread.
        :return:
        """

        self.is_active = True
        self.start()

    def deactivate(self):
        """
        Deactivates the sensor and terminates the thread.
        :return:
        """

        self.is_active = False
        self.join()

    def _activate(self):
        """
        The real activation method. Call this in a separate thread so that it does not interrupt other processes.
        :return:
        """

        i = 0
        while self.is_active:
            i += 1
            if GPIO.input(self.INPUT_PIN_NUMBER):
                # print(str(i).ljust(10) + "Motion detected.")

                if self.cb is not None:
                    self.cb()

            time.sleep(0.5)
