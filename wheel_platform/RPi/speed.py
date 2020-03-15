#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(2)
print(ser.readline())
print("Ready!")

#while 1:
#    print(ser.readline())
while True:
    a = int(input())
    if a == 1:
        ser.write(bytes("0", encoding = 'UTF-8'))
        ser.write(bytes("1", encoding = 'UTF-8'))
        ser.write(bytes("0", encoding = 'UTF-8'))
        ser.write(bytes("0", encoding = 'UTF-8'))
        ser.write(bytes("0", encoding = 'UTF-8'))
    elif a == 2:
        ser.write(bytes("0", encoding = 'UTF-8'))
        ser.write(bytes("2", encoding = 'UTF-8'))
        ser.write(bytes("0", encoding = 'UTF-8'))
        ser.write(bytes("0", encoding = 'UTF-8'))
        ser.write(bytes("0", encoding = 'UTF-8'))
    elif a == 3:
        ser.write(bytes("0", encoding = 'UTF-8'))
        ser.write(bytes("0", encoding = 'UTF-8'))
        ser.write(bytes("0", encoding = 'UTF-8'))
        ser.write(bytes("0", encoding = 'UTF-8'))
        ser.write(bytes("1", encoding = 'UTF-8'))
    elif a == 4:
        ser.write(bytes("0", encoding = 'UTF-8'))
        ser.write(bytes("0", encoding = 'UTF-8'))
        ser.write(bytes("0", encoding = 'UTF-8'))
        ser.write(bytes("0", encoding = 'UTF-8'))
        ser.write(bytes("2", encoding = 'UTF-8'))
    elif a == 5:
        ser.write(bytes("1", encoding = 'UTF-8'))
        ser.write(bytes("3", encoding = 'UTF-8'))
        ser.write(bytes("1", encoding = 'UTF-8'))
        ser.write(bytes("0", encoding = 'UTF-8'))
        ser.write(bytes("0", encoding = 'UTF-8'))
        print("existing step 5")
    elif a == 6:
        ser.write(bytes("1", encoding = 'UTF-8'))
        ser.write(bytes("1", encoding = 'UTF-8'))
        ser.write(bytes("0", encoding = 'UTF-8'))
        ser.write(bytes("0", encoding = 'UTF-8'))
        ser.write(bytes("0", encoding = 'UTF-8'))
        print("existing step 6")
