import asyncio
import logging
from tinydb import TinyDB, Query

logger = logging.getLogger(__name__)

class DataStorage:
    def __init__(self, settings):
        self.settings = settings
        self.db = TinyDB(self.settings['TINYDB_STORAGE_PATH']) 
        self.query = Query()

    def initial_data_after_restart(self, data):
        self.db.purge()
        self.db.insert({'passcode': data['passcode'], 'type': 'passcode'})
        user_groups = data['user_groups']
        for group in user_groups:
            for member in group['members']:
                user = self.db.search(self.query.username==member['username'])
                if user:
                    continue
                self.db.insert({'username': member['username'], 'rfid': member['rfid'], 'type':'user'})

    def update_data(self, data):
        logger.debug(f'>>>>>>>{data}')
        passcode = self.db.search(self.query.type=='passcode')
        if passcode:
            self.db.update({'passcode': data['passcode']}, self.query.type=='passcode')
        else:
            self.db.insert({'passcode': data['passcode'], 'type': 'passcode'})
        user_groups = data['user_groups']
        users = self.db.search(self.query.type=='user')
        for user in users:
            
        for group in user_groups:
            for member in group['members']:
                user = self.db.search(self.query.username==member['username'])
                if user:
                    continue
                self.db.insert({'username': member['username'], 'rfid': member['rfid']})
        logger.debug(f'>>>>>>>{data}')

