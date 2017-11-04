import json

class JSONMessage(object):
    def __init__(self, message_type, addr, msg, port=80):
        self.d = {}
        self.d["data"] = msg
        self.d["addr"] = addr
        self.d["type"] = str(message_type)
        self.d["port"] = port
    
    def to_string(self):
        return json.dumps(self.d)

    def to_dict(self):
        return self.d
