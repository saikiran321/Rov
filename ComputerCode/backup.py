import lcm
from exlcm import xbox
from os import popen
from sys import stdin
import re  # Regular expressions to search for patterns in a list

s = re.compile('[ :]') #s stores the pattern [ :] which can be used for searching later


class CurrentState(dict):
     def __missing__(self, key):
        return 0
# initializing current state
current_state=CurrentState()



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
            if not _data:
                _data = data
                continue
            # yield data
            #print data
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
                
                yield event



            _data = data

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
def maneuver(event):
    a=0
    b=0
    if 'LT' in event:
        if event['LT']<50:
            a=0
        elif event['LT']<100:
            a=1
        elif event['LT']<150:
            a=2
        elif event['LT']<200:
            a=3
        else:
            a=4
    if 'RT' in event:
        if event['RT']<50:
            b=0
        elif event['RT']<100:
            b=1
        elif event['RT']<150:
            b=2
        elif event['RT']<200:
            b=3
        else:
            b=4
        if 'A' in event:
            a=b
    res=str(a)+str(b)

    if 'Y2' in event:
        encres=encmap(event['Y2'])
    else:
        encres='090'
    if 'Y' in event:
        if event['Y']==1:
            encres="095"
    if 'B' in event:
        if event['B']==1:
            encres="085"
    res=res+encres
    print res
      
    # if 'Y2' in event:
    #     Y2_val=event['Y2']*90/32768
    #     # Y2_val=int(Y2_val)
    #     print Y2_val
    # print event
    # msg=xbox()
    # msg.message=str(a)    
    # print str(a)
    
    # lc.publish("Xbox", msg.encode())



    #     print event['RT']
    # if 'Y2' in event:
    #     Y2_val=event['Y2']*90/32768
    #     Y2_val=int(Y2_val)
    #     print Y2_val  




lc = lcm.LCM("udpm://224.0.0.251:7667?ttl=1")
for event in event_stream(deadzone=12000):
    if 'start' in event:
        if current_state['start']==1:
            current_state['start']=0
        else:
            current_state['start']=1
            print "started"

    if current_state['start']==1:
        if event:               # only allows if event has any value
            maneuver(event)
        # print event
        # msg=xbox()
        # msg.message=str(new_event)
        # lc.publish("Xbox", msg.encode())   
        
