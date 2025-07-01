import asyncio
import logging
from telethon import (
    TelegramClient,
    Button
)
from telethon.errors import (
    MessageDeleteForbiddenError,
    # FloodWaitError
)
from telethon.tl.types import (
    BotCommandScopePeer,
    BotCommandScopeDefault,
    InputPhoto
)
from telethon.tl.functions.bots import (
    SetBotCommandsRequest,
    SetBotInfoRequest,
    GetBotInfoRequest
)
from telethon.tl.functions.photos import (
    UpdateProfilePhotoRequest,
    UploadProfilePhotoRequest
)
from typing import TypeVar, Generic, Type, Dict, Any
from smartbot.plugin_loader import PluginLoader
from enum import Enum
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO
)

StateT = TypeVar('StateT', bound=Enum)
SessionT = TypeVar('SessionT')


class ConversationState(Enum):
    """Available conversation states for user sessions."""
    IDLE = "idle"


class UserSession(Generic[StateT]):
    """
    Class for managing individual user session data and conversation state.

    This class handles user-specific data including conversation state,
    temporary context, persistent data, and session timeout management.
    """
    def __init__(self, user_id: int, state_class: Type[StateT]):
        """
        Initialize a new user session.

        Args:
            user_id (int): Telegram user ID
            state_class (Type[Enum]): Class to use for conversation states
        """
        self.user_id = user_id
        self.state_class = state_class
        self.state = state_class.IDLE
        self.context = {}  # Temporary conversation data
        self.data = {}  # Persistent user data
        self.last_activity = datetime.now()
        self.timeout_duration = timedelta(minutes=30)  # Default timeout

    def set_state(self, state: StateT, context: Dict = None):
        """
        Set the conversation state for this user session.
        Args:
            state: The new conversation state (should be from state_class)
            context (Dict, optional): Additional context data to store
        """
        self.state = state
        if context:
            self.context.update(context)
        self.last_activity = datetime.now()

    def get_state(self):
        """
        Get the current conversation state.
        Returns:
            Current state of the conversation
        """
        return self.state

    def set_context(self, key: str, value: Any):
        """
        Set a value in the temporary conversation context.
        Args:
            key (str): Context key
            value (Any): Value to store
        """
        self.context[key] = value
        self.last_activity = datetime.now()

    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the conversation context.
        Args:
            key (str): Context key to retrieve
            default (Any, optional): Default value if key not found
        Returns:
            Any: The context value or default
        """
        return self.context.get(key, default)

    def clear_context(self):
        """Clear all temporary context data."""
        self.context.clear()

    def set_data(self, key: str, value: Any):
        """
        Set persistent user data.
        Args:
            key (str): Data key
            value (Any): Value to store
        """
        self.data[key] = value

    def get_data(self, key: str, default: Any = None) -> Any:
        """
        Get persistent user data.
        Args:
            key (str): Data key to retrieve
            default (Any, optional): Default value if key not found
        Returns:
            Any: The data value or default
        """
        return self.data.get(key, default)

    def is_expired(self) -> bool:
        """
        Check if the session has expired based on inactivity.
        Returns:
            bool: True if session has expired, False otherwise
        """
        return datetime.now() - self.last_activity > self.timeout_duration

    def reset_to_idle(self):
        """Reset the session to idle state and clear temporary context."""
        self.state = self.state_class.IDLE
        self.clear_context()
        self.last_activity = datetime.now()


class Client(TelegramClient, Generic[StateT, SessionT]):
    """
    Custom Telegram Client with conversation management and user session control.
    This client extends TelegramClient with additional functionalities for managing
    user conversations, session states, and persistent data storage.
    """
    def __init__(
            self,
            bot_token: str = "",
            plugins: Any | None = None,
            config: dict = None,
            admin_ids: list[int] | None = None,
            commands: dict[str, Any] = None,
            conversation_state: Type[StateT] = ConversationState,
            user_session: Type[SessionT] = UserSession,
            **kwargs
    ) -> None:
        """
        Initialize the Telegram client with conversation management capabilities.
        Args:
            bot_token (str): The bot token to authenticate with the Telegram API
            plugins (Any | None): Plugin configuration
            config (dict): Bot configuration dictionary
            admin_ids (list[int] | None): List of admin user IDs
            commands (dict[str, Any]): Bot commands configuration
            conversation_state (Type[StateT]): Class to use for conversation states
            user_session (Type[SessionT]): Class to use for user sessions
            **kwargs: Additional keyword arguments for TelegramClient
        """
        super().__init__(**kwargs)
        self.bot_token = bot_token
        self.plugins = plugins
        self.config = config
        self.admin_ids = admin_ids
        self.commands = commands
        self.conversation_state = conversation_state
        self.user_session = user_session
        self.drivers = {}
        self.users = {}
        self.chats = []
        self.user_sessions: Dict[int, Any] = {}
        self.conversation_handlers = {}

    def get_user_session(self, sender_id: int):
        """
        Get or create a user session for the given sender ID.
        Args:
            sender_id (int): Telegram user ID
        Returns:
            The user session object
        """
        if sender_id not in self.user_sessions:
            self.user_sessions[sender_id] = self.user_session(
                sender_id,
                self.conversation_state
            )
        return self.user_sessions[sender_id]

    def set_user_state(self, sender_id: int, state: StateT, context: Dict = None):
        """
        Set the conversation state for a specific user.
        Args:
            sender_id (int): Telegram user ID
            state: New conversation state
            context (Dict, optional): Additional context data
        """
        session = self.get_user_session(sender_id)
        session.set_state(state, context)
        logging.info(f"User {sender_id} state changed to {state.value if hasattr(state, 'value') else state}")

    def get_user_state(self, sender_id: int):
        """
        Get the current conversation state for a user.
        Args:
            sender_id (int): Telegram user ID
        Returns:
            Current conversation state
        """
        session = self.get_user_session(sender_id)
        return session.get_state()

    def set_user_context(self, sender_id: int, key: str, value: Any):
        """
        Set temporary context data for a user.
        Args:
            sender_id (int): Telegram user ID
            key (str): Context key
            value (Any): Value to store
        """
        session = self.get_user_session(sender_id)
        session.set_context(key, value)

    def get_user_context(self, sender_id: int, key: str, default: Any = None) -> Any:
        """
        Get temporary context data for a user.
        Args:
            sender_id (int): Telegram user ID
            key (str): Context key
            default (Any, optional): Default value if key not found
        Returns:
            Any: Context value or default
        """
        session = self.get_user_session(sender_id)
        return session.get_context(key, default)

    def clear_user_context(self, sender_id: int):
        """
        Clear temporary context data for a user.
        Args:
            sender_id (int): Telegram user ID
        """
        session = self.get_user_session(sender_id)
        session.clear_context()

    def set_user_data(self, sender_id: int, key: str, value: Any):
        """
        Set persistent data for a user.
        Args:
            sender_id (int): Telegram user ID
            key (str): Data key
            value (Any): Value to store
        """
        session = self.get_user_session(sender_id)
        session.set_data(key, value)

        if sender_id not in self.drivers:
            self.drivers[sender_id] = {}
        self.drivers[sender_id][key] = value

    def get_user_data(self, sender_id: int, key: str, default: Any = None) -> Any:
        """
        Get persistent data for a user.
        Args:
            sender_id (int): Telegram user ID
            key (str): Data key
            default (Any, optional): Default value if key not found
        Returns:
            Any: Data value or default
        """
        session = self.get_user_session(sender_id)
        return session.get_data(key, default)

    def reset_user_session(self, sender_id: int):
        """
        Reset a user's session to idle state.
        Args:
            sender_id (int): Telegram user ID
        """
        if sender_id in self.user_sessions:
            self.user_sessions[sender_id].reset_to_idle()
            logging.info(f"User {sender_id} session reset to idle")

    def is_user_in_conversation(self, sender_id: int) -> bool:
        """
        Check if a user is currently in an active conversation.
        Args:
            sender_id (int): Telegram user ID
        Returns:
            bool: True if user is in conversation, False otherwise
        """
        state = self.get_user_state(sender_id)
        idle_state = self.conversation_state.IDLE
        return state != idle_state

    def get_users_in_state(self, state) -> list[int]:
        """
        Get a list of user IDs currently in a specific conversation state.
        Args:
            state: The conversation state to filter by
        Returns:
            list[int]: List of user IDs in the specified state
        """
        return [
            user_id for user_id, session in self.user_sessions.items()
            if session.get_state() == state
        ]

    async def _cleanup_expired_sessions(self):
        """
        Background task to periodically clean up expired user sessions.
        This method runs continuously and removes sessions that have
        exceeded their timeout duration.
        """
        while True:
            logging.info("Starting session cleanup task...")
            try:
                expired_users = []
                for user_id, session in self.user_sessions.items():
                    if session.is_expired():
                        expired_users.append(user_id)

                for user_id in expired_users:
                    logging.info(f"Cleaning up expired session for user {user_id}")
                    self.reset_user_session(user_id)

                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logging.error(f"Error in session cleanup: {e}")
                await asyncio.sleep(300)

    async def ask_user(self, sender_id: int, question: str, state,
                       context: Dict = None, **kwargs) -> None:
        """
        Ask a question a user and set their conversation state to wait for a response.
        Args:
            sender_id (int): Telegram user ID
            question (str): Question text to send
            state: State to set while waiting for response
            context (Dict, optional): Additional context data
            **kwargs: Additional arguments for send_message
        """
        await self.send_message(sender_id, question, **kwargs)
        self.set_user_state(sender_id, state, context)

    async def handle_user_response(self, event, expected_state) -> bool:
        """
        Check if a user's response matches an expected conversation state.
        Args:
            event: Telegram event object
            expected_state: Expected conversation state
        Returns:
            bool: True if user is in expected state, False otherwise
        """
        current_state = self.get_user_state(event.sender_id)
        return current_state == expected_state

    def register_conversation_handler(self, state, handler_func):
        """
        Register a handler function for a specific conversation state.
        Args:
            state: Conversation state to handle
            handler_func: Function to call when a user is in this state
        """
        self.conversation_handlers[state] = handler_func

    async def process_conversation_message(self, event):
        """
        Process a message based on the user's current conversation state.
        Args:
            event: Telegram event object
        """
        sender_id = event.sender_id
        current_state = self.get_user_state(sender_id)

        if current_state in self.conversation_handlers:
            handler = self.conversation_handlers[current_state]
            await handler(self, event)

    async def get_admin_entity(self):
        """
        Retrieve the input entity for the first valid admin ID.
        This method iterates through the list of admin IDs and attempts to get the input entity
        for each one until it finds a valid entity or exhausts the list.
        Returns:
            The input entity of the first valid admin ID found, or None if no valid admin ID exists.
        """
        peer = None
        for entity in self.admin_ids:
            try:
                peer = await super().get_input_entity(entity)
            finally:
                if peer:
                    return peer

    async def send_message(self, chat_id: Any, message: str = '', **kwargs: Any):
        """
        Send a message to a specified chat.
        Args:
            chat_id (Any): The ID of the chat where the message should be sent
            message (str): The message content to send
            **kwargs (Any): Additional arguments to customize the message (e.g., buttons, parse_mode)
        Returns:
            The result of the send_message operation
        """
        return await super().send_message(chat_id, message, **kwargs)

    async def remove_messages(self, chat_id, message_ids: list[int] = None):
        """
        Delete a message or list of messages from a specified chat.
        Args:
            chat_id: The ID of the chat where the message is located
            message_ids (list[int], optional): The ID or list of the messages to delete
        """
        if not message_ids:
            logging.warning("Message ID is required to delete a message.")
            return

        try:
            await super().delete_messages(chat_id, message_ids)
        except MessageDeleteForbiddenError as e:
            logging.info(f"An error occurred while trying to delete the message: {e}")

    async def update_message(self, chat_id, message_id, message, **kwargs):
        """
        Edit an existing message in a specified chat.
        Args:
            chat_id: The ID of the chat where the message is located
            message_id: The ID of the message to edit
            message: The new content for the message
            **kwargs: Additional arguments to customize the message (e.g., buttons, parse_mode)
        Returns:
            The result of the edit_message operation
        """
        if not message_id:
            logging.warning("Message ID is required to edit a message.")
            return

        try:
            return await super().edit_message(chat_id, message_id, message, **kwargs)
        except Exception as e:
            logging.info(f"Error while editing message: {e}")

    async def inline_button(self, chat_id, line_buttons):
        """
        Create an inline button and send a message with it.
        This method constructs an inline button with the specified chat ID and line buttons,
        and sends a message containing that button to the specified chat.
        This is useful for creating interactive messages in Telegram chats.
        Args:
            chat_id: Chat ID for the button
            line_buttons: Button configuration
        Returns:
            Result of the send_message operation
        """
        buttons = [Button.inline(chat_id, line_buttons)]
        return await self.send_message(chat_id, buttons=buttons)

    async def register_commands(self):
        """
        Register bot commands for the admin and default scopes.
        This method retrieves the admin entity and sets the bot commands accordingly.
        If no valid admin ID is found, it logs a warning and exits.
        """
        admin_input_peer = await self.get_admin_entity()
        if not admin_input_peer:
            logging.warning(
                'No valid admin ID found or you haven\'t started a conversation with the bot yet. '
                'Please send a /start message to the bot and try again. Exiting...'
            )
            return

        admin_commands = self.commands.get('admin_commands', [])
        default_commands = self.commands.get('default_commands', [])

        await self(
            SetBotCommandsRequest(
                scope=BotCommandScopePeer(admin_input_peer),
                lang_code='',
                commands=admin_commands + default_commands
            )
        )

        await self(
            SetBotCommandsRequest(
                scope=BotCommandScopeDefault(),
                lang_code='',
                commands=default_commands
            )
        )

    async def upload_photo(self, photo_path):
        """
        Upload a photo to be used as bot profile picture.
        Args:
            photo_path: Path to the photo file
        Returns:
            Tuple of (photo_id, access_hash)
        """
        file = await self.upload_file(photo_path)
        photo = await self(
            UploadProfilePhotoRequest(
                file=file
            )
        )
        return photo.photo.id, photo.photo.access_hash

    async def get_bot_info(self) -> Any:
        """
        Retrieve the bot's information such as name, description, and profile picture.
        This method is intended to be called after the bot has started.
        Returns:
            Any: The bot's information, or None if retrieval fails
        """
        try:
            return await self(
                GetBotInfoRequest(
                    lang_code=self.config.get('lang', 'pt'),
                    bot=None  # None means the current bot
                )
            )
        except Exception as e:
            logging.error(f'Failed to retrieve bot info: {e}', exc_info=True)
            return None

    async def set_bot_info(self, data: dict = None) -> None:
        """
        Set the bot's information such as name, description, and profile picture.
        This method is intended to be called after the bot has started.
        Args:
            data (dict, optional): Bot information data
        """
        logo_path = self.config.get('logo', 'src/media/logo.png')
        about = self.config.get('about')
        description = self.config.get('description')

        bot_info = await self.get_bot_info()
        if not bot_info:
            logging.error('Bot info not found. Cannot update profile.')
            photo_id, access_hash = await self.upload_photo(
                photo_path=logo_path
            )
            input_photo = InputPhoto(
                id=photo_id,
                access_hash=access_hash,
                file_reference=b''
            )
            await self(
                UpdateProfilePhotoRequest(
                    id=input_photo
                )
            )

            try:
                logging.info('Updating bot profile...')
                await self(
                    SetBotInfoRequest(
                        bot=None,
                        lang_code=self.config.get('lang', 'pt'),
                        description=description,
                        about=about,
                    )
                )
                result = await self.get_bot_info()
                logging.info(f'Bot profile updated successfully: {result}')
            except Exception as e:
                logging.error(f'Failed to update bot profile: {e}', exc_info=True)

    async def keep_alive(self) -> None:
        """
        Keep the bot connected to the Telegram API.
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

    async def run(self) -> None:
        """
        Start the bot, load event handlers, and manage its lifecycle.
        Handles connection errors by attempting to reconnect automatically.
        """
        try:
            await self.start(bot_token=self.bot_token)
            plugin_loader: PluginLoader = PluginLoader(
                self,
                self.plugins
            )
            plugin_loader.load_plugins()
            await self.register_commands()
            await self.set_bot_info()
            logging.info('Starting Telegram bot!')
            await asyncio.gather(
                self.run_until_disconnected(),
                self.keep_alive(),
                self._cleanup_expired_sessions()
            )

        except ConnectionError:
            logging.error('Failed to connect to Telegram.')
            await asyncio.sleep(5)
            await self.run()

    async def shutdown(self) -> None:
        """
        Gracefully disconnect the bot from the Telegram API.
        Ensures proper cleanup of resources before exiting.
        """
        await self.disconnect()
        logging.info('Bot successfully disconnected.')

    def start_service(self) -> None:
        """
        Start the bot service and run it until interrupted.
        Handles cleanup upon keyboard interruption to ensure a graceful shutdown.
        """
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.run())
        except KeyboardInterrupt:
            logging.info(
                'Bot interrupted by user.\n'
                'Disconnecting...'
            )
            loop.run_until_complete(self.shutdown())