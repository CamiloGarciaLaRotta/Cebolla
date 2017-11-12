import argparse         # for command-line argument parsing
import json             # for encoding data sent through TCP
import threading        # for one thread per TCP connection
import socket           # for TCP communication

import sys, os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../stealth'))
import stealth          # for communication encryption


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
    # TODO need to establish symkey with back_conn, connect to forw_conn
    msg = back_conn.recv(2048).decode('utf-8').rstrip()
    if args.verbose: print('[Status] received SYN')

    # (TODO:decrypt data, initialize+respond with symkey. for now send 'ACK')
    back_conn.sendall("ACK".encode('utf-8'))

    # Wait for first-ever onion from back_conn
    if args.verbose: print('[Status] Waiting for first data onion...')
    msg = back_conn.recv(2048).decode('utf-8').rstrip()
    if args.verbose: print('[Status] First data onion: {}'.format(msg))

    # (TODO:decrypt)

    # parse onion to find out who to send to and what to send
    msg_dict = json.loads(msg)
    msg_addr = msg_dict["addr"]
    msg_next = msg_dict["next"]

    port = int(msg_dict["port"]) if "port" in msg_dict else DEFAULT_NEXT_PORT

    # connect to forw_conn and pass along data from back_conn
    forw_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if args.verbose: print('[Status] Connecting to next onion node...')
    forw_conn.connect((msg_addr, port))
    if args.verbose: print('[Status] Connected.')

    if args.verbose: print('[Status] Sending: {} To: {}'.format(msg_next, msg_addr))
    forw_conn.sendall(msg_next.encode('utf-8'))

    # now that two way communication is established, pass data back and forth forever

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

        # (TODO: decrypt)

        # pass it on
        forw_conn.sendall(msg.encode('utf-8'))


def backward_transfer(forw_conn, back_conn):
    while True:
        msg = forw_conn.recv(2048).decode('utf-8').rstrip()

        if args.verbose: print('[Data] From fwd_conn: {}'.format(msg))
        # (TODO: encrypt)

        # pass it on
        back_conn.sendall(msg.encode('utf-8'))


#       RUN MAIN
########################################################

if __name__ == "__main__":
    main()
