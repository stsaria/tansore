import socket, sys

PORT = 52268

def create_client(ip,port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect( (ip,port) )
    return client

if __name__ == '__main__':
    con = create_client(sys.argv[1], PORT)
    print("Success connect to Server")
    con.send("0000000000".encode('utf-8'))
    while True:
        data = con.recv(1024).decode('utf-8')
        if not data:
            continue
        print(data)
        con.close()
        break
    print("Client finish")