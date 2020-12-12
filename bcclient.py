#-*- coding: utf-8 -*-
import random
import socket
import sys
import time

import _util
import bc_layer.blockchain as b_blockchain
import bc_layer._params as b_params
import p2p_layer.peer as p_peer

class Bcclient():
    # init: ip, port, ecc_curve
    def __init__(self, 
            ip=socket.gethostbyname(socket.getfqdn()), 
            port=7250,
            ecc_curve=b_params.ecc_curve_default,
            miner_filename="miner_list.txt",
            debug=0
        ):
        # parameter acceptance
        self.id = "%s:%d" % (ip, port)
        self.miner_list = _util.get_list_from_file(miner_filename)
        self.debug = debug

        # # class generation
        self.bc = b_blockchain.Blockchain(self.id, ecc_curve, self.miner_list)
        self.comm = p_peer.Peer(ip, port)

    def print_debug(self, msg):
        if self.debug:
            print("[%s] (Client) %s" % (self.id, msg))

    def main_loop(self):
        # mainloop
        self.print_debug("Main loop started.")
        while True:
            try:
                if self.bc.status != "REQUEST" :
                    time.sleep(1)
                    msg = self.bc.gen_request_msg()
                    self.comm.broadcasting(self.miner_list, "REQU", msg)
                    self.print_debug("Broadcast (REQU) msg")
                # when reply is received
                else:
                    (src_id, msgtype, msgdata) = self.comm.listening()
                    next_action = self.bc.handler[msgtype](src_id, msgdata)

            except KeyboardInterrupt:
                self.comm.close()
                sys.exit()
                break
            except:
                continue