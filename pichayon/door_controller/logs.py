import asyncio
import logging
import pathlib
import datetime

from tinydb import TinyDB, Query
import json

logger = logging.getLogger(__name__)

class LogManager:
    def __init__(self, db_manager, device_id):
        self.db_manager = db_manager
        self.device_id = device_id

    async def set_message_client(self, client):
        self.message_client = client

    async def put_log(self, user, action='open-door', type='rfid'):
        log = {
            'username':user['username'] if user else 'system',
            'action': action,
            'type': type,
            'datetime': datetime.datetime.now().isoformat(),
            'status': 'wait',
            }
        await self.db_manager.put_log(log)


    async def send_log_to_server(self):
        is_send = False
        query = Query()
        while not is_send:
            logs = await self.db_manager.get_waiting_logs()
            if not logs:
                return
            logger.debug(f'log {logs}')
            data = dict(
                device_id=self.device_id,
                data=logs
            )
            try:
                response = await self.message_client.request(
                                'pichayon.node_controller.send_log',
                                json.dumps(data).encode(),
                                timeout=5
                            )
                is_send = True
                self.db.update({'status': 'send'}, self.query.status=='wait')
                logger.debug('data was send')
            except Exception as e:
                logger.debug(e)

            if not is_send:
                await asyncio.sleep(1)
        
