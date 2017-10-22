import json
from enum import Enum

class MessageType(Enum):
    Onion = 1
    Data = 2

class JSONMessage(object):
    def __init__(self, message_type, addr, msg):
        self.s = '{"type": "' + str(message_type) + '", "addr": "' + str(addr) + '", "data": "' + msg + '"}'
    
    def to_string(self):
        return self.s

    def to_dict(self):
        return json.loads(self.s)
