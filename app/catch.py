from demux import handle_packet
from scapy.error import Scapy_Exception
from scapy.sendrecv import sniff


def start_capture(iface):
    #capture TCP packets on iface and pass each one to handle_packet
    try:
        sniff(iface=iface, filter='tcp', prn=handle_packet, store=False)
    except Scapy_Exception as e:
        if 'filter' in str(e).lower():
            print('BPF filter unavailable (libpcap missing); filtering in Python instead.')
            sniff(iface=iface, prn=handle_packet, store=False)
        else:
            raise SystemExit(
                f'Capture failed: {e}\n'
                'Windows: install Npcap and run as Administrator. '
                'Linux/macOS: run with sudo.'
            )