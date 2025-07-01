import logging
from typing import Any
from telethon import events, Button
from smartbot.utils.handler import ClientHandler

logging.basicConfig(level=logging.INFO)

client = ClientHandler()


@client.on(events.NewMessage(pattern='/start'))
async def handle_start(event: Any):
    """
    Handles the `/start` command by sending a greeting message.

    :param event: The event triggered by the `/start` command.
    """
    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"Start Handler Triggered by User ID: {sender_id}")
    logging.debug(f"Event Client Instance: {event.client}")

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
        f"Olá, {sender.first_name}! Este é o start handler."
    )

@client.on(events.NewMessage(pattern='/button'))
async def handle_send_button(event: Any):
    """
    Handles the `/button` command by sending a message with an inline button.

    :param event: The event triggered by the `/button` command.
    """
    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"Handler Triggered by User ID: {sender_id}")
    logging.debug(f"Event Client Instance: {event.client}")

    button = [
        Button.inline(
            '👋 Clique em mim.',
            'Test'
        )
    ]

    await event.respond(
        message='Botão enviado como resposta.',
        buttons=button
    )

    await event.reply(
        f"Olá, {sender.first_name}! Este é o button handler."
    )
