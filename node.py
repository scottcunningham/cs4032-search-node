import socket
import json 
from thread import start_new_thread
import messages

# Because the protocol depends on integer overflow, we have to do these ridiculous things
from numpy import int32
import warnings
warnings.simplefilter("ignore", RuntimeWarning)

UDP_PORT = 8767
BACKOFF_TIME_MS = 5000

def node(node_id, ip_address):
    return { "node_id" : node_id, "ip_address" : ip_address }

class Node:
    def __init__(self, udp_socket, node_id):
        self.node_id = node_id
        self.udp_socket = udp_socket
        self.routing_table = []
        # Need mechanism for dealing with ACKed messages...

    def SendMessage(self, message, destination_ip, destination_port, retries=1):
        for x in range(retries):
            # try to send msg
            self.udp_socket.sendto(message, (destination_ip, destination_port))
            # sleep for some time
            # if msg ACKed then break

    def ReceiveMessage(self):
        data, addr = self.udp_socket.recvfrom(1024)
        return (data, addr)

    def JoinNetwork(self, bootstrap_node_ip):
        msg = messages.JoiningNetworkMessage(self.node_id, bootstrap_node_ip)
        self.SendMessage(msg, bootstrap_node_ip, UDP_PORT)
        json_message, addr = self.udp_socket.recvfrom(1024)
        response = messages.Message(json_message=json_message)
        if response.type() is not "ROUTING_TABLE":
            print "lol dunno???"
        self.routing_table = json.loads(response.msg["route_table"])

    def LeaveNetwork(self, network_id):
        leaving_message_json = messages.LeavingMessage(self.node_id).json()
        for node in self.routing_table:
            self.SendMessage(leaving_message_json, (node["ip_address"], UDP_PORT))     

    def IndexPage(self, url, keywords):
        pass

    def Search(self, keywords):
        pass

    def DecodeMessage(self, json_message, addr):
        msg_dict = json.loads(json_message)
        print msg_dict

    def HashCode(input_string):
        code = int32(0)
        for char in input_string:
            code = (code * int32((31))) + int32(ord(char))
        return code

    def Run(self):
        while True:
            data, addr = self.ReceiveMessage()
            start_new_thread(self.DecodeMessage, (data, addr))
