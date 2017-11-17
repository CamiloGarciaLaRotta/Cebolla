import argparse             # for command-line argument parsing
import socket               # for TCP communication
import threading            # for one thread per TCP connection


#       CLI ARGS
#########################################################

# define cli positional args
parser = argparse.ArgumentParser() # instantiate cli args parser

parser.add_argument("port", help="port to listen on", type=int)
parser.add_argument("-v", "--verbose",
                    help="level of logging verbose", action="store_true")

args = parser.parse_args() # parse the args


#       GLOBALS
########################################################

SOCKET_LISTEN = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCKET_LISTEN.bind(("",args.port))
SOCKET_LISTEN.listen(1)


#       MAIN
########################################################

def main():
    if args.verbose: print('[Status] Destination Node UP')
    try:
        while 1:
            conn_socket, client_addr = SOCKET_LISTEN.accept()
            t = threading.Thread(target=reply, args=(conn_socket, client_addr))
            t.setDaemon(True)
            t.start()
    except KeyboardInterrupt:
        if args.verbose: print('[Error] Destination Node DOWN')
        SOCKET_LISTEN.close()


#       HANDLE CONNECTIONS
########################################################

def reply(conn_socket, addr):
    try:
        while True:
            msg = conn_socket.recv(2048).decode('utf-8')
            print('[Status] Recieved: {} from: {}:{}'.format(msg, addr[0], str(addr[1])))
            mod_msg = msg.upper().encode('utf-8')
            conn_socket.send(mod_msg)
    except Exception as e:
        if args.verbose:
            print('[Error] Lost communication with {}:{}'.format(addr[0], str(addr[1])))
        conn_socket.close()
        SOCKET_LISTEN.close()


#       RUN MAIN
########################################################

if __name__ == "__main__":
    main()
