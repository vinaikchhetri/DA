from threading import Thread
import socket
import struct
import pickle
import sys
import math

from message import message

NUM_ACCEPTORS = 3.0
class Proposer(Thread):
    
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
        self.instance_index += 1
        self.instances[self.instance_index] = {"c_rnd":0, "c_val":None, "votes1": 0, "votes2": 0, "client_val":msg.client_val, "k":0, "k_val":None}

    def create_message(self, msg):
        newmsg = message()
        if msg.phase == "CLIENT":
            newmsg.instance_index = self.instance_index 
            newmsg.phase = "PHASE1A"
            newmsg.c_rnd = 1
            newmsg.client_val = msg.client_val
        return newmsg


    def run(self):
        #global NUM_ACCEPTORS

        print ('-> proposer', self.id)
        while True:
            msg = self.receiver.recv(2**16)
            msg = pickle.loads(msg)


            if msg.phase == "CLIENT": 
                self.create_instance(msg)            
                newmsg = self.create_message(msg)
                newmsg = pickle.dumps(newmsg)
                self.sender.sendto(newmsg, self.config['acceptors'])
            
            if msg.phase == "PHASE1B":

                if msg.v_rnd > self.instances[msg.instance_index]["k"]:
                    self.instances[msg.instance_index]["k"] = msg.v_rnd
                    self.instances[msg.instance_index]["k_val"] = msg.v_val

                if msg.rnd == self.instances[msg.instance_index]["c_rnd"]:
                    self.instances[msg.instance_index]["votes1"]+=1

                if self.instances[msg.instance_index]["votes1"] > math.ceil(NUM_ACCEPTORS/2):
                    if self.instances[msg.instance_index]["k"]==0:
                        self.instances[msg.instance_index]["c_val"] = self.instances[msg.instance_index]["client_val"]
                    else:
                        self.instances[msg.instance_index]["c_val"] = self.instances[msg.instance_index]["k_val"]

                print(self.instances[msg.instance_index]["votes1"])
                print(self.instances[msg.instance_index]["c_val"])

                

                



        




    
