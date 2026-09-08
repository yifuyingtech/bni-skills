#!/usr/bin/env python3
"""Validate weekly BNI PALMS SpreadsheetML exports without external packages."""

from __future__ import annotations

import argparse
import csv
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date
from pathlib import Path


SS = "urn:schemas-microsoft-com:office:spreadsheet"
FILE_RE = re.compile(r"^PALMS_(?P<chapter>.+)_(?P<start>\d{4}-\d{2}-\d{2})_(?P<end>\d{4}-\d{2}-\d{2})\.xls$", re.I)


@dataclass
class Result:
    filename: str
    chapter: str = ""
    starts_on: str = ""
    ends_on: str = ""
    member_rows: int = 0
    status: str = "ok"
    message: str = ""


def row_values(row: ET.Element) -> list[str]:
    values: list[str] = []
    column = 0
    for cell in row.findall(f"{{{SS}}}Cell"):
        requested = cell.get(f"{{{SS}}}Index")
        if requested:
            column = int(requested) - 1
        while len(values) <= column:
            values.append("")
        data = cell.find(f"{{{SS}}}Data")
        values[column] = (data.text or "").strip() if data is not None else ""
        column += 1
    return values


def workbook_date(rows: list[list[str]], label: str) -> str:
    for row in rows:
        if row and row[0] == label:
            value = next((cell for cell in row[1:] if cell), "")
            return value[:10]
    return ""


def validate(path: Path) -> Result:
    result = Result(filename=path.name)
    match = FILE_RE.match(path.name)
    if not match:
        result.status, result.message = "error", "filename does not match PALMS_<chapter>_<start>_<end>.xls"
        return result
    result.chapter, result.starts_on, result.ends_on = match.group("chapter", "start", "end")

    try:
        payload = path.read_bytes()
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError:
            text = payload.decode("cp950")
        root = ET.fromstring(text)
        rows = [row_values(row) for row in root.findall(f".//{{{SS}}}Row")]
    except (ET.ParseError, OSError, ValueError) as exc:
        result.status, result.message = "error", f"invalid SpreadsheetML: {exc}"
        return result

    embedded_start, embedded_end = workbook_date(rows, "從:"), workbook_date(rows, "至:")
    if (embedded_start, embedded_end) != (result.starts_on, result.ends_on):
        result.status, result.message = "error", f"embedded dates are {embedded_start} to {embedded_end}"
        return result
    if (date.fromisoformat(result.ends_on) - date.fromisoformat(result.starts_on)).days > 6:
        result.status, result.message = "error", "range exceeds seven inclusive days"
        return result

    header_index = next((i for i, row in enumerate(rows) if "姓氏" in row and "名字" in row and "出席" in row), -1)
    if header_index < 0:
        result.status, result.message = "error", "PALMS member header not found"
        return result

    system_names = {"", "總數", "來賓", "BNI"}
    for row in rows[header_index + 1 :]:
        name = "".join(row[:2]).replace(" ", "")
        if name not in system_names:
            result.member_rows += 1
    if result.member_rows == 0:
        result.status, result.message = "empty", "no member rows"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--manifest", type=Path, help="optional CSV manifest output")
    args = parser.parse_args()

    files = sorted(args.directory.glob("*.xls"))
    results = [validate(path) for path in files]
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        with args.manifest.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=Result.__dataclass_fields__.keys())
            writer.writeheader()
            writer.writerows(result.__dict__ for result in results)

    for result in results:
        print(f"{result.status.upper():5} {result.filename} rows={result.member_rows} {result.message}".rstrip())
    errors = sum(result.status == "error" for result in results)
    print(f"FILES={len(results)} ERRORS={errors} EMPTY={sum(result.status == 'empty' for result in results)}")
    return 1 if errors or not results else 0


if __name__ == "__main__":
    sys.exit(main())
