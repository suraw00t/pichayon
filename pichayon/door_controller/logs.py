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

    async def put_log(self, user, action='open-door', type='rfid', **kw_args):
        current_date = datetime.datetime.now()
        log = {
            'id': current_date.timestamp(),
            'actor': 'user' if user else 'system',
            'user_id':user['id'] if user else 'system',
            'action': action,
            'type': type,
            'log_date': datetime.datetime.now().isoformat(),
            'status': 'wait',
            }
        log.update(kw_args)
        await self.db_manager.put_log(log)


    async def send_log_to_server(self):
        logs = await self.db_manager.get_waiting_logs()
        # logger.debug(f'-> {logs}')
        for log in logs:
            data = dict(
                device_id=self.device_id,
                log=log
            )
            # logger.debug(f'send {data}')
            try:
                response = await self.message_client.request(
                                'pichayon.door_controller.log',
                                json.dumps(data).encode(),
                                timeout=5
                            )

                await self.db_manager.delete_log(log['id'])
                
                # logger.debug('data was send')
            except Exception as e:
                logger.exception(e)
                break



        
