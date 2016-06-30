import lcm
from exlcm import xbox
import ast
import serial

port='/dev/ttyUSB1'
s=serial.Serial(port,115200)
port2='/dev/ttyUSB2'
s2=serial.Serial(port2,)

def modify(i):
    if i<10:
        a='00'+str(i)
    elif i<100:
        a='0'+str(i)
    else:
        a=str(i)
    return a
def  iron_msg(channel,data):
    msg=xbox.decode(data)
    input_msg=ast.literal_eval(msg.message)
    content=""
    if 'RT' in input_msg:
        content+='R'+str(modify(input_msg['RT']))
    if 'LT' in input_msg:
        content+='L'+str(modify(input_msg['LT']))
    print content
    if len(content)>0:
        s.write(content)
lc = lcm.LCM("udpm://224.0.0.251:7667?ttl=1")
subscribe=lc.subscribe("Xbox",iron_msg)

try :
    while True:
        lc.handle()
except KeyboardInterrupt:
    pass
