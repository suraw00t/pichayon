import uuid
import asyncio
import logging
import datetime
import RPi.GPIO as GPIO

from .rfid import asr1200e, vguang_sk330, vguang_m300

logger = logging.getLogger(__name__)


class Device:
    def __init__(self):
        self.device_id = "0000000000000000"

        self.door_closed_pin = 15
        self.switch_pin = 16
        self.relay_pin = 18

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.relay_pin, GPIO.OUT)
        GPIO.output(self.relay_pin, GPIO.HIGH)
        # GPIO.setup(self.switch_pin, GPIO.IN)
        GPIO.setup(self.switch_pin, GPIO.IN)
        GPIO.setup(self.door_closed_pin, GPIO.IN)

        self.last_opened_date = datetime.datetime.now()

        self.rfid = self.get_reader_device()

    def get_reader_device(self, name):
        if name == "ASR1200E":
            return asr1200e.WiegandReader()
        elif name == "VGUANG-M300":
            return vguang_m300.RS235Reader()
        elif name == "VGUANG-SK330":
            return vguang_sk330.RS235Reader()

        return None

    def get_device_id(self):
        try:
            f = open("/proc/cpuinfo", "r")
            for line in f:
                if line[0:6] == "Serial":
                    self.device_id = line[10:26]
            f.close()
        except Exception as e:
            logger.exception(e)
            # self.device_id = "ERROR000000000"
        if self.device_id == "0000000000000000":
            self.device_id = uuid.getnode()

        return self.device_id

    async def open_door(self):
        current_date = datetime.datetime.now()
        diff = current_date - self.last_opened_date
        # print(f'--> {diff}')
        if diff.seconds < 5:
            logger.debug("Last opened date less than 5 seconds")
            return

        logger.debug("Open door")
        beeb_task = asyncio.create_task(self.rfid.play_beep(0.1))

        self.last_opened_date = current_date
        GPIO.output(self.relay_pin, GPIO.LOW)
        await asyncio.sleep(5)
        GPIO.output(self.relay_pin, GPIO.HIGH)

        await beeb_task

    async def is_turn_on_switch(self):
        return not GPIO.input(self.switch_pin)

    async def is_door_opened(self):
        return GPIO.input(self.door_closed_pin)
