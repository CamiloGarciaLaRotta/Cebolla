import argparse             # for command-line argument parsing
def shut_down_directory_node():
    LISTEN_SOCKET.close()
    if args.verbose: print('Client Node DOWN')

import random               # for random path selection
import socket               # for TCP communication
import json                 # for encoding data sent through TCP
import threading            # for one thread per TCP connection


#   CLI ARGS
###############################################################################

parser = argparse.ArgumentParser()

parser.add_argument("destination", help="hostname to connect to")
parser.add_argument("port", help="port to listen on", type=int)
parser.add_argument("-v", "--verbose",
                    help="level of logging verbose", action="store_true")

args = parser.parse_args()

# validate args against conditions
if args.port < 5551 or args.port > 5557: # 7 group members, each get a port
    parser.error("port must satisfy: 5551 <= port <= 5557")


#   GLOBALS
#################################################################################

HOST = ''                            # empty string => all IPs of this machine
PORT = args.port                     # port for server to listen on, cli arg

DIRECTORY_NODE = 'cs-1'              # TODO hardcoded value or CL argument

LISTEN_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
LISTEN_SOCKET.bind((HOST, PORT))
LISTEN_SOCKET.listen(1)

encapsulate = lambda addr, key, next_node: {'addr': addr, 'key': key,
                                            'next': next_node} 


#   MAIN
#################################################################################

def main():
    if args.verbose: print('Client Node UP')

    try:
        run_client_node()
    except (socket.error, KeyboardInterrupt, Exception) as e:
        shut_down_directory_node()
        exit(str(e))


#   THE CLIENT NODE SERVER
###############################################################################

def run_client_node():
    if args.verbose: print('Obtaining path...')
    path = get_path()
    path.append({'addr' : args.destination, 'key': 'DST_KEY'})
    if args.verbose: print('Path: {}'.format(path))

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((path[0]['addr'],PORT))

    if args.verbose: print('Setting up VC...')
    if not setup_vc(path, s): raise Exception('Could not setup VC')

    t = threading.Thread(target=handle_response, args=(s,))
    t.start()

    if args.verbose: print('Virtual Circuit UP')

    while True:
        msg = input('Enter Message > ')
            
        # TODO encrypt

        s.sendall(msg.encode('utf-8'))


def get_path():
    dir_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dir_sock.connect((DIRECTORY_NODE,PORT))

    # TODO define what to send because directory doesn't even care
    dir_sock.sendall(b'TODO')

    data = dir_sock.recv(1024).decode('utf-8').rstrip()

    # TODO code directory-side get path
    path = json.loads(data)

    dir_sock.close()

    return path

def setup_vc(path, conn):
    # get ACK from first node
    conn.sendall(b'SYN')
    response = conn.recv(1024).decode('utf-8').rstrip()
    if response != 'ACK': return false
    if args.verbose: print('ACK recieved')

    # get ACK for remaining nodes and destination
    for i in range(1,4):
        setup_onion = encapsulate(path[i]['addr'], path[i]['key'], 'SYN')
        if args.verbose: print('setup_onion: {}'.format(setup_onion))
        
        # TODO encrypt data
        
        conn.sendall(json.dumps(setup_onion).encode('utf-8'))
        response = conn.recv(1024).decode('utf-8').rstrip()
        if response != 'ACK': return false
        if args.verbose: print('ACK recieved')


    return True


def handle_response(conn):
    while True:
        msg = conn.recv(2048).decode('utf-8').rstrip()

        # TODO decrypt

        print('\nReply from {}: {}'.format('ADD SRC',msg))


def shut_down_directory_node():
    LISTEN_SOCKET.close()
    if args.verbose: print('Client Node DOWN')


#   RUN MAIN
###############################################################################

if __name__ == '__main__':
    main()

