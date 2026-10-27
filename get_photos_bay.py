#!/usr/bin/env python3
"""Find a CC-licensed landscape photo per spot on Wikimedia Commons, download a 560px thumb to img/<id>.jpg,
and write img/credits.json. Prefers landscape orientation and Oregon-specific titles."""
import json, os, re, sys, time, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img"); os.makedirs(IMG, exist_ok=True)
UA = {"User-Agent": "WindwardMark/1.0 (kite spot app; 1mikestone@gmail.com)"}
QUERIES = {
  "paradisecay": ["Tiburon Belvedere Richardson Bay sailboats", "Raccoon Strait Tiburon", "Angel Island from Tiburon water", "Tiburon waterfront San Francisco Bay"],
  "coyote": ["Coyote Point San Mateo bay", "Coyote Point Recreation Area", "Coyote Point Park San Mateo"],
  "sherman": ["Antioch Bridge San Joaquin River", "Sacramento River Delta levee water", "San Joaquin River Antioch", "Sacramento River near Rio Vista"],
  "windycove": ["Rio Vista California Sacramento River", "Sacramento River Delta Rio Vista", "Rio Vista California"],
  "baypoint": ["Suisun Bay mothball fleet ships", "Carquinez Strait water", "Benicia waterfront Carquinez", "Suisun Bay from Benicia"],
  "stinson": ["Stinson Beach sand ocean waves", "Stinson Beach aerial", "Bolinas Bay Stinson Beach", "Stinson Beach surf"],
  "bodega": ["Doran Beach Bodega Bay", "Bodega Bay California beach", "Bodega Head"],
  "waddell": ["Waddell Beach California", "Waddell Creek Beach Santa Cruz", "Big Basin Waddell Beach"],
  "hmb": ["Half Moon Bay State Beach", "Half Moon Bay California beach", "Francis Beach Half Moon Bay"],
  "oceanbeach": ["Ocean Beach San Francisco", "Ocean Beach San Francisco surf", "Great Highway Ocean Beach"],
  "davenport": ["Davenport California beach", "Davenport Landing Beach", "Davenport Santa Cruz County coast"],
  "tollplaza": ["Emeryville Crescent", "Bay Bridge toll plaza Oakland bay", "Emeryville shoreline San Francisco Bay", "Eastshore State Park"],
  "racetrack": ["Golden Gate Fields Albany", "Albany Bulb shoreline", "Albany Beach California", "Albany California waterfront"],
  "pointemery": ["Point Emery Emeryville", "Emeryville Marina San Francisco Bay", "Emeryville California shoreline"],
  "dillon": ["Dillon Beach sand ocean", "Tomales Point Dillon Beach", "Tomales Bay mouth", "Dillon Beach surf waves"],
  "gazos": ["Gazos Creek State Beach", "Gazos Creek beach San Mateo County", "Pigeon Point Lighthouse"],
  "pillarpoint": ["Pillar Point Harbor Half Moon Bay", "Pillar Point Harbor", "Mavericks Pillar Point"],
  "kingsbeach": ["Lake Tahoe north shore beach sand", "Kings Beach pier Lake Tahoe", "Lake Tahoe Tahoe Vista beach", "Lake Tahoe beach water"],
  "granitebay": ["Folsom Lake beach water", "Folsom Lake shoreline", "Folsom Lake Granite Bay boats", "Folsom Lake aerial"],
  "folsompoint": ["Folsom Point Folsom Lake", "Folsom Lake California", "Folsom Lake Dam"],
  "marina": ["Marina State Beach California", "Marina State Beach dunes", "Marina California beach Monterey Bay"],
}
OK_LIC = ("CC0", "Public domain", "CC BY", "CC BY-SA")

def api(params):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    for i in range(5):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            print("retry", i, e, file=sys.stderr); time.sleep(20*(i+1))
    raise RuntimeError("gave up")

def candidates(q):
    d = api({"action":"query","generator":"search","gsrsearch":q+" filetype:bitmap","gsrnamespace":6,"gsrlimit":12,
             "prop":"imageinfo","iiprop":"url|extmetadata|size|mime","iiurlwidth":640,"format":"json"})
    out = []
    for p in d.get("query",{}).get("pages",{}).values():
        ii = p["imageinfo"][0]; m = ii.get("extmetadata",{})
        lic = m.get("LicenseShortName",{}).get("value","")
        if not any(lic.startswith(o) for o in OK_LIC): continue
        if ii.get("mime") not in ("image/jpeg","image/png"): continue
        w,h = ii.get("width",0), ii.get("height",0)
        if w < 600 or h == 0: continue
        ratio = w/h
        if ratio < 1.15: continue   # landscape only
        t = p["title"].lower()
        if re.search(r"\b19[0-8]\d\b", t): continue
        bad = any(x in t for x in ("map","flood","1945","19[0-8]","sign","logo","diagram","plaque","interior","museum","school","church","house","building","chart","flag","seal","restroom","visitor","station","vineyard","street","depot","caboose","hotel","motel","store"))
        score = (0 if bad else 2) + (1 if "california" in t or "san francisco" in t or "tahoe" in t else 0) + (1 if 1.3 <= ratio <= 2.0 else 0)
        out.append((score, p["title"], ii["thumburl"], lic, m.get("Artist",{}).get("value",""), p.get("index",99)))
    out.sort(key=lambda x: (-x[0], x[5]))
    return out

credits = {}
for sid, qs in QUERIES.items():
    dest = os.path.join(IMG, sid + ".jpg")
    if os.path.exists(dest): continue
    pick = None
    for q in qs:
        try: c = candidates(q)
        except Exception as e: print("search failed", sid, q, e, file=sys.stderr); c = []
        if c: pick = c[0]; break
        time.sleep(10)
    if not pick: print("NO PHOTO", sid); continue
    score, title, url, lic, artist, _ = pick
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=40) as r: data = r.read()
        open(dest,"wb").write(data)
        import re
        artist = re.sub(r"<[^>]+>", "", artist).strip()
        credits[sid] = {"title": title.replace("File:",""), "license": lic, "artist": artist[:80]}
        print(sid, "ok", len(data)//1024, "KB |", lic, "|", title[:70])
    except Exception as e:
        print("download failed", sid, e, file=sys.stderr)
    time.sleep(10)

old = {}
cp = os.path.join(IMG, "credits.json")
if os.path.exists(cp): old = json.load(open(cp))
old.update(credits); json.dump(old, open(cp,"w"), indent=1)
