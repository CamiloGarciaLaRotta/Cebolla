import json
import threading
from socket import *
import argparse

#       CLI ARGS
#########################################################

parser = argparse.ArgumentParser() # instantiate cli args parser

# define cli positional args
parser.add_argument("port", help="port to listen on", type=int)

args = parser.parse_args() # parse the args

# validate args against conditions
if args.port < 5551 or args.port > 5557: # 7 group members, each get a port
    parser.error("port must satisfy: 5551 <= port <= 5557")



#       RUN DUMMY SERVER
########################################################

PORT = args.port
HOST = ""
SOCKET_LISTEN = socket(AF_INET, SOCK_STREAM)
SOCKET_LISTEN.bind((HOST,PORT))
SOCKET_LISTEN.listen(1)

try:
    while 1:
        conn_socket, client_addr = SOCKET_LISTEN.accept()
        print('Connected to: {}:{}'.format(client_addr[0], str(client_addr[1])))

        # new thread for backward data passing
        t = theading.Thread(target=two_way_setup, args=(conn_socket,))
        t.start()

except KeyboardInterrupt:
    SOCKET_LISTEN.close()

def two_way_setup(back_conn):
    msg = back_conn.recv(2048).decode('utf-8').rstrip()

    # (TODO:decrypt data, initialize symkey, send ACK)

    # Wait for data onion
    msg = back_conn.recv(2048).decode('utf-8')
    # (TODO:decrypt)
    msg_dict = json.loads(msg)
    msg_data = msg_dict["data"]
    msg_addr = msg_dict["addr"]

    forw_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    forw_conn.connect((msg_addr, PORT))
    forw_conn.send(msg_data)
        	
    t = threading.Thread(target=backward_transfer, args=(forw_conn, back_conn))
    t.start()
    forward_transfer(forw_conn, back_conn)

def backward_transfer(forw_conn, back_conn):
    while True:
        msg = forw_conn.recv(2048).decode('utf-8').rstrip()

        # (TODO: encrypt)
        # 'msg = decrypt(msg)'

        # send it on down the line!
        back_conn.send(msg)

def forward_transfer(back_conn, forw_conn):
    while True:
        msg = back_conn.recv(2048).decode('utf-8').rstrip()

        # (TODO:decrypt)

        # json parse
        msg_dict = json.loads(msg)
        msg_data = msg_dict["data"]
        msg_addr = msg_dict["addr"]

        # send it on down the line!
        forw_conn.send(msg_data)

#<socket.socket fd=3, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('132.206.52.24', 36818), raddr=('132.206.52.27', 22)>

    # continue doing your shit
    # while (True):
    #   pass
