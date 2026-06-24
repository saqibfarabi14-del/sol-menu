# CLAUDE.md — SOL Menu

This file documents the `sol-menu` repository for AI assistants. Read it before making any changes.

---

## What this project is

A **build pipeline** for a self-contained luxury restaurant digital menu. The workflow is:

1. Edit data in **Airtable**
2. Run `python build.py`
3. Get a fresh `SOL_v3_built.html` with data baked in
4. Deploy via GitHub Pages

The menu is a single, fully self-contained HTML file — no external JS dependencies, no build framework, no bundler.

---

## Repository structure

```
sol-menu/
├── SOL_v3.html            ← Source template — NEVER modified by build or AI
├── SOL_v3_built.html      ← Build output (overwritten on every build)
├── index.html             ← GitHub Pages entry point
├── build.py               ← Main build script (Airtable → HTML injection)
├── seed.py                ← Seeds Airtable tables with initial data
├── setup_fields.py        ← Creates Airtable fields programmatically
├── cleanup.py             ← Utility to clean up Airtable records
├── verify.py              ← Verifies Airtable connection and data shape
├── requirements.txt       ← requests==2.31.0, python-dotenv==1.0.1
├── airtable_schema.md     ← Canonical Airtable table/field reference
├── SOL_MENU_BRIEF.md      ← Project context brief
├── CNAME                  ← GitHub Pages custom domain
├── manifest.json          ← PWA manifest
├── ambiance.mp4           ← Background video asset
├── favicon*, icon*, apple-touch-icon.png  ← PWA/favicon assets
├── sitemap.xml
├── robots.txt
└── .github/
    └── workflows/
        └── build.yml      ← CI: manual + auto-trigger on SOL_v3.html push
```

---

## The sacred rule: never touch `SOL_v3.html`

`SOL_v3.html` is the **source template**. The build always reads from it and writes to `SOL_v3_built.html`. The build script, CI pipeline, and any AI assistant must never write to or overwrite `SOL_v3.html`.

---

## How the build works (`build.py`)

`build.py` performs string-marker injection — not regex replacement. It locates four JavaScript `const` blocks by searching for start and end string markers, then replaces each block with freshly serialized Airtable data.

### The four injected blocks

| Start marker | End marker | Content |
|---|---|---|
| `const SOL_DATA` | `/* ── Apply meta to page` | Restaurant meta (phone, email, hours, socials, photos) |
| `const ITEMS=` | `const BBQ=` | 104 menu dishes |
| `const BBQ=` | `const SIG=` | BBQ cuts by tier + assortments |
| `const SIG=` | `/* ═══ TAG + PRICE` | Chef's Path tasting menus |

### Running the build

```bash
pip install -r requirements.txt
# Set AIRTABLE_TOKEN and AIRTABLE_BASE_ID in .env first
python build.py
# Writes SOL_v3_built.html
```

### Environment variables

```
AIRTABLE_TOKEN=patXXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
```

- Place in `.env` for local runs (loaded by `python-dotenv`)
- Add as GitHub Actions secrets for CI runs (Settings → Secrets → Actions)

---

## Airtable data model

6 tables in one base. Field names must match exactly — the build script uses them verbatim.

### `Menu Items` (104 dishes)

| Field | Type | Notes |
|---|---|---|
| En | Single line | English name — primary field |
| Section | Single line | Section ID (see list below) |
| Ko | Single line | Korean name |
| Rom | Single line | Romanisation (optional) |
| Description | Long text | Dish description |
| Prices | Single line | `5100` or `3 pcs:1350, 5 pcs:2150` |
| Tags | Multiple select | `seafood`, `spicy`, `veg`, `sig`, `premium` |
| Sub | Single line | Only for noodles: `hot` or `cold` |
| Sort | Number | Display order within section |

**Section IDs**: `hoe`, `chobap`, `mandu`, `kimbap`, `appetizers`, `salad`, `soup-stew`, `hotpot`, `chicken`, `beef`, `seafood`, `vegetable`, `noodles`, `rice`, `sotbap`, `beverages`, `dessert`

### `BBQ Cuts`

| Field | Type | Notes |
|---|---|---|
| En | Single line | English name — primary field |
| Ko | Single line | Korean name |
| Tier | Single select | `premium`, `regular`, or `duck` |
| Price | Number | Price in BDT |
| Highlight | Checkbox | Gold styling |

### `BBQ Assortments`

| Field | Type | Notes |
|---|---|---|
| Name | Single line | Primary field |
| Items | Long text | One cut name per line |
| Price | Number | Total price in BDT |
| Highlight | Checkbox | Gold styling |
| Sort | Number | Display order |

### `Tasting` (Chef's Path menus)

| Field | Type | Notes |
|---|---|---|
| Title | Single line | e.g. `Seven Course` |
| Description | Long text | Menu intro |
| Courses | Long text | One `한국어 · English` pair per line |
| Price | Number | Per-person price |
| Sort | Number | Display order |

### `Meta` (key/value)

Required keys: `name`, `tagline`, `phone`, `whatsapp`, `email`, `instagram`, `facebook`, `address`, `coordinates`, `ga4`, `hours`

### `Photos` (optional)

| Field | Notes |
|---|---|
| Dish Name | Must match `En` field in Menu Items exactly |
| URL | Cloudinary or CDN link |

### Price field format

- Single price: `5100` → `[{"a": 5100}]`
- Multi-variant: `3 pcs:1350, 5 pcs:2150` → `[{"l":"3 pcs","a":1350},{"l":"5 pcs","a":2150}]`

---

## HTML constraints — do not violate

The HTML was written for maximum browser compatibility. These rules are hard constraints:

- **No optional chaining** (`?.`) — use `&&` guards instead
- **No `URLSearchParams`** — not supported in all target browsers
- **No `const`/`let` inside swipe handlers** — use `var`
- **No external JS dependencies** — the file must be fully self-contained
- **No modification of `SOL_v3.html`** — build always writes to `SOL_v3_built.html`

When editing the HTML template (`SOL_v3.html`) directly for layout/style changes, observe these constraints throughout.

---

## GitHub Actions CI (`build.yml`)

Two triggers:
- **Manual**: Actions tab → "Build SOL Menu" → Run workflow
- **Auto**: fires when `SOL_v3.html` is pushed to the repo

The workflow:
1. Checks out the repo
2. Installs Python dependencies
3. Runs `python build.py` (using repo secrets)
4. Uploads `SOL_v3_built.html` as a downloadable artifact
5. Commits the built file back to the repo

Required repo secrets: `AIRTABLE_TOKEN`, `AIRTABLE_BASE_ID`

---

## Utility scripts

| Script | Purpose |
|---|---|
| `seed.py` | Seeds all 6 Airtable tables with SOL's real menu data |
| `setup_fields.py` | Creates Airtable field definitions programmatically |
| `cleanup.py` | Deletes all records from tables (use with caution) |
| `verify.py` | Confirms Airtable connectivity and validates data shapes |

---

## Development workflow

### Making menu data changes
1. Edit records in Airtable (never edit `SOL_v3_built.html` directly)
2. Run `python build.py` locally to preview
3. Push `SOL_v3.html` (or trigger manually) to auto-rebuild via CI

### Making layout/style changes
1. Edit `SOL_v3.html` directly (respect HTML constraints above)
2. Run `python build.py` to produce the built version
3. Test `SOL_v3_built.html` in a browser
4. Commit both files

### First-time setup
1. Create the 6 Airtable tables using `airtable_schema.md`
2. Fill in `.env` with `AIRTABLE_TOKEN` and `AIRTABLE_BASE_ID`
3. Run `python seed.py` to populate data
4. Run `python build.py` and verify `SOL_v3_built.html`
5. Push to GitHub and confirm the Actions workflow

---

## Airtable API pattern

`build.py` fetches all records with pagination, using a shared helper:

```python
def fetch_table(table_name):
    # Follows offset pagination automatically
    # Exits with sys.exit(1) on HTTP errors
```

All Airtable field access uses the safe getter `f(record, "FieldName", default="")` to handle missing fields gracefully.
