# Demultiplexer

A TCP flow demultiplexer CLI. It captures live TCP traffic on a network interface
(Scapy/libpcap) and writes each connection's payload bytes into a separate file,
so you can inspect individual flows instead of one interleaved packet stream.

## Usage

```
sudo python -m app.main            # capture on the default interface
sudo python -m app.main -i eth0    # capture on a specific interface
python -m app.main --list          # list available interfaces
```

Live capture needs root/admin privileges (Npcap on Windows with the Npcap
SDK installed and Scapy's Npcap bindings). Press Ctrl+C to stop; a summary of
captured flows, packets and bytes is printed on shutdown.

Output files land in `output/`, one per flow.

## Architecture

The code is split into three single-responsibility modules under `app/`:

- `catch.py` — capture: listens on the interface and hands packets onward.
- `demux.py` — demultiplexer: normalizes each packet into a flow key and
  extracts its payload.
- `storage.py` — storage: maps flow keys to open files and appends payloads.

This separation keeps capture, flow-identification and file I/O independent:
each stage can be tested or replaced (e.g. reading from a pcap file instead of
a live interface) without touching the others.

### Normalized flow keys

A flow key is `((src_ip, src_port), (dst_ip, dst_port))` with the endpoints
sorted, so packets from both directions of a connection (client→server and
server→client) merge into a single output file.

### IPv4 and IPv6

Both address families are supported. Since IPv6 addresses contain `:`, which
is illegal in filenames on Windows, addresses are sanitized (`:` → `-`, zone
ids stripped) before becoming filenames.

### Cross-platform interface handling

Interfaces are listed and resolved through Scapy (`conf.iface`, Scapy's
interface enumeration) rather than hardcoded OS-specific names, so the same
code works on Linux, macOS and Windows. On Windows, Npcap is required; on
Unix-like systems, capture needs sudo/root.

### TLS traffic

TLS encryption sits above TCP, so the tool sees only connection metadata (IPs,
ports, timing, sizes) plus ciphertext payloads. Decryption is out of scope.
Validation of the tool was done over plain HTTP, where payload bytes are
readable in the output files.

### BPF filter fallback

Capture uses a `tcp` BPF filter when available; if libpcap lacks BPF support
the capture is retried without the filter instead of failing.

### TCP reassembly

Payloads are reassembled per direction using TCP sequence numbers, so
out-of-order segments, retransmissions and partially overlapping segments are
written in the correct order. Each direction of a flow tracks its own next
expected sequence number; segments that arrive early are held in a buffer and
flushed once the gap in front of them is filled, while retransmitted or
already-covered bytes are dropped. On shutdown, any segments still stuck in a
buffer (a gap that never got filled, i.e. truly lost data) are reported as a
warning before the flow files are closed.

## Known limitations

- Reassembly anchors on the first data segment seen per direction. If capture
  starts mid-flow, earlier segments that were never observed stay missing.

## Future work

- Handle mid-flow capture starts (e.g. anchor on the lowest buffered segment
  instead of the first observed one).
- `argparse` is already used for CLI parsing and can be extended with more
  options (output directory, BPF filter override, pcap input, etc.).
