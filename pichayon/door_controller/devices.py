import uuid
import asyncio
import logging
import datetime
import RPi.GPIO as GPIO

logger = logging.getLogger(__name__)


class Device:
    def __init__(self):
        self.device_id = '0000000000000000'

        GPIO.setmode(GPIO.BOARD)
        self.relay_pin = 26 
        GPIO.setup(self.relay_pin, GPIO.OUT)
        GPIO.output(self.relay_pin, GPIO.HIGH)


        self.switch_pin = 16
        GPIO.setup(self.switch_pin, GPIO.IN)
        # GPIO.output(self.switch_pin, GPIO.HIGH)
        GPIO.setup(self.switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.last_opened_date = datetime.datetime.now()

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
        current_date = datetime.datetime.now()
        diff = current_date - self.last_opened_date
        # print(f'--> {diff}')
        if diff.seconds < 5:
            logger.debug('Last opened date less than 5 seconds')
            return

        logger.debug('Open door')
        self.last_opened_date = current_date
        GPIO.output(self.relay_pin, GPIO.LOW)
        await asyncio.sleep(5)
        GPIO.output(self.relay_pin, GPIO.HIGH)

    
    async def is_turn_on_switch(self):
        return GPIO.input(self.switch_pin)
