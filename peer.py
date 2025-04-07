import socket
import time
import re
import threading
import os
import math
from datetime import datetime


#TODO Anywhere there is a connection.send, need to wrap it in a connection error handler

HANDSHAKE_HEADER = 'P2PFILESHARINGPROJ'
DOWNLOAD_RATE_WINDOW = 0.5

class Tables:
    def __init__(self):
        self.connection_table = {}
        self.connection_key_table = {}
        self.download_table = {}
        
    def getConnectionTable(self):        
        return self.connection_table
    def setConnectionTableEntry(self,entry,value):
        self.connection_table[entry] = value
        
    def getConnectionKeyTable(self):        
        return self.connection_key_table
    def setConnectionKeyTableEntry(self,entry,value):
        self.connection_key_table[entry] = value
           
    def getDownloadTable(self):        
        return self.download_table
    def setDownloadTableEntry(self,entry,value):
        self.download_table[entry] = value


def exit_thread_and_cleanup():
    
    
    #Delete connection entry from table
    
    #Delete all existing pieces in peer file
    
    exit()
    
    return


def send_message(connection, message, self_peer_id, target_peer_id, i):
    
    try:
        connection.send(message.encode('utf-16'))
    except:
        print(f"Connection Lost {self_peer_id} to {target_peer_id} on {i}")
        # exit_thread_and_cleanup()
        return 1
        
    
    
    return



def cleanup_logs(self_peer_id):
    
    filepath = os.path.join(os.getcwd(), 'logs', str(self_peer_id) + '_log')
    
    if os.path.exists(filepath):    
        os.remove(filepath)
    
    return


def log_entry(filename, log_entry):
    
    
    current_timestamp = round(datetime.now().timestamp(),2)
    file_written = False
    while file_written == False:
    
        filepath = os.path.join(os.getcwd(), 'logs', filename)

        if not os.path.exists(os.path.join(os.getcwd(), 'logs')):
            os.mkdir(os.path.join(os.getcwd(), 'logs'))          
    
        try:
                
            # if os.path.exists(os.path.join(os.getcwd(), 'logs', filename)):
            #     # file1 = open('logs/'+ filename, "a")
            #     with open(os.path.join(os.getcwd(), 'logs', filename), 'a') as file:
            #         file.write(log_entry)
            #     file_written = True           
                
            
            if not os.path.exists(filepath): 
                    
                file = open(filepath, "w")  # write mode
                file.write(log_entry + ": " + str(current_timestamp) + "\n")
                file.close()
                file_written = True
            else:

                file = open(filepath, "a")  # append mode
                file.write(log_entry + ": " + str(current_timestamp) + "\n")
                file.close()
                file_written = True               
                
                    
        except:
            print(f"File {filename} is open")
    



def optimistic_interval(connection, interval_time):
    
    prev_timestamp_optimistic = datetime.now().timestamp()
    
    while True:
        current_timestamp = datetime.now().timestamp()
        if current_timestamp - prev_timestamp_optimistic > interval_time:
        
            print(current_timestamp - prev_timestamp_unchoking, 'Optimistic Interval')

        
            prev_timestamp_unchoking = current_timestamp
                        


def unchoking_interval(connection, interval_time):
    
    prev_timestamp_unchoking = datetime.now().timestamp()
    
    while True:
        current_timestamp = datetime.now().timestamp()
        if current_timestamp - prev_timestamp_unchoking > interval_time:
        
            print(current_timestamp - prev_timestamp_unchoking, 'Choking Interval')
        
            prev_timestamp_unchoking = current_timestamp
        
            # send_download_message(connection,0)
                

    return


def generate_piece_list(self_peer_id,common_cfg):
    
    
    
    directory = "peer_" + str(self_peer_id)
    #check to see if the directory exists, if not create it
    if not os.path.exists(os.path.join(os.getcwd(), directory)):
        os.mkdir(os.path.join(os.getcwd(), directory))
    
    
    file_name = common_cfg['FileName']
    if os.path.exists(os.path.join(os.getcwd(), directory, file_name)):
   
        piece_size = int(common_cfg['PieceSize'])
        file_size = int(common_cfg['FileSize'])
        
        number_of_pieces = file_size/piece_size
        number_of_pieces_int = int(number_of_pieces)
        total_number_of_pieces = 0
        
        if number_of_pieces != number_of_pieces_int:
            #Float has extra decimal, not a perfect split, need one extra piece for remaining file chunk
            total_number_of_pieces = number_of_pieces_int + 1
        else:
            total_number_of_pieces = number_of_pieces_int
            
            
        
    return

def binary_to_string(bits):
    return ''.join([chr(int(i, 2)) for i in bits])


def check_integer(s):
    # our created pattern to check for the integer value
    if re.match('^[+-]?[0-9]+$', s):
        return True
    else:
        return False










def handle_message(message_type,message_payload,tables, connected_peer_id, self_peer_id, peer_cfg,common_cfg, pieces_list):
    
    match message_type:
        case 0:
            #Choke Case
            print("Choking")
        case 1:
            #Unchoke
            print("Unchoking")
        case 2:
            #Interested 
            print("Interested")
        case 3:
            #Not Interested
            print("Not Interested")
        case 4:
            #Have
            print("Have")
        case 5:
            #Bitfield
            print("Bitfield")
            handle_bitfield_message(message_payload,self_peer_id,connected_peer_id, pieces_list)
        case 6:
            #request
            print("Request")
            handle_request_message(message_payload,self_peer_id,connected_peer_id,tables, peer_cfg)
            # print(len(connection_table))
        case 7:
            #piece
            print("Piece")
            print(message_payload)
        case 8:
            #Establishing Connection Table Needed for python
            # print("Establishing")
            # print(message_payload)
            handle_establishing_message(message_payload,tables, connected_peer_id, self_peer_id,peer_cfg)
            
        case 9:
            #Download Rate Message
            # print("Download Rate Message")
            handle_download_rate_message(message_payload,tables,connected_peer_id,self_peer_id,peer_cfg)        
    
            
    
    
    
    return


def handle_download_rate_message(message_payload,tables, connected_peer_id, self_peer_id,peer_cfg):
    
    
    if message_payload[0] == '0':
        #Start Junk Download Data
        
        # print("Junk Data begin")
        log_entry(str(self_peer_id)+'_log','Junk Download Data Message')

        byte_entry = str(connected_peer_id) + "-bytes"
        tables.setDownloadTableEntry(byte_entry,0)

        connection_key_table = tables.getConnectionKeyTable()
        connection_table = tables.getConnectionTable()
        
        connection_key = connection_key_table[str(connected_peer_id)]
        
        
        connection = connection_table[connection_key]
        # connection = connection_table[connection_table[str(connected_peer_id)]]
        t = threading.Thread(target=send_junk_message, args=(connection,self_peer_id,connected_peer_id))
        t.start()
        current_timestamp = datetime.now().timestamp()
        tables.setDownloadTableEntry(str(connected_peer_id) + '-start',current_timestamp)
        
    if message_payload[0] == '1':
        # Calculate Download Rate
        # print("Download Rate Message")
        # print(len(message_payload))
        
        download_table = tables.getDownloadTable()
        byte_entry = str(connected_peer_id) + "-bytes"
        if byte_entry in download_table:
            prev_bytes = download_table[byte_entry]
            new_bytes = prev_bytes + len(message_payload) +5 
            tables.setDownloadTableEntry(byte_entry,new_bytes)
        else:
            new_bytes = len(message_payload) + 5
            tables.setDownloadTableEntry(byte_entry,new_bytes)
            
        
        
        
    if message_payload[0] == '2':
        # print("Stop Message")
        stop_timestamp = datetime.now().timestamp()
        
        download_table = tables.getDownloadTable()
        start_entry = str(connected_peer_id) + '-start'
        byte_entry = str(connected_peer_id) + "-bytes"
        rate_entry = str(connected_peer_id) + "-rate"
        
        
        #TODO Somehow, some way, '0' is being skipped, and the table entry is not being set, defaulting to 0, bad connection
        try:
            start_timestamp = download_table[start_entry]
            total_bytes_transferred = download_table[byte_entry]
        except:
            start_timestamp = 0
            total_bytes_transferred = 0
        
        
        #TODO stop_timestamp-start_timestamp can sometimes be zero, how to handle? Also why? How can two timestamps possibly be identical?
        
        try:
            if stop_timestamp-start_timestamp == 0:
                download_rate = 0
            else:
                download_rate = total_bytes_transferred/(stop_timestamp-start_timestamp)
        except:
            print(stop_timestamp,start_timestamp)
        
        
        
        tables.setDownloadTableEntry(rate_entry,download_rate)
        
        
        dlTable = tables.getDownloadTable()
        print('Download Rate', dlTable[rate_entry])
        
        # print(dlTable)
    
    
    return



def handle_request_message(message_payload,self_peer_id,connected_peer_id, tables, peer_cfg):
    
    
    #Upon getting the request message, if not choking, send the piece
    
    piece_index = ""
    if len(message_payload) >= 4:
        piece_index = message_payload[:4]
        
        

    
    
    # connection = connection_table[connection_table[str(connected_peer_id)]]  
    

    # piece = '9u3yry293yr3iurhoewhiofewoijfeo2'
    piece = 'hello!'
    
    

    # send_piece(connection,piece,6)
    # if str(self_peer_id) == '1001':
    #     # print(connection_table.keys())
    #     print(len(peer_cfg)-1)
    # print(connection_table, str(connected_peer_id))
    
    # print(piece_index)
    
    # print(len(connection_table))
     
    
              
    
    return


def handle_establishing_message(message_payload, tables, connected_peer_id, self_peer_id, peer_cfg):
    
    
    # print(message_payload)
    #Only forward once
    # print("Establishing Message: ", message_payload, "from",connected_peer_id, "to", self_peer_id)
    
    
    if len(message_payload) > 0:
        if message_payload[0:1] == '0': 
    
            message_length = len(message_payload)
            forward_message = ""
            
            for i in range(0,4-len(str(message_length))):
                forward_message += "0"
            forward_message += str(message_length)
            forward_message += "8"
            message_payload = '1' + message_payload[1:]
            forward_message += message_payload
            
            
            #will act weird for over 1000 peers
            
            #Make sure the connection table is fully populated before iterating over it
            num_connections = len(peer_cfg)-1
            
            
            while len(tables.getConnectionTable()) < num_connections:
                print("Waiting for connection table to populate",num_connections,len(tables.getConnectionTable()))
                time.sleep(5)
                # print(connection_table)
                
            
            
            #Should be populated with all connections, but not the actual peers
            for i in range(1,num_connections+1):
                
                connection_table = tables.getConnectionTable()
                connection = connection_table[i]
                connection.send(forward_message.encode('utf-16'))

            
        else:
            # print("Not forwarding")
            
            # print(message_payload)
            
            if len(message_payload) >= 9:
                peer_id = message_payload[1:5]
                connection_number = message_payload[5:9]
                connection_number = int(connection_number.replace("0", ""))
                

                
                if str(self_peer_id) == str(peer_id):
                    # print()
                    tables.setConnectionKeyTableEntry(str(connected_peer_id), connection_number)
                    
                    # connection_table[str(connected_peer_id)] = connection_number
                    # print(message_payload)
            
        
    
                    # print(len(connection_table))
    return 



def handle_bitfield_message(message_payload,self_peer_id,connected_peer_id):
    
    res = ''.join(format(ord(i), '08b') for i in message_payload)
    
    
    # print(res)
    avaliable_list = []
    for chunk,c in enumerate(res):
        if c == '1':
            avaliable_list.append(chunk)
            
    # print(message_payload,self_peer_id)
    print(avaliable_list)
    #If peer has pieces this peer wants, send interested message else, send 
    
        
    
    
    return


def check_message(message,self_peer_id,tables, connected_peer_id, peer_cfg, common_cfg, pieces_list):
    
    
    offset_handshake = 0
    if str(hex(ord(message[0:1]))) == '0xfeff':
        offset_handshake = 1


    if len(message) >= 18:
        handshake_header = message[offset_handshake:18+offset_handshake]
    else:
        handshake_header = ""
    
    
    
    if handshake_header == 'P2PFILESHARINGPROJ':
        # print(message,len(message))
        
        
        # print(handshake_header)
        # print("is handshake")
        if len(message) >= 32:
            zero_bits = message[18+offset_handshake:28+offset_handshake]
            peer_id = message[28+offset_handshake:32+offset_handshake]
        
            print("Handshake from ", connected_peer_id ,"to", self_peer_id)
        
        
        
            #return the DECODED message, consistent with size
        
            # print(message)
            return message[32+offset_handshake:]
    else:
        # print(message)
        
        if len(message) > 5:
            # print(message)

            
            # print(message_length,message)
            
            # print(decoded_message,message_length,message_type)
            
            # print(message)
            #Check to see if it is a valid message info
            
            
            #There is a very weird issue with UTF-16 encoding, need to use it, but causes a bug I can't figure out
            # https://unicodemap.com/details/0xFEFF/
            
            offset = 0
            if str(hex(ord(message[0:1]))) == '0xfeff':
                offset = 1
                
            message_length = message[offset:4+offset]
            message_type = message[4+offset:5+offset]   
            
            
            if check_integer(message_length) and check_integer(message_type):
                #Make sure the length field and type field are what we expect, and that the message contains the full payload. Reject bad messages
                message_length = int(message_length)
                
                if message_type == '7':
                    message_length *= 2
                
                
                if int(message_type) < 10 and int(message_length) > 0 and len(message) >= (int(message_length) + 5):
      
                    # message_length = int(message_length.replace("0", ""))
                    
                    message_payload = message[5+offset:5+message_length+offset]
                    handle_message(int(message_type), message_payload, tables, connected_peer_id, self_peer_id, peer_cfg,common_cfg, pieces_list)
                    # print(message_payload)
                
                
                    # print(message[5+message_length:])
                    # return ""
                    # print(message[5+message_length:])
                    # print(message[5+message_length:],message)
                    
                    # if message[5+message_length+offset:] == None:
                        
                        # print(message)
                        # exit()
                        
                    
                    return message[5+message_length +offset:]
                else:
                    print("Invalid Msg Length,Invalid Msg Type, or Invalid Msg Payload")
                    # print(message)
                    return ""
            else:
                
                print("Invalid Msg Length Field or Invalid Msg Type")
                
                # print(message)
                return ""
            
        return ""
    
    return ""
    



#Sends a request message to the desired peer connection for a specific piece
def send_request_message(connection, piece):
    
    payload = ""
    
    length_of_piece = len(str(piece))
    
    
    for i in range(0,4-length_of_piece):
        payload += '0'
    payload += str(piece)
    
    length_of_payload = len(str(payload))
    
    request_message = ""
    
    for i in range(0, 4-len(str(length_of_payload))):
        request_message += '0'
    
    request_message += str(length_of_payload)
    request_message += '6'
    request_message += payload
    
    
    # print(request_message)
    
    connection.send(request_message.encode('utf-16'))  
    
    
    return

def send_piece(connection, piece, piece_size):
    
    #Assuming message length field is 4 bytes long, we must divide 5 byte int by 2 to fit it in 4 byte length field
    piece_message = ""
    
    
    #Divide the piece by n, based on how large the piece size is, such that it fits in a 4 byte number.
    
    message_payload_length = piece_size/2
    
    for i in range(0,4-len(str(int(message_payload_length)))):
        piece_message += '0'
    
    piece_message += str(int(message_payload_length))
    
    piece_message += '7'
    
    piece_message += piece
    
    # print(piece_message)
    
    connection.send(piece_message.encode('utf-16'))
    
    
    return

#Not correct, need to make this able to send upon connection check the pieces that the peer has.
def send_bitfield_message(connection,self_peer_id,common_cfg):
    
    
    directory = "peer_" + str(self_peer_id)
    #check to see if the directory exists, if not create it
    if not os.path.exists(os.path.join(os.getcwd(), directory)):
        os.mkdir(os.path.join(os.getcwd(), directory))
    
    
    file_name = common_cfg['FileName']
    if os.path.exists(os.path.join(os.getcwd(), directory, file_name)):
        
        bitfield_message = ""
        bin_values = []
        piece_size = int(common_cfg['PieceSize'])
        file_size = int(common_cfg['FileSize'])
        
        number_of_pieces = file_size/piece_size
        number_of_pieces_int = int(number_of_pieces)
        total_number_of_pieces = 0
        
        if number_of_pieces != number_of_pieces_int:
            #Float has extra decimal, not a perfect split, need one extra piece for remaining file chunk
            total_number_of_pieces = number_of_pieces_int + 1
        else:
            total_number_of_pieces = number_of_pieces_int
         
         
        # print(total_number_of_pieces)
        # piece_count = 0   
        bin_string = ""
        for i in range(0,total_number_of_pieces):
            # print(i)
            if i % 8 == 0:
                # print(bin_string)
                
                if i != 0:
                    bin_values.append(bin_string)
                bin_string = '1'
            else:
                bin_string += '1'
        if len(bin_string) > 0:
            for i in range(0,8-len(bin_string)):
                bin_string += '0'
            bin_values.append(bin_string)
        piece_string = binary_to_string(bin_values)
        # print(piece_string)
        # print(bin_values)

        # piece_string_length = len(piece_string)
        
        # print(len(str(len(piece_string))))
        # size_of_length = len(piece_size)
        
        # print(size_of_length)
        # print(len(str(piece_string)))
        # string = "11"
        
        
        for i in range(0,4-len(str(len(piece_string)))):
            bitfield_message += '0'
            # print('hello')
        bitfield_message += str(len(piece_string))
        
        # print(bitfield_message)
        bitfield_message += '5'
        bitfield_message += piece_string
        
        # encoded = bitfield_message.encode()
        # print(encoded.decode())
        
        # print(bitfield_message.encode())
        # connection.send()
        encoded = bitfield_message.encode('utf-16')
        # connection.send(encoded)
        # print(encoded)
    
    
    return



def send_establishing_message(connection,self_peer_id, connection_number):

    establishing_message = "000980"

    establishing_message += str(self_peer_id)
    
    
    for i in range(0, 4 - len(str(connection_number))):
        establishing_message += str(0)    

    
    establishing_message += str(connection_number)
    
    # print(establishing_message)
        
    connection.send(establishing_message.encode('utf-16')) 
    
    
    return


def send_download_message(connection, message_type):
    
    download_message = '00019' + str(message_type)
    
    connection.send(download_message.encode('utf-16')) 
    
    return
    
def send_junk_message(connection, self_peer_id, target_peer_id):
    
    junk_message = '0032911234567890123456789012345678901' 
    stop_message = '000192'
    
    # prev_timestamp = datetime.now().timestamp()
    # current_timestamp = datetime.now().timestamp()
    
    # while current_timestamp - prev_timestamp < DOWNLOAD_RATE_WINDOW:
    #TODO Connection sometimes drops here. Might Need a way to reconnect. Might actually be too many messages. Connection is fine
    for i in range(0,10):
        
        error_code = send_message(connection,junk_message,self_peer_id,target_peer_id,i)
        if error_code == 1:
            break
        # connection.send(junk_message.encode('utf-16'))
    
    error_code = send_message(connection,stop_message,self_peer_id,target_peer_id,-1)
    # connection.send(stop_message.encode('utf-16')) 
    
        # current_timestamp = datetime.now().timestamp()
        
    
    return
    



def peer_recieve_routine(ip,port,target_peer_id,self_peer_id,tables, peer_cfg, common_cfg, pieces_list):
    s = socket.socket()
    connected = False
    message_content = False

    message_recieve_size = int(common_cfg['PieceSize']) + 5
    

    #Try to connect to host
    while connected == False:
        try:
            s.connect((ip, int(port)))
            # s.connect((ip, int(port)))
            connected = True
            print(self_peer_id,"Connected", target_peer_id)
            
        except:
            print(self_peer_id,"Couldn't Connect To",target_peer_id)
            connected = False

    prev_timestamp = datetime.now().timestamp()

    while True:
    # receive data from the server
        
        #What if message gets cut off?
        
        #Need to make this the max packet size
        # print(message_recieve_size)
        message = s.recv(message_recieve_size)
        # print(message)
        # print("Recieve loop")
        
        #TODO Messages can be malformed. Need to add, to all send_routines, a re-send based on response or lack thereof
        decoded_message = message.decode('utf-16', errors="ignore")
        #Looking for handshake segment
        # print(decoded_message)
        #what if message contains more than one message? NEED TO FIX
        while len(decoded_message) > 0:
            # print(message)
            # copy = decoded_message
            # print(decoded_message)
            
            
            decoded_message = check_message(decoded_message,self_peer_id,tables,target_peer_id, peer_cfg, common_cfg, pieces_list)
            # print(message)
            prev_timestamp = datetime.now().timestamp()
            #Error here, sometimes returning None, don't know why
            #Might need to fix this, temp fix
            #This might actually work for improperly formatted messages that are returned
            #I'm pretty sure it only returns None when it's improperly formatted
            # if decoded_message == None:
            #     decoded_message = ""
                # print(copy)
            current_timestamp = datetime.now().timestamp()
        
        
        #TODO Need to deal with dropped connections. Later
        if (current_timestamp - prev_timestamp) > 5:
            #It has been 5 seconds since last message, connection likely broke
            print("Connection Dropped, attempting to reconnect")
            # connected = False
            # s = socket.socket() 
            
            # while connected == False:
            #     try:
            #         s.connect((ip, int(port)))
            #         # s.connect((ip, int(port)))
            #         connected = True
            #         print(self_peer_id,"Connected", target_peer_id)
            
            #     except:
            #         print(self_peer_id,"Couldn't Connect To",target_peer_id)
            #         connected = False     
        
    
    
    
    return


def peer_send_routine(self_peer_id,tables, connection_number, peer_cfg, common_cfg):
    
    
    connection_table = tables.getConnectionTable()
    connection = connection_table[connection_number]
    
    handshake = False
    established = False
    connection_table_populated = False
    unchoking_thread_started = False
    optimistic_thread_started = False


    handshake_message = 'P2PFILESHARINGPROJ0000000000' + str(self_peer_id)
    # print(handshake_message)
    # print(handshake_message)
    # handshake_message = HANDSHAKE_HEADER + b'0000000000' + str(self_peer_id).encode('utf-16')
    handshake_message = handshake_message.encode('utf-16')
    
    # print(handshake_message)
    
    # fake_message = '00055hello'.encode()
    
    

    prev_timestamp_unchoking = datetime.now().timestamp()
    prev_timestamp_optimistic = datetime.now().timestamp()

    while True:
        # try:
            # Sending pipeline for messages
            #CHECK initial message header and peer id
            # connection.send(b'Thank you for connecting ' + str(peer_count).encode())
        if handshake == False:
            # print(handshake_message.decode('utf-16'))
            connection.send(handshake_message)
            # handshake = True
            #Check to make sure peer is correct (handshake is also good on their end)
            
            #Send ACK that it is the correct connection?
            handshake = True
        # connection.send(fake_message)
        # print("sent fake message")
        else:
            # established = True
            if established == False:
                send_establishing_message(connection,self_peer_id,connection_number)
                # print("hi")
                established = True
            
            #TODO
            #Update, there MIGHT be an issue with dropped messages
            #There is a race case condition where the connection table is stuck at 3 entries. No idea why. Breaks sometimes
            #MAKE SURE Connection table populates before sending ANY messages
            if connection_table_populated == False:
                while (len(tables.getConnectionKeyTable()) < (len(peer_cfg)-1)):
                    print('Waiting for connection key table to populate-main loop', len(tables.getConnectionKeyTable()), 2*(len(peer_cfg)-1))   
                    
                    time.sleep(2)
                    
                    if(len(tables.getConnectionKeyTable()) < (len(peer_cfg)-1)):
                        #Deal with message being dropped and repopulate the table
                        send_establishing_message(connection,self_peer_id, connection_number)
                            
                
                
                if connection_table_populated == False:
                    print("Connection Table Populated")
                    connection_table_populated = True
                
            
            current_timestamp = datetime.now().timestamp()
                        
            # print(current_timestamp)
            # print(current_timestamp - prev_timestamp)
            # print(current_timestamp)
            
            #TODO Make this it's own thread to be non-blocking for the optimistic interval, not really necessary given how fast this works
            if current_timestamp - prev_timestamp_unchoking > int(common_cfg['UnchokingInterval']):
                
                # print(current_timestamp - prev_timestamp_unchoking, "Unchoking Interval")
                
                # log_entry(str(self_peer_id)+'_log','Unchoking Interval ' + str(connection_number))
                
                prev_timestamp_unchoking = current_timestamp
                
                # print("Unchoking Interval")
                
                send_download_message(connection,0)
            
            
            # while unchoking_thread_started == False:
            #     try:
            #         t1 = threading.Thread(target=unchoking_interval, args=(connection,int(common_cfg['UnchokingInterval'])) )
            #         t1.start()
            #         unchoking_thread_started = True
            #         print("Started Send Thread")
            #     except:
            #         print("Error starting choking thread")
                    
            # while optimistic_thread_started == False:
            #     try:
            #         t1 = threading.Thread(target=optimistic_interval, args=(connection,int(common_cfg['OptimisticUnchokingInterval'])))
            #         t1.start()
            #         optimistic_thread_started = True
            #     except:
            #         print("Error starting optimistic unchoking thread")
                
            #TODO Make this it's own thread to be non-blocking for the choking interval, not really necessary given how fast 
            if current_timestamp - prev_timestamp_optimistic > int(common_cfg['OptimisticUnchokingInterval']):
                
                # print(current_timestamp - prev_timestamp_optimistic, "Optimistic Unchoking " + str(connection_number))
                
                # log_entry(str(self_peer_id)+'_log','Optimistic Unchoking')
                
                
                prev_timestamp_optimistic = current_timestamp
            
       
                
                
            

        
        time.sleep(1)
        # except:
        #     print("Closing Connection")
        #     connection.close()
        #     break
    
    return




def start_peer(peer_id, port):
    
    
    # connection_table = ConnectionTable()
    
    # os.remove("filename.txt")
    cleanup_logs(peer_id)
    
    tables = Tables()
    
    common_cfg_file = open("project_config_file_small/Common.cfg", "r")
    peer_info_cfg_file = open("project_config_file_small/PeerInfo.cfg", "r")
    
    common_cfg = {}
    peer_cfg = {}
    
    pieces_list = []
    
    for line in common_cfg_file:
        options = line.split(" ")
        common_cfg[options[0]] = options[1].rstrip()
        
    for line in peer_info_cfg_file:
        peer_info = line.split(" ")
        peer_cfg[peer_info[0]] = {'ip' : peer_info[1], 'port' : peer_info[2], 'has_file' : peer_info[3]}
    # print(peer_cfg)
    
    #Keep track of the send & recieve threads
    
    
    
    #Establish Connection to all other peers in peer list
    for peer,info in peer_cfg.items():
        if str(peer) != str(peer_id):
            
            peer_ip = info['ip']
            peer_port = info['port']
            recieve_thread = threading.Thread(target=peer_recieve_routine, args=(peer_ip,peer_port,int(peer),int(peer_id),tables,peer_cfg,common_cfg,pieces_list))
            recieve_thread.start()

    
    
    
    
    
    
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hostName = socket.gethostbyname( '0.0.0.0' )
    s.bind((hostName, port))


    # print ("socket binded to %s" %(port))

    # put the socket into listening mode
    s.listen(5)    
    # print ("socket is listening")
    connection_count = 1
    while True:

    # Establish connection with client.
        #How to tell what peer the connection is to
        c, addr = s.accept()
        # print ('Got connection from', addr)
        
        
        
        # connection_table.updateTable(connection_count,c)
        tables.setConnectionTableEntry(connection_count,c)
        # connection_table[connection_count] = c
        # print(connection_count)
        
        
        
        t1 = threading.Thread(target=peer_send_routine, args=(peer_id,tables, connection_count, peer_cfg,common_cfg))
        
        connection_count += 1
        # t2 = threading.Thread(target=peer_recieve_routine, args=(peer_ip,peer_port,peer_id,))
        # print ('Got connection from', addr )
        t1.start()
        # t2.start()