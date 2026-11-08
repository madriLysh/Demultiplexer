import os
from scapy.all import conf
from catch import start_capture
from storage import close_all

os.makedirs("output", exist_ok=True)
try:
    start_capture(conf.iface)
finally:
    close_all()
