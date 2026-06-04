from pathlib import Path
from config_manager import get_config

class DB:
    def __init__(self) -> None:
        self.config = get_config()
        self.db_path = Path(self.config.base_dir)
        self.filename = "db"
        self.file_index = 1
        if (existing_files := self.db_path.glob(self.filename)):
            self.file_index = max(int(f.name.split("_")[1]) for f in existing_files) + 1
        self.write_head  = self.db_path / self.filename / str(self.file_index)

    def write(self, key: str, value: str) -> None:
        """Write a key-value pair to the database."""
        file_path = self.write_head
        with open(file_path, 'a') as f:
            f.write(value)