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
    def __init__(self, node_id, ip_address):
        Message.__init__(self)
        self.msg["type"] = "JOINING_NETWORK"
        self.msg["ip_address"] = ip_address

class JoiningNetworkRelayMessage(Message):
    def __init__(self, node_id, ip_address):
        Message.__init__(self)
        self.msg["type"] = "JOINING_NETWORK"
        self.msg["ip_address"] = ip_address

class RoutingInfoMessage(Message):
    def __init__(self, bootstrap_id, node_id, ip_address, routing_table):
        Message.__init__(self)
        self.msg["type"] = "ROUTING_INFO"
        self.msg["bootstrap_id"] = bootstrap_id
        self.msg["node_id"] = node_id
        self.msg["ip_address"] = ip_address
        self.msg["route_table"] = routing_table

class LeavingNetworkMessage(Message):
    def __init__(self, node_id):
        Message.__init__(self)
        self.msg["type"] = "LEAVING_NETWORK"
        self.msg["node_id"] = node_id

class IndexMessage(Message):
    def __init__(self, node_id, keyword_id, link):
        Message.__init__(self)
        self.msg["type"] = "INDEX"
        self.msg["node_id"] = node_id
        self.msg["keyword_id"] = keyword_id
        self.msg["link"] = link

class SearchMessage(Message):
    def __init__(self, word, node_id, sender_id):
        Message.__init__(self)
        self.msg["type"] = "SEARCH" 
        self.msg["word"] = word
        self.msg["node_id"] = node_id
        self.msg["sender_id"] = sender_id

class SearchResponseMessage(Message):
    def __init__(self, word, node_id, response):
        Message.__init__(self)
        self.msg["type"] = "SEARCH_RESPONSE"
        self.msg["word"] = word
        self.msg["node_id"] = node_id
        self.msg["response"] = response

class PingMessage(Message):
    def __init__(self, sender_id, node_id, ip_address):
        Message.__init__(self)
        self.msg["type"] = "PING"
        self.msg["sender_id"] = sender_id
        self.msg["node_id"] = node_id
        self.msg["ip_address"] = ip_address

class AckMessage(Message):
    def __init__(self, node_id, ip_address):
        Message.__init__(self)
        self.msg["type"] = "ACK"
        self.msg["node_id"] = node_id
        self.msg["ip_address"] = ip_address
