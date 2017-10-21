import sys                  # for CL argument parsing
import json                 # for encoding data sent through TCP
import random               # for shuffling node indices during path selection
import socket               # for TCP communication
from _thread import *       # for threaded client TCP connections

###############################################################################
#                                                                             #
#   TODO                                                                      #
#    - handle invalid input hostname from TCP client                          #
#    - if CL argument passing is accepted as feature implement flag system    #
#    - implement encryption key mgmt                                          #
#    - implement Circuit Number (CN) mgmt                                     #
#                                                                             #
###############################################################################


###############################################################################
#   GLOBALS                                                                   #
###############################################################################
HOST = ''
PORT = 5555 
NODES = []
directory_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

# returns a unique circuit number
def get_CN():
    # TODO implement Circuit Number (CN) mgmt 
    return 69

# makes the input CN available for future reuse
def pop_CN(cn):
    # TODO implement Circuit Number (CN) mgmt
    pass

# return the string of a JSON encoded object
# which contains the hostname, keys and CN for a random path
def get_path(dst):
    path = {}
    
    if dst in NODES:
        path_nodes = [NODES[i] for i in random.sample(range(len(NODES)),3)]
        
        for i in range(3):
            key = 'n{}'.format(str(i))
            path[key] = {'hostname': path_nodes[i], 'key': get_key(path_nodes[i])}

        path['CN'] = get_CN()

    return json.dumps(path)

# thread function wich establishes TCP connection with a client
# recieves a destination node and returns a random path
def threaded_client(conn):
    conn.send(str.encode('\nConnected to Directory Node\n'))
    
    # TODO in final version no need to send prompt, no interactive comm needed
    conn.send(str.encode('Enter hostname of destination node: '))
    data = conn.recv(1024)
        
    if data:
        path = get_path(data.decode('utf-8').rstrip())
        if path:
            conn.sendall(str.encode(path))
        else:
            # TODO handle invalid input hostname from TCP client
            conn.sendall(str.encode('Illegal Input'))

    conn.close()

# configures threaded TCP server on PORT
def start_server():
    directory_socket.bind((HOST,PORT))
    directory_socket.listen(len(NODES))

    print('Directory Node UP')

    while True:
        conn, addr = directory_socket.accept()
        print('Connected to: {}:{}'.format(addr[0],str(addr[1])))
        start_new_thread(threaded_client,(conn,))

# closes the listening TCP server on PORT
def stop_server():
    directory_socket.close()
    print('Directiry Node DOWN')

# main entry point
def main():
    # TODO if CL argument passing is accepted as feature implement flag system
    if len(sys.argv) > 1:
        global PORT 
        PORT = int(sys.argv[1])

    query_network()
    try:
        start_server()
    except (socket.error, KeyboardInterrupt) as e:
        print(str(e))
        stop_server()
        sys.exit(0)

if __name__ == '__main__':
    main()

