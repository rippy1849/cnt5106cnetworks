import threading
import peer
from datetime import datetime
import time



        
        
        


# exit()

t1 = threading.Thread(target=peer.start_peer, args=(1001,5001,))
t2 = threading.Thread(target=peer.start_peer, args=(1002,5002,))
t3 = threading.Thread(target=peer.start_peer, args=(1003,5003,))
t4 = threading.Thread(target=peer.start_peer, args=(1004,5004,))
t5 = threading.Thread(target=peer.start_peer, args=(1005,5005,))
t6 = threading.Thread(target=peer.start_peer, args=(1006,5006,))
t7 = threading.Thread(target=peer.start_peer, args=(1007,5007,))
t8 = threading.Thread(target=peer.start_peer, args=(1008,5008,))
t9 = threading.Thread(target=peer.start_peer, args=(1009,5009,))
t10 = threading.Thread(target=peer.start_peer, args=(1010,5010,))



t1.start()
t2.start()
t3.start()
t4.start()
t5.start()
t6.start()
t7.start()
t8.start()
t9.start()
t10.start()

# dropped_connection = False


# prev_timestamp = datetime.now().timestamp()
# while dropped_connection == False:
    # current_timestamp = datetime.now().timestamp()
    
    # if (current_timestamp - prev_timestamp) > 10:

time.sleep(5)
# t10._stop.set()
# # dropped_connection = True


time.sleep(5)
# t10.start()
