from threading import Thread
import socket
import struct
import pickle
import sys
import time


from message import message

class Acceptor():
    
    def __init__(self, addr, id, config):
       
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
            self.instances[msg.instance_index] = {"rnd":0, "v_val":None, "v_rnd": 0}

    def create_message(self, msg):
        newmsg = message()
        # newmsg.pid = msg.pid

        if msg.phase == "PHASE1A":
            newmsg.instance_index = msg.instance_index 
            newmsg.phase = "PHASE1B"
            newmsg.rnd = self.instances[msg.instance_index]["rnd"]
            newmsg.v_rnd = self.instances[msg.instance_index]["v_rnd"]
            newmsg.v_val = self.instances[msg.instance_index]["v_val"]
            newmsg.c_rnd = msg.c_rnd #delete
            newmsg.c_val = msg.client_val #delete
            newmsg.client_val = msg.client_val #delete

        # elif msg.phase == "PHASE1A-REJECTED":
        #     newmsg.instance_index = msg.instance_index 
        #     newmsg.phase = "PHASE1A-REDO"
        #     newmsg.c_rnd = msg.c_rnd
        #     newmsg.client_val = msg.client_val            

        elif msg.phase == "PHASE2A":
            newmsg.instance_index = msg.instance_index 
            newmsg.phase = "PHASE2B"
            newmsg.v_rnd = self.instances[msg.instance_index]["v_rnd"]
            newmsg.v_val = self.instances[msg.instance_index]["v_val"]
            newmsg.c_val = msg.client_val #delete
            newmsg.c_rnd = msg.c_rnd #delete
        return newmsg

    def print_message(self, msg):
        print(msg)
        sys.stdout.flush()
    
    def print_instance(self, id):
        print(self.instances[id])
        sys.stdout.flush()

    def run(self):
        print ('-> acceptor', self.id)
        sys.stdout.flush()
        while True:
            msg = self.receiver.recv(2**16)
            msg = pickle.loads(msg)
            # print("receive-acceptor",msg)
            # sys.stdout.flush()
            self.create_instance(msg)

            if msg.phase == "PHASE1A":

                if msg.c_rnd > self.instances[msg.instance_index]["rnd"]:
                    # print("paased1-a",msg)
                    # sys.stdout.flush()
                    self.instances[msg.instance_index]["rnd"] = msg.c_rnd 
                    newmsg = self.create_message(msg)
                    # if newmsg.phase == "PHASE1B":
                    #     print("accep: ",newmsg)
                    #     sys.stdout.flush()
                    # print("send-acceptor",newmsg)
                    # sys.stdout.flush()
                    newmsg = pickle.dumps(newmsg)
                    self.sender.sendto(newmsg, self.config['proposers'])

                # else:
                #     print("@@@@@@@@@@@",msg)
                #     sys.stdout.flush()

                    # print("rejection1",msg.c_rnd)
                    # print("rejection2",self.instances[msg.instance_index]["rnd"])
                    # sys.stdout.flush()

                
            #     else:
            #         print(msg)
            #         sys.stdout.flush()
            #         msg.phase = "PHASE1A-REJECTED"
            #         newmsg = self.create_message(msg)
            #         newmsg = pickle.dumps(newmsg)
            #         self.sender.sendto(newmsg, self.config['proposers'])

            if msg.phase == "PHASE2A":
                if msg.c_rnd >= self.instances[msg.instance_index]["rnd"]:
                    # print("passes2-a",msg)
                    # sys.stdout.flush()
                    self.instances[msg.instance_index]["v_rnd"] = msg.c_rnd 
                    self.instances[msg.instance_index]["v_val"] = msg.c_val 
                    newmsg = self.create_message(msg)
                    # print("send-acceptor",newmsg)
                    # sys.stdout.flush()
                    newmsg = pickle.dumps(newmsg)
                    self.sender.sendto(newmsg, self.config['proposers'])
                # else:
                #     print("#########",msg)
                #     sys.stdout.flush()

                



        




    
