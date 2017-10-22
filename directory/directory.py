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
NODES = []                  # active nodes in networks
directory_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# parse config file, return dict-like ConfigParser object
def parse_config():
    config = configparser.ConfigParser()
    config.read('network.conf')
    return config

# initializes global parameters based on an input config dict
def init_params(config):
    global HOST, PORT, MAX_CN, CNS

    network_config = config['NETWORK']
    HOST = network_config['HOST']
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else int(network_config['PORT'])
    MAX_CN = int(network_config['MAX_CN'])
    CNS.extend(range(MAX_CN))
    print("HOST: {0}, PORT: {1}, MAX_CN: {2}".format(HOST, PORT, MAX_CN))

    random.shuffle(CNS)


# fills the NODES lsit with the machines in the LAN that are listening on PORT
def query_network():
    print('Querying the network ...')

    for i in range(2,51):
        hostname = 'lab2-{}.cs.mcgill.ca'.format(i)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        timeout = s.connect_ex((hostname,PORT))
        s.close()

        # This functionality was already tested,
        # commented out to avoid having to setup TCP clients  while testing
        #        if not timeout and hostname not in NODES:
        #            NODES.append(hostname)
        NODES.append(hostname)

    random.shuffle(NODES)

    print('There are {} node(s) in the network'.format(len(NODES)))


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


# thread function wich establishes TCP connection with a client
# recieves a destination node and returns a random path
# in case of invalid input or no available CNs an empty object is returned
def threaded_client(conn):
    data = conn.recv(1024)

    path = get_path(data.decode('utf-8').rstrip())

    conn.sendall(str.encode(path))

    conn.close()


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


def main():
    config = parse_config()
    init_params(config)

    query_network()
    try:
        start_server()
    except (socket.error, KeyboardInterrupt) as e:
        stop_server()
        sys.exit(str(e))


if __name__ == '__main__':
    main()
