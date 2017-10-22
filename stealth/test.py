import onion
import stealth
from onion import Originator
from onion import OnionNode

# TEST CASE FOR THE ONION LAYERING
# Onion nodes kept in an array in onion.py
# IP addresses/domain names are replaced by the index of the onion node
# For the sake of the test, the message intended for the destination is typed as MessageType.Data, to give the while loop an edge condition

originator = Originator()
packet = originator.create_onion('i also hate nvidia', 'Linus Torvalds')
print('Originator creates:')
print(packet.to_dict())
print('')

d = packet.to_dict()
while(True):
    if d["type"] == "MessageType.Data":
        print('========================')
        print('To: ' + d["addr"])
        print(d["data"])
        print('========================')
        break
    addr = int(d["addr"])
    packet = d["data"]
    packet = onion.onions[addr].peel_layer(packet)
    print('Node ' + str(addr) + ' creates:')
    print(packet)
    print('')
    d = packet
