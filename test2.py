import argparse
import numpy as np
import random
from pathlib import Path
import os



# directory = 'peer_1001'
    
# # piece_files = Path(directory).glob("*.piece")


# file_name = 'output.piece'

# file_path = os.path.join(os.getcwd(), directory, file_name)

# f = open(file_path, "w")
# f.write("Now the file has more content!")
# f.close()


# f = open(file_path)


# total_bytes = 0
# for i,line in enumerate(f):
#     # print(line)
#     if line == '\n':
#         continue
#     # print(len(line),line)
#     total_bytes += len(line)
    
# print(total_bytes)
    
    # if i == 10:
    #     break
    
    
# test = [1,2,3,4]

# test2 = test.copy()

# del test[2]

# print(test,test2)

# print(test.index(2))

# peers_preferred = np.random.choice(test, size=1, replace=False)

# print(peers_preferred[0])


f = open('thefile')


total_bytes = 0
for line in f:
    total_bytes += len(line)
    
print(total_bytes)