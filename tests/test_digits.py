import pytest

from digits import to_english, to_persian, to_words


def test_to_persian_converts_ascii_and_arabic_indic():
    assert to_persian("سال 2026 و ٢٠٢٧") == "سال ۲۰۲۶ و ۲۰۲۷"


def test_to_persian_keeps_digits_inside_latin_tokens():
    assert to_persian("نسخه v1.2 و H2O و 3D و utf-8") == "نسخه v1.2 و H2O و 3D و utf-8"


def test_to_persian_without_protection_converts_everything():
    assert to_persian("v1", protect_latin=False) == "v۱"


def test_to_english():
    assert to_english("۱۴۰۵ و ٢٠٢٦") == "1405 و 2026"


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (0, "صفر"),
        (5, "پنج"),
        (15, "پانزده"),
        (21, "بیست و یک"),
        (100, "صد"),
        (123, "صد و بیست و سه"),
        (1000, "هزار"),
        (1405, "هزار و چهارصد و پنج"),
        (2026, "دو هزار و بیست و شش"),
        (1_000_000, "یک میلیون"),
        (1_001_000, "یک میلیون و هزار"),
        (-7, "منفی هفت"),
    ],
)
def test_to_words(number, expected):
    assert to_words(number) == expected


def test_to_words_rejects_huge_numbers_and_non_ints():
    with pytest.raises(ValueError):
        to_words(10**15)
    with pytest.raises(TypeError):
        to_words("12")
