import argparse             # for command-line argument parsing
import json                 # for encoding data sent through TCP
import random               # for random path selection
import socket               # for TCP communication
import threading            # for one thread per TCP connection
from Crypto.Random.Fortuna.FortunaGenerator import AESGenerator

import sys, os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../stealth'))
import stealth              # for communication encryption
from stealth import AESProdigy


#   CLI ARGS
###############################################################################

# define cli positional args
parser = argparse.ArgumentParser() 

parser.add_argument("max_nodes", help="Quantity of nodes in network", type=int)
parser.add_argument("port", help="Port to listen on for path requests", type=int)
parser.add_argument("dir_port", 
                    help="Port that routers will listen for Directory", type=int)
parser.add_argument("-v", "--verbose",
                    help="level of logging verbose", action="store_true")

args = parser.parse_args() # parse the args

# validate args against conditions
if args.max_nodes > 50 or args.max_nodes < 1: # no more than 50 nodes
    parser.error("max_nodes must satisfy: 1 <= max_nodes <= 50")
# TODO disabled to a facilitate testing
#if args.port < 5551 or args.port > 5557: # 7 group members, each get a port
#    parser.error("port must satisfy: 5551 <= port <= 5557")


#   GLOBALS
#################################################################################


KEYPAIR = stealth.RSAVirtuoso()             # directory's encryption key pairs

ROUTERS = []                                # available routers in the onion network

HOST = ""                            
PORT = args.port                     
MAX_NODES = args.max_nodes                  # max number of nodes in onion network

LISTEN_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
LISTEN_SOCKET.bind((HOST, PORT))
LISTEN_SOCKET.listen(MAX_NODES)


#   MAIN
#################################################################################

def main():
    global ROUTERS
    
    if args.verbose: print('[Status] Querying network nodes...')
    
    # build list of available routers with their respective encryption keys
    nodes = ['lab2-{}'.format(i) for i in range(1, MAX_NODES+1)]
    up_nodes = list( filter(ping_node, nodes) ) 
    nodes_keys = zip(up_nodes, map(get_node_pubkey, up_nodes))
    ROUTERS = [{'addr':x[0], 'key':x[1], 'port': PORT} for x in nodes_keys]

    if args.verbose: print('[Status] Directory UP')
    try:
        run_directory_node()
    except (socket.error, KeyboardInterrupt) as e:
        shut_down_directory_node()
        if args.verbose: print('[Error] Directory DOWN')



#   INITIALIZE NODES LIST, GET PUBKEYS
###############################################################################

# return true if node is listening on dir port
def ping_node(ndn): # ndn = node domain name
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    exit_code = s.connect_ex((ndn,args.dir_port))
    s.close()

    if args.verbose: 
        node_status = "LISTENING" if not exit_code else "DOWN"
        print("Node {} is {}".format(ndn,node_status))

    return not exit_code

def get_node_pubkey(ndn): # ndn = node domain name
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ndn,args.dir_port))

    s.sendall(b'get_key')
    key = s.recv(2048).decode('utf-8')

    s.close()
    
    return key 


#   THE DIRECTORY NODE SERVER
###############################################################################

def run_directory_node():
    global LISTEN_SOCKET

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

    pubkey = KEYPAIR.get_public_key().exportKey()
    conn.sendall(pubkey)
    
    data = conn.recv(2048).decode('utf-8').rstrip()

    condata = KEYPAIR.extract_path_data(data)

    path = random.sample(ROUTERS, 3)
    if args.verbose: print('[Status] Selected path: {}, {}, {}'
                            .format(path[0]['addr'],path[1]['addr'],path[2]['addr']))

    rng = AESGenerator()
    rng.reseed(condata[0])
    aesmachine = AESProdigy(condata[0], rng.pseudo_random_data(16))
    
    # TODO: encrypt message
    ciphertext = aesmachine.encrypt(json.dumps(path))
    
    conn.sendall(ciphertext.encode('utf-8'))

    conn.close()


#   RUN MAIN
###############################################################################

if __name__ == '__main__':
    main()
