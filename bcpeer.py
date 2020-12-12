#-*- coding: utf-8 -*-
import socket
import sys
import time

import _util
import bc_layer.blockchain as b_blockchain
import bc_layer._params as b_params
import p2p_layer.peer as p_peer

class Bcpeer:
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

        # class generation
        self.bc = b_blockchain.Blockchain(self.id, ecc_curve, self.miner_list)
        self.comm = p_peer.Peer(ip, port)

    def print_debug(self, msg):
        if self.debug:
            print("[%s] (v:%d,s:%s) %s" % (self.id, self.bc.view, self.bc.status, msg))

    def main_loop(self):
        # mainloop
        self.print_debug("Main loop started.")
        while True:
            try:
                time.sleep(1)
                if self.bc.isleader_todo():
                    self.print_debug("Leader to do (PPRE)")
                    msg = self.bc.gen_preprepare_msg()
                    self.print_debug("Broadcast --(PPRE)-->> ")
                    self.comm.broadcasting(self.miner_list, "PPRE", msg)
                else:
                    (src_id, msgtype, msgdata) = self.comm.listening()
                    next_action = self.bc.handler[msgtype](src_id, msgdata)
                    if next_action == "PREP":
                        msg = self.bc.gen_prepare_msg()
                        self.print_debug("Broadcast --(PREP)-->> ")
                        self.comm.broadcasting(self.miner_list, "PREP", msg)
                    elif next_action == "COMM":
                        msg = self.bc.gen_commit_msg()
                        self.print_debug("Broadcast --(COMM)-->>")
                        self.comm.broadcasting(self.miner_list, "COMM", msg)
                    elif next_action == "REPL":
                        (requester, msg) = self.bc.gen_reply_msg()
                        self.print_debug("Send --(REPL)--> " + str(requester))
                        self.comm.sending(requester, "REPL", msg)
                        self.bc.round_finish()
            except KeyboardInterrupt:
                self.comm.close()
                sys.exit()
                break
            except:
                continue