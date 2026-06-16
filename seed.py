"""
SOL Menu — Airtable Seed Script
─────────────────────────────────
Pushes all menu data into your Airtable base in one shot.
Run ONCE after creating the 6 tables in Airtable.

Usage:
    python seed.py

Env vars (in .env):
    AIRTABLE_TOKEN   — Personal Access Token (pat...)
    AIRTABLE_BASE_ID — Base ID (app...)
"""

import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN   = os.environ.get("AIRTABLE_TOKEN", "")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID", "")

if not TOKEN or not BASE_ID:
    print("ERROR: AIRTABLE_TOKEN and AIRTABLE_BASE_ID must be set in .env")
    sys.exit(1)

HEADERS = {
    "Authorization": "Bearer " + TOKEN,
    "Content-Type": "application/json",
}
API_URL = "https://api.airtable.com/v0/" + BASE_ID + "/"


# ── Airtable helper ───────────────────────────────────────────────────────────

def create_records(table, records):
    """Push records in batches of 10 (Airtable API limit)."""
    url = API_URL + requests.utils.quote(table)
    created = 0
    for i in range(0, len(records), 10):
        batch = records[i : i + 10]
        payload = {"records": [{"fields": r} for r in batch]}
        resp = requests.post(url, headers=HEADERS, json=payload)
        if resp.status_code not in (200, 201):
            print("ERROR in '" + table + "': " + resp.text)
            sys.exit(1)
        created += len(batch)
        print("  " + table + ": " + str(created) + " / " + str(len(records)))
        time.sleep(0.25)  # stay under rate limit
    return created


# ── DATA ──────────────────────────────────────────────────────────────────────

META = [
    {"Key": "name",        "Value": "SOL Korean BBQ"},
    {"Key": "tagline",     "Value": "Wood. Stone. Fire."},
    {"Key": "phone",       "Value": "+8801717567556"},
    {"Key": "whatsapp",    "Value": "+8801717567556"},
    {"Key": "email",       "Value": "sol.restaurant.bd@gmail.com"},
    {"Key": "instagram",   "Value": "https://www.instagram.com/sol.dhk"},
    {"Key": "facebook",    "Value": "https://www.facebook.com/solrestaurant"},
    {"Key": "address",     "Value": "12th Floor, Ventura Mall, Road 103, Gulshan 2, Dhaka-1212"},
    {"Key": "coordinates", "Value": "23.7937° N, 90.4066° E"},
    {"Key": "ga4",         "Value": "G-XXXXXXXXXX"},
    {"Key": "hours",       "Value": "Thu – Sun, Dinner"},
]

# 104 menu items. Tags are lists (Airtable multiple-select).
# Records without Tags are omitted from the field so Airtable leaves them blank.
ITEMS = [
    # ── HOE (Sashimi) ─────────────────────────────────────────────────────────
    {"Section":"hoe","Ko":"모둠회","Rom":"Modeum Hoe","En":"Assorted Sashimi",
     "Description":"Eel, salmon, tuna, and scallop — sliced to order, served over crushed ice with perilla, crisp seaweed and house dipping sauce.",
     "Prices":"5100","Tags":["seafood","premium","sig"],"Sort":10},
    {"Section":"hoe","Ko":"연어회","Rom":"Salmon Hoe","En":"Salmon Sashimi",
     "Description":"Premium salmon sliced thin and served at the precise temperature where the fat is alive — clean, delicate, and nothing more.",
     "Prices":"3 pcs:1350, 5 pcs:2150","Tags":["seafood"],"Sort":20},
    {"Section":"hoe","Ko":"참치회","Rom":"Tuna Hoe","En":"Tuna Sashimi",
     "Description":"Deep-red tuna brought to room temperature so the richness fully opens — served with wasabi and a soy that stays in the background.",
     "Prices":"3 pcs:1450, 5 pcs:2250","Tags":["seafood","premium"],"Sort":30},
    {"Section":"hoe","Ko":"장어회","Rom":"Jangeo Hoe","En":"Eel Sashimi",
     "Description":"Eel sashimi sliced with precision — its natural sweetness present before any sauce, the texture firm and clean.",
     "Prices":"3 pcs:1750, 5 pcs:2950","Tags":["seafood","premium"],"Sort":40},

    # ── CHOBAP (Nigiri) ────────────────────────────────────────────────────────
    {"Section":"chobap","Ko":"모둠초밥","Rom":"Modeum Chobap","En":"Assorted Nigiri",
     "Description":"Eel, salmon, tuna and scallop pressed over vinegared rice — each piece made to order, the fish at room temperature so the fat is fully awake.",
     "Prices":"2980","Tags":["seafood","premium","sig"],"Sort":10},
    {"Section":"chobap","Ko":"연어초밥","Rom":"Salmon Chobap","En":"Salmon Nigiri",
     "Description":"Flame-seared salmon over seasoned rice — the heat applied only enough to release the oil, leaving the centre cool and silky.",
     "Prices":"2 pcs:750, 4 pcs:1490","Tags":["seafood"],"Sort":20},
    {"Section":"chobap","Ko":"참치초밥","Rom":"Tuna Chobap","En":"Tuna Nigiri",
     "Description":"Tuna pressed over vinegared rice at the exact moment the fish is at room temperature — the result is a single clean flavour, nothing competing.",
     "Prices":"2 pcs:850, 4 pcs:1650","Tags":["seafood"],"Sort":30},
    {"Section":"chobap","Ko":"장어초밥","Rom":"Jangeo Chobap","En":"Eel Nigiri",
     "Description":"Glazed eel over delicate sushi rice — the lacquered sweetness of the eel settles into the vinegared grain.",
     "Prices":"2 pcs:1150, 4 pcs:2250","Tags":["seafood","premium"],"Sort":40},

    # ── MANDU (Dumplings) ──────────────────────────────────────────────────────
    {"Section":"mandu","Ko":"트러플 비프 만두","Rom":"Truffle Sogogi Mandu","En":"Truffle Beef Dumplings",
     "Description":"Beef folded with truffle oil, ginger and scallion inside a thin steamed skin — the truffle is present but never loud, letting the beef carry the weight.",
     "Prices":"1150","Tags":["sig","premium"],"Sort":10},
    {"Section":"mandu","Ko":"마라튀김만두","Rom":"Saeu Mala Mandu","En":"Prawn & Chicken Fried Dumplings",
     "Description":"Prawn and chicken fried until the pleated base crisps and the skin blisters — finished with mala spice that numbs the lips and keeps you reaching for the next one.",
     "Prices":"1150","Tags":["spicy","seafood"],"Sort":20},
    {"Section":"mandu","Ko":"소고기김치만두","Rom":"Sogogi Gimchi Mandu","En":"Beef Kimchi Dumplings",
     "Description":"Aged kimchi and spiced beef packed into a pan-fried skin — the kimchi's sourness and the beef's richness have nowhere to go but into each other.",
     "Prices":"980","Sort":30},
    {"Section":"mandu","Ko":"그린 매듭 만두","Rom":"Geurin Maedeub Mandu","En":"Green Knot Dumplings",
     "Description":"Chicken and shiitake folded inside translucent rice paper and tied at the top — the wrapper reveals everything inside before you open it.",
     "Prices":"850","Sort":40},
    {"Section":"mandu","Ko":"닭고기 만두","Rom":"Dakgogi Mandu","En":"Chicken Cheese Dumplings",
     "Description":"Steamed until the skin turns translucent and the cheese inside goes completely molten — bite carefully, the first one always surprises.",
     "Prices":"750","Sort":50},
    {"Section":"mandu","Ko":"치킨새우만두","Rom":"Dak Saeu Mandu","En":"Chicken Prawn Mandu",
     "Description":"Tender chicken and prawn folded together in a light, thin-skinned dumpling — clean flavour, gentle bite.",
     "Prices":"750","Tags":["seafood"],"Sort":60},
    {"Section":"mandu","Ko":"양배추만두","Rom":"Yangbaechu Mandu","En":"Chicken Cabbage Dumplings",
     "Description":"Light chicken, cabbage, and tofu wrapped in a delicate, thin skin for a subtle bite.",
     "Prices":"680","Sort":70},

    # ── KIMBAP ────────────────────────────────────────────────────────────────
    {"Section":"kimbap","Ko":"모자이크 김밥","Rom":"Mosaic Kimbap","En":"Mosaic Kimbap",
     "Description":"Named for what it reveals when sliced — a mosaic of salmon, tuna, crab stick, cream cheese and avocado. Each cross-section a small piece of edible art.",
     "Prices":"1850","Tags":["sig"],"Sort":10},
    {"Section":"kimbap","Ko":"로제 김밥","Rom":"Rosé Kimbap","En":"Rosé Kimbap",
     "Description":"Pink-tinted rice wrapped around salmon, cream cheese and crab stick — it arrives looking like something from a different world, and tastes as good as it looks.",
     "Prices":"1790","Tags":["seafood"],"Sort":20},
    {"Section":"kimbap","Ko":"우나기 김밥","Rom":"Unagi Kimbap","En":"Unagi Kimbap",
     "Description":"Glazed eel with avocado and spicy mayo rolled into seasoned rice — the eel's caramelised sweetness meets the cool creaminess of avocado in every bite.",
     "Prices":"1760","Tags":["seafood"],"Sort":30},
    {"Section":"kimbap","Ko":"깻잎 불고기 김밥","Rom":"Gaennip Bulgogi Kimbap","En":"Kkaennip Bulgogi Kimbap",
     "Description":"Tender bulgogi meets aromatic kkaennip leaf — a balanced, modern roll where sweet soy and fresh herb find each other.",
     "Prices":"1150","Sort":40},
    {"Section":"kimbap","Ko":"참치김밥","Rom":"Chamchi Kimbap","En":"Cabbage Tuna Kimbap",
     "Description":"Shredded cabbage and tuna folded together — a creamy, familiar bite with clean contrast.",
     "Prices":"1150","Tags":["seafood"],"Sort":50},
    {"Section":"kimbap","Ko":"맛살 김밥","Rom":"Matsal Kimbap","En":"Crab Stick Kimbap",
     "Description":"Crab stick and cream cheese rolled with spinach and seasoned rice — smooth, delicate, and quietly satisfying.",
     "Prices":"950","Tags":["seafood"],"Sort":60},

    # ── APPETIZERS ────────────────────────────────────────────────────────────
    {"Section":"appetizers","Ko":"꿀새우볼","Rom":"Ggul Saewoo Ball","En":"Honey Shrimp Ball",
     "Description":"Golden-fried shrimp balls lacquered in a citrus-honey glaze — crisp shell, yielding centre, sweet heat that lingers at the back.",
     "Prices":"950","Tags":["seafood","sig"],"Sort":10},
    {"Section":"appetizers","Ko":"새우튀김","Rom":"Saeu Twigim","En":"Korean Prawn Tempura",
     "Description":"Whole prawns in a batter so thin it barely exists — fried to a shattering crisp and served with a soy dip that brings everything into focus.",
     "Prices":"1450","Tags":["seafood"],"Sort":20},
    {"Section":"appetizers","Ko":"오징어튀김","Rom":"Ojingeo Twigim","En":"Cuttlefish Tempura",
     "Description":"Cuttlefish sliced thick and battered to an almost translucent crisp — tender inside, a clean ocean flavour that the light batter never overwhelms.",
     "Prices":"1450","Tags":["seafood"],"Sort":30},
    {"Section":"appetizers","Ko":"새우 오징어전","Rom":"Saeu Ojing-eo Jeon","En":"Squid & Shrimp Pancake",
     "Description":"A wide golden pancake of squid and shrimp — crisp at the edges, yielding at the centre, with a soy dipping sauce that cuts through the richness.",
     "Prices":"1480","Tags":["seafood"],"Sort":40},
    {"Section":"appetizers","Ko":"해물파전","Rom":"Haemul Pajeon","En":"Seafood Scallion Pancake",
     "Description":"Haemul pajeon — a wide, golden pancake of prawn and cuttlefish with charred scallion edges. Cut tableside.",
     "Prices":"1380","Tags":["seafood"],"Sort":50},
    {"Section":"appetizers","Ko":"닭양파","Rom":"Dak Yangpa","En":"Crispy Snow Chicken",
     "Description":"Crackling fried chicken beneath a drift of cold cream and raw onion — the contrast between hot and cold, crisp and cool, is the whole point.",
     "Prices":"1280","Sort":60},
    {"Section":"appetizers","Ko":"콘치즈","Rom":"Kkon-Chijeu","En":"Corn Parmesan Cheese",
     "Description":"Prawn, crabstick and sweet corn enfolded in warm, stretching mozzarella — finished with parmesan that browns and crisps at the edges.",
     "Prices":"1350","Tags":["seafood"],"Sort":70},
    {"Section":"appetizers","Ko":"주먹밥튀김","Rom":"Jumeok-bap Twigim","En":"Fried Bibimbap Ball",
     "Description":"The entire architecture of bibimbap compressed into a crisp, golden rice ball — served over a creamy base and finished with parmesan. A clever, satisfying bite.",
     "Prices":"1450","Tags":["veg"],"Sort":80},
    {"Section":"appetizers","Ko":"로제 떡볶이","Rom":"Rosé Tteokbokki","En":"Creamy Rosé Rice Cake",
     "Description":"Thick-cut rice cakes pulled through a blush rosé-gochujang cream — silky, gently spiced, with a heat that never overwhelms the sweetness.",
     "Prices":"1950","Tags":["spicy","veg"],"Sort":90},
    {"Section":"appetizers","Ko":"떡볶이","Rom":"Tteokbokki","En":"Spicy Rice Cake",
     "Description":"Thick rice cakes simmered in a dark, deeply reduced gochujang that clings to every surface — spicy, sticky, and nearly irresistible.",
     "Prices":"1650","Tags":["spicy","veg"],"Sort":100},
    {"Section":"appetizers","Ko":"팽이튀김","Rom":"Paengi Twigim","En":"Enoki Tempura",
     "Description":"Enoki clusters dipped in a barely-there batter and fried until they shatter at the touch — golden, paper-thin, impossible to stop.",
     "Prices":"1150","Tags":["veg"],"Sort":110},
    {"Section":"appetizers","Ko":"김치전","Rom":"Kimchi Jeon","En":"Kimchi Pancake",
     "Description":"Aged kimchi folded into a batter and pressed wide on a hot iron until the edges turn deeply golden — tangy, rich, and impossible to share.",
     "Prices":"900","Tags":["spicy"],"Sort":120},
    {"Section":"appetizers","Ko":"계란찜","Rom":"Gyeran-Jjim","En":"Steamed Egg Custard",
     "Description":"Egg steamed until it trembles — a cloud-light custard barely set, seasoned with melted soft cheese that pools at the surface.",
     "Prices":"650","Tags":["veg"],"Sort":130},

    # ── SALAD ─────────────────────────────────────────────────────────────────
    {"Section":"salad","Ko":"연어 샐러드","Rom":"Yeoneo Salad","En":"Salmon Avocado Salad",
     "Description":"Salmon and avocado layered with sweet orange and cream cheese over crisp lettuce — bright, creamy and citrus-lifted, with a clean finish that makes you want another forkful.",
     "Prices":"2350","Tags":["seafood"],"Sort":10},
    {"Section":"salad","Ko":"게 새우 샐러드","Rom":"Ge-saeu Salad","En":"Crab Prawn Salad",
     "Description":"Sweet crab and crispy prawns over fresh greens in a silky mayo dressing — a lively balance of crunch, creaminess, and brine that opens the palate.",
     "Prices":"1650","Tags":["seafood"],"Sort":20},
    {"Section":"salad","Ko":"호두 샐러드","Rom":"Hodu Salad","En":"Walnut Salad",
     "Description":"Lettuce and red cabbage with toasted walnuts and dried dashima — tossed in a savoury vinaigrette that earns its place as the quietest, most considered dish on the table.",
     "Prices":"1550","Tags":["veg"],"Sort":30},
    {"Section":"salad","Ko":"오징어 무침","Rom":"Ojing-eo Muchim","En":"Spicy Cuttlefish Salad",
     "Description":"Chilled cuttlefish and crisp vegetables in a bright gochugaru chili-vinegar dressing — cold, bold, and deeply refreshing.",
     "Prices":"1450","Tags":["spicy","seafood"],"Sort":40},
    {"Section":"salad","Ko":"감자샐러드","Rom":"Gamja Salad","En":"Potato Salad",
     "Description":"Korean-style potato salad — smooth and lightly sweet, with a softness that contrasts every crisp and char that comes after it.",
     "Prices":"850","Tags":["veg"],"Sort":50},

    # ── SOUP & STEW ───────────────────────────────────────────────────────────
    {"Section":"soup-stew","Ko":"갈비탕","Rom":"Galbitang","En":"Beef Short Rib Soup",
     "Description":"A long-simmered bone broth so clear you can see the short ribs at the bottom — radish softened through, glass noodles folded in. One of the most quietly impressive dishes on the menu.",
     "Prices":"1780","Sort":10},
    {"Section":"soup-stew","Ko":"해물탕","Rom":"Haemul Tang","En":"Seafood Soft Tofu Stew",
     "Description":"Silken tofu trembling in a fiery seafood broth — prawn, cuttlefish and octopus beneath the surface, the heat arriving slowly and staying.",
     "Prices":"1680","Tags":["spicy","seafood"],"Sort":20},
    {"Section":"soup-stew","Ko":"소꼬리탕","Rom":"Kkori Gomtang","En":"Oxtail Soup",
     "Description":"Oxtail simmered for hours until the collagen dissolves into the broth — milky, deeply savoury, with meat that slides from the bone without resistance.",
     "Prices":"1480","Sort":30},
    {"Section":"soup-stew","Ko":"꼬리 우거지 곰탕","Rom":"Kkori Ugeoji Gomtang","En":"Slow Simmered Oxtail Stew",
     "Description":"Oxtail braised low and slow until the broth thickens around it — fresh cabbage added late to keep its crunch against the yielding meat.",
     "Prices":"1580","Sort":40},
    {"Section":"soup-stew","Ko":"김치찌개","Rom":"Kimchi Jjigae","En":"Kimchi Stew with Beef",
     "Description":"Aged kimchi and beef simmered until the kimchi loses its edge and takes on a deep, rounded sourness — the broth turns brick-red and lingers.",
     "Prices":"1350","Tags":["spicy"],"Sort":50},
    {"Section":"soup-stew","Ko":"육개장","Rom":"Yuk Gae Jang","En":"Spicy Shredded Beef Soup",
     "Description":"Hand-shredded beef pulled through a fiery gochugaru broth with glass noodles and vegetables — deep red, deeply warming, built for the coldest nights.",
     "Prices":"1050","Tags":["spicy"],"Sort":60},
    {"Section":"soup-stew","Ko":"닭개장","Rom":"Dak Gae Jang","En":"Spicy Chicken Soup",
     "Description":"Chicken shredded by hand and returned to its own broth — gochugaru heat builds with each spoonful, the glass noodles absorbing every bit of it.",
     "Prices":"850","Tags":["spicy"],"Sort":70},
    {"Section":"soup-stew","Ko":"된장찌개","Rom":"Doenjang Jjigae","En":"Soybean Paste Stew",
     "Description":"Fermented soybean paste slow-dissolved into a broth that smells like a Korean home — earthy, umami-deep, with soft tofu and garden vegetables.",
     "Prices":"850","Tags":["veg"],"Sort":80},

    # ── HOTPOT ────────────────────────────────────────────────────────────────
    {"Section":"hotpot","Ko":"불고기 전골","Rom":"Bulgogi Jeongol","En":"Bulgogi Hotpot",
     "Description":"Marinated bulgogi beef lowered into a bubbling broth tableside — glass noodles, mushrooms and vegetables follow, absorbing the sweetened soy as the pot builds in depth.",
     "Prices":"3750","Tags":["sig"],"Sort":10},
    {"Section":"hotpot","Ko":"부대찌개","Rom":"Budae Jjigae","En":"Korean Army Stew",
     "Description":"Born in post-war Korea from whatever was available — beef, sausage, tuna, fishcake, kimchi, tofu, corn and noodles in a deep chili broth. Chaotic by design, and entirely its own thing.",
     "Prices":"3650","Tags":["spicy"],"Sort":20},
    {"Section":"hotpot","Ko":"불낙전골","Rom":"Bulnak Jeongol","En":"Bulnak Hotpot",
     "Description":"Beef and octopus in a fiery red broth — shiitake mushroom and bok choy added tableside. The octopus tightens as it cooks, the beef surrenders. Order this when you want heat that means something.",
     "Prices":"2850","Tags":["spicy","seafood"],"Sort":30},

    # ── CHICKEN ───────────────────────────────────────────────────────────────
    {"Section":"chicken","Ko":"치즈닭갈비","Rom":"Chejeu Dak-Galbi","En":"Dak Galbi with Cheese",
     "Description":"Spicy chicken galbi cooked on a cast iron until the sauce darkens at the edges — finished with a blanket of molten cheese that stretches at the pull.",
     "Prices":"1650","Tags":["spicy"],"Sort":10},
    {"Section":"chicken","Ko":"안동찜닭","Rom":"Andong Jjimdak","En":"Braised Chicken with Glass Noodles",
     "Description":"Bone-in chicken and glass noodles slow-braised in soy, garlic and ginger until the noodles drink up the sauce and the chicken yields at a touch.",
     "Prices":"1650","Sort":20},
    {"Section":"chicken","Ko":"닭도리탕","Rom":"Dakdoritang","En":"Spicy Chicken Stew",
     "Description":"Bone-in chicken pieces simmered in a fiery gochugaru broth until the meat begins to fall — rich, warming, and deeply satisfying on a cold night.",
     "Prices":"1600","Tags":["spicy"],"Sort":30},
    {"Section":"chicken","Ko":"보쌈닭","Rom":"Bossam Dak","En":"Bossam Chicken",
     "Description":"Soft-braised chicken served bossam-style with crisp lettuce leaves for wrapping — a quiet, composed dish with clean flavour.",
     "Prices":"1450","Sort":40},
    {"Section":"chicken","Ko":"양념치킨","Rom":"Yangnyeom Chicken","En":"Sweet & Spicy Fried Chicken",
     "Description":"Double-fried until the crust locks in, then tossed in a glossy chili-sweet sauce that coats every ridge — sticky, addictive, and better than you expect.",
     "Prices":"1190","Tags":["spicy"],"Sort":50},
    {"Section":"chicken","Ko":"닭강정","Rom":"Dak-Gang Jeong","En":"Crispy Glazed Chicken",
     "Description":"Fried chicken pieces tossed in a dark, sticky glaze — sesame and walnut add crunch where the coating meets the sauce.",
     "Prices":"1100","Sort":60},
    {"Section":"chicken","Ko":"닭불고기","Rom":"Dak Bulgogi","En":"Chicken Bulgogi",
     "Description":"Chicken marinated in a soy-pear bulgogi base and cooked until the edges catch — aromatic, lightly caramelised, and far lighter than its beef counterpart.",
     "Prices":"1350","Sort":70},
    {"Section":"chicken","Ko":"매운 닭불고기","Rom":"Maeun Dak Bulgogi","En":"Spicy Chicken Bulgogi",
     "Description":"Chicken in a bulgogi marinade turned up with gochugaru — the sweetness keeps pace with the heat, and neither wins.",
     "Prices":"1350","Tags":["spicy"],"Sort":80},
    {"Section":"chicken","Ko":"닭구이","Rom":"Dak Gui","En":"Charcoal Grilled Chicken",
     "Description":"Whole chicken pieces over live charcoal until the skin crisps and the smoke gets inside. Served simply, because it needs nothing else.",
     "Prices":"950","Sort":90},

    # ── BEEF ──────────────────────────────────────────────────────────────────
    {"Section":"beef","Ko":"갈비찜","Rom":"Galbi-jjim","En":"Braised Short Rib",
     "Description":"Galbi-jjim — short rib braised for hours until the bone surrenders. Sweet soy, chestnuts, carrot, and radish absorb every drop.",
     "Prices":"2550","Tags":["sig"],"Sort":10},
    {"Section":"beef","Ko":"동파로우","Rom":"Dongpa Ro-u","En":"Dongpo-Style Braised Beef",
     "Description":"Pork belly braised for hours in a dark soy and Shaoxing reduction until every layer yields completely — served with bok choy, the sauce glossy enough to see your reflection.",
     "Prices":"2450","Tags":["sig"],"Sort":20},
    {"Section":"beef","Ko":"소불고기","Rom":"So Bulgogi","En":"Beef Bulgogi",
     "Description":"Paper-thin slices of beef in the marinade that made Korean cooking famous — soy, pear, sesame, and a touch of sweetness that caramelises at the edges.",
     "Prices":"1950","Sort":30},
    {"Section":"beef","Ko":"매운소불고기","Rom":"Maeun-So Bulgogi","En":"Spicy Beef Bulgogi",
     "Description":"The same tender bulgogi, pulled in a hotter direction — gochugaru heat building slowly over sweet soy, finished with sesame and spring onion.",
     "Prices":"1950","Tags":["spicy"],"Sort":40},
    {"Section":"beef","Ko":"불고기찜","Rom":"Bulgogi-jjim","En":"Braised Bulgogi",
     "Description":"Bulgogi left in the pot long enough to surrender fully — the soy, garlic and ginger reducing into a glossy, deeply savoury braise that coats the meat completely.",
     "Prices":"1850","Sort":50},
    {"Section":"beef","Ko":"꼬리찜","Rom":"Kori Jjim","En":"Braised Oxtail",
     "Description":"Slow-braised oxtail falling off the bone in a deep, aromatic broth of garlic, ginger, and Korean spices — rich and unhurried.",
     "Prices":"1650","Sort":60},

    # ── SEAFOOD MAINS ─────────────────────────────────────────────────────────
    {"Section":"seafood","Ko":"고등어구이","Rom":"Godeungeo Gui","En":"Japanese Grilled Mackerel",
     "Description":"Whole Japanese mackerel grilled over high heat until the skin blisters and chars at the spine — the flesh underneath stays moist and oily-rich. Served with pickled sides that cut clean through.",
     "Prices":"4360","Tags":["seafood"],"Sort":10},
    {"Section":"seafood","Ko":"대구카퍼","Rom":"Daegu Kapeo","En":"Caper Cod Fish",
     "Description":"Cod seared until a golden crust forms, finished with a butter emulsion of lemon and capers that cuts cleanly through the richness.",
     "Prices":"3950","Tags":["seafood"],"Sort":20},
    {"Section":"seafood","Ko":"장어찜","Rom":"Jang-eo Jjim","En":"Steamed Whole Sea Bass",
     "Description":"Whole sea bass steamed until the flesh pulls apart in clean white flakes — barely seasoned, finished with red chili and ginger oil poured hot over the surface.",
     "Prices":"3790","Tags":["seafood"],"Sort":30},
    {"Section":"seafood","Ko":"장어구이","Rom":"Jangeo Gui","En":"Grilled Eel",
     "Description":"Eel grilled over live charcoal until the skin blisters and caramelises — finished with a lacquered reduction that deepens everything. Rich, precise, and memorable.",
     "Prices":"3490","Tags":["seafood","premium"],"Sort":40},
    {"Section":"seafood","Ko":"연어구이두부크림","Rom":"Salmon Gui Dubu Beureom","En":"Grilled Salmon in Cream",
     "Description":"Salmon grilled until the skin is lacquer-crisp, set over a smooth cream of silken tofu and peanut — nutty, savoury, and completely unexpected.",
     "Prices":"2150","Tags":["seafood"],"Sort":50},
    {"Section":"seafood","Ko":"문어볶음","Rom":"Muneo Bokkeum","En":"Spicy Octopus Stir-fry",
     "Description":"Thick-cut octopus seared over high heat with the chef's signature seasoning — bold, chewy, and deeply aromatic.",
     "Prices":"1920","Tags":["spicy","seafood"],"Sort":60},
    {"Section":"seafood","Ko":"생선구이","Rom":"Saengseon Gui","En":"Fried Sea Bass",
     "Description":"Sea bass fried whole until the skin is glass-crisp — finished with a bright pour of citrus and ginger that hisses against the hot surface and perfumes the table.",
     "Prices":"1890","Tags":["seafood"],"Sort":70},
    {"Section":"seafood","Ko":"해물볶음","Rom":"Haemul Bokkeum","En":"Seafood Stir-fry",
     "Description":"Crab, prawn, cuttlefish and octopus hit a screaming-hot wok with gochujang — the sauce caramelises at the edges and the seafood takes on a char that the sauce alone cannot give.",
     "Prices":"1890","Tags":["spicy","seafood"],"Sort":80},

    # ── VEGETABLE ─────────────────────────────────────────────────────────────
    {"Section":"vegetable","Ko":"버섯강정","Rom":"Beoseot Gangjeong","En":"Sweet Crispy Mushrooms",
     "Description":"A trio of shiitake, king oyster, and oyster mushrooms — battered, fried crisp, then glazed in sweet soy. The coating shatters, the mushroom beneath stays soft.",
     "Prices":"1150","Tags":["veg","sig"],"Sort":10},
    {"Section":"vegetable","Ko":"두부김치","Rom":"Dubu Kimchi","En":"Tofu Kimchi",
     "Description":"Aged kimchi stir-fried with tofu and shiitake until the kimchi caramelises and turns a deep brick-red — the tofu absorbs everything around it.",
     "Prices":"900","Tags":["veg"],"Sort":20},
    {"Section":"vegetable","Ko":"두부강정","Rom":"Dubu-gangjeong","En":"Soy Glazed Crispy Tofu",
     "Description":"Tofu fried until the crust shatters on contact — tossed in a dark soy glaze with a thread of sweetness and sesame that makes it disappear faster than anything else on the table.",
     "Prices":"650","Tags":["veg"],"Sort":30},

    # ── NOODLES ───────────────────────────────────────────────────────────────
    {"Section":"noodles","Sub":"hot","Ko":"소고기 잡채","Rom":"Sogogi Japchae","En":"Beef Japchae",
     "Description":"Silky glass noodles with marinated beef, shiitake mushrooms, and crisp vegetables — finished with a deep soy-garlic sweetness that pulls everything together.",
     "Prices":"1800","Tags":["sig"],"Sort":10},
    {"Section":"noodles","Sub":"hot","Ko":"닭고기 잡채","Rom":"Dakgogi Japchae","En":"Chicken Japchae",
     "Description":"Glass noodles wok-tossed with chicken, earthy mushrooms, and seasonal vegetables in a savory-sweet soy glaze — silky, light, and deeply comforting.",
     "Prices":"1550","Sort":20},
    {"Section":"noodles","Sub":"hot","Ko":"짬뽕","Rom":"Jjamppong","En":"Spicy Seafood Noodle Soup",
     "Description":"Fiery broth with crab, prawn, and octopus — simmered deep with vegetables and a smoky chili heat that builds. Noodles arrive already swimming in it.",
     "Prices":"1550","Tags":["spicy","seafood"],"Sort":30},
    {"Section":"noodles","Sub":"hot","Ko":"해물볶음면","Rom":"Haemul Bokkeum Myeon","En":"Spicy Seafood Noodles",
     "Description":"Wok-fired noodles with crab, prawn, and cuttlefish — tossed in a bold chili sauce at high heat until the edges catch.",
     "Prices":"1450","Tags":["spicy","seafood"],"Sort":40},
    {"Section":"noodles","Sub":"hot","Ko":"소고기 라면","Rom":"Beef Ramyun","En":"Beef Ramen",
     "Description":"Spicy peanut broth with chili garlic, soy, and spring onion — served over slow-cooked brisket. Rich, creamy, and completely satisfying.",
     "Prices":"1290","Tags":["spicy"],"Sort":50},
    {"Section":"noodles","Sub":"hot","Ko":"잔치국수","Rom":"Janchi Guksu","En":"Warm Noodle Soup",
     "Description":"A classic Korean celebratory noodle — soft wheat noodles in a clear, gently savory broth. Simple, honest, and warming.",
     "Prices":"950","Sort":60},
    {"Section":"noodles","Sub":"cold","Ko":"비빔냉면","Rom":"Bibim Naengmyeon","En":"Spicy Cold Buckwheat Noodles",
     "Description":"Chilled buckwheat noodles tossed in a fiery-sweet gochugaru sauce — topped with beef, pear, cucumber, a soft egg, and a final flourish of sesame. Cold, bold, and deeply Korean.",
     "Prices":"1250","Tags":["spicy"],"Sort":70},
    {"Section":"noodles","Sub":"cold","Ko":"메밀국수","Rom":"Memil Guksu","En":"Cold Buckwheat Noodles",
     "Description":"Chilled soba-style noodles with a clean soy dressing, toasted sesame, and a whisper of seaweed — restrained and elegant.",
     "Prices":"780","Tags":["veg"],"Sort":80},
    {"Section":"noodles","Sub":"cold","Ko":"말차 콩국수","Rom":"Matcha Kongguksu","En":"Matcha Soymilk Noodles",
     "Description":"Cold soba noodles submerged in creamy matcha-soy milk, a spoon of peanut butter stirred through, topped with lightly torched tofu. Unusual, precise, and quietly addictive.",
     "Prices":"780","Tags":["veg"],"Sort":90},

    # ── RICE & BIBIMBAP ───────────────────────────────────────────────────────
    {"Section":"rice","Ko":"해물비빔밥","Rom":"Haemul Bibimbap","En":"Seafood Bibimbap",
     "Description":"Prawn, cuttlefish and octopus over bibimbap rice in a hot bowl — stir before eating, letting the gochujang paste coat everything as the rice crisps below.",
     "Prices":"1280","Tags":["seafood"],"Sort":10},
    {"Section":"rice","Ko":"주먹밥","Rom":"Jumeok-bap","En":"Korean Rice Balls",
     "Description":"Hand-formed rice balls filled with seasoned beef and wrapped in toasted seaweed — a snack, a side, a small ritual.",
     "Prices":"1280","Sort":20},
    {"Section":"rice","Ko":"해물볶음밥","Rom":"Haemul Bokkeum Bap","En":"Seafood Fried Rice",
     "Description":"Prawn, cuttlefish and octopus wok-fired with day-old rice over maximum heat — the grains separate, the seafood chars at the edges, the sesame oil goes in last.",
     "Prices":"990","Tags":["seafood"],"Sort":30},
    {"Section":"rice","Ko":"돌솥비빔밥","Rom":"Dolsot Bibimbap","En":"Stone Pot Bibimbap",
     "Description":"Rice pressed against a scorching stone pot until a crust forms at the base — topped with chicken or beef and seasonal vegetables. Stir everything in, then listen for the crackle.",
     "Prices":"950","Sort":40},
    {"Section":"rice","Ko":"소고기볶음밥","Rom":"So-gogi Bokkeum Bap","En":"Beef Fried Rice",
     "Description":"Marinated beef and rice wok-fired together until the rice picks up every bit of the soy-sesame flavour from the meat. Rich and complete.",
     "Prices":"950","Sort":50},
    {"Section":"rice","Ko":"닭볶음밥","Rom":"Dak Bokkeum Bap","En":"Chicken Fried Rice",
     "Description":"Seasoned chicken and fragrant rice wok-tossed over high heat — smoky edges, clean flavour, finished with spring onion and sesame.",
     "Prices":"750","Sort":60},
    {"Section":"rice","Ko":"마늘볶음밥","Rom":"Manul Bokkeum Bap","En":"Garlic Fried Rice",
     "Description":"Each grain of rice fried separately with caramelised garlic until the kitchen fills with the smell. Simple, precise, and deeply satisfying.",
     "Prices":"650","Tags":["veg"],"Sort":70},

    # ── SOTBAP (Claypot Rice) ─────────────────────────────────────────────────
    {"Section":"sotbap","Ko":"와규솥밥","Rom":"Wagyu Sotbap","En":"Wagyu Claypot Rice",
     "Description":"A5-grade wagyu short rib rested over seasoned rice and shiitake mushrooms, sealed in a claypot until the fat renders completely into the grain. Opened tableside. Rich, unhurried, precise.",
     "Prices":"2650","Tags":["sig","premium"],"Sort":10},
    {"Section":"sotbap","Ko":"장어솥밥","Rom":"Jangeo Sotbap","En":"Eel Claypot Rice",
     "Description":"Glazed eel placed over uncooked rice and sealed in a claypot — as the rice cooks, the eel's lacquered sweetness seeps through. Lifted with a drizzle of house tare.",
     "Prices":"2250","Tags":["seafood","premium"],"Sort":20},
    {"Section":"sotbap","Ko":"트러플소고기솥밥","Rom":"Teureopeul So-gogi Sotbap","En":"Truffle Beef Claypot Rice",
     "Description":"Beef folded with truffle oil rested over rice in a sealed claypot — as the steam builds, the truffle scent rises first. Lift the lid at the table and let it arrive properly.",
     "Prices":"1850","Tags":["premium"],"Sort":30},
    {"Section":"sotbap","Ko":"소고기솥밥","Rom":"So-gogi Sotbap","En":"Beef Claypot Rice",
     "Description":"Marinated beef resting on rice inside a sealed claypot — the steam does the work, and the flavour from the beef soaks down through every grain.",
     "Prices":"1350","Sort":40},
    {"Section":"sotbap","Ko":"닭구이솥밥","Rom":"Dak Gui Sotbap","En":"Chicken Claypot Rice",
     "Description":"Chicken and shiitake mushrooms cooked with rice in a sealed claypot until the base forms a golden crust. Cracked open at the table.",
     "Prices":"1050","Sort":50},

    # ── BEVERAGES ─────────────────────────────────────────────────────────────
    {"Section":"beverages","Ko":"시나몬 블루","Rom":"Cinnamon Blue","En":"Cinnamon Blue",
     "Description":"Blue pea tea infused with cinnamon and ginger, lifted with fresh lemon — gently spiced, citrus-bright, and cooling.",
     "Prices":"520","Tags":["veg"],"Sort":10},
    {"Section":"beverages","Ko":"생과일주스","Rom":"Fresh Juice","En":"Fresh Juice",
     "Description":"Freshly pressed to order — orange, watermelon, or pineapple.",
     "Prices":"520","Tags":["veg"],"Sort":20},
    {"Section":"beverages","Ko":"파인애플 아이스티","Rom":"Pineapple Iced Tea","En":"Pineapple Iced Tea",
     "Description":"Chilled tea blended with ripe pineapple and a squeeze of lemon — clean tropical sweetness with a bright finish.",
     "Prices":"450","Tags":["veg"],"Sort":30},
    {"Section":"beverages","Ko":"허니그라스 민트","Rom":"Honeygrass Mint","En":"Honeygrass Mint",
     "Description":"Sparkling lemongrass soda softened with honey and fresh mint — light, aromatic, effortlessly refreshing.",
     "Prices":"470","Tags":["veg"],"Sort":40},
    {"Section":"beverages","Ko":"라임 수박","Rom":"Lime Watermelon","En":"Lime Watermelon",
     "Description":"Cold watermelon juice sharpened with fresh lime — bright, clean, and lightly sweet.",
     "Prices":"420","Tags":["veg"],"Sort":50},
    {"Section":"beverages","Ko":"소프트 드링크","Rom":"Soft Drinks","En":"Soft Drinks",
     "Description":"A selection of imported soft drinks.",
     "Prices":"300","Sort":60},

    # ── DESSERT ───────────────────────────────────────────────────────────────
    {"Section":"dessert","En":"Dark Harmony",
     "Description":"A fudgy chocolate cake base beneath a layer of rich, dark ganache — deep, unhurried, and entirely its own thing. The only way to end a meal like this.",
     "Prices":"550","Tags":["veg","sig"],"Sort":10},
]

BBQ_CUTS = [
    # Premium
    {"Ko":"와규 A5 립아이",   "En":"Wagyu A5 Ribeye",                      "Tier":"premium","Price":8800,"Highlight":True},
    {"Ko":"앵거스 양념갈비",  "En":"Angus Short Rib (Marinated)",           "Tier":"premium","Price":7500},
    {"Ko":"앵거스 LA갈비",    "En":"Angus LA Galbi — Marinated Short Ribs", "Tier":"premium","Price":6400},
    {"Ko":"앵거스 립아이",    "En":"Angus Beef Rib Eye",                    "Tier":"premium","Price":5800},
    {"Ko":"무뼈 프라임 우육", "En":"Boneless Prime Beef (Marinated)",       "Tier":"premium","Price":4800},
    {"Ko":"와규 차돌박이",    "En":"Beef Brisket (Wagyu)",                  "Tier":"premium","Price":4400},
    # Regular
    {"Ko":"양념안심", "En":"Tenderloin (Marinated)",          "Tier":"regular","Price":3450},
    {"Ko":"립아이",   "En":"Rib Eye",                         "Tier":"regular","Price":3350},
    {"Ko":"안심",     "En":"Tenderloin",                      "Tier":"regular","Price":3150},
    {"Ko":"양념갈비", "En":"Short Rib (Marinated)",           "Tier":"regular","Price":2950},
    {"Ko":"LA갈비",   "En":"LA Galbi — Marinated Short Ribs", "Tier":"regular","Price":2850},
    # Duck
    {"Ko":"훈제오리 프리미엄", "En":"Smoked Duck — Premium", "Tier":"duck","Price":3350},
    {"Ko":"훈제오리",          "En":"Smoked Duck — Regular", "Tier":"duck","Price":2600},
]

BBQ_ASSORTMENTS = [
    {"Name":"Assortment I",
     "Items":"Regular Ribeye\nRegular Short Ribs\nRegular LA Galbi\nPremium Wagyu Brisket",
     "Price":13100,"Sort":10},
    {"Name":"Assortment II",
     "Items":"Premium Angus Ribeye\nRegular LA Galbi\nRegular Tenderloin\nPremium Wagyu Brisket",
     "Price":15200,"Sort":20},
    {"Name":"Assortment III",
     "Items":"Premium A5 Wagyu Ribeye\nPremium Angus LA Galbi\nRegular Tenderloin\nPremium Angus Brisket",
     "Price":21600,"Highlight":True,"Sort":30},
]

TASTING = [
    {
        "Title": "Seven Course",
        "Description": "Seven courses that move from bright to deep — a complete journey through SOL's kitchen. No pre-order required.",
        "Courses": (
            "게 새우 샐러드 · Crab Prawn Salad\n"
            "꿀새우볼 · Honey Shrimp Ball\n"
            "소꼬리탕 · Oxtail Soup\n"
            "매운소불고기 · Spicy Beef Bulgogi\n"
            "안동찜닭 · Braised Chicken with Glass Noodles\n"
            "버섯강정 · Sweet Crispy Mushrooms\n"
            "비빔냉면 · Spicy Cold Buckwheat Noodles"
        ),
        "Price": 9700,
        "Sort": 10,
    },
    {
        "Title": "Nine Course",
        "Description": "The complete SOL experience — nine courses built from bright starters through the depth of the grill. Includes premium tableside BBQ cuts. For those who want to stay a while.",
        "Courses": (
            "호두 샐러드 · Walnut Salad\n"
            "모자이크 김밥 · Mosaic Kimbap\n"
            "마라튀김만두 · Prawn Fried Dumplings\n"
            "소꼬리탕 · Oxtail Soup\n"
            "앵거스 브리스켓 · Premium Wagyu Brisket — table BBQ\n"
            "훈제오리 · Smoked Duck — table BBQ\n"
            "닭개장 · Spicy Chicken Soup\n"
            "매운소불고기 · Spicy Beef Bulgogi\n"
            "말차 콩국수 · Matcha Soymilk Cold Noodles"
        ),
        "Price": 15800,
        "Sort": 20,
    },
]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("SOL Menu — Airtable Seed")
    print("=" * 44)

    total = 0
    total += create_records("Meta",            META)
    total += create_records("Menu Items",      ITEMS)
    total += create_records("BBQ Cuts",        BBQ_CUTS)
    total += create_records("BBQ Assortments", BBQ_ASSORTMENTS)
    total += create_records("Tasting",         TASTING)

    print()
    print("Done — " + str(total) + " records created across 5 tables.")
    print("Photos table left empty. Add dish image URLs there whenever ready.")
    print()
    print("Next step: run  py build.py  to generate SOL_v3_built.html")


if __name__ == "__main__":
    main()
