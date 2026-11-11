import pytest
from app import storage


@pytest.fixture
def clean_storage(tmp_path, monkeypatch):
    storage.open_files.clear()
    storage.packet_count = 0
    storage.byte_count = 0
    monkeypatch.setattr(storage, "OUTPUT_DIR", tmp_path)
    yield tmp_path
    # teardown close_all() may log a "stuck in buffer" warning when a test
    # fails mid-write; that warning is a reaction to the failure, not the cause
    storage.close_all()
