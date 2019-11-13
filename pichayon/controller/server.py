import asyncio
import logging
import json
from nats.aio.client import Client as NATS
from pichayon import models

logger = logging.getLogger(__name__)
from . import data_resources

class ControllerServer:
    def __init__(self, settings):
        self.settings = settings
        models.init_mongoengine(settings)
        self.running = False
        self.command_queue = asyncio.Queue()
        self.data_resource = data_resources.DataResourceManager()
    
    async def handle_command(self, msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        data = json.loads(data)
        await self.command_queue.put(data)

    async def handle_node_controller_greeting(self, msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        # logger.debug('Yes')
        
        data = json.loads(data)
        if data['action'] == 'register':
            logger.debug('before res')
            response = await self.data_resource.get_authorization_data(data['device_id'])
            logger.debug('after res')
            await self.nc.publish(reply,
                            json.dumps(response).encode())
            logger.debug('client {} is registed'.format(data['device_id']))
        return

    async def process_command(self):
        while self.running:
            data = await self.command_queue.get()
            logger.debug('command: {}'.format(data))
            
            door = models.Door.objects.get(id=data['door_id'])
            user = models.User.objects.get(id=data['user_id'])
            user_group = models.UserGroup.objects(id=data['user_group_id']).first()
            door_auth = door.get_door_auth()
            if not user_group.is_member(user):
                continue

            if not door_auth.is_authority(user_group):
                logger.debug('No Authority')
                continue
            topic = f'pichayon.node_controller.{door.device_id}'
            command = dict(device_id=door.device_id, action='open')
            await self.nc.publish(
                        topic,
                        json.dumps(command).encode())
            logger.debug('Send Success')

    async def set_up(self, loop):
        self.nc = NATS()
        await self.nc.connect(self.settings['PICHAYON_MESSAGE_NATS_HOST'], loop=loop)
        logging.basicConfig(
                format='%(asctime)s - %(name)s:%(levelname)s - %(message)s',
                datefmt='%d-%b-%y %H:%M:%S',
                level=logging.DEBUG,
                )
        greeting_topic = 'pichayon.node_controller.greeting'
        command_topic = 'pichayon.controller.command'
        # logger.debug('OK')

        nc_id = await self.nc.subscribe(
                greeting_topic,
                cb=self.handle_node_controller_greeting)
        cc_id = await self.nc.subscribe(
                command_topic,
                cb=self.handle_command)

    def run(self):
        self.running = True
        loop = asyncio.get_event_loop()
        # loop.set_debug(True)
        loop.run_until_complete(self.set_up(loop))
        command_task = loop.create_task(self.process_command())
        # handle_expired_data_task = loop.create_task(self.process_expired_controller())
        # handle_controller_task = loop.create_task(self.handle_controller())

        try:
            loop.run_forever()
        except Exception as e:
            print(e)
            self.running = False
            # self.cn_report_queue.close()
            # self.processor_command_queue.close()
            self.nc.close()
        finally:
            loop.close()

