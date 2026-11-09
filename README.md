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

## Known limitations

- Payloads are appended in packet arrival order; segments are not reordered by
  TCP sequence numbers, so out-of-order delivery appears out of order in the
  output file.

## Future work

- TCP reassembly via sequence numbers (handling out-of-order and retransmitted
  segments).
- `argparse` is already used for CLI parsing and can be extended with more
  options (output directory, BPF filter override, pcap input, etc.).
