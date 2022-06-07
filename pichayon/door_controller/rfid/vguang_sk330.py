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


class RS235Reader:
    def __init__(self, device="/dev/ttyACM0", baudrate=115200):

        # Pin Definitons:
        self.device = device
        self.baudrate = baudrate
        self.timeout = 0.5

        self.data = []
        self.raw_data = []
        self.tag = []
        self.serial = None

        self.read_header = [0x55, 0xAA, 0x00]  # header 0x55 0xAA command word 0x00
        self.running = False
        self.read_queue = asyncio.Queue()
        self.tag_queue = asyncio.Queue()

    async def connect(self):

        self.running = True

        self.reader, self.writer = await serial_asyncio.open_serial_connection(
            url=self.device, baudrate=self.baudrate
        )

        self.read_task = asyncio.create_task(self.wait_for_tag())
        self.tag_verify_task = asyncio.create_task(self.verify_tag())

    async def play_beep(self, seconds=1, times=1):
        command = [0x55, 0xAA, 0x04, 0x01, 0x00]
        control = 0
        red_light = 0b10
        green_light = 0b100
        buzzer = 0b1000

        control = red_light

        command.append(0x08)

        check_byte = await self.calculate_check_byte(command)
        command.append(check_byte)

        x = b"".join([chr(d).encode() for d in command])
        print("play_beep", [f"{d:02X}" for d in command])
        print(x)
        self.writer.write(x)
        self.writer.write(x)
        await self.writer.drain()

    async def wait_for_tag(self):
        while self.running:
            data = await self.reader.read(1)
            await self.read_queue.put(ord(data))

    async def calculate_check_byte(self, data):
        check_byte = data[0]
        for i in data[1:]:
            check_byte = check_byte ^ i

        return check_byte

    async def verify_tag(self):
        # print("verify_tag")
        data_buffer = []
        while self.running:
            data = await self.read_queue.get()
            # print("got->", f"{data:02X}")
            data_buffer.append(data)

            while data_buffer and data_buffer[0] != 0x55:
                data_buffer.pop(0)

            if len(data_buffer) < 7:
                continue

            if len(data_buffer[6:]) >= data_buffer[4] + 1:
                data_arr = data_buffer.copy()
                data_buffer.clear()
                if await self.verify_data(data_arr):
                    await self.tag_queue.put(
                        # "".join([f"{d:02X}" for d in data_arr[6:-1]])
                        "".join([f"{d:02X}" for d in data_arr[8:-1]])
                    )

    async def verify_data(self, data):
        # check header
        if not self.read_header == data[:3]:
            return False

        if data[3] != 0:
            return False

        lenght = data[4]
        if len(data[6:-1]) != lenght:
            return False

        check_byte = await self.calculate_check_byte(data[:-1])

        if check_byte != data[-1]:
            return False

        return True

    async def decrypt(self, raw_data):
        pass

    async def get_id(self):
        tag = await self.tag_queue.get()
        return tag


async def run():
    readerx = RS235Reader("/dev/ttyS0")
    await readerx.connect()
    while True:
        print("wait for tag")
        data = await readerx.get_id()
        print("got =>", data)
        if data == "040031CB494C":
            await readerx.play_beep()


if __name__ == "__main__":
    asyncio.run(run())
