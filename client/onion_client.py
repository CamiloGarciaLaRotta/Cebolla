import argparse             # for command-line argument parsing
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
if args.verbose: print('Verbosity ON')


#   GLOBALS
#################################################################################

HOST = ''                            # empty string => all IPs of this machine
PORT = args.port                     # port for server to listen on, cli arg

DIRECTORY_NODE = 'cs-1'              # TODO hardcoded value or CL argument

LISTEN_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
LISTEN_SOCKET.bind((HOST, PORT))
LISTEN_SOCKET.listen(1)

build_onion = lambda n2: lambda n3: lambda dst, data: {'addr': n2, 'data': 
        {'addr': n3, 'data': {'addr': dst, 'data': data}}}


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
        data_onion = build_onion( path[1]['addr'])(path[2]['addr'])(args.destination, msg)
        
        if args.verbose: print('data_onion: {}'.format(data_onion))
            
        # TODO encrypt

        s.sendall(json.dumps(data_onion).encode('utf-8'))


def shut_down_directory_node():
    LISTEN_SOCKET.close()
    if args.verbose: print('Client Node DOWN')

def get_path():
    dir_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dir_sock.connect((DIRECTORY_NODE,PORT))

    # TODO define what to send because directory doesn't even care
    dir_sock.sendall(b'dunno what to put here yet')

    data = dir_sock.recv(1024).decode('utf-8').rstrip()

    # TODO code directory-side get path
    path = json.loads(data)

    dir_sock.close()

    return path

def setup_vc(path, conn):
    setup_onion = build_onion(
            path[1]['addr'])(path[2]['addr'])(args.destination, 'dummy data')
    data = json.dumps(setup_onion).encode('utf-8')

    if args.verbose: print('setup_onion: {}'.format(setup_onion))

    # TODO encrypt data

    # the setup onion sent twice will establish the VC
    # along the 3 internal nodes
    for _ in range(3):
        conn.sendall(data)
        response = conn.recv(1024).decode('utf-8').rstrip()

        # TODO add timeout or some handling mechanism in case node is not
        # respondant
        if response != 'ACK': return False
        
        if args.verbose: print('ACK recieved')

    return True


def handle_response(conn):
    while True:
        msg = conn.recv(2048).decode('utf-8').rstrip()

        # TODO decrypt

        print('')
        print('Reply from {}: {}'.format('ADD SRC',msg))

#   RUN MAIN
###############################################################################

if __name__ == '__main__':
    main()

