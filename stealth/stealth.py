import base64
import json
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.PublicKey import RSA

RSA_KEY_SIZE = 2048

#Block Size for AES
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

class RSAVirtuoso(object):
    def __init__(self, key=None):
        if(key is None): self.key = RSA.generate(RSA_KEY_SIZE)
        else: self.key = key
    
    def get_public_key(self):
        return self.key.publickey()

    def encrypt(self, msg):
        return base64.b64encode(self.key.encrypt(msg.encode('utf-8'), 742072781)[0]).decode('utf-8')

    def decrypt(self, cipher):
        return self.key.decrypt(base64.b64decode(cipher)).decode('utf-8')

    #Extracts symmetric key, next node address, and next node port from RSA-encrypted establishment packet
    #Returns (symkey, addr, port)
    def extract_path_data(self, cipher):
        msg = self.decrypt(cipher)
        msg_dict = json.loads(msg)
        symkey = base64.b64decode(msg_dict["symkey"])
        addr = msg_dict["addr"]
        port = msg_dict["port"]
        return (symkey, addr, port)
