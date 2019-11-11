import asyncio
import logging
import json
from nats.aio.client import Client as NATS
from pichayon import models

logger = logging.getLogger(__name__)


class ControllerServer:
    def __init__(self, settings):
        self.settings = settings
        models.init_mongoengine(settings)
        self.running = False
        self.command_queue = asyncio.Queue()
    
    async def handle_node_controller_greeting(self, msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        logger.debug('Yes')
        
        data = json.loads(data)
        if data['action'] == 'register':
            # response = await self.register_node_controller(data)
            response = {'data':1}
            await self.nc.publish(reply,
                            json.dumps(response).encode())
            logger.debug('client {} is registed'.format(data['device_id']))
            return
        await self.cn_report_queue.put(data)

    async def set_up(self, loop):
        self.nc = NATS()
        await self.nc.connect(self.settings['PICHAYON_MESSAGE_NATS_HOST'], loop=loop)
        logging.basicConfig(
                format='%(asctime)s - %(name)s:%(levelname)s - %(message)s',
                datefmt='%d-%b-%y %H:%M:%S',
                level=logging.DEBUG,
                )
        greeting_topic = 'pichayon.node_controller.greeting'
        logger.debug('OK')

        nc_id = await self.nc.subscribe(
                greeting_topic,
                cb=self.handle_node_controller_greeting)
        # cs_id = await self.nc.subscribe(
        #         command_topic,
        #         cb=self.handle_command)

    def run(self):
        self.running = True
        loop = asyncio.get_event_loop()
        # loop.set_debug(True)
        loop.run_until_complete(self.set_up(loop))
        # processor_command_task = loop.create_task(self.process_processor_command())
        # handle_expired_data_task = loop.create_task(self.process_expired_controller())
        # handle_controller_task = loop.create_task(self.handle_controller())

        try:
            loop.run_forever()
        except Exception as e:
            print(e)
            self.running = False
            # self.cn_report_queue.close()
            # self.processor_command_queue.close()
            self.nc.close()
        finally:
            loop.close()

