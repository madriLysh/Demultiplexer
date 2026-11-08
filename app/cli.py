import argparse
from scapy.all import conf 

iface_list = {}

def create_args():
    parse = argparse.ArgumentParser(description='TCP flow demultiplexer')
    parse.add_argument(
        '--iface',
        metavar='IFACE',
        help="choose iface by name or number from list. defualt(auto)"
        )
    parse.add_argument(
        '--list',
        action='store_true',
        help="list of available ifaces"
        )

    return parse.parse_args()
def data_fields():
    ifaces = list(conf.ifaces.values())
    default_name = getattr(conf.iface, "name", conf.iface)
    return ifaces, default_name

def create_iface_list():
    ifaces, _ = data_fields()

    for n, i in enumerate(ifaces, start=1):
        iface_list[n] = i.name

def list_ifaces():
    ifaces, default_name = data_fields()

    for n, i in enumerate(ifaces, start=1):
        ip = i.ip or 'no IP'
        mark = '  (default)' if i.name == default_name else ''
        print(f'{n:>2}. {i.name:<12} {ip:<16} {i.description}{mark}')

def resolve_iface(value: str):
    try:
        iface = iface_list[int(value)]
    except ValueError:
        iface = value
    return iface