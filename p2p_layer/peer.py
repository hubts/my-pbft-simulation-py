#-*- coding: utf-8 -*-

import os
import psutil
import socket

from . import connection

class Peer:    
    def __init__(self, ip, port):
        self.ip = ip
        self.port = int(port)
        self.socket = self.__make_socket()

    def __make_socket(self, backlog=5):
        """ To construct and prepare a server socket listening on the given port. """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', self.port))
        s.listen(backlog)
        s.settimeout(2)
        return s
    
    def listening(self):
        """ Lisetning the received msg and handling """
        client_sock = self.socket.accept()[0]
        client_sock.settimeout(None)

        host, port = client_sock.getpeername()
        p2p_conn = connection.Connection(host, port, client_sock)
        try:
            msgtype, msgdata = p2p_conn.receive()
        except KeyboardInterrupt:
            self.close()
            return (False, False, False)
        p2p_conn.close()
        opposite_id = "%s:%d" % (host, port)
        return (opposite_id, msgtype, msgdata)

    def sending(self, dest_id, msgtype, msgdata):
        # destination peer id = ip:port
        ip = dest_id.split(":")[0]
        port = dest_id.split(":")[1]
        # try to send
        try :
            p2p_conn = connection.Connection(ip, port)
            p2p_conn.transmit(msgtype, msgdata)
        except KeyboardInterrupt:
            self.close()
            return False
        return True

    def broadcasting(self, dest_id_list, msgtype, msgdata):
        myid = "%s:%d" % (self.ip, self.port)
        for dest_id in dest_id_list:
            if dest_id != myid:
                self.sending(dest_id, msgtype, msgdata)
        return True

    def close(self):
        self.socket.close()
        parent_pid = os.getpid()
        parent = psutil.Process(parent_pid)
        for child in parent.children(recursive=True):
            child.kill()
        return True