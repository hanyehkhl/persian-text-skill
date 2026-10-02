---
name: persian-text-skill
description: Cleans and normalizes Persian (Farsi) text. Fixes Arabic ي/ك letters, half-spaces (نیم‌فاصله), digits (۱۲۳ vs 123), punctuation (، ؛ ؟) and spacing, converts Gregorian and Jalali (شمسی) dates, and spells numbers in Persian words. Use when the user writes, edits, reviews or publishes Persian or RTL text, Markdown or docs, or mentions نیم‌فاصله, اعداد فارسی, تاریخ شمسی, تمیزکاری متن فارسی.
license: MIT
compatibility: Requires Python 3.9+ (standard library only, no network access).
metadata:
  author: hanieh
  version: "1.0.0"
  tags: "persian,farsi,rtl,text-normalization,jalali"
---

# Persian Text Skill

Deterministic helpers for the mechanical parts of Persian typography. The
scripts do the rule-based work; you decide which operations fit the request and
review the result.

## When to Use

- The user asks to fix, clean, proofread or standardize Persian text or Markdown.
- Text shows Arabic letters (ي ك ة), missing or wrong half-spaces, mixed digit
  styles, or Latin punctuation (`,` `?` `;`) inside Persian sentences.
- A Gregorian date must become Jalali (or the reverse), or a number must be
  written in words (cheques, contracts, formal text).

Do not use it to translate, rewrite style or fix grammar. This skill only
normalizes. Combine it with normal editing when those are needed.

## Procedure

All commands run from this skill's directory. Use `python` or `python3`,
whichever exists. Scripts read UTF-8 and write UTF-8.

1. **Pick the digit style first.** Ask only if unclear. Defaults: Persian
   digits (`fa`) for prose, English digits (`en`) for technical docs, code,
   tables and data, `keep` when unsure.
2. **Normalize text** (stdin or file):

   ```bash
   python scripts/normalize.py input.md --digits fa            # print result
   python scripts/normalize.py input.md --digits fa --in-place # rewrite file
   echo "او می رود, چرا?" | python scripts/normalize.py
   ```

   Flags: `--digits {fa,en,keep}`, `--strip-diacritics`, `--no-halfspace`,
   `--no-punctuation`. Code blocks, inline code, URLs, e-mails, HTML tags and
   Markdown link targets are never modified.
3. **Convert digits only:** `python scripts/digits.py fa "سال 2026"` or
   `python scripts/digits.py en "۱۴۰۵"`.
4. **Spell a number:** `python scripts/digits.py words 1405`
   gives `هزار و چهارصد و پنج`.
5. **Convert dates:**

   ```bash
   python scripts/jalali.py to-jalali 2026-10-02      # ۱۴۰۵/۰۷/۱۰ (شنبه)
   python scripts/jalali.py to-jalali 2026-10-02 --long  # ۱۰ مهر ۱۴۰۵
   python scripts/jalali.py to-gregorian 1405-07-10
   python scripts/jalali.py today
   ```
6. **Review the diff.** For a file edit, compare before and after and report
   what changed in one or two lines.

Details of every rule and its known false positives are in
[references/rules.md](references/rules.md). Read it when a user questions a
specific change.

## Pitfalls

- Half-space rules are heuristics. Check phrases like `می` used as a noun
  (wine), and unusual compounds. Use `--no-halfspace` when text is poetry or
  already carefully typeset.
- Never convert digits inside code, IDs, versions, phone numbers or file names
  unless asked. The scripts already protect Latin tokens (`v1.2`, `H2O`).
- Jalali dates are exact for 1178 to 1633 AP only. Outside that range say so.
- A new file is safer than `--in-place` unless the user asked to change the
  original. Line endings (CRLF/LF) are preserved either way.
- Always keep the output UTF-8. Do not paste Persian text through tools that
  re-encode it.

## Verification

- Re-run the same command on its own output. A second pass must change nothing
  (the normalizer is idempotent).
- Spot-check three changed sentences and one protected code or URL segment.
- For dates, convert back and confirm the original date is returned.
