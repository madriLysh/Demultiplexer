import argparse
from scapy.config import conf


def parse_args():
    parser = argparse.ArgumentParser(description='TCP flow demultiplexer')
    parser.add_argument(
        '--iface',
        metavar='IFACE',
        help='choose iface by name or number from --list (default: auto)',
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='list available ifaces and exit',
    )
    return parser.parse_args()


def get_ifaces():
    #all interfaces Scapy sees on this machine.
    return sorted(conf.ifaces.values(), key=lambda i: i.name) 


def default_iface_name():
    #name of Scapy's default iface (conf.iface may be an object or a plain str)
    return getattr(conf.iface, 'name', conf.iface)


def list_ifaces():
    default = default_iface_name()
    for number, iface in enumerate(get_ifaces(), start=1):
        ip = iface.ip or 'no IP'
        mark = '  (default)' if iface.name == default else ''
        print(f'{number:>2}. {iface.name:<12} {ip:<16} {iface.description}{mark}')


def resolve_iface(value: str):
    #turn what the user typed (a number from --list, or a name) into an iface.
    iface_by_number = dict(enumerate(get_ifaces(), start=1))

    if value.isdigit():
        iface = iface_by_number.get(int(value))
        if iface is None:
            raise SystemExit(f'No interface number {value}. Run with --list to see options.')
        return iface

    for iface in iface_by_number.values():
        if value in (iface.name, iface.description):
            return iface
    raise SystemExit(f"Unknown interface '{value}'. Run with --list to see options.")