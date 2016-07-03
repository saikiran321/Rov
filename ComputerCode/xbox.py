import lcm
from exlcm import xbox
from os import popen
from sys import stdin
import re  # Regular expressions to search for patterns in a list

s = re.compile('[ :]') #s stores the pattern [ :] which can be used for searching later

class Event:
    def __init__(self,key,value,old_value):
        self.key = key
        self.value = value
        self.old_value = old_value
    def is_press(self):
        return self.value==1 and self.old_value==0
    def __str__(self):
        return 'Event(%s,%d,%d)' % (self.key,self.value,self.old_value)

def apply_deadzone(x, deadzone, scale):
    if x < 0:
        return (scale * min(0,x+deadzone)) / (32768-deadzone)
    return (scale * max(0,x-deadzone)) / (32768-deadzone)

def event_stream(deadzone=0,scale=32768):      #is generally called from our program
    _data = None    #old values of keys
    
    subprocess = popen('nohup sudo rmmod xpad','w',65536)
    subprocess = popen('sudo xboxdrv','r',65536) #runs xboxdrv in nohup mode which makes it run even after exiting a SSH session
    #subprocess = popen('1234','w',65536) #runs xboxdrv in nohup mode which makes it run even after exiting a SSH session
    
    while (True):
        line = subprocess.readline()  #reads output of xboxdrv
        if 'Error' in line:     #if there is an error in the lines
            raise ValueError(line) # raise an error
        data = filter(bool,s.split(line[:-1]))
        if len(data)==42:
            # Break input string into a data dict
            data = { data[x]:int(data[x+1]) for x in range(0,len(data),2) }  #Creates a dictionary with values assigned to each button
            if not _data:
                _data = data
                continue
            for key in data:
                if key=='X1' or key=='X2' or key=='Y1' or key=='Y2':
                    data[key] = apply_deadzone(data[key],deadzone,scale) #applies deadzones as X1, X2s have a big deadzone
                if data[key]==_data[key]: continue
                event = Event(key,data[key],_data[key])  #outputs in the format Event(key, value, old value)
                yield event
            _data = data
            

lc = lcm.LCM("udpm://224.0.0.251:7667?ttl=1")
for event in event_stream(deadzone=12000):
    print event
    if event:
        msg=xbox()
        msg.message=str(event)
        lc.publish("Xbox", msg.encode())