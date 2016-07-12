import lcm
from exlcm import xbox

def  s1_msg(channel,data):
    msg=xbox.decode(data)
    print msg.message
def  s2_msg(channel,data):
    msg=xbox.decode(data)
    print msg.message

lc1 = lcm.LCM("udpm://224.0.0.250:7666?ttl=1")
subscribe1=lc1.subscribe("s1data",s1_msg)
#lc2 = lcm.LCM("udpm://224.0.0.251:7665?ttl=1")
#subscribe2=lc2.subscribe("s2data",s2_msg)
try :
    while True:
        lc1.handle()
        #lc2.handle() 
except KeyboardInterrupt:
    pass

