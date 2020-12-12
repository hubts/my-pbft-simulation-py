import socket
import struct

from . import _util

class Connection:
    def __init__(self, destination_ip, destination_port, sock=None):
        if not sock:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((destination_ip, int(destination_port)))
        else:
            self.s = sock
        self.sd = self.s.makefile("brw", 0)

    def transmit(self, msgtype, msgdata):
        try:
            # packing the msg
            msgtype = msgtype.encode()
            msgdata = _util.dict_to_bin(msgdata)
            msglen = len(msgdata)
            msg = struct.pack("!4sL%ds" % msglen, msgtype, msglen, msgdata)
            # send the msg
            self.sd.write(msg)
            self.sd.flush()
        except KeyboardInterrupt:
            self.close()
            return False
        except:
            return False
        return True

    def receive(self):
        try:
            msgtype = self.sd.read(4)
            if not msgtype :
                return (None, None)
            lenstr = self.sd.read(4)
            msglen = int(struct.unpack("!L", lenstr)[0])
            msg = b''
            while len(msg) != msglen :
                data = self.sd.read(min(2048, msglen - len(msg)))
                if not len(data) :
                    break
                msg += data
            if len(msg) != msglen :
                return (None, None)
        except KeyboardInterrupt :
            self.close()
            return (None, None)
        except :
            return (None, None)
        msgtype = msgtype.decode()
        msgtype = msgtype.upper()
        msgdata = _util.bin_to_dict(msg)
        return (msgtype, msgdata)

    def close(self):
        self.s.close()
        self.s = None
        self.sd = None