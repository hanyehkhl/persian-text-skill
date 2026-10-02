#!/usr/bin/env python3
"""Normalize Persian text: Arabic letters, half-spaces, digits, punctuation.

Usage:
    normalize.py [FILE] [options]        # reads stdin when FILE is omitted

Options:
    --digits {fa,en,keep}    digit style (default: keep)
    --strip-diacritics       remove harakat (fatha, kasra, ...)
    --no-halfspace           skip half-space (ZWNJ) insertion rules
    --no-punctuation         skip , ; ? -> ، ؛ ؟ conversion and spacing
    --in-place               rewrite FILE instead of printing

Markdown code blocks, inline code, URLs, e-mails, HTML tags and link targets
are never modified. Standard library only.
"""

from __future__ import annotations

import argparse
import re
import sys

from digits import to_english, to_persian

ZWNJ = "‌"

# One Persian/Arabic-script letter (without diacritics and digits).
_L = "ء-غف-يپچژکگیۀ"
_LETTER = f"[{_L}]"

_CHAR_MAP = str.maketrans(
    {
        "ي": "ی",  # ي  Arabic yeh        -> ی
        "ى": "ی",  # ى  alef maksura      -> ی
        "ك": "ک",  # ك  Arabic kaf        -> ک
        "ڪ": "ک",  # ڪ  swash kaf         -> ک
        "ة": "ه",  # ة  teh marbuta       -> ه
        "ھ": "ه",  # ھ  do-chashmi heh    -> ه
        "ـ": None,      # ـ  tatweel (kashida) -> removed
    }
)
_DIACRITICS = re.compile("[ً-ٰٟ]")

# Segments that must never be touched.
_PROTECTED = re.compile(
    r"""
      (?P<fence>(?:```|~~~).*?(?:```|~~~)) # fenced code blocks
    | (?P<inline>`[^`\n]*`)                # inline code
    | (?P<linkurl>(?<=\])\([^)\s]*\))      # markdown link target
    | (?P<url>(?:https?|ftp)://[^\s<>"')]+) # URLs
    | (?P<mail>[\w.+-]+@[\w-]+(?:\.[\w-]+)+) # e-mail addresses
    | (?P<tag><[A-Za-z/!][^>\n]*>)         # HTML tags
    """,
    re.VERBOSE | re.DOTALL,
)

# --- half-space rules (conservative; see references/rules.md) ---------------
_RE_MI = re.compile(rf"(?<!{_LETTER})(ن?می)[ \t]+(?={_LETTER})")
_RE_PLURAL = re.compile(rf"(?<={_LETTER})[ \t]+(ها|های|هایی)(?!{_LETTER})")
_RE_COMPARATIVE = re.compile(rf"(?<={_LETTER})[ \t]+(تر|ترین)(?!{_LETTER})")
_RE_EZAFE_YE = re.compile(rf"(?<=ه)[ \t]+(ی)(?!{_LETTER})")

# --- whitespace / ZWNJ cleanup ----------------------------------------------
_RE_MULTI_SPACE = re.compile(r"(?<=\S)[ \t]{2,}(?=\S)")
_RE_MULTI_ZWNJ = re.compile(f"{ZWNJ}{{2,}}")
_RE_ZWNJ_BEFORE_SPACE = re.compile(f"{ZWNJ}+(?=\\s|$)", re.MULTILINE)
_RE_ZWNJ_AFTER_SPACE = re.compile(f"(?:(?<=\\s)|^){ZWNJ}+", re.MULTILINE)

# --- punctuation -------------------------------------------------------------
_PUNCT_MAP = {",": "،", ";": "؛", "?": "؟"}
_RE_LATIN_PUNCT = re.compile(rf"(?<=[{_L}۰-۹])([,;?])")
_RE_SPACE_BEFORE_PUNCT = re.compile(rf"(?<={_LETTER})[ \t]+([،؛؟])")
_RE_NO_SPACE_AFTER_PUNCT = re.compile(rf"([،؛])(?={_LETTER})")


def _normalize_segment(
    text: str,
    *,
    digits: str,
    strip_diacritics: bool,
    halfspace: bool,
    punctuation: bool,
) -> str:
    text = text.translate(_CHAR_MAP)
    if strip_diacritics:
        text = _DIACRITICS.sub("", text)

    if digits == "fa":
        text = to_persian(text)
    elif digits == "en":
        text = to_english(text)

    if punctuation:
        text = _RE_LATIN_PUNCT.sub(lambda m: _PUNCT_MAP[m.group(1)], text)
        text = _RE_SPACE_BEFORE_PUNCT.sub(r"\1", text)
        text = _RE_NO_SPACE_AFTER_PUNCT.sub(r"\1 ", text)

    if halfspace:
        text = _RE_MI.sub(rf"\1{ZWNJ}", text)
        text = _RE_PLURAL.sub(rf"{ZWNJ}\1", text)
        text = _RE_COMPARATIVE.sub(rf"{ZWNJ}\1", text)
        text = _RE_EZAFE_YE.sub(rf"{ZWNJ}\1", text)

    text = _RE_MULTI_ZWNJ.sub(ZWNJ, text)
    text = _RE_ZWNJ_BEFORE_SPACE.sub("", text)
    text = _RE_ZWNJ_AFTER_SPACE.sub("", text)
    text = _RE_MULTI_SPACE.sub(" ", text)
    return text


def normalize(
    text: str,
    *,
    digits: str = "keep",
    strip_diacritics: bool = False,
    halfspace: bool = True,
    punctuation: bool = True,
) -> str:
    """Normalize ``text``; protected segments (code, URLs, ...) are preserved."""
    if digits not in {"fa", "en", "keep"}:
        raise ValueError(f"digits must be 'fa', 'en' or 'keep', got {digits!r}")

    options = dict(
        digits=digits,
        strip_diacritics=strip_diacritics,
        halfspace=halfspace,
        punctuation=punctuation,
    )
    # Segments are normalized independently, so a protected span acts as a
    # hard boundary for every rule (no rule ever reaches across code or URLs).
    out: list[str] = []
    last = 0
    for match in _PROTECTED.finditer(text):
        out.append(_normalize_segment(text[last : match.start()], **options))
        out.append(match.group())
        last = match.end()
    out.append(_normalize_segment(text[last:], **options))
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdin, sys.stdout):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", nargs="?", help="input file (default: stdin)")
    parser.add_argument("--digits", choices=["fa", "en", "keep"], default="keep")
    parser.add_argument("--strip-diacritics", action="store_true")
    parser.add_argument("--no-halfspace", action="store_true")
    parser.add_argument("--no-punctuation", action="store_true")
    parser.add_argument("--in-place", action="store_true")
    args = parser.parse_args(argv)

    if args.in_place and not args.file:
        parser.error("--in-place requires FILE")

    try:
        if args.file:
            # newline="" keeps CRLF/LF line endings exactly as in the file.
            with open(args.file, encoding="utf-8", newline="") as handle:
                source = handle.read()
        else:
            source = sys.stdin.read()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"error: cannot read input: {exc}", file=sys.stderr)
        return 1

    result = normalize(
        source,
        digits=args.digits,
        strip_diacritics=args.strip_diacritics,
        halfspace=not args.no_halfspace,
        punctuation=not args.no_punctuation,
    )

    if args.in_place:
        # Path.write_text(newline=...) needs Python 3.10+, so use open() for 3.9.
        with open(args.file, "w", encoding="utf-8", newline="") as handle:
            handle.write(result)
    else:
        sys.stdout.write(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
