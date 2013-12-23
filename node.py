import json 
import messages
import random
import hashing
import leveldb
import routing_table
import time
from thread import start_new_thread
import threading
from constants import *

class Node:
    ''' Node class.

    Usage:
        n = Node(some_socket, 42)
        net_id = n.JoinNetwork(bootstrap_ip_addr)
        n.run() # accepts connections forever in a new thread

        If the node is not the first node in the network, you can tell it to
        join a network if you know an existing node:
        n.JoinNetwork(bootstrap_node_ip)

        You can interface with the node while it is running like so:

        n.Search(["abc", "hello", "keyword"])

        Which will eventually return results or timeout errors.

        Then, to stop it:

        same_net_id = n.LeaveNetwork() 
        
        Which returns the same net_id as before (as per the spec).
    '''

    def __init__(self, udp_socket, ip_address, node_id):
        ''' Node class constructor.

            Arguments:
                udp_socket:
                    udp socket to be used for communications in this network.
                ip_address:
                    IP address that we're listening on. Needed for some messages to other nodes (eg. ROUTING_INFO).
                
                node_id:
                    node_id of this node to be used in this network.

            Notes:
                Takes node_id in its constructor - this is divergent from the spec.
                However, this makes more sense than taking it in JoinNetwork - 
                otherwise, the first node in a network would not know its id
                This constructor also does the job of "init" from the spec.
                Also takes ip_address from

        '''
        self.node_id = node_id
        self.ip_address = ip_address
        self.udp_socket = udp_socket
        self.routing_table = routing_table.RoutingTable()
        self.routing_table_lock = threading.Lock()
        self.net_id = 0
        # The acks_waiting dict is a map of (ip, port) -> threads waiting to be ACKed.
        # The threads count down from N seconds and then throws an error. 
        # We tell the thread to stop counting down when an ACK is received for that address.
        self.acks_waiting = {}
        self.acks_waiting_lock = threading.Lock()
        # LevelDB is a string/string key -> value store. We just use it to persistently store
        # URL -> frequency for our word. 
        self.db = leveldb.LevelDB("./db")

    def Run(self):
        ''' The main loop of the class - just receives data on the UDP port and dispatches threads to handle 
            it asynchronously. Doesn't block, dispatches a new thread.
        '''
        start_new_thread(self._Run, ())

    def _Run(self):
        while True:
            data, addr = self.ReceiveMessage()
            start_new_thread(self.DecodeMessage, (data, addr))

    def JoinNetwork(self, bootstrap_node_ip):
        ''' Joins a network through a node on IP bootstrap_node_ip.
        
        Arguments:
            bootstrap_node_ip: The IP address of the node through which we will join a network.
        '''
        msg = messages.JoiningNetworkMessage(self.node_id, bootstrap_node_ip)
        self.SendMessage(msg, bootstrap_node_ip, UDP_PORT)
        # Wait to get a response from the bootstrap node
        json_message, addr = self.udp_socket.recvfrom(MAX_MESSAGE_SIZE)
        response = messages.Message(json_message=json_message)
        # We incorporate all of the bootstrap node's routing table into our own
        self.routing_table_lock.acquire()
        self.routing_table.from_json(response.msg["routing_table"])
        self.routing_table_lock.release()
        # The NetID isn't used for any external communication, so it doesn't matter
        # if it's random within each client's internals.
        self.net_id = random.randint(0, 4096)
        return self.net_id

    def SendMessage(self, message, node_id):
        # Find the closest node and send the message to it
        closest_node_id = self.routing_table.find_closest_match(node_id, self.node_id)
        if node_id != self.node_id:
            destination_ip = self.routing_table[closest_node_id]
            print "Message destined for", node_id, " - sent to closest id: ", closest_node_id
            self.udp_socket.sendto(message, (destination_ip, UDP_PORT))
        else:
            print "ERROR! No node_id closer to", node_id, "thank our own (,", self.node_id, ")! Abandoning sending!"

    def ReceiveMessage(self):
        data, addr = self.udp_socket.recvfrom(MAX_MESSAGE_SIZE)
        return (data, addr)

    def LeaveNetwork(self, network_id):
        # The spec calls for us to pass the network_id to leave as an argument, and return a boolean success 
        if self.net_id is not network_id:
            print "Invalid net_id passed to leave network - refusing to leave!"
            return False
        leaving_message_json = messages.LeavingNetworkMessage(self.node_id).json()
        # Tell every node in our routing table that we're leaving
        self.routing_table_lock.acquire()
        for node_id in self.routing_table.keys():
            self.SendMessage(leaving_message_json, node_id)
        return True
        self.routing_table_lock.release()

    def RequestIndex(self, word, urls):
        ''' Send a request to ask a node to index a URL for a word
        '''
        target_id = hashing.HashCode(word)
        msg = messages.IndexMessage(target_id, self.node_id, word, urls).json()
        # Send the message over the overlay network - ie, not directly (unless possible)
        closest_id = self.routing_table.find_closest_match(target_id, self.node_id)
        self.SendMessage(msg, closest_id)
        # We want an ACK sent back to us over the overlay network
        self.acks_waiting_lock.acquire()
        start_new_thread(self.AckThreadRun, (target_id, ACK_TIMEOUT_MS))
        self.acks_waiting[target_id] = True
        self.acks_waiting_lock.release()

    def IndexPage(self, url):
        # Since we only index one word, our DB can be an mapping of URL -->
        # frequency of our single word
        keyword_frequency = 1
        try:
            keyword_frequency += self.db.Get(url)
        except:
            pass
        self.db.Put(url, str(keyword_frequency))

    def Search(self, keywords):
        for keyword in keywords:
            target_id = hashing.HashCode(keyword)
            closest_node_id = self.routing_table.find_closest_match(target_id)
            msg = messages.SearchMessage(word, target_id, self.node_id).json()

    def DecodeMessage(self, json_message, addr):
        try:
            incoming_message = json.loads(json_message)
            msg_type = incoming_message["type"]
            # Note: routing_info should not be handled here.
            # it should really never arrive after the node is initialised.
            if msg_type == "JOINING_NETWORK_SIMPLIFIED":
                # A node is joining the network and wants us to 'bootstrap' them.
                # Send JOINING_NETWORK_RELAY the node CLOSEST to the new node.
                closest_node_id = incoming_message["target_id"]
                relay_msg = messages.JoiningNetworkRelayMessage()
                self.SendMessage(closest_node_id, relay_msg)

                # Add their IP and node_id to our routing table.
                self.routing_table[joining_node_id] = incoming_message["ip_address"]

            elif msg_type == "JOINING_NETWORK_RELAY":
                dest_id = incoming_message["target_id"]
                if target_id == self.node_id:
                    joining_node_id = incoming_message["node_id"]
                    # Send ROUTING_INFO to them
                    routing_msg = RoutingInfoMessage(self.node_id, joining_node_id,
                            self.ip_address, self.routing_table.to_json()).json()           
                    # Add their IP and node_id to our routing table
                    # Note: this has to be after generating the message because we don't want to 
                    # send them their own routing info (makes no sense)
                    self.routing_table[joining_node_id] = incoming_message["ip_address"] 
                    # Send them the routing info 
                    self.SendMessage(routing_msg, joining_node_id)
                else:
                    closer_id = self.routing_table.find_closest_match(dest_id)
                    self.SendMessage(incoming_message, closer_id)

            elif msg_type == "LEAVING_NETWORK":
                # Remove node routing info from routing table if exists
                leaving_node_id = incoming_message["node_id"]
                try:
                    self.routing_table.pop(leaving_node_id, None)
                except KeyError:
                    print "Tried to remove a node from our routing table that didn't exist, just ignoring."

            elif msg_type == "INDEX":
                # Add data into DB
                dest_id = incoming_message["target_id"] 
                if self.node_id == dest_id:
                    # Then this message is for us, index all the URLs in it
                    for url in incoming_message["link"]:
                        self.IndexPage(url)
                    # Send an ACK to the sender_id so they know we got it
                    ack_msg = messages.AckMessage(self.node_id)
                    ack_destination = incoming_message["sender_id"]
                    self.SendMessage(ack_msg, ack_destination)
                    self.acks_waiting_lock.acquire()
                    self.acks_waiting[ack_destination] = True
                    self.acks_waiting_lock.release()
                else:
                    # Not for us to index. Pass it on through the overlay network
                    closer_id = self.routing_table.find_closest_match(dest_id)
                    self.SendMessage(incoming_message, closer_id)

            elif msg_type == "SEARCH":
                # If we're responsible for the word, great! Tell them about it
                # Otherwise pass it on
                dest_id = incoming_message["node_id"]
                if dest_id == self.node_id:
                    # Send search response back to the sender_id
                    word = incoming_message["word"]
                    sender_id = incoming_message["sender_id"]
                    response = messages.SearchResponse(word, sender_id, self.node_id, self.DumpDBEntries) 
                else:
                    # Not for us, send it over the overlay network
                    closer_id = self.routing_table.find_closest_match(dest_id)
                    self.SendMessage(incoming_message, closer_id)

            elif msg_type == "SEARCH_RESPONSE":
                # Awesome, we got results for the stuff we were searching for
                sender_id = incoming_message["sender_id"]
                word = incoming_message["word"]
                response = incoming_message["response"]
                print "Got search response for word:", word, ". Results are:\n", response

            elif msg_type == "PING":
                # PONG 'em
                pass

            elif msg_type == "ACK":
                # They got our message
                # Make sure we don't retry again
                sender_id = incoming_message["node_id"]
                self.acks_waiting_lock.acquire()
                self.acks_waiting[sender_id] = False
                self.acks_waiting_lock.release()

            else:
                print "Junk message from", addr, " - ignoring"
            # Check if we're still waiting for a reply from this host 

            # Since we got a message from the sending node, we know it's still alive so we can clear any
            # ACKs that we are waiting to receive from it.
            self.acks_waiting_lock.acquire()
            self.acks_waiting[addr] = False
            self.acks_waiting_lock.release()

        except:
            print "Junk message receiver from", addr, "could not be parsed from JSON - ignoring!"

    def AckThreadRun(self, node_id, timeout_s):
        # Wait for an ACK for timeout_s
        time.sleep(timeout_s)
        # If we have waited until now and have not been stopped by
        # the calling program, then we have NOT received an ACK
        # from this node_id yet
        self.acks_waiting_lock.acquire()
        if self.acks_waiting[node_id] is True:
            print "ERROR: No ACK received from node", node_id, " in max timeout (", timeout_ms, "s)"
            self.acks_waiting[node_id] = False
            # This person hasn't responded to pings to we can just remove it from our routing table.
            try:
                self.routing_table.pop(node_id)
            except KeyError:
                pass
        self.acks_waiting_lock.release()


    def DumpDBEntries(self):
        dumped = []
        for url, freq in self.db.RangeIter():
            dumped.append({ "url" : url, "rank" : freq })
        return json.dumps(dumped)

    def ShowEntries(self, url=None):
        print "Showing all indexed entries:"
        if url is not "" and url is not None:
            try:
                frequency = self.db.Get(url)
                print url, " -- ", frequency
            except KeyError:
                print "URL", url, "not indexed by this node."
        else:
            for url, frequency in self.db.RangeIter():
                print url, "--", frequency

    def Shell(self):
        help_msg = "Welcome to the node shell. Commands: search | quit | show | add | index | ?"
        print help_msg
        prompt = "n:" + str(self.node_id) + " >> "
        while True:
            command = raw_input(prompt).lower()
            if command == "search":
                terms = raw_input("Comma-separated search terms >> ")
                terms = terms.split(",")
                print "Searching for terms:", terms, " - results will come back asynchronously (or report errors)"
                self.Search(terms)
            elif command == "quit":
                print "Sending goodbye messages."
                self.LeaveNetwork(self.net_id)
                break
            elif command == "show":
                url = raw_input("URL to show (hit return for all) >> ")
                self.ShowEntries(url)
            elif command == "add":
                url = raw_input("URL to add >>")
                frequency = raw_input("Frequency to store >>")
                self.db.Put(url, frequency)
                print "Added URL", url, "with frequency", frequency
            elif command == "index":
                word = raw_input("Word to index >> ")
                url = raw_input("Associated url >> ")
                print "Sending index request for word, '", word, "' :", url
                dest_id = hashing.HashCode(word)
                self.RequestIndex(word, url)
                self.acks_waiting_lock.acquire()
                start_new_thread(self.AckThreadRun, (dest_id, ACK_TIMEOUT_MS))
                self.acks_waiting[dest_id] = True
                self.acks_waiting_lock.release()
            elif command == "?":
                print help_msg
            else:
                print "Bad command:", command
                print help_msg
