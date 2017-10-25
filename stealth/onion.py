import stealth
import jmsg
import json
import random
from stealth import AESProdigy
from jmsg import JSONMessage
from jmsg import MessageType
from Crypto.Random.Fortuna.FortunaGenerator import AESGenerator

PATH_LENGTH = 3

onions = []

class Originator(object):
    def __init__(self):
        self.path = dummy_get_onion_circuit()
        self.gens = [AESGenerator() for i in range(len(self.path))]
        for c in range(len(self.path)):
            self.gens[c].reseed(self.path[c][1])

    # Creates the full encryption-layered message
    def create_onion(self, msg, dst):
        msg = JSONMessage(MessageType.Data, dst, msg) # Mark the destination message as MessageType.Data for now, just for testing
        for i in range(len(self.path)-1,-1,-1): # Cycles list in reverse order
            msg = self.add_layer(msg.to_string(), i)
        return msg

    # Adds another onion layer to a message
    def add_layer(self, msg, node):
        machine = AESProdigy(self.path[node][1], self.gens[node].pseudo_random_data(16))
        msg = machine.encrypt(msg)
        return JSONMessage(MessageType.Onion, self.path[node][0], msg)

class OnionNode(object):
    def __init__(self):
        self.key =  ''
        self.rng = AESGenerator()
    
    def set_key(self, key):
        self.key = key

    def set_seed(self, seed):
        self.rng.reseed(seed)

    # Decrypts an onion layer to retrieve the underlying JSON for the next layer
    def peel_layer(self, cipher):
        machine = AESProdigy(self.key, self.rng.pseudo_random_data(16))
        data = json.loads(machine.decrypt(cipher))
        return data

# Temporary until we merge with the directory node code
def dummy_get_onion_circuit():
    path = []
    for i in range(0,PATH_LENGTH):
        k = stealth.get_random_key(16)
        path.append((i, k))
        onion = OnionNode()
        onion.set_key(k)
        onion.set_seed(k)
        onions.append(onion)
    return path

