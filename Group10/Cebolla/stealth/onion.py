import base64
import json
import random
import stealth
from enum import Enum
from itertools import dropwhile
from stealth import AESProdigy
from stealth import RSAVirtuoso
from Crypto.Random.Fortuna.FortunaGenerator import AESGenerator

PATH_LENGTH = 3

MAX_MESSAGE_SIZE = 4096

class OriginatorSecurityEnforcer(object):
    def __init__(self):
        self.path = []
        self.gens = []
        self.directorySymKey = stealth.get_random_key(16)
        self.directoryGen = AESGenerator()
        self.directoryGen.reseed(self.directorySymKey)
        self.directoryPubKey = None
        self.pubkeys = []

    def set_path(self, pathdata):
        for c in pathdata:
            self.path.append((c["addr"], stealth.get_random_key(16), c["key"]))
        self.gens = [AESGenerator() for i in range(len(self.path))]
        for c in range(len(self.path)):
            self.gens[c].reseed(self.path[c][1])

    def get_path(self):
        return self.path

    # Creates public key encrypted JSON with symkey and next address/port
    # depth is how far in the path the destination onion should be
    # Ex, if you're establishing a connection with the second onion, set depth=2
    # If you are communicating with the directory node, set depth=0
    def create_symkey_msg(self, depth, next_addr, next_port):
        msg = {}
        if depth > 0:
            sym = self.path[depth-1][1]
            pubkey = self.pubkeys[depth-1]
        else:
            sym = self.directorySymKey
            pubkey = self.directoryPubKey
        msg["symkey"] = base64.b64encode(sym).decode('utf-8')
        msg["addr"] = next_addr
        msg["port"] = next_port
        return pubkey.encrypt(json.dumps(msg))

    # Creates symmetric key encrypted message
    # depth is how many onion nodes it will be passed through
    # Set depth=0 if talking to the directory node, depth=1 for the first node in the path...etc
    def create_onion(self, depth, msg):
        ciphertext = msg
        if depth == 0:
            machine = AESProdigy(self.directorySymKey, self.directoryGen.pseudo_random_data(16))
            ciphertext = machine.encrypt(ciphertext)
        else:
            if depth > len(self.path) + 1:
                depth = len(self.path)
            for c in range(depth-2, -1, -1): #Never want to encrypt the destination's message
                machine = AESProdigy(self.path[c][1], self.gens[c].pseudo_random_data(16))
                ciphertext = machine.encrypt(ciphertext)
        return ciphertext

    # Decrypts encryption layers from a response message
    # Depth is how many onion nodes  have encrypted the response
    # Ex, if passed through all onion nodes, depth=amount of nodes in path
    def decipher_response(self, depth, msg):
        if depth < 1:
            machine = AESProdigy(self.directorySymKey, self.directoryGen.pseudo_random_data(16))
            msg = machine.decrypt(msg)
        else:
            for c in range(depth):
                machine = AESProdigy(self.path[c][1], self.gens[c].pseudo_random_data(16))
                msg = machine.decrypt(msg)
        return msg

    def set_pubkeys(self, keys):
        self.pubkeys = keys

class OnionNodeSecurityEnforcer(object):
    def __init__(self):
        self.key = None
        self.rng = AESGenerator()
    
    def set_key(self, key):
        self.key = key
        self.set_seed(key)

    def set_seed(self, seed):
        self.rng.reseed(seed)

    def peel_layer(self, cipher):
        machine = AESProdigy(self.key, self.rng.pseudo_random_data(16))
        return machine.decrypt(cipher)

    def add_layer(self, message):
        machine = AESProdigy(self.key, self.rng.pseudo_random_data(16))
        return machine.encrypt(message)

    def decrypt(self, cipher):
        return self.keypair.decrypt(cipher)

# Temporary until we merge with the directory node code
def dummy_get_onion_circuit():
    path = []
    onions = []
    for i in range(0,PATH_LENGTH):
        k = stealth.get_random_key(16)
        path.append((i, k))
        onion = OnionNodeSecurityEnforcer()
        onion.set_key(k)
        onions.append(onion)
    return (path, onions)


#These functions can be used if we want to implement garbage padding. 
#They aren't being used right now.
def remove_padding(msg):
    for c in range(0, len(msg)):
        if c + 3 <= len(msg):
            if msg[c] == '*' and msg[c+1] == '*' and msg[c+2] == '*':
                return msg[c+3:]
    return msg

def add_padding(msg):
    padding_amount = PATH_LENGTH * MAX_MESSAGE_SIZE - len(msg) - 3
    rand = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz1234567890') for _ in range(0,padding_amount)])
    return rand + '***' + msg
