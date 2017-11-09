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

#onions = []

class MessageType(Enum):
    Onion = 1
    Data = 2
    Establish = 3

class OriginatorSecurityEnforcer(object):
    def __init__(self):
        circuit = dummy_get_onion_circuit()
        self.path = circuit[0]
        self.onions = circuit[1]
        self.gens = [AESGenerator() for i in range(len(self.path))]
        for c in range(len(self.path)):
            self.gens[c].reseed(self.path[c][1])
        self.pubkeys = []

    def get_onions(self): # For testing before network only
        return self.onions

    def get_path(self):
        return self.path

    def create_symkey_msg(self, depth, next_addr, next_port):
        msg = {}
        sym = self.path[depth-1][1]
        msg["symkey"] = base64.encodebytes(self.path[depth-1][1]).decode('utf-8')
        msg["addr"] = next_addr
        msg["port"] = next_port
        return self.pubkeys[depth-1].encrypt(json.dumps(msg).encode('utf-8'))

    def create_onion(self, depth, msg):
        ciphertext = msg
        if depth > len(self.path):
            depth = len(self.path)
        for c in range(depth-1, -1, -1):
            machine = AESProdigy(self.path[c][1], self.gens[c].pseudo_random_data(16))
            ciphertext = machine.encrypt(ciphertext)
        return ciphertext

    def decipher_response(self, msg):
        for c in range(len(self.path)):
            machine = AESProdigy(self.path[c][1], self.gens[c].pseudo_random_data(16))
            msg = machine.decrypt(msg)
        return msg

    def set_pubkeys(self, keys):
        self.pubkeys = keys

class OnionNodeSecurityEnforcer(object):
    def __init__(self):
        self.key = None
        self.rng = AESGenerator()
        self.keypair = RSAVirtuoso()
    
    def get_public_key(self):
        return self.keypair.get_public_key()

    def set_key(self, key):
        self.key = key
        self.set_seed(key)

    def set_seed(self, seed):
        self.rng.reseed(seed)

    #Extracts path data from establishment packet
    #Returns tuple: (next address, next port)
    def extract_path_data(self, cipher):
        msg = self.keypair.decrypt(cipher).decode('utf-8')
        msg_dict = json.loads(msg)
        self.set_key(base64.b64decode(msg_dict["symkey"]))
        return (msg_dict["addr"], msg_dict["port"])

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
