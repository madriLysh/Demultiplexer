import logging

import app.storage as storage
from app.storage import close_all, flow_filename, sanitize, store


def read_flow(key):
    storage.open_files[key]["file"].flush()
    return flow_filename(key).read_bytes()


def test_sanitize_ipv4_unchanged():
    assert sanitize("192.168.1.1") == "192.168.1.1"


def test_sanitize_ipv6_colons_replaced():
    assert sanitize("fe80::1") == "fe80--1"


def test_sanitize_zone_id_stripped():
    assert sanitize("fe80::1%eth0") == "fe80--1"


def test_flow_filename_format(clean_storage):
    key = (("10.0.0.1", 1), ("10.0.0.2", 2))
    assert flow_filename(key) == clean_storage / "10.0.0.1_1_10.0.0.2_2.txt"


def test_store_first_segment_writes(clean_storage):
    key = (("10.0.0.1", 1), ("10.0.0.2", 2))
    sender = key[0]
    store(key, sender, b"hello", 1000)

    assert read_flow(key) == b"hello"
    assert storage.open_files[key]["dirs"][sender]["next_seq"] == 1005


def test_store_in_order_appends(clean_storage):
    key = (("10.0.0.1", 1), ("10.0.0.2", 2))
    sender = key[0]
    store(key, sender, b"hello", 1000)
    store(key, sender, b" world", 1005)

    assert read_flow(key) == b"hello world"
    assert storage.open_files[key]["dirs"][sender]["next_seq"] == 1011


def test_store_anchors_on_first_segment(clean_storage):
    key = (("10.0.0.1", 1), ("10.0.0.2", 2))
    sender = key[0]
    store(key, sender, b" world!", 1005)
    store(key, sender, b"hello", 1000)

    assert read_flow(key) == b" world!"
    assert storage.open_files[key]["dirs"][sender]["next_seq"] == 1012


def test_store_out_of_order_buffers_then_flushes(clean_storage):
    key = (("10.0.0.1", 1), ("10.0.0.2", 2))
    sender = key[0]
    store(key, sender, b"hello", 1000)
    store(key, sender, b" world!", 1011)

    assert read_flow(key) == b"hello"
    store(key, sender, b" world", 1005)

    assert read_flow(key) == b"hello world world!"
    assert storage.open_files[key]["dirs"][sender]["next_seq"] == 1018


def test_store_retransmission_dropped(clean_storage):
    key = (("10.0.0.1", 1), ("10.0.0.2", 2))
    sender = key[0]
    store(key, sender, b"hello", 1000)
    store(key, sender, b"hello", 1000)

    assert read_flow(key) == b"hello"
    assert storage.open_files[key]["dirs"][sender]["next_seq"] == 1005


def test_store_partial_overlap_trims(clean_storage):
    key = (("10.0.0.1", 1), ("10.0.0.2", 2))
    sender = key[0]
    store(key, sender, b"hello", 1000)
    store(key, sender, b"llo world", 1002)

    assert read_flow(key) == b"hello world"
    assert storage.open_files[key]["dirs"][sender]["next_seq"] == 1011


def test_store_write_after_close_all(clean_storage):
    key = (("10.0.0.1", 1), ("10.0.0.2", 2))
    sender = key[0]
    store(key, sender, b"hello", 1000)
    store(key, sender, b" world", 1005)
    close_all()

    store(key, sender, b"!", 1011)
    assert flow_filename(key).read_bytes() == b"hello world"
    assert storage.open_files[key]["dirs"][sender]["next_seq"] == 1012


def test_store_both_directions_one_file(clean_storage):
    key = (("10.0.0.1", 1), ("10.0.0.2", 2))
    store(key, key[0], b"req", 1000)
    store(key, key[1], b"resp", 5000)

    assert read_flow(key) == b"reqresp"
    assert storage.open_files[key]["dirs"][key[0]]["next_seq"] == 1003
    assert storage.open_files[key]["dirs"][key[1]]["next_seq"] == 5004


def test_store_two_flows_files(clean_storage):
    key1 = (("10.0.0.1", 1), ("10.0.0.2", 2))
    key2 = (("10.0.0.1", 1), ("10.0.0.3", 2))
    store(key1, key1[0], b"file1", 1000)
    store(key2, key2[0], b"file2", 2000)

    assert read_flow(key1) == b"file1"
    assert storage.open_files[key1]["dirs"][key1[0]]["next_seq"] == 1005
    assert read_flow(key2) == b"file2"
    assert storage.open_files[key2]["dirs"][key2[0]]["next_seq"] == 2005


def test_store_counters_increment(clean_storage):
    key1 = (("10.0.0.1", 1), ("10.0.0.2", 2))
    key2 = (("10.0.0.1", 1), ("10.0.0.3", 2))
    store(key1, key1[0], b"file1", 1000)
    store(key2, key2[0], b"file2", 2000)

    assert read_flow(key1) == b"file1"
    assert read_flow(key2) == b"file2"
    assert storage.packet_count == 2
    assert storage.byte_count == 10


def test_store_early_segment_stays_buffered_until_close(clean_storage, caplog):
    key = (("10.0.0.1", 1), ("10.0.0.2", 2))
    sender = key[0]
    store(key, sender, b"hello", 1000)
    store(key, sender, b"LOST", 1010)

    assert read_flow(key) == b"hello"
    with caplog.at_level(logging.WARNING):
        close_all()

    assert "stuck in buffer" in caplog.text
    assert flow_filename(key).read_bytes() == b"hello"


def test_close_all_clears_and_flushes(clean_storage):
    key = (("10.0.0.1", 1), ("10.0.0.2", 2))
    store(key, key[0], b"hello", 1000)

    close_all()
    assert storage.open_files == {}
    assert flow_filename(key).read_bytes() == b"hello"
