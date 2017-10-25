import json
from enum import Enum

class MessageType(Enum):
    Onion = 1
    Data = 2

class JSONMessage(object):
    def __init__(self, message_type, addr, msg):
        self.d = {}
        self.d["data"] = msg
        self.d["addr"] = addr
        self.d["type"] = str(message_type)
    
    def to_string(self):
        return json.dumps(self.d)

    def to_dict(self):
        return self.d