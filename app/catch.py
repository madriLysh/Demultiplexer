from demux import handle_packet
from scapy.sendrecv import sniff

def start_capture(iface: str):
    """capture each TCP packets and pass them to handle_packet"""
    sniff(iface=iface, filter="tcp", prn=handle_packet, store=False)

    