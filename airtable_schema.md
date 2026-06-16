# Airtable Schema — SOL Menu

Create **6 tables** in a single Airtable base. Field names must match exactly.

---

## Table 1: `Menu Items`
*104 dishes — the main menu body.*

| Field name  | Field type              | Notes / Example                                              |
|-------------|-------------------------|--------------------------------------------------------------|
| En          | Single line text        | English name — **primary field**. e.g. `Assorted Sashimi`   |
| Section     | Single line text        | Matches section IDs in the HTML: `hoe`, `chobap`, `mandu`, `kimbap`, `appetizers`, `salad`, `soup-stew`, `hotpot`, `chicken`, `beef`, `seafood`, `vegetable`, `noodles`, `rice`, `sotbap`, `beverages`, `dessert` |
| Ko          | Single line text        | Korean name. e.g. `모둠회`                                   |
| Rom         | Single line text        | Romanisation. e.g. `Modeum Hoe` (leave blank if none)        |
| Description | Long text               | Dish description paragraph                                   |
| Prices      | Single line text        | **Single price:** `5100` · **Multi-variant:** `3 pcs:1350, 5 pcs:2150` |
| Tags        | Multiple select         | Options: `seafood` `spicy` `veg` `sig` `premium`             |
| Sub         | Single line text        | Only for noodles — enter `hot` or `cold`. Leave blank otherwise. |
| Sort        | Number                  | Controls order within a section. 10, 20, 30… (leave gaps)   |

### Section IDs reference
```
hoe          → Hoe (Sashimi)
chobap       → Chobap (Nigiri)
mandu        → Mandu (Dumplings)
kimbap       → Kimbap
appetizers   → Appetizers
salad        → Salad
soup-stew    → Soups & Stew
hotpot       → Hotpot
chicken      → Chicken mains
beef         → Beef mains
seafood      → Seafood mains
vegetable    → Vegetable mains
noodles      → Noodles (use Sub: hot/cold)
rice         → Rice & Bibimbap
sotbap       → Sotbap (Claypot Rice)
beverages    → Beverages
dessert      → Dessert
```

---

## Table 2: `BBQ Cuts`
*Individual BBQ cuts (premium, regular, duck tiers).*

| Field name | Field type   | Notes / Example                                              |
|------------|--------------|--------------------------------------------------------------|
| En         | Single line  | English name — **primary field**. e.g. `Wagyu A5 Ribeye`    |
| Ko         | Single line  | Korean name. e.g. `와규 A5 립아이`                           |
| Tier       | Single select| `premium` · `regular` · `duck`                               |
| Price      | Number       | Price in BDT e.g. `8800`                                     |
| Highlight  | Checkbox     | Check for gold "highlight" styling (Wagyu A5, Assortment III)|

---

## Table 3: `BBQ Assortments`
*Pre-set tasting assortments shown at the bottom of the BBQ section.*

| Field name | Field type  | Notes / Example                                              |
|------------|-------------|--------------------------------------------------------------|
| Name       | Single line | **Primary field.** e.g. `Assortment I`                       |
| Items      | Long text   | One cut name per line. e.g.:<br>`Regular Ribeye`<br>`Regular Short Ribs`<br>`Regular LA Galbi`<br>`Premium Wagyu Brisket` |
| Price      | Number      | Total price e.g. `13100`                                     |
| Highlight  | Checkbox    | Check for gold styling                                       |
| Sort       | Number      | Display order: 10, 20, 30…                                   |

---

## Table 4: `Tasting`
*Chef's Path tasting menus (Seven Course, Nine Course, etc.).*

| Field name  | Field type  | Notes / Example                                              |
|-------------|-------------|--------------------------------------------------------------|
| Title       | Single line | **Primary field.** e.g. `Seven Course`                       |
| Description | Long text   | Menu intro paragraph                                         |
| Courses     | Long text   | One dish per line in format `한국어 · English name`<br>e.g.:<br>`게 새우 샐러드 · Crab Prawn Salad`<br>`꿀새우볼 · Honey Shrimp Ball`<br>(if no Korean, just write the English name) |
| Price       | Number      | Per person price e.g. `9700`                                 |
| Sort        | Number      | Display order: 10, 20…                                       |

---

## Table 5: `Meta`
*Restaurant contact info, social links, GA4 tag.*

| Field name | Field type  | Notes                              |
|------------|-------------|------------------------------------|
| Key        | Single line | **Primary field.** Exact key names below. |
| Value      | Single line | The value for that key             |

### Required rows in Meta:

| Key           | Example value                                                  |
|---------------|----------------------------------------------------------------|
| `name`        | `SOL Korean BBQ`                                               |
| `tagline`     | `Wood. Stone. Fire.`                                           |
| `phone`       | `+8801717567556`                                               |
| `whatsapp`    | `+8801717567556`                                               |
| `email`       | `sol.restaurant.bd@gmail.com`                                  |
| `instagram`   | `https://www.instagram.com/sol.dhk`                            |
| `facebook`    | `https://www.facebook.com/solrestaurant`                       |
| `address`     | `12th Floor, Ventura Mall, Road 103, Gulshan 2, Dhaka-1212`    |
| `coordinates` | `23.7937° N, 90.4066° E`                                       |
| `ga4`         | `G-XXXXXXXXXX`                                                 |
| `hours`       | `Thu – Sun, Dinner`                                            |

---

## Table 6: `Photos`
*Maps English dish names to image URLs.*

| Field name | Field type  | Notes                                                        |
|------------|-------------|--------------------------------------------------------------|
| Dish Name  | Single line | **Primary field.** Must match the `En` field in Menu Items exactly. e.g. `Mosaic Kimbap` |
| URL        | URL         | Cloudinary, S3, or any CDN link. e.g. `https://res.cloudinary.com/...` |

> Leave this table empty initially — the menu works fine without photos. Add them over time.

---

## Getting your credentials

1. **Base ID** — open your base. The URL is `https://airtable.com/appXXXXXXXXXXXXXX/...`.  
   Copy the `appXXX...` segment.

2. **Personal Access Token** → [airtable.com/create/tokens](https://airtable.com/create/tokens)  
   Scopes needed: `data.records:read` on your base.

3. Add to `.env`:
   ```
   AIRTABLE_TOKEN=patXXXXXXXXXXXXXX
   AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
   ```

4. For GitHub Actions → Settings → Secrets → Actions → New repository secret.  
   Add `AIRTABLE_TOKEN` and `AIRTABLE_BASE_ID`.

---

## Local run

```bash
pip install -r requirements.txt
python build.py
# → writes SOL_v3_built.html (SOL_v3.html is never touched)
```

## Prices format cheatsheet

| Airtable Prices field | Result in menu |
|-----------------------|----------------|
| `5100`                | ৳ 5,100        |
| `3 pcs:1350, 5 pcs:2150` | 3 pcs ৳ 1,350 / 5 pcs ৳ 2,150 |
| `2 pcs:750, 4 pcs:1490`  | 2 pcs ৳ 750 / 4 pcs ৳ 1,490  |
