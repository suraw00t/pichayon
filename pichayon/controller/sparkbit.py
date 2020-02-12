import datetime
import asyncio
import logging

from cloudant.client import Cloudant

logger = logging.getLogger(__name__) 

class DoorController:
    def __init__(self, settings):
        self.settings = settings

        self.client = Cloudant(
                settings.get('SPARKBIT_APT_USERNAME'),
                settings.get('SPARKBIT_APT_PASSWORD'),
                url=settings.get('SPARKBIT_APT_URL'),
                connect=True,
                auto_renew=True)
        self.session = self.client.session()
        self.command_queue = asyncio.Queue()
        self.running = False

    async def put_command(self, data):
        await self.command_queue.put(data)

    async def process(self):
        self.running = True
        logger.debug('Databases: {0}'.format(client.all_dbs()))
        while self.running:
            data = await self.command_queue.get()
            action = data.get('action', '')
            if action == 'add_user':
                print('add user')
                user = get_document()
                db = client['door-r202-test']
                doc = db.create_document(data)
            elif action == 'delete_user':
                db = client['door-r202-test']
                doc = db.get_design_document('user_id')
                doc.delete()
            print('finish cloudant process')

    def stop(self):
        self.running = False
        self.command_queue.put({})

        self.client.disconnect()

    def get_document(user_id, start_date, end_date, **params):
        start_date = int(datetime.datetime.timestamp(
                start_date.date()) * 1000)
        end_date = int(datetime.datetime.timestamp(
                end_date.date()) * 1000)
        data = dict(
                _id='user-{}'.format(user_id),
                thFirstName=params.get('th_first_name', ''),
                thLastName=params.get('th_last_name', ''),
                enFirstName=params.get('en_first_name', ''),
                enLastName=params.get('en_last_name', ''),
                idCardNumber=params.get('id_card_number', ''),
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
