import base64
import json
import onion
import random
import stealth
from stealth import RSAVirtuoso
from onion import OriginatorSecurityEnforcer
from onion import OnionNodeSecurityEnforcer

import unittest

# TEST CASE FOR THE ONION LAYERING
# Onion nodes kept in an array in onion.py
# IP addresses/domain names are replaced by the index of the onion node
# For the sake of the test, the message intended for the destination is typed as MessageType.Data, to give the while loop an edge condition

#Obsolete, for now
#class TestOnioning(unittest.TestCase):
#    def test_forward_onion(self):
#        originator = Originator()
#        onions = originator.get_onions()
#        msg = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(0,4096)])
#        packet = originator.create_onion(onion.MessageType.Data, 3,  msg, 'Linus Torvalds', 80)
#
#        d = packet.to_dict()
#        while(True):
#            if d["type"] == "Data":
#                print('========================')
#                print('To: ' + d["addr"])
#                print(d["data"])
#                print('========================')
#                self.assertEqual(d["data"], msg)
#                break
#            addr = int(d["addr"])
#            packet = d["data"]
#            packet = onions[addr].peel_layer(packet)
#            d = packet

class TestPublicKeyCrypto(unittest.TestCase):
    def test_basic_rsa(self):
        keypair = RSAVirtuoso()
        sender = RSAVirtuoso(keypair.get_public_key())
        msg = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(0,256)])
        cipher = sender.encrypt(msg)
        self.assertEqual(keypair.decrypt(cipher), msg)

class TestSymkeyCommunication(unittest.TestCase):
    def test_basic_symkey_message(self):
        addr = 'cs-1.cs.mcgill.ca'
        port = 5551
        originator = OriginatorSecurityEnforcer()
        nodekey = RSAVirtuoso()
        originator.set_pubkeys([RSAVirtuoso(nodekey.key.publickey())])
        msg = originator.create_symkey_msg(1, addr, port)
        data = nodekey.extract_path_data(msg)
        self.assertEqual(data[1], addr)
        self.assertEqual(data[2], port)

class TestDataCommunication(unittest.TestCase):
    def test_basic_data_message(self):
        message = 'Hello, Newman'
        originator = OriginatorSecurityEnforcer()
        node = OnionNodeSecurityEnforcer()
        nodekey = RSAVirtuoso()
        originator.set_pubkeys([RSAVirtuoso(nodekey.key.publickey())])
        msg = originator.create_symkey_msg(1, 'cs-1.cs.mcgill.ca', 5551)
        data = nodekey.extract_path_data(msg)
        node.set_key(data[0])
        ciphertext = originator.create_onion(1, message)
        msg = node.peel_layer(ciphertext)
        self.assertEqual(msg, message)

    def test_basic_message_retrieval(self):
        message = 'Hello, Newman'
        originator = OriginatorSecurityEnforcer()
        nodes = originator.get_onions()
        cipher = message
        for c in range(len(nodes)-1, -1, -1):
            cipher = nodes[c].add_layer(cipher)
        retrieved = originator.decipher_response(cipher)
        self.assertEqual(message, retrieved)

#Obsolete, for now
#class TestEstablishment(unittest.TestCase):
#    def test_basic_establishment(self):
#        nodes = [OnionNode() for _ in range(3)]
#        originator = Originator()
#        originator.set_pubkeys(list(map(lambda x: RSAVirtuoso(x.get_public_key()), nodes)))
#        path = originator.get_path()
#        packet = originator.create_onion(onion.MessageType.Establish, 1, '', 0, 80).to_dict()
#        addr = int(packet["addr"])
#        while packet["type"] != "Establish":
#            packet = packet["data"]
#            packet = nodes[addr].peel_layer(packet)
#            addr = int(packet["addr"])
#        keydata = json.loads(packet["data"])
#        k = base64.b64decode(keydata["symkey"])
#        symkey = nodes[addr].decrypt(k)
#        self.assertEqual(path[addr][1], symkey)

if __name__ == '__main__':
    unittest.main()
