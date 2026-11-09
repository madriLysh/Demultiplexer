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

def store(key, payload: bytes):
    #append payload bytes to the file belonging to key's connection
    global packet_count, byte_count
    packet_count += 1
    byte_count += len(payload)
    if key not in open_files:
        open_files[key] = open(flow_filename(key), 'ab')
        (src_ip, src_port), (dst_ip, dst_port) = key
        logger.info(f'+ new flow: {src_ip}:{src_port} <-> {dst_ip}:{dst_port} -> {open_files[key].name}')
    open_files[key].write(payload)


def close_all():
    #flush and close every open flow file
    n = len(open_files)
    for f in open_files.values():
        f.close()
    open_files.clear()
    logger.info(f'Closed {n} flow files — {packet_count} packets, {byte_count} bytes captured.')