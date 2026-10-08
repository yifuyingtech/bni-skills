# Optional PALMS MCP backfill workflow

Contract checked against bni-platform implementation on 2026-09-22, not a live deployment test. Prefer the connected server's current `tools/list` schemas when executing. If schemas differ, resolve the difference before writing.

## Connection and boundaries

- The optional platform endpoint is `https://bni-it.com/api/mcp`, connection name commonly `bni-palms`. Use a different endpoint if the user explicitly selects it.
- The MCP reads/writes platform PALMS records; it does not log in to BNI Connect or download reports. Those steps still require the user's authorized browser session.
- Each key selects one chapter; tools do not accept `chapterId`. Confirm the key's chapter from its issuing configuration/user and compare the visible BNI report chapter. An empty member list is not evidence of chapter identity. Never guess the tenant or send another chapter's reports.
- Use an already connected client. Configuration template, only when the user asks to configure Claude Code:

```sh
claude mcp add --transport http bni-palms https://bni-it.com/api/mcp --header "Authorization: Bearer <YOUR_KEY>"
```

Do not put real keys in shell history, repo configuration or documentation. Prefer the client's supported secure credential mechanism. Never reuse the key from an example conversation. Missing/expired authentication requires the user to connect a valid key; do not request BNI cookies. A read-only key can audit gaps but cannot import or run the write tool's dry-run.

## 1. Define the expected weeks

Confirm chapter, start/end dates, timezone, seven-day anchor and whether the final partial week is requested. Do not silently reinterpret Jan 1–7 as Monday–Sunday, or treat a still-open current week as final. Generate inclusive, non-overlapping intervals, each at most seven days.

Call `palms_list_batches` with `limit:100`, increasing `offset` until all `total` records are retrieved. Inspect all statuses, not only `imported`. Its date filters `startsOnFrom`/`startsOnTo` filter START dates, not overlap; fetch all pages without date filters when checking overlap, so an older long-range/partial batch is not missed. If data changes during pagination, reconcile again before writing.

Classify each expected interval:

- Exact dates, one imported batch: already present, normally skip. This does not prove every value is correct; use `palms_get_batch` if completeness is questioned.
- No intersecting batch: missing; eligible for download and dry-run.
- Uploaded/validated/rejected batch, multiple matches, partial overlap, or suspicious row counts: needs review, not automatically missing.
- No meeting/empty report: report separately; do not fabricate zero rows or declare attendance absent.

Produce a compact plan listing interval, existing batch ID/status, action and reason before downloading missing reports. Never subtract cumulative reports to invent weekly values.

## 2. Download and parse

Use SKILL.md's BNI browser workflow. Validate workbook-embedded dates, chapter, encoding and file coverage; the existing `validate_palms.py` checks basic file/date structure only, not every numeric field or MCP eligibility. Read `bni-connect-report.md` for SpreadsheetML details.

MCP does not accept `.xls` bytes, file paths or CSV. Parse worksheet cells by their header labels, honoring `ss:Index`. Decode strict UTF-8, then CP950; stop on invalid encoding, malformed XML, missing headers, ambiguous names, invalid dates/numbers or duplicate row keys. Exclude totals/BNI/visitor summary rows, not real members based on position. Preserve all source values; do not turn a missing/invalid numeric cell into zero without source confirmation. No real member data in the public skill repo or examples.

Canonical mapping (13 raw numeric measures, plus name):

| Source header | JSON field |
|---|---|
| 姓氏 + 名字, remove whitespace | fullName |
| 出席 | presentCount |
| 缺席 | absentCount |
| 遲到 | lateCount |
| 病假 | medicalLeaveCount |
| 替代人 | substituteCount |
| 提供內部引薦 | internalReferralsGiven |
| 提供外部引薦 | externalReferralsGiven |
| 收到內部引薦 | internalReferralsReceived |
| 收到外部引薦 | externalReferralsReceived |
| 來賓 | visitorCount |
| 一對一會面 | oneToOneCount |
| 交易價值 | thankYouAmount |
| 分會教育單位 | educationUnits |

All values must be finite and nonnegative. Counts through visitorCount are integers; oneToOneCount, thankYouAmount and educationUnits permit decimals. Preserve numeric precision; remove validated thousands separators, not arbitrary nonnumeric characters.

Additional REQUIRED fields, matching the platform parser:

- `attendanceScore`: denominator = present + absent + late + medicalLeave + substitute. If zero, score is 0; otherwise `Math.round((present + late + medicalLeave + substitute) / denominator * 10000) / 100`. Use equivalent nonnegative half-up rounding if not using JavaScript.
- `referralCount` = internalReferralsGiven + externalReferralsGiven (not received referrals).
- `trainingPoints` = educationUnits; `guestCount` = visitorCount; `valueAmount` = thankYouAmount.
- `sourceRecordKey` = `startsOn:endsOn:fullName`. Duplicate normalized names require resolution; do not append arbitrary suffixes to hide ambiguous membership.

Do not send memberId, email, memberNo or extra fields in create rows. Use `palms_list_members` (respect its current pagination schema) to identify ambiguities; the server performs the final match. Do not create or rename members through unrelated tools to force a match.

## 3. Resolve period and dry-run

Call `palms_list_periods` with `limit:100`. This implementation has no offset parameter or period-creation tool. Choose a real returned `periodId` with appropriate dates/rules/status, confirmed by the user when ambiguous. If no suitable period is returned, stop that import and ask for a platform administrator to prepare/select it. Do not invent IDs or silently use the latest period.

`palms_create_batch` requires `startsOn`, `endsOn`, `sourceFilename`, `periodId`, and 1–500 fully parsed `rows`. Always first call with `dryRun:true, replaceExisting:false`. More than 500 rows must not be split into separate same-week batches; report the server limit.

Inspect the MCP tool's `isError` and decoded business result, not only HTTP 200. Successful dry-run returns `checksum`, `validRows`, `rowErrors`, `unmatchedMembers`, `wouldConflictWith`. An `ok:true` dry-run with errors/unmatched members/conflicts is NOT ready to import. Require zero errors/unmatched, no conflicts, and validRows equal the complete source member row count.

Present chapter, dates, source files, row counts, selected periods and dry-run results; obtain confirmation for the exact new batches before writing. Default remains `replaceExisting:false`. Audit/download-only requests stop here.

## 4. Import and verify

Re-read intersecting batches immediately before each write. Submit the exact reviewed payload with `dryRun:false, replaceExisting:false`. Save a local non-secret manifest with interval, file, checksum, periodId, batch ID, rowsImported, changeSetId and outcome. Keep manifests containing member details outside the public repo.

Verify each result using `palms_get_batch`: exact dates/period, imported status, source checksum and all row values/counts against the validated payload. Inspect `snapshotRecalculation`; do not claim dashboard recomputation succeeded if it failed or was skipped. Optionally use `palms_get_member_metrics` for an authorized targeted check. Do not repeatedly write to fix a display problem.

- `duplicate_checksum` or `week_already_imported`: re-read and compare; skip only when the existing data is genuinely the same expected interval/content. Otherwise report conflict. Identical zero-activity values in two different weeks may trigger a checksum collision; never alter genuine values to defeat it.
- Timeout/connection loss after write: outcome unknown. Re-read batches and changes before any retry; do not assume rollback or resend blindly. Reconcile once, then stop for review if still uncertain.
- 401/403 or `forbidden_scope`: stop and report missing authorization; do not switch identities or broaden scopes silently.
- 429: honor Retry-After if present and use bounded retries; after two repeated failures stop and report remaining weeks.

No automatic delete/replace/update belongs to a missing-week backfill. `replaceExisting:true` deletes/replaces the old batch and needs separate explicit approval of the affected batch and full replacement data, with a fresh dry-run. `palms_list_changes` is read-only history; there is no `palms_revert_change` or one-click rollback.

## Completion report

Distinguish already present, downloaded, validated, dry-run ready, imported and verified, empty, conflicting and blocked intervals. Include output directory and batch IDs; never include keys/tokens or unnecessary member details. State the exact remaining gaps. Download success is not import success, and import success is not proof of red/green scoring correctness.

## Maintainer sources

Contract source: bni-platform `apps/api/src/mcp/tools/read-batches.ts`, `read-members.ts`, `read-periods.ts`, `write-batches.ts`, `protocol.ts`, and `apps/web/src/utils/palms.ts`. The old `palms-mcp-plan.md` is not authoritative where it conflicts with runtime schemas (notably required periodId and absent revert tool). This reference is self-contained; consumers do not need the private platform repo.
