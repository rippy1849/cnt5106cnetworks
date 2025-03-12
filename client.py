import socket
import time
import re
# Create a socket object


def peer_recieve_routine():
    s = socket.socket()

    # Define the port on which you want to connect
    port = 5000
    # ip = '10.192.162.102'
    ip = '127.0.0.1'

    # connect to the server on local computer
    s.connect((ip, port))


    while True:
    # receive data from the server
        
        #What if message gets cut off?
        
        #Need to make this the max packet size
        message = s.recv(32773)

    
        #Looking for handshake segment
        
        #what if message contains more than one message?
        while len(message) > 0:
            message = check_message(message)
    
    
    
    return



def check_integer(s):
    # our created pattern to check for the integer value
    if re.match('^[+-]?[0-9]+$', s):
        return True
    else:
        return False



def handle_message(message_type,message_payload):
    
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
            handle_bitfield_message(message_payload)
        case 6:
            #request
            print("Request")
        case 7:
            #piece
            print("Piece")
    
    
    
    return

def handle_bitfield_message(message_payload):
    
    res = ''.join(format(ord(i), '08b') for i in message_payload)
    
    avaliable_list = []
    for chunk,c in enumerate(res):
        if c == '1':
            avaliable_list.append(chunk)
    # print(avaliable_list)
    #If peer has pieces this peer wants, send interested message else, send 
    
        
    
    
    return


def check_message(message):
    
    if message != "" and len(message) >= 32:
        
        handshake_header = message[:18]
        # print(handshake_header)
        if handshake_header.decode() == 'P2PFILESHARINGPROJ':
            # print("is handshake")
            zero_bits = message[18:28].decode()
            peer_id = message[28:32].decode()
            
            print(zero_bits)
            print(peer_id)
            
            
            #Check peer_id to see if it is correct, then begin accepting messages
            #NEED THE CHECK PEER ID
            #See if the connection is the correct neighbor ie check the header and make sure the peer id is good
            
            return message[32:]
                
    else:
        # print(message)
        if len(message) > 5:
            
            message_length = message[:4].decode()
            message_type = message[4:5].decode()
            
            #Check to see if it is a valid message info
            if check_integer(message_length) and check_integer(message_type):
                
                #Make sure the length field and type field are what we expect, and that the message contains the full payload. Reject bad messages
                if int(message_type) < 8 and int(message_length) > 0 and len(message) >= (int(message_length) + 5):
      
                    message_length = int(message_length.replace("0", ""))
                    
                    message_payload = message[5:5+message_length].decode()
                    handle_message(int(message_type), message_payload)
                    # print(message_payload)
                    return message[5+message_length:]
                else:
                    print("Invalid Msg Length,Invalid Msg Type, or Invalid Msg Payload")
                    return ""
            else:
                print("Invalid Msg Length Field or Invalid Msg Type")
                return ""
    


peer_recieve_routine()