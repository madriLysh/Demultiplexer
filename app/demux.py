from scapy.layers.inet import IP, TCP
from scapy.layers.inet6 import IPv6
from scapy.packet import Packet, Raw
from storage import store

def flow_key(pkt: Packet):
    #Return a direction-independent connection ID, or None if not TCP/IP
    ip =  get_ip_layer(pkt)
    if not pkt.haslayer(TCP) or ip is None:
        return None

    a = (ip.src, pkt[TCP].sport)
    b = (ip.dst, pkt[TCP].dport)

    return (a, b) if a < b else (b, a)
def handle_packet(pkt: Packet):
    #decides to drop or keep the packet
    key = flow_key(pkt)
    if key is None:
        return

    if not pkt.haslayer(Raw):
        return
    store(key, bytes(pkt[Raw].load))

def get_ip_layer(pkt: Packet):
    if pkt.haslayer(IPv6):
        return pkt[IPv6]
    if pkt.haslayer(IP):
        return pkt[IP]
    return None
