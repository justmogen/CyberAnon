import argparse
import socket
import socketserver
import nmap
import json

# Set up the Nmap scanner
nm = nmap.PortScanner()

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print("Client connected from {}".format(self.client_address))

        # Receive data from the client
        data = self.request.recv(4096)
        if not data:
            print("No data received from client")
            return

        # Decode the data as JSON
        try:
            request = json.loads(data.decode())
        except json.JSONDecodeError as e:
            print("Error decoding JSON data: {}".format(str(e)))
            return

        # Check if the request is valid
        if "target" not in request:
            print("Invalid request: missing 'target' field")
            return

        # Scan for open ports on the target
        target = request["target"]
        try:
            nm.scan(target, arguments="-T4 -p1-65535 -s" + args.protocol_version)
        except nmap.PortScannerError as e:
            print("Error scanning target {}: {}".format(target, str(e)))
            return

        # Get the scan results and construct the response
        open_ports = []
        for protocol in nm[target].all_protocols():
            ports = nm[target][protocol].keys()
            for port in ports:
                if nm[target][protocol][port]["state"] == "open":
                    open_ports.append(int(port))
        response = {"status": "OK", "target": target, "open_ports": open_ports}

        # Encode the response as JSON and send it back to the client
        response_data = json.dumps(response).encode()
        self.request.sendall(response_data)

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="TCP port scanner server")
    parser.add_argument("ip_address", type=str, help="IP address to listen on")
    parser.add_argument("port_number", type=int, help="Port number to listen on")
    parser.add_argument("protocol_version", type=str, help="Protocol version (e.g. 4, 6)")

    # Parse command line arguments
    args = parser.parse_args()

    # Create a threaded TCP server and start listening for incoming connections
    server = socketserver.ThreadingTCPServer((args.ip_address, args.port_number), TCPHandler)
    print("Server listening on {}:{}".format(args.ip_address, args.port_number))
    server.serve_forever()

