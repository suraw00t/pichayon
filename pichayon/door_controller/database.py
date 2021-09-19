import asyncio
import logging
import pathlib

from tinydb import TinyDB, Query
import json

logger = logging.getLogger(__name__)

class Manager:
    def __init__(self, settings, device_id):
        self.settings = settings
        dbpath = pathlib.Path(self.settings['TINYDB_STORAGE_PATH'])
        dbpath.parent.mkdir(parents=True, exist_ok=True)
        self.db = TinyDB(str(dbpath))
        self.user = self.db.table('users')
        self.log = self.db.table('logs')

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
       
        
        if data['action'] == 'revoke':
            self.user.truncate()

        user_groups = data['user_groups']
        #for user in users:

        User = Query()

        for group in user_groups:
            for member in group['members']:
                user = self.user.get(User.id==member['id'])
                if user:
                    user.update(member)
                    self.user.update(user)
                else:
                    self.user.insert(
                            member
                            )


    async def get_user_by_rfid(self, rfid_number):
        User = Query()

        def filter(ids, rfid_number):
            for id in ids:
                if id['identifier'].upper() == rfid_number.upper():
                    return True
            return False

        user = self.user.get(User.identifiers.test(filter, rfid_number))

        return user

    async def put_log(self, log):
        self.log.insert(log)

    async def get_waiting_logs(self):
        query = Query()
        logs = self.db.search(query.status=='wait')
      
        return logs
