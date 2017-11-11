import argparse             # for command-line argument parsing
import json                 # for encoding data sent through TCP
import random               # for random path selection
import socket               # for TCP communication
import threading            # for one thread per TCP connection

import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../stealth'))
import stealth


#   TODO:
#    - incorporate encryption key mgmt
#    - directory ping of nodes causes routers to fail, must start directory
#      before router

#   CLI ARGS
###############################################################################

parser = argparse.ArgumentParser() # instantiate cli args parser

# define cli positional args
parser.add_argument("max_nodes", help="qty of nodes in network", type=int)
parser.add_argument("port", help="port to listen on", type=int)
parser.add_argument("-v", "--verbose",
                    help="level of logging verbose", action="store_true")

args = parser.parse_args() # parse the args

# validate args against conditions
if args.max_nodes > 50 or args.max_nodes < 1: # no more than 50 nodes
    parser.error("max_nodes must satisfy: 1 <= max_nodes <= 50")
if args.port < 5551 or args.port > 5557: # 7 group members, each get a port
    parser.error("port must satisfy: 5551 <= port <= 5557")



#   GLOBALS
#################################################################################

HOST = ""                            # empty string => all IPs of this machine
PORT = args.port                     # port for server to listen on, cli arg

MAX_NODES = args.max_nodes           # max number of nodes in onion network
NODE_FORMAT = "lab2-{}.cs.mcgill.ca" # python formatstring of nodes' domain names
NODES = [NODE_FORMAT.format(i) for i in range(1, MAX_NODES+1)]

KEYPAIR = stealth.RSAVirtuoso()              # directory's encryption key pairs

LISTEN_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
LISTEN_SOCKET.bind((HOST, PORT))
LISTEN_SOCKET.listen(MAX_NODES)


#   MAIN
#################################################################################

def main():
    global NODES

    if args.verbose: print('[Status] Querying network nodes...')
    NODES = list( filter(ping_node, NODES) ) # keep nodes that respond to ping
    NODES = list( zip(NODES, map(get_node_pubkey, NODES)) )  # and get pubkeys

    if args.verbose: print('[Status] Directory UP')
    try:
        run_directory_node()
    except (socket.error, KeyboardInterrupt) as e:
        shut_down_directory_node()
        if args.verbose: print('[Error] Directory DOWN')
        exit(str(e))



#   INITIALIZE NODES LIST, GET PUBKEYS
###############################################################################

# return true if node is activated
def ping_node(ndn): # ndn = node domain name
    socket.setdefaulttimeout(0.7) # (seconds) to ping node faster

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    exit_code = s.connect_ex((ndn,PORT))
    s.close()

    socket.setdefaulttimeout(None) # restore default
    
    if args.verbose: 
        node_status = "LISTENING" if not exit_code else "DOWN"
        print("Node {} is {}".format(ndn,node_status))

    return not exit_code

# get node pubkey
def get_node_pubkey(ndn): # ndn = node domain name
    # TODO: fill this in
    return "not a real pubkey"



#   THE DIRECTORY NODE SERVER
###############################################################################

def run_directory_node():
    global LISTEN_SOCKET

    while True:
        conn, addr = LISTEN_SOCKET.accept()
        print('[Status] Connected to: {}:{}'.format(addr[0], str(addr[1])))

        # new thread for each connection
        #t = threading.Thread(target=handle_path_request, args=(conn,), daemon=True) # TODO commented until reported to py3
        t = threading.Thread(target=handle_path_request, args=(conn,))
        t.setDaemon(True)
        t.start()

def shut_down_directory_node():
    LISTEN_SOCKET.close()


def handle_path_request(conn):
    data = conn.recv(1024).decode('utf-8').rstrip()
    if args.verbose: print('[Status] Recieved path request from {}'.format(data)) 

    # TODO: read path request, decrypt, enrypt with symkey
    conn.sendall( json.dumps(get_path()).encode('utf-8') )

    conn.close()


def get_path():
    # TODO implement actual retrieval of data
    path =  [{'addr':'lab2-1','key':'KEY_1'},
            {'addr':'lab2-2','key':'KEY_2'},
            {'addr':'lab2-3','key':'KEY_3'}]
    if args.verbose: print('[Status] Selected path: {}'.format(path))
    
    return path



#   RUN MAIN
###############################################################################

if __name__ == '__main__':
    main()
