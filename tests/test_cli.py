from app.cli import default_iface_name, resolve_iface, list_ifaces
from app import cli
from types import SimpleNamespace
import pytest

def test_default_iface_name_string(monkeypatch):
    monkeypatch.setattr(cli, "conf", SimpleNamespace(iface="eth0"))
    assert default_iface_name() == "eth0"


def test_default_iface_name_object(monkeypatch):
    iface = SimpleNamespace(name="eth0")
    monkeypatch.setattr(cli, "conf", SimpleNamespace(iface=iface))
    assert default_iface_name() == "eth0"


def test_resolve_iface_by_number(monkeypatch):
    ifaces = [SimpleNamespace(name="eth0"), SimpleNamespace(name= "wlan0")]
    monkeypatch.setattr(cli, "get_ifaces", lambda: ifaces)
    assert resolve_iface("1") == ifaces[0]


def test_resolve_iface_uknown_name_exits(monkeypatch):
    ifaces = [SimpleNamespace(name="eth0", description="Ethernet")]
    monkeypatch.setattr(cli, "get_ifaces", lambda: ifaces)
    with pytest.raises(SystemExit, match="Unknown interface"):
        resolve_iface("nonexistent0")


def test_resolve_iface_bad_number_exit(monkeypatch):
    ifaces = [SimpleNamespace(name="eth0")]
    monkeypatch.setattr(cli, "get_ifaces", lambda: ifaces)
    with pytest.raises(SystemExit, match="No interface number"):
        resolve_iface("999")


def test_list_ifaces_output(monkeypatch, capsys):
    ifaces = [
        SimpleNamespace(name="eth0", ip="192.168.1.5", description="Ethernet"),
        SimpleNamespace(name="wlan0", ip=None, description="Wi-Fi"),
    ]
    monkeypatch.setattr(cli, "get_ifaces", lambda: ifaces)
    monkeypatch.setattr(cli, "default_iface_name", lambda: "eth0")

    list_ifaces()

    assert capsys.readouterr().out == (
        " 1. eth0         192.168.1.5      Ethernet  (default)\n"
        " 2. wlan0        no IP            Wi-Fi\n"
    )