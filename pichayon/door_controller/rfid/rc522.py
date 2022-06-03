import asyncio
import logging
import RPi.GPIO as GPIO
import time
from pirc522 import RFID

logger = logging.getLogger(__name__)
"""
## Connecting
Connecting RC522 module to SPI is pretty easy. You can use [this neat website](http://pi.gadgetoid.com/pinout) for reference.

| Board pin name | Board pin | Physical RPi pin | RPi pin name | Beaglebone Black pin name |
|----------------|-----------|------------------|--------------| --------------------------|
| SDA            | 1         | 24               | GPIO8, CE0   | P9\_17, SPI0\_CS0         |
| SCK            | 2         | 23               | GPIO11, SCKL | P9\_22, SPI0\_SCLK        |
| MOSI           | 3         | 19               | GPIO10, MOSI | P9\_18, SPI0\_D1          |
| MISO           | 4         | 21               | GPIO9, MISO  | P9\_21, SPI0\_D0          |
| IRQ            | 5         | 18               | GPIO24       | P9\_15, GPIO\_48          |
| GND            | 6         | 6, 9, 20, 25     | Ground       | Ground                    |
| RST            | 7         | 22               | GPIO25       | P9\_23, GPIO\_49          |
| 3.3V           | 8         | 1,17             | 3V3          | VDD\_3V3                  |

"""


class RC522RFIDReader:
    def __init__(self):
        # GPIO.setmode(GPIO.BCM)
        # self.reader = RFID(pin_mode=GPIO.BCM)
        # GPIO.setmode(GPIO.BOARD)
        # print(GPIO.getmode())
        self.reader = RFID()
        # self.buzzer = 4
        # GPIO.setup(self.buzzer, GPIO.OUT)
        # GPIO.output(self.buzzer, GPIO.LOW)

    async def uid_to_num(self, uid):
        n = 0
        for i in range(0, 5):
            n = n * 256 + uid[i]
        return n

    async def uid_to_hex(self, uid):
        hexs = []
        for num in uid:
            hexs.append(f"{num:02X}")

        return "".join(hexs)

    async def get_id(self):
        # while True:
        # logger.debug('okayy')
        self.reader.wait_for_tag()
        try:
            (error, tag_type) = self.reader.request()
            if not error:

                (error, uid) = self.reader.anticoll()

                if not error:
                    self.reader.stop_crypto()
                    # print(f'---> {uid}')
                    # return str(self.uid_to_num(uid))
                    # print(f'-->{self.uid_to_hex(uid)}')
                    return await self.uid_to_hex(uid)
        except Exception as e:
            logger.exception(e)
        return ""
