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

        self.file_index = 1
        self.get_write_head_index()

        self.write_head = self.db_path / f"{self.filename} {self.file_index}"

        self.entry_format = "{created_at:10}|{last_read:10}|{key_size:7}|{value_size:7}|{key}|{value}\n"

    def get_write_head_index(self):
        """update the write head index"""
        if (existing_files := list(self.db_path.glob(self.filename))):
            self.file_index = max(int(f.name.split("_")[1]) for f in existing_files) + 1

    def write(self, key: str, value: str) -> None:
        """write a key-value pair to the database"""
        file_path = self.write_head
        created_at = datetime.timestamp(datetime.now())
        if len(key) > self.max_key_size or len(value) > self.max_value_size:
            raise ValueError(f"Key or value size exceeds maximum allowed size: {len(key)}/{self.max_key_size} {len(value)}/{self.max_value_size}")
        with open(file_path, 'a') as f:
            f.write(self.entry_format.format(created_at=created_at, last_read=0, key_size=len(key), value_size=len(value), key=key, value=value))