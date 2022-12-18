from threading import Thread
import socket
import struct
import pickle
import sys
import time

from message import message

class Client():
    
    def __init__(self, addr, id, config):
        
        self.addr = addr
        self.id = id
        self.config = config
        self.sender = self.send_config()
    
    def send_config(self):
        sock = socket.socket(socket.AF_INET,
                            socket.SOCK_DGRAM,
                            socket.IPPROTO_UDP)
        return sock

    def run(self):
        print ('-> client ', self.id)
        while True:       
            count = 0
            for value in sys.stdin:
                count+=1

                value = value.strip()
                msg = message()
                msg.phase = "CLIENT-REQUEST"
                msg.client_val = value
                msg.msg_id = count

                msg = pickle.dumps(msg)
                print ("client: sending %s to proposers" % (value))
                sys.stdout.flush()
                self.sender.sendto(msg, self.config['proposers'])
                
                #time.sleep(0.001)

        
        




    
