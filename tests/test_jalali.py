from datetime import date, timedelta

import pytest

from jalali import (
    format_jalali,
    gregorian_to_jalali,
    is_leap,
    jalali_to_gregorian,
    parse_date_parts,
)

# Well-known Nowruz dates (1 Farvardin).
NOWRUZ = [
    ((2023, 3, 21), (1402, 1, 1)),
    ((2024, 3, 20), (1403, 1, 1)),
    ((2025, 3, 21), (1404, 1, 1)),
    ((2026, 3, 21), (1405, 1, 1)),
]


@pytest.mark.parametrize(("greg", "jal"), NOWRUZ)
def test_nowruz_round_trip(greg, jal):
    assert gregorian_to_jalali(*greg) == jal
    assert jalali_to_gregorian(*jal) == greg


def test_known_mid_year_date():
    assert gregorian_to_jalali(2026, 10, 2) == (1405, 7, 10)


def test_leap_years():
    assert is_leap(1403)
    assert not is_leap(1404)
    assert jalali_to_gregorian(1403, 12, 30) == (2025, 3, 20)


def test_invalid_leap_day_rejected():
    with pytest.raises(ValueError):
        jalali_to_gregorian(1404, 12, 30)


def test_invalid_inputs_rejected():
    with pytest.raises(ValueError):
        jalali_to_gregorian(1405, 13, 1)
    with pytest.raises(ValueError):
        gregorian_to_jalali(2026, 2, 30)


def test_full_range_round_trip():
    start = date(1990, 1, 1)
    for offset in range(0, 365 * 60, 7):
        d = start + timedelta(days=offset)
        j = gregorian_to_jalali(d.year, d.month, d.day)
        assert jalali_to_gregorian(*j) == (d.year, d.month, d.day)


def test_consecutive_days_are_consecutive_in_jalali():
    d = date(2024, 1, 1)
    previous = gregorian_to_jalali(d.year, d.month, d.day)
    for _ in range(1500):
        d += timedelta(days=1)
        current = gregorian_to_jalali(d.year, d.month, d.day)
        if current[:2] == previous[:2]:
            assert current[2] == previous[2] + 1
        else:
            assert current[2] == 1
        previous = current


def test_format():
    assert format_jalali(1405, 7, 10) == "۱۴۰۵/۰۷/۱۰"
    assert format_jalali(1405, 7, 10, long=True) == "۱۰ مهر ۱۴۰۵"
    assert format_jalali(1405, 7, 10, persian_digits=False) == "1405/07/10"


def test_parse_accepts_persian_digits_and_separators():
    assert parse_date_parts("۱۴۰۵/۰۷/۱۰") == (1405, 7, 10)
    assert parse_date_parts("2026-10-02") == (2026, 10, 2)
    with pytest.raises(ValueError):
        parse_date_parts("not a date")
