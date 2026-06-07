from pathlib import Path
from config_manager import get_config
from logger import get_logger
from datetime import datetime
import threading

logger = get_logger(__name__)

class DB:
    def __init__(self) -> None:
        config = get_config()
        self.max_key_size = config.db_config.max_key_size
        self.max_value_size = config.db_config.max_value_size
        self.max_file_entries = config.db_config.max_file_entries
        self.current_file_entries = 0
        self.max_file_count = config.db_config.max_file_count
        self.db_path = config.db_config.base_dir
        self.filename = "db"

        self.Lock = threading.Lock()
        self.cleanup_trigger = threading.Event()
        t = threading.Thread(target=self.clean_up, daemon=True)
        t.start()

        self.key_index: dict[str, tuple[Path, int]] = {}

        self.file_index = 1
        self.get_write_head_index()
        self.write_head = self.db_path / f"{self.filename} {self.file_index}"

        self.initialize_key_index()


        self.entry_format = "{deleted:1}|{created_at:017.6f}|{last_read:017.6f}|{key_size:7}|{value_size:7}|{key}|{value}\n"

    def initialize_key_index(self):
        """initialize the key index by reading existing files"""
        with self.Lock:
            for file in self.db_path.glob(f"{self.filename}*"):
                with open(file, 'r') as f:
                    offset = 0
                    while True:
                        line = f.readline()
                        if not line:
                            break
                        entry = self.deserialize_entry(line)
                        if entry['deleted']:
                            if self.key_index.get(entry['key']):
                                del self.key_index[entry['key']]
                        else:
                            self.key_index[entry['key']] = (file, offset)
                        offset += len(line)
                        if file == self.write_head:
                            self.current_file_entries += 1

    def serialize_entry(self, key: str, value: str, deleted: int = 0) -> str:
        created_at = datetime.timestamp(datetime.now())
        return self.entry_format.format(deleted=deleted, created_at=created_at, last_read=0.0, key_size=len(key), value_size=len(value), key=key, value=value)   

    def deserialize_entry(self, entry: str) -> dict:
        parts = entry.split('|', 6)
        return {
            'deleted': int(parts[0]),
            'created_at': float(parts[1]),
            'last_read': float(parts[2]),
            'key_size': int(parts[3]),
            'value_size': int(parts[4]),
            'key': parts[5],
            'value': parts[6].rstrip('\n')
        }

    def update_write_head(self):
        """update the write head if the current file exceeds the maximum entries"""
        logger.debug(f"current file entries: {self.current_file_entries}, max file entries: {self.max_file_entries}")
        if self.current_file_entries >= self.max_file_entries:
            logger.info(f"current file '{self.write_head}' reached max entries, creating new file")
            self.file_index += 1
            if self.max_file_count < self.file_index:
                    self.file_index = 1
                    logger.info(f"max file count reached {self.max_file_count}, current index {self.file_index}, triggering cleanup")
                    self.cleanup_trigger.set()
            self.write_head = self.db_path / f"{self.filename} {self.file_index}"
            logger.debug(f"new write head: {self.write_head}")
            self.current_file_entries = 0

    def get_write_head_index(self):
        """update the write head index"""
        if (existing_files := list(self.db_path.glob(f"{self.filename}*"))):
            self.file_index = max(int(f.name.split(" ")[1]) for f in existing_files) + 1
            logger.debug(f"existing files found, setting file index to {self.file_index}")

    def write_entry(self, file_path: Path, key: str, value: str, deleted: int = 0) -> None:
        with open(file_path, 'a') as f:
                offset = f.tell()
                f.write(self.serialize_entry(key, value, deleted))
                self.key_index[key] = (file_path, offset)
                self.current_file_entries += 1
                
    def write(self, key: str, value: str, deleted: int = 0) -> None:
        """write a key-value pair to the database"""
        with self.Lock:
            file_path = self.write_head
            if len(key) > self.max_key_size or len(value) > self.max_value_size:
                raise ValueError(f"Key or value size exceeds maximum allowed size: {len(key)}/{self.max_key_size} {len(value)}/{self.max_value_size}")
            self.write_entry(file_path, key, value, deleted)
            self.update_write_head()

    def read(self, key: str) -> str:
        """read a value from the database by key"""
        with self.Lock:
            if key not in self.key_index:
                raise KeyError(f"Key not found: {key}")
            file_path, offset = self.key_index[key]
            with open(file_path, 'r') as f:
                f.seek(offset)
                entry = f.readline()
                if self.deserialize_entry(entry)['deleted']:
                    raise KeyError(f"Key not found: {key}")
            self.update_write_head()
            return self.deserialize_entry(entry)['value']

    def delete(self, key: str) -> None:
        """delete a key-value pair from the database"""
        with self.Lock:
            if key not in self.key_index:
                raise KeyError(f"key not found: {key}")
            self.write_entry(self.write_head, key, '', deleted=1)
            del self.key_index[key]
            self.update_write_head()

    def clean_up(self) -> None:
        """clear up the database by removing deleted entries"""
        backup_path = self.db_path / f"temp_{self.filename}_backup"
        def determine_pos(key: str) -> bool:
            if self.key_index.get(key, (None, None)) == (file, f.tell() - len(line)):
                return True
            return False
        while True:
            self.cleanup_trigger.wait()
            with self.Lock:
                logger.info("starting cleanup process")
                entries_written = 0
                for file in self.db_path.glob(f"{self.filename}*"):
                    with open(file, 'r') as f:
                        while True:
                            line = f.readline()
                            if not line:
                                break
                            entry = self.deserialize_entry(line)
                            if entry['key'] in self.key_index:
                                if not entry['deleted'] and determine_pos(entry['key']):
                                    self.write_entry(backup_path, entry['key'], entry['value'], deleted=0)
                                    entries_written += 1
                logger.info(f"cleanup process completed, entries written to backup: {entries_written}")
                status = [f.unlink() for f in self.db_path.glob(f"{self.filename}*") if f != backup_path]
                logger.info(f"deleting old files deletion status: {status}")
                self.current_file_entries = entries_written
                backup_path.rename(self.db_path / f"{self.filename} 0")
            self.cleanup_trigger.clear()