"""Generate brand pages, per-formula pages and sitemap.xml for cat food from foods.json."""
import json, html, re, statistics, os
BASE = "https://maxotto-agent.github.io/catfood/"
foods = json.load(open("foods.json"))
FOOT = "This application was autonomously scaffolded and deployed using generative software agents. Designed for lightweight, single-purpose utility. Curated and maintained by @maxim-k."
CSS = open("index.html").read().split("<style>")[1].split("</style>")[0]
CSS += "table{margin-top:.5rem}td.n,th.n{text-align:right;white-space:nowrap}"
slug = lambda b: re.sub(r"[^a-z0-9]+", "-", b.lower()).strip("-")
e = html.escape
ku = lambda f: f["kcal_can"] if f["kind"] == "wet" else f["kcal_cup"]
unit = lambda f: "can" if f["kind"] == "wet" else "cup"
brands = {}
for f in foods:
    brands.setdefault(f["brand"], []).append(f)

def page(title, desc, path, body):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{BASE}{path}">
<style>{CSS}</style>
</head>
<body>
<main>
{body}
<footer>{FOOT}</footer>
</main>
</body>
</html>
"""

os.makedirs("brands", exist_ok=True); os.makedirs("formulas", exist_ok=True)
urls = [""]
for b, fs in sorted(brands.items()):
    fs = sorted(fs, key=lambda f: (f["kind"], f["name"]))
    dates = sorted({f["checked"] for f in fs})
    parts = []
    for kind, label in (("dry", "dry (per cup)"), ("wet", "wet (per can)")):
        k = [f for f in fs if f["kind"] == kind]
        if not k: continue
        v = [ku(f) for f in k]
        parts.append(f"{len(k)} {kind} formulas range from {min(v)} to {max(v)} kcal per {unit(k[0])} (median {round(statistics.median(v))})")
    rows = "\n".join(
        f'<tr><td><a href="../formulas/{slug(b+" "+f["name"]+" "+f["kind"])}.html">{e(f["name"])}</a> ({f["kind"]}; <a href="{e(f["url"])}">maker</a>)</td><td class="n">{ku(f)} /{unit(f)}</td><td class="n">{f["kcal_kg"]}</td></tr>' for f in fs)
    body = f"""<p class="sub"><a href="../">Cat food calorie calculator</a> › Brands</p>
<h1>{e(b)} cat food: calories per cup and per can, {len(fs)} formulas</h1>
<p class="lead">{e(b)}'s {'; '.join(parts)}. Formulas differ a lot, so work out the daily amount from the exact one.</p>
<p><a href="../"><b>Calculate cups or cans per day for a {e(b)} formula →</b></a></p>
<table>
<tr><th>Formula</th><th class="n">kcal</th><th class="n">kcal/kg</th></tr>
{rows}
</table>
<p class="sub">Figures are metabolizable energy as fed, copied from each formula's product page on the maker's site, checked {e(", ".join(dates))}. Makers revise formulas; check the package in your hands. Not affiliated with {e(b)}.</p>"""
    p = f"brands/{slug(b)}.html"
    open(p, "w").write(page(f"{b} cat food calories per cup and per can ({len(fs)} formulas)",
        f"Calories per cup (dry) and per can (wet) for {len(fs)} {b} cat food formulas, from the maker's product pages.", p, body))
    urls.append(p)

seen = set()
for b, fs in brands.items():
    for f in fs:
        fslug = slug(b + " " + f["name"] + " " + f["kind"])
        while fslug in seen: fslug += "-2"
        seen.add(fslug)
        same = [x for x in fs if x["kind"] == f["kind"]]
        med = round(statistics.median([ku(x) for x in same]))
        kc, u = ku(f), unit(f)
        diff = kc - med
        cmp_ = f"{abs(diff)} kcal per {u} {'above' if diff > 0 else 'below'} the {e(b)} {f['kind']} median of {med}" if diff else f"equal to the {e(b)} {f['kind']} median of {med}"
        g = round(1000 * f["kcal_can"] / f["kcal_kg"]) if f["kind"] == "wet" else round(1000 * f["kcal_cup"] / f["kcal_kg"])
        gtxt = f" A can holds about {g} g ({g/28.35:.1f} oz)." if f["kind"] == "wet" else f" A cup weighs about {g} g."
        wrows = ""
        for kg in (3, 4, 5, 6):
            kcal = 1.2 * 70 * kg ** 0.75
            wrows += f'<tr><td class="n">{kg} kg ({round(kg*2.2046)} lb)</td><td class="n">{round(kcal)}</td><td class="n">{kcal/kc:.2f}</td></tr>'
        body = f"""<p class="sub"><a href="../">Cat food calorie calculator</a> › <a href="../brands/{slug(b)}.html">{e(b)}</a> › Formula</p>
<h1>{e(b)} {e(f["name"])}: calories per {u}</h1>
<p class="lead">{e(b)} {e(f["name"])} ({f["kind"]} cat food) has {kc} kcal per {u}, {f["kcal_kg"]} kcal per kg, according to the maker's product page. That is {cmp_}.{gtxt}</p>
<p><a href="../"><b>Work out {u}s per day for your cat →</b></a></p>
<h2>Rough daily amount, neutered adult cat at a healthy weight</h2>
<table>
<tr><th class="n">Cat weight</th><th class="n">kcal/day</th><th class="n">{u.capitalize()}s/day</th></tr>
{wrows}
</table>
<p class="sub">Estimate: resting energy 70 × kg^0.75 times 1.2 (neutered adult factor, <a href="https://www.merckvetmanual.com/multimedia/table/daily-maintenance-energy-requirements-for-dogs-and-cats">Merck Veterinary Manual</a>). Kittens, intact, overweight or sick cats differ; ask your vet. Figure copied from <a href="{e(f["url"])}">the maker's page</a>, checked {e(f["checked"])}. Makers revise formulas; check the package in your hands. Not affiliated with {e(b)}.</p>"""
        p = f"formulas/{fslug}.html"
        open(p, "w").write(page(f"{b} {f['name']} calories per {u} ({kc} kcal)",
            f"{b} {f['name']} {f['kind']} cat food: {kc} kcal per {u}, {f['kcal_kg']} kcal per kg. Daily amount by cat weight.", p, body))
        urls.append(p)

open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"<url><loc>{BASE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
open("robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
print({b: len(f) for b, f in brands.items()}, len(urls))
