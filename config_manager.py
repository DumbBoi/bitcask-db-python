from typing import Annotated
from pathlib import Path
from pydantic import BaseModel, Field
from typing import ClassVar
from pydantic.functional_validators import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class DbModel(BaseModel):
    base_dir: Annotated[Path, lambda x: Path(x) if isinstance(x, str) else x]
    max_key_size: int = 1
    max_value_size: int = 10

    @field_validator('base_dir', mode='after')
    def validate_base_dir(cls, base_dir: Path) -> Path:
        if not base_dir.exists():
            raise ValueError(f"base directory '{base_dir}' does not exist.")
        if not base_dir.is_dir():
            raise ValueError(f"base directory '{base_dir}' is not a directory.")
        return base_dir

    @field_validator('max_key_size', 'max_value_size')
    def validate_positive_int(cls, value: int) -> int:
        if not isinstance(value, int):
            raise ValueError(f"Value must be an integer, got {type(value)}")
        if value <= 0:
            raise ValueError(f"Value must be a positive integer, got {value}")
        value = value * 1024 * 1024 # convert from MB to bytes
        return value

class Settings(BaseSettings):
    db_config: DbModel = Field(default_factory=lambda: DbModel())
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(env_file=".env", 
                                                                    env_nested_delimiter="__")

def get_config() -> Settings:
    return Settings()