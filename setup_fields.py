"""
SOL Menu — Field Setup Script
──────────────────────────────
Creates all required fields in each Airtable table.
Run ONCE before seed.py.
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN   = os.environ.get("AIRTABLE_TOKEN", "")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID", "")

HEADERS = {
    "Authorization": "Bearer " + TOKEN,
    "Content-Type": "application/json",
}

META_URL = "https://api.airtable.com/v0/meta/bases/" + BASE_ID + "/tables"


def get_tables():
    resp = requests.get(META_URL, headers=HEADERS)
    if resp.status_code != 200:
        print("ERROR fetching tables: " + resp.text)
        sys.exit(1)
    return {t["name"]: t["id"] for t in resp.json().get("tables", [])}


def get_existing_fields(table_id):
    resp = requests.get(META_URL, headers=HEADERS)
    tables = resp.json().get("tables", [])
    for t in tables:
        if t["id"] == table_id:
            return [f["name"] for f in t.get("fields", [])]
    return []


def create_field(table_id, field):
    url = META_URL + "/" + table_id + "/fields"
    resp = requests.post(url, headers=HEADERS, json=field)
    if resp.status_code not in (200, 201):
        print("    WARN: " + field["name"] + " — " + resp.json().get("error", {}).get("message", resp.text))
    else:
        print("    + " + field["name"])


def setup_table(tables, table_name, fields):
    table_id = tables.get(table_name)
    if not table_id:
        print("ERROR: Table '" + table_name + "' not found.")
        return
    print(table_name)
    existing = get_existing_fields(table_id)
    for field in fields:
        if field["name"] in existing:
            print("    = " + field["name"] + " (exists)")
        else:
            create_field(table_id, field)


def main():
    print("SOL Menu — Field Setup")
    print("=" * 44)

    tables = get_tables()

    # ── Meta ──────────────────────────────────────────────────────
    setup_table(tables, "Meta", [
        {"name": "Key",   "type": "singleLineText"},
        {"name": "Value", "type": "singleLineText"},
    ])

    # ── Menu Items ────────────────────────────────────────────────
    setup_table(tables, "Menu Items", [
        {"name": "En",          "type": "singleLineText"},
        {"name": "Section",     "type": "singleLineText"},
        {"name": "Ko",          "type": "singleLineText"},
        {"name": "Rom",         "type": "singleLineText"},
        {"name": "Description", "type": "multilineText"},
        {"name": "Prices",      "type": "singleLineText"},
        {"name": "Tags",        "type": "multipleSelects",
         "options": {"choices": [
             {"name": "seafood"},
             {"name": "spicy"},
             {"name": "veg"},
             {"name": "sig"},
             {"name": "premium"},
         ]}},
        {"name": "Sub",  "type": "singleLineText"},
        {"name": "Sort", "type": "number", "options": {"precision": 0}},
    ])

    # ── BBQ Cuts ──────────────────────────────────────────────────
    setup_table(tables, "BBQ Cuts", [
        {"name": "En",        "type": "singleLineText"},
        {"name": "Ko",        "type": "singleLineText"},
        {"name": "Tier",      "type": "singleSelect",
         "options": {"choices": [
             {"name": "premium"},
             {"name": "regular"},
             {"name": "duck"},
         ]}},
        {"name": "Price",     "type": "number", "options": {"precision": 0}},
        {"name": "Highlight", "type": "checkbox", "options": {"icon": "check", "color": "yellowBright"}},
    ])

    # ── BBQ Assortments ───────────────────────────────────────────
    setup_table(tables, "BBQ Assortments", [
        {"name": "Name",      "type": "singleLineText"},
        {"name": "Items",     "type": "multilineText"},
        {"name": "Price",     "type": "number", "options": {"precision": 0}},
        {"name": "Highlight", "type": "checkbox", "options": {"icon": "check", "color": "yellowBright"}},
        {"name": "Sort",      "type": "number", "options": {"precision": 0}},
    ])

    # ── Tasting ───────────────────────────────────────────────────
    setup_table(tables, "Tasting", [
        {"name": "Title",       "type": "singleLineText"},
        {"name": "Description", "type": "multilineText"},
        {"name": "Courses",     "type": "multilineText"},
        {"name": "Price",       "type": "number", "options": {"precision": 0}},
        {"name": "Sort",        "type": "number", "options": {"precision": 0}},
    ])

    # ── Photos ────────────────────────────────────────────────────
    setup_table(tables, "Photos", [
        {"name": "Dish Name", "type": "singleLineText"},
        {"name": "URL",       "type": "url"},
    ])

    print()
    print("Done. Run:  py seed.py")


if __name__ == "__main__":
    main()
