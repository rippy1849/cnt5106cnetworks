import socket
import signal
import sys
import threading
import time

HANDSHAKE_HEADER = b'P2PFILESHARINGPROJ'



def peer_send_routine(connection, peer_count):
    
    handshake = False
    
    peer_id = '1001'

    handshake_message = HANDSHAKE_HEADER + b'0000000000' + str(peer_id).encode()
    fake_message = '00055hello'.encode()



    while True:
        try:
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
                connection.send(fake_message)
            
            time.sleep(1)
        except:
            connection.close()
            break
    
    return


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


port = 5000

# Next bind to the port
# we have not typed any ip in the ip field
# instead we have inputted an empty string
# this makes the server listen to requests
# coming from other computers on the network

# common_cfg_file = open("project_config_file_small/Common.cfg", "r")
# peer_info_cfg_file = open("project_config_file_small/PeerInfo.cfg", "r")
# # file_to_share_file = open("thefile", "r")

# # Read each line one by one
# common_cfg = {}
# # peer_info_cfg = {}

# for line in common_cfg_file:
#     line_stripped = line.strip()
#     options = line_stripped.split(" ")
#     common_cfg[options[0]] = options[1]
# # Close the file
# common_cfg_file.close()

# for line in peer_info_cfg_file:
#     line_stripped = line.strip()
#     options = line_stripped.split(" ")
#     peer_info_cfg[options[0]] = options[1]
# # Close the file
# peer_info_cfg_file.close()

# print(peer_info_cfg)


hostName = socket.gethostbyname( '0.0.0.0' )
s.bind((hostName, port))


print ("socket binded to %s" %(port))

# put the socket into listening mode
s.listen(5)    
print ("socket is listening")


# exit()
# a forever loop until we interrupt it or
# an error occurs

#NEED A WAY TO ACCEPT AND HOLD MULTIPLE CONNECTIONS
peer_count = 0
while True:

    # Establish connection with client.
    c, addr = s.accept()
    peer_count += 1
    print ('Got connection from', addr )
    
    t1 = threading.Thread(target=peer_send_routine, args=(c,peer_count,))
    # print ('Got connection from', addr )
    t1.start()
    # # send a thank you message to the client.
    # c.send(b'Thank you for connecting')
    
    # Close the connection with the client
    # c.close()