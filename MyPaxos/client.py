import socket
import struct

# set socket option: https://www.ibm.com/docs/en/i/7.1?topic=ssw_ibm_i_71/apis/ssocko.html

class Client:

    def __init__(self, ip, port):

        self.ip = ip
        self.port = port
        self.server = self.create_server()
        self.client = self.create_client()

    def create_server(self):
        recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
        recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, 
                        struct.pack('4sL', socket.inet_aton(self.ip), socket.INADDR_ANY))
        return recv_sock
    
    def create_client(self):
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
        send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, 
                        struct.pack('4sL', socket.inet_aton(self.ip), socket.INADDR_ANY))
        return send_sock

    
