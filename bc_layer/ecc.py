#-*- coding: utf-8 -*-
import base64
import hashlib
from ecpy.curves        import Curve,Point
from ecpy.keys          import ECPublicKey, ECPrivateKey
from ecpy.ecdsa         import ECDSA
from ecpy.ecrand        import rnd
from Crypto             import Random
from Crypto.Cipher      import AES

class Ecc:
    def __init__(self, curve):
        self.curve_str = curve
        (self.pu_key, self.pv_key, self.curve, self.signer) = self.generate_key(curve)

    def generate_key(self, curve): # curve : curve 이름 
        cv     = Curve.get_curve(curve)
        pv_key = ECPrivateKey(rnd(cv.order), cv)
        pu_key = pv_key.get_public_key()
        return (pu_key, pv_key, cv, ECDSA())

    def generate_key_with_peerid(self, curve, peerid):
        cv     = Curve.get_curve(curve)
        pv_key = ECPrivateKey(peerid, cv)
        pu_key = pv_key.get_public_key()
        return (pu_key, pv_key, cv, ECDSA())

    def ecdh(self, ppu, d): # ppu : 대칭키 상대의 공개키 d: 자신의 공개키
        return ppu * d

    def aes_enc(self, key, msg):
        key = hashlib.sha256(key.encode()).digest()
        iv = Random.new().read(AES.block_size)
        msg = self._pad(msg)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        # return base64.b64encode(iv + cipher.encrypt(msg))
        return iv + cipher.encrypt(msg)

    def aes_dec(self, key, enc):
        key = hashlib.sha256(key.encode()).digest()
        # enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        bs = (len(s)//16 + 1)*16
        return s + ( bs - len(s) % bs) * chr(bs - len(s) % bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

    def generate_pu_key_with_point(self, x, y):
        return ECPublicKey(Point(x, y, self.curve))

# ecc = Ecc('secp256r1')
# encccc = ecc.aes_enc("12455",''.join((ecc.pu_key, "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW", "3")))
# print(encccc)
# deccccc = ecc.aes_dec("12455",encccc)
# print(deccccc)
# print(ecc.signer.verify(hashlib.sha256("123123".encode()).hexdigest().encode(),ecc.signer.sign(hashlib.sha256("123123".encode()).hexdigest().encode(),ecc.pv_key),ecc.pu_key))
