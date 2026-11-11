import pytest
from app import storage

@pytest.fixture
def clean_storage(tmp_path, monkeypatch):     
    storage.open_files.clear()                 
    storage.packet_count = 0
    storage.byte_count = 0
    monkeypatch.setattr(storage, "OUTPUT_DIR", tmp_path)
    return tmp_path                             


@pytest.fixture(autouse=True)
def reset_storage():
    storage.OUTPUT_DIR.mkdir(exist_ok=True)
    for f in storage.OUTPUT_DIR.iterdir():
        if f.is_file():
            f.unlink()
    storage.open_files.clear()
    storage.packet_count = 0
    storage.byte_count = 0
    yield
    storage.close_all()
