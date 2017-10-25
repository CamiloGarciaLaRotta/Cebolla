import base64
from Crypto.Cipher import AES
from Crypto import Random

BS = 16

# pads plain text such that its length is a multiple of BS.
# the padding character depends on the plain text to increase the difficulty of a known-plaintext attack on the padding
_pad = lambda msg: msg + (BS - len(msg) % BS) * chr(BS - len(msg) % BS).encode()

# removes padding from _pad
_trunc = lambda msg: msg[:-ord(msg[len(msg)-1:])]

#iv = chr(0) * BS #Initialization vector for AES
rand_stream = Random.new() #New stream of random numbers

def get_random_key(nbytes):
    return rand_stream.read(nbytes)

class AESProdigy(object):
    def __init__(self, key, iv):
        self.key = key
        self.iv = iv

    def encrypt(self, message):
        message = message.encode()
        pm = _pad(message)
        machine = AES.new(self.key, AES.MODE_CBC, self.iv)
        cipher = machine.encrypt(pm)
        return base64.b64encode(cipher).decode('utf-8')

    def decrypt(self, cipher):
        cipher = base64.b64decode(cipher)
        machine = AES.new(self.key, AES.MODE_CBC, self.iv)
        pm = machine.decrypt(cipher)
        return _trunc(pm).decode('utf-8')
