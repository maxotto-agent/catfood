"""Build foods.json for cats from raw/*.json. Dry: kcal/cup + kcal/kg. Wet: kcal/can + kcal/kg (can grams derived)."""
import json, re, html
from collections import Counter
out = []; seen = set()
def num(x): return int(str(x).replace(',', '')) if x else None
def add(brand, name, kind, kg, cup, can, url, date):
    name = re.sub(r'\s+', ' ', html.unescape(name)).strip()
    if not kg or not (700 <= kg <= 5200): return
    if kind == 'dry' and not (150 <= (cup or 0) <= 600): return
    if kind == 'wet':
        if not can: return
        g = can / kg * 1000
        if not (40 <= g <= 450): return   # can sizes 1.2 oz to 15 oz
    k = (brand, name.lower(), kind, kg)
    if k in seen: return
    seen.add(k)
    out.append(dict(brand=brand, name=name, kind=kind, kcal_kg=kg, kcal_cup=cup if kind == 'dry' else None,
                    kcal_can=can if kind == 'wet' else None, url=url, checked='2026-10-21'))
for r in json.load(open('raw/hills-cat.json')):
    if r.get('err') or re.search(r'treat|starter-kit|sample-pack', r['url'] + r['name'], re.I): continue
    kg, cup, can = num(r['kg']), num(r['cup']), num(r['can'])
    n = r['name'].replace('&#43;', '+').replace('&amp;', '&')
    line = 'Prescription Diet' if re.search(r'/prescription|/pd-', r['url']) else 'Science Diet'
    if cup and kg: add("Hill's", f'{line} {n}', 'dry', kg, cup, None, r['url'], '')
    elif can and kg: add("Hill's", f'{line} {n}', 'wet', kg, None, can, r['url'], '')
for r in json.load(open('raw/bb-cat.json')):
    kg, cup, can = num(r['kg']), num(r['cup']), num(r['can'])
    slug = r['url'].rstrip('/').split('/')[-1].replace('-', ' ').title()
    line = r['url'].rstrip('/').split('/')[-2].replace('-', ' ').title()
    if '/dry-cat-food/' in r['url'] and cup and kg: add('Blue Buffalo', f'BLUE {line}: {slug}', 'dry', kg, cup, None, r['url'], '')
    elif '/wet-cat-food/' in r['url'] and can and kg: add('Blue Buffalo', f'BLUE {line}: {slug}', 'wet', kg, None, can, r['url'], '')
for r in json.load(open('raw/merrick-cat.json')):
    if re.search(r'treat|topper|variety', r['name'], re.I): continue
    m = re.findall(r'([\d,]+)\s*kcal/(kg|cup|can)', r['cal'])
    v = {u: float(x.replace(',', '')) for x, u in m}
    n = re.sub(r'\s*\|.*$', '', r['name']).replace('Purrfect Bistro ', '').strip()
    if 'cup' in v and 'kg' in v: add('Merrick', f'Purrfect Bistro {n}', 'dry', v['kg'], v['cup'], None, r['url'], '')
    elif 'can' in v and 'kg' in v: add('Merrick', f'Purrfect Bistro {n}', 'wet', v['kg'], None, v['can'], r['url'], '')
# drop dry formulas whose implied grams per cup is implausible (70-150 g): likely a page error
out = [r for r in out if not (r['kind']=='dry' and r['kcal_kg'] and not 70 <= 1000*r['kcal_cup']/r['kcal_kg'] <= 150)]
for r in out:
    for k in ('kcal_kg','kcal_cup','kcal_can'):
        if r[k] is not None: r[k] = int(round(r[k]))
out.sort(key=lambda r: (r['brand'], r['kind'], r['name']))
json.dump(out, open('foods.json', 'w'), separators=(',', ':'), ensure_ascii=False)
print(len(out), Counter((r['brand'], r['kind']) for r in out))
