from normalize import ZWNJ, main, normalize


def test_arabic_letters_become_persian():
    assert normalize("علي كتاب خواندى") == "علی کتاب خواندی"


def test_tatweel_removed_and_diacritics_optional():
    assert normalize("سلــام") == "سلام"
    assert normalize("كِتَاب") == "کِتَاب"
    assert normalize("كِتَاب", strip_diacritics=True) == "کتاب"


def test_mi_prefix_halfspace():
    assert normalize("او می رود و نمی داند") == f"او می{ZWNJ}رود و نمی{ZWNJ}داند"


def test_mi_not_joined_to_latin_or_inside_words():
    assert normalize("می abc") == "می abc"
    assert normalize("دمی رفت") == "دمی رفت"


def test_plural_and_comparative_halfspace():
    assert normalize("کتاب ها و خانه های بزرگ تر") == (
        f"کتاب{ZWNJ}ها و خانه{ZWNJ}های بزرگ{ZWNJ}تر"
    )
    assert normalize("بهترین ها") == f"بهترین{ZWNJ}ها"


def test_ye_after_heh():
    assert normalize("خانه ی بزرگ") == f"خانه{ZWNJ}ی بزرگ"


def test_halfspace_can_be_disabled():
    assert normalize("می رود", halfspace=False) == "می رود"


def test_stray_zwnj_cleaned():
    assert normalize(f"سلام{ZWNJ} دنیا") == "سلام دنیا"
    assert normalize(f"کتاب{ZWNJ}{ZWNJ}ها") == f"کتاب{ZWNJ}ها"


def test_spaces_collapsed_but_indentation_preserved():
    assert normalize("سلام    دنیا") == "سلام دنیا"
    assert normalize("    - سلام") == "    - سلام"


def test_digit_modes():
    assert normalize("سال 2026", digits="fa") == "سال ۲۰۲۶"
    assert normalize("سال ۲۰۲۶", digits="en") == "سال 2026"
    assert normalize("سال 2026", digits="keep") == "سال 2026"


def test_punctuation_converted_in_persian_context():
    assert normalize("چرا?") == "چرا؟"
    assert normalize("سلام,دنیا") == "سلام،دنیا".replace("،", "، ")
    assert normalize("سلام ، دنیا") == "سلام، دنیا"


def test_punctuation_untouched_in_latin_context():
    assert normalize("Hello, world? yes; no") == "Hello, world? yes; no"


def test_punctuation_can_be_disabled():
    assert normalize("چرا?", punctuation=False) == "چرا?"


def test_code_urls_and_tags_are_protected():
    text = (
        "ك `ك ي 123` و https://example.com/ي?q=ك ?\n"
        "```py\nprint('ك ي', 2026)\n```\n"
        "[ك](https://x.org/ي) <a href=\"ك\">ي</a>"
    )
    result = normalize(text, digits="fa")
    assert "`ك ي 123`" in result
    assert "https://example.com/ي?q=ك" in result
    assert "print('ك ي', 2026)" in result
    assert "(https://x.org/ي)" in result
    assert '<a href="ك">' in result
    assert result.startswith("ک ")  # text outside code is normalized


def test_idempotent():
    text = "او می رود و کتاب ها را می خواند, چرا?\n```\nكد\n```"
    once = normalize(text, digits="fa")
    assert normalize(once, digits="fa") == once


def test_invalid_digits_mode():
    import pytest

    with pytest.raises(ValueError):
        normalize("x", digits="bad")


def test_cli_in_place_preserves_crlf(tmp_path):
    path = tmp_path / "doc.md"
    path.write_bytes("می رود\r\nعلي\r\n".encode("utf-8"))
    assert main([str(path), "--in-place"]) == 0
    assert path.read_bytes() == f"می{ZWNJ}رود\r\nعلی\r\n".encode("utf-8")


def test_cli_missing_file_returns_error(tmp_path, capsys):
    assert main([str(tmp_path / "missing.md")]) == 1
    assert "cannot read input" in capsys.readouterr().err
