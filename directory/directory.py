import sys                  # for CL argument parsing
import json                 # for encoding data sent through TCP
import random               # for shuffling node indices during path selection
import socket               # for TCP communication
import configparser         # for parsing the config file
from _thread import *       # for threaded client TCP connections

###############################################################################
#                                                                             #
#   TODO                                                                      #
#    - implement encryption key mgmt                                          #
#    - implement TLS                                                          #
#                                                                             #
###############################################################################


###############################################################################
#   GLOBALS                                                                   #
###############################################################################
HOST = None
PORT = None

MAX_CN = None               # maximum number of concurrent Circuit Numbers
CNS = []                    # available Circuit Numbers

NODES = []                  # active nodes in onion network
MAX_NODES = None            # max number of nodes in onion network
NODE_FORMAT = None          # python format string of nodes' domain names

directory_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


###############################################################################
#   MAIN                                                                      #
###############################################################################
def main():
    config = parse_config()
    init_params(config)

    query_network()
    try:
        start_server()
    except (socket.error, KeyboardInterrupt) as e:
        stop_server()
        sys.exit(str(e))


###############################################################################
#   INITIALIZATION HELPERS                                                    #
###############################################################################

# parse config file, return dict-like ConfigParser object
def parse_config():
    config = configparser.ConfigParser()
    config.read('network.conf')
    return config

# init global params from ConfigParser object
def init_params(config):
    nconfig = config['NETWORK']
    global HOST, PORT, MAX_CN, CNS, MAX_NODES, NODE_FORMAT, NODES

    HOST = nconfig['host']
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else int(nconfig['port'])

    MAX_CN = int(nconfig['max_cn'])
    CNS.extend(range(MAX_CN))
    random.shuffle(CNS)

    MAX_NODES = int(nconfig['max_nodes'])
    NODE_FORMAT = nconfig['node_format']
    NODES = [NODE_FORMAT.format(i) for i in range(2,MAX_NODES + 1)]


# fills the NODES lsit with the machines in the LAN that are listening on PORT
def query_network():
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

# return the string of a JSON encoded object
# which contains the hostname, keys and CN for a random path
# in case of invalid input or no available CNs an empty object is returned
def get_path(dst):
    path = {}

    if dst in NODES:
        path_nodes = [NODES[i] for i in random.sample(range(len(NODES)),3)]

        for i in range(3):
            key = 'n{}'.format(str(i))
            path[key] = {'hostname': path_nodes[i], 'key': get_key(path_nodes[i])}

        try:
            path['CN'] = pop_CN()
        except IndexError as e:
            print(str(e))
            path = {}

    return json.dumps(path)

# returns the encryption key associated with an input hostname
def get_key(hostname):
    # TODO implement encryption key mgmt
    return "TODO_KEY_MGMT"

# returns a unique CN and removes it from available CNs
def pop_CN():
    if CNS:
        cn = random.choice(CNS)
        idx = CNS.index(cn)

        return CNS.pop(idx)
    else:
        raise IndexError('No more available CNs')

# makes the input CN available for future reuse
def push_CN(cn):
    CNS.append(cn)



###############################################################################
#   RUN MAIN                                                                  #
###############################################################################
if __name__ == '__main__':
    main()