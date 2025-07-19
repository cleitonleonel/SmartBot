import logging
import functools
from typing import Callable, Awaitable
from collections import defaultdict
from telethon.events import CallbackQuery
from smartbot.utils.context import (
    get_user_driver,
    DELETE_KEY,
    MENU_KEY
)


def with_stack_and_cleanup(push: bool = True, cleanup: bool | None = None):
    """
    Decorator to manage UI stack and clean up temporary messages.

    :param push: Whether to push the current message to the user's menu stack.
    :param cleanup: True = always clean, False = never clean, None = only if CallbackQuery.
    """

    def decorator(handler: Callable[[any], Awaitable[None]]):
        @functools.wraps(handler)
        async def wrapper(event):
            sender = await event.get_sender()
            sender_id = sender.id

            user_data = get_user_driver(event)
            delete_queue = user_data[DELETE_KEY]

            message = None
            is_callback = isinstance(event, CallbackQuery.Event)
            should_cleanup = cleanup if cleanup is not None else is_callback

            if should_cleanup and delete_queue:
                try:
                    await event.client.delete_messages(sender_id, delete_queue)
                except Exception as e:
                    logging.warning(f"[{sender_id}] Failed to delete previous messages: {e}")
                delete_queue.clear()

            if is_callback:
                message = await event.get_message()
            elif hasattr(event, 'message'):
                message = event.message

            if push and message and message.text:
                try:
                    user_data[MENU_KEY].append((message.text, message.reply_markup))
                except Exception as e:
                    logging.warning(f"[{sender_id}] Failed to push to stack: {e}")

            await handler(event)

        return wrapper

    return decorator


async def clear_temp_messages(event, sender_id: int):
    """
    Clears all temporary messages for a given user by deleting
    the message IDs stored in the delete queue.

    Initializes the user driver context if it doesn't exist.

    :param event: The Telegram event instance.
    :param sender_id: The Telegram user ID whose messages should be deleted.
    """
    if not isinstance(event.client.drivers.get(sender_id), dict):
        event.client.drivers[sender_id] = defaultdict(list)

    user_data = event.client.drivers[sender_id]
    delete_queue = user_data[DELETE_KEY]

    if not delete_queue:
        return

    try:
        await event.client.delete_messages(sender_id, delete_queue)
        delete_queue.clear()
    except Exception as e:
        logging.warning(f"Error while clearing messages for {sender_id}: {e}")


async def go_back(event):
    """
    Navigates back to the previous menu by popping from the user's menu stack.

    If the stack is empty, notifies the user that there is no previous menu.
    Also handles whether the event is a CallbackQuery or a regular message.

    :param event: The incoming event (either CallbackQuery or NewMessage).
    """
    sender = await event.get_sender()
    sender_id = sender.id

    if not isinstance(event.client.drivers.get(sender_id), dict):
        event.client.drivers[sender_id] = defaultdict(list)

    user_data = event.client.drivers[sender_id]
    stack = user_data[MENU_KEY]

    if stack:
        text, buttons = stack.pop()

        if isinstance(event, CallbackQuery.Event):
            try:
                await event.edit(text, buttons=buttons)
            except Exception:
                msg = await event.respond(text, buttons=buttons)
                user_data[DELETE_KEY].append(msg.id)
        else:
            msg = await event.respond(text, buttons=buttons)
            user_data[DELETE_KEY].append(msg.id)
    else:
        if isinstance(event, CallbackQuery.Event):
            await event.answer("⚠️ No previous menu.", alert=True)
        else:
            await event.respond("⚠️ No previous menu.")
