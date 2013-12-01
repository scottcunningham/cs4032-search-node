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

class Node:
	def __init__(self, udp_socket, node_id):
		self.node_id = node_id
		self.udp_socket = udp_socket
		self.routing_table = {}
        # Need mechanism for dealing with ACKed messages...
        

	def SendMessageWithRetry(self, message, destination_ip, destination_port, retries=5):
        # Open socket to destination
        s = socket(AF_INET,SOCK_DGRAM)

        for x in range(retries):
            # try to send msg
            s.sendto(message, (destination_ip, destination_port))
            # sleep for some time
            # if msg ACKed then break

	def JoinNetwork(self, bootstrap_node_ip):
		msg = messages.JoiningNetworkMessage(self.node_id, bootstrap_node_ip)
        SendMessageWithRetry(msg, bootstrap_node_ip, UDP_PORT) 

	def LeaveNetwork(self, network_id):
		pass

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

    def GracefulExit(self):
        pass
        # For everything in routing table, just reply saying goodbye

	def Run(self):
		while True:
			data, addr = self.udp_socket.recvfrom(1024)
			start_new_thread(self.DecodeMessage, (data, addr))
