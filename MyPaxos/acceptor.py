from threading import Thread
import socket
import struct
import pickle
import sys

from message import message

class Acceptor(Thread):
    
    def __init__(self, addr, id, config, role):
        Thread.__init__(self)
        self.instances = {}
        self.instance_index = -1
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

    def create_instance(self, msg):
        self.instance_index = msg.instance_index
        if not self.instance_index in self.instances:
            self.instances[self.instance_index] = {"rnd":0, "v_val":None, "v_rnd": 0}

    def create_message(self, msg):
        newmsg = message()
        if msg.phase == "PHASE1A":
            newmsg.instance_index = msg.instance_index 
            newmsg.phase = "PHASE1B"
            newmsg.rnd = self.instances[msg.instance_index]["rnd"]
            newmsg.v_rnd = self.instances[msg.instance_index]["v_rnd"]
            newmsg.v_val = self.instances[msg.instance_index]["v_val"]
        return newmsg

    def print_message(self, msg):
        print(msg)

    def run(self):
        print ('-> acceptor', self.id)
        while True:
            msg = self.receiver.recv(2**16)
            msg = pickle.loads(msg)
            self.create_instance(msg)

            if msg.phase == "PHASE1A":

                if msg.c_rnd > self.instances[msg.instance_index]["rnd"]:
                    self.instances[msg.instance_index]["rnd"] = msg.c_rnd 
                    newmsg = self.create_message(msg)
                    newmsg = pickle.dumps(newmsg)
                    self.sender.sendto(newmsg, self.config['proposers'])

                



        




    
