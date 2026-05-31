from PiPerW.interfaces.storage_interface import JSONFileStorage, SQLiteStorage


def test_json_storage_roundtrip(tmp_path):
    s = JSONFileStorage(str(tmp_path))
    s.set("k", {"a": 1})
    assert s.get("k") == {"a": 1}
    assert "k" in s.keys()
    s.delete("k")
    assert s.get("k") is None


def test_sqlite_storage_roundtrip(tmp_path):
    s = SQLiteStorage(str(tmp_path))
    s.set("k", [1, 2, 3])
    assert s.get("k") == [1, 2, 3]
    s.delete("k")
    assert s.get("k") is None
