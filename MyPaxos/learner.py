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
        self.max_instance_index = -1
        self.last = 0
    
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
        if not msg.instance_index in self.instances and not msg.instance_index == -1:
            self.instances[msg.instance_index] = {"v_val":None}
            if self.max_instance_index < msg.instance_index:
                self.max_instance_index = msg.instance_index

    def print_message_and_call(self):
        # print("LOG "+str(self.id)+" :",self.len)
        # sys.stdout.flush()
        # print(msg)
        # # print(msg.v_val)
        # sys.stdout.flush()
        flag = 0
        for i in range(self.last, self.max_instance_index+1):
            if i not in self.instances:
                flag=1
                break
        if flag==1:
            newmsg = message()
            newmsg.phase = "CATCHUP"
            newmsg = pickle.dumps(newmsg)
            self.sender.sendto(newmsg, self.config['proposers'])

        if flag==0:
            print("here",self.last)
            sys.stdout.flush()
            for i in range(self.last, self.max_instance_index+1):
                print("LOG "+str(self.id))
                sys.stdout.flush()
                print("inst", i, "val: ",self.instances[i]["v_val"] )
                sys.stdout.flush()
            self.last = self.max_instance_index+1

    def print_message(self):
        flag = 0
        for i in range(self.last, self.max_instance_index+1):
            if i not in self.instances:
                flag=1
                break

        if flag==0:
            print("here",self.last)
            sys.stdout.flush()
            for i in range(self.last, self.max_instance_index+1):
                print("LOG "+str(self.id))
                sys.stdout.flush()
                print("inst", i, "val: ",self.instances[i]["v_val"] )
                sys.stdout.flush()
            self.last = self.max_instance_index+1
  
    
    def print_instance(self, id):
        print(self.instances[id])

    def run(self):
        print ('-> learner', self.id)
        while True:
            msg = self.receiver.recv(2**16)
            msg = pickle.loads(msg)
            self.create_instance(msg)

            if msg.phase == "DECISION" and self.instances[msg.instance_index]["v_val"]==None:
                self.instances[msg.instance_index]["v_val"] = msg.v_val
                self.print_message_and_call()
            
            if msg.phase == "CAUGHTUP":
               
                for i in range(self.last, self.max_instance_index+1):
                    if i not in self.instances and i in msg.decision:
                        self.instances[i] = {"v_val":None}
                        self.instances[i]["v_val"] = msg.decision[i]
                        

                self.print_message()


            # if msg.phase == "DECISION":
            #     self.len+=1
            #     self.instances[msg.instance_index]["v_val"] = msg.v_val
            #     self.print_message(msg)

                



        




    
