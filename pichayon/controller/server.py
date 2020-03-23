import asyncio
import logging
import json
from nats.aio.client import Client as NATS
from pichayon import models

logger = logging.getLogger(__name__)
from . import data_resources
#from . import sparkbit

class ControllerServer:
    def __init__(self, settings):
        self.settings = settings
        models.init_mongoengine(settings)
        self.running = False
        self.command_queue = asyncio.Queue()
        self.data_resource = data_resources.DataResourceManager()
        # self.sparkbit_controller = sparkbit.DoorController(self.settings)

    async def handle_sparkbit_command(self, msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        data = json.loads(data)
        # await self.sparkbit_controller.put_command(data)

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
            # logger.debug('before res')
            response = await self.data_resource.get_authorization_data(data['device_id'])
            # logger.debug('after res')
            await self.nc.publish(reply,
                            json.dumps(response).encode())
            logger.debug('client {} is registed'.format(data['device_id']))
        return
    
    async def update_data_to_node_controller(self):
        while self.running:
            logger.debug('start sync data')
            doors = models.Door.objects(status='active', type='pichayon')
            logger.debug('after query')
            for door in doors:
                logger.debug(f'>>>>{door.device_id}')
                if len(door.device_id) == 0:
                    continue
                topic = f'pichayon.node_controller.{door.device_id}'
                response = await self.data_resource.get_authorization_data(door.device_id)
                await self.nc.publish(topic,
                                      json.dumps(response).encode())
            await asyncio.sleep(3600)
            

    async def process_command(self):
        while self.running:

            data = await self.command_queue.get()
            logger.debug('command: {}'.format(data))
            if 'update_passcode' in data['action']:
                door = models.Door.objects.get(id=data['door_id'])
                topic = f'pichayon.node_controller.{door.device_id}'
                logger.debug('update passcode')
                response = await self.data_resource.get_authorization_data(door.device_id)
                await self.nc.publish(topic,
                                json.dumps(response).encode())
                logger.debug('update Success')
                continue
                
            logger.debug('door')
            door = models.Door.objects.get(id=data['door_id'])
            logger.debug('user')
            user = models.User.objects.get(id=data['user_id'])
            logger.debug('user_group')
            user_group = models.UserGroup.objects.get(id=data['user_group_id'])
            door_auth = door.get_door_auth()
            logger.debug(door_auth)

            if not user_group.is_user_member(user):
                continue

            # logger.debug(user_group.name)
            if not door_auth.is_authority(user_group):
                logger.debug('No Authority')
                continue
            if 'sparkbit' in data['type']:
                logger.debug('open sparkbit')
                topic = 'pichayon.controller.sparkbit.command'
                command = dict(door_id=data['door_id'], user_id=data['user_id'], action='open_door')
                logger.debug('set success')
            else:
                topic = f'pichayon.node_controller.{door.device_id}'
                command = dict(device_id=door.device_id, action='open')
            try:
                await self.nc.publish(
                            topic,
                            json.dumps(command).encode())
            except Exception as e:
                logger.exception(e)
            logger.debug('Send Success')

    async def handle_node_controller_log(self, msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        response = dict(
            status='OK'
        )
        await self.nc.publish(reply,
                            json.dumps(response).encode())

    async def set_up(self, loop):
        self.nc = NATS()
        logger.debug('Connecting....')
        await self.nc.connect(self.settings['PICHAYON_MESSAGE_NATS_HOST'], loop=loop)
        logging.basicConfig(
                format='%(asctime)s - %(name)s:%(levelname)s - %(message)s',
                datefmt='%d-%b-%y %H:%M:%S',
                level=logging.DEBUG,
                )
        greeting_topic = 'pichayon.node_controller.greeting'
        command_topic = 'pichayon.controller.command'
        sparkbit_topic = 'pichayon.controller.sparkbit.command'
        logging_topic = 'pichayon.node_controller.send_log'
        logger.debug('OK')

        nc_id = await self.nc.subscribe(
                greeting_topic,
                cb=self.handle_node_controller_greeting
                )
        log_id = await self.nc.subscribe(
                logging_topic,
                cb=self.handle_node_controller_log
                )
        cc_id = await self.nc.subscribe(
                command_topic,
                cb=self.handle_command
                )
        spb_id = await self.nc.subscribe(
                sparkbit_topic,
                cb=self.handle_sparkbit_command
                )

        logger.debug('pichayon setup finish, start door controller')


    def run(self):
        logger.debug('start run')
        self.running = True

        loop = asyncio.get_event_loop()
        logger.debug('start run')
        loop.set_debug(True)
        loop.run_until_complete(self.set_up(loop))
        command_task = loop.create_task(self.process_command())
        # sparkbit_task = loop.create_task(self.sparkbit_controller.process_command())
        handle_update_data_to_node_task = loop.create_task(self.update_data_to_node_controller())
        # handle_controller_task = loop.create_task(self.handle_controller())

        try:
            loop.run_forever()
        except Exception as e:
            print('got:', e)
            self.running = False
            self.sparkbit_controller.stop()
            # self.cn_report_queue.close()
            # self.processor_command_queue.close()
            self.nc.close()
        finally:
            loop.close()

