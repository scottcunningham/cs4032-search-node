# Search Node
Scott Cunningham // 10311491 // cunninsc@tcd.ie

## node.py
The node class differs from the given interface slightly. Python doesn't have
interfaces because it supports multiple inheritance, so I just give the
implementation in a Node class.

The constructor takes udp_socket, ip_address, node_id - it needs to take the
ip_address so that it can generate the JOINING_NETWORK_RELAY message, and the
node_id so that if it is the bootstrap node it knows what its id is (bootstrap
nodes never call JoinNetwork).

## constants.py
Configuration and constants used through several modules.

## hashing.py
Defines a HashCode function to generate node IDs from words.

## messages.py
Defines instantiations of classes that hold messages and can be dumped to JSON.

## populate-db.py
Just generates fake DB entries into the LevelDB in ./db for debugging the Node.

## routing_table.py
A class representing a routing table, serialisable into JSON in the proper 
format (because the spec calls for an array of dictionaries).

## main.py
Instantiates a Node and runs it. Needs one of two sets of command-line arguments:
1. For bootstrap node: --ip=134.226.49.32 --node_id=123 --boot
2. For joining node: --ip=134.226.49.06 --node_id=123 \
                            --bootstrap_ip=134.226.83.42 --target_id=1337
Then it runs an interactive shell with the Node where the user can enter
commands.
The shell can be quit at any time with a CTRL-c. This interrupts the node and
attempts to perform a graceful exit from the network through sending
LeavingNetwork messages.
