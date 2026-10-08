---
name: bni-palms-weekly
description: Download and validate weekly BNI PALMS .xls reports; optionally identify missing weeks and import validated data through a chapter-scoped PALMS MCP. Use for weekly exports or PALMS backfills, not bypassing BNI login or accessing unauthorized chapters.
---

# BNI PALMS Weekly

Use the user's existing authenticated BNI Connect browser session. Never request, store, print, or commit passwords, cookies, session identifiers, `crypt`, `__params_key`, or `encryptString` values.

## Download workflow

For download-only requests, follow the workflow below without requiring an MCP connection. For missing-week discovery or platform import, first read [references/palms-mcp.md](references/palms-mcp.md) and follow its reconcile → download → validate → dry-run → approve → import → verify workflow. A request to improve this skill is not permission to import live data.

1. Confirm the user has explicitly identified the BNI Connect tab and requested report downloads. If login is required, let the user complete login and any CAPTCHA.
2. Open **Reports → Chapter → PALMS Summary Report** and derive the currently selected chapter from the visible page. Do not hardcode a chapter name or organization ID.
3. Confirm the requested start date, end date, and interval. For weekly exports, produce inclusive, non-overlapping ranges of seven calendar days. A final partial range is allowed only when the requested end date is not a complete week.
4. Test one range first. Verify the rendered report's visible `From` and `To` values, not only the date inputs. Some BNI Connect date fields have display and hidden values that can diverge.
5. Export the `.xls` report for every range. Prefer normal browser download behavior. If the legacy export link is blocked, inspect the authenticated report request and retrieve the export inside the same browser origin; transfer only the returned workbook bytes to the local output folder. Do not export browser credentials.
6. Name files `PALMS_<chapter-key>_<YYYY-MM-DD>_<YYYY-MM-DD>.xls`. Sanitize the chapter key to ASCII letters, digits, `_`, and `-` when possible.
7. Run `scripts/validate_palms.py <output-directory>`. Do not claim completion unless every expected range is present and the embedded workbook dates match its filename.
8. Report the output folder, number of files, covered dates, validation errors, and weeks containing no member rows.

For endpoint behavior, browser-blocking recovery, and workbook field names, read [references/bni-connect-report.md](references/bni-connect-report.md) only when implementing or debugging the download integration.

## Safety and maintenance

- Treat report contents as chapter-confidential membership data. Save locally or to the destination the user explicitly requested.
- Do not turn transient export URLs into a public API: their encrypted parameters are short-lived and session-bound.
- Stop after repeated authentication/permission failures and ask the user to verify their BNI role or selected chapter.
- Keep parsing independent of member names, chapter names, locale text outside the documented PALMS fields, and a specific calendar year.
- Never store MCP bearer keys in this skill, its examples, manifests, or Git. Use the client's existing authorized connection; do not install or persist credentials just to inspect the skill.
