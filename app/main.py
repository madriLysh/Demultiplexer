from scapy.all import conf
from catch import start_capture
from cli import parse_args, list_ifaces, resolve_iface
from storage import close_all, init_storage


def main():
    args = parse_args()

    if args.list:
        list_ifaces()
        return

    # conf.iface is Scapy's own pick of the default iface, so this works on any OS
    iface = resolve_iface(args.iface) if args.iface else conf.iface

    init_storage()
    try:
        start_capture(iface)
    except PermissionError:
        raise SystemExit('Live capture needs root/admin (Npcap on Windows).')
    except KeyboardInterrupt:
        pass
    finally:
        close_all()


if __name__ == '__main__':
    main()