"""
## Connecting
Connecting Vguang SK330 device as RS485 via rs 232.
A = white
B = green
Ground = black
VCC
"""

import asyncio
import logging
import time

import serial_asyncio

logger = logging.getLogger(__name__)


class Reader:
    def __init__(self):

        self.running = False
        self.read_queue = asyncio.Queue()
        self.tag_queue = asyncio.Queue()

    async def connect(self):

        self.running = True

        self.read_task = asyncio.create_task(self.wait_for_tag())
        self.tag_verify_task = asyncio.create_task(self.verify_tag())

    async def play_success_action(self, seconds=1, times=1):
        pass

    async def play_denied_action(self, seconds=1, times=1):
        pass

    async def verify_tag(self):
        while self.running:
            tag = self.read_queue.get()
            self.tag_queue.push(tag)

    async def wait_for_tag(self):
        while self.running:
            self.read_queue.put(None)
            asyncio.sleep(10)

    async def get_id(self):
        tag = await self.tag_queue.get()
        return tag
