import datetime
import asyncio
import logging
import requests

from cloudant.client import Cloudant

from pichayon import models

logger = logging.getLogger(__name__) 

class DoorController:
    def __init__(self, settings):
        self.settings = settings

        self.client = Cloudant(
                settings.get('SPARKBIT_API_DATABASE_USERNAME'),
                settings.get('SPARKBIT_API_DATABASE_PASSWORD'),
                url=settings.get('SPARKBIT_API_DATABASE_URL'),
                connect=True,
                auto_renew=True)
        self.session = self.client.session()
        self.command_queue = asyncio.Queue()
        self.running = False

        self.door_status_url = settings.get('SPARKBIT_API_DOOR_STATUS')
        self.door_lock_url = settings.get('SPARKBIT_API_DOOR_LOCK')
        self.door_unlock_url = settings.get('SPARKBIT_API_DOOR_UNLOCK')

    async def put_command(self, data):
        await self.command_queue.put(data)

    async def process_command(self):
        self.running = True
        while self.running:
            command = await self.command_queue.get()
            action = command.get('action', None)
            if not action:
                return

            if action == 'list':
                db = self.client['door-r202-test']
                logger.debug('all document')
                for document in db:
                    logger.debug(document)
            if action == 'add_user':
                self.add_user(command)
            elif action == 'delete_user':
                self.delete_user(command)
            elif action == 'open_door':
                self.open_door(command)
            print('finish cloudant process')

    def stop(self):
        self.running = False
        self.command_queue.put({})

        self.client.disconnect()

    def delete_user(self, command):
        logger.debug('delete user')
        try:
            door = models.Door.objects.get(id=command.get('door_id'))
            user = models.User.objects.get(id=command.get('user_id'))
            sparkbit_door = models.SparkbitDoorSystem.objects.get(door=door)
        except Exception as e:
            logger.exception(e)
            return

        db = self.client[sparkbit_door.device_id]
        doc = db.get_design_document('user-{}'.format(user.system_id))
        doc.delete()

    
    def open_door(self, command):
        logger.debug('open door')
        door = models.Door.objects.get(id=command.get('door_id'))
        user = models.User.objects.get(id=command.get('user_id'))
        sparkbit_door = models.SparkbitDoorSystem.objects(door=door).first()

        if not sparkbit_door:
            logger.debug(f'door id {command.get("door_id")} is not sparkbit member')

        db = self.client[sparkbit_door.device_id]
        if not 'user-{}'.format(user.system_id) in db:
            logger.debug(f'user {user.system_id} is not in db')
            return

        try:
            # response = requests.post(
            #         self.door_unlock_url.format(
            #             sparkbit_door.device_id.replace('door-', '')),
            #         verify=False)
            # logger.debug(response.status_code)
            # if response.status_code != 200:
            #     logger.debug(f'door {user.system_id} is not open')
            #     return

            db = self.client[sparkbit_door.device_id]
            if 'status' not in db:
                logger.debug(f'door {user.system_id} is not open -> no status')
            
            status = db['status']
            status.fetch()

            if status['doorState'] != 'closed':
                logger.debug(f'door {user.system_id} is not open -> status {status["doorState"]}')
                return

            status['lockState'] = 'unlocked'
            status.save()
        
            logger.debug(f'door {user.system_id} is open')
        except Exception as e:
            logger.debug(e)


    def add_user(self, command):
        logger.debug('add user')
        door = None
        try: 
            door_group = models.DoorGroup.objects.get(id=command.get('door_group_id'))
            user = models.User.objects.get(id=command.get('user_id'))
            
            door_auth = models.DoorAuthorization.objects.get(
                    door_group=door_group)
            
        except Exception as e:
            logger.exception(e)

        has_auth = False
        user_group = None

        for auth_group in door_auth.authorization_groups:
            if auth_group.user_group.is_user_member(user):
                has_auth = True
                user_group = models.UserGroupMember.objects.get(
                        user=user,
                        group=auth_group.user_group)
                break

        sparkbit_doors = []
        if has_auth:
            for door in door_group.members:
                sparkbit_door = models.SparkbitDoorSystem.objects.get(door=door)
                sparkbit_doors.append(sparkbit_door)

        for sb_door in sparkbit_doors:
            db = self.client[sb_door.device_id]
            logger.debug(f'db: {db} {sb_door.device_id}')
            logger.debug('user-{}'.format(user.system_id))
            if 'user-{}'.format(user.system_id) in db:
                continue

            data = self.get_document(user, user_group)
            doc = db.create_document(data)


    def get_document(self, user, member_group):

        started_date = int(datetime.datetime.timestamp(
                member_group.started_date) * 1000)
        ended_date = int(datetime.datetime.timestamp(
                member_group.expired_date) * 1000)
        data = dict(
                _id='user-{}'.format(user.system_id),
                thFirstName=user.first_name_th,
                thLastName=user.last_name_th,
                enFirstName=user.first_name,
                enLastName=user.last_name,
                idCardNumber=user.id_card_number,
                calendarsEvents=[
                    dict(
                        startDate=started_date,
                        duration=86400000,
                        endDate=ended_date,
                        rRule=dict(
                            type='text',
                            value='every day'
                            )
                        )
                ],
                isAdmin=False,
                mifareCards=dict(),
                nfcDevices=dict(),
                pin=""
            )
        return data
