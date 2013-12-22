#!/usr/bin/python2

from node import Node
import argparse
import socket
import sys

UDP_IP = "127.0.0.1"
UDP_PORT = 8767

parser = argparse.ArgumentParser(description='')
parser.add_argument('--port', metavar='p', type=int, help="Port to listen on.", default=8767)
parser.add_argument('--node_id', type=int, help='NodeID of this node.')
parser.add_argument('--bootstrap_ip', type=str, help='IP address of bootstrap node to contact.')
parser.add_argument('--boot',dest='boot',action='store_true',help='Switch to turn on boot mode, enabling this node to start the network')
parser.set_defaults(boot=False)

args = parser.parse_args()

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((UDP_IP, UDP_PORT))

net_id = 0

if args.node_id is None:
    sys.exit("Missing required flag: --node_id.")

n = Node(udp_socket, args.node_id)

if args.boot:
    # We are the first node
    # Just start listening and wait for people 
    if args.bootstrap_ip is not None:
        sys.stderr.write("Incompatible arguments --bootstrap_ip and --boot passed simultaneously; ignoring --bootstrap_ip.")
else:
    if args.bootstrap_ip is None:
        sys.exit("If the --boot flag is not set, the IP of a bootstrap node must be passed with the --bootstrap_ip flag.")        
    # Join the network
    # Contact the bootstrap node based on the bootstrap_id
    net_id = n.JoinNetwork(args.bootstrap_ip)

n.Run()

try:
    n.Shell()
except KeyboardInterrupt:
    print "Node interrupted, attempting to send LEAVING_NETWORK message for graceful shutdown."
    n.LeaveNetwork(net_id)
