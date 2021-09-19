import asyncio
import logging
import RPi.GPIO as GPIO
import time
from pirc522 import RFID

logger = logging.getLogger(__name__)


class RFIDReader:
    def __init__(self):
        # GPIO.setmode(GPIO.BCM)
        # self.reader = RFID(pin_mode=GPIO.BCM)
        # GPIO.setmode(GPIO.BOARD)
        # print(GPIO.getmode())
        self.reader = RFID()
        #self.buzzer = 4
        #GPIO.setup(self.buzzer, GPIO.OUT)
        #GPIO.output(self.buzzer, GPIO.LOW)
    
    def uid_to_num(self, uid):
      n = 0
      for i in range(0, 5):
          n = n * 256 + uid[i]
      return n

    def uid_to_hex(self, uid):
        hexs = []
        for num in uid:
            hexs.append(f'{num:02X}')

        return ''.join(hexs)

    def get_id(self):
        #while True:
            #logger.debug('okayy')
        self.reader.wait_for_tag()
        try:   
            (error, tag_type) = self.reader.request()
            if not error:

                (error, uid) = self.reader.anticoll()

                if not error:
                    self.reader.stop_crypto()
                    # print(f'---> {uid}')
                    # return str(self.uid_to_num(uid))
                    # print(f'-->{self.uid_to_hex(uid)}')
                    return self.uid_to_hex(uid)
        except Exception as e:
            logger.exception(e)
        return ''
