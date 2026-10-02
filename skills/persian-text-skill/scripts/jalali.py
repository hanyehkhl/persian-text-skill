#!/usr/bin/env python3
"""Gregorian <-> Jalali (Solar Hijri) date conversion.

Usage:
    jalali.py to-jalali    2026-10-02    # -> ۱۴۰۵/۰۷/۱۰ (شنبه ... )
    jalali.py to-gregorian 1405-07-10    # -> 2026-10-02
    jalali.py today

Options: --digits {fa,en} (default fa), --long (day month-name year).
Persian/Arabic digits are accepted in the input. Standard library only.

The 33-year arithmetic algorithm used here matches the official calendar for
years 1178-1633 AP (roughly 1799-2254 CE), which covers practical use.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date

from digits import to_english, to_persian

MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]
# datetime.weekday(): Monday == 0
WEEKDAYS = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه", "یکشنبه"]

_G_DAYS_BEFORE_MONTH = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]


def gregorian_to_jalali(gy: int, gm: int, gd: int) -> tuple[int, int, int]:
    date(gy, gm, gd)  # validates the input
    gy2 = gy + 1 if gm > 2 else gy
    days = (
        355666
        + 365 * gy
        + (gy2 + 3) // 4
        - (gy2 + 99) // 100
        + (gy2 + 399) // 400
        + gd
        + _G_DAYS_BEFORE_MONTH[gm - 1]
    )
    jy = -1595 + 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm, jd = 1 + days // 31, 1 + days % 31
    else:
        jm, jd = 7 + (days - 186) // 30, 1 + (days - 186) % 30
    return jy, jm, jd


def jalali_to_gregorian(jy: int, jm: int, jd: int) -> tuple[int, int, int]:
    if not 1 <= jm <= 12:
        raise ValueError(f"invalid Jalali month: {jm}")
    max_day = 31 if jm <= 6 else 30 if jm <= 11 else (30 if is_leap(jy) else 29)
    if not 1 <= jd <= max_day:
        raise ValueError(f"invalid Jalali day: {jy}/{jm}/{jd}")

    jy += 1595
    days = (
        -355668
        + 365 * jy
        + (jy // 33) * 8
        + ((jy % 33) + 3) // 4
        + jd
        + ((jm - 1) * 31 if jm < 7 else (jm - 7) * 30 + 186)
    )
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    february = 29 if (gy % 4 == 0 and gy % 100 != 0) or gy % 400 == 0 else 28
    month_lengths = [31, february, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 0
    while gm < 12 and gd > month_lengths[gm]:
        gd -= month_lengths[gm]
        gm += 1
    return gy, gm + 1, gd


def is_leap(jy: int) -> bool:
    """True when Esfand has 30 days in Jalali year ``jy``."""
    # Compare the Gregorian dates of 1 Farvardin in consecutive years. Month 1
    # never consults is_leap in jalali_to_gregorian, so there is no recursion.
    this_year = date(*jalali_to_gregorian(jy, 1, 1))
    next_year = date(*jalali_to_gregorian(jy + 1, 1, 1))
    return (next_year - this_year).days == 366


def weekday_name(d: date) -> str:
    return WEEKDAYS[d.weekday()]


def format_jalali(
    jy: int, jm: int, jd: int, *, long: bool = False, persian_digits: bool = True
) -> str:
    text = f"{jd} {MONTHS[jm - 1]} {jy}" if long else f"{jy:04d}/{jm:02d}/{jd:02d}"
    return to_persian(text) if persian_digits else text


_DATE_RE = re.compile(r"^\s*(\d{1,4})\D+(\d{1,2})\D+(\d{1,4})\s*$")


def parse_date_parts(text: str) -> tuple[int, int, int]:
    match = _DATE_RE.match(to_english(text))
    if not match:
        raise ValueError(f"cannot parse date: {text!r} (expected YYYY-MM-DD)")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdin, sys.stdout):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=["to-jalali", "to-gregorian", "today"])
    parser.add_argument("value", nargs="?", help="date as YYYY-MM-DD")
    parser.add_argument("--digits", choices=["fa", "en"], default="fa")
    parser.add_argument("--long", action="store_true", help="e.g. ۱۰ مهر ۱۴۰۵")
    args = parser.parse_args(argv)

    persian = args.digits == "fa"
    try:
        if args.command == "today":
            today = date.today()
            jy, jm, jd = gregorian_to_jalali(today.year, today.month, today.day)
            label = format_jalali(jy, jm, jd, long=args.long, persian_digits=persian)
            print(f"{label} ({weekday_name(today)})")
        elif args.value is None:
            parser.error("a date value is required")
        elif args.command == "to-jalali":
            gy, gm, gd = parse_date_parts(args.value)
            jy, jm, jd = gregorian_to_jalali(gy, gm, gd)
            label = format_jalali(jy, jm, jd, long=args.long, persian_digits=persian)
            print(f"{label} ({weekday_name(date(gy, gm, gd))})")
        else:
            jy, jm, jd = parse_date_parts(args.value)
            gy, gm, gd = jalali_to_gregorian(jy, jm, jd)
            print(f"{gy:04d}-{gm:02d}-{gd:02d}")  # Gregorian output stays ASCII
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
