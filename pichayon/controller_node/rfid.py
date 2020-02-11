import asyncio
import logging
import RPi.GPIO as GPIO
import time
from pirc522 import RFID

logger = logging.getLogger(__name__)


class RFIDReader:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.reader = RFID(pin_mode=GPIO.BCM)
        self.buzzer = 4
        GPIO.setup(self.buzzer, GPIO.OUT)
        GPIO.output(self.buzzer, GPIO.LOW)
    
    def uid_to_num(self, uid):
      n = 0
      for i in range(0, 5):
          n = n * 256 + uid[i]
      return n

    def get_id(self):
        #while True:
            #logger.debug('okayy')
            #self.reader.wait_for_tag()
            #logger.debug('readddd')
            
        (error, tag_type) = self.reader.request()
        if not error:
            (error, uid) = self.reader.anticoll()
            if not error:
                self.reader.stop_crypto()
                return str(self.uid_to_num(uid))
            #time.sleep(0.5)
        return ''
