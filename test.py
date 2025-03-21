import threading
import peer

def binary_to_string(bits):
    return ''.join([chr(int(i, 2)) for i in bits])
   
# Driver Code
 
# This is the binary equivalent of string "GFG"
# bin_values = ['01101011', '01101011'] 
 
# # calling the function
# # and storing the result in variable 's'
# s = binary_to_string(bin_values)


# s = '0009'
# print(int(s))
# print(s)

# test_number = 1.2
# print(int(test_number))

# print(len('P2PFILESHARINGPROJ'))

# string = 'testString'

# print(string[0:1])
piece = '9u3yry293yr3iurhoewhiofewoijfeo'

# print(len(piece))

# exit()

t1 = threading.Thread(target=peer.start_peer, args=(1001,5000,))
t2 = threading.Thread(target=peer.start_peer, args=(1002,5001,))
t3 = threading.Thread(target=peer.start_peer, args=(1003,5002,))


t1.start()
t2.start()
t3.start()