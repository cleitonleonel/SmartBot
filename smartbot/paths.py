from typing import Final
import os

ROOT_DIR: Final[str] = os.getcwd()
MODULE_DIR: Final[str] = os.path.dirname(os.path.abspath(__file__))
BASE_NAME: Final[str] = os.path.basename(MODULE_DIR)
HANDLER_DIR: Final[str] = os.path.join(BASE_NAME, 'handlers')
SESSIONS_DIR: Final[str] = os.path.join(ROOT_DIR, 'sessions')
CLIENTS_DIR: Final[str] = os.path.join(SESSIONS_DIR, 'clients')

if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)


def get_session_path(client_id: int) -> str:
    return os.path.join(CLIENTS_DIR, f'{client_id}')


def get_handlers_path(plugins_dir: str | None=None) -> str:
    if plugins_dir:
        return ".".join(plugins_dir.split(os.path.sep))

    return ".".join(HANDLER_DIR.split(os.path.sep))
