from threading import Thread
import socket
import struct
import pickle
import sys
import time

from message import message

class Client(Thread):
    
    def __init__(self, addr, id, config):
        Thread.__init__(self)
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
            for value in sys.stdin:
                value = value.strip()
                msg = message()
                msg.phase = "CLIENT-REQUEST"
                msg.client_val = value
                msg = pickle.dumps(msg)
                print ("client: sending %s to proposers" % (value))
                self.sender.sendto(msg, self.config['proposers'])
                #time.sleep(0.001)

        
        




    
