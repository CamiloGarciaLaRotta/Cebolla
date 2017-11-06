import socket
import argparse
import threading



#       CLI ARGS
#########################################################

parser = argparse.ArgumentParser() # instantiate cli args parser

# define cli positional args
parser.add_argument("port", help="port to listen on", type=int)
parser.add_argument("-v", "--verbose",
                            help="level of logging verbose", action="store_true")

args = parser.parse_args() # parse the args

# validate args against conditions
if args.port < 5551 or args.port > 5557: # 7 group members, each get a port
    parser.error("port must satisfy: 5551 <= port <= 5557")
if args.verbose: print('Verbosity ON\n')



#       RUN DUMMY SERVER
########################################################

PORT = args.port
HOST = ""
SOCKET_LISTEN = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCKET_LISTEN.bind((HOST,PORT))
SOCKET_LISTEN.listen(1)

def main():
    try:
        while 1:
            conn_socket, client_addr = SOCKET_LISTEN.accept()
            t = threading.Thread(target=reply, args=(conn_socket,))
            t.start()
    except KeyboardInterrupt:
        SOCKET_LISTEN.close()

def reply(conn_socket):
    try:
        while True:
            msg = conn_socket.recv(2048).decode('utf-8')
            print('Recieved: {}'.format(msg))
            if msg == 'SYN': 
                conn_socket.send(b'ACK')
            else: 
                mod_msg = msg.upper().encode('utf-8')
                conn_socket.send(mod_msg)
    except Exception as e:
        conn_socket.close()

if __name__ == "__main__":
    main()
