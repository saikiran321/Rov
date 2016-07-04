import lcm
from exlcm import xbox
import ast
import serial

port='/dev/ttyUSB1'
s=serial.Serial(port,38400)
port2='/dev/ttyUSB2'
s2=serial.Serial(port2,38400)

def  iron_msg(channel,data):
    msg=xbox.decode(data)
    input_msg=msg.message
    first_arduino_msg=input_msg[2:]
    second_arduino_msg=input_msg[:2]
    s1.write(first_arduino_msg)
    s2.write(second_arduino_msg)
    print input_msg
    if s1.readline():
        print s1.readline()
    if s2.readline():
        print s2.readline()


lc = lcm.LCM("udpm://224.0.0.251:7667?ttl=1")
subscribe=lc.subscribe("Xbox",iron_msg)

try :
    while True:
        lc.handle()
except KeyboardInterrupt:
    pass
