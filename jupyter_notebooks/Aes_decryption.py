import numpy as np
import math
import Aes_encryption as encryp


# most of the lambdas and short methods are here

character_conversion=np.vectorize(chr)   # this is to conver a numpy uint8 array to its unicode containing numpy array

# all the definitions/methods are here

def encrypted_text_read(filename):
    
    state_array= np.loadtxt(filename,dtype=str,delimiter=" ",encoding="utf-8")[:-1].astype(np.uint8)                  
                                                                        # store them into utf-8 integer encoding in a variable of 8-bit integer.
                                                                        # here is we have no need of padding zeroes at the end because the
                                                                        # filtered input from loadtxt line of code is already in multiple of 16.
    state_array= np.array([np.reshape(i,(4,4)) for i in np.split(state_array,len(state_array)/16)])                        
    return state_array 