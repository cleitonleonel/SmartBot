import logging
from telethon import events
from typing import Any
from smartbot.utils.handler import ClientHandler


logging.basicConfig(level=logging.INFO)

client = ClientHandler()


@client.on(events.CallbackQuery)
async def handle_callback(event: Any):
    """
    Handles callback queries triggered by inline button interactions.

    :param event: The event is triggered by an inline button interaction.
    """
    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"Callback Triggered by User ID: {sender_id}")
    logging.debug(f"Event Client Instance: {event.client}")

    await event.respond(
        message=f'Resposta do callback event: {event.data}',
        buttons=None
    )
    await event.reply(
        f"Olá, {sender.first_name}! Este é o callback handler."
    )
