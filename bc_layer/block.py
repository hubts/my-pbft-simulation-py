from . import _util

class Block():
    def __init__(self, prev_hash, payload=[], gen_time=_util.gen_timestamp()):
        self.prev_hash = prev_hash
        self.payload = payload # list of dictionary? double dictionary?
        self.merkle_root = self.__make_merkle_root(self.payload)
        self.gen_time = gen_time

    def to_dict(self):
        new_block = {
            'prev_hash': self.prev_hash,
            'merkle_root': self.merkle_root,
            'gen_time': self.gen_time,
            'payload': self.payload
        }
        return new_block

    def __make_merkle_root(self, payload):
        if payload == []:
            return _util.hash256("")
        
        # hashing all transactions in block
        to_merkle_tree = []
        for tx in payload:
            to_merkle_tree.append(_util.hash256(tx))

        while True:
            new_to_merkle_tree = []
            while len(to_merkle_tree) != 0 :
                if len(to_merkle_tree) == 1:
                    block1 = to_merkle_tree.pop()
                    block2 = block1
                else :
                    block1 = to_merkle_tree.pop()
                    block2 = to_merkle_tree.pop()
                hashed_block = _util.hash256(block1 + block2)
                new_to_merkle_tree.append(hashed_block)
            if len(new_to_merkle_tree) == 1 :
                merkle_root = new_to_merkle_tree.pop()
                return merkle_root
            to_merkle_tree = new_to_merkle_tree

    def check_merkle_root(self):
        return self.__make_merkle_root() == self.merkle_root