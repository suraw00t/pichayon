import uuid
import asyncio
import logging
import RPi.GPIO as GPIO

logger = logging.getLogger(__name__)


class Device:
    def __init__(self):
        self.device_id = '0000000000000000'

        GPIO.setmode(GPIO.BCM)
        self.relay_pin = 26 
        GPIO.setup(self.relay_pin, GPIO.OUT)
        GPIO.output(self.relay_pin, GPIO.HIGH)

    def get_device_id(self):
        try:
            f = open('/proc/cpuinfo', 'r')
            for line in f:
                if line[0:6] == 'Serial':
                    self.device_id = line[10:26]
            f.close()
        except Exception as e:
            logger.exception(e)
            # self.device_id = "ERROR000000000"
        if self.device_id == '0000000000000000':
            self.device_id = uuid.getnode()

        return self.device_id
    
    async def open_door(self):
        logger.debug('Opendoor')
        GPIO.output(self.relay_pin, GPIO.LOW)
        await asyncio.sleep(5)
        GPIO.output(self.relay_pin, GPIO.HIGH)

        
