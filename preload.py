#!/usr/bin/env python3
# By icarus747
# Created 10/26/2023

from machine import Pin


def getProgrammingStatus():
    # check GPIO 15 for setup mode
    # see setup mode for instructions
    progStatusPin = Pin(15, Pin.IN, pull=Pin.PULL_UP)
    progStatus = not progStatusPin.value()
    return (progStatus)