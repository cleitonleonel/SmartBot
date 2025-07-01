from telethon import Button


def build_inline_buttons(options: list[tuple[str, bytes]], cols: int = 2) -> list:
    return [
        [Button.inline(label, data) for label, data in options[i:i+cols]]
        for i in range(0, len(options), cols)
    ]
