from threading import Thread
import socket
import struct
import pickle
import sys

from message import message

class Learner(Thread):
    
    def __init__(self, addr, id, config):
        Thread.__init__(self)
        self.instances = {}
        self.addr = addr
        self.id = id
        self.config = config
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
        if not msg.instance_index in self.instances:
            self.instances[msg.instance_index] = {"v_val":None}

    def print_message(self, msg):
        print(msg)
        sys.stdout.flush()
    
    def print_instance(self, id):
        print(self.instances[id])

    def run(self):
        print ('-> learner', self.id)
        while True:
            msg = self.receiver.recv(2**16)
            msg = pickle.loads(msg)
            self.create_instance(msg)

            # if msg.phase == "DECISION" and self.instances[msg.instance_index]["v_val"]==None:
            if msg.phase == "DECISION":
                self.instances[msg.instance_index]["v_val"] = msg.v_val
                self.print_message(msg)

                



        




    
