from threading import Thread
from threading import Timer
import threading
import socket
import struct
import pickle
import sys
import time

from message import message


NUM_ACCEPTORS = 3.0
class Proposer():
    
    def __init__(self, addr, id, config):
        
        self.instances = {}
        self.pending = []
        self.pending2 = []
        self.paxos=False
        

        self.instance_index = -1
        self.addr = addr
        self.id = id
        self.config = config
        self.sender = self.send_config()
        self.receiver = self.receive_config()
        self.decision = {}
        self.new_instance_blocker = []
        
        
    
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
        "timert":None}

    def create_message(self, msg):
        newmsg = message()

        if msg.phase == "CLIENT-REQUEST":
            newmsg.instance_index = self.instance_index 
            newmsg.phase = "PHASE1A"
            newmsg.c_rnd = self.id
            # newmsg.client_val = msg.client_val
            newmsg.client_val = self.instances[self.instance_index]["client_val"]

        elif msg.phase == "PHASE1B":
            newmsg.instance_index = msg.instance_index 
            # self.instances[msg.instance_index]["timer_stop"]=False
            newmsg.phase = "PHASE2A"
            newmsg.c_rnd = self.instances[msg.instance_index]["c_rnd"]
            newmsg.c_val = self.instances[msg.instance_index]["c_val"]
            newmsg.client_val = msg.client_val #delete

        elif msg.phase == "PHASE2B":
            newmsg.instance_index = msg.instance_index 
            # self.instances[msg.instance_index]["timer_stop2"]=False
            newmsg.phase = "DECISION"
            newmsg.v_val = msg.v_val
            newmsg.c_rnd = msg.c_rnd #delete

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


   

    def run(self):
        global NUM_ACCEPTORS

        print ('-> proposer', self.id)

        self.receiver.settimeout(0.0001)
        
        while True:

        
            try:
                msg = self.receiver.recv(2**16)
                #time.sleep(0.001)
                ## store message
                 
                self.pending.append(msg)


            except:
                # process message
                self.pending2 = self.pending[0:501]
                self.pending = self.pending[501:]
                # self.pending2 = self.pending[0:len(self.pending2)//2]
                # self.pending = self.pending[len(self.pending2)//2:]
                # self.pending2 = self.pending
                # self.pending = []
                # print("sending 1a",len(self.pending2 ))
                # sys.stdout.flush()
                for msg in self.pending2:
                    # self.pending.remove(msg)


                    #msg = self.receiver.recv(2**16)
                    msg = pickle.loads(msg)
                    if msg.phase == "CLIENT-REQUEST": 
                        # print("sending 1a",msg)
                        # sys.stdout.flush()
                
                                    
                        self.create_instance(msg)            
                        newmsg = self.create_message(msg)
                        self.new_instance_blocker.append(newmsg.client_val)
                        self.instances[self.instance_index]["c_rnd"] = self.id
                        self.instances[self.instance_index]["votes1"][self.id] = 0
                        self.instances[self.instance_index]["votes2"][self.id] = 0               
                        # t = Timer(1, self.timer, args=(newmsg,))
                        # t.start()
                        self.instances[self.instance_index]["timert"] = time.time()
                        newmsg = pickle.dumps(newmsg)
                        self.sender.sendto(newmsg, self.config['acceptors'])
                            


                    if msg.phase == "PHASE1B":
                        # print("Do I receive the message ",msg," prop-id ", self.id)
                        #sys.stdout.flush()
                        if msg.instance_index in self.instances:
                            crnd = self.instances[msg.instance_index]["c_rnd"]
                            if self.instances[msg.instance_index]["votes1"][crnd]<2: 
                                if msg.rnd == crnd and msg.v_rnd > self.instances[msg.instance_index]["k"]:
                                    self.instances[msg.instance_index]["k"] = msg.v_rnd
                                    self.instances[msg.instance_index]["k_val"] = msg.v_val
                                    
                                if msg.rnd == crnd:
                                    self.instances[msg.instance_index]["votes1"][crnd] += 1

                                    if self.instances[msg.instance_index]["votes1"][crnd] > int(NUM_ACCEPTORS/2):
                                        # print("recieve  1b quo",msg)
                                        # sys.stdout.flush()


                                        if self.instances[msg.instance_index]["k"]==0:
                                            self.instances[msg.instance_index]["c_val"] = self.instances[msg.instance_index]["client_val"]
                                            newmsg = self.create_message(msg)

                                            newmsg = pickle.dumps(newmsg)
                                            self.sender.sendto(newmsg, self.config['acceptors'])

                                        else:
                                            self.instances[msg.instance_index]["c_val"] = self.instances[msg.instance_index]["k_val"]
                                            
                                            

                                            newmsg = self.create_message(msg)
                                    
                                            newmsg = pickle.dumps(newmsg)
                                            self.sender.sendto(newmsg, self.config['acceptors'])
                                            

                                            if self.instances[msg.instance_index]["client_val"] in self.new_instance_blocker:
                                                msg.client_val = self.instances[msg.instance_index]["client_val"]
                                                self.create_instance(msg)
                                                msg.phase = "CLIENT-REQUEST"            
                                                newmsg = self.create_message(msg)
                                                self.instances[self.instance_index]["c_rnd"] = self.id
                                                self.instances[self.instance_index]["votes1"][self.id] = 0
                                                self.instances[self.instance_index]["votes2"][self.id] = 0
                
                                                self.instances[self.instance_index]["timert"] = time.time()
                                                self.new_instance_blocker.remove(newmsg.client_val)
                                                # print("sending 2a broken",newmsg)
                                                # sys.stdout.flush()
                                                newmsg = pickle.dumps(newmsg)
                                                self.sender.sendto(newmsg, self.config['acceptors'])



                    if msg.phase == "PHASE2B":
                        

                        if msg.instance_index in self.instances:
                            crnd = self.instances[msg.instance_index]["c_rnd"]
                            if self.instances[msg.instance_index]["votes2"][crnd]<2: 
                                if msg.v_rnd == crnd:
                                    self.instances[msg.instance_index]["votes2"][crnd]+=1


                                    if self.instances[msg.instance_index]["votes2"][crnd] > int(NUM_ACCEPTORS/2):
                    
                                        # print("recieve  2b quo",msg)
                                        # sys.stdout.flush()
                                    
                                        self.instances[msg.instance_index]["timert"] = None
                                    


                                        # print(msg)
                                        # sys.stdout.flush()
                                        self.decision[msg.instance_index] = msg.v_val
                                        newmsg = self.create_message(msg)
                                        newmsg = pickle.dumps(newmsg)
                                        self.sender.sendto(newmsg, self.config['learners'])

                    
                    if msg.phase == "CATCHUP":
                        if not self.decision =={}:
                            newmsg = message()
                            newmsg.phase = "CAUGHTUP"
                            newmsg.decision = {}
                            for i in self.decision:
                                if i in msg.gap:
                                    newmsg.decision[i] = self.decision[i]
                    
                            # print("whats wrong", newmsg.decision)
                            # sys.stdout.flush()
                            newmsg = pickle.dumps(newmsg)
                            self.sender.sendto(newmsg, self.config['learners']) 

                for ins in (self.instances):
                    curr_instance = self.instances[ins]
                    curr_time = time.time()
                    if not curr_instance["timert"] == None:
                        time_elapsed = curr_time - curr_instance["timert"]
                        if time_elapsed > 1:
                            curr_instance["c_rnd"] += 100
                            ic_rnd = curr_instance["c_rnd"]
                            curr_instance["votes1"][ic_rnd] = 0
                            curr_instance["votes2"][ic_rnd] = 0
                            msg = message()
                            
                            msg.phase = "PHASE1A"
                            msg.c_rnd = curr_instance['c_rnd']
                            msg.instance_index = ins
                            msg.client_val = curr_instance['client_val']
                            
                
                            curr_instance["timert"] = time.time()
                            # print("sending 1a broken",msg)
                            # sys.stdout.flush()
                        
                            msg = pickle.dumps(msg)
                            self.sender.sendto(msg, self.config['acceptors'])



