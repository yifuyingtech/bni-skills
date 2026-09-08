# BNI Skills

An open-source collection of Codex/ChatGPT skills for BNI chapter workflows.

## Available skills

### `bni-palms-weekly`

Exports consecutive weekly PALMS Summary Reports from a BNI core-team member's own authenticated BNI Connect browser session and validates the downloaded workbooks.

The skill does not store BNI credentials, cookies, or transient report tokens. Each user remains responsible for access rights to the selected chapter and for handling downloaded member data appropriately.

## Install

Install the PALMS skill with the Skills CLI:

```bash
npx skills add yifuyingtech/bni-skills@bni-palms-weekly
```

Start a new task and invoke `$bni-palms-weekly` with a signed-in BNI Connect report tab.

## Validate downloads

```bash
python skills/bni-palms-weekly/scripts/validate_palms.py /path/to/downloads --manifest /path/to/manifest.csv
```

## Maintenance scope

- Keep each skill self-contained under `skills/<skill-name>/`.
- Update `skills/bni-palms-weekly/references/bni-connect-report.md` when BNI Connect changes its report flow.
- Keep the validator compatible with Excel 2003 XML `.xls` exports.
- Do not add shared credentials or cookie-based automation.

Licensed under MIT.
