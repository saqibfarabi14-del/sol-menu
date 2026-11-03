#!/usr/bin/env node
/*
 SOL — SEO page generator
 ─────────────────────────
 Reads the live menu data baked into index.html (SOL_DATA, GROUPS, ITEMS, BBQ, SIG)
 and writes crawlable static pages:
   menu/index.html             → https://soldhaka.com/menu/
   korean-bbq-dhaka/index.html → https://soldhaka.com/korean-bbq-dhaka/
 plus sitemap.xml.

 Re-run after any menu or price change in index.html:
   node tools/seo-pages.js
*/
var fs = require('fs');
var path = require('path');

var ROOT = path.join(__dirname, '..');
var SITE = 'https://soldhaka.com';
var html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');

// ── extract a JS literal assigned to `const NAME` ───────────────────────────
function grab(name) {
  var i = html.indexOf('const ' + name);
  if (i < 0) throw new Error('missing const ' + name);
  var j = html.indexOf('=', i) + 1;
  while (html[j] === ' ' || html[j] === '\n') j++;
  var open = html[j], close = open === '[' ? ']' : '}';
  var d = 0, k = j, s = null;
  for (; k < html.length; k++) {
    var c = html[k];
    if (s) { if (c === '\\') { k++; continue; } if (c === s) s = null; continue; }
    if (c === '"' || c === "'" || c === '`') { s = c; continue; }
    if (c === open) d++;
    else if (c === close) { d--; if (d === 0) break; }
  }
  return eval('(' + html.slice(j, k + 1) + ')');
}

var META = grab('SOL_DATA').meta;
var GROUPS = grab('GROUPS');
var ITEMS = grab('ITEMS');
var BBQ = grab('BBQ');
var SIG = grab('SIG');
var LOGO = (html.match(/class="n-logo"[^>]*><img src="(data:image\/png;base64,[^"]+)"/) || [])[1] || '/icon-192.png';

// ── content rule: SOL never references pork or alcohol ──────────────────────
var BANNED = /\b(pork|bacon|ham|lard|wine|soju|sake|beer|mirin|rum|whisk(e)?y|vodka|liquor|alcohol(ic)?|shaoxing|makgeolli|cognac|brandy|gin)\b/i;
function audit(label, text) {
  var m = String(text).match(BANNED);
  if (m) throw new Error('Content rule violation (' + m[0] + ') in ' + label);
}

// ── helpers ─────────────────────────────────────────────────────────────────
function esc(s) {
  return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
function tk(n) { return '৳' + Number(n).toLocaleString('en-US'); }
function priceText(p) {
  return p.map(function (v) { return (v.l ? esc(v.l) + ' ' : '') + tk(v.a); }).join(' · ');
}
function offers(p) {
  var o = p.map(function (v) {
    var x = { '@type': 'Offer', price: String(v.a), priceCurrency: 'BDT' };
    if (v.l) x.name = v.l;
    return x;
  });
  return o.length === 1 ? o[0] : o;
}

var sectionMeta = {};
var sectionOrder = [];
GROUPS.forEach(function (g) {
  (g.sections || []).forEach(function (s) { sectionMeta[s.id] = s; sectionOrder.push(s.id); });
});
var bySection = {};
ITEMS.forEach(function (it) { (bySection[it.s] = bySection[it.s] || []).push(it); });

var allBeef = BBQ.premium.concat(BBQ.regular);
var minBeef = Math.min.apply(null, allBeef.map(function (c) { return c.a; }));
var phone = META.phone;
var wa = 'https://wa.me/' + META.whatsapp.replace(/[^0-9]/g, '');
var hoursText = 'Open daily 1 PM–11 PM, Friday 2 PM–11 PM';
var addressText = '12th Floor, Ventura Mall, Road 103, Gulshan 2, Dhaka 1212';

var RESTAURANT_REF = {
  '@type': 'Restaurant',
  '@id': SITE + '/#restaurant',
  name: 'SOL Korean BBQ',
  url: SITE + '/',
  telephone: phone,
  servesCuisine: ['Korean', 'Korean BBQ'],
  priceRange: '৳৳৳',
  image: SITE + '/og-image.jpg',
  address: {
    '@type': 'PostalAddress',
    streetAddress: '12th Floor, Ventura Mall, Road 103',
    addressLocality: 'Gulshan 2, Dhaka',
    postalCode: '1212',
    addressCountry: 'BD'
  },
  geo: { '@type': 'GeoCoordinates', latitude: '23.7937', longitude: '90.4066' },
  openingHoursSpecification: [
    { '@type': 'OpeningHoursSpecification', dayOfWeek: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Saturday', 'Sunday'], opens: '13:00', closes: '23:00' },
    { '@type': 'OpeningHoursSpecification', dayOfWeek: ['Friday'], opens: '14:00', closes: '23:00' }
  ],
  sameAs: [META.instagram, META.facebook]
};

function breadcrumb(name, url) {
  return {
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'SOL', item: SITE + '/' },
      { '@type': 'ListItem', position: 2, name: name, item: url }
    ]
  };
}

// ── shared shell (Gilt Void) ────────────────────────────────────────────────
function page(o) {
  return '<!DOCTYPE html>\n<html lang="en">\n<head>\n' +
    '<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">\n' +
    '<title>' + esc(o.title) + '</title>\n' +
    '<meta name="description" content="' + esc(o.description) + '">\n' +
    '<link rel="canonical" href="' + o.url + '">\n' +
    '<meta name="robots" content="index, follow">\n<meta name="theme-color" content="#05060b">\n' +
    '<meta name="geo.region" content="BD-13"><meta name="geo.placename" content="Dhaka"><meta name="geo.position" content="23.7937;90.4066"><meta name="ICBM" content="23.7937, 90.4066">\n' +
    '<meta property="og:type" content="website"><meta property="og:site_name" content="SOL Restaurant">\n' +
    '<meta property="og:title" content="' + esc(o.title) + '"><meta property="og:description" content="' + esc(o.description) + '">\n' +
    '<meta property="og:url" content="' + o.url + '"><meta property="og:image" content="' + SITE + '/og-image.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">\n' +
    '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="' + SITE + '/og-image.jpg">\n' +
    '<link rel="icon" href="/favicon.ico"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/manifest.json">\n' +
    '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n' +
    '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,200;0,9..144,300;1,9..144,300&family=Inter:wght@300;400&family=Noto+Serif+KR:wght@300&display=swap" rel="stylesheet">\n' +
    '<script type="application/ld+json">' + JSON.stringify({ '@context': 'https://schema.org', '@graph': o.schema }) + '</script>\n' +
    '<script async src="https://www.googletagmanager.com/gtag/js?id=' + META.ga4 + '"></script>\n' +
    '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag(\'js\',new Date());gtag(\'config\',\'' + META.ga4 + '\');</script>\n' +
    '<style>' + CSS + '</style>\n</head>\n<body>\n' +
    '<header class="top"><a href="/" class="logo" aria-label="SOL home"><img src="' + LOGO + '" alt="SOL" width="19" height="36"></a>' +
    '<nav aria-label="Main"><a href="/menu/"' + (o.active === 'menu' ? ' aria-current="page"' : '') + '>Menu</a><a href="/korean-bbq-dhaka/"' + (o.active === 'bbq' ? ' aria-current="page"' : '') + '>Korean BBQ</a><a href="/#res" class="cta">Reserve</a></nav></header>\n' +
    '<main>\n' + o.body + '\n</main>\n' +
    '<footer><div class="rule"></div>' +
    '<p class="addr">' + esc(addressText) + '</p>' +
    '<p class="hrs">' + esc(hoursText) + '</p>' +
    '<p class="links"><a href="tel:' + phone + '">' + esc(phone) + '</a><a href="' + wa + '" rel="noopener">WhatsApp</a><a href="' + META.instagram + '" rel="noopener">Instagram</a><a href="' + META.facebook + '" rel="noopener">Facebook</a></p>' +
    '<p class="links"><a href="/">Home</a><a href="/menu/">Menu</a><a href="/korean-bbq-dhaka/">Korean BBQ</a><a href="/#res">Reserve</a></p>' +
    '<p class="copy">© ' + new Date().getFullYear() + ' SOL · Korean BBQ · Ventura Mall, Gulshan 2, Dhaka</p></footer>\n' +
    '</body>\n</html>\n';
}

var CSS = [
  ':root{--ink:#05060b;--inks:#090b12;--inkm:#0d1018;--cream:#f0e6d3;--mute:rgba(240,230,211,.62);--brass:#b89558;--blt:#d1b077;--line:rgba(184,149,88,.22)}',
  '*{box-sizing:border-box;margin:0;padding:0}',
  'html{background:var(--ink);-webkit-text-size-adjust:100%}',
  'body{background:var(--ink);color:var(--cream);font:300 15px/1.65 Inter,system-ui,sans-serif;letter-spacing:.01em}',
  'a{color:var(--blt);text-decoration:none}a:hover{color:var(--cream)}',
  '.top{position:sticky;top:0;z-index:5;display:flex;align-items:center;justify-content:space-between;padding:14px 16px;background:rgba(5,6,11,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}',
  '.logo img{height:36px;width:auto;display:block;opacity:.9}',
  '.top nav{display:flex;gap:18px;align-items:center;font-size:11px;letter-spacing:.22em;text-transform:uppercase}',
  '.top nav a{color:var(--mute)}.top nav a[aria-current]{color:var(--blt)}',
  '.top .cta{color:var(--ink);background:var(--brass);padding:8px 14px}.top .cta:hover{background:var(--blt);color:var(--ink)}',
  'main{max-width:760px;margin:0 auto;padding:56px 16px 40px}',
  '.eyebrow{font:300 11px/1 Inter,sans-serif;letter-spacing:.32em;text-transform:uppercase;color:var(--brass);margin-bottom:18px}',
  'h1{font:200 clamp(32px,7vw,52px)/1.1 Fraunces,Georgia,serif;margin-bottom:20px}',
  'h2{font:300 clamp(24px,5vw,32px)/1.2 Fraunces,Georgia,serif;margin:64px 0 6px}',
  'h3{font:300 18px/1.35 Fraunces,Georgia,serif;margin-bottom:4px}',
  '.ko{font-family:"Noto Serif KR",serif;color:var(--brass);font-weight:300}',
  'h2 .ko{display:block;font-size:13px;letter-spacing:.2em;margin-bottom:8px}',
  '.lede{color:var(--mute);font-size:16px;max-width:60ch}',
  '.sub{color:var(--mute);font-size:13px;margin-bottom:22px}',
  'p+p{margin-top:14px}',
  '.toc{display:flex;flex-wrap:wrap;gap:8px 16px;margin:32px 0 8px;padding:18px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);font-size:12px;letter-spacing:.12em;text-transform:uppercase}',
  '.toc a{color:var(--mute)}',
  '.items{list-style:none;border-top:1px solid var(--line)}',
  '.items li{padding:18px 0;border-bottom:1px solid var(--line);display:grid;grid-template-columns:1fr auto;gap:4px 16px}',
  '.items .d{grid-column:1/-1;color:var(--mute);font-size:14px}',
  '.items .pr{color:var(--blt);white-space:nowrap;font-size:14px;text-align:right}',
  '.items .ko{font-size:13px;margin-right:8px}',
  '.mark{display:inline-block;font-size:9px;letter-spacing:.2em;text-transform:uppercase;color:var(--brass);border:1px solid var(--line);padding:2px 6px;margin-left:8px;vertical-align:middle}',
  '.course{list-style:none;counter-reset:c;margin-top:10px}.course li{counter-increment:c;padding:6px 0;color:var(--mute)}.course li:before{content:counter(c,upper-roman) "  ";color:var(--brass);font-size:12px;letter-spacing:.1em}',
  '.box{border:1px solid var(--line);padding:22px;margin-top:22px;background:var(--inks)}',
  '.btns{display:flex;flex-wrap:wrap;gap:12px;margin-top:26px}',
  '.btn{border:1px solid var(--brass);color:var(--cream);padding:12px 20px;font-size:11px;letter-spacing:.22em;text-transform:uppercase}.btn.p{background:var(--brass);color:var(--ink)}.btn:hover{background:var(--blt);color:var(--ink)}',
  'dl dt{font:300 18px/1.35 Fraunces,Georgia,serif;margin-top:26px}dl dd{color:var(--mute);margin-top:6px}',
  'footer{text-align:center;padding:40px 16px 56px;color:var(--mute);font-size:12px;letter-spacing:.06em}',
  'footer .rule{width:40px;height:1px;background:var(--brass);margin:0 auto 22px}',
  'footer p{margin-top:8px}footer .links a{margin:0 9px;display:inline-block}footer .copy{margin-top:20px;opacity:.6}',
  '@media (max-width:420px){.top nav{gap:12px;letter-spacing:.14em}.top .cta{padding:7px 10px}}',
  '@media print{.top,footer,.btns,.toc{display:none}body,html{background:#fff;color:#000}.items .d,.lede,.sub{color:#333}}'
].join('');

// ── /menu/ ──────────────────────────────────────────────────────────────────
function itemLi(it) {
  audit(it.en, JSON.stringify(it));
  var marks = '';
  if ((it.t || []).indexOf('sig') >= 0) marks += '<span class="mark">Signature</span>';
  if ((it.t || []).indexOf('spicy') >= 0) marks += '<span class="mark">Spicy</span>';
  return '<li><h3><span class="ko" lang="ko">' + esc(it.ko) + '</span>' + esc(it.en) + marks + '</h3>' +
    '<span class="pr">' + priceText(it.p) + '</span>' +
    (it.d ? '<p class="d">' + esc(it.d) + '</p>' : '') + '</li>';
}
function cutLi(c) {
  audit(c.en, JSON.stringify(c));
  return '<li><h3><span class="ko" lang="ko">' + esc(c.ko) + '</span>' + esc(c.en) + '</h3><span class="pr">' + tk(c.a) + '</span></li>';
}
function assortLi(a) {
  audit(a.name, JSON.stringify(a));
  return '<li><h3>' + esc(a.name) + '</h3><span class="pr">' + tk(a.a) + '</span><p class="d">' + a.items.map(esc).join(' · ') + '</p></li>';
}

var menuSectionsSchema = [];
var menuBody = [];
var toc = ['<a href="#bbq">Korean BBQ</a>', '<a href="#chefs-path">Chef’s Path</a>'];

menuBody.push('<p class="eyebrow">SOL · Gulshan 2, Dhaka</p>');
menuBody.push('<h1>The SOL Menu</h1>');
menuBody.push('<p class="lede">Korean BBQ grilled over real charcoal at your table, the Chef’s Path tasting courses, and ' + ITEMS.length +
  ' dishes from across the Korean kitchen — dumplings, kimbap, soups, hotpot, claypot rice, sashimi and nigiri. ' +
  'On the 12th floor of Ventura Mall, Gulshan 2. Prices in Bangladeshi Taka and subject to change.</p>');

// BBQ
var bbqHtml = '<section id="bbq"><h2><span class="ko" lang="ko">한국식 바베큐</span>Korean BBQ</h2><p class="sub">Grilled tableside over charcoal. <a href="/korean-bbq-dhaka/">About our Korean BBQ →</a></p>' +
  '<h3 style="margin-top:26px">Premium Cuts</h3><ul class="items">' + BBQ.premium.map(cutLi).join('') + '</ul>' +
  '<h3 style="margin-top:30px">Regular Cuts</h3><ul class="items">' + BBQ.regular.map(cutLi).join('') + '</ul>' +
  (BBQ.duck && BBQ.duck.length ? '<h3 style="margin-top:30px">Smoked Duck</h3><ul class="items">' + BBQ.duck.map(cutLi).join('') + '</ul>' : '') +
  (BBQ.assortments && BBQ.assortments.length ? '<h3 style="margin-top:30px">Assortments</h3><ul class="items">' + BBQ.assortments.map(assortLi).join('') + '</ul>' : '') +
  '</section>';
menuBody.push('<div class="toc" aria-label="Menu sections">__TOC__</div>');
menuBody.push(bbqHtml);
menuSectionsSchema.push({
  '@type': 'MenuSection', name: 'Korean BBQ',
  hasMenuItem: BBQ.premium.concat(BBQ.regular, BBQ.duck || []).map(function (c) {
    return { '@type': 'MenuItem', name: c.en, alternateName: c.ko, offers: offers([{ a: c.a }]) };
  }).concat((BBQ.assortments || []).map(function (a) {
    return { '@type': 'MenuItem', name: 'BBQ ' + a.name, description: a.items.join(', '), offers: offers([{ a: a.a }]) };
  }))
});

// Chef's Path
var sigHtml = '<section id="chefs-path"><h2><span class="ko" lang="ko">시그니처</span>Chef’s Path</h2><p class="sub">Tasting courses through SOL’s kitchen.</p>';
SIG.forEach(function (s) {
  audit(s.t, JSON.stringify(s));
  sigHtml += '<div class="box"><h3>' + esc(s.t) + (s.p ? ' <span class="pr" style="float:right;color:var(--blt);font-size:14px">' + tk(s.p) + ' per person</span>' : '') + '</h3>' +
    (s.d ? '<p class="d" style="color:var(--mute);font-size:14px;margin-top:6px">' + esc(s.d) + '</p>' : '') +
    '<ol class="course">' + (s.items || []).map(function (c) { return '<li><span class="ko" lang="ko">' + esc(c.ko) + '</span> ' + esc(c.en) + '</li>'; }).join('') + '</ol></div>';
});
sigHtml += '</section>';
menuBody.push(sigHtml);
menuSectionsSchema.push({
  '@type': 'MenuSection', name: 'Chef’s Path',
  hasMenuItem: SIG.map(function (s) {
    var mi = { '@type': 'MenuItem', name: 'Chef’s Path — ' + s.t, description: s.d || '' };
    if (s.p) mi.offers = offers([{ a: s.p }]);
    return mi;
  })
});

// à la carte sections in the homepage's order
sectionOrder.forEach(function (id) {
  var list = bySection[id];
  if (!list || !list.length) return;
  var m = sectionMeta[id] || { label: id };
  var name = m.label + (m.sub ? ' — ' + m.sub : '');
  toc.push('<a href="#' + id + '">' + esc(m.label) + '</a>');
  menuBody.push('<section id="' + id + '"><h2><span class="ko" lang="ko">' + esc(m.ko || '') + '</span>' + esc(name) + '</h2>' +
    '<ul class="items">' + list.map(itemLi).join('') + '</ul></section>');
  menuSectionsSchema.push({
    '@type': 'MenuSection', name: name,
    hasMenuItem: list.map(function (it) {
      return { '@type': 'MenuItem', name: it.en, alternateName: it.ko + (it.rom ? ' (' + it.rom + ')' : ''), description: it.d || undefined, offers: offers(it.p) };
    })
  });
});
// any section not in GROUPS (safety)
Object.keys(bySection).forEach(function (id) {
  if (sectionOrder.indexOf(id) < 0) console.warn('WARN: section not in GROUPS, skipped: ' + id);
});

menuBody.push('<div class="btns"><a class="btn p" href="/#res">Reserve a table</a><a class="btn" href="tel:' + phone + '">Call ' + esc(phone) + '</a></div>');

var menuUrl = SITE + '/menu/';
var menuHtml = page({
  title: 'SOL Menu | Korean BBQ, Wagyu & Korean Dishes — Gulshan 2, Dhaka',
  description: 'Full menu of SOL Korean BBQ, Gulshan 2, Dhaka: charcoal-grilled Wagyu A5 and LA Galbi, Chef’s Path tasting courses, mandu, kimbap, bibimbap, hotpot, sashimi and more. Prices in BDT.',
  url: menuUrl,
  active: 'menu',
  schema: [
    RESTAURANT_REF,
    { '@type': 'Menu', '@id': menuUrl + '#menu', name: 'SOL Menu', url: menuUrl, inLanguage: 'en', hasMenuSection: menuSectionsSchema },
    breadcrumb('Menu', menuUrl)
  ],
  body: menuBody.join('\n').replace('__TOC__', toc.join(''))
});

// ── /korean-bbq-dhaka/ ──────────────────────────────────────────────────────
var bbqUrl = SITE + '/korean-bbq-dhaka/';
var faqs = [
  ['Where is SOL Korean BBQ in Dhaka?', 'SOL is on the 12th floor of Ventura Mall, Road 103, Gulshan 2, Dhaka 1212.'],
  ['What are SOL’s opening hours?', 'SOL is open daily from 1 PM to 11 PM, and from 2 PM to 11 PM on Fridays.'],
  ['Is the BBQ grilled at the table?', 'Yes. Every cut is grilled tableside over real charcoal, and our servers guide the order and the grill.'],
  ['What cuts are on the Korean BBQ menu?', 'Premium cuts include ' + BBQ.premium.map(function (c) { return c.en.split(' — ')[0]; }).join(', ') +
    '. Regular cuts include ' + BBQ.regular.map(function (c) { return c.en.split(' — ')[0]; }).join(', ') + '.'],
  ['How much does Korean BBQ cost at SOL?', 'Beef cuts start from ' + tk(minBeef) + ', and Wagyu A5 Ribeye is ' + tk(BBQ.premium[0].a) +
    '. Assortments for sharing start from ' + tk(Math.min.apply(null, BBQ.assortments.map(function (a) { return a.a; }))) + '.'],
  ['How do I reserve a table?', 'Call or WhatsApp ' + phone + ', or use the reservation form on soldhaka.com.']
];
faqs.forEach(function (f) { audit('faq', f.join(' ')); });

var bbqBody = [
  '<p class="eyebrow">참숯 · 직화 · Gulshan 2</p>',
  '<h1>Korean BBQ in Dhaka, grilled over real charcoal</h1>',
  '<p class="lede">At SOL, Korean BBQ is cooked at your table over live charcoal — Wagyu A5 ribeye, marinated LA galbi, tenderloin and wagyu brisket, ' +
  'grilled in front of you and eaten the moment it comes off the fire. On the 12th floor of Ventura Mall, Gulshan 2.</p>',
  '<div class="btns"><a class="btn p" href="/#res">Reserve a table</a><a class="btn" href="' + wa + '" rel="noopener">WhatsApp</a></div>',

  '<h2><span class="ko" lang="ko">참숯</span>Why charcoal</h2>',
  '<p>Charcoal burns hotter and drier than gas. The surface of the meat sears fast and takes on a light smoke, while the inside stays tender. ' +
  'Marinated cuts like galbi caramelise at the edges instead of steaming. It is the way Korean BBQ is done in Seoul, and the way we do it here.</p>',

  '<h2><span class="ko" lang="ko">프리미엄</span>Premium cuts</h2>',
  '<ul class="items">' + BBQ.premium.map(cutLi).join('') + '</ul>',
  '<h2><span class="ko" lang="ko">레귤러</span>Regular cuts</h2>',
  '<ul class="items">' + BBQ.regular.map(cutLi).join('') + '</ul>',
  (BBQ.duck && BBQ.duck.length ? '<h2><span class="ko" lang="ko">훈제오리</span>Smoked duck</h2><ul class="items">' + BBQ.duck.map(cutLi).join('') + '</ul>' : ''),
  '<h2><span class="ko" lang="ko">모둠</span>Assortments to share</h2>',
  '<p class="sub">Four cuts on one board — the easiest way to order for a table.</p>',
  '<ul class="items">' + BBQ.assortments.map(assortLi).join('') + '</ul>',

  '<h2><span class="ko" lang="ko">시그니처</span>Beyond the grill</h2>',
  '<p>Pair the BBQ with dishes from the kitchen — soups and stews, dumplings, claypot rice, sashimi — or let the Chef’s Path tasting courses take you through the whole menu. ' +
  '<a href="/menu/">See the full menu →</a></p>',

  '<h2><span class="ko" lang="ko">자주 묻는 질문</span>Questions</h2>',
  '<dl>' + faqs.map(function (f) { return '<dt>' + esc(f[0]) + '</dt><dd>' + esc(f[1]) + '</dd>'; }).join('') + '</dl>',

  '<div class="box"><h3>Visit SOL</h3><p class="d" style="color:var(--mute);margin-top:6px">' + esc(addressText) + '<br>' + esc(hoursText) + '</p>' +
  '<div class="btns" style="margin-top:16px"><a class="btn p" href="/#res">Reserve</a><a class="btn" href="tel:' + phone + '">Call</a>' +
  '<a class="btn" href="https://www.google.com/maps/search/?api=1&amp;query=23.7937,90.4066" rel="noopener">Directions</a></div></div>',
  '<p class="sub" style="margin-top:28px">As featured in <a href="https://www.tbsnews.net/features/habitat/bangladeshi-craft-meets-korean-design-sol-restaurant-1326946" rel="noopener">The Business Standard</a>.</p>'
].join('\n');
audit('bbq page copy', bbqBody.replace(/<[^>]+>/g, ' '));

var bbqHtml2 = page({
  title: 'Korean BBQ in Dhaka | Charcoal-Grilled Wagyu at SOL, Gulshan 2',
  description: 'Korean BBQ grilled tableside over real charcoal at SOL, Ventura Mall, Gulshan 2, Dhaka. Wagyu A5 ribeye, LA galbi, tenderloin and sharing assortments. Open daily.',
  url: bbqUrl,
  active: 'bbq',
  schema: [
    RESTAURANT_REF,
    { '@type': 'WebPage', '@id': bbqUrl, url: bbqUrl, name: 'Korean BBQ in Dhaka — SOL', about: { '@id': SITE + '/#restaurant' } },
    { '@type': 'FAQPage', mainEntity: faqs.map(function (f) { return { '@type': 'Question', name: f[0], acceptedAnswer: { '@type': 'Answer', text: f[1] } }; }) },
    breadcrumb('Korean BBQ in Dhaka', bbqUrl)
  ],
  body: bbqBody
});

// ── write ───────────────────────────────────────────────────────────────────
function write(rel, content) {
  var p = path.join(ROOT, rel);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, content);
  console.log('wrote ' + rel + ' (' + Math.round(content.length / 1024) + ' KB)');
}
write('menu/index.html', menuHtml);
write('korean-bbq-dhaka/index.html', bbqHtml2);

var today = new Date().toISOString().slice(0, 10);
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
  [[SITE + '/', '1.0'], [menuUrl, '0.9'], [bbqUrl, '0.9']].map(function (u) {
    return '  <url>\n    <loc>' + u[0] + '</loc>\n    <lastmod>' + today + '</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>' + u[1] + '</priority>\n  </url>';
  }).join('\n') + '\n</urlset>\n');
