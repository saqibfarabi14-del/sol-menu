"""
SOL Menu Build Script
─────────────────────
Fetches from Airtable and injects into SOL_v3.html → SOL_v3_built.html.
Original file is never modified.

Usage:
    python build.py

Env vars (in .env or GitHub Secrets):
    AIRTABLE_TOKEN   — Personal Access Token (pat...)
    AIRTABLE_BASE_ID — Base ID (app...)
"""

import json
import os
import re
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN   = os.environ.get("AIRTABLE_TOKEN", "")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID", "")

if not TOKEN or not BASE_ID:
    print("ERROR: AIRTABLE_TOKEN and AIRTABLE_BASE_ID must be set in .env")
    sys.exit(1)

HEADERS = {"Authorization": "Bearer " + TOKEN}
API_URL = "https://api.airtable.com/v0/" + BASE_ID + "/"


# ── Airtable helpers ──────────────────────────────────────────────────────────

def fetch_table(table_name):
    """Fetch all records from a table, following pagination."""
    url = API_URL + requests.utils.quote(table_name)
    params = {}
    records = []
    while True:
        resp = requests.get(url, headers=HEADERS, params=params)
        if resp.status_code != 200:
            print("ERROR fetching '" + table_name + "': " + resp.text)
            sys.exit(1)
        data = resp.json()
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break
        params["offset"] = offset
    return records


def f(record, key, default=""):
    """Safe field getter."""
    return record.get("fields", {}).get(key, default)


def parse_prices(price_str):
    """
    Parse a price string into the JS price array format.

    Single price:          "1350"           → [{"a": 1350}]
    Multi-variant prices:  "3 pcs:1350, 5 pcs:2150"  → [{"l":"3 pcs","a":1350},{"l":"5 pcs","a":2150}]
    """
    price_str = str(price_str).strip()
    if not price_str or price_str == "0":
        return [{"a": 0}]
    parts = [p.strip() for p in price_str.split(",") if p.strip()]
    result = []
    for part in parts:
        if ":" in part:
            label, amount = part.split(":", 1)
            try:
                result.append({"l": label.strip(), "a": int(amount.strip())})
            except ValueError:
                result.append({"l": label.strip(), "a": 0})
        else:
            try:
                result.append({"a": int(part)})
            except ValueError:
                result.append({"a": 0})
    return result if result else [{"a": 0}]


def parse_tags(tags_val):
    """
    Parse tags from Airtable. Accepts:
    - A list (Airtable multi-select returns a list)
    - A comma-separated string
    """
    if isinstance(tags_val, list):
        return [t.strip().lower() for t in tags_val if t.strip()]
    if isinstance(tags_val, str) and tags_val.strip():
        return [t.strip().lower() for t in tags_val.split(",") if t.strip()]
    return []


# ── Table builders ────────────────────────────────────────────────────────────

def build_sol_data():
    """
    Table: Meta
    Fields: Key (text), Value (text)
    Plus a Photos table for dish name → image URL mapping.
    """
    meta = {}
    for r in fetch_table("Meta"):
        key = f(r, "Key")
        val = f(r, "Value")
        if key:
            meta[key] = val

    photos = {}
    try:
        for r in fetch_table("Photos"):
            dish = f(r, "Dish Name")
            url  = f(r, "URL")
            if dish and url:
                photos[dish] = url
    except SystemExit:
        print("  (Photos table not found — continuing without photos)")

    return {
        "meta": {
            "name":        meta.get("name",        "SOL Korean BBQ"),
            "tagline":     meta.get("tagline",     "Wood. Stone. Fire."),
            "phone":       meta.get("phone",       ""),
            "whatsapp":    meta.get("whatsapp",    ""),
            "email":       meta.get("email",       ""),
            "instagram":   meta.get("instagram",   ""),
            "facebook":    meta.get("facebook",    ""),
            "address":     meta.get("address",     ""),
            "coordinates": meta.get("coordinates", ""),
            "ga4":         meta.get("ga4",         "G-XXXXXXXXXX"),
            "hours":       meta.get("hours",       ""),
        },
        "photos": photos,
    }


def build_items():
    """
    Table: Menu Items
    Fields: Section (text), Ko (text), Rom (text), En (text),
            Description (text), Prices (text), Tags (multi-select or text),
            Sub (text, optional — only used for noodles: 'hot' or 'cold'),
            Sort (number, optional)
    """
    records = fetch_table("Menu Items")
    records.sort(key=lambda r: f(r, "Sort", 9999) if isinstance(f(r, "Sort", 9999), (int, float)) else 9999)

    items = []
    for r in records:
        item = {
            "s":  f(r, "Section"),
            "ko": f(r, "Ko"),
            "en": f(r, "En"),
            "d":  f(r, "Description"),
            "p":  parse_prices(f(r, "Prices", "0")),
            "t":  parse_tags(f(r, "Tags", [])),
        }
        rom = f(r, "Rom")
        if rom:
            item["rom"] = rom
        sub = f(r, "Sub")
        if sub:
            item["sub"] = sub
        # Remove empty string values to keep the JS compact
        item = {k: v for k, v in item.items() if v != "" and v != []}
        items.append(item)

    return items


def build_bbq():
    """
    Table: BBQ Cuts
    Fields: Tier (single select: premium | regular | duck),
            Ko (text), En (text), Price (number), Highlight (checkbox)

    Table: BBQ Assortments
    Fields: Name (text), Items (long text — one cut per line),
            Price (number), Highlight (checkbox), Sort (number)
    """
    # Cuts
    cut_records = fetch_table("BBQ Cuts")
    premium = []
    regular = []
    duck    = []

    for r in cut_records:
        tier = f(r, "Tier", "regular").lower().strip()
        cut = {
            "ko": f(r, "Ko"),
            "en": f(r, "En"),
            "a":  int(f(r, "Price", 0) or 0),
        }
        hi = f(r, "Highlight", False)
        if hi:
            cut["hi"] = True
        if tier == "premium":
            premium.append(cut)
        elif tier == "duck":
            duck.append(cut)
        else:
            regular.append(cut)

    # Assortments
    assort_records = fetch_table("BBQ Assortments")
    assort_records.sort(key=lambda r: f(r, "Sort", 9999) if isinstance(f(r, "Sort", 9999), (int, float)) else 9999)

    assortments = []
    for r in assort_records:
        raw_items = f(r, "Items", "")
        item_list = [line.strip() for line in raw_items.splitlines() if line.strip()]
        assort = {
            "name":  f(r, "Name"),
            "items": item_list,
            "a":     int(f(r, "Price", 0) or 0),
        }
        hi = f(r, "Highlight", False)
        if hi:
            assort["hi"] = True
        assortments.append(assort)

    return {
        "premium":     premium,
        "regular":     regular,
        "duck":        duck,
        "assortments": assortments,
    }


def build_sig():
    """
    Table: Tasting
    Fields: Title (text), Description (text), Price (number),
            Courses (long text — one 'Ko · En' pair per line),
            Sort (number)

    Each line in Courses should be formatted as:  한국어 · English name
    If only English, omit the Korean part.
    """
    records = fetch_table("Tasting")
    records.sort(key=lambda r: f(r, "Sort", 9999) if isinstance(f(r, "Sort", 9999), (int, float)) else 9999)

    sig = []
    for r in records:
        raw_courses = f(r, "Courses", "")
        items = []
        for line in raw_courses.splitlines():
            line = line.strip()
            if not line:
                continue
            if "·" in line:
                parts = line.split("·", 1)
                items.append({"ko": parts[0].strip(), "en": parts[1].strip()})
            else:
                items.append({"en": line})

        sig.append({
            "t":     f(r, "Title"),
            "d":     f(r, "Description"),
            "items": items,
            "p":     int(f(r, "Price", 0) or 0),
        })

    return sig


# ── Injection ─────────────────────────────────────────────────────────────────

def inject(html, sol_data, items, bbq, sig):
    """Replace the four const blocks in the HTML with fresh Airtable data.

    Uses start/end string markers instead of regex so semicolons inside
    comments in the original source don't cause early truncation.
    """

    blocks = [
        (
            "const SOL_DATA",
            "/* ── Apply meta to page",
            "const SOL_DATA = " + json.dumps(sol_data, ensure_ascii=False, indent=2) + ";\n",
        ),
        (
            "const ITEMS=",
            "const BBQ=",
            "const ITEMS=" + json.dumps(items, ensure_ascii=False, separators=(",", ":")) + ";\n",
        ),
        (
            "const BBQ=",
            "const SIG=",
            "const BBQ=" + json.dumps(bbq, ensure_ascii=False, separators=(",", ":")) + ";\n",
        ),
        (
            "const SIG=",
            "/* ═══ TAG + PRICE",
            "const SIG=" + json.dumps(sig, ensure_ascii=False, separators=(",", ":")) + ";\n",
        ),
    ]

    for start_marker, end_marker, replacement in blocks:
        start_idx = html.find(start_marker)
        end_idx   = html.find(end_marker, start_idx)
        if start_idx == -1 or end_idx == -1:
            print("  WARNING: markers not found for '" + start_marker + "' — skipping.")
            continue
        html = html[:start_idx] + replacement + html[end_idx:]
        label = start_marker.strip().split()[1]
        print("  [OK] " + label)

    return html


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    src  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SOL_v3.html")
    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SOL_v3_built.html")

    if not os.path.exists(src):
        print("ERROR: SOL_v3.html not found at " + src)
        sys.exit(1)

    print("Reading " + src)
    with open(src, "r", encoding="utf-8") as fh:
        html = fh.read()

    print("\nFetching from Airtable...")
    sol_data = build_sol_data()
    items    = build_items()
    bbq      = build_bbq()
    sig      = build_sig()

    print("  Menu items:       " + str(len(items)))
    print("  BBQ premium cuts: " + str(len(bbq["premium"])))
    print("  BBQ regular cuts: " + str(len(bbq["regular"])))
    print("  BBQ duck cuts:    " + str(len(bbq["duck"])))
    print("  BBQ assortments:  " + str(len(bbq["assortments"])))
    print("  Tasting menus:    " + str(len(sig)))

    print("\nInjecting data blocks...")
    built = inject(html, sol_data, items, bbq, sig)

    print("\nWriting " + dest)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(built)

    print("\nDone. Open SOL_v3_built.html to verify.")


if __name__ == "__main__":
    main()
