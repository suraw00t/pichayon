import uuid
import asyncio
import logging
import datetime
import RPi.GPIO as GPIO

from .rfid import asr1200e, vguang_sk330, vguang_m300

logger = logging.getLogger(__name__)


class Device:
    def __init__(
        self,
        settings,
    ):
        self.settings = settings
        self.device_id = "0000000000000000"
        self.door_id = None
        self.log_manager = None

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

        self.last_opened_date = datetime.datetime.now()

        self.reader_name = self.settings.get("PICHAYON_DOOR_READER", "ASR1200E")
        print(self.reader_name)
        self.rfid = None
        self.door_config = {}
        self.key_types = {}
        self.is_auto_relock = True
        self.is_force_unlock = False

    def get_reader_device(self, name, key_types):
        if name == "ASR1200E":
            return asr1200e.WiegandReader()
        elif name == "VGUANG-M300":
            return vguang_m300.RS485Reader(key_types, self.door_config, "/dev/ttyS0")
        elif name == "VGUANG-SK330":
            return vguang_sk330.RS485Reader(key_types, self.door_config, "/dev/ttyS0")

        return None

    async def set_log_manager(self, log_manager):
        self.log_manager = log_manager

    async def initial(self, key_types):
        try:
            self.rfid = self.get_reader_device(self.reader_name, key_types)
            await self.lock_door()
            await self.rfid.connect()
        except Exception as e:
            logger.exception(e)

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

    async def update_information(self, data):
        self.is_auto_relock = data.get("is_auto_relock", True)
        self.door_id = data.get("door_id", "")

        self.door_config["begin_access_time"] = datetime.datetime.strptime(
            data.get("begin_access_time", 

                    "00:00"), "%H:%M"
        ).time()
        self.door_config["end_access_time"] = datetime.datetime.strptime(
                data.get("end_access_time", "00:00"), "%H:%M"
        ).time()

        if data.get("end_access_time") != "00:00":
            self.door_config["end_access_time"] = self.door_config[
                "end_access_time"
            ].replace(hour=23, minute=59, second=59, microsecond=999999)

        self.door_config["allow_read_sector0"] = data.get("allow_read_sector0", False)

        if self.is_auto_relock:
            self.is_force_unlock = False
            await self.lock_door()

        logger.debug(f"auto_relock status -> {self.is_auto_relock}")
        logger.debug(f"force_unlock status -> {self.is_force_unlock}")

    async def open_door(self):
        if not self.is_auto_relock and self.is_force_unlock:
            logger.debug(
                f"auto relock status {self.is_auto_relock} and force unlock {self.is_force_unlock}"
            )
            return

        current_date = datetime.datetime.now()
        diff = current_date - self.last_opened_date
        open_door_duration = 5
        # print(f'--> {diff}')
        if diff.seconds < open_door_duration:
            logger.debug(f"Last opened date less than {open_door_duration} seconds")
            return

        logger.debug("Open door")
        if self.rfid:
            beeb_task = asyncio.create_task(self.rfid.play_success_action(0.1))

        self.last_opened_date = current_date

        await self.unlock_door()
        await asyncio.sleep(open_door_duration)
        await self.lock_door()

        if self.rfid:
            await beeb_task

    async def unlock_door(self):
        # logger.debug("unlock door")
        if self.is_relay_active_high:
            GPIO.output(self.relay_pin, GPIO.LOW)
        else:
            GPIO.output(self.relay_pin, GPIO.HIGH)

    async def lock_door(self):
        # logger.debug("lock door")
        if self.is_relay_active_high:
            GPIO.output(self.relay_pin, GPIO.HIGH)
        else:
            GPIO.output(self.relay_pin, GPIO.LOW)

    async def force_unlock(self):
        logger.debug(f"unlock door until")

        if self.is_auto_relock:
            logger.debug(f"auto_relock is on force unlock is disable")
            return

        if not await self.is_access_time():
            logger.debug(f"Not in range of access time force unlock is disable")
            await self.play_denied_access_sound()
            if self.is_force_unlock:
                self.is_force_unlock = False
                await self.lock_door()

            return

        if self.rfid:
            beeb_task = asyncio.create_task(self.rfid.play_success_action(0.3))
        if not self.is_force_unlock:
            logger.debug(f"force unlock is on")
            await self.unlock_door()
            await self.put_log(None, type="switch", action="force-unlock")
            self.is_force_unlock = True
        else:
            logger.debug(f"force unlock is off")
            await self.lock_door()
            await self.put_log(None, type="switch", action="relock")
            self.is_force_unlock = False

        if self.rfid:
            await beeb_task

    async def put_log(self, user, type="switch", action=""):
        if self.log_manager:
            await self.log_manager.put_log(user, type=type, action=action)

    async def play_denied_access_sound(self, duration=0.1):
        if self.rfid:
            beeb_task = asyncio.create_task(self.rfid.play_denied_action(duration))
            await beeb_task

    async def play_success_access_sound(self, duration=0.1):
        if self.rfid:
            beeb_task = asyncio.create_task(self.rfid.play_success_action(duration))
            await beeb_task

    async def is_turn_on_switch(self):
        return not GPIO.input(self.switch_pin)

    async def is_door_opened(self):
        return GPIO.input(self.door_closed_pin)

    async def is_access_time(self):
        current_time = datetime.datetime.now().time()
        logger.debug(f'{current_time} {self.door_config["begin_access_time"]} - {self.door_config["end_access_time"]}')
        if (
 (
            current_time >= self.door_config["begin_access_time"]
            and current_time <= self.door_config["end_access_time"]
            )
            or
            self.door_config["begin_access_time"]
            == self.door_config["end_access_time"]
                   ):
            return True

        return False
