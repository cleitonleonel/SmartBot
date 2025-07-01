from typing import Final, Any
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import toml


def load_config(file_path: str) -> dict[str, Any]:
    if sys.version_info >= (3, 11):
        with open(file_path, 'rb') as f:
            return tomllib.load(f)
    with open(file_path, 'r') as f:
        return toml.load(f)


config = load_config('config.toml')

API_ID: Final[str] = config['API']['ID']
API_HASH: Final[str] = config['API']['HASH']
BOT_TOKEN: Final[str] = config['API']['BOT_TOKEN']
ADMIN_IDS: Final[list] = config['ADMIN']['IDS']
APP_NAME: Final[str] = config['APPLICATION']['APP_NAME']
APP_AUTHOR: Final[str] = config['APPLICATION']['APP_AUTHOR']
APP_VERSION: Final[str] = config['APPLICATION']['APP_VERSION']
DEVICE_MODEL: Final[str] = config['APPLICATION']['DEVICE_MODEL']
SYSTEM_VERSION: Final[str] = config['APPLICATION']['SYSTEM_VERSION']
