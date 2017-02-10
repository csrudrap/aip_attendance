# Use a socket to accept connections from clients
# Accept connection and receive data
# Check if they belong to the correct subnet, then process the data sent.
# If they are requesting for attendance.html, read attendance.html from a file and send it on this connection.
# Read asynchronously from a file with unity IDs of all the students of this class, and see if the entered ID is valid.
# If they are submitting, extract the values they are sending from the POST req, put the values into a text file.


import socket
import os
import sys
import time

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

    def listen_main_loop(self):
        while True:
            self.sock.listen(1)
            conn, cli_addr = self.sock.accept()
            if os.fork() == 0:
                if process_client_address(cli_addr[0]):
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
                    process_data(data, conn)
                else:
                    print "Access Denied."
                sys.exit(1)
            else:
                # Parent should simply listen to incoming requests
                pass


def process_client_address(cli_ip):
    server_ip = socket.gethostbyname(socket.gethostname())
    if is_in_same_subnet(server_ip, cli_ip):
        return True
    else:
        return False


def is_in_same_subnet(server_ip, cli_ip):
    # must fill this out
    return True


def get_file(filename):
    filename_stripped = filename.split("?")[0]
    try:
        f = open(filename_stripped[1:], 'rb')
        try:
            file_contents = f.read()
            return file_contents
        except Exception as e:
            print "File could not be read: ", e.message
            return None
    except Exception as e:
        print "File could not be opened: ", e.message
        return None


def write_attendance_file(dict_params):
    try:
        file_all_students = open("Students_Sorted.txt")
        try:
            all_students_contents = file_all_students.read()
            lines = all_students_contents.split("\n")
            dict_unity_ids = {}
            for i in lines:
                if ":" in i and ";" in i:
                    dict_unity_ids[i.split(";")[1].strip()] = int(i.split(":")[0])
            dict_unity_ids_str_keys = map(str.strip, dict_unity_ids.keys())
            if dict_params.get("unity_id") in dict_unity_ids_str_keys:
                # open the new file
                # acquire lock (global boolean?)
                # write
                # release lock
                try:
                    f_att_out = open("Att_output.txt", "ab")
                    try:
                        output = "\n" + str(dict_unity_ids.get(dict_params.get("unity_id"))) + ". " \
                            + str(dict_params.get("unity_id")) + "\t" + dict_params.get("last_name") + " " \
                            + dict_params.get("first_name")
                        try:
                            f_att_out.write(output)
                            return True
                        except Exception as e:
                            print "Error in writing to file", e.message
                    except Exception as e:
                        print "File could not be read: ", e.message
                        return False
                except Exception as e:
                    print "File could not be opened: ", e.message
                    return False

        except Exception as e:
            print "File could not be read: ", e.message
            sys.exit(1)
    except Exception as e:
        print "File could not be opened: ", e.message
        sys.exit(1)
    return False


def process_data(data, conn):
    header_lines = data.split("\n")
    method_and_file = header_lines[0].split(" ")
    print method_and_file
    method = method_and_file[0]
    filename = None
    if len(method_and_file) > 1:
        filename = method_and_file[1] if method_and_file is not None else None
    if method is not None and method == "GET":
        file_to_send = get_file(filename)
        if file_to_send:
            global http_header_success
            conn.send(http_header_success + file_to_send)
        else:
            global http_header_file_not_found
            conn.send(http_header_file_not_found)
    elif method is not None and method == "POST":
        split_data = data.split("\n")
        path = split_data[0].split(" ")[1]
        if path.lower() == "/submit":
            '''dict_cli_inp = {}
            for item in data.split("\n")[1:]:
                if ":" in item:
                    dict_cli_inp[item.split(":")[0]] = item[len(item.split(":")[0]) + 1:]
            print dict_cli_inp'''
            params_joined = split_data[-1]
            dict_params = {}
            for item in params_joined.split("&"):
                if "=" in item:
                    dict_params[item.split("=")[0]] = item.split("=")[1]
            w = write_attendance_file(dict_params)
            if w:
                conn.send(http_header_success + "<html><body><h1>Attendance has been recorded</h1></body</html>")
            else:
                conn.send(http_header_file_not_found)   # have to handle properly
    conn.close()
    sys.exit(0)


def main():
    client_count = 0
    s = Server(8956)
    s.create_socket()

if __name__ == "__main__":
    main()

'''POST /submit HTTP/1.1
Host: 192.168.0.14:8953
Connection: keep-alive
Content-Length: 35
Cache-Control: max-age=0
Origin: http://192.168.0.14:8953
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36
Content-Type: application/x-www-form-urlencoded
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Referer: http://192.168.0.14:8953/attendance.html
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.8

unity_id=0&first_name=s&last_name=q'''