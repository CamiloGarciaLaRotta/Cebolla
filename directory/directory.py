import argparse             # for command-line argument parsing
import json                 # for encoding data sent through TCP
import random               # for shuffling node indices during path selection
import socket               # for TCP communication
from _thread import *       # for threaded client TCP connections

###############################################################################
#                                                                             #
#   TODO                                                                      #
#    - incorporate encryption key mgmt                                        #
#                                                                             #
###############################################################################


###############################################################################
#   CLI ARGS                                                                  #
###############################################################################

parser = argparse.ArgumentParser() # instantiate cli args parser

# define cli args
parser.add_argument("port", help="port to listen on", type=int)
parser.add_argument("max_nodes", help="qty of nodes in network", type=int)

args = parser.parse_args() # parse the args

# validate args against conditions
if args.max_nodes > 50 or args.max_nodes < 1: # no more than 50 nodes
    parser.error("max_nodes must satisfy: 0 < max_nodes < 50")
if args.port < 5551 or args.port > 5557: # 7 group members, each get a port for testing
    parser.error("port must satisfy: 5551 <= port < 5557")

###############################################################################
#   GLOBALS                                                                   #
###############################################################################

HOST = ""           # empty string => all IPs of this machine
PORT = args.port    # port for server to listen on, cli arg

MAX_NODES = args.max_nodes # max number of nodes in onion network
NODE_FORMAT = "cs-{}.cs.mcgill.ca" # python format string of nodes' domain names
NODES = [NODE_FORMAT.format(i) for i in range(1, MAX_NODES+1)] # all nodenames

# socket listens on HOST:PORT
LISTEN_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
LISTEN_SOCKET.bind((HOST, PORT))
LISTEN_SOCKET.listen(MAX_NODES)

print("congratz you parsed the args")
exit()

###############################################################################
#   MAIN                                                                      #
###############################################################################

def main():
    global NODES

    NODES = NODES.map(query_node) # find which nodes are activated
    NODES = list( zip(NODES, NODES.map(get_node_pubkey)) ) # and get their pubkeys

    # try:
        # start_server()
    # except (socket.error, KeyboardInterrupt) as e:
        # stop_server()
        # sys.exit(str(e))


###############################################################################
#   INITIALIZE NODES LIST                                                     #
###############################################################################

# fills the NODES lsit with the machines in the LAN that are listening on PORT
def query_node():
    print('Querying the network ...')

    for node_name in NODES:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        timeout = s.connect_ex((node_name,PORT))
        s.close()

        # This functionality was already tested,
        # commented out to avoid having to setup TCP clients  while testing
        #        if timeout or hostname in NODES:
        #            NODES.remove(node_name)

    random.shuffle(NODES)

    print('There are {} node(s) in the network'.format(len(NODES)))


###############################################################################
#   THE DIRECTORY NODE SERVER                                                 #
###############################################################################

# creates worker threads for the TCP server
def start_server():
    directory_socket.bind((HOST,PORT))
    directory_socket.listen(len(NODES))

    print('Directory Node UP')

    while True:
        conn, addr = directory_socket.accept()
        print('Connected to: {}:{}'.format(addr[0], str(addr[1])))
        start_new_thread(threaded_client,(conn,))

def stop_server():
    directory_socket.close()
    print('Directiry Node DOWN')

# thread function wich establishes TCP connection with a client
# recieves a destination node and returns a random path
# in case of invalid input or no available CNs an empty object is returned
def threaded_client(conn):
    data = conn.recv(1024)

    path = get_path(data.decode('utf-8').rstrip())

    conn.sendall(str.encode(path))

    conn.close()


def get_path(dst):
    return random.sample(NODES, 3)

###############################################################################
#   RUN MAIN                                                                  #
###############################################################################

if __name__ == '__main__':
    main()
