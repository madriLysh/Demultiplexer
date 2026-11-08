from pathlib import Path

# app/storage.py -> parent = app/ -> parent = repo root
OUTPUT_DIR = Path(__file__).resolve().parent.parent / 'output'

# normalized flow key -> open file handle
open_files = {}


def init_storage():
    OUTPUT_DIR.mkdir(exist_ok=True)


def flow_filename(key) -> Path:
    #build the output path from a normalized flow key
    (src_ip, src_port), (dst_ip, dst_port) = key
    return OUTPUT_DIR / f'{src_ip}_{src_port}_{dst_ip}_{dst_port}.txt'


def store(key, payload: bytes):
    #append payload bytes to the file belonging to key's connection
    if key not in open_files:
        open_files[key] = open(flow_filename(key), 'ab')
    open_files[key].write(payload)


def close_all():
    #flush and close every open flow file
    for f in open_files.values():
        f.close()
    open_files.clear()