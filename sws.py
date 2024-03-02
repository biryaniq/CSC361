import select
import socket
import sys
import queue
import time
import re
import os

############################################
# Returns formatted timestamp: 
# e.g. Mon Jan 15 08:44:35 PST 2024
############################################  
def get_formatted_timestamp():
    ts = time.ctime().split(" ")
    formatted_timestamp = ts[0] + " " + ts[1] + ts[2] + " " + ts[3]  + " " + time.tzname[0] + " " + ts[4]
    return formatted_timestamp

############################################
# Creates formatted log for server
############################################  
def create_log(formatted_timestamp, ip, port, request, response):
    log = formatted_timestamp + " " + ip + ":" + port + " " + request + "; " + response
    return log

############################################
# Closes Socket 
############################################ 
def close_socket(s):
    
    if s in request_message:
        del request_message[s]
    if s in response_message:
        del response_message[s]
    if s in inputs: 
        inputs.remove(s)
    if s in outputs:
        outputs.remove(s)
    s.close()
    
    
    
############################################
# Checks if message is valid   
############################################    
def check_validity(message, request_no):
 
    valid = ""

    get_request = re.search(r"^GET .+/* HTTP/1\.0",message)
    keep_alive = re.search(r"Connection:\s*keep-alive", message, re.IGNORECASE)
    conn_close = re.search(r"Connection:\s*close", message, re.IGNORECASE)
    
    empty_newline = re.search(r"^(\n|\r\n)$",message)
    
    if get_request or keep_alive or conn_close or empty_newline:
        valid = "yes"
        
    #check to see if keep_alive or close is the first header (invalid)
    if (keep_alive or conn_close) and request_no == 0:
        valid = ""
    
    return valid


############################################
# Takes complete request headers and parses
# into a response message
# 
############################################    
def process_message(request_queue):
    
    persistence = 0
    close = 0
    
    req_line_1 = request_queue.get()
    
    #check that it's not an endline
    if re.search("^(\n|\r\n)$",req_line_1):
        response = str()
        return response
    
    #parse first line for filename
    parsed_msg = req_line_1.split(" ")
    
    #search for file
    unparsed_filename = parsed_msg[1].split("/")
    filename = unparsed_filename[1]
    
    #initialize list for contents
    file_contents = []
    
    #create response string
    response = "HTTP/1.0 "
    
    try:
        file = open(filename, 'r')
        response += "200 OK"
        #add contents to temp string
        file_contents = file.readlines()
        file.close()
            
    except (FileNotFoundError, IOError):
        response += "404 Not Found"    
    
    req_line_2 = request_queue.get()
    
    formatted_req_line_1 = req_line_1.strip("\r\n")
    #We have the code, print log
    log = create_log(get_formatted_timestamp(), client_ip, str(client_port), formatted_req_line_1, response)
    print(log)
    
    #Add endline to response msg
    response += "\r\n"
    
    # make sure it's not an endline
    if not re.search("^(\n|\r\n)$",req_line_2):
        
        #add connection type to response header
        response += req_line_2
        response += "\r\n"
        #check if it's keep alive or close
        parsed_conn_msg = req_line_2.split(" ")
        conn_type = parsed_conn_msg[1]
        if re.search("Keep-alive",conn_type, re.IGNORECASE):
            # we need to reset timeout
            persistence = 1
        else:
            # we need to close connection after printing response
            close = 1
    else:
        # endline also closes
        close = 1
        response += "Connection: close\r\n\r\n"
    
    #add file list contents to response message
    response += "".join(file_contents)
        
    return response, persistence, close

############################################
# Check if message has multiple headers
# and parse it into a list
############################################
def get_all_requests(message):
    header_list = [line.rstrip('\r\n') + '\r\n' for line in message.splitlines(True)]
    return header_list


############################################
# Initialization
############################################

# Create timestamp
initial_ts = time.localtime()

# Initialize "Connection: keep-alive" variable
persistence = 0

# Initialize "Connection: close" variable
close = 0

# Initialize bad request flag
bad_request = 0

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4, TCP based stream

# Allow address reuse
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Set the socket to non-blocking mode
server.setblocking(0)

# Bind address, server_address is defined by the input
server_address = sys.argv[1]
port = int(sys.argv[2])

server.bind((server_address, port))
# Listen for incoming connections
server.listen(5)

#server timeout check
timeout = 5

###############################################
# Main Loop
###############################################

inputs = [server] # Sockets to watch for readability

# Sockets to watch for writability
outputs = [] 

# Outgoing message queues (socket:queue)
response_message = {}

# Incoming message
request_message = {}

while True:
    # Wait for at least one of the sockets to be ready for processing
    readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
    


###############################################
# Handle Readable Sockets
###############################################

    for s in readable:
        if s is server:
            # Accept new connection and append new connection socket to the list to watch for readability
            conn, addr = s.accept()
            inputs.append(conn)
            request_message[conn] = queue.Queue()
            response_message[conn] = queue.Queue()

        else: 
            # Receive message from the receiving buffer
            message = s.recv(1024).decode()
            client_ip, client_port = s.getpeername()

            if message:
                #check message, parse into multiple messages if multiple request lines
                header_list = get_all_requests(message)
                size = len(header_list)
                if size > 0:
                    for i in header_list:
                        #check if valid
                        if not check_validity(i, request_message[s].qsize()): 
                            #if invalid, add bad request to response queue
                            if bad_request == 0:
                                response = "HTTP/1.0 400 Bad Request\r\n"
                                formatted_request = i.strip("\r\n")
                                log = create_log(get_formatted_timestamp(), client_ip, str(client_port), formatted_request, response)
                                print(log)

                                response += "Connection: close\r\n\r\n"
                                outputs.append(conn)
                                response_message[s].put(response.encode())
                                bad_request = 1
                            else:
                                continue
                            
                        else:
                            request_message[s].put(i)
                            
                            l = list(request_message[s].queue)     
                            whole_message = "".join(l)
                
                            if re.search(r"^(\n|\r\n)",whole_message):
                                whole_message = str()
                        
                            #if message is complete (ends with "\r\n\r\n" or "\n\n"):
                            check_request_end = re.search(r"(\n\n|\r\n\r\n)$",whole_message)
                            if check_request_end:

                                # Add connection socket s to the list for outputs as we will send back messages
                                outputs.append(conn)

                                # Process the message into a response
                                response, persistence, close = process_message(request_message[s])
                                
                                # Add the response to the response queue
                                response_message[s].put(response.encode())
                                
                                if persistence:
                                    #reset timestamp for timeout
                                    initial_ts = time.localtime()

                                    while not request_message[s].empty():
                                        temp = request_message[s].get()
                                    whole_message = str()

            else:
                close_socket(s)

###############################################
# Handle Writable Sockets
###############################################
    for s in writable:
        # Get messages from response_message[s]
        try:
            #check if closed socket not removed
            if s.fileno() == -1:
                if s in outputs: 
                    outputs.remove(s)
                continue
            next_msg = response_message[s].get_nowait()
        except KeyboardInterrupt:
            close_socket(s)
        except queue.Empty:
            # Check if timeout or connection is persistent or not, and close socket accordingly
            if (not persistence or close or bad_request):
                close_socket(s)
                close = 0 
                bad_request = 0
        else:
            s.send(next_msg)

if s not in readable or writable or exception:
    if time.mktime(time.localtime()) - time.mktime(initial_ts) > 30:
        close_socket(s)
        


