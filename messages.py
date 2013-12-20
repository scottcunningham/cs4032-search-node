#!/usr/bin/python2

import json

class Message():
    def __init__(self, json_message=None):
        if json_message is not None:
            self.msg = json.loads(json_message)
        else:
            self.msg = {}

    def json(self):
        return json.dumps(self.msg)

    def type(self):
        if "type" in self.msg.iterkeys():
            return self.msg["type"]
        else:
            raise Exception("Object message incomplete or not properly initialised.")

class JoiningNetworkMessage(Message):
    def __init__(self, node_id, target_id, ip_address):
        Message.__init__(self)
        self.msg["type"] = "JOINING_NETWORK_SIMPLIFIED"
        self.msg["target_id"] = target_id
        self.msg["ip_address"] = ip_address

class JoiningNetworkRelayMessage(Message):
    def __init__(self, node_id, target_id, ip_address):
        Message.__init__(self)
        self.msg["type"] = "JOINING_NETWORK_RELAY"
        self.msg["node_id"] = node_id
        self.msg["target_id"] = target_id
        self.msg["ip_address"] = ip_address

class RoutingInfoMessage(Message):
    def __init__(self, gateway_id, node_id, ip_address, routing_table):
        Message.__init__(self)
        self.msg["type"] = "ROUTING_INFO"
        self.msg["gateway_id"] = gateway_id
        self.msg["node_id"] = node_id
        self.msg["ip_address"] = ip_address
        self.msg["route_table"] = routing_table

class LeavingNetworkMessage(Message):
    def __init__(self, node_id):
        Message.__init__(self)
        self.msg["type"] = "LEAVING_NETWORK"
        self.msg["node_id"] = node_id

class IndexMessage(Message):
    def __init__(self, target_id, sender_id, keyword, link):
        Message.__init__(self)
        self.msg["type"] = "INDEX"
        self.msg["target_id"] = target_id
        self.msg["sender_id"] = sender_id
        self.msg["keyword"] = keyword
        # link is actually a LIST of links...
        self.msg["link"] = link 

class SearchMessage(Message):
    def __init__(self, word, node_id, sender_id):
        Message.__init__(self)
        self.msg["type"] = "SEARCH" 
        self.msg["word"] = word
        self.msg["node_id"] = node_id
        self.msg["sender_id"] = sender_id

class SearchResponseMessage(Message):
    def __init__(self, word, node_id, sender_id, response):
        Message.__init__(self)
        self.msg["type"] = "SEARCH_RESPONSE"
        self.msg["word"] = word
        self.msg["node_id"] = node_id
        self.msg["sender_id"] = sender_id
        self.msg["response"] = response

class PingMessage(Message):
    def __init__(self, target_id, sender_id, ip_address):
        Message.__init__(self)
        self.msg["type"] = "PING"
        self.msg["target_id"] = target_id
        self.msg["sender_id"] = sender_id
        self.msg["ip_address"] = ip_address

class AckMessage(Message):
    def __init__(self, node_id, ip_address):
        Message.__init__(self)
        self.msg["type"] = "ACK"
        self.msg["node_id"] = node_id
        self.msg["ip_address"] = ip_address
