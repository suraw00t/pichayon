import asyncio
import logging
import pathlib

from tinydb import TinyDB, Query
import json

logger = logging.getLogger(__name__)

class LogManager:
    def __init__(self, data_storage, device_id):
        self.data_storage = data_storage
        self.device_id = device_id

    async def set_message_client(self, client):
        self.message_client = client

    async def send_log_to_server(self):
        is_send = False
        query = Query()
        while not is_send:
            logs = await self.data_storage.get_waiting_logs()
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
        
