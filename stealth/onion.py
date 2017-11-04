import base64
import jmsg
import json
import random
import stealth
from enum import Enum
from itertools import dropwhile
from jmsg import JSONMessage
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

class Originator(object):
    def __init__(self):
        self.key = stealth.get_random_key(16);
        a = dummy_get_onion_circuit(self.key)
        self.path = a[0]
        self.onions = a[1] # For testing before network only
        self.gens = [AESGenerator() for i in range(len(self.path))]
        for c in range(len(self.path)):
            self.gens[c].reseed(self.path[c][1])
        self.rng = AESGenerator()
        self.rng.reseed(self.key[8:16])
        self.pubkeys = []

    def get_onions(self): # For testing before network only
        return self.onions

    def get_path(self):
        return self.path

    # Creates the full encryption-layered message
    def create_onion(self, mtype, depth, msg, dst, dstPort=80):
        if mtype == MessageType.Data: msg = JSONMessage("Data", dst, msg, dstPort)
        elif mtype == MessageType.Establish: msg = JSONMessage("Establish", dst, self.create_symkey_msg(depth), dstPort)
        for i in range(depth-1,0,-1): # Cycles list in reverse order
            msg = self.add_layer(msg.to_string(), i, False)
        if(mtype == MessageType.Data): msg = self.add_layer(msg.to_string(), 0, True)
        return msg

    # Adds another onion layer to a message
    def add_layer(self, msg, node, first):
        machine = AESProdigy(self.path[node][1], self.gens[node].pseudo_random_data(16))
        msg = machine.encrypt(msg)
        if first:
            padding = PATH_LENGTH * MAX_MESSAGE_SIZE - len(msg)
            msg = add_padding(msg)
            machine = AESProdigy(self.key, self.rng.pseudo_random_data(16))
            msg = machine.encrypt(msg)
        return JSONMessage("Onion", self.path[node][0], msg)

    def create_symkey_msg(self, depth):
        msg = {}
        sym = self.path[depth-1][1]
        enc_sym = self.pubkeys[depth-1].encrypt(sym)
        msg["symkey"] = base64.encodestring(enc_sym[0]).decode('utf-8')
        if(depth == 1): msg["prevKey"] = base64.encodestring(self.pubkeys[depth-1].encrypt(self.key)[0]).decode('utf-8')
        else: msg["prevKey"] = base64.encodestring(self.pubkeys[depth-1].encrypt(self.path[depth-2][1])[0]).decode('utf-8')
        return json.dumps(msg)

    def set_pubkeys(self, keys):
        self.pubkeys = keys

class OnionNode(object):
    def __init__(self):
        self.key = None
        self.prevKey = None
        self.rng = AESGenerator()
        self.prevrng = AESGenerator()
        self.nextrng = AESGenerator()
        self.keypair = RSAVirtuoso()
    
    def get_public_key(self):
        return self.keypair.get_public_key()

    def set_key(self, key):
        self.key = key
        self.nextrng.reseed(self.key[8:16])

    def set_prev_key(self, key):
        self.prevKey = key
        self.prevrng.reseed(key[8:16])

    def set_seed(self, seed):
        self.rng.reseed(seed)

    # Decrypts an onion layer to retrieve the underlying JSON for the next layer
    def peel_layer(self, cipher):
        machine = AESProdigy(self.prevKey, self.prevrng.pseudo_random_data(16))
        garbage = machine.decrypt(cipher)
        garbage = remove_padding(garbage)
        machine = AESProdigy(self.key, self.rng.pseudo_random_data(16))
        data = json.loads(machine.decrypt(garbage))
        if(data["type"] == "Onion"): 
            padding = PATH_LENGTH * MAX_MESSAGE_SIZE - len(data["data"])
            data["symkey"] = self.key
            data["data"] = add_padding(data["data"])
            machine = AESProdigy(self.key, self.nextrng.pseudo_random_data(16))
            data["data"] = machine.encrypt(data["data"])
        elif(data["type"] == "Establish"):
            self.set_prev_key(data["symkey"])
            self.set_key(self.keypair.decrypt(data["data"]))
        return data

    def decrypt(self, cipher):
        return self.keypair.decrypt(cipher)

# Temporary until we merge with the directory node code
def dummy_get_onion_circuit(key):
    path = []
    onions = []
    for i in range(0,PATH_LENGTH):
        k = stealth.get_random_key(16)
        path.append((i, k))
        onion = OnionNode()
        onion.set_key(k)
        onion.set_seed(k)
        if i == 0:
            onion.set_prev_key(key)
        else:
            onion.set_prev_key(path[i-1][1])
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
