import socket
import colorama as c


ClientMultiSocket = socket.socket()
host = '127.0.0.1'
port = 2004
print('Waiting for connection response')
try:
    ClientMultiSocket.connect((host, port))
except socket.error as e:
    print(str(e))
res = ClientMultiSocket.recv(1024)
print(res.decode('utf-8'), end='')
name = input()
ClientMultiSocket.send(str.encode(name))
res = ClientMultiSocket.recv(1024)
print(res.decode('utf-8'), end='')

while True:
    # res = ClientMultiSocket.recv(10240)
    # print(res.decode('utf-8'), end='')
    Input = input()
    if Input == 'exit' or Input == 'Exit':
        print(c.Fore.GREEN+"Exiting..."+c.Fore.RESET)
        break
    ClientMultiSocket.send(str.encode(Input))
    res = ClientMultiSocket.recv(10240)
    print(res.decode('utf-8'), end='')
ClientMultiSocket.close()
