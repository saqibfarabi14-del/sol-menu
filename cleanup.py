"""
Deletes blank default rows Airtable adds when a new table is created.
"""
import os, sys, requests
from dotenv import load_dotenv

load_dotenv()
TOKEN   = os.environ.get("AIRTABLE_TOKEN", "")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID", "")
HEADERS = {"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"}
API     = "https://api.airtable.com/v0/" + BASE_ID + "/"

# primary field for each table — blank rows have no value here
PRIMARY = {
    "Menu Items":      "En",
    "BBQ Cuts":        "En",
    "BBQ Assortments": "Name",
    "Tasting":         "Title",
    "Meta":            "Key",
}

def fetch_all(table):
    url = API + requests.utils.quote(table)
    records, params = [], {}
    while True:
        r = requests.get(url, headers=HEADERS, params=params).json()
        records.extend(r.get("records", []))
        if not r.get("offset"): break
        params["offset"] = r["offset"]
    return records

def delete_records(table, ids):
    url = API + requests.utils.quote(table)
    for i in range(0, len(ids), 10):
        batch = ids[i:i+10]
        params = [("records[]", rid) for rid in batch]
        r = requests.delete(url, headers=HEADERS, params=params)
        if r.status_code != 200:
            print("  ERROR: " + r.text)

print("Cleaning up blank rows...")
for table, primary in PRIMARY.items():
    records = fetch_all(table)
    blank = [r["id"] for r in records if not r.get("fields", {}).get(primary, "").strip()]
    if blank:
        delete_records(table, blank)
        print("  " + table + ": deleted " + str(len(blank)) + " blank rows")
    else:
        print("  " + table + ": clean")

print("Done.")
