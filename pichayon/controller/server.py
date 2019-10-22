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

    async def handle_command(self, msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        # logger.debug("Received a rpc message on '{subject} {reply}': {data}".format(
        #         subject=msg.subject, reply=msg.reply, data=msg.data.decode()))
        data = json.loads(data)
        await self.command_queue.put(data)

    async def set_up(self, loop):
        self.nc = NATS()
        await self.nc.connect(self.settings['PICHAYON_MESSAGE_NATS_HOST'], loop=loop)
        logging.basicConfig(
                format='%(asctime)s - %(name)s:%(levelname)s - %(message)s',
                datefmt='%d-%b-%y %H:%M:%S',
                level=logging.DEBUG,
                )


        report_topic = 'pichayon.processor.report'
        command_topic = 'pichayon.processor.command'

        # ps_id = await self.nc.subscribe(
        #         report_topic,
        #         cb=self.handle_processor_report)
        cs_id = await self.nc.subscribe(
                command_topic,
                cb=self.handle_command)

    def run(self):
        self.running = True
        loop = asyncio.get_event_loop()
        # loop.set_debug(True)
        loop.run_until_complete(self.set_up(loop))
        # cn_report_task = loop.create_task(self.process_compute_node_report())
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

