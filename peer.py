import socket
import time
import re
import threading
import os
import math
from datetime import datetime
from multiprocessing import Process, Lock
import random
import numpy as np
from pathlib import Path

# from threading import Thread, Lock
# from multiprocessing import Lock

#TODO Anywhere there is a connection.send, need to wrap it in a connection error handler

#TODO Processes Cannot share data, they make a copy and pass it in. There is a max number of threads allowed, threads are a necessity. 
#TODO Max Number of peers allowed is 10 without slowing down to nothing.

#TODO Remove interested entries in handle_not_interested

HANDSHAKE_HEADER = 'P2PFILESHARINGPROJ'
DOWNLOAD_RATE_WINDOW = 0.5

class Tables:
    def __init__(self):
        self.connection_table = {}
        self.connection_key_table = {}
        self.download_table = {}
        self.piece_list = {}
        # self.preferred_peers = {}
        self.rate_entry = {}
        self.interested_peers = {}
        self.choked_peers = {}
        self.optimistically_unchoked_neighbor = ''
        self.has_file = ''
        self.lock = Lock()
        self.semaphore = 0
        
        self.self_piece_list = []
        
        self.connected_piece_list = {}
        
        self.requested_piece_list = {}
        
        self.self_interested_in_connected_peers = {}
        
        # self.peer_list = []
        # self.current_peer = 0
        
    def getConnectionTable(self):        
        return self.connection_table
    def setConnectionTableEntry(self,entry,value):
        self.connection_table[entry] = value
        
    def getConnectionKeyTable(self):        
        return self.connection_key_table
    def setConnectionKeyTableEntry(self,entry,value):
        self.connection_key_table[entry] = value
           
    def getDownloadTable(self):    
        with self.lock:    
            return self.download_table
    def setDownloadTableEntry(self,entry,value):
        
        with self.lock:
            self.download_table[entry] = value
        
    def resetDownloadTable(self):
        self.download_table = {}
    
    def setRateEntry(self,entry,value):
        self.rate_entry[entry] = value
    def getRateTable(self):
        return self.rate_entry
    
    def setInterestedEntry(self,entry,value):
        
        with self.lock:
            self.interested_peers[entry] = value
        
    def getInterestedTable(self):
        with self.lock:
            return self.interested_peers
    
    def setChokedEntry(self,entry,value):
        with self.lock:
            self.choked_peers[entry] = value
    
    def getChokedTable(self):
        with self.lock:
            return self.choked_peers 
    
    def removeChokedEntry(self,entry):
        del self.choked_peers[entry]
    
    def setOptimisticNeighbor(self,neighbor):
        self.optimistically_unchoked_neighbor = neighbor
    def getOptimisticNeighbor(self):
        return self.optimistically_unchoked_neighbor
    
    def setHasFile(self,value):
        self.has_file = value
    def getHasFile(self):
        return self.has_file
    
    def setPieceList(self, list):
        
        with self.lock:
            self.self_piece_list = list
        
        return
    
    def getPieceList(self):
        with self.lock:
            return self.self_piece_list
        
    
    def getConnectedPiecesList(self):
        with self.lock:
            return self.connected_piece_list
    
    def setConnectedPieceList(self, connected_peer_id, piece_list):
        with self.lock:
            self.connected_piece_list[connected_peer_id] = piece_list
            
    def setRequestedPiece(self, connected_peer_id, requested_piece):
        with self.lock:
            self.requested_piece_list[connected_peer_id] = requested_piece
    
    def getRequestedPieceList(self):
        
        return self.requested_piece_list
    
    def getSelfInterestedTable(self):
        
        return self.self_interested_in_connected_peers
    
    def setSelfInterestedTableEntry(self, connected_peer_id, interested):
        with self.lock:
            self.self_interested_in_connected_peers[str(connected_peer_id)] = interested
        return
    
    def removeSelfInterestedTableEntry(self,connected_peer_id):
        with self.lock:
            if connected_peer_id in self.self_interested_in_connected_peers:
            
                del self.self_interested_in_connected_peers[str(connected_peer_id)]
        
        return
    
    
    
    
    
    # def setPeerList(self,array_list):
    #     self.peer_list = array_list
        
    #     return
    # def nextPeer(self):
        
    #     self.current_peer += 1
        
    #     return
    
    # def getCurrentPeer(self):
    #     return self.peer_list[self.current_peer]
    
    # def getPeerCount(self):
        
    #     return len(self.peer_list)
    # def getPeerCounter(self):
    #     return self.current_peer
    
    # def setPeerCounter(self):
    #     self.current_peer = 0
        
    
        

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


def preferred_peers(tables,self_peer_id,peer_cfg,common_cfg):
    
    prev_timestamp_dl_table = datetime.now().timestamp()
    
    while True:
        
        
        
        file_name = common_cfg['FileName']
        download_table = tables.getDownloadTable()
        
        
        
        number_of_preffered_neighbors = int(common_cfg['NumberOfPreferredNeighbors'])
        top_dl_rate_list = []
        top_rates = []
        peers_preferred = []
        
                
        # if str(self_peer_id) == '1001':
        #     print("hi - 1001", len(download_table))
        
        #TODO Is there a chance a start download message never makes it through? If so, default to 0. Set a timeout here as well? Error later on where start messages
        
        if len(download_table) == (len(peer_cfg)-1)*2:
            prev_timestamp_dl_table = datetime.now().timestamp()
            # log_entry(self_peer_id,'Download Table Populated')
            
            
            # print("Determining Preffered Peers")
            has_file = check_file(file_name,self_peer_id)
            
            if has_file:
                #If peer has the file randomize preferred peers
                error = 1
                peer_list = []
                peers_preferred = []
                
                for peer,value in peer_cfg.items():
                    if str(peer) != str(self_peer_id):
                        peer_list.append(peer)
      
                peers_preferred = np.random.choice(peer_list, size=number_of_preffered_neighbors, replace=False)
                # print(peers_preferred)
       
                download_rate_table = tables.getRateTable()
                choked_table = tables.getChokedTable()
                # print(choked_table)
                connection_table = tables.getConnectionTable()
                connection_key_table = tables.getConnectionKeyTable()
                
                
                # print(self_peer_id,peers_preferred)
                for pref_neighbor in peers_preferred:
                    # if pref_neighbor in choked_table:
                    #Send Unchoke to preffered peers regardless of choke status
                    connection_key = connection_key_table[str(pref_neighbor)]
                    connection = connection_table[connection_key]
                        
                    # print(connection)
                    send_unchoking_message(connection,tables,pref_neighbor)
                
                optimistic_neighbor = tables.getOptimisticNeighbor()
                for key,value in download_rate_table.items():
                    #Make sure not optimistic neighbor, not already choked, and not a preferred peer
                    if key != optimistic_neighbor and (key not in peers_preferred) and key not in choked_table:
                        connection_key = connection_key_table[key]
                        connection = connection_table[connection_key]
                        
                        
                        send_choking_message(connection, tables, key)
                
                
                tables.resetDownloadTable()
            else:
            # print(download_table)
            
                download_rate_table = tables.getRateTable()
                
                
                prev_timestamp = datetime.now().timestamp()
                while len(download_rate_table) < len(peer_cfg)-1:
                    current_timestamp = datetime.now().timestamp()
                    # print("Waiting for Download Rate Table to Populate", len(download_rate_table),current_timestamp - prev_timestamp)
                    download_rate_table = tables.getRateTable()
                    
                    
                    if current_timestamp - prev_timestamp > 1:
                        # print("Timeout - Download Rate Table")
                        for key,value in peer_cfg.items():
                            if str(key) != str(self_peer_id):
                                # print(download_rate_table)
                                if key not in download_rate_table:
                                    #Fill in missing entries with byte-rate that made it through
                                    # print(key)
                                    start_entry = str(key) + '-start'
                                    byte_entry = str(key) + '-bytes'
                                    
                                    start_timestamp = download_table[start_entry]
                                    total_bytes = download_table[byte_entry]
                                    stop_timestamp = datetime.now().timestamp()
                                    
                                    try:
                                        download_rate = total_bytes/(start_timestamp-stop_timestamp)
                                    except:
                                        download_rate = random.randint(0,10)
                                    
                                    tables.setRateEntry(key,download_rate)
                    download_rate_table = tables.getRateTable()
                                
                                
                        
                    
                
                download_rate_table = tables.getRateTable()
                
                interested_table = tables.getInterestedTable()
                
                
                
                try:
                    for key,value in download_rate_table.items():
                        #Check only interested neighbors
                        #Assume if entry not in interested table, peer is not interested (no)
                        if key in interested_table:
                            if interested_table[key] == 'Yes':
                                #Of peers that are interested choose top k
                                top_dl_rate_list.append(value)
                    top_dl_rate_list.sort()
                    
                    size = min(int(number_of_preffered_neighbors),len(top_dl_rate_list))
                    for i in range(len(top_dl_rate_list)-1,len(top_dl_rate_list)-size-1,-1):
                        top_rates.append(top_dl_rate_list[i])
                    
                    for i in range(0,len(top_rates)):
                        for key,value in download_rate_table.items():
                            if value == top_rates[i] and key not in peers_preferred:
                                
                                peers_preferred.append(key)
                                del download_rate_table[key]
                                break
                    #Send unchoke message to all preffered peers
                    #Check which neighbors are choked
                    
                    
                    choked_table = tables.getChokedTable()
                    # print(choked_table)
                    connection_table = tables.getConnectionTable()
                    connection_key_table = tables.getConnectionKeyTable()
                    
                    
                    # print(self_peer_id,peers_preferred)
                    for pref_neighbor in peers_preferred:
                        # if pref_neighbor in choked_table:
                        #Send Unchoke to preffered peers regardless of choke status
                        connection_key = connection_key_table[str(pref_neighbor)]
                        connection = connection_table[connection_key]
                            
                        # print(connection)
                        send_unchoking_message(connection,tables,pref_neighbor)
                    
                    optimistic_neighbor = tables.getOptimisticNeighbor()
                    for key,value in download_rate_table.items():
                        #Make sure not optimistic neighbor, not already choked, and not a preferred peer
                        if key != optimistic_neighbor and key not in peers_preferred and key not in choked_table:
                            connection_key = connection_key_table[key]
                            connection = connection_table[connection_key]
                            
                            
                            send_choking_message(connection, tables, key)
                        
                            
                except:
                    #Sometimes DL rate table not fully populated (error reading download table, size changes)
                    print("Download Table Not Populated")
                
                tables.resetDownloadTable()
        
        # print("hi")
        current_timestamp_dl = datetime.now().timestamp()
        
        
        
        if current_timestamp_dl - prev_timestamp_dl_table > 2 and len(download_table) > 0: 
            
            #Fill in missing entires caused by dropped or corrupted download message
            
            prev_timestamp_dl_table = datetime.now().timestamp()
            
            for peer, value in peer_cfg.items():
                
                if str(peer) != str(self_peer_id):
                    byte_entry = str(peer) + '-bytes'
                    start_entry = str(peer) + '-start'
                    
                    download_table = tables.getDownloadTable()
                    
                    if byte_entry not in download_table:
                        
                        tables.setDownloadTableEntry(byte_entry,random.randint(1,10))
                    
                    if start_entry not in download_table:
                        tables.setDownloadTableEntry(start_entry,prev_timestamp_dl_table)
                    
                
            download_table = tables.getDownloadTable()
            # print(len(download_table))
            # print(download_table)
                    # download_table[start_entry] = prev_timestamp_dl_table
                    
            
                
                
                
            
            # if len(download_table) == 9:
            #     print(download_table)
            #TODO Only fix this in the event download messages don't make it through. If that's the case the connection is broken
               
          
        # download_table = tables.getDownloadTable()
        # print(len(download_table))
    
    return

def timeout_download_rate():
    
    return


def cleanup_logs(self_peer_id):
    
    filepath = os.path.join(os.getcwd(), 'logs', str(self_peer_id) + '_log')
    
    if os.path.exists(filepath):    
        os.remove(filepath)
    
    return


def log_entry(self_peer_id, log_entry):
    
    
    current_timestamp = round(datetime.now().timestamp(),2)
    
    file_name = str(self_peer_id) + '_log'
    
    file_written = False
    while file_written == False:
    
        filepath = os.path.join(os.getcwd(), 'logs', file_name)

        if not os.path.exists(os.path.join(os.getcwd(), 'logs')):
            os.mkdir(os.path.join(os.getcwd(), 'logs'))          
    
        try:
                   
                
            
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
            print(f"File {file_name} is open")
    

def check_file(file_name, self_peer_id):
    
    directory = 'peer_' + str(self_peer_id)
    
    if os.path.exists(os.path.join(os.getcwd(), directory, file_name)):
        # print("Has File =================================================")
        return True
    else:
        return False
    
    return

def determine_requested_piece_index(tables):
    
    requested_piece_list = tables.getRequestedPieceList()
    requested_pieces = []
    
    for peer,req_piece in requested_piece_list.items():
        
        requested_pieces.append(req_piece)
        
    self_pieces_list = tables.getPieceList()
    needed_pieces = []
    # self_pieces_list = self_pieces_table_output.copy()
    
    # print(self_pieces_list)
    for index,has_piece in enumerate(self_pieces_list):
        if has_piece == 0:
            needed_pieces.append(index)
    
    # print(needed_pieces)
    
    for req_piece in requested_pieces:
        if req_piece in needed_pieces:
            index_of_req_piece = needed_pieces.index(req_piece)
            del needed_pieces[index_of_req_piece]
    
    if len(needed_pieces) > 0:
        requested_piece_index = (np.random.choice(needed_pieces, size=1, replace=False))
        requested_piece_index = requested_piece_index[0]
        # print(len(needed_pieces))
    else:
        requested_piece_index = -1
    
    
    
    return requested_piece_index
    
    
    
    
    
        
        
    
    
    
    
    return



def generate_piece_list(tables,self_peer_id,common_cfg,peer_cfg):
    
    piece_list = []
    default_piece_list = []
    
    
    directory = "peer_" + str(self_peer_id)
    #check to see if the directory exists, if not create it
    if not os.path.exists(os.path.join(os.getcwd(), directory)):
        os.mkdir(os.path.join(os.getcwd(), directory))
    
    
    file_name = common_cfg['FileName']
   
   
    piece_size = int(common_cfg['PieceSize'])
    file_size = int(common_cfg['FileSize'])
    
    number_of_pieces = file_size/piece_size
    
    # print(number_of_pieces)
    number_of_pieces_int = int(number_of_pieces)
    total_number_of_pieces = 0
    
    if number_of_pieces != number_of_pieces_int:
        #Float has extra decimal, not a perfect split, need one extra piece for remaining file chunk
        total_number_of_pieces = number_of_pieces_int + 1
    else:
        total_number_of_pieces = number_of_pieces_int
        
    if os.path.exists(os.path.join(os.getcwd(), directory, file_name)):
        for i in range(0,total_number_of_pieces):
            piece_list.append(1)
    else:
        for i in range(0,total_number_of_pieces):
            piece_list.append(0) 
            
    for i in range(0,total_number_of_pieces):
        default_piece_list.append(0)  
        
    for peer, value in peer_cfg.items():
        if str(peer) != str(self_peer_id):
            tables.setConnectedPieceList(str(peer),default_piece_list)
     
    # print(total_number_of_pieces)       
    
             
    
    tables.setPieceList(piece_list) 
        
            
            
        
    return

def binary_to_string(bits):
    return ''.join([chr(int(i, 2)) for i in bits])


def check_integer(s):
    # our created pattern to check for the integer value
    if re.match('^[+-]?[0-9]+$', s):
        return True
    else:
        return False


def cleanup_and_generate_pieces(self_peer_id, common_cfg):
    
    directory = 'peer_' + str(self_peer_id)
    
    piece_files = Path(directory).glob("*.piece")


    file_name = common_cfg['FileName']
    piece_size = int(common_cfg['PieceSize'])
    file_path = os.path.join(os.getcwd(), directory, file_name)

    
    for piece in piece_files:
        os.remove(piece)
    
    
    piece_string = '' 
    total_piece_bytes = 0
    piece_count = 0  
    if os.path.exists(file_path):
        #Generate the piece files
        f = open(file_path)
        
        
        for line in f:
            
            if total_piece_bytes + len(line) < piece_size:
                piece_string += line
                total_piece_bytes += len(line)
        
            else:
                # print("hi")
                remaining_piece = piece_size - total_piece_bytes
                remaining_bytes = line[0:remaining_piece]
                
                piece_string += remaining_bytes
                
                # print(len(piece_string))
                piece_file = str(piece_count) + '.piece'
                piece_path = os.path.join(os.getcwd(), directory, piece_file)
                f2 = open(piece_path, "w")
                f2.write(piece_string)
                f2.close()
                piece_count += 1
                start_of_next_piece = line[remaining_piece:]
                
                piece_string = start_of_next_piece
                total_piece_bytes = len(start_of_next_piece)
                
        if len(piece_string) > 0:
            
            # print("helloooo ================================")
            # piece_count += 1
            piece_file = str(piece_count) + '.piece'
            piece_path = os.path.join(os.getcwd(), directory, piece_file)
            f2 = open(piece_path, "w")
            f2.write(piece_string)
            f2.close()
                
                
                
            
        
    
    
    
    return







def handle_message(message_type,message_payload,tables, connected_peer_id, self_peer_id, peer_cfg,common_cfg, pieces_list):
    
    match message_type:
        case 0:
            #Choke Case
            # print("Choking")
            error = 1 # Need something here to not error
        case 1:
            #Unchoke
            # print("Unchoking")
            handle_unchoking_message(tables, connected_peer_id)
            # log_entry(self_peer_id, 'Unchoking')
        case 2:
            #Interested 
            print("Interested")
            #TODO Sometimes interested message gets dropped. Might have to deal with this
            # log_entry(self_peer_id,'Interested')
            
            handle_interested_message(tables, connected_peer_id)
            
        case 3:
            #Not Interested
            print("Not Interested")
            
            handle_not_interested_message(tables, connected_peer_id)
            # log_entry(self_peer_id,'Not Interested')
        case 4:
            #Have
            # print("Have")
            handle_have_message(tables, self_peer_id,connected_peer_id, message_payload)
        case 5:
            #Bitfield
            print("Bitfield")
            handle_bitfield_message(message_payload,tables,self_peer_id,connected_peer_id)
        case 6:
            #request
            # print("Request")
            handle_request_message(message_payload,self_peer_id,connected_peer_id,tables, peer_cfg)
            # print(len(connection_table))
        case 7:
            #piece
            # print("Piece")
            
            #Check to see the index of the piece
            handle_piece_message(message_payload,tables, connected_peer_id, self_peer_id)
            
            
            # print(message_payload)
            

        case 8:
            #Establishing Connection Table Needed for python
            # print("Establishing")
            # print(message_payload)
            handle_establishing_message(message_payload,tables, connected_peer_id, self_peer_id,peer_cfg)
            
        case 9:
            #Download Rate Message
            # print("Download Rate Message")
            handle_download_rate_message(message_payload,tables,connected_peer_id,self_peer_id,peer_cfg, common_cfg)        
    
            
    
    
    
    return


def handle_piece_message(message_payload, tables, connected_peer_id, self_peer_id):
    
    requested_piece_list = tables.getRequestedPieceList()
    
    # print(connected_peer_id in requested_piece_list)
    
    # print(requested_piece_list)

    connection_table = tables.getConnectionTable()
    connection_key_table = tables.getConnectionKeyTable()
    connection_key = connection_key_table[str(connected_peer_id)]
    connection = connection_table[connection_key]
  
    
    if connected_peer_id in requested_piece_list:
        # print("hi")
        directory = 'peer_' + str(self_peer_id)
        piece_index = requested_piece_list[connected_peer_id]
        piece_file = str(piece_index) + '.piece'
        file_path = os.path.join(os.getcwd(), directory, piece_file)
        
        
        f = open(file_path, "w")
        f.write(message_payload)
        f.close()
        
        # for key,value in connection_key_table.items():
        
        for key,conn in connection_table.items():
            
            send_have_message(conn,piece_index)
            # print(key)
            # print(value)
        
        
        
        
    #         def setPieceList(self, list):
        
    #     with self.lock:
    #         self.self_piece_list = list
        
    #     return
    
    # def getPieceList(self):
    #     with self.lock:
    #         return self.self_piece_list
        
        piece_list = tables.getPieceList()
        piece_list[piece_index] = 1
        tables.setPieceList(piece_list)
    
    #Determine what piece to ask for here
    

    
    requested_piece_index = determine_requested_piece_index(tables)
    
    if requested_piece_index != -1:
    
        send_request_message(tables,connection,requested_piece_index,connected_peer_id)
    
    #send request
    
    
    return


def handle_unchoking_message(tables,connected_peer_id):
    
    connection_table = tables.getConnectionTable()
    connection_key_table = tables.getConnectionKeyTable()
    connection_key = connection_key_table[str(connected_peer_id)]
    connection = connection_table[connection_key]
    
    requested_piece_index = determine_requested_piece_index(tables)
    
    if requested_piece_index != -1:
    
        send_request_message(tables,connection,requested_piece_index, connected_peer_id)
    
    
    return


def handle_have_message(tables, self_peer_id,connected_peer_id,message_payload):
    
    #Send an interested if peer does not have piece.
    
    #TODO Update peer pieces list '1001' [...], '1002' [...] to include a '1' at the correct index
    
    connection_table = tables.getConnectionTable()
    connection_key_table = tables.getConnectionKeyTable()
    
    connection_key = connection_key_table[str(connected_peer_id)]
    
    connection = connection_table[connection_key]


    
    piece_index = int(message_payload)
    
    piece_list = tables.getPieceList()
    
    if piece_list[piece_index] == 0:
        #Send interested message if peer does not have this piece
        
        self_interest_table = tables.getSelfInterestedTable()
        
        if str(connected_peer_id) not in self_interest_table:
            send_interested_message(connection, tables, self_peer_id)
            current_timestamp = datetime.now().timestamp()
            tables.setSelfInterestedTableEntry(str(connected_peer_id),['Yes', current_timestamp])
        
    
    # def getConnectedPiecesList(self):
    #     with self.lock:
    #         return self.connected_piece_list
    
    # def setConnectedPieceList(self, connected_peer_id, piece_list):
    #     with self.lock:
    #         self.connected_piece_list[connected_peer_id] = piece_list
            
    connected_pieces_list = tables.getConnectedPiecesList()
    
    connected_piece_list = connected_pieces_list[str(connected_peer_id)]
    
    connected_piece_list[piece_index] = 1
    
    tables.setConnectedPieceList(str(connected_peer_id),connected_piece_list)
    
    
    #Issue caused by rate limiting. Too many not interested messages overloads the connection. Had to comment out.
    
    interested = False
    for self_piece,conn_piece in zip(piece_list,connected_piece_list):
        
        if self_piece == 0 and conn_piece == 1:
            interested = True
        
    if interested == False:
        
        # current_timestamp = datetime.now().timestamp()
        
        self_interested_table = tables.getSelfInterestedTable()
        
        if str(connected_peer_id) in self_interested_table:
            
            last_message_sent = self_interest_table[str(connected_peer_id)][1]
            
            if current_timestamp - last_message_sent > 1:
                
                send_not_interested_message(connection,tables,self_peer_id)
                tables.removeSelfInterestedTableEntry(str(connected_peer_id))
    
    
    
    #TODO Cannot test this code until piece and request are complete
    
    
    
    
    return


def handle_interested_message(tables, connected_peer_id):
    
    tables.setInterestedEntry(str(connected_peer_id), 'Yes')
    
    return

def handle_not_interested_message(tables, connected_peer_id):
    
    tables.setInterestedEntry(str(connected_peer_id), 'No')
    
    return



def handle_download_rate_message(message_payload,tables, connected_peer_id, self_peer_id,peer_cfg, common_cfg):
    
    
    
    
    if message_payload[0] == '0':
        #Start Junk Download Data
        # print(len(tables.getDownloadTable()))
        # print("Junk Data begin")
        # log_entry(str(self_peer_id),'Junk Download Data Message')
        # current_peer = tables.getCurrentPeer()
        # while str(current_peer) != str(self_peer_id):
        #     current_peer = tables.getCurrentPeer()
            
        #     print(current_peer)

        

        byte_entry = str(connected_peer_id) + "-bytes"
        tables.setDownloadTableEntry(byte_entry,0)

        current_timestamp = datetime.now().timestamp()
        start_entry = str(connected_peer_id) + '-start'
        tables.setDownloadTableEntry(start_entry,current_timestamp)

        # tables.nextPeer()

        connection_key_table = tables.getConnectionKeyTable()
        connection_table = tables.getConnectionTable()
        
        connection_key = connection_key_table[str(connected_peer_id)]
        
        
        connection = connection_table[connection_key]
        # connection = connection_table[connection_table[str(connected_peer_id)]]
        
        
        #Assuming no junk messages made it through, will need this 
        # t = threading.Thread(target=timeout_download_rate, args=(tables,self_peer_id,connected_peer_id))
        # t.start()

        
        #Issue with threads, unfixable the way that threads work. Since we are comparing download rates, this is functionally the same.
        send_junk_message(connection,self_peer_id,connected_peer_id)

        
        
        
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
            
        
    
    #If a stop message is never recieved, likely dropped, stop after fixed time   
    if message_payload[0] == '2':
        # print("Stop Message")
        # log_entry(str(self_peer_id),'Stop Message')
        
        stop_timestamp = datetime.now().timestamp()
        
        download_table = tables.getDownloadTable()
        start_entry = str(connected_peer_id) + '-start'
        byte_entry = str(connected_peer_id) + "-bytes"
        # stop_entry = str(connected_peer_id) + '-stop'
        
        # tables.setDownloadTableEntry(stop_entry, stop_timestamp)
        
        # rate_entry = str(connected_peer_id) + "-rate"
        rate_entry = str(connected_peer_id)
        
        
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
        
        #If bad download rate, randomize so that all peers are possible. Only happens when rate limited
        if download_rate == 0:
            download_rate = random.randint(1, 10)
        
        tables.setRateEntry(rate_entry,download_rate)
        
        
        #TODO Need to do this upon recieving interested entry, in handle_interested. Putting it here to make all interested for testing.
        #TODO Need to do this upon recieving choked, in handle_choke. Remove from table in handle_unchoke
        
        # tables.setInterestedEntry(rate_entry, 'Yes')
        # tables.setChokedEntry(rate_entry, 'Yes')
        
        # dlTable = tables.getDownloadTable()
        # print('Download Rate', dlTable[rate_entry])
        
        # print(dlTable)
    
    
    return



def handle_request_message(message_payload,self_peer_id,connected_peer_id,tables, peer_cfg):
    
    
    connection_table = tables.getConnectionTable()
    connection_key_table = tables.getConnectionKeyTable()
    
    connection_key = connection_key_table[str(connected_peer_id)]
    connection = connection_table[connection_key]
    
    #Upon getting the request message, if not choking, send the piece
    
    choked_table = tables.getChokedTable()
    
    requested_index = int(message_payload)
    
    # print(choked_table)
    if str(connected_peer_id) not in choked_table:
        send_piece(connection,requested_index,self_peer_id)
        
    # piece_index = ""
    # if len(message_payload) >= 4:
    #     piece_index = message_payload[:4]
        
        

    
    
    # connection = connection_table[connection_table[str(connected_peer_id)]]  
    

    # piece = '9u3yry293yr3iurhoewhiofewoijfeo2'
    # piece = 'hello!'
    
    

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



def handle_bitfield_message(message_payload, tables, self_peer_id,connected_peer_id):
    
    res = ''.join(format(ord(i), '08b') for i in message_payload)
    interested = False
    
    connection_table = tables.getConnectionTable()
    connection_key_table = tables.getConnectionKeyTable()
    
    connection_key = connection_key_table[str(connected_peer_id)]
    connection = connection_table[connection_key]
    
    
    # print(res)
    avaliable_list = []
    for chunk,c in enumerate(res):
        if c == '1':
            #might need to make these numbers
            avaliable_list.append(1)
        # else:
            
            
    piece_list = tables.getPieceList()
    tables.setConnectedPieceList(str(connected_peer_id),avaliable_list)
    
    
    # connected_pieces_list = tables.getConnectedPiecesList()
    # print(connected_pieces_list)
    
    # print(len(piece_list),len(avaliable_list))
    
    for piece,avaliable in zip(piece_list,avaliable_list):
        if piece != avaliable:
            # print("Has interesting piece")
            # if str(self_peer_id) == '1001' and str(connected_peer_id) == '1002':
            #     print("Issue here")
            #     print(avaliable_list,piece_list)
            self_interested_table = tables.getSelfInterestedTable()
            
            if str(connected_peer_id) not in self_interested_table:
                send_interested_message(connection, tables, self_peer_id)
            
                current_timestamp = datetime.now().timestamp()
                tables.setSelfInterestedTableEntry(str(connected_peer_id),['Yes',current_timestamp])
            
            
            interested = True
            break
        
    
    if interested == False:
        self_interested_table = tables.getSelfInterestedTable()
        send_not_interested_message(connection, tables,self_peer_id)
        
        self_interested_table = tables.getSelfInterestedTable()
        
        if str(connected_peer_id) in self_interested_table:
            tables.removeSelfInterestedTableEntry(str(connected_peer_id))
            
            
            
    # print(len(avaliable_list))
            
    # print(message_payload,self_peer_id)
    # print(avaliable_list)
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
        
        if len(message) >= 5:
            # print(message)

            
            # print(message_length,message)
            
            # print(decoded_message,message_length,message_type)
            
            # print(message)
            #Check to see if it is a valid message info
            
            
            #There is a very weird issue with utf-16 encoding, need to use it, but causes a bug I can't figure out
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
                
                
                if int(message_type) < 10 and int(message_length) >= 0 and len(message) >= (int(message_length) + 5):
      
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
                    # print(message, int(message[offset:4+offset]),message[4+offset:5+offset])
                    return ""
            else:
                
                print("Invalid Msg Length Field or Invalid Msg Type - 1")
                
                # print(message)
                return ""
        
        print("Invalid Msg Length Field or Invalid Msg Type - 2") 
        print(message)
        return ""
    print("Invalid Msg Length Field or Invalid Msg Type - 3")
    return ""
    

def send_interested_message(connection, tables, self_peer_id):
    
    interested_message = '00002'
    
    # log_entry(self_peer_id, 'Interested')
    
    connection.send(interested_message.encode('utf-16'))
    
    return

def send_not_interested_message(connection, tables, self_peer_id):
    
    not_interested_message = '00003'
    
    connection.send(not_interested_message.encode('utf-16'))
    
    return

def send_unchoking_message(connection, tables, target_peer_id):
    
    unchoking_message = '00001'
    
    
    
    # print(f"Sending Unchoking Message to {target_peer_id}")
    # tables.setChokedEntry(str(target_peer_id), 'No')
    
    connection.send(unchoking_message.encode('utf-16'))
    
    choked_table = tables.getChokedTable()
    
    if target_peer_id in choked_table:
    
        tables.removeChokedEntry(str(target_peer_id))
    
    
    return

def send_choking_message(connection, tables, target_peer_id):
    
    choking_message = '00000'
    
    connection.send(choking_message.encode('utf-16'))
    tables.setChokedEntry(str(target_peer_id), 'Yes')
    
    
    return


#Sends a request message to the desired peer connection for a specific piece index
def send_request_message(tables,connection, piece_index, connected_peer_id):
    
    payload = ""
    
    length_of_piece = len(str(piece_index))
    
    
    for i in range(0,4-length_of_piece):
        payload += '0'
    payload += str(piece_index)
    
    request_message = '00046' + payload
    
    
    # length_of_payload = len(str(payload))
    # length_of_payload = 4
    
    # request_message = ""
    
    # for i in range(0, 4-len(str(length_of_payload))):
    #     request_message += '0'
    
    # request_message += str(length_of_payload)
    # request_message += '6'
    # request_message += payload
    
    
    # print(request_message)
    
    tables.setRequestedPiece(connected_peer_id, piece_index)
    
    connection.send(request_message.encode('utf-16'))  
    
    
    return

def send_piece(connection, piece_index, self_peer_id):
    
    #Assuming message length field is 4 bytes long, we must divide 5 byte int by 2 to fit it in 4 byte length field
    piece_message = ""
    piece_string = ""
    
    
    directory = 'peer_' + str(self_peer_id)
    piece_file = str(piece_index) + '.piece'
    file_path = os.path.join(os.getcwd(), directory, piece_file)
    
    if os.path.exists(file_path):
        #has piece file
        
        f = open(file_path)
        
        for line in f:
            piece_string += line
        
        f.close()
        
        piece_size = len(piece_string)
        
        
        
        
        message_payload_length = piece_size/2
    
        for i in range(0,4-len(str(int(message_payload_length)))):
            piece_message += '0'
    
        piece_message += str(int(message_payload_length))
        
        piece_message += '7'
        
        piece_message += piece_string
        
        # print(len(piece_message))
        

    # print(piece_message)
    
        connection.send(piece_message.encode('utf-16'))
        
        
    # else:
    #     print("Missing Piece File")
    


    
    
    return


def send_have_message(connection, piece_index):
    
    have_message = '00044'
    
    
    piece_index_length = len(str(piece_index))
        
    for i in range(0,4-piece_index_length):
        have_message += "0"
    
    have_message += str(piece_index)
    
    # print(have_message)
    
    connection.send(have_message.encode('utf-16'))
    
    
    
    return


def send_bitfield_message(connection,self_peer_id,common_cfg):
    
    
    #TODO When generating bitfield, might need to check pieces
    
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
        # print(bitfield_message)
        connection.send(bitfield_message.encode('utf-16'))
        
        # encoded = bitfield_message.encode('utf-16')
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
        # time.sleep(0.1)
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
    # message_content = False

    message_recieve_size = (int(common_cfg['PieceSize']) + 5)*4
    

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
        #TODO errors="ignore" to fix byte errors
        decoded_message = message.decode('utf-16', errors='ignore')
        
        # if decoded_message[]
        #Looking for handshake segment
        # print(decoded_message)
        #what if message contains more than one message? NEED TO FIX
        while len(decoded_message) > 0:
            # print(message)
            # copy = decoded_message
            # print(decoded_message)
            
            
            decoded_message = check_message(decoded_message,self_peer_id,tables,target_peer_id, peer_cfg, common_cfg, pieces_list)
            # print(message)
            # prev_timestamp = datetime.now().timestamp()
            #Error here, sometimes returning None, don't know why
            #Might need to fix this, temp fix
            #This might actually work for improperly formatted messages that are returned
            #I'm pretty sure it only returns None when it's improperly formatted
            # if decoded_message == None:
            #     decoded_message = ""
                # print(copy)
            # current_timestamp = datetime.now().timestamp()
        
        
        # #TODO Need to deal with dropped connections. Later.
        # if (current_timestamp - prev_timestamp) > 5:
        #     #It has been 5 seconds since last message, connection likely broke
        #     print("Connection Dropped, attempting to reconnect")
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
    bitfield = False
    # piece_sent = False


    handshake_message = 'P2PFILESHARINGPROJ0000000000' + str(self_peer_id)
    # print(handshake_message)
    # print(handshake_message)
    # handshake_message = HANDSHAKE_HEADER + b'0000000000' + str(self_peer_id).encode('utf-16')
    handshake_message = handshake_message.encode('utf-16')
    
    # print(handshake_message)
    
    # fake_message = '00055hello'.encode()
    # recieve_thread = threading.Thread(target=preferred_peers, args=(tables,peer_cfg,common_cfg,))
    # recieve_thread.start()
    

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
                
            
            #TODO Might need to make sure and wait here to see if all recieved bitfield message
            
            if bitfield == False:
                send_bitfield_message(connection,self_peer_id,common_cfg)
                bitfield = True
            
            
            # if piece_sent == False and str(self_peer_id) == '1001':
            #     send_piece(connection,0,self_peer_id)
            #     piece_sent = True
            
            
            
            current_timestamp = datetime.now().timestamp()
                        
            # print(current_timestamp)
            # print(current_timestamp - prev_timestamp)
            # print(current_timestamp)
            
            #Make this it's own thread to be non-blocking for the optimistic interval, not really necessary given how fast this works
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
                
            # Make this it's own thread to be non-blocking for the choking interval, not really necessary given how fast 
            if current_timestamp - prev_timestamp_optimistic > int(common_cfg['OptimisticUnchokingInterval']):
                
                # print(current_timestamp - prev_timestamp_optimistic, "Optimistic Unchoking " + str(connection_number))
                
                # log_entry(str(self_peer_id)+'_log','Optimistic Unchoking')
                
                
                prev_timestamp_optimistic = current_timestamp
                
                choked_table = tables.getChokedTable()
                interested_table = tables.getInterestedTable()
                
                # print(choked_table)
                
                choked_and_interested = []
                
                # print(choked_table)
                
                for choked_neighbor,value in choked_table.items():
                    if choked_neighbor in interested_table:
                        #Assume no if no entry yet due to no interested or not interested message being sent
                        interested = interested_table[choked_neighbor]
                    else:
                        interested = 'No'
                    
                    # print(interested)
                    
                    if interested == 'Yes':
                        choked_and_interested.append(choked_neighbor)

                # print(choked_and_interested)
                
                if len(choked_and_interested) > 0:
                    random_peer_index = random.randint(0, len(choked_and_interested)-1)
                
                    optimistic_peer = choked_and_interested[random_peer_index]
                    
                    # print(optimistic_peer)
                    connection_table = tables.getConnectionTable()
                    connection_key_table = tables.getConnectionKeyTable()
                    
                    connection_key = connection_key_table[optimistic_peer]
                    connection = connection_table[connection_key]
                    
                    
                    # prev_neighbor = tables.getOptimisticNeighbor()
                    # print(prev_neighbor)
                    send_unchoking_message(connection,tables,optimistic_peer)
                    tables.setOptimisticNeighbor(optimistic_peer)


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
    # peer_list = []
    # for peer,value in peer_cfg.items():
    #     peer_list.append(peer)
        
    # tables.setPeerList(peer_list)
    
    cleanup_and_generate_pieces(peer_id, common_cfg)
    
    generate_piece_list(tables,peer_id,common_cfg, peer_cfg)
    
    # print(len(tables.getPieceList()),'generate piece list')
    
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

    preferred_peer_process = threading.Thread(target=preferred_peers, args=(tables,peer_id,peer_cfg,common_cfg,))
    preferred_peer_process.start()


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