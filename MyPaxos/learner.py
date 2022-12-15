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
        self.instance_index = -1
        self.delivered_index = -1
        self.addr = addr
        self.id = id
        self.config = config
        self.sender = self.send_config()
        self.receiver = self.receive_config()
        self.deliver = True
    
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
        print("LOG")
        print(msg)
        sys.stdout.flush()
    
    def print_instance(self, id):
        print(self.instances[id])

    def catch_up(self):
        for i in range(0, self.instance_index + 1):
            if i != -1 and i not in self.instances:
                self.deliver = False
                break

        if self.deliver:
            for i in range((self.delivered_index + 1), (len(self.instances))):
                if i in self.instances and self.instances[i]['v_val'] is not None:
                    print(f"Instance {i}: ", self.instances[i]['v_val'])
                    sys.stdout.flush()
            self.delivered_index = len(self.instances)-1

        else:
            msg = message()
            msg.phase = "LEARNER-CATCHUP"
            msg = pickle.dumps(msg)
            self.sender.sendto(msg, self.config['proposers'])


    def run(self):
        print ('-> learner', self.id)
        while True:
            msg = self.receiver.recv(2**16)
            msg = pickle.loads(msg)
            self.create_instance(msg)


            if msg.phase == "DECISION":
                if msg.instance_index is not None and msg.instance_index > self.instance_index:
                    self.instance_index  = msg.instance_index 
                if msg.instance_index not in self.instances:
                    self.instances[msg.instance_index] = {'v_val': None}
                self.instances[msg.instance_index]['v_val'] = msg.v_val
                self.deliver = True
                self.catch_up()
                

            if msg.phase == "LEARNER-CATCHUP":
                if msg.decisions is not None:
                    if len(msg.decisions) - 1 > self.instance_index:
                        self.instance_index = len(msg.decisions) - 1
                    for instance in msg.decisions:
                        if instance not in self.instances or self.instances[instance]['v_val'] is None:
                            self.instances[instance] = {'v_val': msg.decisions[instance]}
                self.deliver = True
                self.catch_up()

           
  
