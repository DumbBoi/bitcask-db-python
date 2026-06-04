from typing import Annotated
from pathlib import Path
from pydantic.functional_validators import field_validator
from pydantic_settings import BaseSettings

class ConfigModel(BaseSettings):
    base_dir: Annotated[Path, lambda x: Path(x) if isinstance(x, str) else x]

    @field_validator('base_dir', mode='after')
    def validate_base_dir(base_dir: Path) -> Path:
        if not base_dir.exists():
            raise ValueError(f"base directory '{base_dir}' does not exist.")
        if not base_dir.is_dir():
            raise ValueError(f"base directory '{base_dir}' is not a directory.")
        return base_dir

def get_config() -> ConfigModel:
    return ConfigModel()