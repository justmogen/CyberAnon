import socket
import struct
import json
import argparse

# Define the message format as a list of field names
message_format = ['id', 'name', 'value']

def connect(ip_address, port_number):
    # Create a socket object and connect to the server's IP address and port number
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip_address, port_number))
    return sock

def negotiate_protocol(sock, protocol_version):
    # Send the protocol version to the server
    message = {"protocol": protocol_version}
    message_json = json.dumps(message).encode()
    sock.sendall(struct.pack('>I', len(message_json)) + message_json)

    # Wait for a response from the server indicating whether the protocol version is supported
    response_length = struct.unpack('>I', sock.recv(4))[0]
    response_json = sock.recv(response_length).decode()
    response = json.loads(response_json)
    if response.get("protocol") != protocol_version or not response.get("supported"):
        print("Server does not support the same protocol version. Closing connection.")
        sock.close()
        exit()

def send_message(sock, message_data):
    # Pack a message into a JSON object using the message format
    message_dict = {field_name: message_data[i] for i, field_name in enumerate(message_format)}
    message_json = json.dumps(message_dict).encode()

    # Send the message to the server
    sock.sendall(struct.pack('>I', len(message_json)) + message_json)

def receive_message(sock):
    # Receive a message from the server
    response_length = struct.unpack('>I', sock.recv(4))[0]
    response_json = sock.recv(response_length).decode()

    # Decode the message using the agreed message format
    response_dict = json.loads(response_json)
    response_data = [response_dict[field_name] for field_name in message_format]

    return response_data

def close_connection(sock):
    # Close the connection
    sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TCP client for exchanging messages with a server.')
    parser.add_argument('ip_address', type=str, help='IP address of the server')
    parser.add_argument('port_number', type=int, help='Port number of the server')
    parser.add_argument('protocol_version', type=str, help='Protocol version to use')
    args = parser.parse_args()

    try:
        sock = connect(args.ip_address, args.port_number)
        negotiate_protocol(sock, args.protocol_version)

        # Send and receive messages
        message_data = (1, "hello", 3.14)
        send_message(sock, message_data)

        response_data = receive_message(sock)
        print(response_data)

    except socket.error as e:
        print(f"Socket error occurred: {e}")

    finally:
        close_connection(sock)

