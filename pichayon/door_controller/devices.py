import uuid
import asyncio
import logging
import datetime
import RPi.GPIO as GPIO

from .rfid import asr1200e, vguang_sk330, vguang_m300

logger = logging.getLogger(__name__)


class Device:
    def __init__(self, settings):
        self.settings = settings
        self.device_id = "0000000000000000"

        self.door_closed_pin = 15
        self.switch_pin = 16
        self.relay_pin = 18
        self.is_relay_active_high = settings.get(
            "PICHAYON_DOOR_RELAY_ACTIVE_HIGH", True
        )

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.relay_pin, GPIO.OUT)
        GPIO.setup(self.switch_pin, GPIO.IN)
        GPIO.setup(self.door_closed_pin, GPIO.IN)

        if self.is_relay_active_high:
            GPIO.output(self.relay_pin, GPIO.HIGH)
        else:
            GPIO.output(self.relay_pin, GPIO.LOW)

        self.last_opened_date = datetime.datetime.now()

        self.reader_name = self.settings.get("PICHAYON_DOOR_READER", "ASR1200E")
        self.rfid = self.get_reader_device(self.reader_name)

    def get_reader_device(self, name):
        if name == "ASR1200E":
            return asr1200e.WiegandReader()
        elif name == "VGUANG-M300":
            return vguang_m300.RS235Reader("/dev/ttyS0")
        elif name == "VGUANG-SK330":
            return vguang_sk330.RS235Reader("/dev/ttyS0")

        return None

    async def initial(self):
        await self.rfid.connect()

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
        open_door_duration = 3
        # print(f'--> {diff}')
        if diff.seconds < open_door_duration:
            logger.debug(f"Last opened date less than {open_door_duration} seconds")
            return

        logger.debug("Open door")
        beeb_task = asyncio.create_task(self.rfid.play_success_action(0.1))

        self.last_opened_date = current_date

        await self.unlock_door()
        await asyncio.sleep(open_door_duration)
        await self.lock_door()

        # lock door
        await beeb_task

    async def unlock_dock(self):
        if self.is_relay_active_high:
            GPIO.output(self.relay_pin, GPIO.LOW)
        else:
            GPIO.output(self.relay_pin, GPIO.HIGH)

    async def lock_dock(self):
        if self.is_relay_active_high:
            GPIO.output(self.relay_pin, GPIO.HIGH)
        else:
            GPIO.output(self.relay_pin, GPIO.LOW)

    async def unlock_door_until(self):
        logger.debug(f"unlock door until")

    async def deny_access(self):
        logger.debug("Denied Access")
        beeb_task = asyncio.create_task(self.rfid.play_denied_action(0.1))
        await beeb_task

    async def is_turn_on_switch(self):
        return not GPIO.input(self.switch_pin)

    async def is_door_opened(self):
        return GPIO.input(self.door_closed_pin)
