import logging
from typing import Any
from telethon import events
from smartbot.utils.handler import ClientHandler
from smartbot.utils.menu import with_stack_and_cleanup


logging.basicConfig(level=logging.INFO)

client = ClientHandler()


@client.on(events.NewMessage(pattern='/start'))
@with_stack_and_cleanup(push=False, cleanup=True)
async def handle_start(event: Any):
    """
    Handles the `/start` command by sending a greeting message.

    :param event: The event is triggered by the `/start` command.
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
