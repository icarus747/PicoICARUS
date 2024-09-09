#!/usr/bin/env python3
# By DangerZone
# Created 9/6/2024

import serial
from math import floor
import statistics

serialPort = serial.Serial(
    port="COM6", baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
)
serialString = ""  # Used to hold data coming over UART
factor_list = []
for x in range(20):
    # Read data out of the buffer until a carraige return / new line is found
    serialString = serialPort.readline()
    # Print the contents of the serial dat
    # serial_string=b"$PUAVALT,991.899109,29.694635,179.191528*41"
    try:
        # print(serialString)#.decode("Ascii"))
        data = serialString.decode("utf-8").split(',')
        if data[0] == "$PUAVALT":
            ALT_fine = (1 - (float(data[1]) / 1013.25) ** .190284) * 144594.94052583326


            factor = 1/(1 - (float(data[1]) / 1013.25) ** .190284) * 575
            ALT = 100 * floor(ALT_fine/100 + .5)
            factor_list.append(factor)
            print(ALT, factor)

    except:
        pass

alt_factor = statistics.median(factor_list)
print(alt_factor)