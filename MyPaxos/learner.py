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
        self.instances_queue = {}
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
    
    def create_instance_in_queue(self, msg):
        if not msg.instance_index in self.instances_queue:
            self.instances_queue[msg.instance_index] = {"v_val":None}
    
    def create_msg_catchup(self,instance_index):
        newmsg = message()
        newmsg.instance_index = instance_index 
        newmsg.phase = "LEARNER-CATCHUP"
        newmsg.learner_id = self.id
        return newmsg
    
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
            

            # if msg.phase == "DECISION" and self.instances[msg.instance_index]["v_val"]==None:
            if msg.phase == "DECISION":
                print("HERE 1")
                
                if msg.instance_index == 0: #check if first message
                    self.create_instance(msg)
                    self.instances[msg.instance_index]["v_val"] = msg.v_val
                    self.print_message(msg)
                    print("HERE 2")
                elif msg.instance_index != 0 and msg.instance_index - 1 in self.instances: #check if previous message was delivered
                    self.create_instance(msg)
                    self.instances[msg.instance_index]["v_val"] = msg.v_val
                    self.print_message(msg)
                    print("HERE 3")

                #if not, then catch up
                else:
                    print("HERE 4")
                    #add the new message to the queue and then we add it to the main instances set once we are ready
                    self.create_instance_in_queue(msg)
                    self.instances_queue[msg.instance_index]["v_val"] = msg.v_val

                    #find last existing index (we are guaranteed that there are no missing indices between the previous index and the 0 index)
                    last_index = 0
                    if self.instances: 
                        last_index = list(self.instances)[-1] + 1
  
                    #ask proposer for last index
                    newmsg = self.create_msg_catchup(last_index)
                    newmsg = pickle.dumps(newmsg)
                    self.sender.sendto(newmsg, self.config['proposers'])



            if msg.phase == "LEARNER-CATCHUP":
                print("HERE 6")
                if msg.learner_id == self.id: #make sure the response if for specific the current learner
                    print("HERE 7")
                    self.create_instance(msg)
                    self.instances[msg.instance_index]["v_val"] = msg.v_val
                    self.print_message(msg)
                    
                    #now we check to see if the next item in the queue follows this past message
                    current_msg_idx = msg.instance_index
                    while self.instances_queue:
                        idx = list(self.instances)[0]
                        print("HERE 8")
                        if current_msg_idx + 1 == idx:
                            print("HERE 9")
                            print(self.instances)
                            print(self.instances_queue)
                            #self.instances[idx]["v_val"] = self.instances_queue[idx]["v_val"] #add the msg from queue
                            self.instances[idx] = self.instances_queue[idx]
                            self.instances_queue.pop(idx) #remove msg from queue
                            current_msg_idx = idx #update current_msg_idx to the new one just added to instances
                        else:
                            print("HERE 10")
                            print(self.instances)
                            current_msg_idx += 1
                            newmsg = self.create_msg_catchup(current_msg_idx)
                            newmsg = pickle.dumps(newmsg)
                            self.sender.sendto(newmsg, self.config['proposers'])
                            break


                



        




    
