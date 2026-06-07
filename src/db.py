from logging import config
from pathlib import Path
from config_manager import get_config
from logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

class DB:
    def __init__(self) -> None:
        config = get_config()
        self.max_key_size = config.db_config.max_key_size
        self.max_value_size = config.db_config.max_value_size
        self.db_path = config.db_config.base_dir
        self.filename = "db"

        self.key_index: dict[str, tuple[Path, int]] = {}

        self.file_index = 1
        self.get_write_head_index()

        self.write_head = self.db_path / f"{self.filename} {self.file_index}"

        self.entry_format = "{created_at:017.6f}|{last_read:017.6f}|{key_size:7}|{value_size:7}|{key}|{value}\n"

    def serialize_entry(self, key: str, value: str) -> str:
        created_at = datetime.timestamp(datetime.now())
        return self.entry_format.format(created_at=created_at, last_read=0.0, key_size=len(key), value_size=len(value), key=key, value=value)   

    def deserialize_entry(self, entry: str) -> dict:
        parts = entry.split('|', 5)
        return {
            'created_at': float(parts[0]),
            'last_read': float(parts[1]),
            'key_size': int(parts[2]),
            'value_size': int(parts[3]),
            'key': parts[4],
            'value': parts[5].rstrip('\n')
        }

    def get_write_head_index(self):
        """update the write head index"""
        if (existing_files := list(self.db_path.glob(self.filename))):
            self.file_index = max(int(f.name.split("_")[1]) for f in existing_files) + 1

    def write(self, key: str, value: str) -> None:
        """write a key-value pair to the database"""
        file_path = self.write_head
        if len(key) > self.max_key_size or len(value) > self.max_value_size:
            raise ValueError(f"Key or value size exceeds maximum allowed size: {len(key)}/{self.max_key_size} {len(value)}/{self.max_value_size}")
        with open(file_path, 'a') as f:
            offset = f.tell()
            f.write(self.serialize_entry(key, value))
            self.key_index[key] = (file_path, offset)

    def read(self, key: str) -> str:
        """read a value from the database by key"""
        if key not in self.key_index:
            raise KeyError(f"Key not found: {key}")
        file_path, offset = self.key_index[key]
        with open(file_path, 'r') as f:
            f.seek(offset)
            entry = f.readline()
            return self.deserialize_entry(entry)['value']