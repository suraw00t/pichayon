import asyncio
import threading
import json
import datetime
import os
import time
import logging
import RPi.GPIO as GPIO

from nats.aio.client import Client as NATS
from nats.aio.errors import ErrTimeout
from pichayon import crypto

from . import devices

# from .rfid import rc522
from . import database
from . import logs

logger = logging.getLogger(__name__)


class DoorControllerServer:
    def __init__(self, settings):
        self.settings = settings
        self.is_register = False
        self.controller_command_queue = asyncio.Queue()
        self.rfid_queue = asyncio.Queue()
        self.device = devices.Device(self.settings)
        self.device_id = self.device.get_device_id()
        self.db_manager = database.Manager(self.settings, self.device_id)

        self.nc = None
        self.log_manager = logs.LogManager(
            self.db_manager,
            self.device_id,
        )

        self.key_types = {}
        # self.keypad = keypad.Keypad()
        # self.passcode = ''

        self.running = False
        self.max_rfid_read_retry = self.settings.get("MAX_RFID_READ_RETRY", 3)

    async def get_ipv4(self):
        import subprocess

        output = subprocess.getoutput("hostname -I")

        return output.split(" ")[0]

    async def handle_controller_command(self, msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        data = json.loads(data)
        await self.controller_command_queue.put(data)
        # logger.debug(data)

    async def request_initial_authorization(self):

        logger.debug("initial authorization")
        data = dict(
            action="request_initial_data",
            device_id=self.device_id,
            ipv4=await self.get_ipv4(),
        )
        await self.nc.publish(
            "pichayon.controller.command",
            json.dumps(data).encode(),
        )

    async def process_controller_command(self):
        logger.debug("start process controller command")
        commands = {
            "initial": self.db_manager.initial_data,
            "add-user": self.db_manager.add_user,
            "delete-user": self.db_manager.delete_user,
            "update-user": self.db_manager.update_user,
            "update_door_information": self.device.update_information,
        }

        while self.running:
            data = await self.controller_command_queue.get()

            logger.debug(f"process command -> {data}")
            if "action" not in data:
                logger.debug("action not found")

            if data["action"] == "open-door":
                user = await self.db_manager.get_user_by_id_with_current_date(
                    data["user_id"]
                )
                if user:
                    await self.log_manager.put_log(
                        user,
                        type="web",
                        action="open-door",
                        message="success",
                        ip=data.get("ip"),
                    )
                    await self.device.open_door()
                else:
                    await self.device.play_denied_access_sound()
                    await self.log_manager.put_log(
                        user, type="web", action="open-door", message="denied"
                    )
                    logger.debug(f"user not allow")

            elif data["action"] in commands:
                await commands[data["action"]](data)
            else:
                logger.debug(f"command: {data['action']} not found")

            await asyncio.sleep(0.01)

        logger.debug("end process controller command")

    async def process_keypad(self):
        time_stamp = datetime.datetime.now()
        passcode = ""
        while self.running:
            # passcode will expire in 3 sec
            if datetime.datetime.now() > time_stamp + datetime.timedelta(seconds=3):
                passcode = ""

            key = self.keypad.get_key()
            if key is None:
                await asyncio.sleep(0.25)
                continue
            time_stamp = datetime.datetime.now()
            passcode += key
            logger.debug(f"passcode >>> {passcode}")
            if len(passcode) == 6:
                # device_passcode = self.db.search(self.query.passcode == passcode)
                user_passcode = self.db.search(self.query.passcode == passcode)
                if user_passcode:
                    await self.device.open_door()
                    # self.db.insert({
                    #     'username': user_passcode[0]['username'],
                    #     'action': 'open_door',
                    #     'type': 'passcode',
                    #     'datetime': datetime.datetime.now().strftime("%Y, %m, %d, %H, %M, %S"),
                    #     'status': 'wait'
                    #     })
                passcode = ""
                await asyncio.sleep(2)
            await asyncio.sleep(0.2)

    async def read_rfid(self):
        try:
            await self.device.initial(self.key_types)
            while self.running:
                rfid_data = await self.device.rfid.get_tag()

                if len(rfid_data) > 0:
                    await self.rfid_queue.put(rfid_data)
                    await asyncio.sleep(0.5)

                await asyncio.sleep(0.1)
        except Exception as e:
            logger.exception(e)

    async def process_rfid(self):
        while self.running:
            # logger.debug(f'while in process{type(rfid_number)}')
            # rfid_number = self.rfid.get_id()
            if self.rfid_queue.empty():
                await asyncio.sleep(0.1)
                continue

            try:
                rfid_data = await self.rfid_queue.get()
                logger.debug(f"rfid >>> {rfid_data['uid']}")
                # user = await self.db_manager.get_user_by_rfid(rfid_number)
                user = await self.db_manager.get_user_by_rfid_with_current_date(
                    rfid_data["uid"]
                )

                message = "success"
                grant_access = await self.granting_access(user)
                if user and grant_access:
                    await self.device.open_door()
                else:
                    await self.device.play_denied_access_sound()
                    message = "denied"
                    logger.debug(f"There are no user rfid {rfid_data['uid']}")

                identity_number = {}
                if "identity_number" in rfid_data:
                    identity_number["identity_number"] = rfid_data["identity_number"]
                    identity_number["expire_date"] = rfid_data["expire_date"]

                await self.log_manager.put_log(
                    user,
                    type="rfid",
                    action="open-door",
                    rfid=rfid_data["uid"],
                    message=message,
                    **identity_number,
                )

                while not self.rfid_queue.empty():
                    await self.rfid_queue.get()

            except Exception as e:
                logger.exception(e)

    async def process_log(self):
        while self.running:
            # logger.debug('Start to send log to server')
            await self.log_manager.send_log_to_server()
            await asyncio.sleep(5)

    async def listen_open_switch(self):
        force_unlock_max_counter = 10
        while self.running:
            is_open = await self.device.is_turn_on_switch()
            if is_open:
                logger.debug(f"Listen switch {is_open}")
                counter = 0
                while await self.device.is_turn_on_switch():
                    counter += 1
                    await asyncio.sleep(0.1)

                    if counter == force_unlock_max_counter:
                        await self.device.play_success_access_sound(0.2)

                # print("got counter:", counter)
                if counter < force_unlock_max_counter:
                    await self.log_manager.put_log(
                        None, type="switch", action="open-door"
                    )
                    await self.device.open_door()
                    await asyncio.sleep(0.1)
                else:
                    await self.device.force_unlock()

            if not (await self.device.is_access_time()) and self.device.is_force_unlock:
                self.device.is_force_unlock = False
                await self.device.lock_door()
                await self.device.play_success_access_sound(1)
                logger.debug("Force unlock is turned off")

            await asyncio.sleep(0.2)

    async def listen_door_closed(self):
        is_door_opened = False
        while self.running:
            # print('--->', is_door_opened)
            is_opened = await self.device.is_door_opened()
            if is_opened != is_door_opened:
                is_door_opened = is_opened
                # print('state is', is_opened)

                state = "closed"
                if is_opened:
                    state = "opened"

                await self.log_manager.put_log(
                    None,
                    type="switch",
                    action="door-status",
                    state=state,
                )

                if is_opened:
                    logger.debug("door state is opened")
                else:
                    logger.debug("door state is closed")

            await asyncio.sleep(0.5)

    async def register_node(self):
        data = dict(
            action="register",
            device_id=self.device_id,
            date=datetime.datetime.now().isoformat(),
            result="wating",
        )
        while not self.is_register:
            try:
                logger.debug("Try to register node controller")
                response = await self.nc.request(
                    "pichayon.door_controller.greeting",
                    json.dumps(data).encode(),
                    timeout=5,
                )
                data = json.loads(response.data.decode())

                if "key_types" in data:
                    ciphertext = data.get("key_types")
                    del data["key_types"]

                logger.debug(f"-> {data}")
                if (
                    data["action"] == "register"
                    and data["device_id"] == self.device_id
                    and data["status"] == "registed"
                ):
                    self.is_register = True
                    await self.device.update_information(data.get("door", {}))

                    aes_crypto = crypto.AESCrypto(self.device_id)
                    self.key_types = eval(aes_crypto.decrypt(ciphertext))

                    self.cc_id = await self.nc.subscribe(
                        f"pichayon.door_controller.{self.device_id}",
                        cb=self.handle_controller_command,
                    )

                # self.db_manager.initial_data_after_restart(data)
                # logger.debug('Data was saved')
            except Exception as e:
                logger.debug(e)

            if not self.is_register:
                await asyncio.sleep(1)
            logger.debug("Register success")

    async def check_roles(self, user, roles=[]):
        for role in roles:
            if role in user["roles"]:
                return True

        return False

    async def granting_access(
        self, user, roles=["admin", "lecturer", "staff", "supervisor"]
    ):
        if not user:
            return False

        can_access_role = await self.check_roles(user, roles)
        if await self.device.is_access_time() or can_access_role:
            return True

        logger.debug(f"User {user['id']} cannot open door in this time")
        return False

    async def set_up(self):
        # self.read_rfid_thread = threading.Thread(target=self.read_rfid)
        # self.read_rfid_thread.start()

        self.nc = NATS()

        await self.nc.connect(
            self.settings["PICHAYON_MESSAGE_NATS_HOST"],
            max_reconnect_attempts=-1,
            reconnect_time_wait=2,
        )

        await self.log_manager.set_message_client(self.nc)
        await self.device.set_log_manager(self.log_manager)
        logger.debug("setup success")

    async def setup_task(self):
        logging.basicConfig(
            format="%(asctime)s - %(name)s:%(levelname)s:%(lineno)d - %(message)s",
            datefmt="%d-%b-%y %H:%M:%S",
            level=logging.DEBUG,
        )

        await self.device.update_information({})

        while self.running:
            if self.nc and self.nc.is_connected:
                await asyncio.sleep(60)
                continue

            try:
                await self.set_up()
                await self.register_node()
                await self.request_initial_authorization()

            except Exception as e:
                logger.exception(f"Setup error {e}")
                logger.debug("Wait 5s")
                await asyncio.sleep(5)

    def run(self):
        loop = asyncio.get_event_loop()
        # loop.set_debug(True)
        self.running = True

        setup_task = loop.create_task(self.setup_task())
        controller_command_task = loop.create_task(self.process_controller_command())

        logger.debug("start setup device")
        read_rfid_task = loop.create_task(self.read_rfid())
        process_rfid_task = loop.create_task(self.process_rfid())
        listen_switch_task = loop.create_task(self.listen_open_switch())
        listen_door_closed_task = loop.create_task(self.listen_door_closed())
        process_logging_task = loop.create_task(self.process_log())

        # process_access_time_task = loop.create_task(self.process_access_time())

        # process_keypad_task = loop.create_task(self.process_keypad())
        logger.debug("end setup device")
        try:
            loop.run_forever()
        except Exception as e:
            self.running = False
            self.processor_controller.stop_all()
            self.nc.close()
        finally:
            # self.read_rfid_thread.join(timeout=1)
            loop.close()
            GPIO.cleanup()
