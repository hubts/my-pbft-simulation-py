#-*- coding: utf-8 -*-
import pickle

def dict_to_bin(dictionary):
    """ dictionary to binary """
    return pickle.dumps(dictionary)

def bin_to_dict(binary):
    """ binary to dictionary """
    return pickle.loads(binary)