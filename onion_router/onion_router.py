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
        msg = conn_socket.recv(2048)
        mod_msg = msg.upper()
        conn_socket.send(mod_msg)
        conn_socket.close()
except KeyboardInterrupt:
    SOCKET_LISTEN.close()
