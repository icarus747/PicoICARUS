#!/usr/bin/env python3
# By icarus747
# Created 10/21/2023
# Version 1.0


import machine
import usocket as socket
import network
import ure
import asyncio
from preload import *
import ujson


progStatus = False
progStatus = getProgrammingStatus()
print("progStatus", progStatus)
if (progStatus == False):

    # Configure your Wi-Fi credentials
    with open('secrets.json') as fp:
        secrets = ujson.loads(fp.read())
    SSID = secrets['SSID']
    PASSWORD = secrets['PASSWORD']

    # Set up the UART for serial communication
    SERIAL_PORT1 = machine.UART(0, baudrate=secrets['baudrate0'], invert=1)
    SERIAL_PORT2 = machine.UART(1, baudrate=secrets['baudrate1'], invert=0)

    # Connect to Wi-Fi
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(SSID, PASSWORD)

    # Wait for the connection to be established
    while not wifi.isconnected():
        pass

    print(f"Connected to Wi-Fi. IP: {wifi.ifconfig()[0]}")

    # Set up a UDP server
    UDP_IP = "0.0.0.0"  # Listen on all available network interfaces
    UDP_PORT = secrets['UDP_PORT']

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((UDP_IP, UDP_PORT))

    print(f"UDP Server listening on {UDP_IP}:{UDP_PORT}\n{SERIAL_PORT1}\n{SERIAL_PORT2}")

    # Setup regex search string
    search_string = ure.compile('^\$PGRMZ,(\d+),')
    # Default "test" altitude
    global_altitude = "ALT 02121\r"
    # Led handling
    led = machine.Pin("LED", machine.Pin.OUT)


    async def udp_listener():
        global led
        global global_altitude
        while True:
            data, addr = udp_socket.recvfrom(1024)
            data = data.decode('utf-8')
            alt_group = search_string.match(data)
            if alt_group:
                alt = f'ALT {int(alt_group.group(1)):05d}\r'
                if alt:
                    print(f"Received data: {data}\rAnd ICARUS: {alt}")
                    global_altitude = alt
                    led.toggle()
            await asyncio.sleep(0.001)  # Sleeps every 100ms


    async def serial_output():
        global global_altitude
        while True:
            SERIAL_PORT1.write(global_altitude)
            SERIAL_PORT2.write(global_altitude)
            await asyncio.sleep(1)  # Sleeps every second.


    async def ICARUS():
        asyncio.create_task(udp_listener())
        asyncio.create_task(serial_output())
        while True:
            await asyncio.sleep(10)  # Keeps the main coroutine alive


    asyncio.run(ICARUS())

else:
    print("GPIO15 grounded.  Modify your code.")
