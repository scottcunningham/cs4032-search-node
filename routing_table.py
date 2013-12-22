#!/usr/bin/python2

import json

class RoutingTable(dict):
    def from_json(self, msg):
        # routing information comes in as a JSON list of JSON dictionaries
        # which parse to a list of dictionaries of the form:
        # { "node_id" : "something", "ip_address" : "something else" }
        nodes = json.dumps(msg)
        # Just parse it into dictionary form -
        # node_id as key and ip as value
        for node in nodes:
            # JSON, even when given an integer key to begin with, casts keys to strings
            # So we have to manually cast them back to integers here.
            self[int(node["node_id"])] = node["ip_address"]

    def to_json(self):
        dictlist = []
        for key, value in dict.iteritems():
            dictlist.append({"ip_address":value, "node_id":key})
        return json.dumps(dictlist)

    def find_closest_match(self, target_key, initial_key):
        closest_key = initial_key

        for key in self.keys():
            if abs(key - target_key) < abs(closest_key - target_key):
                closest_key = key

        # Pair of (IP, node_id)
        return closest_key
