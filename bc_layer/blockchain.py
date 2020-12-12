#-*- coding: utf-8 -*-
from . import _util
from . import _params
from . import ecc
from . import block

class Blockchain():
    def __init__(self, id, ecc_curve=_params.ecc_curve_default, miner_list=[]):
        self.id = id
        self.debug = 1
        self.miner_list = miner_list
        self.ecc = ecc.Ecc(ecc_curve)
        
        # storage settings
        self.txpool = [] # list of request msg
        self.ledger = [
            block.Block(prev_hash=_util.hash256(_params.genesis_block_seed), gen_time=0).to_dict()
        ]
        
        # consensus settings
        self.view = 0
        self.status = None
        self.leader = None

        # Processing
        self.request_msg = None
        self.requester_id = None
        self.preprepare_msg = None
        self.prepare_msgs = []
        self.commit_msgs = []
        self.reply_msgs = [] # for the client

        # handlers
        self.handler = {
            "REQU": self.handler_request,
            "PPRE": self.handler_preprepare,
            "PREP": self.handler_prepare,
            "COMM": self.handler_commit,
            "REPL": self.handler_reply
        }

    def print_debug(self, msg):
        if self.debug:
            print("[%s] (v:%d,s:%s) %s" % (self.id, self.view, self.status, msg))

    def isleader_todo(self):
        # view % num of miners = leader
        if self.leader == None:
            leader_index = self.view % len(self.miner_list)
            self.leader = self.miner_list[leader_index]
        return (self.id == self.leader) and (self.status == None) and (len(self.txpool) > 0)

    def round_finish(self):
        accepted_block = self.preprepare_msg["m"]
        self.ledger.append(accepted_block)
        accepted_txs = accepted_block["payload"]
        for tx in accepted_txs:
            if tx in self.txpool:
                self.txpool.remove(tx)
            else:
                self.print_debug("Error: no same transactions")
        self.view += 1

        self.request_msg = None
        self.requester_id = None
        self.preprepare_msg = None
        self.prepare_msgs = []
        self.commit_msgs = []
        self.reply_msgs = []

        self.status = None
        self.leader = None

        self.print_debug("Round is finished, Status: " + str(self.status) + ", Now View: " + str(self.view))

    def get_last_block_prev_hash(self):
        # prev_hash
        last_block = self.ledger[len(self.ledger)-1]
        del last_block["payload"]
        prev_hash = _util.hash256(last_block) # without payload = header
        return prev_hash

    def get_txpool_one(self):
        return [self.txpool[0]]

    def get_txpool_max_block_size(self, prev_hash):
        txs = []
        new_block = block.Block(prev_hash, txs)
        current_size = _util.size_of_dict(new_block.to_dict())
        residual_size = _params.max_block_size - current_size

        max_count_tx = 0
        for tx in self.txpool:
            tx_size = _util.size_of_dict(tx)
            if residual_size - tx_size >= 0:
                residual_size = residual_size - tx_size
                max_count_tx = max_count_tx + 1
            else:
                break
        
        txs = []
        for _ in range(max_count_tx):
            txs.append(self.txpool.pop())
        return txs

    def gen_request_msg(self):
        """ for a client to broadcast the request msg(transaction) """
        msg = {}
        msg["client"] = self.id
        msg["m"] = "EXAMPLE TRANSACTION"
        msg["t"] = _util.gen_timestamp()

        self.status = "REQUEST"
        return msg

    def gen_preprepare_msg(self):
        """ Only leader generates a (PPRE) msg in a View """
        """ The status of the leader will go through (PREP) """
        msg = {}
        msg["status"] = "PREPREPARE"
        msg["v"] = self.view
        msg["n"] = 1
        
        prev_hash = self.get_last_block_prev_hash()
        txs = self.get_txpool_one() # self.get_txpool_max_block_size(prev_hash)
        new_block = block.Block(prev_hash, txs) # error
        msg["m"] = new_block.to_dict()

        self.status = "PREPARE"
        self.preprepare_msg = msg # for leader, preprepare_msg is prepared
        return msg

    def gen_prepare_msg(self):
        msg = {}
        msg["status"] = "PREPARE"
        msg["v"] = self.view
        msg["d(m)"] = _util.hash256(self.preprepare_msg)
        msg["n"] = self.preprepare_msg["n"]
        msg["i"] = self.id

        self.status = "PREPARE"
        self.prepare_msgs.append(msg) # my msg
        return msg
    
    def gen_commit_msg(self):
        msg = {}
        msg["status"] = "COMMIT"
        msg["v"] = self.view
        msg["d(m)"] = _util.hash256(self.preprepare_msg)
        msg["n"] = self.preprepare_msg["n"]
        msg["i"] = self.id

        self.status = "COMMIT"
        self.commit_msgs.append(msg) # my msg
        return msg

    def gen_reply_msg(self):
        msg = {}
        msg["status"] = "REPLY"
        msg["v"] = self.view
        msg["n"] = self.preprepare_msg["n"]
        msg["i"] = self.id

        self.status = "REPLY"
        requester = self.requester_id
        return (requester, msg)

    def handler_request(self, src_id, msgdata):
        self.requester_id = msgdata["client"]
        self.request_msg = msgdata
        self.txpool.append(msgdata)
        self.print_debug("Received (REQU) from " + str(self.requester_id))
        return True

    def handler_preprepare(self, src_id, msgdata):
        self.print_debug("Received (PPRE) from " + str(self.leader))
        def verify_txs(txs):
            return True

        def verify_preprepare(self, msgdata):
            # msg checking
            if msgdata["status"] != "PREPREPARE":
                return False
            elif msgdata["v"] != self.view:
                return False
            
            # block checking
            last_block = self.ledger[len(self.ledger)-1]
            del last_block["payload"]
            prev_hash = _util.hash256(last_block) # without payload = header

            if msgdata["m"]["prev_hash"] != prev_hash:
                return False
            elif msgdata["m"]["gen_time"] >= _util.gen_timestamp():
                return False
            elif not verify_txs(msgdata["m"]["payload"]):
                return False

            return True

        if verify_preprepare(self, msgdata):
            self.preprepare_msg = msgdata
            self.requester_id = msgdata["m"]["payload"][0]["client"] # 1 transaction is in it
            return "PREP"
        else:
            return False
    
    def handler_prepare(self, src_id, msgdata):
        self.print_debug("Received (PREP) from " + str(msgdata["i"]))
        def verify_prepare(self, msgdata):
            if msgdata["status"] != "PREPARE":
                return False
            elif msgdata["v"] != self.view:
                return False
            elif msgdata["d(m)"] != _util.hash256(self.preprepare_msg):
                return False
            return True

        if verify_prepare(self, msgdata) and (self.status == "PREPARE"):
            self.prepare_msgs.append(msgdata)
            if len(self.prepare_msgs) > int((_params.fault_factor * (len(self.miner_list)-1))) and (self.status == "PREPARE"):
                self.status = "PREPARED"
                return "COMM"
            else:
                return False
        else:
            return False
    
    def handler_commit(self, src_id, msgdata):
        self.print_debug("Received (COMM) from " + str(msgdata["i"]))
        def verify_commit(self, msgdata):
            if msgdata["status"] != "COMMIT":
                return False
            elif msgdata["v"] != self.view:
                return False
            elif msgdata["d(m)"] != _util.hash256(self.preprepare_msg):
                return False
            return True

        if verify_commit(self, msgdata) and (self.status == "COMMIT"):
            self.commit_msgs.append(msgdata)
            if len(self.commit_msgs) > int((_params.fault_factor * (len(self.miner_list)-1))) and (self.status == "COMMIT"):
                self.status = "COMMITTED"
                return "REPL"
            else:
                return False
        else:
            return False

    def handler_reply(self, src_id, msgdata):
        self.print_debug("(Client) Received (REPL) from " + str(msgdata["i"]))
        if self.status == "REQUEST" and self.view == msgdata["v"]:
            self.reply_msgs.append(msgdata)
            if len(self.reply_msgs) > int((_params.fault_factor * (len(self.miner_list)-1))):
                self.view += 1
                self.reply_msgs = []
                self.status = None
                self.print_debug("Round is finished, Status: " + str(self.status) + ", Now View: " + str(self.view))
                return "REQU"
            else:
                return False
        else:
            return False
