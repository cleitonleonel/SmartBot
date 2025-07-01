import logging
from telethon import events
from typing import Any
from smartbot.utils.handler import ClientHandler
from smartbot.utils.menu import go_back

logging.basicConfig(level=logging.INFO)

client = ClientHandler()


@client.on(events.CallbackQuery(pattern=b"^back_menu$"))
async def handle_back_menu(event: Any):
    await go_back(event)