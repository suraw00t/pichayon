'''
## Connecting
Connecting ASR1200E device as wiegand via logic converter.
LED = brown
D0 = white
D1 = green
Ground = black
VCC = Red -> 5, 9-15 V in specification

timeout = 108 * (34 + 1) = 3780 us ~ 0.004 s
'''

import asyncio
import logging
import RPi.GPIO as GPIO
import time

logger = logging.getLogger(__name__)
class WiegandReader:
    def __init__(self, d0_pin=11, d1_pin=12, beep_pin=37, timeout=0.05):

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
                d0_pin, GPIO.FALLING,
                callback=self.callback,
                )
        GPIO.add_event_detect(
                d1_pin, 
                GPIO.FALLING, 
                callback=self.callback,
                )

        self.data = []
        self.raw_data = []
        self.tag = []
        self.start_time = time.monotonic()
        self.is_bit_reading = False

    def callback(self, pin):
        if not self.is_bit_reading:
            self.is_bit_reading = True
            self.start_time = time.monotonic()

        if pin == self.d0_pin:
            self.data.append(0)
        else:
            self.data.append(1)
  
    async def play_beep(self, seconds=1, times=1):
        for i in range(times):
            GPIO.output(self.beep_pin, GPIO.LOW)
            await asyncio.sleep(seconds)
            GPIO.output(self.beep_pin, GPIO.HIGH)

    async def wait_for_tag(self):
        while not self.is_bit_reading:
            await asyncio.sleep(0.0001)

        while (time.monotonic() - self.start_time <= self.timeout):
            await asyncio.sleep(0.0001)

        self.is_bit_reading = False
        self.raw_data = self.data.copy()
        self.data.clear()


    async def verify_data(self, data):
        if len(data) <= 24:
            return False

        even_parity_bit = data[0]
        odd_parity_bit = data[-1]
        if data[1: 17].count(1) % 2 == 0:
            if not even_parity_bit:
                return False

        if data[17: -1].count(1) % 2 == 1:
            if not odd_parity_bit:
                return False

        return True

    
    async def decrypt(self, raw_data):
        data = raw_data[1: -1]

        out = 0
        for bit in data:
            nbit = bit ^ 1
            out = (out << 1) | nbit

        return f'{out:X}'

    async def get_id(self):
        #while True:
            #logger.debug('okayy')
        await self.wait_for_tag()
        try:
            if not await self.verify_data(self.raw_data):
                return ''

            tag = await self.decrypt(self.raw_data)

            return tag

        except Exception as e:
            logger.exception(e)

        return ''
