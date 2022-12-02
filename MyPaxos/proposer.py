from threading import Thread
import socket
import struct
import pickle
import sys
import time

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
        self.instances[self.instance_index] = {"c_rnd":0, "c_val":None, 
        "votes1":{}, "votes2":{},
        "client_val":msg.client_val, "k":0, "k_val":None, 
        "timer_stop":False}

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
        sys.stdout.flush()
    
    def print_instance(self, id):
        print(self.instances[id])
        sys.stdout.flush()
    
    def timer(self, msg):
        begin = time.time()
        while(self.instances[msg.instance_index]["timer_stop"]==False):
            if time.time()-begin>1:
                print("broken")
                sys.stdout.flush()
                if msg.phase == "PHASE1A":
                    self.instances[msg.instance_index]["c_rnd"] += 100
                    msg.phase = "PHASE1A-REDO"
                    newmsg = self.create_message(msg)
                    t = Thread(target=self.timer, args = (newmsg,))
                    newmsg = pickle.dumps(newmsg)
                    t.start()
                    self.sender.sendto(newmsg, self.config['acceptors'])
                    break


    
    def run(self):
        global NUM_ACCEPTORS

        print ('-> proposer', self.id)
        while True:
            msg = self.receiver.recv(2**16)
            msg = pickle.loads(msg)


            if msg.phase == "CLIENT-REQUEST": 
                print(msg)
                sys.stdout.flush()
                self.create_instance(msg)            
                newmsg = self.create_message(msg)
                self.instances[self.instance_index]["c_rnd"] = self.id
                self.instances[self.instance_index]["votes1"][self.id] = 0
                self.instances[self.instance_index]["votes2"][self.id] = 0
                t = Thread(target=self.timer, args = (newmsg,))
                t.start()
                newmsg = pickle.dumps(newmsg)
                self.sender.sendto(newmsg, self.config['acceptors'])

            
            if msg.phase == "PHASE1B":
                if msg.instance_index in self.instances:
                    crnd = self.instances[msg.instance_index]["c_rnd"]
                    if msg.rnd == crnd:
                        self.instances[msg.instance_index]["timer_stop"]=True
                        print("done")
                        print(msg)
                    

            
            # # if msg.pid == self.id: 
            # if msg.phase == "PHASE1B":
            #     if msg.instance_index in self.instances:
            #         crnd = self.instances[msg.instance_index]["c_rnd"]
            #         if msg.rnd == crnd and msg.v_rnd > self.instances[msg.instance_index]["k"]:
            #             self.instances[msg.instance_index]["k"] = msg.v_rnd
            #             self.instances[msg.instance_index]["k_val"] = msg.v_val
                        
                    
            #         if msg.rnd == crnd:
            #             self.instances[msg.instance_index]["votes1"][crnd] += 1
            #             print(msg)
            #             sys.stdout.flush()

            #         if self.instances[msg.instance_index]["votes1"][crnd] > int(NUM_ACCEPTORS/2):
            #             self.instances[msg.instance_index]["votes1"][crnd] = 0
            #             if self.instances[msg.instance_index]["k"]==0:
            #                 self.instances[msg.instance_index]["c_val"] = self.instances[msg.instance_index]["client_val"]
            #             else:
            #                 self.instances[msg.instance_index]["c_val"] = self.instances[msg.instance_index]["k_val"]
            #             newmsg = self.create_message(msg)
            #             newmsg = pickle.dumps(newmsg)
            #             self.sender.sendto(newmsg, self.config['acceptors'])

            # if msg.phase == "PHASE2B":
            #     if msg.instance_index in self.instances:
            #         crnd = self.instances[msg.instance_index]["c_rnd"]

            #         if msg.v_rnd == crnd:
            #             self.instances[msg.instance_index]["votes2"][crnd]+=1
            #             print(msg)
            #             sys.stdout.flush()

            #         if self.instances[msg.instance_index]["votes2"][crnd] > int(NUM_ACCEPTORS/2):
            #             self.instances[msg.instance_index]["votes2"][crnd] = 0
            #             newmsg = self.create_message(msg)
            #             newmsg = pickle.dumps(newmsg)
            #             self.sender.sendto(newmsg, self.config['learners'])
            
            # if msg.phase == "PHASE1A-REDO":
            #     if msg.instance_index in self.instances:
            #         crnd = self.instances[msg.instance_index]["c_rnd"]

            #         if msg.c_rnd == crnd: 
            #             self.instances[msg.instance_index]["nack1"][crnd]+=1
            #             print(msg)
            #             sys.stdout.flush()

            #         if self.instances[msg.instance_index]["nack1"][crnd] > int(NUM_ACCEPTORS/2):
            #             self.instances[msg.instance_index]["nack1"][crnd] = 0
            #             self.instances[msg.instance_index]["c_rnd"] += 100
            #             icrnd = self.instances[msg.instance_index]["c_rnd"]
            #             self.instances[msg.instance_index]["votes1"][icrnd] = 0
            #             self.instances[msg.instance_index]["votes2"][icrnd] = 0
            #             self.instances[msg.instance_index]["nack1"][icrnd] = 0
            #             newmsg = self.create_message(msg)
            #             newmsg = pickle.dumps(newmsg)
            #             self.sender.sendto(newmsg, self.config['acceptors'])

            #             # self.create_instance(msg)
            #             # # print(msg.pid)
            #             # msg.phase = "CLIENT-REQUEST"            
            #             # newmsg = self.create_message(msg)
            #             # self.instances[self.instance_index]["c_rnd"] = self.id
            #             # newmsg = pickle.dumps(newmsg)
            #             # self.sender.sendto(newmsg, self.config['acceptors'])


                    

                

                



        




    
