import asyncio
import logging
import json
from nats.aio.client import Client as NATS
from pichayon import models
import datetime

logger = logging.getLogger(__name__)
from . import data_resources
from . import sparkbit

class DoorManager:
    def __init__(self):
        self.nc = None

    async def set_message_client(self, nc):
        self.nc = nc

    async def handle_door_controller_greeting(self, msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()

        data = json.loads(data)
        logger.debug(f'===> {data}')
        if data['action'] == 'register':
            # logger.debug('before res')
            logger.debug(f'client {data["device_id"]} is registering')
            # response = await self.data_resource.get_authorization_data(data['device_id'])
            # logger.debug('after res')
            door = models.Door.objects(device_id=device_id).first()
            response = data
            if door:
                response['status'] = 'registed'
                registed['completed_date'] = datetime.datetime.now()
                door.device_updated_date = datetime.datetime.now()
                door.save()
            else:
                response['status'] = 'rejected'

            await self.nc.publish(
                    reply,
                    json.dumps(response).encode())
            logger.debug('client {} is registed'.format(data['device_id']))
        return
    
    # async def update_data_to_door_controller(self):
    #     while self.running:
    #         logger.debug('start sync data')
    #         doors = models.Door.objects(status='active', type='pichayon')
    #         for door in doors:
    #             logger.debug(f' {door.device_id}')
    #             if len(door.device_id) == 0:
    #                 continue

    #             topic = f'pichayon.door_controller.{door.device_id}'
    #             response = await self.data_resource.get_authorization_data(door.device_id)

    #             await self.nc.publish(
    #                     topic,
    #                     response,
    #                     )

    #         logger.debug('end sync sleep')
    #         await asyncio.sleep(3600)
            
    async def open(self, data):
        door = models.Door.objects.get(id=data['door_id'])
        user = models.User.objects.get(id=data['user_id'])
    
        if not door.is_allow(user):
            logger.debug('No Authority')
            return

        if 'sparkbit' in data['type']:
            if not self.sparkbit_enable:
                logger.debug('Sparkbit Disable')
                return

            logger.debug('open sparkbit')
            topic = 'pichayon.controller.sparkbit.command'
            command = dict(door_id=data['door_id'], user_id=data['user_id'], action='open')
            logger.debug('set success')
        else:
            topic = f'pichayon.door_controller.{door.device_id}'
            command = dict(device_id=door.device_id, user_id=data['user_id'], action='open')


        try:
            await self.nc.publish(
                        topic,
                        json.dumps(command).encode())
        except Exception as e:
            logger.exception(e)
        logger.debug('Send Success')
    '''
    async def handle_door_controller_log(self, msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        logger.debug('start save log')
        data = json.loads(data)
        # logger.debug(f'{type(data)}')
        logger.debug(f"recieve log >>>{data['device_id']}")
        device_id = data['device_id']
        door = models.Door.objects(device_id=device_id).first()
        logs = data['data']
        # logger.debug(f'{door.id}')
        # logger.debug('before loop')

        for log in logs:
            # logger.debug('1 loop')
            y, m, d, h, min, sec = log['datetime'].split(', ')
            # logger.debug('2 loop')
            history_log = models.HistoryLog(
                action = 'open',
                details = {
                    'door': str(door.id),
                    'user': log['username']
                    },
                recorded_date = datetime.datetime(int(y), int(m), int(d), int(h), int(min), int(sec))
            )
            # logger.debug('3 loop')
            if 'passcode' in log['type']:
                history_log.message = f"{log['username']} opened Door: {door.name} via Passcode"
            elif 'rfid' in log['type']:
                history_log.message = f"{log['username']} opened Door: {door.name} via RFID"
            history_log.save()
            # logger.debug('4 loop')

        

        response = dict(
            status='OK'
        )
        await self.nc.publish(reply,
                            json.dumps(response).encode())

    '''
