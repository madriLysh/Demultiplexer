from scapy.all import conf
from catch import start_capture
from storage import close_all, init_storage

init_storage()
try:
    start_capture(conf.iface)
finally:
    close_all()
