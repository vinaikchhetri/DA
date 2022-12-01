from threading import Thread
import socket
import struct
import pickle
import sys

from message import message

NUM_ACCEPTORS = 3.0
class Proposer(Thread):
    
    def __init__(self, addr, id, config):
        Thread.__init__(self)
        self.instances = {}
        self.instance_index = -1
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
        self.instance_index += 1
        self.instances[self.instance_index] = {"c_rnd":0, "c_val":None, "votes1": 0, "votes2": 0, "client_val":msg.client_val, "k":0, "k_val":None, "rejections":0}

    def create_message(self, msg):
        newmsg = message()
        # newmsg.pid = self.id

        if msg.phase == "CLIENT-REQUEST":
            newmsg.instance_index = self.instance_index 
            newmsg.phase = "PHASE1A"
            newmsg.c_rnd = self.id
            newmsg.client_val = msg.client_val

        elif msg.phase == "PHASE1B":
            newmsg.instance_index = msg.instance_index 
            newmsg.phase = "PHASE2A"
            newmsg.c_rnd = self.instances[msg.instance_index]["c_rnd"]
            newmsg.c_val = self.instances[msg.instance_index]["c_val"]

        elif msg.phase == "PHASE2B":
            newmsg.instance_index = msg.instance_index 
            newmsg.phase = "DECISION"
            newmsg.v_val = msg.v_val
            newmsg.c_rnd = self.instances[msg.instance_index]["c_rnd"] #To delete. Just useful for printing.

        elif msg.phase == "PHASE1A-REDO":
            newmsg.instance_index = msg.instance_index 
            newmsg.phase = "PHASE1A"
            newmsg.c_rnd = msg.c_rnd + 100
            newmsg.client_val = msg.client_val
    
        return newmsg
    
    def print_message(self, msg):
        print(msg)
    
    def print_instance(self, id):
        print(self.instances[id])


    def run(self):
        global NUM_ACCEPTORS

        print ('-> proposer', self.id)
        while True:
            msg = self.receiver.recv(2**16)
            msg = pickle.loads(msg)


            if msg.phase == "CLIENT-REQUEST": 
                print(msg)
                self.create_instance(msg)            
                newmsg = self.create_message(msg)
                self.instances[self.instance_index]["c_rnd"] = self.id
                newmsg = pickle.dumps(newmsg)
                self.sender.sendto(newmsg, self.config['acceptors'])
            
            # if msg.pid == self.id: 
            if msg.phase == "PHASE1B":
                print(msg)
                if msg.instance_index in self.instances:
                    if msg.rnd == self.instances[msg.instance_index]["c_rnd"] and msg.v_rnd > self.instances[msg.instance_index]["k"]:
                        self.instances[msg.instance_index]["k"] = msg.v_rnd
                        self.instances[msg.instance_index]["k_val"] = msg.v_val

                    if msg.rnd == self.instances[msg.instance_index]["c_rnd"]:
                        self.instances[msg.instance_index]["votes1"]+=1

                    if self.instances[msg.instance_index]["votes1"] > int(NUM_ACCEPTORS/2):
                        self.instances[msg.instance_index]["votes1"] = int(int(NUM_ACCEPTORS/2) - NUM_ACCEPTORS + 1)
                        if self.instances[msg.instance_index]["k"]==0:
                            self.instances[msg.instance_index]["c_val"] = self.instances[msg.instance_index]["client_val"]
                        else:
                            self.instances[msg.instance_index]["c_val"] = self.instances[msg.instance_index]["k_val"]
                        newmsg = self.create_message(msg)
                        newmsg = pickle.dumps(newmsg)
                        self.sender.sendto(newmsg, self.config['acceptors'])

            if msg.phase == "PHASE2B":
                print(msg)
                if msg.instance_index in self.instances:
                    if msg.v_rnd == self.instances[msg.instance_index]["c_rnd"]:
                        self.instances[msg.instance_index]["votes2"]+=1

                    if self.instances[msg.instance_index]["votes2"] > int(NUM_ACCEPTORS/2):
                        self.instances[msg.instance_index]["votes2"] = int(int(NUM_ACCEPTORS/2) - NUM_ACCEPTORS + 1)
                        newmsg = self.create_message(msg)
                        newmsg = pickle.dumps(newmsg)
                        self.sender.sendto(newmsg, self.config['learners'])
            
            if msg.phase == "PHASE1A-REDO":
                print(msg)
                if msg.instance_index in self.instances:
                    if msg.c_rnd == self.instances[msg.instance_index]["c_rnd"]: 
                        self.instances[msg.instance_index]["rejections"]+=1

                    if self.instances[msg.instance_index]["rejections"] == NUM_ACCEPTORS:
                        self.instances[msg.instance_index]["rejections"] = 0
                        self.instances[msg.instance_index]["c_rnd"] += 100
                        newmsg = self.create_message(msg)
                        newmsg = pickle.dumps(newmsg)
                        self.sender.sendto(newmsg, self.config['acceptors'])

                        self.create_instance(msg)
                        # print(msg.pid)
                        msg.phase = "CLIENT-REQUEST"            
                        newmsg = self.create_message(msg)
                        self.instances[self.instance_index]["c_rnd"] = self.id
                        newmsg = pickle.dumps(newmsg)
                        self.sender.sendto(newmsg, self.config['acceptors'])


                    

                

                



        




    
