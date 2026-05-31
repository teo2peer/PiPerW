"""StorageInterface — per-app key/value persistence.

Backends:
- JSONFileStorage: human-readable, single file. Default.
- SQLiteStorage: durable, log-friendly. Use for high-volume.

Apps get a `self.storage` lazy attr via AppInterface.
"""
import json
import os
import sqlite3
import threading
from abc import ABC, abstractmethod


class StorageInterface(ABC):
    @abstractmethod
    def get(self, key, default=None): ...
    @abstractmethod
    def set(self, key, value): ...
    @abstractmethod
    def delete(self, key): ...
    @abstractmethod
    def keys(self): ...


class JSONFileStorage(StorageInterface):
    def __init__(self, base_dir, filename="storage.json"):
        os.makedirs(base_dir, exist_ok=True)
        self._path = os.path.join(base_dir, filename)
        self._lock = threading.Lock()
        self._data = self._load()

    def _load(self):
        if not os.path.exists(self._path):
            return {}
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

    def _flush(self):
        tmp = self._path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)
        os.replace(tmp, self._path)

    def get(self, key, default=None):
        with self._lock:
            return self._data.get(key, default)

    def set(self, key, value):
        with self._lock:
            self._data[key] = value
            self._flush()

    def delete(self, key):
        with self._lock:
            self._data.pop(key, None)
            self._flush()

    def keys(self):
        with self._lock:
            return list(self._data.keys())


class SQLiteStorage(StorageInterface):
    def __init__(self, base_dir, filename="storage.db"):
        os.makedirs(base_dir, exist_ok=True)
        self._path = os.path.join(base_dir, filename)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self._path, check_same_thread=False)
        self._conn.execute("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT)")
        self._conn.commit()

    def get(self, key, default=None):
        with self._lock:
            row = self._conn.execute("SELECT v FROM kv WHERE k = ?", (key,)).fetchone()
        if row is None:
            return default
        try:
            return json.loads(row[0])
        except json.JSONDecodeError:
            return row[0]

    def set(self, key, value):
        s = json.dumps(value)
        with self._lock:
            self._conn.execute(
                "INSERT INTO kv(k, v) VALUES (?, ?) ON CONFLICT(k) DO UPDATE SET v=excluded.v",
                (key, s),
            )
            self._conn.commit()

    def delete(self, key):
        with self._lock:
            self._conn.execute("DELETE FROM kv WHERE k = ?", (key,))
            self._conn.commit()

    def keys(self):
        with self._lock:
            return [r[0] for r in self._conn.execute("SELECT k FROM kv").fetchall()]
