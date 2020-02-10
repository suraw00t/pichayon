import asyncio
import logging
import RPi.GPIO as GPIO
import time
from mfrc522 import MFRC522

logger = logging.getLogger(__name__)


class RFID:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.READER = MFRC522(pin_mode=GPIO.BCM)
        self.buzzer = 4
        GPIO.setup(self.buzzer, GPIO.OUT)
        GPIO.output(self.buzzer, GPIO.LOW)
    
    def read_id_no_block(self):
      (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
      if status != self.READER.MI_OK:
          return None
      (status, uid) = self.READER.MFRC522_Anticoll()
      if status != self.READER.MI_OK:
          return None
      return self.uid_to_num(uid)
    
    def uid_to_num(self, uid):
      n = 0
      for i in range(0, 5):
          n = n * 256 + uid[i]
      return n

    def get_id(self):
        try:
            # while True:
            id_read = self.read_id_no_block()
            if id_read:
                GPIO.output(self.buzzer, GPIO.HIGH)
                time.sleep(.05)
                GPIO.output(self.buzzer, GPIO.LOW)
                time.sleep(.05)
                GPIO.output(self.buzzer, GPIO.HIGH)
                time.sleep(.025)
                GPIO.output(self.buzzer, GPIO.LOW)
                return id_read
            return None
        except KeyboardInterrupt:
            GPIO.cleanup()
            # raise
