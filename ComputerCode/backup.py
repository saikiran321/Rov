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

class CurrentState(dict):
     def __missing__(self, key):
        return 0
# initializing current state
current_state=CurrentState()


class LocalValues():
    def __init__(self):
        self.presentAngle=0
        self.currentReading=''
current_angle=LocalValues()
current_reading=LocalValues()


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
        msg=""
        line = subprocess.readline()  #reads output of xboxdrv
        if 'Error' in line:     #if there is an error in the lines
            raise ValueError(line+"sai") # raise an error
        data = filter(bool,s.split(line[:-1]))
        if len(data)==42:
            # Break input string into a data dict
            data = { data[x]:int(data[x+1]) for x in range(0,len(data),2) }  #Creates a dictionary with values assigned to each button
            # print data
            if not _data:
                _data = data
                continue
            # yield data
            # print data
            for key in data:
                if key=='X1' or key=='X2' or key=='Y1' or key=='Y2':
                    data[key] = apply_deadzone(data[key],deadzone,scale) #applies deadzones as X1, X2s have a big deadzone
                if data[key]==_data[key]: continue
                # event = Event(key,data[key],_data[key])  #outputs in the format Event(key, value, old value)
                btn=''
                event={}
                if key=='X1' or key=='X2' or key=='Y1' or key=='Y2':
                    btn=btn+key+'=>'+str(data[key])+";"
                    event[key]=data[key]
                for new_key in data:
                    
                    if data[new_key]==1:
                        btn=btn+new_key+'=>'+str(data[new_key])+";"
                        event[new_key]=data[new_key]
                    if (((new_key=='RT') or (new_key=='LT')) and data[new_key]>0):
                        btn=btn+new_key+'=>'+str(data[new_key])+";"
                        event[new_key]=data[new_key]
                # print btn       # btn not literlal btn but gives event press msg
                # print event
                yield event



            _data = data

def fourDigit(val):
    if val<10:
        new_val='000'+str(val)
    elif val<100:
        new_val='00'+str(val)
    elif val<1000:
        new_val='0'+str(val)
    else:
        new_val=str(val)
    return new_val

def encmap(val):
    val=val+32768
    val=val*90/32768
    val=int(5 * round(val/5.0))
    new_val=''
    if val<10:
        new_val='00'+str(val)
    elif val<100:
        new_val='0'+str(val)
    else:
        new_val=str(val)
    return new_val

def getRTvalue(event):
    if 'LB' in event and event['LB']==1:
            if event['RT']<50:
                b=5
            elif event['RT']<100:
                b=4
            elif event['RT']<150:
                b=3
            elif event['RT']<200:
                b=2
            else:
                b=1
    else:
        if event['RT']<50:
            b=5
        elif event['RT']<100:
            b=6
        elif event['RT']<150:
            b=7
        elif event['RT']<200:
            b=8
        else:
            b=9
    return b

def getLTvalue(event):
    if 'LB' in event and event['LB']==1:

        if event['LT']<50:
            a=5
        elif event['LT']<100:
                a=4
        elif event['LT']<150:
                a=3
        elif event['LT']<200:
                a=2
        else:
                a=1
    else:   
        if event['LT']<50:
            a=5
        elif event['LT']<100:
            a=6
        elif event['LT']<150:
            a=7
        elif event['LT']<200:
            a=8
        else:
            a=9
    return a

def get_data_y2(val):
    return val*85
def maneuver(event):
    a=5
    b=5
    flapres='0'
    
    if 'LT' in event:
        a=getLTvalue(event)

    if 'RT' in event:
        b=getRTvalue(event)
        if 'A' in event:
            a=b


    if 'B' in event:
        if 'RT' in event:
            b=5
            flapres=int(int(event['RT'])/28)
    
    res=str(a)+str(b)
    
    encres=fourDigit(current_angle.presentAngle)
    # if 'Y2' in event:
    #     encres=encmap(event['Y2'])
    # else:
    #     encres='000'
    if 'Y' in event:
        if event['Y']==1:
            current_angle.presentAngle=current_angle.presentAngle+85
        if current_angle.presentAngle>1530:
            current_angle.presentAngle=1530
        encres=fourDigit(current_angle.presentAngle)

    if 'X' in event:
        if event['X']==1:
            if current_angle.presentAngle>0:
                current_angle.presentAngle=current_angle.presentAngle-85
        encres=fourDigit(current_angle.presentAngle)


    if 'RB' in event:
        if event['RB']==1:
            current_angle.presentAngle=0
            encres="0000"

    if 'A' in event:
        if 'RT' in event:
            # a=b
            flapres=int(int(event['RT'])/28)
    if 'Y2' in event:
         
        xx=abs(int(event['Y2']/1800))
        encres=fourDigit(get_data_y2(xx))
        if int(encres)>1530:
            encres=1530
    if 'Y1' in event or 'X1' in event:

        if 'Y1' in event:
            print event['Y1']/3500
        if 'X1' in event:
            print event['X1']/3500
        

    res=res+str(flapres)+encres
    
      
    
    if current_reading.currentReading!=res:
        print res
        msg=xbox()
        msg.message=str(res)    
        #print str(a)
        lc.publish("Xbox", msg.encode())
        current_reading.currentReading=res

    




lc = lcm.LCM("udpm://224.0.0.251:7667?ttl=1")
for event in event_stream(deadzone=12000):
    if 'start' in event:
        if current_state['start']==1:
            current_state['start']=0
        else:
            current_state['start']=1
            print "started"

    if current_state['start']<=1:
        if event:               # only allows if event has any value
            maneuver(event)
        # print event
        # msg=xbox()
        # msg.message=str(new_event)
        # lc.publish("Xbox", msg.encode())   
        
