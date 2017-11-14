import argparse             # for command-line argument parsing
import json                 # for encoding data sent through TCP
import random               # for random path selection
import socket               # for TCP communication
import threading            # for one thread per TCP connection

import sys, os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../stealth'))
import stealth              # for communication encryption


#   CLI ARGS
###############################################################################

parser = argparse.ArgumentParser() 

# positional args
parser.add_argument("pr_port", help="dirictory node's path request port", type=int)
parser.add_argument("orkr_port", help="onion routers' pubkey-request port", type=int)
parser.add_argument("-v", "--verbose", help="level of logging verbose", action="store_true")

args = parser.parse_args() # parse the args

# validate args against conditions
if args.max_nodes > 50 or args.max_nodes < 1: # no more than 50 nodes
    parser.error("max_nodes must satisfy: 1 <= max_nodes <= 50")


#   GLOBALS
#################################################################################

# directory node's encryption key pairs
KEYPAIR = stealth.RSAVirtuoso()

# TCP port on which to respond to path requests
PORT = args.pr_port                     

# TCP port on which onion routers listen for pubkey requests
ORKR_PORT = args.orkr_port

# number of onion routers to query for participation
MAX_NODES = 50

# list of routers in the onion network
ROUTERS = ['lab2-{}'.format(i) for i in range(1, MAX_NODES+1)]

# socket to listen for path requests from originators
LISTEN_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
LISTEN_SOCKET.bind(("", PORT))
LISTEN_SOCKET.listen(MAX_NODES)


#   MAIN
#################################################################################

def main():
    global ROUTERS

    if args.verbose: print('[Status] Querying onion routers...')
    
    up_nodes        = filter(ping_node, ROUTERS)
    up_node_pubkeys = map(get_node_pubkey, up_nodes)
    ROUTERS = [{'addr':a, 'key':k} for a,k in zip(up_nodes, up_node_pubkeys)]

    if args.verbose: print('[Status] Directory UP')

    try:
        run_directory_node()
    except (socket.error, KeyboardInterrupt) as e:
        shut_down_directory_node()
        if args.verbose: print('[Error] Directory DOWN')



#   INITIALIZE NODES LIST, GET PUBKEYS
###############################################################################

# return true if node is listening on orkr port
def ping_node(node):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ping_successful = s.connect_ex((node,args.orkr_port))
    s.close()

    if args.verbose: 
        node_status = "LISTENING" if not ping_successful else "DOWN"
        print("Node {} is {}".format(ndn,node_status))

    return not exit_code

def get_node_pubkey(node):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((node,args.orkr_port))

    s.sendall(b'get_key')
    key = s.recv(2048).decode('utf-8')

    s.close()
    
    return key 


#   THE DIRECTORY NODE SERVER
###############################################################################

def run_directory_node():
    while True:
        conn, addr = LISTEN_SOCKET.accept()
        print('[Status] Connected to: {}:{}'.format(addr[0], str(addr[1])))

        # new thread for each connection
        t = threading.Thread(target=handle_path_request, args=(conn,))
        t.setDaemon(True)
        t.start()


def shut_down_directory_node():
    LISTEN_SOCKET.close()


def handle_path_request(conn):
    data = conn.recv(1024).decode('utf-8').rstrip()
    if args.verbose: print('[Status] Recieved path request from {}'.format(data)) 

    path = random.sample(ROUTERS, 3)
    if args.verbose:
        print('[Status] Selected path: {}, {}, {}'.format(*[path[i]['addr'] for i in range(3)]))
    
    # TODO: encrypt message
    
    conn.sendall(json.dumps(path).encode('utf-8'))

    conn.close()


#   RUN MAIN
###############################################################################

if __name__ == '__main__':
    main()
