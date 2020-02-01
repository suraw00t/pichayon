import asyncio
import logging
import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522

logger = logging.getLogger(__name__)


class RFID:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.reader = SimpleMFRC522()
        self.buzzer = 4
        GPIO.setup(self.buzzer, GPIO.OUT)
        GPIO.output(self.buzzer, GPIO.LOW)

    def get_id(self):
        try:
            while True:
                id, text = self.reader.read()
                if id:
                    GPIO.output(self.buzzer, GPIO.HIGH)
                    time.sleep(.05)
                    GPIO.output(self.buzzer, GPIO.LOW)
                    time.sleep(.05)
                    GPIO.output(self.buzzer, GPIO.HIGH)
                    time.sleep(.025)
                    GPIO.output(self.buzzer, GPIO.LOW)
                    return id

                time.sleep(1)
        except KeyboardInterrupt:
            GPIO.cleanup()
            raise
