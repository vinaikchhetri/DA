#!/usr/bin/env python3
import sys
import socket
import struct
from client import Client
from proposer import Proposer
from acceptor import Acceptor
from learner import Learner

def mcast_receiver(hostport):
    """create a multicast socket listening to the address"""
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    recv_sock.bind(hostport)

    mcast_group = struct.pack("4sl", socket.inet_aton(hostport[0]), socket.INADDR_ANY)
    recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mcast_group)
    return recv_sock


def mcast_sender():
    """create a udp socket"""
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    return send_sock


def parse_cfg(cfgpath):
    cfg = {}
    with open(cfgpath, 'r') as cfgfile:
        for line in cfgfile:
            (role, host, port) = line.split()
            cfg[role] = (host, int(port))
        # print(cfg)
        # breakpoint() 
    return cfg

# ----------------------------------------------------

def acceptor(config, id):
    # print ('-> acceptor', id)
    # state = {}
    # r = mcast_receiver(config['acceptors'])
    # s = mcast_sender()
    # while True:
    #     msg = r.recv(2**16)
    #     # fake acceptor! just forwards messages to the learner
    #     if id == 1:
    #         # print "acceptor: sending %s to learners" % (msg)
    #         s.sendto(msg, config['learners'])
    a = Acceptor(config['acceptors'], id, config)
    a.start()


def proposer(config, id):
    # print ('-> proposer', id)
    # r = mcast_receiver(config['proposers'])
    # s = mcast_sender()
    # while True:
    #     msg = r.recv(2**16)
    #     # fake proposer! just forwards message to the acceptor
    #     if id == 1:
    #         # print "proposer: sending %s to acceptors" % (msg)
    #         s.sendto(msg, config['acceptors'])
    p = Proposer(config['proposers'], id, config)
    p.start()



def learner(config, id):
    # r = mcast_receiver(config['learners'])
    # while True:
    #     msg = r.recv(2**16)
    #     print(msg)
    #     sys.stdout.flush()
    l = Learner(config['learners'], id, config)
    l.start()


def client(config, id):
    # print ('-> client ', id)
    # s = mcast_sender()
    # for value in sys.stdin:
    #     value = value.strip()
    #     print ("client: sending %s to proposers" % (value))
    #     s.sendto(value.encode(), config['proposers'])
    # print ('client done.')
    c = Client(config['clients'], id, config)
    c.start()


if __name__ == '__main__':
        cfgpath = sys.argv[1]
        config = parse_cfg(cfgpath)
        role = sys.argv[2]
        id = int(sys.argv[3])
        if role == 'acceptor':
            rolefunc = acceptor
        elif role == 'proposer':
            rolefunc = proposer
        elif role == 'learner':
            rolefunc = learner
        elif role == 'client':
            rolefunc = client
        rolefunc(config, id)
