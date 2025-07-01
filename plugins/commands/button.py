import logging
from telethon import events
from typing import Any
from smartbot.utils.handler import ClientHandler
from smartbot.utils.buttons import build_inline_buttons
from smartbot.utils.menu import (
    with_stack_and_cleanup
)

logging.basicConfig(level=logging.INFO)

client = ClientHandler()


@client.on(events.NewMessage(pattern='/button'))
@with_stack_and_cleanup()
async def handle_grades(event: Any):
    """
    Handles callback queries triggered by inline button interactions.

    :param event: The event is triggered by an inline button interaction.
    """
    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"Callback Triggered by User ID: {sender_id}")
    logging.debug(f"Event Client Instance: {event.client}")

    disciplines = [
        ("Matemática", b"matematica"),
        ("Português", b"portugues"),
        ("História", b"historia")
    ]
    utility_section = [
        ("🔙 Voltar", b"back_menu"),
    ]

    disciplines_buttons = (
            build_inline_buttons(disciplines, cols=2)
            + [[]]
            + build_inline_buttons(utility_section, cols=1)
    )

    await event.delete()
    menu_title = "📚 **Selecione uma disciplina**"
    await event.respond(menu_title, buttons=disciplines_buttons)