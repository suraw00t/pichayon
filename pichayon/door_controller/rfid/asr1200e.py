"""
## Connecting
Connecting ASR1200E device as wiegand via logic converter.
LED = brown
D0 = white
D1 = green
Ground = black
VCC = Red -> 5, 9-15 V in specification

timeout = 108 * (34 + 1) = 3780 us ~ 0.004 s
"""

import asyncio
import logging
import RPi.GPIO as GPIO
import time

from . import readers

logger = logging.getLogger(__name__)


class WiegandReader(readers.Reader):
    def __init__(self, d0_pin=11, d1_pin=12, beep_pin=37, timeout=0.05):
        super().__init__()

        # Pin Definitons:
        self.d0_pin = 11
        self.d1_pin = 12
        self.beep_pin = 13
        self.timeout = timeout

        GPIO.setup(self.d0_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.d1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.setup(self.beep_pin, GPIO.OUT)
        GPIO.output(self.beep_pin, GPIO.HIGH)

        GPIO.add_event_detect(
            d0_pin,
            GPIO.FALLING,
            callback=self.callback,
        )
        GPIO.add_event_detect(
            d1_pin,
            GPIO.FALLING,
            callback=self.callback,
        )

        self.data = []
        self.start_time = time.monotonic()
        self.is_bit_reading = False

    async def connect(self):
        await super().connect()

    def callback(self, pin):
        if not self.is_bit_reading:
            self.is_bit_reading = True
            self.start_time = time.monotonic()

        if pin == self.d0_pin:
            self.data.append(0)
        else:
            self.data.append(1)

    async def play_success_action(self, seconds=1, times=1):
        await asyncio.sleep(0.2)
        for i in range(times):
            GPIO.output(self.beep_pin, GPIO.LOW)
            await asyncio.sleep(seconds)
            GPIO.output(self.beep_pin, GPIO.HIGH)

    async def play_denied_action(self, seconds=1, times=1):
        await asyncio.sleep(0.2)
        for i in range(times):
            GPIO.output(self.beep_pin, GPIO.LOW)
            await asyncio.sleep(seconds)
            GPIO.output(self.beep_pin, GPIO.HIGH)

    async def wait_for_tag(self):
        while self.running:
            while not self.is_bit_reading:
                await asyncio.sleep(0.0001)

            while time.monotonic() - self.start_time <= self.timeout:
                await asyncio.sleep(0.0001)

            self.is_bit_reading = False
            raw_data = self.data.copy()
            self.data.clear()
            await self.read_queue.put(raw_data)

    async def verify_tag(self):
        while self.running:
            data = await self.read_queue.get()
            if await self.verify_data(data):
                tag = dict(uid=await self.decrypt(data))
                await self.tag_queue.put(tag)

    async def verify_data(self, data):
        if len(data) <= 24:
            return False

        even_parity_bit = data[0]
        odd_parity_bit = data[-1]

        if data[1:17].count(1) % 2 == 0:
            # new version
            # if not even_parity_bit:
            if even_parity_bit:
                return False

        if data[17:-1].count(1) % 2 == 1:
            if not odd_parity_bit:
                return False

        return True

    async def decrypt(self, raw_data):
        data = raw_data[1:-1]

        out = 0
        for bit in data:
            # for new rpi version
            # nbit = bit ^ 1
            # out = (out << 1) | nbit

            out = (out << 1) | bit
        logger.debug(f'>>> {out:08X}')
        return f"{out:08X}"

    async def get_tag(self):
        tag = await self.tag_queue.get()
        return tag
