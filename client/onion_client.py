import argparse             # for command-line argument parsing
import random               # for random path selection
import socket               # for TCP communication
import json                 # for encoding data sent through TCP
import threading            # for one thread per TCP connection


#   CLI ARGS
###############################################################################

parser = argparse.ArgumentParser()

parser.add_argument("destination", help="hostname to connect to")
parser.add_argument("onion_port", 
                    help="port to communicate with onion network", type=int)
parser.add_argument("-d", "--destination_port", 
                    help="port in which destination will be listening. If not \
                    specified, port 80 is implied", type=int)
parser.add_argument("-v", "--verbose",
                    help="level of logging verbose", action="store_true")

args = parser.parse_args()

# validate args against conditions
if args.onion_port < 5551 or args.onion_port > 5557: # 7 group members, each get a port
    parser.error("port must satisfy: 5551 <= port <= 5557")


#   GLOBALS
#################################################################################

HOST = ''                            # empty string => all IPs of this machine
PORT = args.onion_port               # port for server to send data onto, cli arg
SENDER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

DIRECTORY_NODE = 'cs-1'              # TODO hardcoded value or CL argument


#   MAIN
#################################################################################

def main():
    if args.verbose: print('[Status] Client Node UP')

    try:
        run_client_node()
    except (socket.error, KeyboardInterrupt, Exception) as e:
        shut_down_client_node()
        if args.verbose: print('[Status] Client Node DOWN')
        exit(str(e))


#   THE CLIENT NODE SERVER
###############################################################################

def run_client_node():
    if args.verbose: print('[Status] Obtaining path...')
    path = get_path()
    path.append({'addr' : args.destination, 'key': 'DST_KEY'})
    if args.verbose: print('[Status] Path: {}'.format(path))

    SENDER_SOCKET.connect((path[0]['addr'],PORT))

    if args.verbose: print('[Status] Setting up VC...')
    if not setup_vc(path, SENDER_SOCKET): raise Exception('[Error] Could not setup VC')

    t = threading.Thread(target=handle_response, args=(SENDER_SOCKET,))
    t.setDaemon(True)
    t.start()

    # send first data onion 
    msg = raw_input('Enter Message > ')

    first_onion = encapsulate(path[3]['addr'], path[3]['key'], 
                                msg, args.destination_port)

    if args.verbose: print('[Data] First_onion: {}'.format(first_onion))
    
    # TODO encrypt data
    
    SENDER_SOCKET.sendall(json.dumps(first_onion).encode('utf-8'))
    
    if args.verbose: print('[Status] Virtual Circuit UP')

    while True:
        msg = raw_input('Enter Message > ')
            
        # TODO encrypt

        SENDER_SOCKET.sendall(msg.encode('utf-8'))


def shut_down_client_node():
    SENDER_SOCKET.close()


def get_path():
    dir_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dir_sock.connect((DIRECTORY_NODE,PORT))

    # TODO define what to send because directory doesn't even care
    dir_sock.sendall(socket.gethostname().encode('utf-8'))

    data = dir_sock.recv(1024).decode('utf-8').rstrip()

    path = json.loads(data)

    dir_sock.close()

    return path


def setup_vc(path, conn):
    # get ACK from first node
    conn.sendall(b'SYN')
    response = conn.recv(1024).decode('utf-8').rstrip()
    if response != 'ACK': return false
    if args.verbose: print('[Status] ACK recieved')

    # get ACK for remaining internal nodes
    for i in range(1,3):
        setup_onion = encapsulate(path[i]['addr'], path[i]['key'], 
                                'SYN', args.onion_port)
        if args.verbose: print('[Status] setup_onion: {}'.format(setup_onion))
        
        # TODO encrypt data
        
        conn.sendall(json.dumps(setup_onion).encode('utf-8'))
        response = conn.recv(1024).decode('utf-8').rstrip()
        if response != 'ACK': return false
        if args.verbose: print('[Status] ACK recieved')
    
    return True


def encapsulate(addr, key, next_node, port=None):
    onion = {'addr': addr, 'key': key, 'next': next_node} 
    if port: onion['port'] = port

    return onion


def handle_response(conn):
    while True:
        msg = conn.recv(2048).decode('utf-8').rstrip()

        # TODO decrypt

        print('\nReply from {}: {}'.format('ADD SRC',msg))


#   RUN MAIN
###############################################################################

if __name__ == '__main__':
    main()

