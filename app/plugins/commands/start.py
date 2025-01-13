import logging
from typing import Any
from telethon import events
from app.utils.base_handler import ClientHandler


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
    logging.info(f"Event Client Instance: {event.client}")

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


@client.on(events.NewMessage(pattern='/help'))
async def handle_help(event: Any):
    """
    Handles the `/help` command by sending a greeting message.

    :param event: The event triggered by the `/help` command.
    """

    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"Help Handler Triggered by User ID: {sender_id}")
    logging.info(f"Event Client Instance: {event.client}")

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
        f"Olá, {sender.first_name}! Este é o help handler."
    )


@client.on(events.NewMessage(pattern='/exit'))
async def handle_exit(event: Any):
    """
    Handles the `/exit` command by sending a greeting message.

    :param event: The event triggered by the `/exit` command.
    """
    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"Exit Handler Triggered by User ID: {sender_id}")
    logging.info(f"Event Client Instance: {event.client}")

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
        f"Olá, {sender.first_name}! Este é o exit handler."
    )
