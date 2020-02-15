import datetime
import asyncio
import logging

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
        self.door_unlock_url = settings.get('SPARKBIT_API_DOOR_UNLOCLK')

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


    def add_user(self, command):
        logger.debug('add user')
        door = None
        try: 
            door = models.Door.objects.get(id=command.get('door_id'))
            user = models.User.objects.get(id=command.get('user_id'))
            sparkbit_door = models.SparkbitDoorSystem.objects.get(door=door)
            user_group_member = models.UserGroupMember.objects.get(user=user)
            door_group = models.DoorGroup.objects(members=door).first()

            door_auth = models.DoorAuthorizations.objects(door_group=door_group).first()
            if not door_auth.is_group_member(user_group_member.group):
                return
        except Exception as e:
            logger.exception(e)

        if not door:
            return

        db = self.client[sparkbit_door.device_id]

        data = get_document(user)

        doc = db.create_document(data)


    def get_document(user, member_group):

        start_date = int(datetime.datetime.timestamp(
                member_group.start_date.date()) * 1000)
        end_date = int(datetime.datetime.timestamp(
                member_group.expired_date.date()) * 1000)
        data = dict(
                _id='user-{}'.format(user.system_id),
                thFirstName=user.first_name_th,
                thLastName=user.last_name_th,
                enFirstName=user.first_name,
                enLastName=user.last_name,
                idCardNumber=user.id_card_number,
                calendarsEvents=[
                    dict(
                        startDate=start_date,
                        duration=86400000,
                        endDate=end_date,
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
