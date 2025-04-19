import socket
import select

HOST_IP= socket.gethostbyname(socket.gethostname())
HOST_PORT= 1234
BYTESIZE=10



server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print('Server Is Running')
server_socket.bind((HOST_IP, HOST_PORT))
server_socket.listen(10)
print('Waiting for connections.....')


server_socket_list=[server_socket]
clients={}




def receive_message(client_socket):
    try:
        msg_length_bytes=client_socket.recv(BYTESIZE)
        if not len(msg_length_bytes):
            return False
        message_length= int(msg_length_bytes.decode("utf-8").strip())
        message= client_socket.recv(message_length)
        return {'header': msg_length_bytes, 'data': message}
    except:
        return False

while True:
    read_sockets, _, exception_sockets= select.select(server_socket_list, [], server_socket_list)
    for pending_client in read_sockets:
        if pending_client == server_socket:
            client_socket, client_address= server_socket.accept()
            username_data= receive_message(client_socket)
            if username_data is False:
                continue
            server_socket_list.append(client_socket)
            clients[client_socket]= username_data
            print(f"{username_data['data'].decode('utf-8')} has joined the live chat....")

        else:
            message = receive_message(pending_client)
            if message is False:
                print(f"{clients[pending_client]['data'].decode('utf-8')} left the live chat")
                server_socket_list.remove(pending_client)
                del clients[pending_client]
                continue

            user = clients[pending_client]
            print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

            for client_socket in clients:
                if client_socket != pending_client:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

            if message['data'].decode('utf-8') == "quit":
                print(f"{user['data'].decode('utf-8')} left the live chat")
                server_socket_list.remove(pending_client)
                del clients[pending_client]
                break