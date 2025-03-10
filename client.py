import socket
import time
import re
# Create a socket object

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
    
    print(res)
    # print(message_payload)
    
    # for c in message_payload:
    #     print(c)
        
    
    
    
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
                
    else:
        # print(message)
        if len(message) > 5:
            
            message_length = message[:4].decode()
            message_type = message[4:5].decode()
            
            #Check to see if it is a valid message
            if check_integer(message_length) and check_integer(message_type):
                
                #Make sure the length field and type field are what we expect
                if int(message_type) < 8 and int(message_length) > 0:
                    
                
                    
                    message_length = int(message_length.replace("0", ""))
                    
                    message_payload = message[5:5+message_length].decode()
                    handle_message(int(message_type), message_payload)
                    # print(message_payload)
                else:
                    print("Invalid Msg Length Field or Invalid Msg Type")
            else:
                print("Invalid Msg Length Field or Invalid Msg Type")
    

s = socket.socket()

# Define the port on which you want to connect
port = 5000
# ip = '10.192.162.102'
ip = '127.0.0.1'

# connect to the server on local computer
s.connect((ip, port))



handshake_read = False
while True:
# receive data from the server
    
    
    message = s.recv(1024)

    #Looking for handshake segment
    check_message(message) 
        
        
    # time.sleep(3)
# close the connection
# s.close()