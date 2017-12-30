import threading
import time


class Timer:
    """
    Keeps time and notifies in case of timeout
    """

    # Callback that will be called in case of timeout
    cb = None

    duration_in_seconds = 0

    is_canceled = False

    # The thread
    thr = None

    def __init__(self, callback):
        """
        :param callback: A callback that will be called when the time is out. Takes one parameter, which is the duration
            provided: callback(duration_in_seconds)
        :return:
        """

        if callback is None or not callable(callback):
            raise TypeError("Provide a valid callback function.")

        self.cb = callback

    def initialize(self, duration_in_seconds):
        self.thr = threading.Thread(target=self._wait)
        self.duration_in_seconds = duration_in_seconds
        self.is_canceled = False
        self.thr.start()

    def cancel(self):
        self.is_canceled = True

    def reinitialize(self):
        self.cancel()
        self.initialize(self.duration_in_seconds)

    def _wait(self):
        # Wait for the specified duration
        first_epoch = time.time()

        while time.time() - first_epoch < self.duration_in_seconds and not self.is_canceled:
            continue

        # time.sleep(self.duration_in_seconds)

        # Call the callback if the timer has not been canceled
        if not self.is_canceled:
            self.cb(self.duration_in_seconds)

        # Exit the thread
        self._exit_thread()

    def _exit_thread(self):
        try:
            self.thr.join(0.00001)
        except RuntimeError:
            pass