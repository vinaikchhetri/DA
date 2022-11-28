from threading import Thread
import socket
import struct
import pickle
import sys

from message import message

class Acceptor(Thread):
    
    def __init__(self, addr, id, config, role):
        Thread.__init__(self)
        self.addr = addr
        self.id = id
        self.config = config
        self.role = role
        self.sender = self.send_config()
        self.receiver = self.receive_config()
    
    def send_config(self):
        sock = socket.socket(socket.AF_INET,
                            socket.SOCK_DGRAM,
                            socket.IPPROTO_UDP)
        return sock

    def receive_config(self):
        recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recv_sock.bind(self.addr)
        mcast_group = struct.pack("4sl", socket.inet_aton(self.addr[0]), socket.INADDR_ANY)
        recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mcast_group)
        return recv_sock

    def run(self):
        print ('-> acceptor', self.id)
        while True:
            msg = self.receiver.recv(2**16)
            msg = pickle.loads(msg)
            if msg.phase == "Phase1A":
                # if msg.c_rnd > 
                newmsg = message()
                newmsg.phase = "Phase1B"
                newmsg.rnd = 1
                # print(newmsg.c_val)



        




    
