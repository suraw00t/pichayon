import uuid
import asyncio
import logging
import RPi.GPIO as GPIO
import time
logger = logging.getLogger(__name__)


class Keypad:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.keypad = [
                ['1', '2', '3', "A"],
                ['4', '5', '6', "B"],
                ['7', '8', '9', "C"],
                ["*", '0', "#", "D"]
            ]
        self.col_pins = [19, 13, 6, 5]
        self.row_pins = [21, 20, 16, 12]
        self.buzzer = 4
        GPIO.setup(buzzer, GPIO.OUT)
        GPIO.output(buzzer, GPIO.LOW)

    def get_key(self):
        for pin in self.col_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        for pin in self.row_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        row_val = -1
        for i in range(len(self.row_pins)):
            tmp_read = GPIO.input(self.row_pins[i])
            if tmp_read == 0:
                row_val = i

        if row_val < 0 or row_val > 3:
            self.exit()
            return

        for pin in self.col_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        GPIO.setup(self.row_pins[row_val], GPIO.OUT)
        GPIO.output(self.row_pins[row_val], GPIO.HIGH)

        col_val = -1
        for j in range(len(self.col_pins)):
            tmp_read = GPIO.input(self.col_pins[j])
            if tmp_read == 1:
                col_val = j

        if col_val < 0 or col_val > 3:
            self.exit()
            return

        self.exit()
        GPIO.output(self.buzzer, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(self.buzzer, GPIO.LOW)
        return self.keypad[row_val][col_val]

    def exit(self):
        for pin in self.row_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        for pin in self.col_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
