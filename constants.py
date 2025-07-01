from telethon.tl.types import BotCommand

# Comandos disponíveis apenas para administradores
ADMIN_COMMANDS = [
    BotCommand(
        command="restart",
        description="Reiniciar o bot e limpar o cache."
    ),
    BotCommand(
        command="broadcast",
        description="Enviar uma mensagem para todos os usuários."
    ),
]

# Comandos disponíveis para todos os usuários
DEFAULT_COMMANDS = [
    BotCommand(
        command="start",
        description="Iniciar ou reiniciar uma conversa com o bot."
    ),
    BotCommand(
        command="help",
        description="Listar os comandos disponíveis."
    ),
    BotCommand(
        command="status",
        description="Exibir o status atual do bot."
    ),
    BotCommand(
        command="settings",
        description="Ajustar preferências ou configurações do usuário."
    ),
    BotCommand(
        command="clear",
        description="Limpar mensagens ou cache local."
    ),
]
