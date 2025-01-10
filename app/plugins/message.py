import logging
from telethon import (
    events
)
from app.utils.base_handler import ClientHandler

logging.basicConfig(level=logging.INFO)

client = ClientHandler()


@client.on(events.NewMessage(pattern='/text'))
async def handle_text(event):
    """
    Handles the `/text` command by sending a greeting message.

    :param event: The event triggered by the `/text` command.
    """
    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"Start Handler Triggered by User ID: {sender_id}")
    logging.info(f"Event Client Instance: {event.client}")
    logging.info(f"User Data Client: {event.client.user_data}")
    event.client.user_data["name"] = sender.first_name

    await event.client.send_message(
        sender_id,
        message=f'Mensagem enviada pelo client: {event.client}',
        buttons=None
    )
    await event.respond(
        message='Resposta enviada por evento.',
        buttons=None
    )
    await event.reply(
        f"Olá, {sender.first_name}! Este é o text handler."
    )