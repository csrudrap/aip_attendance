# Use a socket to accept connections from clients
# Accept connection and receive data
# Check if they belong to the correct subnet, then process the data sent.
# If they are requesting for attendance.html, read attendance.html from a file and send it on this connection.
# Read asynchronously from a file with unity IDs of all the students of this class, and see if the entered ID is valid.
# If they are submitting, extract the values they are sending from the POST req, put the values into a text file.


import socket
import os
import sys
import commands
import time
import random
import logging
import json

http_header_success = "HTTP/1.0 200 OK\nContent-Type: text/html\nKeep - Alive: timeout = 1, " \
                  "max = 100\nConnection: close\n\n"
http_header_file_not_found = "HTTP/1.0 404 Not Found\nContent-Type: text/html\nKeep - Alive: timeout = 1, " \
                  "max = 100\nConnection: close\n\n"
lock_att_output = False


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
        logging.info("Socket has been opened on port: " + str(self.port))
        self.listen_main_loop()

    def shutdown_and_close(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            print "Socket shutdown successfully."
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
            logging.info("Client connection accepted with: " + str(cli_addr))
            if os.fork() == 0:
                data = conn.recv(1024)
                student_info = data.split("\n")[-1]
                logging.info("data: " + str(student_info))
                #if process_client_address(cli_addr[0]):
                    #logging.info("Data received by " + str(cli_addr),
                #                 " at time: %s is: %s" % (str(time.ctime()), str(student_info)))
                process_data(data, conn, cli_addr[0])
                self.shutdown_and_close()
                #else:
                    # Must get client IP address and what they send. Create a different function that
                    # extracts IP address from data sent by the client.
                    #print "Access Denied. Client IP address not in same subnet: " + str(cli_addr[0])
                    #logging.info("Access Denied. Client IP address not in same subnet: " + str(cli_addr[0]) + \
                     #            "and the data sent by the client is: " + data)
                sys.exit(1)
            else:
                # Parent should simply listen to incoming requests
                pass


def process_client_address(cli_ip):
    # server_ip = socket.gethostbyname(socket.gethostname())
    if is_in_same_subnet(cli_ip):
        return True
    else:
        return False

# def add_ip_unity_pair()
    # For every request to submit attendance, add the unity ID and IP address pair to a new file. Also add Y for same
    # subnet and N for not in the same subnet. Same subnet check should be done AFTER this.

# def get_cli_ip()

def is_in_same_subnet(cli_ip):
    if cli_ip == "127.0.0.1":
        return True
    status, ip_addr_op = commands.getstatusoutput("ifconfig en0 | grep \"inet \"")
    ip_addr_mask = ip_addr_op.split(" ")[0:4]
    if ip_addr_mask is not None:
        server_ip = ip_addr_mask[1]
        mask_in_hex = ip_addr_mask[3]
        mask_in_bin = bin(int(mask_in_hex, 16))
        mask_count = mask_in_bin.count('1')
        # We have the IP address and mask now.
        # if cli_ip XOR server_ip starts with at least mask_count number of 0s, then same subnet
        bin_cli = bin_from_dotted_decimal(cli_ip)
        bin_server = bin_from_dotted_decimal(server_ip)
        xor = bin(int(bin_cli, 2) ^ int(bin_server, 2))
        num_padding = 32 - len(xor[2:])
        padding = "0" * num_padding
        xor = padding + str(xor[2:])
        if xor.startswith("0" * mask_count):
            return True
        else:
            return False


def bin_from_dotted_decimal(ip):
    ip_split = map(int, ip.split("."))
    ip_split_bin = map(bin, ip_split)
    ip_bin_str = ""
    for i in ip_split_bin:
        if len(i[2:]) < 8:
            mul_qty = 8 - len(i[2:])
            running_str = str(mul_qty * "0")
            ip_bin_str += str(running_str) + str(i[2:])
        elif len(i[2:]) == 8:
            ip_bin_str += str(i[2:])
    return ip_bin_str


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


def already_exists(param):
    file_output = open("Att_output.txt", "rb")
    # check if this unity ID exists in the file already, do not have duplicates.
    output_lines = file_output.read()
    output_lines_l = output_lines.split("\n")
    if len(output_lines_l) > 1:
        new_l = []
        for i in output_lines_l[1:]:
            new_l.append(i.split(" ")[1].split("\t")[0])
        if param in new_l:
            return True
        else:
            return False
    else:
        return False


def write_attendance_file(dict_params, cli_ip):
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
                        output = ""
                        if not already_exists(dict_params.get("unity_id")):
                            output = "\n" + str(dict_unity_ids.get(dict_params.get("unity_id"))) + ". " \
                                + str(dict_params.get("unity_id")) + "\t" + dict_params.get("last_name") + " " \
                                + dict_params.get("first_name") + "\t" + cli_ip
                            try:
                                global lock_att_output
                                while lock_att_output:
                                    logging.warn("Cannot write to file, lock cannot be acquired. Will try again.")
                                    time.sleep(random.randint(0, 1))
                                if not lock_att_output:
                                    lock_att_output = True
                                    logging.info(output)
                                    #check_with_arp(dict_params.get("unity_id"), cli_ip)
                                    if process_client_address(cli_ip):
                                        f_att_out.write(output)
                                    else:
                                        f_diff_subnet_clients = open("Diff_subnets.txt", "ab")
                                        f_diff_subnet_clients.write(output)
                                        # CLIENT FROM DIFF SUBNET COMING HERE.
                                        # WRITE TO A DIFF FILE: output, cli_ip
                                        pass
                                    lock_att_output = False
                                return True
                            except Exception as e:
                                print "Error in writing to file", e.message
                        else:
                            return False
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


def process_data(data, conn, cli_ip):
    header_lines = data.split("\n")
    method_and_file = header_lines[0].split(" ")
    method = method_and_file[0]
    filename = None
    if len(method_and_file) > 1:
        filename = method_and_file[1] if method_and_file is not None else None
    if method is not None and method == "GET":
        file_to_send = get_file(filename)
        if file_to_send:
            global http_header_success
            logging.info("Sending HTTP success with file to client.")
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
                    dict_params[item.split("=")[0]] = item.split("=")[1].lower()
            w = write_attendance_file(dict_params, cli_ip)
            if w:
                conn.send(http_header_success + "<html><body><h1>Attendance has been recorded</h1></body</html>\n")
            else:
                conn.send(http_header_success + "<html><body><h1>Unable to add attendance. Make sure you belong to this"
                                                " class, and make sure you submit only once!</h1></body</html>\n")
    conn.close()
    sys.exit(0)


def check_with_arp(unity_id, cli_ip):
    status, arp_entry = commands.getstatusoutput("arp -n -i en0 -a | grep \(" + str(cli_ip) + "\)")
    if len(arp_entry) > 0:
        mac_address = arp_entry.split("at ")[1].split(" ")[0].strip()
        data = {}
        with open("unity_mac.json", "w+") as f1:
            data = json.load(f1)
        print "open worked"
        if len(data.keys()) == 0:
            data[unity_id] = [mac_address]
        if mac_address not in data[unity_id][0]:
            data[unity_id].extend(mac_address)
        if len(data[unity_id][0]) > 2:
            logging.critical(unity_id, "has more than 2 MAC addresses associated with the unity ID! Their IP addr is:", cli_ip)
        with open("unity_mac.json", "w+") as f2:
            json.dump(data, f2)
    else:
        if check_with_arp.counter < 5:
            time.sleep(random.randint(0, 1))
            check_with_arp(unity_id, cli_ip)
    check_with_arp.counter += 1


        # put this in the json file that has unity_id: {mac1, mac2..}
        # if this list has more than 2 macs, log it (critical)

def main():
    # client_count = 0
    global lock_att_output
    lock_att_output = False
    check_with_arp.counter = 0
    logging.basicConfig(filename="att.log", level=logging.DEBUG)
    logging.info("Started")
    s = Server(8980)
    s.create_socket()
    logging.info("Finished")

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
