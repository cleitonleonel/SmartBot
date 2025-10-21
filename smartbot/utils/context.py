from collections import defaultdict

DELETE_KEY = "delete_queue"
MENU_KEY = "menu_stack"
BACK_TO_HOME = """
🏠 **Você voltou ao menu inicial!**

✨ Dica: a qualquer momento, você pode:
• Digitar **/start** para reiniciar o bot  
• Usar o **menu de comandos** abaixo  
• Ou enviar manualmente qualquer comando da lista disponível

🔍 Explore as opções e continue interagindo com o bot!
"""


def get_user_driver(event) -> dict:
    """
    Returns the user's dictionary (driver).
    Initializes it if it doesn't exist yet.
    """
    user_id = event.sender_id if hasattr(event, "sender_id") else event.chat_id
    client = event.client

    if not hasattr(client, "drivers"):
        event.client.drivers = {}

    if not isinstance(event.client.drivers.get(user_id), dict):
        event.client.drivers[user_id] = defaultdict(list)

    return event.client.drivers[user_id]
