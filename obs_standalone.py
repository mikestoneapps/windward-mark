#!/usr/bin/env python3
"""Resolve nearest public wind stations per spot (once, cached to stations.json) and fetch latest observations
into obs.json (repo root, or the path given as the first argument):
{fetchedAt, obs: {spotId: [{id,name,kind,dist_mi,time,spd,gst,dir,wvht_ft,age_min}, ...]}}.
Sources: NWS/METAR via api.weather.gov (nearest 2 land stations), NOAA NDBC realtime2 (hand-mapped buoys).
Run hourly by .github/workflows/observations.yml; the page reads obs.json same-origin."""
import json, os, sys, time, math, urllib.request, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "obs.json")
UA = {"User-Agent": "WindwardMark/1.0 (github.com/mikestoneapps/windward-mark)", "Accept": "application/geo+json, application/json"}
spots = []
CACHE = os.path.join(HERE, "stations.json")

# NDBC buoys / C-MAN near the Bay Area coast (id: name). Distance computed from spot.
NDBC = {"46026": "San Francisco buoy", "46012": "Half Moon Bay buoy", "46013": "Bodega Bay buoy",
        "46237": "San Francisco Bar buoy", "46042": "Monterey buoy"}
NDBC_LL = {"46026": (37.754, -122.839), "46012": (37.356, -122.881), "46013": (38.235, -123.307),
           "46237": (37.786, -122.634), "46042": (36.785, -122.396)}

def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read().decode()
        except Exception as e:
            if i == tries - 1: raise
            time.sleep(2 + 2 * i)

def mi(a, b, c, d):
    R = 3958.8; r = math.pi / 180
    x = math.sin((c - a) * r / 2) ** 2 + math.cos(a * r) * math.cos(c * r) * math.sin((d - b) * r / 2) ** 2
    return 2 * R * math.asin(math.sqrt(x))

STATIONS = {"crissy":[{"id":"FTPC1","name":"Fort Point, Golden Gate","kind":"nws","lat":37.8065,"lon":-122.4652,"dist_mi":0.6},{"id":"RCMC1","name":"Richmond Berth 5","kind":"nws","lat":37.9233,"lon":-122.4097,"dist_mi":8.5},{"id":"46237","name":"San Francisco Bar buoy","kind":"ndbc","lat":37.786,"lon":-122.634,"dist_mi":9.9}],"candlestick":[{"id":"KSFO","name":"San Francisco Intl Airport","kind":"nws","lat":37.6213,"lon":-122.379,"dist_mi":5.9},{"id":"AAMC1","name":"Alameda NAS, San Francisco Bay","kind":"nws","lat":37.7717,"lon":-122.3,"dist_mi":6.5},{"id":"46237","name":"San Francisco Bar buoy","kind":"ndbc","lat":37.786,"lon":-122.634,"dist_mi":14.6}],"thirdave":[{"id":"KSQL","name":"San Carlos Airport","kind":"nws","lat":37.5119,"lon":-122.2495,"dist_mi":5.1},{"id":"KSFO","name":"San Francisco Intl Airport","kind":"nws","lat":37.6213,"lon":-122.379,"dist_mi":5.9},{"id":"46237","name":"San Francisco Bar buoy","kind":"ndbc","lat":37.786,"lon":-122.634,"dist_mi":23.9}],"coyote":[{"id":"KSFO","name":"San Francisco Intl Airport","kind":"nws","lat":37.6213,"lon":-122.379,"dist_mi":4.0},{"id":"KSQL","name":"San Carlos Airport","kind":"nws","lat":37.5119,"lon":-122.2495,"dist_mi":6.6},{"id":"46237","name":"San Francisco Bar buoy","kind":"ndbc","lat":37.786,"lon":-122.634,"dist_mi":21.9}],"alameda":[{"id":"AAMC1","name":"Alameda NAS, San Francisco Bay","kind":"nws","lat":37.7717,"lon":-122.3,"dist_mi":1.8},{"id":"KOAK","name":"Oakland Intl Airport","kind":"nws","lat":37.7214,"lon":-122.2208,"dist_mi":3.7},{"id":"46237","name":"San Francisco Bar buoy","kind":"ndbc","lat":37.786,"lon":-122.634,"dist_mi":19.9}],"berkeley":[{"id":"AAMC1","name":"Alameda NAS, San Francisco Bay","kind":"nws","lat":37.7717,"lon":-122.3,"dist_mi":6.4},{"id":"RCMC1","name":"Richmond Berth 5","kind":"nws","lat":37.9233,"lon":-122.4097,"dist_mi":6.6},{"id":"46237","name":"San Francisco Bar buoy","kind":"ndbc","lat":37.786,"lon":-122.634,"dist_mi":18.2}],"pointisabel":[{"id":"RCMC1","name":"Richmond Berth 5","kind":"nws","lat":37.9233,"lon":-122.4097,"dist_mi":5.0},{"id":"AAMC1","name":"Alameda NAS, San Francisco Bay","kind":"nws","lat":37.7717,"lon":-122.3,"dist_mi":8.9},{"id":"46237","name":"San Francisco Bar buoy","kind":"ndbc","lat":37.786,"lon":-122.634,"dist_mi":18.6}],"sherman":[{"id":"PCOC1","name":"Port Chicago, Suisun Bay","kind":"nws","lat":38.056,"lon":-122.039,"dist_mi":12.7},{"id":"KCCR","name":"Buchanan Field, Concord","kind":"nws","lat":37.9897,"lon":-122.0569,"dist_mi":14.2}],"windycove":[{"id":"KSUU","name":"Travis AFB, Fairfield","kind":"nws","lat":38.2627,"lon":-121.9272,"dist_mi":15.2},{"id":"PCOC1","name":"Port Chicago, Suisun Bay","kind":"nws","lat":38.056,"lon":-122.039,"dist_mi":19.6}],"baypoint":[{"id":"PCOC1","name":"Port Chicago, Suisun Bay","kind":"nws","lat":38.056,"lon":-122.039,"dist_mi":4.2},{"id":"KCCR","name":"Buchanan Field, Concord","kind":"nws","lat":37.9897,"lon":-122.0569,"dist_mi":6.6},{"id":"46237","name":"San Francisco Bar buoy","kind":"ndbc","lat":37.786,"lon":-122.634,"dist_mi":40.9}],"stinson":[{"id":"46237","name":"San Francisco Bar buoy","kind":"ndbc","lat":37.786,"lon":-122.634,"dist_mi":7.7},{"id":"FTPC1","name":"Fort Point, Golden Gate","kind":"nws","lat":37.8065,"lon":-122.4652,"dist_mi":11.6},{"id":"RCMC1","name":"Richmond Berth 5","kind":"nws","lat":37.9233,"lon":-122.4097,"dist_mi":12.9}],"bodega":[{"id":"46013","name":"Bodega Bay buoy","kind":"ndbc","lat":38.235,"lon":-123.307,"dist_mi":15.7},{"id":"KSTS","name":"Sonoma County Airport, Santa Rosa","kind":"nws","lat":38.5089,"lon":-122.8128,"dist_mi":17.8},{"id":"PRYC1","name":"Point Reyes","kind":"nws","lat":37.9961,"lon":-123.02,"dist_mi":22.6}],"waddell":[{"id":"46042","name":"Monterey buoy","kind":"ndbc","lat":36.785,"lon":-122.396,"dist_mi":22.5},{"id":"46012","name":"Half Moon Bay buoy","kind":"ndbc","lat":37.356,"lon":-122.881,"dist_mi":37.8}],"hmb":[{"id":"KHAF","name":"Half Moon Bay Airport","kind":"nws","lat":37.5134,"lon":-122.5011,"dist_mi":3.2},{"id":"KSFO","name":"San Francisco Intl Airport","kind":"nws","lat":37.6213,"lon":-122.379,"dist_mi":10.1},{"id":"46237","name":"San Francisco Bar buoy","kind":"ndbc","lat":37.786,"lon":-122.634,"dist_mi":22.9}],"oceanbeach":[{"id":"FTPC1","name":"Fort Point, Golden Gate","kind":"nws","lat":37.8065,"lon":-122.4652,"dist_mi":3.4},{"id":"46237","name":"San Francisco Bar buoy","kind":"ndbc","lat":37.786,"lon":-122.634,"dist_mi":6.7},{"id":"AAMC1","name":"Alameda NAS, San Francisco Bay","kind":"nws","lat":37.7717,"lon":-122.3,"dist_mi":11.6}],"davenport":[{"id":"46042","name":"Monterey buoy","kind":"ndbc","lat":36.785,"lon":-122.396,"dist_mi":19.9},{"id":"46012","name":"Half Moon Bay buoy","kind":"ndbc","lat":37.356,"lon":-122.881,"dist_mi":41.9}]}
def resolve():
    return STATIONS
    out = {}
    for s in spots:
        lst = []
        try:
            pts = json.loads(get(f"https://api.weather.gov/points/{s['lat']},{s['lon']}"))
            st = json.loads(get(pts["properties"]["observationStations"]))
            for f in st["features"][:6]:
                lon, lat = f["geometry"]["coordinates"]
                d = mi(s["lat"], s["lon"], lat, lon)
                if d <= 25: lst.append({"id": f["properties"]["stationIdentifier"], "name": f["properties"]["name"], "kind": "nws", "lat": lat, "lon": lon, "dist_mi": round(d, 1)})
            lst = sorted(lst, key=lambda x: x["dist_mi"])[:2]
        except Exception as e:
            print("nws resolve failed", s["id"], e, file=sys.stderr)
        for bid, (la, lo) in NDBC_LL.items():
            d = mi(s["lat"], s["lon"], la, lo)
            if d <= 45: lst.append({"id": bid, "name": NDBC[bid], "kind": "ndbc", "lat": la, "lon": lo, "dist_mi": round(d, 1)})
        out[s["id"]] = sorted(lst, key=lambda x: x["dist_mi"])[:3]
        print(s["id"], [(x["id"], x["dist_mi"]) for x in out[s["id"]]])
        time.sleep(0.6)
    json.dump(out, open(CACHE, "w"), indent=1)
    return out

MS2KN = 1.94384
def fetch_obs(stations):
    now = datetime.datetime.now(datetime.timezone.utc)
    cache = {}
    def nws(sid):
        if sid in cache: return cache[sid]
        try:
            d = json.loads(get(f"https://api.weather.gov/stations/{sid}/observations/latest"))["properties"]
            t = datetime.datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00"))
            spd = d["windSpeed"]["value"]; gst = d["windGust"]["value"]; dr = d["windDirection"]["value"]
            # NWS reports km/h
            o = {"time": d["timestamp"], "spd": None if spd is None else round(spd / 1.852, 1), "gst": None if gst is None else round(gst / 1.852, 1),
                 "dir": dr, "age_min": int((now - t).total_seconds() / 60)}
        except Exception as e:
            print("nws obs failed", sid, e, file=sys.stderr); o = None
        cache[sid] = o; return o
    def ndbc(sid):
        if sid in cache: return cache[sid]
        try:
            lines = [l for l in get(f"https://www.ndbc.noaa.gov/data/realtime2/{sid}.txt").splitlines() if not l.startswith("#")]
            cols = ["YY", "MM", "DD", "hh", "mm", "WDIR", "WSPD", "GST", "WVHT", "DPD", "APD", "MWD", "PRES", "ATMP", "WTMP", "DEWP", "VIS", "PTDY", "TIDE"]
            o = None
            for l in lines[:6]:
                v = dict(zip(cols, l.split()))
                if v.get("WSPD", "MM") == "MM": continue
                t = datetime.datetime(int(v["YY"]), int(v["MM"]), int(v["DD"]), int(v["hh"]), int(v["mm"]), tzinfo=datetime.timezone.utc)
                f = lambda k: None if v.get(k, "MM") == "MM" else float(v[k])
                o = {"time": t.isoformat(), "spd": round(f("WSPD") * MS2KN, 1), "gst": None if f("GST") is None else round(f("GST") * MS2KN, 1),
                     "dir": f("WDIR"), "wvht_ft": None if f("WVHT") is None else round(f("WVHT") * 3.281, 1), "wtmp_f": None if f("WTMP") is None else round(f("WTMP") * 9 / 5 + 32),
                     "age_min": int((now - t).total_seconds() / 60)}
                break
        except Exception as e:
            print("ndbc obs failed", sid, e, file=sys.stderr); o = None
        cache[sid] = o; return o
    out = {}
    for sid, lst in stations.items():
        rows = []
        for st in lst:
            o = nws(st["id"]) if st["kind"] == "nws" else ndbc(st["id"])
            if o: rows.append({**{k: st[k] for k in ("id", "name", "kind", "dist_mi")}, **o})
            time.sleep(0.3)
        out[sid] = rows
    with open(OUT_FILE, "w") as fh:
        json.dump({"fetchedAt": now.isoformat(timespec="seconds"), "obs": out}, fh, separators=(",", ":"))
        fh.write("\n")
    return out

if __name__ == "__main__":
    st = resolve()
    obs = fetch_obs(st)
    for k, v in obs.items():
        print(k, [(r["id"], r["dist_mi"], r["spd"], r["dir"], r["age_min"]) for r in v])
