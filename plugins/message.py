import logging
from typing import Any
from telethon import events
from smartbot.utils.handler import ClientHandler


logging.basicConfig(level=logging.INFO)

client: ClientHandler = ClientHandler()


@client.on(events.NewMessage(pattern='/text'))
async def handle_text(event: Any) -> None:
    """
    Handles the `/text` command by sending a greeting message.

    :param event: The event triggered by the `/text` command.
    """

    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"Start Handler Triggered by User ID: {sender_id}")
    logging.info(f"Event Client Instance: {event.client}")
    logging.info(f"User Data Client: {event.client.drivers}")
    event.client.drivers["user_data"] = {}
    event.client.drivers["user_data"]["id"] = sender_id
    event.client.drivers["user_data"]["name"] = sender.first_name
    logging.info(f"User Data Client: {event.client.drivers}")

    response = await event.client.send_message(
        sender_id,
        message=f'Mensagem enviada pelo client: {event.client}',
        buttons=None
    )
    msg_response_id = response.id

    await event.respond(
        message='Resposta enviada por evento.',
        buttons=None
    )

    await event.reply(
        f"Olá, {sender.first_name}! Este é o text handler."
    )

    await event.respond(
        message='Resposta enviada por evento.',
        buttons=None
    )

    await event.client.update_message(
        chat_id=sender_id,
        message_id=msg_response_id,
        message=f'Mensagem enviada pelo client: {event.client}, será apagada por evento.',
    )

    await event.client.remove_messages(
        chat_id=sender_id,
        message_ids=msg_response_id
    )
