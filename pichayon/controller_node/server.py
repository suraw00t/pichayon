import asyncio

import json
import datetime
import os

import logging
logger = logging.getLogger(__name__)

from nats.aio.client import Client as NATS
from nats.aio.errors import ErrTimeout

from . import devices
from . import keypad
from . import rfid

class NodeControllerServer:
    def __init__(self, settings):
        self.settings = settings
        self.is_register = False
        self.controller_command_queue = asyncio.Queue()
        self.device = devices.Device()
        self.device_id = self.device.get_device_id()
        self.running = False
        self.keypad = keypad.Keypad()
        # self.passcode = ''
        self.rfid = rfid.RFID()
    
    async def handle_controller_command(self, msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        data = json.loads(data)
        await self.controller_command_queue.put(data)
        # logger.debug(data)

    async def process_controller_command(self):
        while self.running:
            data = await self.controller_command_queue.get()
            logger.debug('process command')
            if data['action'] == 'open':
                await self.device.open_door()

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
            logger.debug(f'>>>{passcode}')
            if len(passcode) == 6:
                passcode = ''
                await asyncio.sleep(1)
            await asyncio.sleep(.25)
    
    async def process_rfid(self):
        while self.running:
            id_read = self.rfid.get_id()
            if id_read:
                logger.debug(f'>>>{id_read}')
            await asyncio.sleep(1)

    async def set_up(self, loop):
        self.nc = NATS()
        await self.nc.connect(self.settings['PICHAYON_MESSAGE_NATS_HOST'], loop=loop)
        
        logging.basicConfig(
                format='%(asctime)s - %(name)s:%(levelname)s - %(message)s',
                datefmt='%d-%b-%y %H:%M:%S',
                level=logging.DEBUG,
                )
 
        data = dict(action='register',
                    device_id=self.device_id,
                    data=datetime.datetime.now().isoformat()
                    )
        command_topic = f'pichayon.node_controller.{self.device_id}'
        cc_id = await self.nc.subscribe(
                command_topic,
                cb=self.handle_controller_command)
        while not self.is_register:        
            try:
                logger.debug('Try to register node controller')
                response = await self.nc.request(
                        'pichayon.node_controller.greeting',
                        json.dumps(data).encode(),
                        timeout=5
                        )
                self.is_register = True
                data = json.loads(response.data.decode())
                logger.debug(data)
            except Exception as e:
                logger.debug(e)

            if not self.is_register:
                await asyncio.sleep(1)
        
        logger.debug('Register success')


    def run(self):
        loop = asyncio.get_event_loop()
        # loop.set_debug(True)
        self.running = True
    
        loop.run_until_complete(self.set_up(loop))
        # controller_command_task = loop.create_task(self.a())
        controller_command_task = loop.create_task(self.process_controller_command())
        process_keypad_task = loop.create_task(self.process_keypad())
        process_rfid_task = loop.create_task(self.process_rfid())
        
        try:
            loop.run_forever()
        except Exception as e:
            self.running = False
            self.processor_controller.stop_all()
            self.nc.close()
        finally:
            loop.close()

