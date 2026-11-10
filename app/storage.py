from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# app/storage.py -> parent = app/ -> parent = repo root
OUTPUT_DIR = Path(__file__).resolve().parent.parent / 'output'

# normalized flow key -> open file handle
open_files = {}

packet_count = 0
byte_count = 0


def init_storage():
    OUTPUT_DIR.mkdir(exist_ok=True)

def sanitize(ip: str) -> str:
    #make an IP address safe for use in a filename on any OS
    return ip.replace(":", "-").split("%")[0]

def flow_filename(key) -> Path:
    #build the output path from a normalized flow key

    (src_ip, src_port), (dst_ip, dst_port) = key
    return OUTPUT_DIR / f'{sanitize(src_ip)}_{src_port}_{sanitize(dst_ip)}_{dst_port}.txt'

def store(key, sender, payload: bytes, seq):
    #append payload bytes to the file belonging to key's connection
    global packet_count, byte_count
    packet_count += 1
    byte_count += len(payload)
    if key not in open_files:
        open_files[key] = {
            "file": open(flow_filename(key), 'ab'),
            "dirs": {
                key[0]: {"next_seq": None, "buffer": {}},
                key[1]: {"next_seq": None, "buffer": {}}
            }
        }
        (src_ip, src_port), (dst_ip, dst_port) = key
        logger.info(f'+ new flow: {src_ip}:{src_port} <-> {dst_ip}:{dst_port} -> {open_files[key]["file"].name}')
    flow = open_files[key]
    d = flow["dirs"].get(sender)
    if d is None:
        logger.warning(f'unknown sender {sender} for flow {key}; packet dropped')
        return

    if d["next_seq"] is None:
        d["next_seq"] = seq

    seq_end = seq + len(payload)
    if seq_end <= d["next_seq"]:
        return 
    if seq < d["next_seq"]:
        payload = payload[d["next_seq"] - seq:]
        seq = d["next_seq"]

    if seq > d["next_seq"]:
        d["buffer"][seq] = payload
        return 
    
    flow["file"].write(payload)
    d["next_seq"] = seq + len(payload)

    while d["buffer"]:
        nxt = d["next_seq"]
        # drop buffered segments fully covered by what we already wrote
        for s in [s for s, p in d["buffer"].items() if s + len(p) <= nxt]:
            del d["buffer"][s]
        # trim buffered segments that partially overlap what we already wrote
        for s in [s for s, p in d["buffer"].items() if s < nxt < s + len(p)]:
            d["buffer"][nxt] = d["buffer"].pop(s)[nxt - s:]
        if nxt not in d["buffer"]:
            break
        buffered = d["buffer"].pop(nxt)
        flow["file"].write(buffered)
        d["next_seq"] += len(buffered)
    
def close_all():
    #flush and close every open flow file
    n = len(open_files)
    for key, flow in open_files.items():
        for sender, d in flow["dirs"].items():
            if d["buffer"]:
                stuck = sum(len(p) for p in d["buffer"].values())
                logger.warning(
                    f'{key} sender {sender}: {stuck} bytes stuck in buffer, '
                    f'gap before seq {min(d["buffer"])}'
                )
        flow["file"].close()
    open_files.clear()
    logger.info(f'Closed {n} flow files — {packet_count} packets, {byte_count} bytes captured.')