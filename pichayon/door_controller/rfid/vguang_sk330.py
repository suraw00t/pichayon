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
from . import readers

logger = logging.getLogger(__name__)


class RS485Reader(readers.Reader):
    def __init__(
        self, key_types={}, door_config={}, device="/dev/ttyACM0", baudrate=115200
    ):
        super().__init__()

        # Pin Definitons:
        self.device = device
        self.baudrate = baudrate
        self.timeout = 0.5

        self.key_types = key_types
        self.door_config = door_config
        self.command_read_sector0 = self.get_command_read_sector0()
        self.command_read_default_sector0 = self.get_command_read_default_sector0()
        self.data = []
        self.raw_data = []
        self.tag = []
        self.serial = None

        self.read_header = [0x55, 0xAA, 0x00]  # header 0x55 0xAA command word 0x00

    async def connect(self):
        self.reader, self.writer = await serial_asyncio.open_serial_connection(
            url=self.device, baudrate=self.baudrate
        )

        await super().connect()

        turn_off_swiping_light_command = [0x55, 0xAA, 0x24, 0x01, 0x00, 0x00, 0xDA]
        byte_command = b"".join(
            [d.to_bytes(1, "big") for d in turn_off_swiping_light_command]
        )
        self.writer.write(byte_command)
        await self.writer.drain()

    async def play_success_action(self, seconds=1, times=1):
        # command = [0x55, 0xAA, 0x04, 0x01, 0x00]
        command = [0x55, 0xAA, 0x04, 0x01, 0x00]
        control = 0
        # red_light = 0b10
        green_light = 0b100
        buzzer = 0b1000

        control = buzzer | green_light

        command.append(control)
        check_byte = await self.calculate_check_byte(command)
        command.append(check_byte)

        byte_command = b"".join([d.to_bytes(1, "big") for d in command])

        await asyncio.sleep(0.3)
        self.writer.write(byte_command)
        await self.writer.drain()
        await asyncio.sleep(0.05)
        self.writer.write(byte_command)
        await self.writer.drain()
        await asyncio.sleep(0.05)
        self.writer.write(byte_command)
        await self.writer.drain()

    async def play_denied_action(self, seconds=1, times=1):
        command = [0x55, 0xAA, 0x04, 0x01, 0x00]
        control = 0
        # red_light = 0b10
        green_light = 0b100
        buzzer = 0b1000
        # blue_light = 0b10000

        control = buzzer

        command.append(control)
        check_byte = await self.calculate_check_byte(command)
        command.append(check_byte)

        byte_command = b"".join([d.to_bytes(1, "big") for d in command])

        await asyncio.sleep(0.3)
        self.writer.write(byte_command)
        await self.writer.drain()
        await asyncio.sleep(0.2)
        self.writer.write(byte_command)
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
        buffer_index = 1
        while self.running:
            data = await self.read_queue.get()
            # print("got->", f"{data:02X}")
            data_buffer.append(data)

            while data_buffer and data_buffer[0] != 0x55:
                data_buffer.pop(0)

            if len(data_buffer) < 7:
                continue

            # print(data_buffer)
            if (
                len(data_buffer[6:-1]) >= data_buffer[4] + data_buffer[5]
                and buffer_index == 1
            ):
                data_arr = data_buffer.copy()
                data_buffer.clear()
                tag_dict = {}

                if await self.verify_data(data_arr):
                    tag_dict["uid"] = "".join([f"{d:02X}" for d in data_arr[8:-1]])
                    if self.key_types.get(
                        "key_type_a_sector_0"
                    ) and self.door_config.get("allow_read_sector0"):
                        await self.read_sector0()
                        buffer_index = 2
                    else:
                        await self.tag_queue.put(tag_dict)

            elif (
                len(data_buffer[6:-1]) >= data_buffer[4] + data_buffer[5]
                and buffer_index == 2
            ):
                data_arr2 = data_buffer.copy()
                data_buffer.clear()

                if await self.verify_sector0_data(data_arr2):
                    sector0_data = data_arr2[6:-1]
                    identity_number, expire_date, _ = [
                        "".join([chr(d) for d in sector0_data[i : i + 16] if d])
                        for i in range(0, len(sector0_data), 16)
                    ]
                    tag_dict["identity_number"] = identity_number
                    tag_dict["expire_date"] = expire_date
                    logger.debug(
                        f"Identity number({len(identity_number)}): {str(identity_number)} expire date({len(expire_date)}): {str(expire_date)}"
                    )

                await self.tag_queue.put(tag_dict)
                buffer_index = 1

    async def verify_data(self, data):
        # check header
        if not self.read_header == data[:3]:
            return False

        if data[3] != 0:
            return False

        lenght = data[4] + data[5]
        if len(data[6:-1]) != lenght:
            return False

        check_byte = await self.calculate_check_byte(data[:-1])

        if check_byte != data[-1]:
            return False

        return True

    async def verify_sector0_data(self, data):
        data_header = [0x55, 0xAA, 0xA0]
        if not data_header == data[:3]:
            return False

        if data[3] != 0:
            return False

        lenght = data[4] + data[5]
        if len(data[6:-1]) != lenght:
            return False

        check_byte = await self.calculate_check_byte(data[:-1])

        if check_byte != data[-1]:
            return False

        return True

    async def read_sector0(self):
        byte_command = b"".join(
            [d.to_bytes(1, "big") for d in self.command_read_sector0]
        )
        self.writer.write(byte_command)
        await self.writer.drain()

    async def read_default_sector0(self):
        byte_command = b"".join(
            [d.to_bytes(1, "big") for d in self.command_read_default_sector0]
        )
        self.writer.write(byte_command)
        await self.writer.drain()

    async def get_tag(self):
        tag = await self.tag_queue.get()
        return tag

    def get_command_read_sector0(self):
        key_type_a = self.key_types.get("key_type_a_sector_0", {})
        command_read_sector0 = [
            0x55,
            0xAA,
            0xA0,
            0x0B,
            0x00,
            0x00,
            0x60,
            0x00,
            0x01,
            0x03,
        ]
        key_type_a_list = [
            int(key_type_a[i : i + 2], 16) for i in range(0, len(key_type_a), 2)
        ]
        command_read_sector0.extend(key_type_a_list + [0x37])

        return command_read_sector0

    def get_command_read_default_sector0(self):
        default_key_type_a = self.key_types.get("default_key_type_a", {})
        command_read_default_sector0 = [
            0x55,
            0xAA,
            0xA0,
            0x0B,
            0x00,
            0x00,
            0x60,
            0x00,
            0x01,
            0x03,
        ]
        key_type_a_list = [
            int(default_key_type_a[i : i + 2], 16)
            for i in range(0, len(default_key_type_a), 2)
        ]
        command_read_default_sector0.extend(key_type_a_list + [0x36])

        return command_read_default_sector0


async def run():
    readerx = RS485Reader(device="/dev/ttyS0")
    await readerx.connect()
    while True:
        print("wait for tag")
        data = await readerx.get_tag()
        print("got =>", data)


if __name__ == "__main__":
    asyncio.run(run())
