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

from . import vguang_sk330

# import vguang_sk330

logger = logging.getLogger(__name__)


class RS485Reader(vguang_sk330.RS485Reader):
    def __init__(self, key_types={}, device="/dev/ttyACM0", baudrate=115200):
        super().__init__(key_types, device, baudrate)
        
        # self.read_header = [0x55, 0xAA, 0x02]  # header 0x55 0xAA command word 0x02
        self.read_header = [
            0x55,
            0xAA,
            0x30,
        ]  # header 0x55 0xAA command word 0x02

    async def play_success_action(self, seconds=1, times=1):
        command = [0x55, 0xAA, 0x04, 0x05, 0x00]
        control = 0
        red_light = 0b10
        green_light = 0b100
        buzzer = 0b1000
        blue_light = 0b10000

        duration = int(seconds * 1000 / 50)  # event long ms
        if duration > 255:
            duration = 255

        times = times
        interval = 0x01  # between event ms
        keep = 0

        control = buzzer

        control |= green_light

        command.append(control)
        command.extend([times, duration, interval, keep])

        check_byte = await self.calculate_check_byte(command)
        command.append(check_byte)

        # print("play_beep", [hex(d) for d in command])

        byte_command = b"".join([d.to_bytes(1, "big") for d in command])

        await asyncio.sleep(0.2)
        self.writer.write(byte_command)

        await self.writer.drain()

    async def play_denied_action(self, seconds=1, times=1):
        command = [0x55, 0xAA, 0x04, 0x05, 0x00]
        control = 0
        red_light = 0b10
        green_light = 0b100
        buzzer = 0b1000
        blue_light = 0b10000

        duration = int(seconds * 1000 / 50)  # event long ms
        if duration > 255:
            duration = 255

        times = times
        interval = 0x01  # between event ms
        keep = 0

        control = buzzer

        control |= red_light
        times = 2
        duration = 0x01

        command.append(control)
        command.extend([times, duration, interval, keep])

        check_byte = await self.calculate_check_byte(command)
        command.append(check_byte)

        # print("play_beep", [hex(d) for d in command])

        byte_command = b"".join([d.to_bytes(1, "big") for d in command])

        await asyncio.sleep(0.2)
        self.writer.write(byte_command)

        await self.writer.drain()

    async def verify_tag(self):
        # print("verify_tag")
        data_buffer = []
        buffer_index = 1
        tag_dict = {}
        while self.running:
            data = await self.read_queue.get()
            data_buffer.append(data)

            while data_buffer and data_buffer[0] != 0x55:
                data_buffer.pop(0)

            if len(data_buffer) < 7:
                continue

            if len(data_buffer[6:-1]) >= data_buffer[4] + data_buffer[5] and buffer_index == 1:
                data_arr = data_buffer.copy()
                data_buffer.clear()
                
                if await self.verify_data(data_arr):
                    await self.read_sector0()
                    buffer_index = 2
                    tag_dict["uid"] = "".join([f"{d:02X}" for d in data_arr[6:-1]])

            elif len(data_buffer[6:-1]) >= data_buffer[4] + data_buffer[5] and buffer_index == 2:
                data_arr2 = data_buffer.copy()
                data_buffer.clear()

                if await self.verify_sector0_data(data_arr2):
                    sector0_data = data_arr2[6:-1]
                    identity_number, expire_date, _ = [ "".join([chr(d) for d in sector0_data[i:i+16] if d]) for i in range(0, len(sector0_data), 16)]
                    tag_dict["identity_number"] = identity_number
                    tag_dict["expire_date"] = expire_date
                    logger.debug(f"Identity number({len(identity_number)}): {str(identity_number)} expire date({len(expire_date)}): {str(expire_date)}")

                await self.tag_queue.put(**tag_dict)
                buffer_index = 1
                tag_dict.clear()

            elif len(data_buffer[6:-1]) > data_buffer[4] + data_buffer[5]:
                data_buffer.clear()
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
        byte_command = b"".join([d.to_bytes(1, "big") for d in self.command_read_sector0])
        self.writer.write(byte_command)
        await self.writer.drain()


    async def read_default_sector0(self):
        byte_command = b"".join([d.to_bytes(1, "big") for d in self.command_read_default_sector0])
        self.writer.write(byte_command)
        await self.writer.drain()


    async def decrypt(self, raw_data):
        pass

    async def get_data(self):
        tag = await self.tag_queue.get()
        return tag

async def run():
    # readerx = RS485Reader("/dev/ttyACM0")
    # readerx = RS485Reader("/dev/ttyS0")
    readerx = RS485Reader("/dev/ttyS0")
    await readerx.connect()
    while True:
        print("wait for tag")
        data = await readerx.get_id()
        print("got =>", data)


if __name__ == "__main__":
    asyncio.run(run())
