#-*- coding: utf-8 -*-
import pickle
import hashlib
import time

def gen_timestamp():
    """ generate a timestamp() """
    return time.time()

def dict_to_bin(dictionary):
    """ dictionary to binary """
    return pickle.dumps(dictionary)

def bin_to_dict(binary):
    """ binary to dictionary """
    return pickle.loads(binary)

def bin_to_str(binary):
    """ binary to string """
    return binary.decode()

def str_to_bin(string):
    """ string to binary """
    return string.encode()

def size_of_dict(dictionary):
    """ get the size of dictionary in bytes? """
    return len(dict_to_bin(dictionary))

def hash256(data):
    """ calculate a hashed data by hashlib """
    t = type(data)
    if t is dict:
        return hashlib.sha256(dict_to_bin(data)).hexdigest()
    elif t is str:
        return hashlib.sha256(str_to_bin(data)).hexdigest()


