import threading
import json
import socket
import argparse



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


#       GLOBALS
########################################################

PORT = args.port
HOST = ""
LISTENER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
LISTENER_SOCKET.bind((HOST,PORT))
LISTENER_SOCKET.listen(50)



#       MAIN
########################################################

def main():
    try:
        while 1:
            # accept connection from previous ('backward') node in path
            back_conn, client_addr = LISTENER_SOCKET.accept()
            print('Connected to: {}:{}'.format(client_addr[0], str(client_addr[1])))

            # new thread for self-setup as onion_router
            t = threading.Thread(target=two_way_setup, args=(back_conn,))
            t.start()

    except (socket.error, KeyboardInterrupt):
        LISTENER_SOCKET.close()



#       SETUP TWO TCP CONNECTIONS
########################################################

# need to establish symkey with back_conn, connect to forw_conn
def two_way_setup(back_conn):
    msg = back_conn.recv(2048).decode('utf-8').rstrip()
    if args.verbose: print('[Onion] received SYN')

    # (TODO:decrypt data, initialize+respond with symkey. for now send 'ACK')
    back_conn.sendall("ACK".encode('utf-8'))

    # Wait for first-ever onion from back_conn
    if args.verbose: print('[Onion] Waiting for setup onion...')
    msg = back_conn.recv(2048).decode('utf-8').rstrip()
    if args.verbose: print('[Onion] Got setup onion.')

    # (TODO:decrypt)

    # parse onion to find out who to send to and what to send
    if args.verbose: print('First data onion: {}'.format(msg))
    msg_dict = json.loads(msg)
    msg_addr = msg_dict["addr"]
    msg_next = msg_dict["next"] 

    # connect to forw_conn and pass along data from back_conn
    forw_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if args.verbose: print('[Onion] Connecting to next onion node...')
    forw_conn.connect((msg_addr, PORT))
    if args.verbose: print('[Onion] Connected.')
    
    if args.verbose: print('Sending: {} \nTo: {}'.format(msg_next, msg_addr))
    forw_conn.sendall(msg_next.encode('utf-8'))

    # now that two way communication is established, pass data back and forth forever

    t = threading.Thread(target=backward_transfer, args=(forw_conn, back_conn))
    t.start()
    forward_transfer(back_conn, forw_conn)



#       PASS DATA FORWARD AND BACKWARD FOREVER
########################################################

def forward_transfer(back_conn, forw_conn):
    while True:
        msg = back_conn.recv(2048).decode('utf-8').rstrip()
        
        if args.verbose: print('From back_conn: {}'.format(msg))

        # (TODO: decrypt)

        # pass it on
        forw_conn.sendall(msg.encode('utf-8'))

def backward_transfer(forw_conn, back_conn):
    while True:
        msg = forw_conn.recv(2048).decode('utf-8').rstrip()

        if args.verbose: print('From fwd_conn: {}'.format(msg))
        # (TODO: encrypt)

        # pass it on
        back_conn.sendall(msg.encode('utf-8'))



#       RUN MAIN
########################################################

if __name__ == "__main__":
    main()
