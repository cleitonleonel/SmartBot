from typing import Callable, Any

class ClientHandler:
    """
    Decorator to register events on the Telegram client.
    """

    def __init__(self) -> None:
        """
        Initializes the handler decorator.
        """

        self.event = None

    def on(self, event: Any) -> Callable:
        """
        Initializes the handler decorator with a specific event.

        :param event: The type of event (e.g., NewMessage()).
        :return: A decorator function that associates the event with the function.
        """

        def decorator(func: Callable):
            """
            Marks the function as a handler and adds relevant information.

            :param func: The function to be decorated as an event handler.
            :return: The decorated function with handler metadata.
            """
            func.is_handler = True
            func.handler_info = {
                "event": event
            }
            return func

        return decorator

    def __call__(self, func: Callable) -> Callable:
        """
        Marks the function as a handler directly using the stored event.

        :param func: The function to be decorated as an event handler.
        :return: The decorated function with handler metadata.
        """

        return self.on(self.event)(func)

