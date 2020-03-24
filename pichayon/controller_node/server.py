import asyncio
import threading
import json
import datetime
import os
import time
import logging
import RPi.GPIO as GPIO
logger = logging.getLogger(__name__)

from nats.aio.client import Client as NATS
from nats.aio.errors import ErrTimeout
from tinydb import TinyDB, Query
from . import devices
from . import keypad
from . import rfid
from . import data_storage


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
        self.id_read = '' 
        self.rfid = rfid.RFIDReader()
        self.data_storage = data_storage.DataStorage(self.settings)
        self.db = TinyDB(self.settings['TINYDB_STORAGE_PATH'])
        self.query = Query()


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
                await asyncio.sleep(.5)
                continue
            elif data['action'] == 'update':
                self.data_storage.update_data(data)
                await asyncio.sleep(.5)
                continue
            await asyncio.sleep(.5)


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
            logger.debug(f'passcode: >>>{passcode}')
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
        while self.running:
            self.id_read = self.rfid.get_id()
            if len(self.id_read) > 0:
                time.sleep(.5)
            time.sleep(.5)
            # logger.debug(f'rfid in read rfid>>>{self.id_read}')
         
    async def process_rfid(self):

        while self.running:

            #logger.debug(f'while in process{type(self.id_read)}')
            #self.id_read = self.rfid.get_id()
            try:
                if len(self.id_read)>0:
                    logger.debug(f'rfid: >>>{self.id_read}')
                    user_rfid = self.db.search(self.query.rfid == self.id_read)
                    if user_rfid:
                        await self.device.open_door()
                        self.db.insert({
                            'username': user_rfid[0]['username'],
                            'action': 'open_door',
                            'type': 'rfid',
                            'datetime': datetime.datetime.now().strftime("%Y, %m, %d, %H, %M, %S"),
                            'status': 'wait'
                            })
                        await asyncio.sleep(.5)
                    # self.id_read = ''
            except Exception as e:
                logger.exception(e)
            await asyncio.sleep(.025)

    async def process_log(self):
        while self.running:
            logger.debug('Start to send log to server')
            is_send = False
            while not is_send:
                logs = self.db.search(self.query.status=='wait')
                if len(logs) == 0:
                    await asyncio.sleep(1)
                    continue
                data = dict(
                    device_id=self.device_id,
                    data=logs
                )
                try:
                    response = await self.nc.request(
                                    'pichayon.node_controller.send_log',
                                    json.dumps(data).encode(),
                                    timeout=5
                                )
                    is_send = True
                    self.db.update({'status': 'send'}, self.query.status=='wait')
                    self.db.remove(self.query.status == 'send')
                    logger.debug('Data was send')
                except Exception as e:
                    logger.debug(e)

                if not is_send:
                    await asyncio.sleep(1)
            
            logger.debug('Send success')
            await asyncio.sleep(5)

    async def register_node(self):
        data = dict(action='register',
                device_id=self.device_id,
                data=datetime.datetime.now().isoformat()
                )
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
                self.data_storage.initial_data_after_restart(data)
                logger.debug('Data was saved')
            except Exception as e:
                logger.debug(e)

            if not self.is_register:
                await asyncio.sleep(1)
            
        logger.debug('Register success')

    async def set_up(self, loop):
        self.nc = NATS()
        await self.nc.connect(self.settings['PICHAYON_MESSAGE_NATS_HOST'], loop=loop)
        
        logging.basicConfig(
                format='%(asctime)s - %(name)s:%(levelname)s - %(message)s',
                datefmt='%d-%b-%y %H:%M:%S',
                level=logging.DEBUG,
                )
 

        command_topic = f'pichayon.node_controller.{self.device_id}'
        cc_id = await self.nc.subscribe(
                command_topic,
                cb=self.handle_controller_command)
        self.read_rfid_thread = threading.Thread(target=self.read_rfid)
        self.read_rfid_thread.start()
        logger.debug('setup success')


    def run(self):
        loop = asyncio.get_event_loop()
        # loop.set_debug(True)
        self.running = True
    
        loop.run_until_complete(self.set_up(loop))
        register_node_task = loop.create_task(self.register_node())
        # controller_command_task = loop.create_task(self.a())
        controller_command_task = loop.create_task(self.process_controller_command())
        process_keypad_task = loop.create_task(self.process_keypad())
        process_rfid_task = loop.create_task(self.process_rfid())
        process_logging_task = loop.create_task(self.process_log())
        
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

