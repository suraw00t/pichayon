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

from . import devices
from . import keypad
from . import rfid
from . import database
from . import logs

logger = logging.getLogger(__name__)


class DoorControllerServer:
    def __init__(self, settings):
        self.settings = settings
        self.is_register = False
        self.controller_command_queue = asyncio.Queue()
        self.rfid_queue = asyncio.Queue()

        self.device = devices.Device()
        self.device_id = self.device.get_device_id()
        # self.keypad = keypad.Keypad()
        # self.passcode = ''
        rfid_number = '' 
        self.rfid = rfid.RFIDReader()
        self.db_manager = database.Manager(
                self.settings,
                self.device_id)

        self.log_manager = logs.LogManager(
                self.db_manager,
                self.device_id,
                )

        self.running = False


    async def handle_controller_command(self, msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        data = json.loads(data)
        await self.controller_command_queue.put(data)
        # logger.debug(data)

    async def request_initial_authorization(self):
        data = dict(
                action='request_initial_data',
                device_id=self.device_id,
                )
        await self.nc.publish(
                'pichayon.controller.command',
                json.dumps(data).encode(),
                )

    async def process_controller_command(self):
       
        logger.debug('initial authorization')
        await self.request_initial_authorization()

        logger.debug('start process controller command')
        while self.running:
            data = await self.controller_command_queue.get()

            logger.debug(f'process command -> {data}')
            if data['action'] == 'open':
                await self.device.open_door()
                await asyncio.sleep(.5)
                continue
            elif data['action'] == 'initial':
                self.db_manager.initial_data(data)
                await asyncio.sleep(.5)
                continue
            await asyncio.sleep(.5)

        logger.debug('end process controller command')


    async def process_keypad(self):
        time_stamp = datetime.datetime.now()
        passcode = ''
        while self.running:
            # passcode will expire in 3 sec
            if datetime.datetime.now() > time_stamp+datetime.timedelta(seconds=3):
                passcode = ''

            key = self.keypad.get_key()
            if key is None:
                await asyncio.sleep(.25)
                continue
            time_stamp = datetime.datetime.now()
            passcode += key
            logger.debug(f'passcode >>> {passcode}')
            if len(passcode) == 6:
                # device_passcode = self.db.search(self.query.passcode == passcode)
                user_passcode = self.db.search(self.query.passcode == passcode)
                if user_passcode:
                    await self.device.open_door()
                    self.db.insert({
                        'username': user_passcode[0]['username'],
                        'action': 'open_door',
                        'type': 'passcode',
                        'datetime': datetime.datetime.now().strftime("%Y, %m, %d, %H, %M, %S"),
                        'status': 'wait'
                        })
                passcode = ''
                await asyncio.sleep(2)
            await asyncio.sleep(.2)

    def read_rfid(self):
        loop = asyncio.new_event_loop()
        while self.running:
            rfid_number = self.rfid.get_id()
            if len(rfid_number) > 0:
                loop.run_until_complete(
                    self.rfid_queue.put(rfid_number)
                )
                time.sleep(1)
            time.sleep(.1)
            # logger.debug(f'rfid in read rfid>>>{rfid_number}')
         
    async def process_rfid(self):
        while self.running:

            #logger.debug(f'while in process{type(rfid_number)}')
            #rfid_number = self.rfid.get_id()
            if self.rfid_queue.empty():
                await asyncio.sleep(0.1)
                continue

            rfid_number = await self.rfid_queue.get()
            try:
                logger.debug(f'rfid >>> {rfid_number}')
                # user = await self.db_manager.get_user_by_rfid(rfid_number)
                user = await self.db_manager.get_user_by_rfid_with_current_date(rfid_number)

                print(f'---> {user}')
                if not user:
                    logger.debug('There are no user rfid {rfid_number}')
                    continue

                await self.device.open_door()
                await self.log_manager.put_log(user, type='rfid', action='open-door')
            except Exception as e:
                logger.exception(e)

    async def process_log(self):
        while self.running:
            logger.debug('Start to send log to server')
            await self.log_manager.send_log_to_server()

            logger.debug('Send success')
            await asyncio.sleep(5)

    async def listen_open_switch(self):
        while self.running:
            is_open = await self.device.is_turn_on_switch()
            if is_open:
                logger.debug(f'Listen switch {is_open}')
                await self.device.open_door()
                await self.log_manager.put_log(None, type='switch', action='open-door')
                await asyncio.sleep(0.3)
            await asyncio.sleep(0.1)

    async def listen_door_closed(self):
        is_door_opened = False
        while self.running:
            # print('--->', is_door_opened)
            is_opened = await self.device.is_door_opened()
            if is_opened != is_door_opened:
                is_door_opened = is_opened
                print('state is', is_opened)
                data = dict(
                        device_id=self.device.device_id,
                        state='closed',
                        )
                if is_opened:
                    data['state'] = 'opened'

                await self.nc.publish(
                        'pichayon.controller.door.status',
                        json.dumps(data).encode(),
                        )

                if is_opened:
                    logger.debug('door state is opened')
                else:
                    logger.debug('door state is closed')

            await asyncio.sleep(0.5)

    async def register_node(self):
        data = dict(action='register',
                device_id=self.device_id,
                date=datetime.datetime.now().isoformat(),
                result='wating',
                )
        while not self.is_register:        
            try:
                logger.debug('Try to register node controller')
                response = await self.nc.request(
                        'pichayon.door_controller.greeting',
                        json.dumps(data).encode(),
                        timeout=5
                        )
                data = json.loads(response.data.decode())
                logger.debug(f'-> {data}')
                if data['action'] == 'register' \
                        and data['device_id'] == self.device_id \
                        and data['status'] == 'registed':
                    self.is_register = True
                    self.door_id = data['door_id']

                    self.cc_id = await self.nc.subscribe(
                            f'pichayon.door_controller.{self.device_id}',
                            cb=self.handle_controller_command,
                            )

                # self.db_manager.initial_data_after_restart(data)
                # logger.debug('Data was saved')
            except Exception as e:
                logger.debug(e)

            if not self.is_register:
                await asyncio.sleep(1)
            logger.debug('Register success')
       
    async def set_up(self, loop):
        self.nc = NATS()
        await self.nc.connect(self.settings['PICHAYON_MESSAGE_NATS_HOST'], loop=loop)

        logging.basicConfig(
                format='%(asctime)s - %(name)s:%(levelname)s:%(lineno)d - %(message)s',
                datefmt='%d-%b-%y %H:%M:%S',
                level=logging.DEBUG,
                )

        self.read_rfid_thread = threading.Thread(
                target=self.read_rfid
                )
        self.read_rfid_thread.start()

        await self.log_manager.set_message_client(self.nc)
        logger.debug('setup success')


    def run(self):
        loop = asyncio.get_event_loop()
        # loop.set_debug(True)
        self.running = True
    
        loop.run_until_complete(self.set_up(loop))
        loop.run_until_complete(self.register_node())
        controller_command_task = loop.create_task(self.process_controller_command())
        
        # process_keypad_task = loop.create_task(self.process_keypad())
        process_rfid_task = loop.create_task(self.process_rfid())
        # process_logging_task = loop.create_task(self.process_log())
        listen_switch_task = loop.create_task(self.listen_open_switch())
        listen_door_closed_task = loop.create_task(self.listen_door_closed())

        try:
            loop.run_forever()
        except Exception as e:
            self.running = False
            self.processor_controller.stop_all()
            self.nc.close()
        finally:
            self.read_rfid_thread.join(timeout=1)
            loop.close()
            GPIO.cleanup()

