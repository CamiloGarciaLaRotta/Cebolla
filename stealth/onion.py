import stealth
import jmsg
import json
from stealth import AESProdigy
from jmsg import JSONMessage
from jmsg import MessageType

PATH_LENGTH = 3

onions = []

class Originator(object):
    def __init__(self):
        self.path = dummy_get_onion_circuit()

    # Creates the full encryption-layered message
    def create_onion(self, msg, dst):
        msg = JSONMessage(MessageType.Data, dst, msg) # Mark the destination message as MessageType.Data for now, just for testing
        for i in range(len(self.path)-1,-1,-1): # Cycles list in reverse order
            msg = add_layer(msg.to_string(), self.path[i][1], self.path[i][0])
        return msg

class OnionNode(object):
    def __init__(self):
        self.key =  ''
    
    def set_key(self, key):
        self.key = key

    # Decrypts an onion layer to retrieve the underlying JSON for the next layer
    def peel_layer(self, cipher):
        machine = AESProdigy(self.key)
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
        onions.append(onion)
    return path

# Adds another onion layer to a message
def add_layer(msg, key, dst):
    machine = AESProdigy(key)
    msg = machine.encrypt(msg)
    return JSONMessage(MessageType.Onion, dst, msg)
