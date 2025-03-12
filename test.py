import threading
import peer

#start a thread for each peer


# string = b"282"


# print(len(string[5:]))

# exit()

t1 = threading.Thread(target=peer.start_peer, args=(1001,5000,))
t2 = threading.Thread(target=peer.start_peer, args=(1002,5001,))
t3 = threading.Thread(target=peer.start_peer, args=(1003,5002,))


t1.start()
t2.start()
t3.start()