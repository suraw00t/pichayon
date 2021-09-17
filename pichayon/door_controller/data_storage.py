import asyncio
import logging
import pathlib

from tinydb import TinyDB, Query
import json

logger = logging.getLogger(__name__)

class DataStorage:
    def __init__(self, settings, device_id):
        self.settings = settings
        dbpath = pathlib.Path(self.settings['TINYDB_STORAGE_PATH'])
        dbpath.parent.mkdir(parents=True, exist_ok=True)
        self.db = TinyDB(str(dbpath))
        self.User = self.db.table('users')

        self.device_id = device_id

    # def initial_data_after_restart(self, data):
    #     logger.debug('Initial data')
    #     self.db.remove(self.query.type=='user')
    #     user_groups = data['user_groups']
    #     for group in user_groups:
    #         for member in group['members']:
    #             user = self.db.search(self.query.username==member['username'])
    #             if user:
    #                 continue
    #             self.db.insert({'username': member['username'], 'rfid': member['rfid'], 'passcode': member['passcode'], 'type':'user'})

    def update_data(self, data):
        logger.debug(f'>>>>>>>{data}')
       
        
        if 'action' in data and data['action'] == 'revoke':
            self.User.truncate()

        user_groups = data['user_groups']
        #for user in users:

        query = Query()

        for group in user_groups:
            for member in group['members']:
                user = self.User.get(query.id==member['id'])
                if user:
                    user.update(member)
                    self.User.update(user)
                else:
                    self.User.insert(
                            member
                            )

        logger.debug(f'>>>>>>>{data}')

    async def get_user_by_rfid(self, rfid_number):
        query = Query()
        user = self.User.get(query.identifiers.identifier==rfid_number)
        return user


    async def get_waiting_logs(self):
        query = Query()
        logs = self.db.search(query.status=='wait')
      
        return logs
