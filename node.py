import json 
from thread import start_new_thread
import messages
import random
import hashing
import leveldb

UDP_PORT = 8767

class Node:
        # Node takes node_id in its ctor - this is divergent for the spec.
        # However, this makes more sense than taking it in JoinNetwork - 
        # otherwise, the first node in a network would not know its id
	# This constructor does the job of the init from the spec.
        def __init__(self, udp_socket, node_id):
		self.node_id = node_id
		self.udp_socket = udp_socket
		self.routing_table = []
		self.net_id = 0
                # The acks_waiting dict is a map of (ip, port) -> threads waiting to be ACKed. The threads count down from 5 seconds and retry messages a few times when the timer runs out. 
                # The Node can then just tell the thread to stop counting down when an ACK is received for that address
		self.acks_waiting = {}
                self.db = leveldb.LevelDB("./db")

	def JoinNetwork(self, bootstrap_node_ip):
		msg = messages.JoiningNetworkMessage(self.node_id, bootstrap_node_ip)
		self.SendMessage(msg, bootstrap_node_ip, UDP_PORT)
		json_message, addr = self.udp_socket.recvfrom(1024)
		# Wait to get a response from the bootstrap node
		response = messages.Message(json_message=json_message)
		self.routing_table = json.loads(response.msg["route_table"])
		self.net_id = random.randint(0,4096)
		return self.net_id

	def SendMessage(self, message, destination_ip, destination_port, retries=1):
		for x in range(retries):
			# try to send msg
			self.udp_socket.sendto(message, (destination_ip, destination_port))
			# sleep for some time
			# if msg ACKed then break

	def ReceiveMessage(self):
		data, addr = self.udp_socket.recvfrom(1024)
		return (data, addr)

        def LeaveNetwork(self, network_id):
		if self.net_id is not network_id:
			print "Invalid net_id passed to leave network - refusing to leave!"
			return False
		leaving_message_json = messages.LeavingMessage(self.node_id).json()
		for node in self.routing_table:
			self.SendMessage(leaving_message_json, (node["ip_address"], UDP_PORT))	 
		return True

	def IndexPage(self, url, keyword_frequency):
		# Since we only index one word, our DB can be an mapping of URL -->
		# frequency of our single word
		self.db.Put(url, str(keyword_frequency))

	def Search(self, keywords):
		pass

	def DecodeMessage(self, json_message, addr):
		msg_dict = json.loads(json_message)
		msg_type = msg_dict["type"]
		# Note: routing_info should not be handled here
		# it should really never arrive after the node is initialised
		if msg_type == "JOINING_NETWORK":
			# Send ROUTING_INFO to them
			# Send JOINING_NETWORK_RELAY to my peers
			# Add their IP and node_id to our routing table
			pass
		elif msg_type == "JOINING_NETWORK_RELAY":
			# Add node_id and ip address to routing table???
			pass
		elif msg_type == "LEAVING_NETWORK":
			# Remove node routing info from routing table if exists
			pass
		elif msg_type == "INDEX":
			# Add data into DB
			pass
		elif msg_type == "SEARCH":
			# If we're responsible for the word, great! Tell them about it
			# Otherwise pass it on
			pass
		elif msg_type == "SEARCH_RESPONSE":
			# Awesome, we got results for the stuff we were searching for
			# Might as well add them to our routing table too, why not
			pass
		elif msg_type == "PING":
			# PONG 'em
			pass
		elif msg_type == "ACK":
			# They got our message, deadly
			# Make sure we don't retry again
			pass
		else:
			print "Junk message from", addr, " - ignoring"
	
        def Run(self):
		while True:
			data, addr = self.ReceiveMessage()
			start_new_thread(self.DecodeMessage, (data, addr))
