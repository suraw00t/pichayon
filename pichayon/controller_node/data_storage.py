import asyncio
import logging
from tinydb import TinyDB, Query
import json

logger = logging.getLogger(__name__)

class DataStorage:
    def __init__(self, settings):
        self.settings = settings
        self.db = TinyDB(self.settings['TINYDB_STORAGE_PATH']) 
        self.query = Query()

    def initial_data_after_restart(self, data):
        logger.debug('Initial data')
        self.db.purge()
        user_groups = data['user_groups']
        for group in user_groups:
            for member in group['members']:
                user = self.db.search(self.query.username==member['username'])
                if user:
                    continue
                self.db.insert({'username': member['username'], 'rfid': member['rfid'], 'passcode': member['passcode'], 'type':'user'})

    def update_data(self, data):
        logger.debug(f'>>>>>>>{data}')
        self.db.purge()
        user_groups = data['user_groups']
        #for user in users:
        for group in user_groups:
            for member in group['members']:
                user = self.db.search(self.query.username==member['username'])
                if user:
                    continue
                self.db.insert(
                        {'username': member['username'],
                         'rfid': member['rfid'],
                         'passcode': member['passcode']})
        logger.debug(f'>>>>>>>{data}')

    def send_log_to_server(self, device_id):
        logger.debug('Start to send log to server')
        is_send = False
        while not is_send:
            logs = self.db.search(self.query.status=='wait')
            data = dict(
                device_id=device_id,
                data=logs
            )
            try:
                response = await self.nc.request(
                                'pichayon.node_controller.send_log',
                                json.dumps(data).encode(),
                                timeout=5
                            )
                is_send = True
                db.update({'status': 'send'}, self.query.status=='wait')
                logger.debug('Data was send')
            except Exception as e:
                logger.debug(e)

            if not is_send:
                await asyncio.sleep(1)
        
        logger.debug('Send success')
