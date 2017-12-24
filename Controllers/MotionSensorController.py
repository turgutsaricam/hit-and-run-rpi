import time
import RPi.GPIO as GPIO

class MotionSensorController():

    # CONSTANTS
    INPUT_PIN_NUMBER = 18

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.INPUT_PIN_NUMBER, GPIO.IN)

    def activate(self):
        i = 0
        while True:
            i += 1
            if GPIO.input(self.INPUT_PIN_NUMBER):
                print(str(i).ljust(10) + "Motion detected.")

            time.sleep(0.5)

    def deactivate(self):
        pass