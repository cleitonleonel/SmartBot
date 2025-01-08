import logging
from pathlib import Path
from importlib import import_module
from app.paths import get_handlers_path


class PluginLoader:
    """
    A class responsible for dynamically loading, unloading, and managing event handlers (plugins)
    for a Telegram client using the Telethon library.

    Attributes:
        client (TelegramClient): The Telethon client instance.
        plugins (dict): Configuration for the plugins to be loaded.
    """

    def __init__(self, client, plugins=None):
        """
        Initialize the PluginLoader.

        Args:
            client (TelegramClient): The Telethon client instance.
            plugins (dict, optional): Plugin configuration. Defaults to an empty dictionary.
        """
        self.client = client
        self.plugins = plugins or {}

    def load_plugins(self):
        """
        Load and manage plugins based on the provided configuration.

        This method processes the plugin configuration, loads specified modules,
        and registers or removes handlers as needed.
        """
        plugins = self.plugins.copy()
        self._process_plugin_config(plugins)

        if not plugins.get("enabled", True):
            return

        root = get_handlers_path(
            plugins_dir=plugins["root"]
        )
        include = plugins.get("include", [])
        exclude = plugins.get("exclude", [])
        count = 0

        count = self._load_modules_from_path(root, include, count)
        count = self._unload_modules_from_path(root, exclude, count)

        if count > 0:
            logging.info(
                f'[{self.client.session}] Successfully loaded {count} plugin{"s" if count > 1 else ""} '
                f'from "{root}"'
            )
        else:
            logging.warning(f'[{self.client.session}] No plugins loaded from "{root}"')

    def _process_plugin_config(self, plugins):
        """
        Process and adjust the 'include' and 'exclude' configuration options.

        Args:
            plugins (dict): Plugin configuration.
        """
        for option in ["include", "exclude"]:
            if plugins.get(option, []):
                plugins[option] = [
                    (i.split()[0], i.split()[1:] or None) for i in plugins[option]
                ]

    def _load_modules_from_path(self, root, include, count):
        """
        Load modules from a specified path and register their handlers.

        Args:
            root (str): The root directory for the plugins.
            include (list): List of specific modules and handlers to include.
            count (int): Current count of loaded plugins.

        Returns:
            int: Updated count of loaded plugins.
        """
        if not include:
            for path in sorted(Path(root.replace(".", "/")).rglob("*.py")):
                module_path = '.'.join(path.parent.parts + (path.stem,))
                count += self._load_module(module_path)

        else:
            for path, handlers in include:
                module_path = root + "." + path
                count += self._load_module(module_path, handlers)

        return count

    def _unload_modules_from_path(self, root, exclude, count):
        """
        Unload modules and remove their handlers based on the configuration.

        Args:
            root (str): The root directory for the plugins.
            exclude (list): List of specific modules and handlers to exclude.
            count (int): Current count of loaded plugins.

        Returns:
            int: Updated count of loaded plugins.
        """

        for path, handlers in exclude:
            module_path = root + "." + path
            count = self._unload_module(module_path, handlers, count)

        return count

    def _load_module(self, module_path, handlers=None):
        """
        Load a single module and register its handlers.

        Args:
            module_path (str): The module path to load.
            handlers (list, optional): Specific handlers to register. Defaults to all handlers in the module.

        Returns:
            int: Number of successfully registered handlers.
        """
        try:
            module = import_module(module_path)
        except ImportError:
            logging.warning(
                f'[{self.client.session}] [LOAD] Ignoring non-existent module "{module_path}"'
            )
            return 0

        if "__path__" in dir(module):
            logging.warning(
                f'[{self.client.session}] [LOAD] Ignoring namespace "{module_path}"'
            )
            return 0

        handlers = handlers or vars(module).keys()

        return self._register_handlers(module, handlers)

    def _unload_module(self, module_path, handlers, count):
        """
        Unload a module and deregister its handlers.

        Args:
            module_path (str): The module path to unload.
            handlers (list): Specific handlers to deregister.
            count (int): Current count of loaded plugins.

        Returns:
            int: Updated count of loaded plugins.
        """
        try:
            module = import_module(module_path)
        except ImportError:
            logging.warning(
                f'[{self.client.session}] [UNLOAD] Ignoring non-existent module "{module_path}"'
            )
            return count

        handlers = handlers or vars(module).keys()

        return self._deregister_handlers(module, handlers, count)

    def _register_handlers(self, module, handlers):
        """
        Register handlers from a given module.

        Args:
            module (module): The Python module containing handlers.
            handlers (list): List of handler names to register.

        Returns:
            int: Number of successfully registered handlers.
        """
        count = 0
        for name in handlers:
            try:
                handler_group = getattr(module, name)
                if callable(handler_group) and getattr(handler_group, 'is_handler', False):
                    handler_info = getattr(handler_group, 'handler_info', {})
                    event = handler_info.get("event")

                    logging.info(f"Registering handler: {name}")
                    self.client.add_event_handler(handler_group, event)

                    logging.info(
                        f'[{self.client.session}] [LOAD] Registered handler "{name}" '
                        f'from "{module.__name__}"'
                    )
                    count += 1
            except Exception as e:
                logging.warning(
                    f'[{self.client.session}] [LOAD] Error while loading handler "{name}" '
                    f'from "{module.__name__}": {str(e)}'
                )

        return count

    def _deregister_handlers(self, module, handlers, count):
        """
        Deregister handlers from a given module.

        Args:
            module (module): The Python module containing handlers.
            handlers (list): List of handler names to deregister.
            count (int): Current count of loaded plugins.

        Returns:
            int: Updated count of loaded plugins.
        """
        for name in handlers:
            try:
                handler_group = getattr(module, name)
                if callable(handler_group) and getattr(handler_group, 'is_handler', False):
                    self.client.remove_event_handler(handler_group)
                    logging.info(
                        f'[{self.client.session}] [UNLOAD] Deregistered handler "{name}" '
                        f'from "{module.__name__}"'
                    )
                    count -= 1
            except Exception as e:
                logging.warning(
                    f'[{self.client.session}] [UNLOAD] Error while unloading handler "{name}" '
                    f'from "{module.__name__}": {str(e)}'
                )

        return count
