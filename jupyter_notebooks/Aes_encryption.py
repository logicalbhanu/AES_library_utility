import numpy as np
import math
import Aes_decryption as decryp
# To use other file variable use the way mentioned below rather than anyother way else
# import file1


Nb=Nk=np.uint8(4)                         # here Nb is the number of columns(32 bit words) in the state arrary and Nk is the number of columns
                                # (32 bit words) in key array, Nk could be 4,6,8 but for this case it is 4

Nr=np.uint8(10)                           # Nr is the number of rounds which is a funciton of Nk and Nb (which is fixed). for this standard Nr = 10

mixcolumn_const=np.array([2,3,1,1,1,2,3,1,1,1,2,3,3,1,1,2],dtype=np.uint8)
mixcolumn_const=np.reshape(mixcolumn_const,(4,4))

rotconst=np.zeros((1,4,4),dtype=np.uint8)
for i in range(4):              # this is the loop to conver the 'rotconst' into required rotation matrix 
    rotconst[0,i,(i+1)%4]=1
                                # as the pattern is always 1+i but when it(i+1) reaches the value of 4 it turns to 0 therefore
                                # use modulus by 4
 
# Sbox creation for the Gf(2^8)

s_box =  np.array([0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67,
         0x2b, 0xfe, 0xd7, 0xab, 0x76, 0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59,
         0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0, 0xb7,
         0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1,
         0x71, 0xd8, 0x31, 0x15, 0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05,
         0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75, 0x09, 0x83,
         0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29,
         0xe3, 0x2f, 0x84, 0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b,
         0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf, 0xd0, 0xef, 0xaa,
         0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c,
         0x9f, 0xa8, 0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc,
         0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2, 0xcd, 0x0c, 0x13, 0xec,
         0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19,
         0x73, 0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee,
         0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb, 0xe0, 0x32, 0x3a, 0x0a, 0x49,
         0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
         0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4,
         0xea, 0x65, 0x7a, 0xae, 0x08, 0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6,
         0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a, 0x70,
         0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9,
         0x86, 0xc1, 0x1d, 0x9e, 0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e,
         0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf, 0x8c, 0xa1,
         0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0,
         0x54, 0xbb, 0x16],dtype=np.uint8)
                                             # this representation is in hexadecimal format so while printing it, we wil get corresponding integers

# most of the lambdas and one liner functions are here

shift = lambda r,Nb: (1 if r== 1 else (2 if r == 2 else (3 if r== 3 else (0 if r==0 else None)))) if Nb == 4 else None

byte_substitution= np.vectorize(lambda index: s_box[index])
                                             # a copy of state_array or array for which subtitution is required should be passed in it.

# calculating the value of x^i for where x = 2 in decimal and the multiplication is abiding the rules of galois field 2^8
lefShift_xor= lambda x : np.uint8(x<<1) if (x<128) else np.uint8(x<<1)^27
                                             # this is equivalent to multiply a number here 'x' with 2 in galois field 2^8
                                             # here i use np.uint8 because python integer is not of 8-bit and bit shift wouldn't work 
                                             # correctly and that is it would drop the bit shifted after 8 bits positions

# methods are all here
# comment for any line of code is listed just below that line at a suitable distance

def input_text(filename):
    
    with open(filename,'r',encoding='utf-8') as f:
        result=list(map(ord,f.read()))
                                                                        # note that 'map' can work only once, so store it result in a varaiable
    state_array= np.array(result, dtype=np.uint8)                  
                                                                        # store them into utf-8 integer encoding in a variable of 8-bit integer.
    
    length= len(state_array)
    padding= length%16
    state_array= np.append(state_array,np.zeros((16-padding)%16).astype(np.uint8)) 
                                                                        # since we don't adding axis here therefore the values of the 
                                                                        # added array will be flattened before use and would then be merged. 
    
    state_array= np.array([np.reshape(i,(4,4)).transpose() for i in np.split(state_array,len(state_array)/16)])                        
    return state_array                                             
         
                                                                        # here each element of the 'state_array' will represent a state array 
                                                                        # for the given text.



def input_text_key(filename):
    
    with open(filename,'r',encoding='utf-8') as f:
        result=list(map(ord,f.read()))
                                                                        # note that 'map' can work only once, so store it result in a varaiable
    state_array= np.array(result, dtype=np.uint8)                  
                                                                        # store them into utf-8 integer encoding in a variable of 8-bit integer.

    length= len(state_array)
    if length >= 16:
        state_array= state_array[:16]
                                                                # here neglecting the rest of the file txt if more than 16 characters
    else:
        padding= length%16
        state_array= np.append(state_array,np.zeros(16-padding).astype(np.uint8))
                                                                # here adding the rest of characters as 0 if have less than 16 
                                                                # character in the input text key file.              
    
    state_array= np.array([np.reshape(state_array,(4,4)).transpose()])                        
    return state_array                                             
                                                                # reshaping the array as a 4x4 matrix and using list to encapsulate it 
                                                                # into another np.array to have the structure similar to the 
                                                                # state_array

def rotkey(roundkey):              # this is the method for applying the left rotation in the given roundkey in total, column wise
    return rotconst.dot(roundkey).transpose()  
                                   # since the rotconst can be used to left rotate a given matrix element column wise hence we apply
                                   # multiplication of the 'roundkey' with rotconst(specifically rotconst with roundkey)


def round_constant(i):
    roundconstant= np.uint8(1)
    for j in range(2,i+1):
                                             # use i because while calling the round_constant function, index of the array is used 
                                             # and which is equal to the round number itself and we want one less than round number as
                                             # as per page 19 and 20 article and sudo code given in nist notes of AES
        roundconstant= lefShift_xor(roundconstant)
        
    return np.array([roundconstant,0,0,0]).reshape(4,1)


def keyexpansion(key):
    
    for index in range(1,11):
        key= np.append(key,np.zeros((1,4,4),dtype=np.uint8),axis=0)
        key[index,:,0]= (key[index-1,:,0].reshape(4,1)^(byte_substitution(rotkey(key[index-1,:,3]))^round_constant(index))).reshape(4)
        key[index,:,1]= key[index,:,0]^key[index-1,:,1]
        key[index,:,2]= key[index,:,1]^key[index-1,:,2]
        key[index,:,3]= key[index,:,2]^key[index-1,:,3]
    
    return key
                    # returning the value here is kind of necessity because we can't use np.append inside a function as it wouldn't 
                    # change the actual passed array beacause we are assigning a new array reference to another object which is "key" 
                    # in this case whereas if we apply np.insert then it do make the changes because it change the actual passed array
                    # reference.

def shiftrows(element):
    temp = np.zeros(element.shape,dtype=np.uint8)
    for r in range(4):
        for j in range(Nb):
            temp[r,(Nb-shift(r,Nb)+j)%Nb]= element[r,j]
    element[:,:]=np.copy(temp)
                    #  don't panic about assignment to value of 'element' reference as it is working absloutely fine, moreover remember that
                    # list are immutable and that they are called by reference in functions and not called by value

    
def multiplication_for_matrix(X,Y):
    # iterate through rows of X
    rough= np.zeros((len(X),len(Y[0])),dtype= np.uint8)
    for i in range(len(X)):
        # iterate through columns of Y
        for j in range(len(Y[0])):
            # iterate through rows of Y
            for k in range(len(Y)):
                if X[i,k]==2:
                    rough[i,j] = rough[i,j]^lefShift_xor(Y[k,j])
                if X[i,k]== 3:
                    rough[i,j] = rough[i,j]^(lefShift_xor(Y[k,j])^Y[k,j])
                if X[i,k]== 1:
                    rough[i,j] = rough[i,j]^Y[k,j]
                    
    Y[:,:]=rough[:,:]
                

def add_round_key(cipher,expanded_key):
    cipher[:,:]= cipher[:,:]^expanded_key[:,:]
    
def storeOutput(filename,state_array_out):
    char_written_length=0
    rowwritten=''
    with open(filename,'w',encoding='utf-8') as f:
        for i in state_array_out:
            rowwritten=' '.join(map(str, np.ravel(i)))
            char_written_length=char_written_length+len(rowwritten.split())
            f.write(rowwritten+' ')
    
    return char_written_length

# only the block of cipher should be passed that need to be ecrypted and not the whole cipher,containing all the blocks of the cipher
def final_encryption(cipher_input,expanded_key):
    round_number= 0
    add_round_key(cipher_input,expanded_key[round_number,:,:])
                                 # this has been done because 0 round_key should be added before any processing of the input cipher
    for round_number in range(1,10):
        cipher_input= byte_substitution(cipher_input)
        shiftrows(cipher_input)
        multiplication_for_matrix(mixcolumn_const,cipher_input)
        add_round_key(cipher_input,expanded_key[round_number,:,:])
                                 # one more thing that has been done here is that passing only the necessary part of the 
                                 # expanded_key with no passing of round number is needed then(also round_number variable
                                 # should also be used in passing the expanded_key as follows expanded_key[round_number,:,:])

                                # above is the process for the round 1 to round 9

    cipher_input= byte_substitution(cipher_input)
    shiftrows(cipher_input)
    round_number= 10
    add_round_key(cipher_input,expanded_key[round_number,:,:])

                                # above is the process for the round 10 only

    return cipher_input

# code for creation of state array and performing encryption on all blocks of the cipher created
def creation_everything():
    filename= input("enter the name of the file with path that need to be encrypted")
    encryption_key= input("enter the name of the key file with path that need to encrypt the file, max length of file is 16 characters")
    OutFileName= input("enter the name of the output file with path that is used to store the encrypted output")
    state_array= input_text(filename)
    original_key= input_text_key(encryption_key)
    expanded_key= keyexpansion(np.copy(original_key))
    state_array_out= np.zeros(state_array.shape,dtype=np.uint8)

                                        
    for index,block in enumerate(state_array):
        state_array_out[index]= final_encryption(np.copy(block),expanded_key)
    
    total_char_wrote= storeOutput(OutFileName,np.copy(state_array_out))

    return np.array_equal(decryp.encrypted_text_read(OutFileName),state_array_out), total_char_wrote
    # below code should only be used for debugging purpose (and before return) as it tells that whether array written to the output file
    # is same as the array read again from the output file
    #print(decryp.encrypted_text_read(OutFileName),"   \n",state_array_out)

    
if __name__=='__main__':

    status,total_char_wrote= creation_everything()
    print(status," ",total_char_wrote)

    