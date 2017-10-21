import sys
import socket
from _thread import *

def threaded_client(conn):
    conn.send(str.encode('\nServer listening\n'))
    while True:
        conn.send(str.encode('\nenter input: '))
        data = conn.recv(1024)
        reply = 'Server Response: ' + data.decode('utf-8') 
        if not data:
            break
        conn.sendall(str.encode(reply))

    conn.close()
host = ''
server_port = 5555 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def main():
    try:
        server_socket.bind((host,server_port))
    except socket.error as e:
        print(str(e))
        sys.exit(0)

    server_socket.listen(5)
    print('GTG')


    try:
        while True:
            conn, addr = server_socket.accept()
            print('Connected to: ' + addr[0] + ':' + str(addr[1]))
            start_new_thread(threaded_client,(conn,))
    except KeyboardInterrupt as e: 
        print(str(e))
        server_socket.close()
        print('Server Socket ' + str(server_port) + ' closed\n')

if __name__ == '__main__':
    main()
