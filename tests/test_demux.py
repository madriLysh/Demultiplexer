import pytest
from unittest import mock

from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import ARP, Ether
from scapy.packet import Raw

from app.demux import flow_key, handle_packet


def make_tcp(src, dst, sport, dport, seq=None, payload=None, ipv6=False):
    #build a TCP packet over IPv4 (default) or IPv6, with optional payload
    ip = IPv6(src=src, dst=dst) if ipv6 else IP(src=src, dst=dst)
    tcp = TCP(sport=sport, dport=dport, seq=seq) if seq is not None else TCP(sport=sport, dport=dport)
    pkt = ip / tcp
    if payload is not None:
        pkt = pkt / Raw(payload)
    return pkt


def test_flow_key_ipv4_basic():
    pkt = make_tcp("10.0.0.1", "10.0.0.2", 12345, 80)
    assert flow_key(pkt) == (("10.0.0.1", 12345), ("10.0.0.2", 80))


def test_flow_key_direction_symmetric():
    fwd = make_tcp("10.0.0.1", "10.0.0.2", 12345, 80)
    rev = make_tcp("10.0.0.2", "10.0.0.1", 80, 12345)
    assert flow_key(fwd) == flow_key(rev)


def test_flow_key_ipv6():
    pkt = make_tcp("::1", "::2", 1, 2, ipv6=True)
    assert flow_key(pkt) == (("::1", 1), ("::2", 2))


def test_flow_key_udp_returns_none():
    pkt = IP() / UDP()
    assert flow_key(pkt) is None


def test_flow_key_arp_returns_none():
    pkt = ARP()
    assert flow_key(pkt) is None


def test_flow_key_tcp_without_ip_returns_none():
    pkt = TCP()
    assert flow_key(pkt) is None

def test_handle_packet_no_ip_does_nothing():
    pkt = Ether() / Raw(b"x")
    with mock.patch("app.demux.store") as fake_store:
        handle_packet(pkt)
        fake_store.assert_not_called()

def test_handle_packet_syn_no_payload_does_nothing():
    pkt = IP() / TCP(flags="S")
    with mock.patch("app.demux.store") as fake_store:
        handle_packet(pkt)
        fake_store.assert_not_called()

def test_hanlde_packet_forwards_payload():
    pkt = make_tcp(..., ..., ..., ..., seq=1000, payload=b"hello")
    with mock.patch("app.demux.store") as fake_store:
        handle_packet(pkt)
        fake_store.assert_called_once()