import logging
from scapy.config import conf
from catch import start_capture
from cli import parse_args, list_ifaces, resolve_iface
from storage import OUTPUT_DIR, close_all, init_storage

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    args = parse_args()

    if args.list:
        list_ifaces()
        return

    # conf.iface is Scapy's own pick of the default iface, so this works on any OS
    iface = resolve_iface(args.iface) if args.iface else conf.iface

    init_storage()
    iface_name = getattr(iface, 'name', iface)
    logger.info(f'Capturing on {iface_name} (filter: tcp), writing to {OUTPUT_DIR}')
    logger.info('Press Ctrl+C to stop.')
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