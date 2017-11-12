import argparse         # for command-line argument parsing
import json             # for encoding data sent through TCP
import threading        # for one thread per TCP connection
import socket           # for TCP communication

import sys, os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../stealth'))
import stealth          # for communication encryption
import onion            # for handling layer peeling and onion-level security
from onion import OnionNodeSecurityEnforcer


#       CLI ARGS
#########################################################

# define cli positional args
parser = argparse.ArgumentParser() # instantiate cli args parser

parser.add_argument("port", help="port to listen on", type=int)
parser.add_argument("dir_port", help="port to listen for directory", type=int)
parser.add_argument("-v", "--verbose",
                    help="level of logging verbose", action="store_true")

args = parser.parse_args() # parse the args

# TODO disabled to facilitate testing
# validate args against conditions
#if args.port < 5551 or args.port > 5557: # 7 group members, each get a port
#    parser.error("port must satisfy: 5551 <= port <= 5557")


#       GLOBALS
########################################################

HOST = ""
PORT = args.port
LISTENER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
LISTENER_SOCKET.bind((HOST,PORT))
LISTENER_SOCKET.listen(50)

DIR_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
DIR_SOCKET.bind((HOST,args.dir_port))
DIR_SOCKET.listen(1)

KEYPAIR = stealth.RSAVirtuoso()     # node's encryption key pairs
ONION_CIPHER = OnionNodeSecurityEnforcer()

DEFAULT_NEXT_PORT = 80              # default port of next hop in virtual circuit

#       MAIN
########################################################

def main():
    if args.verbose: print('[Status] Router Node UP')

    dir_t = threading.Thread(target=dir_setup)
    dir_t.setDaemon(True)
    dir_t.start()

    try:
        while 1:
            # accept connection from previous ('backward') node in path
            back_conn, client_addr = LISTENER_SOCKET.accept()
            print('[Status] Connected to: {}:{}'
                    .format(client_addr[0], str(client_addr[1])))

            # new thread for self-setup as onion_router
            t = threading.Thread(target=two_way_setup, args=(back_conn,))
            t.setDaemon(True)
            t.start()

    except (socket.error, KeyboardInterrupt):
        if args.verbose: print('[Error] Router Node DOWN')
        LISTENER_SOCKET.close()
        DIR_SOCKET.close()


#       SETUP TWO TCP CONNECTIONS
########################################################

# listen on directory dedicated port and handle its key requests
def dir_setup():
    while True:
        conn , addr = DIR_SOCKET.accept()
        req = conn.recv(2048).decode('utf-8')

        # if request is empty, the directory was only pinging
        if req == "get_key":
            if args.verbose: print('[Status] Directory requested key')
            resp = KEYPAIR.get_public_key().exportKey()
            conn.sendall(resp.encode('utf-8'))
        else:
            if args.verbose: print('[Status] Ping from Directory')

        conn.close()


# establish virtual circuit with 2 connection threads: backwards node and forward node
def two_way_setup(back_conn):
    # Wait for first contact
    # First message will contain (symkey, addr of next node, port of next node)
    msg = back_conn.recv(2048).decode('utf-8').rstrip()
    if args.verbose: print('[Status] received estab: ' + msg)
    pathdata = KEYPAIR.extract_path_data(msg) # Gets the (symkey, addr, port) tuple
    ONION_CIPHER.set_key(pathdata[0])
    back_conn.sendall("ACK".encode('utf-8'))

    # Wait for next message to connect with the next node
    # Wait is necessary because we still don't have the (symkey, addr, port) to give to the next node
    msg = back_conn.recv(2048).decode('utf-8').rstrip()
    if args.verbose: print('[Status] received next: ' + msg)
    msg = ONION_CIPHER.peel_layer(msg) #Peel off layer of encryption. Under this is the pubkey encrypted tuple

    # Now that we have the pubkey-encrypted (symkey, addr, tuple), we can encrypt to forw_conn and send it
    forw_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if args.verbose: print('[Status] Trying to connect to {} on port {}...'.format(pathdata[1], pathdata[2]))
    forw_conn.connect((pathdata[1], pathdata[2]))
    if args.verbose: print('[Status] Connected.')
    if args.verbose: print('[Status] Sending: {} To: {}'.format(msg, pathdata[1]))
    forw_conn.sendall(msg.encode('utf-8'))
    
    # Now that two way communication is established, pass data back and forth forever
    t = threading.Thread(target=backward_transfer, args=(forw_conn, back_conn))
    t.setDaemon(True)
    t.start()
    forward_transfer(back_conn, forw_conn)


#       PASS DATA FORWARD AND BACKWARD FOREVER
########################################################

def forward_transfer(back_conn, forw_conn):
    while True:
        msg = back_conn.recv(2048).decode('utf-8').rstrip()

        if args.verbose: print('[Data] From back_conn: {}'.format(msg))

        # pass it on
        forw_conn.sendall(ONION_CIPHER.peel_layer(msg).encode('utf-8'))


def backward_transfer(forw_conn, back_conn):
    while True:
        msg = forw_conn.recv(2048).decode('utf-8').rstrip()

        if args.verbose: print('[Data] From fwd_conn: {}'.format(msg))
        msg = ONION_CIPHER.add_layer(msg)

        # pass it on
        back_conn.sendall(msg.encode('utf-8'))


#       RUN MAIN
########################################################

if __name__ == "__main__":
    main()
