# BNI PALMS Weekly Skill

An open-source Codex/ChatGPT skill for exporting consecutive weekly PALMS Summary Reports from a BNI core-team member's own authenticated BNI Connect browser session.

The skill does not store BNI credentials, cookies, or transient report tokens. Each user remains responsible for access rights to the selected chapter and for handling downloaded member data appropriately.

## Install

Clone this repository directly into your Codex skills directory:

```bash
git clone https://github.com/yifuyingtech/bni-palms-weekly-skill.git ~/.codex/skills/bni-palms-weekly
```

Start a new task and invoke `$bni-palms-weekly` with a signed-in BNI Connect report tab.

## Validate downloads

```bash
python scripts/validate_palms.py /path/to/downloads --manifest /path/to/manifest.csv
```

## Maintenance scope

- Update `references/bni-connect-report.md` when BNI Connect changes its report flow.
- Keep the validator compatible with Excel 2003 XML `.xls` exports.
- Do not add shared credentials or cookie-based automation.

Licensed under MIT.
