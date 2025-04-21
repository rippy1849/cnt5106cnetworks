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


HANDSHAKE_HEADER = 'P2PFILESHARINGPROJ'


#Holds all shared data between peer connections
class Tables:
    def __init__(self):
        self.connection_table = {}
        self.connection_key_table = {}
        self.download_table = {}
        self.piece_list = {}
        self.rate_entry = {}
        self.interested_peers = {}
        self.choked_peers = {}
        self.optimistically_unchoked_neighbor = ''
        self.has_file = ''
        self.lock = Lock()
        
        self.self_piece_list = []
        
        self.connected_piece_list = {}
        
        self.requested_piece_list = {}
        
        self.self_interested_in_connected_peers = {}
        
        self.total_pieces = 0
        self.current_pieces = 0

        self.who_has_file = {}
        self.everyone_has_file = {}
        
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
        with self.lock:
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
    
    def getTotalPieces(self):
        
        
        return self.total_pieces
    
    def setTotalPieces(self, total_number):
        
        self.total_pieces = total_number
        
        return
    
    def setCurrentPieces(self,current_pieces):
        
        self.current_pieces = current_pieces
    
    def getCurrentPieces(self):
        
        return self.current_pieces
    
    def setWhoHasFile(self, entry, value):
        self.who_has_file[entry] = value
        
        return

    def getWhoHasFile(self):
        
        return self.who_has_file    
    
    def setEveryoneHasFile(self,entry,value):
        self.everyone_has_file[entry] = value
        return
    
    def getEveryoneHasFile(self):
        
        return self.everyone_has_file


def send_message(connection, message, self_peer_id, target_peer_id, i):
    
    try:
        connection.send(message.encode('utf-16'))
    except:
        print(f"Connection Lost {self_peer_id} to {target_peer_id} on {i}")
        return 1
        
    return


def generate_file(self_peer_id,common_cfg, tables):
    
    
    # while True:
    
    directory = 'peer_' + str(self_peer_id)
    
    piece_files = Path(directory).glob("*.piece")

    file_name = common_cfg['FileName']
    total_number_of_pieces = tables.getTotalPieces()
    
    total_pieces = 0
    for piece in piece_files:
        total_pieces += 1
    
    tables.setCurrentPieces(total_pieces)
        
    # print(total_number_of_pieces)
    if total_number_of_pieces == total_pieces:                     
        
        filepath = os.path.join(os.getcwd(), directory, file_name)
        
        
        if not os.path.exists(filepath):
            piece_files = Path(directory).glob("*.piece")
            
            file_string = ""
            for piece in piece_files:
                f = open(piece)
                for line in f:
                    file_string += line
            f2 = open(filepath, 'w')
            f2.write(file_string)
            f.close()
            
        log_entry(self_peer_id, f"Peer {self_peer_id} has downloaded the complete file")
        tables.setWhoHasFile(str(self_peer_id),'Yes')
        
        
    # time.sleep(5)
    
    
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
        
        if len(download_table) == (len(peer_cfg)-1)*2:
            prev_timestamp_dl_table = datetime.now().timestamp()
            
            has_file = check_file(file_name,self_peer_id)
            
            if has_file:
                #If peer has the file randomize preferred peers
                error = 1
                
                # print(f"{self_peer_id} has the file")
                c_table = tables.getConnectionTable()
                
                for _,c in c_table.items():
                    send_download_message(c,3)
                
                tables.setWhoHasFile(str(self_peer_id),'Yes')
                
                who_has_file = tables.getWhoHasFile()
                
                # print(f"{self_peer_id} has {len(who_has_file)} entries")
                
                if len(who_has_file) == len(peer_cfg):
                    tables.setEveryoneHasFile(str(self_peer_id),'Yes')
                    # print(f"{self_peer_id} Knows everyone has file")
                    # send_download_message(c,4)
                    for _,c in c_table.items():
                        send_download_message(c,4)
                    
                    everyone_table = tables.getEveryoneHasFile()
                    
                    if len(everyone_table) == len(peer_cfg):
                        
                        print(f"{self_peer_id} exiting Preferred Peer Routine")
                        exit()
                
                peer_list = []
                peers_preferred = []
                
                for peer,value in peer_cfg.items():
                    if str(peer) != str(self_peer_id):
                        peer_list.append(peer)
      
                peers_preferred = np.random.choice(peer_list, size=number_of_preffered_neighbors, replace=False)
       
                download_rate_table = tables.getRateTable()
                choked_table = tables.getChokedTable()
                connection_table = tables.getConnectionTable()
                connection_key_table = tables.getConnectionKeyTable()
                
                
                p_list = ""
                for p in peers_preferred:
                    p_list += str(p) + " "
                
                log_entry(self_peer_id, f"Peer {self_peer_id} has preferred neighbors {p_list}")
                
                
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
                        for key,value in peer_cfg.items():
                            if str(key) != str(self_peer_id):
                                if key not in download_rate_table:
                                    #Fill in missing entries with byte-rate that made it through
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
                    connection_table = tables.getConnectionTable()
                    connection_key_table = tables.getConnectionKeyTable()
                    
                    p_list = ""
                    for p in peers_preferred:
                        p_list += str(p) + " "
                
                    log_entry(self_peer_id, f"Peer {self_peer_id} has preferred neighbors {p_list}")
                    
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
        
        
        
        if current_timestamp_dl - prev_timestamp_dl_table > int(common_cfg['UnchokingInterval']) and len(download_table) > 0: 
            
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
          
                    



def cleanup_logs(self_peer_id):
    
    file_name = 'log_peer_' + str(self_peer_id) + '.log'
    
    filepath = os.path.join(os.getcwd(), 'logs', file_name)
    
    if os.path.exists(filepath):    
        os.remove(filepath)
    
    return


def log_entry(self_peer_id, log_entry):
    
    
    current_timestamp = round(datetime.now().timestamp(),2)
    
    file_name = 'log_peer_' + str(self_peer_id) + '.log'
    
    file_written = False
    while file_written == False:
    
        filepath = os.path.join(os.getcwd(), 'logs', file_name)

        if not os.path.exists(os.path.join(os.getcwd(), 'logs')):
            os.mkdir(os.path.join(os.getcwd(), 'logs'))          
    
        try:
                   
                
            
            if not os.path.exists(filepath): 
                    
                file = open(filepath, "w")  # write mode
                file.write(f"[{str(current_timestamp)}]: {log_entry}\n")
                file.close()
                file_written = True
            else:

                file = open(filepath, "a")  # append mode
                file.write(f"[{str(current_timestamp)}]: {log_entry}\n")
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
    
    # print(needed_pieces)
    
    # for req_piece in requested_pieces:
    #     if req_piece in needed_pieces:
    #         index_of_req_piece = needed_pieces.index(req_piece)
    #         del needed_pieces[index_of_req_piece]
    
    if len(needed_pieces) > 0:
        requested_piece_index = (np.random.choice(needed_pieces, size=1, replace=False))
        requested_piece_index = requested_piece_index[0]
        # print(len(needed_pieces))
    else:
        requested_piece_index = -1
    
    # print(needed_pieces,requested_piece_index)
    
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
    tables.setTotalPieces(total_number_of_pieces)
    
             
    
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
            log_entry(self_peer_id, f"Peer {self_peer_id} is choked by {connected_peer_id}")
            
            error = 1 # Need something here to not error
        case 1:
            #Unchoke
            # print("Unchoking")
            handle_unchoking_message(tables, connected_peer_id)
            
            log_entry(self_peer_id, f"Peer {self_peer_id} is unchoked by {connected_peer_id}")
        case 2:
            #Interested 
            # print("Interested")
            
            handle_interested_message(tables, connected_peer_id)
            log_entry(self_peer_id, f"Peer {self_peer_id} recieved the 'interested' message from {connected_peer_id}")
            
        case 3:
            #Not Interested
            # print("Not Interested")
            log_entry(self_peer_id, f"Peer {self_peer_id} recieved the 'not interested' message from {connected_peer_id}")
            
            handle_not_interested_message(tables, connected_peer_id)
        case 4:
            #Have
            # print("Have")
            handle_have_message(tables, self_peer_id,connected_peer_id, message_payload)
        case 5:
            #Bitfield
            # print("Bitfield")
            handle_bitfield_message(message_payload,tables,self_peer_id,connected_peer_id)
        case 6:
            #request
            # print("Request")
            handle_request_message(message_payload,self_peer_id,connected_peer_id,tables, peer_cfg)
        case 7:
            #piece
            # print("Piece")
            
            #Check to see the index of the piece
            handle_piece_message(message_payload,tables, connected_peer_id, self_peer_id, common_cfg)
            
            
            

        case 8:
            #Establishing Connection Table Needed for python
            # print("Establishing")
            handle_establishing_message(message_payload,tables, connected_peer_id, self_peer_id,peer_cfg)
            
        case 9:
            #Download Rate Message
            # print("Download Rate Message")
            handle_download_rate_message(message_payload,tables,connected_peer_id,self_peer_id,peer_cfg, common_cfg)        
    
            
    
    
    
    return


def handle_piece_message(message_payload, tables, connected_peer_id, self_peer_id, common_cfg):
    
    requested_piece_list = tables.getRequestedPieceList()


    connection_table = tables.getConnectionTable()
    connection_key_table = tables.getConnectionKeyTable()
    connection_key = connection_key_table[str(connected_peer_id)]
    connection = connection_table[connection_key]
  
    
    if connected_peer_id in requested_piece_list:
        directory = 'peer_' + str(self_peer_id)
        piece_index = requested_piece_list[connected_peer_id]
        piece_file = str(piece_index) + '.piece'
        file_path = os.path.join(os.getcwd(), directory, piece_file)
        
        
        f = open(file_path, "w")
        f.write(message_payload)
        f.close()
        
        total_pieces = tables.getTotalPieces()
        current_pieces = tables.getCurrentPieces()
        
        if current_pieces <= total_pieces:
        
            generate_file(self_peer_id,common_cfg,tables)
        
        
            log_entry(self_peer_id,f"Peer {self_peer_id} has downloaded the piece {piece_index} from {connected_peer_id} the number of pieces it has is {current_pieces}")
        
        
        for key,conn in connection_table.items():
            
            send_have_message(conn,piece_index)

        
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
        # print("Sending Request Message")
        send_request_message(tables,connection,requested_piece_index, connected_peer_id)
    
    
    return


def handle_have_message(tables, self_peer_id,connected_peer_id,message_payload):
    
    #Send an interested if peer does not have piece.
   
    connection_table = tables.getConnectionTable()
    connection_key_table = tables.getConnectionKeyTable()
    
    connection_key = connection_key_table[str(connected_peer_id)]
    
    connection = connection_table[connection_key]


    
    piece_index = int(message_payload)
    
    log_entry(self_peer_id, f"Peer {self_peer_id} recieved the 'have' message from {connected_peer_id} for the piece {piece_index}")
    
    
    piece_list = tables.getPieceList()
    
    if piece_list[piece_index] == 0:
        #Send interested message if peer does not have this piece
        
        self_interest_table = tables.getSelfInterestedTable()
        
        if str(connected_peer_id) not in self_interest_table:
            send_interested_message(connection, tables, self_peer_id)
            current_timestamp = datetime.now().timestamp()
            tables.setSelfInterestedTableEntry(str(connected_peer_id),['Yes', current_timestamp])
        

            
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
        
        current_timestamp = datetime.now().timestamp()
        
        self_interested_table = tables.getSelfInterestedTable()
        
        if str(connected_peer_id) in self_interested_table:
            
            last_message_sent = self_interested_table[str(connected_peer_id)][1]
            
            if current_timestamp - last_message_sent > 1:
                
                send_not_interested_message(connection,tables,self_peer_id)
                tables.removeSelfInterestedTableEntry(str(connected_peer_id))
        
    
    return


def handle_interested_message(tables, connected_peer_id):
    
    tables.setInterestedEntry(str(connected_peer_id), 'Yes')
    
    return

def handle_not_interested_message(tables, connected_peer_id):
    
    tables.setInterestedEntry(str(connected_peer_id), 'No')
    
    return



def handle_download_rate_message(message_payload,tables, connected_peer_id, self_peer_id,peer_cfg, common_cfg):
    
    
    
    
    if message_payload[0] == '0':
 
        byte_entry = str(connected_peer_id) + "-bytes"
        tables.setDownloadTableEntry(byte_entry,0)

        current_timestamp = datetime.now().timestamp()
        start_entry = str(connected_peer_id) + '-start'
        tables.setDownloadTableEntry(start_entry,current_timestamp)


        connection_key_table = tables.getConnectionKeyTable()
        connection_table = tables.getConnectionTable()
        
        connection_key = connection_key_table[str(connected_peer_id)]
        
        
        connection = connection_table[connection_key]
        
        #Issue with threads, unfixable the way that threads work. Since we are comparing download rates, this is functionally the same.
        send_junk_message(connection,self_peer_id,connected_peer_id)

        
        
        
    if message_payload[0] == '1':
        # Calculate Download Rate
        
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
        
        stop_timestamp = datetime.now().timestamp()
        
        download_table = tables.getDownloadTable()
        start_entry = str(connected_peer_id) + '-start'
        byte_entry = str(connected_peer_id) + "-bytes"
        rate_entry = str(connected_peer_id)
        
        
        try:
            start_timestamp = download_table[start_entry]
            total_bytes_transferred = download_table[byte_entry]
        except:
            start_timestamp = 0
            total_bytes_transferred = 0
        
        
        
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
        
        
    if message_payload[0] == '3':
        
        tables.setWhoHasFile(str(connected_peer_id), 'Yes')
        
        whoHasFile = tables.getWhoHasFile()
        
        # print(f"{self_peer_id} has {len(whoHasFile)} entries in who has file")
        
    if message_payload[0] == '4':
        tables.setEveryoneHasFile(str(connected_peer_id), 'Yes')
        
        everyone_table = tables.getEveryoneHasFile()
        
        # print(f"So far, {self_peer_id} has {len(everyone_table)} people know everyone has the file")
        
        
    
    return



def handle_request_message(message_payload,self_peer_id,connected_peer_id,tables, peer_cfg):
    
    
    connection_table = tables.getConnectionTable()
    connection_key_table = tables.getConnectionKeyTable()
    
    connection_key = connection_key_table[str(connected_peer_id)]
    connection = connection_table[connection_key]
    
    #Upon getting the request message, if not choking, send the piece
    
    choked_table = tables.getChokedTable()
    
    requested_index = int(message_payload)
    
    if str(connected_peer_id) not in choked_table:
        send_piece(connection,requested_index,self_peer_id)
        
    
              
    
    return


def handle_establishing_message(message_payload, tables, connected_peer_id, self_peer_id, peer_cfg):

    #Only forward once
       
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
            
            

            num_connections = len(peer_cfg)-1
            
            
            while len(tables.getConnectionTable()) < num_connections:
                print("Waiting for connection table to populate",num_connections,len(tables.getConnectionTable()))
                time.sleep(5)
                
            
            #Should be populated with all connections, but not the actual peers
            for i in range(1,num_connections+1):
                
                connection_table = tables.getConnectionTable()
                connection = connection_table[i]
                connection.send(forward_message.encode('utf-16'))

            
        else:
            
            if len(message_payload) >= 9:
                peer_id = message_payload[1:5]
                connection_number = message_payload[5:9]
                connection_number = int(connection_number.replace("0", ""))
                

                
                if str(self_peer_id) == str(peer_id):
                    tables.setConnectionKeyTableEntry(str(connected_peer_id), connection_number)
                    
    return 



def handle_bitfield_message(message_payload, tables, self_peer_id,connected_peer_id):
    
    res = ''.join(format(ord(i), '08b') for i in message_payload)
    interested = False
    
    connection_table = tables.getConnectionTable()
    connection_key_table = tables.getConnectionKeyTable()
    
    connection_key = connection_key_table[str(connected_peer_id)]
    connection = connection_table[connection_key]
    
    
    avaliable_list = []
    for chunk,c in enumerate(res):
        if c == '1':
            avaliable_list.append(1)
            
            
    piece_list = tables.getPieceList()
    tables.setConnectedPieceList(str(connected_peer_id),avaliable_list)
    
    
    for piece,avaliable in zip(piece_list,avaliable_list):
        if piece != avaliable:
  
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
  
        if len(message) >= 32:
            zero_bits = message[18+offset_handshake:28+offset_handshake]
            peer_id = message[28+offset_handshake:32+offset_handshake]
        
            print("Handshake from ", connected_peer_id ,"to", self_peer_id)
        
        
        
            #return the DECODED message, consistent with size
    
            return message[32+offset_handshake:]
    else:
        
        if len(message) >= 5:
            
            
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
      
                    
                    message_payload = message[5+offset:5+message_length+offset]
                    handle_message(int(message_type), message_payload, tables, connected_peer_id, self_peer_id, peer_cfg,common_cfg, pieces_list)
                    
                        
                    
                    return message[5+message_length +offset:]
                else:
                    print("Invalid Msg Length,Invalid Msg Type, or Invalid Msg Payload")
                    return ""
            else:
                
                print("Invalid Msg Length Field or Invalid Msg Type - 1")
                
                return ""
        
        print("Invalid Msg Length Field or Invalid Msg Type - 2") 
        print(message)
        return ""
    print("Invalid Msg Length Field or Invalid Msg Type - 3")
    return ""
    

def send_interested_message(connection, tables, self_peer_id):
    
    interested_message = '00002'
    
    connection.send(interested_message.encode('utf-16'))
    
    return


def send_not_interested_message(connection, tables, self_peer_id):
    
    not_interested_message = '00003'
    
    connection.send(not_interested_message.encode('utf-16'))
    
    return

def send_unchoking_message(connection, tables, target_peer_id):
    
    unchoking_message = '00001'
    
    
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
        
    
        connection.send(piece_message.encode('utf-16'))
        
    


    
    
    return


def send_have_message(connection, piece_index):
    
    have_message = '00044'
    
    
    piece_index_length = len(str(piece_index))
        
    for i in range(0,4-piece_index_length):
        have_message += "0"
    
    have_message += str(piece_index)
    
    
    connection.send(have_message.encode('utf-16'))
    
    
    
    return


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
   
        
        
        for i in range(0,4-len(str(len(piece_string)))):
            bitfield_message += '0'
        bitfield_message += str(len(piece_string))
        
        bitfield_message += '5'
        bitfield_message += piece_string
 
        connection.send(bitfield_message.encode('utf-16'))
        

    
    
    return



def send_establishing_message(connection,self_peer_id, connection_number):

    establishing_message = "000980"

    establishing_message += str(self_peer_id)
    
    
    for i in range(0, 4 - len(str(connection_number))):
        establishing_message += str(0)    

    
    establishing_message += str(connection_number)
    
        
    connection.send(establishing_message.encode('utf-16')) 
    
    
    return


def send_download_message(connection, message_type):
    
    
    
    
    download_message = '00019' + str(message_type)
    
    connection.send(download_message.encode('utf-16')) 
    
    return
    
def send_junk_message(connection, self_peer_id, target_peer_id):
    
    junk_message = '0032911234567890123456789012345678901' 
    stop_message = '000192'
    
   
    for i in range(0,10):
        error_code = send_message(connection,junk_message,self_peer_id,target_peer_id,i)
        if error_code == 1:
            break
    
    error_code = send_message(connection,stop_message,self_peer_id,target_peer_id,-1)
        
    
    return
    



def peer_recieve_routine(ip,port,target_peer_id,self_peer_id,tables, peer_cfg, common_cfg, pieces_list):
    s = socket.socket()
    connected = False
    
    

    message_recieve_size = (int(common_cfg['PieceSize']) + 5)*4
    

    #Try to connect to host
    while connected == False:
        try:
            s.connect((ip, int(port)))
            # s.connect((ip, int(port)))
            connected = True
            print(self_peer_id,"Connected", target_peer_id)
            log_entry(self_peer_id,f"Peer {self_peer_id} makes a connection to Peer {target_peer_id}")
            log_entry(self_peer_id,f"Peer {self_peer_id} makes a connection from Peer {target_peer_id}")
            
        except:
            print(self_peer_id,"Couldn't Connect To",target_peer_id)
            connected = False

    prev_timestamp = datetime.now().timestamp()

    while True:
    # receive data from the server
        
        everyone_table = tables.getEveryoneHasFile()
            
        if len(everyone_table) == len(peer_cfg):
            # s.shutdown(socket.SHUT_RDWR)
            # print(f"{self_peer_id} has {len(everyone_table)} entries")
            print(f"{self_peer_id} exiting recv routine")
            log_entry(self_peer_id,"Exited Recv Routine")
            exit()
        
        #What if message gets cut off?
        
        #Need to make this the max packet size
        message = s.recv(message_recieve_size)
    
        
  
        decoded_message = message.decode('utf-16', errors='ignore')
        
     
        while len(decoded_message) > 0:
        
            
            
            decoded_message = check_message(decoded_message,self_peer_id,tables,target_peer_id, peer_cfg, common_cfg, pieces_list)
           
        


def peer_send_routine(self_peer_id,tables, connection_number, peer_cfg, common_cfg):
    
    
    
    
    connection_table = tables.getConnectionTable()
    connection = connection_table[connection_number]
    
    handshake = False
    established = False
    connection_table_populated = False
    bitfield = False


    handshake_message = 'P2PFILESHARINGPROJ0000000000' + str(self_peer_id)
  
    handshake_message = handshake_message.encode('utf-16')
    
    prev_timestamp_unchoking = datetime.now().timestamp()
    prev_timestamp_optimistic = datetime.now().timestamp()

    while True:
    
        everyone_table = tables.getEveryoneHasFile()
            
        if len(everyone_table) == len(peer_cfg):
                        
            # print(f"{self_peer_id} has {len(everyone_table)} entries")
            print(f"{self_peer_id} exiting send routine")
            log_entry(self_peer_id,"Exited Send Routine")
            exit()
    
    
        if handshake == False:
            connection.send(handshake_message)
   
            handshake = True
    
        else:
            if established == False:
                send_establishing_message(connection,self_peer_id,connection_number)
                established = True
            
        
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
                
                connection_key_table = tables.getConnectionKeyTable()
                
            
            
            if bitfield == False:
                send_bitfield_message(connection,self_peer_id,common_cfg)
                bitfield = True
            
         
            
            
            
            current_timestamp = datetime.now().timestamp()
                        
           
            
            #Make this it's own thread to be non-blocking for the optimistic interval, not really necessary given how fast this works
            if current_timestamp - prev_timestamp_unchoking > int(common_cfg['UnchokingInterval']):
                
               
                prev_timestamp_unchoking = current_timestamp
                
                whoHasFile = tables.getWhoHasFile()
                if str(self_peer_id) in whoHasFile:
                    # print(f"{self_peer_id} has the file")
                    
                    send_download_message(connection,3)
                    send_download_message(connection,0)
                else:
                    send_download_message(connection,0)
                # print(f"{self_peer_id} has sent download message")
                
                
                
            
            
            
                
            # Make this it's own thread to be non-blocking for the choking interval, not really necessary given how fast 
            if current_timestamp - prev_timestamp_optimistic > int(common_cfg['OptimisticUnchokingInterval']):
                
                
                
                prev_timestamp_optimistic = current_timestamp
                
                choked_table = tables.getChokedTable()
                interested_table = tables.getInterestedTable()
                
                
                choked_and_interested = []
                
                
                for choked_neighbor,value in choked_table.items():
                    if choked_neighbor in interested_table:
                        #Assume no if no entry yet due to no interested or not interested message being sent
                        interested = interested_table[choked_neighbor]
                    else:
                        interested = 'No'
                    
                    
                    if interested == 'Yes':
                        choked_and_interested.append(choked_neighbor)

                
                if len(choked_and_interested) > 0:
                    random_peer_index = random.randint(0, len(choked_and_interested)-1)
                
                    optimistic_peer = choked_and_interested[random_peer_index]
                    
                    connection_table = tables.getConnectionTable()
                    connection_key_table = tables.getConnectionKeyTable()
                    
                    connection_key = connection_key_table[optimistic_peer]
                    connection = connection_table[connection_key]
              
                    send_unchoking_message(connection,tables,optimistic_peer)
                    tables.setOptimisticNeighbor(optimistic_peer)
                    
                    log_entry(self_peer_id,f"Peer {self_peer_id} has the optimistically unchoked neighbor {optimistic_peer}")


        time.sleep(1)
      
    




def start_peer(peer_id, port):
    
    
   
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
    
    
    cleanup_and_generate_pieces(peer_id, common_cfg)
    
    generate_piece_list(tables,peer_id,common_cfg, peer_cfg)
    

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

    # generate_the_file = threading.Thread(target=generate_file, args=(peer_id,common_cfg, tables))
    # generate_the_file.start()

    # exit()
 
    s.listen(5)    
    connection_count = 1
    while True:


        if connection_count == len(peer_cfg):
            print("Exiting Main Process")
            exit()
    # Establish connection with client.
        #How to tell what peer the connection is to
        c, addr = s.accept()
        
        
        
        tables.setConnectionTableEntry(connection_count,c)
   
        
        
        
        t1 = threading.Thread(target=peer_send_routine, args=(peer_id,tables, connection_count, peer_cfg,common_cfg))
        
        connection_count += 1
   
        t1.start()