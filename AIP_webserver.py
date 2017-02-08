# Use a socket to accept connections from clients
# Accept connection and receive data
# Check if they belong to the correct subnet, then process the data sent.
# If they are requesting for attendance.html, read attendance.html from a file and send it on this connection.
# Read asynchronously from a file with unity IDs of all the students of this class, and see if the entered ID is valid.
# If they are submitting, extract the values they are sending from the POST req, put the values into a text file.


import socket
import os
import sys

http_header_success = "HTTP/1.0 200 OK\nContent-Type: text/html\nKeep - Alive: timeout = 5, " \
                  "max = 100\nConnection: Keep-Alive\n\n"
http_header_file_not_found = "HTTP/1.0 404 Not Found\nContent-Type: text/html\nKeep - Alive: timeout = 5, " \
                  "max = 100\nConnection: Keep-Alive\n\n"


class Server:
    def __init__(self, port):
        self.port = port
        self.hostname = ""
        self.sock = None

    def create_socket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as e:
            print e.message
            print "Could not create a socket! Exiting"
            sys.exit(1)
        if self.sock is not None:
            try:
                self.sock.bind((self.hostname, self.port))
            except Exception as e:
                print e.message
                print "Could not bind socket to port! Exiting"
                self.shutdown_and_close()
                sys.exit(1)
        self.listen_main_loop()

    def shutdown_and_close(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            print e.message, " Couldn't shutdown the socket on the server."
        try:
            self.sock.close()
        except Exception as e:
            print e.message, " Couldn't close the socket"

    def process_client_address(self, cli_ip):
        server_ip = socket.gethostbyname(socket.gethostname())
        if is_in_same_subnet(server_ip, cli_ip):
            return True
        else:
            return False

    def listen_main_loop(self):
        while True:
            self.sock.listen(1)
            conn, cli_addr = self.sock.accept()
            print "fine" # prints 4 times!

            if os.fork() == 0:
                if self.process_client_address(cli_addr[0]):
                    print "OH!"
                else:
                    print "Access Denied."
                data = conn.recv(1024)
                '''conn.send('HTTP/1.0 200 OK\n')
                conn.send('Content-Type: text/html\n')
                conn.send('Keep - Alive: timeout = 5, max = 100\n')
                conn.send('Connection: Keep-Alive\n')
                conn.send('\n')
                conn.send("""
                            <html>
                            <body>
                            <h1>Hello World</h1> Wait, my server?
                            </body>
                            </html>
                        """)'''
                process_data(self, data, conn)
                sys.exit(1)
            else:
                # Parent should simply listen to incoming requests
                pass


def is_in_same_subnet(server_ip, cli_ip):
    # must fill this out
    return True


def get_file(filename):
    filename_stripped = filename.split("?")[0]
    try:
        f = open(filename_stripped[1:], 'rb')
        file_contents = f.read()
        return file_contents
    except Exception as e:
        print e.message
        return None


def process_data(server, data, conn):
    if data[0:3] == "GET":
        header_lines = data.split("\n")
        method_and_file = header_lines[0].split(" ")
        method = method_and_file[0]
        filename = method_and_file[1]
        file_to_send = get_file(filename)
        if file_to_send:
            global http_header_success
            conn.send(http_header_success + file_to_send)
        else:
            global http_header_file_not_found
            conn.send(http_header_file_not_found)
        conn.close()


def main():
    client_count = 0
    s = Server(8952)
    s.create_socket()

if __name__ == "__main__":
    main()