#-*- coding: utf-8 -*-

def get_list_from_file(filename):
    f = open(filename, "r")
    obtained_list = []
    while True:
        line = f.readline()
        line = line.replace('\n', '')
        if not line: break
        obtained_list.append(line)
    f.close()
    return obtained_list