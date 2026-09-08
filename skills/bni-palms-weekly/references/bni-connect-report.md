# BNI Connect PALMS report integration notes

These observations describe BNI Connect Release 2.35.0 as seen in September 2026. Reverify them when the site changes.

## Report request

The chapter PALMS summary form issues an authenticated request shaped like:

```text
GET /web/secure/reportsChapterPALMS
  ?IdOrg=<selected chapter organization id>
  &startDate=<MM/DD/YYYY>
  &endDate=<MM/DD/YYYY>
  &ShowDetails=false
  &__exports_details=1
```

The response is HTML containing a `reportsIFrame`. The iframe loads a `secureWebReport` URL with a transient encrypted value. Its export control resolves to `/web/secure/WebReport` with `ReportType=XLS` and transient parameters.

This is an authenticated legacy reporting flow, not a stable public REST API. Never log or persist its transient parameters.

## Export format

The `.xls` response is Excel 2003 XML (SpreadsheetML), beginning with:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<?mso-application progid="Excel.Sheet"?>
```

Some Taiwan exports declare UTF-8 while their bytes are actually Big5/CP950. Decode strictly as UTF-8 first, then fall back to Big5/CP950 before parsing XML. Do not accept replacement-character output as valid member data.

The parameters table contains `從:` and `至:` date rows. The member table normally contains:

- `姓氏`, `名字`
- `出席`, `缺席`, `遲到`, `病假`, `替代人`
- `提供內部引薦`, `提供外部引薦`
- `收到內部引薦`, `收到外部引薦`
- `來賓`, `一對一會面`, `交易價值`, `分會教育單位`

Rows named `總數`, `來賓`, or `BNI` are summary/system rows, not chapter members.

## Known browser behavior

- Setting only the visible date text fields may leave hidden submitted values unchanged. Validate the report's rendered parameters.
- Directly navigating an export link may be blocked by Chrome because the legacy report is inside an iframe.
- When normal download fails, execute the authenticated fetch inside the BNI Connect page origin, return only the response bytes to the trusted local process, and save those bytes with the intended filename.
- Never copy cookies into a downloader script or source repository.
