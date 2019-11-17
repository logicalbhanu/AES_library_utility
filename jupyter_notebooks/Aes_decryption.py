import numpy as np
import math
import Aes_encryption as encryp


Nb=Nk=np.uint8(4)                         # here Nb is the number of columns(32 bit words) in the state arrary and Nk is the number of columns
                                # (32 bit words) in key array, Nk could be 4,6,8 but for this case it is 4

Nr=np.uint8(10)                           # Nr is the number of rounds which is a funciton of Nk and Nb (which is fixed). for this standard Nr = 10
inverse_mixcolumn_const=np.array([14,11,13,9,9,14,11,13,13,9,14,11,11,13,9,14],dtype=np.uint8)
inverse_mixcolumn_const=np.reshape(inverse_mixcolumn_const,(4,4))


# RSbox creation for the Gf(2^8)

r_s_box = np.array([0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3,
                    0x9e, 0x81, 0xf3, 0xd7, 0xfb , 0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f,
                    0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb , 0x54,
                    0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b,
                    0x42, 0xfa, 0xc3, 0x4e , 0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24,
                    0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25 , 0x72, 0xf8,
                    0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d,
                    0x65, 0xb6, 0x92 , 0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda,
                    0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84 , 0x90, 0xd8, 0xab,
                    0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3,
                    0x45, 0x06 , 0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1,
                    0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b , 0x3a, 0x91, 0x11, 0x41,
                    0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6,
                    0x73 , 0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9,
                    0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e , 0x47, 0xf1, 0x1a, 0x71, 0x1d,
                    0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b ,
                    0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0,
                    0xfe, 0x78, 0xcd, 0x5a, 0xf4 , 0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07,
                    0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f , 0x60,
                    0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f,
                    0x93, 0xc9, 0x9c, 0xef , 0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5,
                    0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61 , 0x17, 0x2b,
                    0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55,
                    0x21, 0x0c, 0x7d],dtype=np.uint8)
                                             # this representation is in hexadecimal format so while printing it, we wil get corresponding integers


# most of the lambdas and short methods are here

character_conversion=np.vectorize(chr)       # this is to conver a numpy uint8 array to its unicode containing numpy array

inverse_byte_substitution= np.vectorize(lambda index: r_s_box[index])
                                             # a copy of state_array or array for which subtitution is required should be passed in it.

# all the definitions/methods are here

def encrypted_text_read(filename):
    
    state_array= np.loadtxt(filename,dtype=str,delimiter=" ",encoding="utf-8")[:-1].astype(np.uint8)                  
                                                                        # store them into utf-8 integer encoding in a variable of 8-bit integer.
                                                                        # here is we have no need of padding zeroes at the end because the
                                                                        # filtered input from loadtxt line of code is already in multiple of 16.
    state_array= np.array([np.reshape(i,(4,4)) for i in np.split(state_array,len(state_array)/16)])                        
    return state_array 

def invshiftrows(element):
    temp = np.zeros(element.shape,dtype=np.uint8)
    for r in range(4):
        for j in range(Nb):
            temp[r,(encryp.shift(r,Nb)+j)%Nb]= element[r,j]
    element[:,:]=np.copy(temp)
                    #  don't panic about assignment to value of 'element' reference as it is working absloutely fine, moreover remember that
                    # list are immutable and that they are called by reference in functions and not called by value


#inverse_multiplication_for_matrix(inverse_mixcolumn_const,cipher_input) is the prototype for this
def inverse_multiplication_for_matrix(X,Y):
    # iterate through rows of X
    rough= np.zeros((len(X),len(Y[0])),dtype= np.uint8)
    for i in range(len(X)):
        # iterate through columns of Y
        for j in range(len(Y[0])):
            # iterate through rows of Y
            for k in range(len(Y)):
                if X[i,k]==14:
                    a=b=c=Y[k,j]
                    a= encryp.lefShift_xor(a);a= encryp.lefShift_xor(a);a= encryp.lefShift_xor(a)
                    b= encryp.lefShift_xor(b);b= encryp.lefShift_xor(b)
                    c= encryp.lefShift_xor(c)
                    rough[i,j] = rough[i,j]^(a^b^c)
                    
                if X[i,k]== 9:
                    a=Y[k,j]
                    a= encryp.lefShift_xor(a);a= encryp.lefShift_xor(a);a= encryp.lefShift_xor(a)
                    rough[i,j] = rough[i,j]^(a^Y[k,j])
                    
                if X[i,k]== 13:
                    a=b=Y[k,j]
                    a= encryp.lefShift_xor(a);a= encryp.lefShift_xor(a);a= encryp.lefShift_xor(a)
                    b= encryp.lefShift_xor(b);b= encryp.lefShift_xor(b)
                    rough[i,j] = rough[i,j]^(a^b^Y[k,j])
                
                if X[i,k]==11:
                    a=b=Y[k,j]
                    a= encryp.lefShift_xor(a);a= encryp.lefShift_xor(a);a= encryp.lefShift_xor(a)
                    b= encryp.lefShift_xor(b)
                    rough[i,j] = rough[i,j]^(a^b^Y[k,j])
                                        
    Y[:,:]=rough[:,:]

# the final method to store the output of the decrypted array into a passed filename
def storeOutput(filename,state_array_out):
    char_written_length= 0
    with open(filename, 'w', encoding= 'utf-8') as f:
        for i in state_array_out:
            rowwritten= ''.join(map(chr, np.ravel(i,order='F')))
            char_written_length=char_written_length+len(rowwritten)
            f.write(rowwritten)
    
    return char_written_length


# only the block of cipher should be passed that need to be decrypted and not the whole cipher,containing all the blocks of the cipher

def final_decryption(cipher_input,expanded_key):
    round_number= 10
    encryp.add_round_key(cipher_input,expanded_key[round_number,:,:])
                                 # this has been done because 0 round_key should be added before any processing of the input cipher
    for round_number in range(9,0,-1):
        invshiftrows(cipher_input)
        cipher_input= inverse_byte_substitution(cipher_input)
        encryp.add_round_key(cipher_input,expanded_key[round_number,:,:])
        inverse_multiplication_for_matrix(inverse_mixcolumn_const,cipher_input)
                                 # one more thing that has been done here is that passing only the necessary part of the 
                                 # expanded_key with no passing of round number is needed then(also round_number variable
                                 # should also be used in passing the expanded_key as follows expanded_key[round_number,:,:])

                                 # above is the process for the round 9 to round 1

    round_number= 0
    invshiftrows(cipher_input)
    cipher_input= inverse_byte_substitution(cipher_input)
    encryp.add_round_key(cipher_input,expanded_key[round_number,:,:])
                                # above is the process for the round 10 only

    return cipher_input


# code for creation of state array and performing encryption on all blocks of the cipher created
def creation_everything():
    filename= input("enter the name of the file with path that need to be decrypted")
    encryption_key= input("enter the name of the key file with path that need to decrypt the file, max length of file is 16 characters")
    OutFileName= input("enter the name of the output file with path that is used to store the decrypted output")
    state_array= encrypted_text_read(filename)
    original_key= encryp.input_text_key(encryption_key)
    expanded_key= encryp.keyexpansion(np.copy(original_key))
    state_array_out= np.zeros(state_array.shape,dtype=np.uint8)

                                        
    for index,block in enumerate(state_array):
        state_array_out[index]= final_decryption(np.copy(block),expanded_key)
    
    total_char_wrote= storeOutput(OutFileName,np.copy(state_array_out))
    print(state_array_out)  # for debugging purouse only
    print(encryp.input_text(OutFileName))  # for debugging purouse only

    return np.array_equal(encryp.input_text(OutFileName),state_array_out), total_char_wrote


if __name__=='__main__':

    status,total_char_wrote= creation_everything()
    print(status," ",total_char_wrote)