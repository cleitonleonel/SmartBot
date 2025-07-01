from collections import defaultdict

DELETE_KEY = "delete_queue"
MENU_KEY = "menu_stack"


def get_user_state(event) -> dict:
    """
    Returns the user's state dictionary (driver).
    Initializes it if it doesn't exist yet.
    """
    user_id = event.sender_id if hasattr(event, "sender_id") else event.chat_id
    client = event.client

    if not hasattr(client, "drivers"):
        event.client.drivers = {}

    if not isinstance(event.client.drivers.get(user_id), dict):
        event.client.drivers[user_id] = defaultdict(list)

    return event.client.drivers[user_id]
