# persian-text-skill

An [Agent Skill](https://agentskills.io/specification) for Persian (Farsi) text.
It works with any agent that supports the open skills standard, including
Hermes Agent and Claude Code.

It handles the mechanical, rule-based parts of Persian typography with
deterministic, tested scripts, so the model does not have to guess:

- Arabic to Persian letters (ي → ی, ك → ک), tatweel removal
- Half-space (نیم‌فاصله) rules: می‌روم، کتاب‌ها، بزرگ‌تر
- Persian / English digits, with protection for `v1.2`, `H2O`, code and URLs
- Punctuation: `, ; ?` → `، ؛ ؟` and spacing
- Gregorian ↔ Jalali (شمسی) date conversion
- Numbers in Persian words (۱۴۰۵ → هزار و چهارصد و پنج)
- Markdown-safe: code blocks, inline code, URLs, e-mails and HTML tags are never touched

Python 3.9+ and the standard library only. No network access, no dependencies.

## Install

**Hermes Agent**

```bash
hermes skills tap add <your-username>/persian-text-skill
```

**Claude Code and other agentskills.io-compatible agents**: copy the skill
folder into the agent's skills directory:

```bash
cp -r skills/persian-text-skill ~/.claude/skills/
```

## Use the scripts directly

```bash
cd skills/persian-text-skill

echo "او می رود, چرا?" | python scripts/normalize.py
python scripts/normalize.py README.fa.md --digits fa --in-place

python scripts/digits.py fa "سال 2026"
python scripts/digits.py words 1405

python scripts/jalali.py to-jalali 2026-10-02 --long
python scripts/jalali.py to-gregorian 1405-07-10
```

Rules, examples and known limitations: [`references/rules.md`](skills/persian-text-skill/references/rules.md).

## Development

```bash
uv sync
uv run pytest
```

Validate the skill format with the reference library:

```bash
uvx --from git+https://github.com/agentskills/agentskills#subdirectory=skills-ref skills-ref validate skills/persian-text-skill
```

## فارسی

این Skill بخش‌های مکانیکی و قاعده‌مند تایپ فارسی را با اسکریپت‌های قطعی و
تست‌شده انجام می‌دهد: اصلاح ی و ک عربی، نیم‌فاصله، ارقام فارسی و انگلیسی،
نقطه‌گذاری، تبدیل تاریخ شمسی و میلادی، و نوشتن عدد به حروف. کد، لینک و
بلوک‌های Markdown دست‌نخورده می‌مانند. فقط به پایتون ۳٫۹ یا بالاتر نیاز دارد.

## License

MIT
