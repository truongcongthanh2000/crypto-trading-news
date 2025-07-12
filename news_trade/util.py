def is_command_trade(text: str | None) -> bool:
    return text is not None and any(pattern in text.lower() for pattern in ["short", "long", "buy", "sell", "leverage", "sl"])