
OUTPUT_DIR = "output"

# Flow table: normalized flow key -> open file handle
flows = {}

def flow_filename(key) -> str:
    """Build the output filename from a normalized flow key."""
    (src_ip, src_port), (dst_ip, dst_port) = key
    return f"{OUTPUT_DIR}/{src_ip}_{src_port}_{dst_ip}_{dst_port}.txt"


def store(key, payload: bytes):
    """Append payload bytes to the file belonging to key's connection."""
    if key not in flows:
        flows[key] = open(flow_filename(key), "ab")
    flows[key].write(payload)


def close_all():
    """Flush and close every open flow file"""
    for f in flows.values():
        f.close()
    flows.clear()