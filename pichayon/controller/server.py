import asyncio
import logging
import json
from nats.aio.client import Client as NATS
from pichayon import models
import datetime

logger = logging.getLogger(__name__)
from . import data_resources
from . import sparkbit
from . import doors

class ControllerServer:
    def __init__(self, settings):
        self.settings = settings
        models.init_mongoengine(settings)
        self.running = False
        self.command_queue = asyncio.Queue()
        self.data_resource = data_resources.DataResourceManager()
        self.door_manager = doors.DoorManager(self.data_resource)

        self.sparkbit_enable = self.settings.get('SPARKBIT_ENABLE', False)
        if self.sparkbit_enable:
            self.sparkbit_controller = sparkbit.DoorController(self.settings)

    async def handle_sparkbit_command(self, msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        data = json.loads(data)
        await self.sparkbit_controller.put_command(data)

    async def handle_command(self, msg):
        subject = msg.subject
        reply = msg.reply
        raw_data = msg.data.decode()
        data = json.loads(raw_data)
        if type(data) is str:
            data = json.loads(data)

        await self.command_queue.put(data)

    async def handle_door_controller_greeting(self, msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()

        data = json.loads(data)
        if data['action'] != 'register':
            return

        # logger.debug('before res')
        logger.debug(f'client {data["device_id"]} is registering')
        # response = await self.data_resource.get_authorization_data(data['device_id'])
        # logger.debug('after res')
        door = models.Door.objects(
                device_id=data['device_id']).first()
        response = data
        if door:
            response['status'] = 'registed'
            response['door_id'] = str(door.id)
            response['completed_date'] = datetime.datetime.now().isoformat()
            door.device_updated_date = datetime.datetime.now()
            door.save()
        else:
            response['status'] = 'rejected'

        await self.nc.publish(
                reply,
                json.dumps(response).encode(),
                )
        logger.debug('client {} is registed'.format(data['device_id']))


    async def handle_door_controller_log(self, msg):
        await self.door_manager.process_door_controller_log(msg)

    async def update_data_to_door_controller(self):
        
        weak_up = datetime.datetime.combine(
                datetime.date.today(),
                datetime.time(4, 00),
                )
        
        current_date = datetime.datetime.now()
        if current_date > weak_up:
            weak_up = weak_up + datetime.timedelta(days=1)

        while self.running:

            logger.debug('start update data')
            doors = models.Door.objects(status='active', device_type='pichayon')
            for door in doors:
                logger.debug(f'start send data to {door.device_id}')
                if len(door.device_id) == 0:
                    continue
                topic = f'pichayon.door_controller.{door.device_id}'
                response = await self.data_resource.get_authorization_data(door.device_id)
                await self.nc.publish(
                        topic,
                        json.dumps(response).encode())

            # update sleep time
            current_date = datetime.datetime.now()
            logger.debug(f'see you next day {weak_up}')
            await asyncio.sleep((weak_up-current_date).seconds)
            weak_up = weak_up + datetime.timedelta(days=1)

            

    async def process_command(self):
        logger.debug('start process command')
        while self.running:
            data = await self.command_queue.get()
            logger.debug(f'process => {data}')
            # if data['action'] == 'update_passcode':
            #     door = models.Door.objects.get(id=data['door_id'])
            #     topic = f'pichayon.door_controller.{door.device_id}'
            #     logger.debug('update passcode')
            #     response = await self.data_resource.get_authorization_data(door.device_id)
            #     await self.nc.publish(topic,
            #                     json.dumps(response).encode())
            #     logger.debug('update Success')
            #     continue
            if data['action'] == 'request_initial_data':
                logger.debug('got request_initial_data')
                door = models.Door.objects(device_id=data['device_id']).first()
                if not door:
                    continue
                
                topic = f'pichayon.door_controller.{door.device_id}'
                response = await self.data_resource.get_authorization_data(door.device_id)
                logger.debug(f'response {response}')
                await self.nc.publish(
                        topic,
                        json.dumps(response).encode(),
                        )
            elif data['action'] == 'open':
                try:
                    await self.door_manager.open(data)
                except Exception as e:
                    logger.exception(e)
            elif data['action'] == 'add-member-to-group':
                try:
                    await self.door_manager.add_member_to_group(data)
                except Exception as e:
                    logger.exception(e)
            elif data['action'] == 'delete-member-from-group':
                try:
                    await self.door_manager.delete_member_from_group(data)
                except Exception as e:
                    logger.exception(e)
            elif data['action'] == 'update-member':
                try:
                    await self.door_manager.update_member(data)
                except Exception as e:
                    logger.exception(e)

            else:
                logger.debug(f'unprocess command {data}')

        logger.debug('end process command')

    async def set_up(self, loop):
        self.nc = NATS()
        logger.debug('Connecting....')
        await self.nc.connect(self.settings['PICHAYON_MESSAGE_NATS_HOST'], loop=loop)
        await self.door_manager.set_message_client(self.nc)

        logging.basicConfig(
                format='%(asctime)s - %(name)s:%(levelname)s:%(lineno)d - %(message)s',
                datefmt='%d-%b-%y %H:%M:%S',
                level=logging.DEBUG,
                )
        greeting_topic = 'pichayon.door_controller.greeting'
        command_topic = 'pichayon.controller.command'
        sparkbit_topic = 'pichayon.controller.sparkbit.command'
        logging_topic = 'pichayon.door_controller.log'
        logger.debug('OK')

        nc_id = await self.nc.subscribe(
                greeting_topic,
                cb=self.handle_door_controller_greeting
                )
        log_id = await self.nc.subscribe(
                logging_topic,
                cb=self.handle_door_controller_log
                )
        cc_id = await self.nc.subscribe(
                command_topic,
                cb=self.handle_command
                )
        if self.sparkbit_enable:
            spb_id = await self.nc.subscribe(
                    sparkbit_topic,
                    cb=self.handle_sparkbit_command
                    )

            await self.door_manager.set_sparkbit_status(True)

        logger.debug('pichayon setup finish, start door controller')


    def run(self):
        self.running = True

        loop = asyncio.get_event_loop()
        loop.set_debug(True)
        loop.run_until_complete(self.set_up(loop))
        command_task = loop.create_task(self.process_command())
        update_data_task = loop.create_task(self.update_data_to_door_controller())

        if self.sparkbit_enable:
            sparkbit_task = loop.create_task(self.sparkbit_controller.process_command())

        try:
            loop.run_forever()
        except Exception as e:
            print('got:', e)
            self.running = False
            if self.sparkbit_enable:
                self.sparkbit_controller.stop()
            # self.cn_report_queue.close()
            # self.processor_command_queue.close()
            self.nc.close()
        finally:
            loop.close()

