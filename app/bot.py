import sys
import asyncio
import logging
from pathlib import Path
from importlib import import_module
from telethon import TelegramClient
from app.paths import get_handlers_path

logging.basicConfig(level=logging.INFO)


class Client(TelegramClient):
    """
    Custom Telegram Client with additional functionalities for managing handlers and lifecycle.
    """

    def __init__(self, bot_token, **kwargs):
        """
        Initializes the Telegram client with a bot token.

        :param bot_token: The bot token to authenticate with the Telegram API.
        :param kwargs: Additional keyword arguments to pass to the TelegramClient constructor.
        """
        super().__init__(**kwargs)
        self.bot_token = bot_token

    async def send_message(self, chat_id, message='', **kwargs):
        """
        Sends a message to a specified chat.

        :param chat_id: The ID of the chat where the message should be sent.
        :param message: The message content to send.
        :param kwargs: Additional arguments to customize the message (e.g., buttons, parse_mode).
        :return: The result of the send_message operation.
        """
        return await super().send_message(chat_id, message, **kwargs)

    async def load_handlers(self):
        """
        Automatically loads and registers event handlers for the Telegram client.

        Scans the handler directory for Python files, dynamically imports the modules,
        and registers any functions decorated as handlers.
        """
        handlers_path = get_handlers_path()
        for path in sorted(Path(handlers_path).rglob("*.py")):
            module_path = '.'.join(path.parent.parts + (path.stem,))
            if module_path not in sys.modules:
                module = import_module(module_path)
                logging.info(f"Loading module: {module_path}")

                for name in dir(module):
                    handler_func = getattr(module, name)

                    if callable(handler_func) and getattr(handler_func, 'is_handler', False):
                        handler_info = getattr(handler_func, 'handler_info', {})
                        event = handler_info.get("event")

                        logging.info(f"Registering handler: {name}")
                        self.add_event_handler(handler_func, event)

                        await asyncio.sleep(0.1)

    async def keep_alive(self):
        """
        Keeps the bot connected to the Telegram API.

        Periodically checks the connection status and attempts to reconnect if disconnected.
        """
        while True:
            try:
                if not self.is_connected():
                    logging.warning('Bot is not connected. Reconnecting...')
                    await self.connect()
                await asyncio.sleep(60)
            except Exception as e:
                logging.error(f'Error in keep_alive: {e}', exc_info=True)
                await asyncio.sleep(60)

    async def run(self):
        """
        Starts the bot, loads event handlers, and manages its lifecycle.

        Handles connection errors by attempting to reconnect automatically.
        """
        try:
            await self.start(bot_token=self.bot_token)
            await self.load_handlers()
            logging.info('Starting Telegram bot!')
            await asyncio.gather(
                self.run_until_disconnected(),
                self.keep_alive()
            )
        except ConnectionError:
            logging.error('Failed to connect to Telegram.')
            await asyncio.sleep(5)
            await self.run()

    async def shutdown(self):
        """
        Gracefully disconnects the bot from the Telegram API.

        Ensures proper cleanup of resources before exiting.
        """
        await self.disconnect()
        logging.info('Bot successfully disconnected.')

    def start_service(self):
        """
        Starts the bot service and runs it until interrupted.

        Handles cleanup upon keyboard interruption to ensure a graceful shutdown.
        """
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.run())
        except KeyboardInterrupt:
            logging.info(
                'Bot interrupted by user.\n'
                'Disconnecting...'
            )
            loop.run_until_complete(self.shutdown())
