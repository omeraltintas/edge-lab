import secrets

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def new_code(length: int = 7) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))
