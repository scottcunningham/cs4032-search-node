#!/usr/bin/python2

class RoutingTable(dict):
    def find_closest_match(self, target_key, initial_key):
        closest_key = initial_key

        for key in self.iter_keys():
            if abs(key - target_key) < abs(closest_key - target_key):
                closest_key = key

        return closest_key
