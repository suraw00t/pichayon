import asyncio

import json
import datetime
import os

import logging
logger = logging.getLogger(__name__)

from nats.aio.client import Client as NATS
from nats.aio.errors import ErrTimeout

from . import devices


class ControllerNodeServer:
    def __init__(self, settings):
        self.settings = settings
        self.is_register = False
        device = devices.Device()
        self.device_id = device.get_device_id()
        self.running = False

    async def set_up(self, loop):
        self.nc = NATS()
        await self.nc.connect(self.settings['PICHAYON_MESSAGE_NATS_HOST'], loop=loop)
        
        logging.basicConfig(
                format='%(asctime)s - %(name)s:%(levelname)s - %(message)s',
                datefmt='%d-%b-%y %H:%M:%S',
                level=logging.DEBUG,
                )

        # rpc_topic = 'pichayon.controller_node.{}'.format(self.device_id)
        # logger.info('try to subscribe rpc topic: {}'.format(rpc_topic))
        # rpc_sid = await self.nc.subscribe(
        #         rpc_topic,
        #         cb=self.handle_rpc_message)

 
        # data = dict(action='register',
        #             device_id=self.device_id,
        #             data=datetime.datetime.now().isoformat()
        #             )

        while not self.is_register:
            logger.debug('Try to register controller node')
            try:
                response = await self.nc.request(
                        'pichayon.controller_node.report',
                        json.dumps(data).encode(),
                        timeout=5
                        )
                self.is_register = True
                data = json.loads(response.data.decode())
                self.id = data['id']
            except Exception as e:
                logger.debug(e)

            if not self.is_register:
                await asyncio.sleep(1)

        logger.debug('Register success')

    def run(self):
        loop = asyncio.get_event_loop()
        # loop.set_debug(True)
        self.running = True
    
        loop.run_until_complete(self.set_up(loop))
        # update_data_task = loop.create_task(self.update_controller_node_data())
        
        try:
            loop.run_forever()
        except Exception as e:
            self.running = False
            self.processor_controller.stop_all()
            self.nc.close()
        finally:
            loop.close()

