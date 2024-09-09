#!/usr/bin/env python3
# By icarus747
# Created 09/07/2024
# Version 2.0

from machine import UART, Pin  # Used for serial
from time import sleep  # Used for LED
import asyncio  # For listening for alt and repeating out other serial link
import ujson  # User input file for baudrate changes
from preload import *  # To put device in edit mode
import math  # For altitude rounding

#  LED
led = Pin("LED", Pin.OUT)

progStatus = False
progStatus = getProgrammingStatus()  # From preload
print("progStatus", progStatus)
if not progStatus:

    with open('baudrate.json') as br:
        settings = ujson.loads(br.read())
    # Configure the serial port
    # iLevil
    SERIAL_PORT1 = UART(0, baudrate=settings['baudrate0'])
    SERIAL_PORT1.init(invert=SERIAL_PORT1.INV_RX)
    # GTX327
    SERIAL_PORT2 = UART(1, baudrate=settings['baudrate1'], invert=1)

    press_alt = "ALT -2500\r"


    async def EchoALT_listener():
        print("running listener")

        global press_alt
        try:
            while True:
                # serial_string="$PUAVALT,991.899109,29.694635,179.191528*41"
                # Read a single byte from the serial port
                serial_string = SERIAL_PORT1.readline()

                data = serial_string.split(',')
                if data[0] == "$PUAVALT":
                    alt_fine = (1 - (float(data[1]) / 1013.25) ** .190284) * 144594.94052583326

                    # factor = 1 / (1 - (float(data[1]) / 1013.25) ** .190284) * 575
                    alt_rounded = 100 * math.floor(alt_fine / 100 + .5)
                    # factor_list.append(factor)
                    # print(press_alt)
                    press_alt = f"ALT {int(alt_rounded):05d}\r"

                await asyncio.sleep(0.2)  # Sleeps every .2 seconds (5Hz)

        except KeyboardInterrupt:
            # Close the serial port when exiting the program
            SERIAL_PORT1.close()
            SERIAL_PORT2.close()


    async def serial_output():
        global press_alt
        while True:
            SERIAL_PORT2.write(press_alt)  # Writes out pressure altitude from EchoALT
            # print(press_alt)
            await asyncio.sleep(1)
            led.off()
            await asyncio.sleep(1.5)  # Sleeps every 2.5 seconds.
            led.on()


    async def ICARUS():
        asyncio.create_task(EchoALT_listener())
        asyncio.create_task(serial_output())
        while True:
            await asyncio.sleep(10)  # Keeps the main coroutine alive


    asyncio.run(ICARUS())

else:
    print("GPIO15 grounded.  Modify your code.")
