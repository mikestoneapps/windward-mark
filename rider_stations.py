#!/usr/bin/env python3
"""Resolve nearest public wind stations for rider-added spots into rider-stations.json, run just before
obs_standalone.py in the hourly job (.github/workflows/observations.yml).

Curated spots have the hand-verified stations.json. A spot the rider adds (settings.kept, synced through
the Worker — rider_stations reads them off GET /v1/admin/riders like the alerts job) gets the same
treatment here, once, keyed by its spot id:

  - the nearest wind-capable rows already in the catalogue within 15 mi (recomputed from the spot's own
    coordinates, so a Bay rider spot leans on the same CO-OPS backbone the page pairs it with),
  - freshly resolved airports (stations.py rules: 25 mi, widened to 35 when nothing is within 25) and
    NDBC buoys (45 mi),

capped at CAP_WIND wind stations per spot so the hourly fetch stays small (station ids repeat across
spots and are fetched once per run anyway); the nearest wave-only row within 25 mi is added when the
spot has waves. An entry is re-resolved only when the spot's coordinates change, and entries for spots
no rider keeps any more are dropped. The file never carries anything about the rider — only

  {spotId: {"name", "lat", "lon", "stations": [rows in the stations.json shape]}}

Missing SYNC_URL / SYNC_ADMIN_TOKEN (the Worker and its admin token), the step prints a note and exits 0,
like the alerts job; any error also exits 0 so obs.json is still fetched and committed.
`python3 test_rider_stations.py` tests it offline."""
import json
import os
import sys
import urllib.request

import stations as ST
from obs_standalone import UA, load_stations

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "rider-stations.json")
PAIR_WIND_MI, PAIR_WAVE_MI = 15, 25   # the page's stationsFor() pairing radii (index.html)
NWS_MI, NWS_FAR_MI = 25, 35           # airports: 25 mi, widened to 35 when nothing is within 25
CAP_WIND = 3                          # wind stations per rider spot


def get_json(url, token, tries=3):
    req = urllib.request.Request(url, headers={**UA, "Authorization": "Bearer " + token})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception:
            if i == tries - 1: raise
            import time; time.sleep(2 + 2 * i)


def kept_spots(riders):
    """{spotId: {name, lat, lon, waves}} over every rider's kept spots; only what the resolve needs, never the rider."""
    out = {}
    for r in riders or []:
        for k in ((r.get("settings") or {}).get("kept") or []) if isinstance(r, dict) else []:
            if not isinstance(k, dict): continue
            sid, lat, lon = k.get("id"), k.get("lat"), k.get("lon")
            if not isinstance(sid, str) or not sid or lat is None or lon is None: continue
            out[sid] = {"name": str(k.get("name") or sid), "lat": float(lat), "lon": float(lon), "waves": bool(k.get("waves"))}
    return out


def catalogue_rows(stations):
    """Every distinct station row in stations.json (first occurrence wins, like the page's STN_BY_ID)."""
    seen, rows = set(), []
    for lst in stations.values():
        for x in lst:
            if x["id"] in seen or x.get("lat") is None or x.get("lon") is None: continue
            seen.add(x["id"]); rows.append(x)
    return rows


def is_wave(x):
    return bool(x.get("wave_only")) or x.get("kind") == "cdip"


def resolve_spot(spot, cat, airports=None, buoys=None):
    """The station rows for one rider spot: catalogue within 15 mi + airports (25/35 mi) + buoys (45 mi),
    capped at CAP_WIND wind rows, plus the nearest wave row within 25 mi when the spot has waves.
    airports/buoys can be injected for the offline tests."""
    lat, lon = spot["lat"], spot["lon"]
    wind, wave = [], []
    for x in cat:
        d = ST.mi(lat, lon, x["lat"], x["lon"])
        row = {**x, "dist_mi": round(d, 1)}
        if is_wave(x):
            if d <= PAIR_WAVE_MI: wave.append(row)
        elif d <= PAIR_WIND_MI:
            wind.append(row)
    found = airports if airports is not None else ST.nearby_airports(lat, lon, NWS_FAR_MI)
    near = [x for x in found if x["dist_mi"] <= NWS_MI]
    wind += near if near else found   # nothing within 25 mi: take what the 35 mi search found
    wind += buoys if buoys is not None else ST.nearby_buoys(lat, lon, ST.NDBC_RADIUS_MI)
    out, seen = [], set()
    for x in sorted(wind, key=lambda x: x["dist_mi"]):
        if x["id"] in seen: continue
        seen.add(x["id"]); out.append(x)
        if len(out) >= CAP_WIND: break
    if spot.get("waves") and wave:
        w = min(wave, key=lambda x: x["dist_mi"])
        if w["id"] not in seen: out.append(w)
    return sorted(out, key=lambda x: x["dist_mi"])


def read_cache(path=CACHE):
    try:
        d = json.load(open(path, encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def run(riders, cache_path=CACHE, stations=None, resolver=resolve_spot):
    """Bring the cache up to date with every rider's kept spots. Returns (cache, resolved, dropped)."""
    stations = stations if stations is not None else load_stations()
    cat = catalogue_rows(stations)
    kept = kept_spots(riders)
    old = read_cache(cache_path)
    cache = {sid: e for sid, e in old.items() if sid in kept}   # a spot nobody keeps any more is dropped
    dropped = len(old) - len(cache)
    resolved = 0
    for sid, s in sorted(kept.items()):
        if sid in stations: continue   # curated: the hand-verified list covers it
        e = cache.get(sid)
        if isinstance(e, dict) and abs(e.get("lat", 9e9) - s["lat"]) < 1e-4 and abs(e.get("lon", 9e9) - s["lon"]) < 1e-4:
            continue   # already resolved for these coordinates
        try:
            rows = resolver(s, cat)
        except Exception as err:   # leave the spot for the next run rather than caching a half answer
            print(f"rider stations: resolve failed for {sid}: {err!r}", file=sys.stderr)
            continue
        cache[sid] = {"name": s["name"], "lat": s["lat"], "lon": s["lon"], "stations": rows}
        resolved += 1
        print(f"rider stations: {sid} -> {[(x['id'], x['dist_mi']) for x in rows] or 'nothing in range'}")
    if cache != old:
        tmp = cache_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, indent=1, sort_keys=True)
            fh.write("\n")
        os.replace(tmp, cache_path)
    print(f"rider stations: {len(kept)} kept spot(s), {resolved} resolved this run, {dropped} dropped, {len(cache)} cached")
    return cache, resolved, dropped


if __name__ == "__main__":
    url = (os.environ.get("SYNC_URL") or "").rstrip("/")
    token = os.environ.get("SYNC_ADMIN_TOKEN") or ""
    if not url or not token:
        print("Rider stations skipped (need SYNC_URL and SYNC_ADMIN_TOKEN); nothing to do.")
        sys.exit(0)
    try:
        riders = (get_json(url + "/v1/admin/riders", token) or {}).get("riders") or []
        run(riders)
    except Exception as e:   # the observations commit must not depend on this
        print("rider stations skipped:", repr(e), file=sys.stderr)
    sys.exit(0)
