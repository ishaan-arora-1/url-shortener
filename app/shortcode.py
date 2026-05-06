"""Base62 encoding used to turn a numeric row id into a short, URL-safe code."""

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
BASE = len(ALPHABET)


def encode(number: int) -> str:
    if number < 0:
        raise ValueError("cannot encode a negative number")
    if number == 0:
        return ALPHABET[0]

    chars: list[str] = []
    while number > 0:
        number, remainder = divmod(number, BASE)
        chars.append(ALPHABET[remainder])
    return "".join(reversed(chars))


def decode(code: str) -> int:
    number = 0
    for char in code:
        number = number * BASE + ALPHABET.index(char)
    return number
