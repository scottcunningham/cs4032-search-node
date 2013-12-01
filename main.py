from node import Node
import argparse
import signal
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
print args.port
print args.boot

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((UDP_IP, UDP_PORT))

if args.node_id is None:
    sys.exit("Missing required flag: --node_id.")

n = Node(udp_socket, args.node_id)

if args.boot:
    if args.bootstrap_ip is not None:
        sys.stderr.write("Incompatible arguments --bootstrap_ip and --boot passed simultaneously; ignoring --bootstrap_ip.")
    # We are the first node
    # Just start listening and wait for people 

else:
    pass
    if args.bootstrap_ip is None:
        sys.exit("If the --boot flag is not set, the IP of a bootstrap node must be passed with the --bootstrap_ip flag.")        
    # Join the network
    # Contact the bootstrap node based on the bootstrap_id
    n.JoinNetwork(args.bootstrap_ip)
    # Wait to get the ROUTING_INFO

try:
    n.Run()
except KeyboardInterrupt:
    print "Node interrupted, attempting to send LEAVING_NETWORK message"
    n.GracefulExit()
