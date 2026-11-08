from scapy.layers.inet import IP, TCP
from scapy.packet import Packet, Raw
from storage import store

def flow_key(pkt: Packet):
    """Return a direction-independent connection ID, or None if not TCP/IP."""
    if not pkt.haslayer(TCP) or not pkt.haslayer(IP):
        return None

    a = (pkt[IP].src, pkt[TCP].sport)
    b = (pkt[IP].dst, pkt[TCP].dport)

    return (a, b) if a < b else (b, a)

def handle_packet(pkt: Packet):
    """decides to drop or keep the packet"""
    key = flow_key(pkt)
    if key is None:
        return

    if not pkt.haslayer(Raw):
        return 
    store(key, bytes(pkt[Raw].load))
    