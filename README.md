# BNI Skills

An open-source collection of Codex/ChatGPT skills for BNI chapter workflows.

## Available skills

### `bni-palms-weekly`

Exports consecutive weekly PALMS Summary Reports from a BNI core-team member's own authenticated BNI Connect browser session and validates the downloaded workbooks.

Optional PALMS MCP workflow: check missing weeks, download only needed reports, validate and prepare structured rows, dry-run, request confirmation, import and read back for verification. Download-only use does not require MCP. See [MCP backfill guidance](skills/bni-palms-weekly/references/palms-mcp.md).

Example request: `使用 $bni-palms-weekly，檢查我已連線 MCP 所屬分會在指定日期範圍缺少哪些週，下載缺漏 PALMS，先給我 dry-run 結果，確認後再匯入。`

The MCP must already be authorized for the intended chapter. Never commit bearer keys. Existing/conflicting batches are not overwritten automatically. Missing performance periods and unresolved member matches block import. The MCP guide is checked against the platform source contract, not a claim of live end-to-end import testing.

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
