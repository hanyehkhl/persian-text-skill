#!/usr/bin/env python3
"""Digit conversion and number-to-words for Persian text.

Usage:
    digits.py fa    "سال 2026"          # -> سال ۲۰۲۶
    digits.py en    "سال ۲۰۲۶"          # -> سال 2026
    digits.py words 1405                # -> هزار و چهارصد و پنج

Reads from stdin when no text argument is given. Standard library only.
"""

from __future__ import annotations

import re
import sys

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_INDIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
ASCII_DIGITS = "0123456789"

_TO_PERSIAN = str.maketrans(ASCII_DIGITS + ARABIC_INDIC_DIGITS, PERSIAN_DIGITS * 2)
_TO_ASCII = str.maketrans(PERSIAN_DIGITS + ARABIC_INDIC_DIGITS, ASCII_DIGITS * 2)

# A "word" containing at least one Latin letter (v1.2, H2O, 3D, utf-8, file_01).
# Digits inside such tokens belong to Latin/technical text and must stay ASCII.
_LATIN_TOKEN = re.compile(r"[A-Za-z0-9_]*[A-Za-z_][A-Za-z0-9_.\-]*")
_ASCII_DIGIT_RUN = re.compile(r"[0-9]+")


def to_persian(text: str, *, protect_latin: bool = True) -> str:
    """Convert ASCII and Arabic-Indic digits to Persian digits.

    With ``protect_latin`` (default) digits that are part of a Latin token such
    as ``v1.2``, ``H2O`` or ``3D`` are left untouched.
    """
    text = text.translate(
        str.maketrans(ARABIC_INDIC_DIGITS, PERSIAN_DIGITS)
    )  # always safe: Arabic-Indic digits never occur in Latin tokens
    if not protect_latin:
        return text.translate(_TO_PERSIAN)

    out: list[str] = []
    last = 0
    for match in _LATIN_TOKEN.finditer(text):
        out.append(_ASCII_DIGIT_RUN.sub(lambda m: m.group().translate(_TO_PERSIAN), text[last : match.start()]))
        out.append(match.group())
        last = match.end()
    out.append(_ASCII_DIGIT_RUN.sub(lambda m: m.group().translate(_TO_PERSIAN), text[last:]))
    return "".join(out)


def to_english(text: str) -> str:
    """Convert Persian and Arabic-Indic digits to ASCII digits."""
    return text.translate(_TO_ASCII)


# --- number to words -------------------------------------------------------

_ONES = ["", "یک", "دو", "سه", "چهار", "پنج", "شش", "هفت", "هشت", "نه"]
_TEENS = [
    "ده", "یازده", "دوازده", "سیزده", "چهارده",
    "پانزده", "شانزده", "هفده", "هجده", "نوزده",
]
_TENS = ["", "", "بیست", "سی", "چهل", "پنجاه", "شصت", "هفتاد", "هشتاد", "نود"]
_HUNDREDS = [
    "", "صد", "دویست", "سیصد", "چهارصد",
    "پانصد", "ششصد", "هفتصد", "هشتصد", "نهصد",
]
_SCALES = ["", "هزار", "میلیون", "میلیارد", "تریلیون"]
MAX_WORDS_VALUE = 10 ** (3 * len(_SCALES)) - 1  # 999 تریلیون ...


def _below_thousand(n: int) -> str:
    parts: list[str] = []
    hundreds, rest = divmod(n, 100)
    if hundreds:
        parts.append(_HUNDREDS[hundreds])
    if rest:
        if rest < 10:
            parts.append(_ONES[rest])
        elif rest < 20:
            parts.append(_TEENS[rest - 10])
        else:
            tens, ones = divmod(rest, 10)
            parts.append(_TENS[tens])
            if ones:
                parts.append(_ONES[ones])
    return " و ".join(parts)


def to_words(number: int) -> str:
    """Spell an integer in Persian, e.g. ``2026`` -> ``دو هزار و بیست و شش``."""
    if not isinstance(number, int) or isinstance(number, bool):
        raise TypeError("to_words expects an int")
    if abs(number) > MAX_WORDS_VALUE:
        raise ValueError(f"number out of range (max {MAX_WORDS_VALUE})")
    if number == 0:
        return "صفر"
    if number < 0:
        return "منفی " + to_words(-number)

    groups: list[int] = []
    while number:
        number, group = divmod(number, 1000)
        groups.append(group)

    parts: list[str] = []
    for index in range(len(groups) - 1, -1, -1):
        group = groups[index]
        if not group:
            continue
        scale = _SCALES[index]
        if index == 1 and group == 1:  # 1000 is "هزار", not "یک هزار"
            parts.append(scale)
        else:
            text = _below_thousand(group)
            parts.append(f"{text} {scale}".strip())
    return " و ".join(parts)


# --- CLI -------------------------------------------------------------------


def _read_text(args: list[str]) -> str:
    if args:
        return " ".join(args)
    return sys.stdin.read()


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    for stream in (sys.stdin, sys.stdout):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    if not argv or argv[0] not in {"fa", "en", "words"}:
        print(__doc__, file=sys.stderr)
        return 2

    mode, rest = argv[0], argv[1:]
    text = _read_text(rest)
    if mode == "fa":
        sys.stdout.write(to_persian(text))
    elif mode == "en":
        sys.stdout.write(to_english(text))
    else:
        try:
            value = int(to_english(text).strip().replace(",", "").replace("٬", ""))
            print(to_words(value))
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
