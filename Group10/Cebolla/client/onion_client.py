import argparse             # for command-line argument parsing
import json                 # for encoding data sent through TCP
import random               # for random path selection
import socket               # for TCP communication
import threading            # for one thread per TCP connection
import time                 # for sleep between message prompts

from Crypto.PublicKey import RSA

import sys, os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../stealth'))
import onion
import stealth
from onion import OriginatorSecurityEnforcer
from stealth import RSAVirtuoso
from stealth import AESProdigy

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

# TODO disabled for testing purposes
# validate args against conditions
#if args.onion_port < 5551 or args.onion_port > 5557: # 7 group members, each get a port
#    parser.error("port must satisfy: 5551 <= port <= 5557")


#   GLOBALS
#################################################################################

HOST = ''                            
PORT = args.onion_port              
SENDER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

DIRECTORY_NODE = 'cs-1'            
DEFAULT_PORT = 80

ORIGINATOR_CIPHER = OriginatorSecurityEnforcer()


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
    if args.destination_port:
        port = args.destination_port
    else: port = DEFAULT_PORT
    path.append({'addr' : args.destination, 'key': 'DST_KEY', 'port': port}) 
    if args.verbose: print('[Status] Path: {}'.format(path))

    SENDER_SOCKET.connect((path[0]['addr'],PORT))

    if args.verbose: print('[Status] Setting up VC...')
    if not setup_vc(path, SENDER_SOCKET): raise Exception('[Error] Could not setup VC')

    t = threading.Thread(target=handle_response, args=(SENDER_SOCKET,))
    t.setDaemon(True)
    t.start()

    if args.verbose: print('[Status] Virtual Circuit UP')

    while True:
        msg = raw_input('\nEnter Message > ')
        onion = ORIGINATOR_CIPHER.create_onion(4, msg)
        SENDER_SOCKET.sendall(onion.encode('utf-8'))
        #Wait for a short period for a response. 
        #Looks nicer to see the response before the next prompt.
        time.sleep(0.3) 

def shut_down_client_node():
    SENDER_SOCKET.close()


def get_path():
    dir_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dir_sock.connect((DIRECTORY_NODE,PORT))

    dir_sock.sendall(socket.gethostname().encode('utf-8'))

    pubkey = dir_sock.recv(6144).decode('utf-8').rstrip()
    # Create RSAVirtuoso instance from the exported key sent from the directory node
    ORIGINATOR_CIPHER.directoryPubKey = RSAVirtuoso(RSA.importKey(pubkey))
    msg = ORIGINATOR_CIPHER.create_symkey_msg(0, '', '') #Depth is 0 since we're talking to the directory
    if args.verbose:
        print('Sending message: ' + msg)
    dir_sock.sendall(msg.encode('utf-8'))

    data = dir_sock.recv(6144).decode('utf-8').rstrip()

    path = json.loads(ORIGINATOR_CIPHER.decipher_response(0,data))
    if args.verbose:
        print('Received path data: ' + str(path))

    ORIGINATOR_CIPHER.set_path(path)
    ORIGINATOR_CIPHER.set_pubkeys(list(map(lambda x: RSAVirtuoso(RSA.importKey(x["key"])), path)))

    dir_sock.close()

    return path

# send setup onions to all the nodes in path through the conn socket
def setup_vc(path, conn):
    #i represents depth, the amount of nodes deep into the path the dest is
    for i in range(1,4):
        if i != 3: nextaddr = ORIGINATOR_CIPHER.path[i][0]
        else: nextaddr = args.destination
        symkey_msg = ORIGINATOR_CIPHER.create_symkey_msg(i, nextaddr, path[i]["port"])
        setup_onion = ORIGINATOR_CIPHER.create_onion(i, symkey_msg)
        if args.verbose: print('[Status] setup_onion: {}'.format(setup_onion))
        
        conn.sendall(json.dumps(setup_onion).encode('utf-8'))
        if args.verbose: print('[Status] received encrypted response..')
        response = conn.recv(1024).decode('utf-8').rstrip()
        if i > 1 : response = ORIGINATOR_CIPHER.decipher_response(i-1, response)
        if response != 'ACK': return false
        if args.verbose: print('[Status] ACK received')
    
    return True

def handle_response(conn):
    while True:
        msg = conn.recv(2048).decode('utf-8').rstrip()

        msg = ORIGINATOR_CIPHER.decipher_response(3, msg) #Depth is 3 because all 3 onion nodes encrypted
        print('Reply from {}: {}'.format(args.destination, msg))


#   RUN MAIN
###############################################################################

if __name__ == '__main__':
    main()

