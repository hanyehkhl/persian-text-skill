# Normalization rules

Every rule below is applied by `scripts/normalize.py` outside protected
segments (fenced and inline code, URLs, e-mails, HTML tags, link targets).

## Letters

| Input | Output | Note |
|---|---|---|
| ي (U+064A), ى (U+0649) | ی (U+06CC) | Arabic yeh, alef maksura |
| ك (U+0643), ڪ (U+06AA) | ک (U+06A9) | Arabic kaf |
| ة (U+0629) | ه (U+0647) | teh marbuta |
| ھ (U+06BE) | ه (U+0647) | do-chashmi heh from wrong keyboards |
| ـ (U+0640) | removed | tatweel / kashida |

Diacritics (U+064B to U+065F, U+0670) are kept unless `--strip-diacritics`.

## Half-space (ZWNJ, U+200C)

Inserted only when a space separates a Persian letter and one of these forms:

| Rule | Example |
|---|---|
| `می` / `نمی` + word | می رود → می‌رود |
| word + `ها` / `های` / `هایی` | کتاب ها → کتاب‌ها |
| word + `تر` / `ترین` | بزرگ تر → بزرگ‌تر |
| `ه` + `ی` (ezafe or ye) | خانه ی بزرگ → خانه‌ی بزرگ |

Cleanup: repeated ZWNJ collapse to one; ZWNJ next to spaces or at line
edges is removed; runs of spaces between words collapse to one space
(indentation and Markdown trailing spaces are untouched).

### Known limits and false positives

- `می` as a noun (wine) followed by a word will be joined.
- `ام`, `ای`, `ات`, `اش` suffixes (رفته ام → رفته‌ام) are **not** handled
  because `ای` is also a standalone word. Fix manually when needed.
- `تری` is not handled (ambiguous with the word for "wet").
- Words that merely end in `ها` as a separate token are joined, which is almost
  always correct.

## Punctuation

Applied only directly after a Persian letter or Persian digit:

- `,` → `،`, `;` → `؛`, `?` → `؟`
- spaces before `،` `؛` `؟` removed; one space added after `،` `؛` when a
  letter follows immediately

`.` `:` `!` are never changed, because they appear in numbers, times,
file names and abbreviations.

## Digits

- `fa`: ASCII and Arabic-Indic (٠١٢٣) become Persian (۰۱۲۳). Digits inside
  Latin tokens (`v1.2`, `H2O`, `3D`, `utf-8`) stay ASCII.
- `en`: Persian and Arabic-Indic digits become ASCII.
- `keep`: untouched.

## Jalali dates

33-year arithmetic algorithm, exact for 1178 to 1633 AP (about 1799 to
2254 CE). Leap years follow the same cycle (for example 1403 is leap, 1404 is
not). Month names: فروردین، اردیبهشت، خرداد، تیر، مرداد، شهریور، مهر، آبان،
آذر، دی، بهمن، اسفند. Weeks start on شنبه.

## Number words

`digits.py words N` supports integers up to 999 تریلیون, negatives (منفی),
and follows Persian usage: 1000 is «هزار» (no «یک»), 1,000,000 is
«یک میلیون».
