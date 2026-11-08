from scapy.all import conf
from catch import start_capture
from storage import close_all, init_storage
from cli import create_args, list_ifaces, resolve_iface, create_iface_list
def main():

    create_iface_list()
    args = create_args()
    if args.list:
        list_ifaces
        return 

    iface = resolve_iface(args.iface) if args.iface else conf.iface
    init_storage()
    try:
        # here conf.iface will check for the os iface and will pass it. so that it can run on multiple OSes
        start_capture(iface)
    except KeyboardInterrupt:
        pass
    finally:
        close_all()

if __name__ == "__main__":
    main()