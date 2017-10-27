import base64
import json
import onion
import random
import stealth
from stealth import RSAVirtuoso
from onion import Originator
from onion import OnionNode

import unittest

# TEST CASE FOR THE ONION LAYERING
# Onion nodes kept in an array in onion.py
# IP addresses/domain names are replaced by the index of the onion node
# For the sake of the test, the message intended for the destination is typed as MessageType.Data, to give the while loop an edge condition

class TestOnioning(unittest.TestCase):
    def test_forward_onion(self):
        originator = Originator()
        onions = originator.get_onions()
        msg = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(0,4096)])
        packet = originator.create_onion(onion.MessageType.Data, 3,  msg, 'Linus Torvalds')
#        print('Originator creates:')
#        print(packet.to_dict())
#        print('')

        d = packet.to_dict()
        while(True):
            if d["type"] == "Data":
                print('========================')
                print('To: ' + d["addr"])
                print(d["data"])
                print('========================')
                self.assertEqual(d["data"], msg)
                break
            addr = int(d["addr"])
            packet = d["data"]
#            print('Node ' + str(addr) + ' receives packet of length ' + str(len(packet)))
            packet = onions[addr].peel_layer(packet)
#            print('Node ' + str(addr) + ' creates:')
#            print(packet)
#            print('')
            d = packet

class TestPublicKeyCrypto(unittest.TestCase):
    def test_basic_rsa(self):
        keypair = RSAVirtuoso()
        sender = RSAVirtuoso(keypair.get_public_key())
        msg = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(0,256)])
        cipher = sender.encrypt(msg)
        self.assertEqual(keypair.decrypt(cipher), msg)

class TestEstablishment(unittest.TestCase):
    def test_basic_establishment(self):
        nodes = [OnionNode() for _ in range(3)]
        originator = Originator()
        originator.set_pubkeys(list(map(lambda x: RSAVirtuoso(x.get_public_key()), nodes)))
        path = originator.get_path()
        packet = originator.create_onion(onion.MessageType.Establish, 1, '', 0).to_dict()
        addr = int(packet["addr"])
        while packet["type"] != "Establish":
            packet = packet["data"]
            packet = nodes[addr].peel_layer(packet)
            addr = int(packet["addr"])
        keydata = json.loads(packet["data"])
        k = base64.b64decode(keydata["symkey"])
        symkey = nodes[addr].decrypt(k)
        self.assertEqual(path[addr][1],symkey)

if __name__ == '__main__':
    unittest.main()
