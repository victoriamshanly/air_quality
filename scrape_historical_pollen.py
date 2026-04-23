"""Download XAC weekly pollen bulletin PDFs and extract Platanus levels per station.

Usage: uv run python scrape_historical_pollen.py

Writes data/pollen_platanus_historical.csv with columns:
    year, week, week_start, week_end, station, pollen, level, trend
"""

from __future__ import annotations

import csv
import datetime
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pdfplumber
import requests

PDF_URL = "https://aerobiologia.cat/pia/general/pdf/nivells/XAC-{week:02d}-{year}.pdf"
HEADERS = {"User-Agent": "Mozilla/5.0 (air-quality-research)"}

STATIONS = [
    "BARCELONA", "BELLATERRA", "MANRESA", "TARRAGONA", "LLEIDA",
    "GIRONA", "VIELHA", "ROQUETES-TORTOSA", "PLANES", "PALMA",
]

POLLEN = "Plàtan"
X_TOLERANCE = 25
Y_TOLERANCE = 3
MIN_PDF_BYTES = 10_000

START_YEAR = 2021


def fetch_pdf(year: int, week: int) -> bytes | None:
    url = PDF_URL.format(year=year, week=week)
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
    except requests.RequestException:
        return None
    if r.status_code != 200 or len(r.content) < MIN_PDF_BYTES:
        return None
    return r.content


def extract_platanus_levels(pdf_bytes: bytes) -> dict[str, tuple[int, str] | None]:
    """For each station, find the Plàtan line in its column and return (level, trend)."""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        words = pdf.pages[0].extract_words()

    result: dict[str, tuple[int, str] | None] = {}
    for station in STATIONS:
        anchors = [w for w in words if w["text"] == station]
        if not anchors:
            result[station] = None
            continue
        sx, sy = anchors[0]["x0"], anchors[0]["top"]

        plats = [
            w for w in words
            if w["text"] == POLLEN
            and abs(w["x0"] - sx) < X_TOLERANCE
            and w["top"] > sy
        ]
        if not plats:
            result[station] = None
            continue
        plat = min(plats, key=lambda w: w["top"])

        line = sorted(
            [w for w in words
             if abs(w["top"] - plat["top"]) < Y_TOLERANCE
             and w["x0"] >= plat["x0"]],
            key=lambda w: w["x0"],
        )
        if len(line) < 3:
            result[station] = None
            continue
        try:
            level = int(line[1]["text"])
        except ValueError:
            result[station] = None
            continue
        result[station] = (level, line[2]["text"])
    return result


def iso_week_dates(year: int, week: int) -> tuple[datetime.date, datetime.date] | None:
    try:
        monday = datetime.date.fromisocalendar(year, week, 1)
    except ValueError:
        return None
    return monday, monday + datetime.timedelta(days=6)


def process_week(year: int, week: int) -> list[dict]:
    dates = iso_week_dates(year, week)
    if dates is None:
        return []
    monday, sunday = dates
    if monday > datetime.date.today():
        return []

    pdf = fetch_pdf(year, week)
    if not pdf:
        return []

    try:
        levels = extract_platanus_levels(pdf)
    except Exception as e:
        print(f"  [parse-error] {year}-W{week:02d}: {e}")
        return []

    rows = []
    for station, val in levels.items():
        if val is None:
            continue
        level, trend = val
        rows.append({
            "year": year,
            "week": week,
            "week_start": monday.isoformat(),
            "week_end": sunday.isoformat(),
            "station": station,
            "pollen": "Platanus",
            "level": level,
            "trend": trend,
        })
    return rows


def main() -> None:
    out_dir = Path(__file__).parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "pollen_platanus_historical.csv"

    today = datetime.date.today()
    work = [(y, w) for y in range(START_YEAR, today.year + 1) for w in range(1, 54)]

    rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(process_week, y, w): (y, w) for y, w in work}
        for fut in as_completed(futures):
            y, w = futures[fut]
            wk_rows = fut.result()
            if wk_rows:
                print(f"  [ok] {y}-W{w:02d} ({wk_rows[0]['week_start']}) — {len(wk_rows)} stations")
                rows.extend(wk_rows)

    rows.sort(key=lambda r: (r["year"], r["week"], r["station"]))

    with out_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["year", "week", "week_start", "week_end", "station", "pollen", "level", "trend"],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved {len(rows)} rows to {out_file}")


if __name__ == "__main__":
    main()
