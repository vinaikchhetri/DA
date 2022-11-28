from threading import Thread
import socket
import struct
import pickle
import sys

from message import message

class Client(Thread):
    
    def __init__(self, addr, id, config, role):
        Thread.__init__(self)
        self.addr = addr
        self.id = id
        self.config = config
        self.role = role
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
                msg.phase = "Client propose"
                msg.client_val = value
                msg = pickle.dumps(msg)
                print ("client: sending %s to proposers" % (value))
                self.sender.sendto(msg, self.config['proposers'])

        
        




    
