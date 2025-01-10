import os
from app.bot import Client
from app.paths import SESSIONS_DIR
from telethon.network import ConnectionTcpFull
from app.config import (
    BOT_TOKEN,
    APP_NAME,
    DEVICE_MODEL,
    SYSTEM_VERSION,
    APP_VERSION,
    API_ID,
    API_HASH,
)

SESSION_PATH = os.path.join(
    SESSIONS_DIR,
    APP_NAME
)

plugins = dict(
    root="plugins",
    include=[
        "commands.start handle_exit handle_start handle_help", "message"
    ],
    # exclude=["message"]
)

# plugins = dict(root="plugins")

client = Client(
    bot_token=BOT_TOKEN,
    session=SESSION_PATH,
    api_id=API_ID,
    api_hash=API_HASH,
    connection=ConnectionTcpFull,
    device_model=DEVICE_MODEL,
    system_version=SYSTEM_VERSION,
    app_version=APP_VERSION,
    plugins=plugins
)

if __name__ == "__main__":
    client.start_service()
