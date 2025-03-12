import socket
import time
import re
import threading
# Create a socket object


HANDSHAKE_HEADER = b'P2PFILESHARINGPROJ'


#Might need to put mutex's here, maybe
class ConnectionTable:
    def __init__(self):
        self.table = {}

    def updateTable(self,key,connection):
        # print("Hello my name is " + self.name)
        self.table[key] = connection
    def getConnection(self,key):
        return self.table[key]

def peer_recieve_routine(ip,port,target_peer_id,self_peer_id,connection_table):
    s = socket.socket()
    connected = False

    

    #Try to connect to host
    while connected == False:
        try:
            s.connect((ip, int(port)))
            connected = True
        except:
            print(self_peer_id,"Couldn't Connect To",target_peer_id)
            connected = False

    while True:
    # receive data from the server
        
        #What if message gets cut off?
        
        #Need to make this the max packet size
        message = s.recv(32773)
        # print(message)
        # print("Recieve loop")
        
    
        #Looking for handshake segment
        
        #what if message contains more than one message? NEED TO FIX
        while len(message) > 0:
            message = check_message(message,self_peer_id,connection_table,target_peer_id)
        
        
        # check_message(message,self_peer_id,connection_table,target_peer_id)
        
        
    
    
    
    return



def check_integer(s):
    # our created pattern to check for the integer value
    if re.match('^[+-]?[0-9]+$', s):
        return True
    else:
        return False



def handle_message(message_type,message_payload,connection_table, connected_peer_id, self_peer_id):
    
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
        case 8:
            #Establishing Connection Table Needed for python
            # print("Establishing")
            handle_establishing_message(message_payload,connection_table, connected_peer_id, self_peer_id)
    
    
    
    return


def handle_establishing_message(message_payload, connection_table, connected_peer_id, self_peer_id):
    
    
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
            
            connection_table[1].send(forward_message.encode())
            connection_table[2].send(forward_message.encode())
            
            
            
            # connection_table[1].send(HANDSHAKE_HEADER)
            #Send message to all, forward it to all peers
            # print(connection_table)
            # for cn,connection in connection_table.items():
            #     connection.send(forward_message)
                # print("forwarding")
        else:
            # print("Not forwarding")
            
            # print(message_payload)
            
            if len(message_payload) >= 9:
                peer_id = message_payload[1:5]
                connection_number = message_payload[5:9]
                connection_number = int(connection_number.replace("0", ""))
                
                # print(self_peer_id, connection_number,peer_id)
                
                # connection_table[str(peer_id)] = connection_number
                
                # print(len(connection_table))
                
                # peer_id == 
                
                if str(self_peer_id) == str(peer_id):
                    # print(self_peer_id,connected_peer_id)
                    # print("Establishing Message: ", message_payload, "from",connected_peer_id, "to", self_peer_id)
                    # print(self_peer_id, connected_peer_id,connection_number)
                    # if str(self_peer_id)
                    
                    
                    #
                    # connection_table[str(self_peer_id) + str(connected_peer_id)] = connection_number
                    connection_table[str(connected_peer_id)] = connection_number
                    
                    # print(connection_table)
                    
                        # print(peer_id,connection_number)
                    # connection_table[str(connected_peer_id)] = connection_number
                    # print()
                    
                    
                    # if str(self_peer_id) == '1001':
                    #     # print(connected_peer_id)
                    #     if '1002' in connection_table and '1003' in connection_table:
                    #         print(1001,connection_table['1002'],connection_table['1003']) 
                            
                            
                    # if str(self_peer_id) == '1002':
                    #     # print(connected_peer_id)
                    #     if '1001' in connection_table and '1003' in connection_table:
                    #         print(1002,connection_table['1001'],connection_table['1003']) 
                            
                    # if str(self_peer_id) == '1003':
                    #     # print(connected_peer_id)
                    #     if '1002' in connection_table and '1001' in connection_table:
                    #         print(1003,connection_table['1002'],connection_table['1001']) 
                        # print(connection_table)
                    
                    
                    # if str(self_peer_id) == '1002':
                    #     print(connection_table['1001'],connection_table['1003']) 
                        
                    # if str(self_peer_id) == '1003':
                    #     print(connection_table['1002'],connection_table['1001']) 
                    
                    # print(connection_table)
                    
                    
                    
                    # connection_table[connection_number]
                    # print(connection_table)
                
                # print("Establishing Message: ", message_payload, "from",connected_peer_id, "to", self_peer_id)
                # print("Establishing Message: ", message_payload, "from",connected_peer_id, "to", self_peer_id)
                
                
                # if connected_peer_id == 1002:
                #     print(peer_id, connection_number)
                
                # connection_table[str(peer_id)] = connection_number
                # print(connection_table)

                # print(peer_id,connection_number)
                # connection_table[str(peer_id)] = connection_number
                
            
            
            # connection_table[]
            
            #
            
        # if message_payload[0:1] == '1':
            
        
    
    #What happens if they get stacked up
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


def check_message(message,self_peer_id,connection_table, connected_peer_id):
    
    
    if message != "" and len(message) >= 32:
        # print(message,len(message))
        handshake_header = message[:18]
        # print(handshake_header)
        if handshake_header.decode() == 'P2PFILESHARINGPROJ':
            # print("is handshake")
            zero_bits = message[18:28].decode()
            peer_id = message[28:32].decode()
            
            # print(zero_bits)
            # print(peer_id)
            
            print("Handshake from ", connected_peer_id ,"to", self_peer_id)
            
        
            # TODO
            # print(message)
            #Check peer_id to see if it is correct, then begin accepting messages
            #NEED THE CHECK PEER ID
            #See if the connection is the correct neighbor ie check the header and make sure the peer id is good
            # return ""
            
            # if message[32:] == None:
            #     print("---------------")
            #     # print(len(message))
            #     return ""
            
            #Issue with None Type
            
            
            # return ""
            return message[32:]
    else:
        # print(message)
        if len(message) > 5:
            
            message_length = message[:4].decode()
            message_type = message[4:5].decode()
            
            #Check to see if it is a valid message info
            
            if check_integer(message_length) and check_integer(message_type):
                
                #Make sure the length field and type field are what we expect, and that the message contains the full payload. Reject bad messages
                if int(message_type) < 9 and int(message_length) > 0 and len(message) >= (int(message_length) + 5):
      
                    message_length = int(message_length.replace("0", ""))
                    
                    message_payload = message[5:5+message_length].decode()
                    handle_message(int(message_type), message_payload, connection_table, connected_peer_id, self_peer_id)
                    # print(message_payload)
                
                    return message[5+message_length:]
                else:
                    print("Invalid Msg Length,Invalid Msg Type, or Invalid Msg Payload")
                    return ""
            else:
                print(message)
                print(len(message))
                print("Invalid Msg Length Field or Invalid Msg Type")
                return ""
    


def peer_send_routine(connection, self_peer_id, connection_table, connection_number):
    
    handshake = False
    established = False

    handshake_message = HANDSHAKE_HEADER + b'0000000000' + str(self_peer_id).encode()
    
    fake_message = '00055hello'.encode()
    
    

    


    while True:
        # try:
            # Sending pipeline for messages
            #CHECK initial message header and peer id
            # connection.send(b'Thank you for connecting ' + str(peer_count).encode())
        if handshake == False:
            connection.send(handshake_message)
            # handshake = True
            #Check to make sure peer is correct (handshake is also good on their end)
            
            #Send ACK that it is the correct connection?
            handshake = True
        # connection.send(fake_message)
        # print("sent fake message")
        else:
            # print("hi")
            # connection.send(fake_message)
            # for cn,connection_ in connection_table.items():
            if established == False:
                establishing_message = "000980"
                
                # message_length = 9
                
                # for i in range(0, 4 - len(str(message_length))):
                #     establishing_message += str(0)
                
                # establishing_message += str(message_length)
                
                # establishing_message += str(8)
                # establishing_message += '0'
                establishing_message += str(self_peer_id)
                
                
                for i in range(0, 4 - len(str(connection_number))):
                    establishing_message += str(0)    
                # print(establishing_message)

                
                establishing_message += str(connection_number)
                
                # print(establishing_message)
                    
                connection.send(establishing_message.encode())
                
                established = True
            
            
                
                # print("hi")
                
                
            

        
        time.sleep(1)
        # except:
        #     print("Closing Connection")
        #     connection.close()
        #     break
    
    return




def start_peer(peer_id, port):
    
    
    # connection_table = ConnectionTable()
    connection_table = {}
    
    common_cfg_file = open("project_config_file_small/Common.cfg", "r")
    peer_info_cfg_file = open("project_config_file_small/PeerInfo.cfg", "r")
    
    common_cfg = {}
    peer_cfg = {}
    
    for line in common_cfg_file:
        options = line.split(" ")
        common_cfg[options[0]] = options[1]
        
    for line in peer_info_cfg_file:
        peer_info = line.split(" ")
        peer_cfg[peer_info[0]] = {'ip' : peer_info[1], 'port' : peer_info[2], 'has_file' : peer_info[3]}
    
    #Keep track of the send & recieve threads
    
    
    #Establish Connection to all other peers in peer list
    for peer,info in peer_cfg.items():
        if str(peer) != str(peer_id):
            
            peer_ip = info['ip']
            peer_port = info['port']
            recieve_thread = threading.Thread(target=peer_recieve_routine, args=(peer_ip,peer_port,int(peer),int(peer_id),connection_table,))
            recieve_thread.start()
            print(peer_id,"Connecting to", peer)

    
    
    
    
    
    
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hostName = socket.gethostbyname( '0.0.0.0' )
    s.bind((hostName, port))


    print ("socket binded to %s" %(port))

    # put the socket into listening mode
    s.listen(5)    
    print ("socket is listening")
    connection_count = 1
    while True:

    # Establish connection with client.
        #How to tell what peer the connection is to
        c, addr = s.accept()
        print ('Got connection from', addr)
        
        # connection_table.updateTable(connection_count,c)
        connection_table[connection_count] = c
        
        
        t1 = threading.Thread(target=peer_send_routine, args=(c,peer_id,connection_table, connection_count))
        
        connection_count += 1
        # t2 = threading.Thread(target=peer_recieve_routine, args=(peer_ip,peer_port,peer_id,))
        # print ('Got connection from', addr )
        t1.start()
        # t2.start()