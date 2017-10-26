import jmsg
import json
import random
import stealth
from itertools import dropwhile
from jmsg import JSONMessage
from jmsg import MessageType
from stealth import AESProdigy
from Crypto.Random.Fortuna.FortunaGenerator import AESGenerator

PATH_LENGTH = 3

MAX_MESSAGE_SIZE = 4096

onions = []

class Originator(object):
    def __init__(self):
        self.key = stealth.get_random_key(16);
        self.path = dummy_get_onion_circuit(self.key)
        self.gens = [AESGenerator() for i in range(len(self.path))]
        for c in range(len(self.path)):
            self.gens[c].reseed(self.path[c][1])

    # Creates the full encryption-layered message
    def create_onion(self, msg, dst):
        msg = JSONMessage(MessageType.Data, dst, msg) # Mark the destination message as MessageType.Data for now, just for testing
        for i in range(len(self.path)-1,0,-1): # Cycles list in reverse order
            msg = self.add_layer(msg.to_string(), i, False)
        msg = self.add_layer(msg.to_string(), 0, True)
        return msg

    # Adds another onion layer to a message
    def add_layer(self, msg, node, first):
        machine = AESProdigy(self.path[node][1], self.gens[node].pseudo_random_data(16))
        msg = machine.encrypt(msg)
        if first:
            print('DEBUG: Doing second encryption for innermost layer')
            padding = PATH_LENGTH * MAX_MESSAGE_SIZE - len(msg)
            msg = '0' * padding + msg
            machine = AESProdigy(self.key, chr(0) * 16)
            msg = machine.encrypt(msg)
        return JSONMessage(MessageType.Onion, self.path[node][0], msg)

class OnionNode(object):
    def __init__(self):
        self.key =  ''
        self.prevKey = ''
        self.rng = AESGenerator()
    
    def set_key(self, key):
        self.key = key

    def set_prev_key(self, key):
        self.prevKey = key

    def set_seed(self, seed):
        self.rng.reseed(seed)

    # Decrypts an onion layer to retrieve the underlying JSON for the next layer
    def peel_layer(self, cipher):
        print('DEBUG: Length of cipher = ' + str(len(cipher)))
        machine = AESProdigy(self.prevKey, chr(0) * 16)
        garbage = machine.decrypt(cipher)
        while garbage[0] == '0':
            garbage = garbage[1:]
        machine = AESProdigy(self.key, self.rng.pseudo_random_data(16))
        data = json.loads(machine.decrypt(garbage))
        print('DEBUG: Length of unpadded plaintext = ' + str(len(json.dumps(data))))
        if(data["type"] != "MessageType.Data"): 
            padding = PATH_LENGTH * MAX_MESSAGE_SIZE - len(data["data"])
            print('DEBUG: Amount of padding necessary = ' + str(padding))
            data["data"] = '0' * (padding) + data["data"]
            print('DEBUG: Length of padded plaintext = ' + str(len(json.dumps(data))))
            machine = AESProdigy(self.key, 16 * chr(0).encode())
            data["data"] = machine.encrypt(data["data"])
            print('DEBUG: Length of new ciphertext = ' + str(len(json.dumps(data))))
        return data

# Temporary until we merge with the directory node code
def dummy_get_onion_circuit(key):
    path = []
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
    return path

