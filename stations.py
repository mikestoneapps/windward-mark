#!/usr/bin/env python3
"""Resolve nearest public wind stations per spot (cached to stations.json) and fetch latest observations
into out/obs.json (same row shape as obs_standalone.py, which holds the per-kind fetchers).

stations.json is a hand-verified catalogue first (docs/research/stations-proposed.json, merged in 2026-10;
each row names its feed in `kind` — see docs/research/networks.md). Auto-resolution only ever ADDS to it:
it asks api.weather.gov for the stations near each spot, keeps airports only (K### ids; CWOP/MADIS mesonet
mirrors lagged days at last check and are deliberately excluded — never let them back in), adds the known
NDBC buoys by distance, and appends whatever the catalogue doesn't already carry. Hand-verified rows are
never dropped or reordered against fresher distances.

Search radius: 35 mi for the Delta, Ocean, Monterey Bay and Tahoe spots (sensors are sparse out there),
25 mi elsewhere, NDBC_RADIUS_MI for buoys, or the spot's own `stationRadiusMi` (spots.json) when larger.

    python3 stations.py --resolve [id ...]    re-resolve every spot (or just those ids) into stations.json

The build container cannot reach NOAA, so run a resolve live on GitHub with the "Resolve stations"
workflow (.github/workflows/resolve-stations.yml), which commits the result."""
import json
import os
import re
import sys
import time
import math
import urllib.request

from obs_standalone import fetch_obs, UA, load_stations

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
spots = json.load(open(os.path.join(HERE, "spots.json")))
CACHE = os.path.join(HERE, "stations.json")

# NDBC buoys / C-MAN near the Bay Area coast (id: name). Distance computed from spot.
NDBC = {"46026": "San Francisco buoy", "46012": "Half Moon Bay buoy", "46013": "Bodega Bay buoy",
        "46042": "Monterey buoy", "46092": "MBARI M1 mooring"}
NDBC_LL = {"46026": (37.754, -122.839), "46012": (37.356, -122.881), "46013": (38.235, -123.307),
           "46042": (36.785, -122.396), "46092": (36.751, -122.029)}

AIRPORT = re.compile(r"^K[A-Z0-9]{3}$")   # ASOS/AWOS airports; everything else on api.weather.gov is a CWOP/MADIS mirror


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read().decode()
        except Exception:
            if i == tries - 1: raise
            time.sleep(2 + 2 * i)


def mi(a, b, c, d):
    R = 3958.8; r = math.pi / 180
    x = math.sin((c - a) * r / 2) ** 2 + math.cos(a * r) * math.cos(c * r) * math.sin((d - b) * r / 2) ** 2
    return 2 * R * math.asin(math.sqrt(x))


NWS_RADIUS_MI, FAR_RADIUS_MI, NDBC_RADIUS_MI = 25, 35, 45
FAR_REGIONS = {"Delta", "Ocean", "Monterey Bay", "Tahoe"}


def radii(s):
    base = FAR_RADIUS_MI if s.get("region") in FAR_REGIONS else NWS_RADIUS_MI
    r = s.get("stationRadiusMi")
    return (max(base, r), max(NDBC_RADIUS_MI, r)) if r else (base, NDBC_RADIUS_MI)


def resolve(only=None):
    """Merge freshly found airports and buoys into the hand-verified catalogue; adds only, never drops."""
    out = load_stations() if os.path.exists(CACHE) else {}
    for s in spots:
        if only and s["id"] not in only: continue
        nws_mi, ndbc_mi = radii(s)
        have = {x["id"] for x in out.get(s["id"], [])}
        found = []
        try:
            pts = json.loads(get(f"https://api.weather.gov/points/{s['lat']},{s['lon']}"))
            st = json.loads(get(pts["properties"]["observationStations"]))
            for f in st["features"][:12]:
                sid = f["properties"]["stationIdentifier"]
                if not AIRPORT.match(sid): continue   # keep CWOP/MADIS mirrors out: they were days stale at last audit
                lon, lat = f["geometry"]["coordinates"]
                d = mi(s["lat"], s["lon"], lat, lon)
                if d <= nws_mi: found.append({"id": sid, "name": f["properties"]["name"], "kind": "nws", "lat": lat, "lon": lon, "dist_mi": round(d, 1)})
        except Exception as e:
            print("nws resolve failed", s["id"], e, file=sys.stderr)
        for bid, (la, lo) in NDBC_LL.items():
            d = mi(s["lat"], s["lon"], la, lo)
            if d <= ndbc_mi: found.append({"id": bid, "name": NDBC[bid], "kind": "ndbc", "lat": la, "lon": lo, "dist_mi": round(d, 1)})
        added = [x for x in sorted(found, key=lambda x: x["dist_mi"]) if x["id"] not in have][:3]
        out[s["id"]] = sorted(out.get(s["id"], []) + added, key=lambda x: x.get("dist_mi", 99))
        print(s["id"], "added" if added else "kept", [(x["id"], x["dist_mi"]) for x in added] or len(out[s["id"]]))
        time.sleep(0.6)
    with open(CACHE, "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--resolve":
        only = set(sys.argv[2:]) or None
        st = resolve(only=only)
        for k in (sys.argv[2:] or st): print(k, json.dumps(st.get(k, [])))
        sys.exit(0)
    st = load_stations()
    obs = fetch_obs(st, out_file=os.path.join(OUT, "obs.json"))
    for k, v in obs.items():
        print(k, [(r["id"], r["dist_mi"], r["spd"], r["dir"], r["age_min"]) for r in v])
