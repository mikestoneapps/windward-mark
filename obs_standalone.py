#!/usr/bin/env python3
"""Fetch the latest station observations for every spot into obs.json (repo root, or the path
given as the first argument): {fetchedAt, obs: {spotId: [{id,name,kind,dist_mi,time,spd,gst,dir,wvht_ft,age_min}, ...]}}.

The station catalogue is stations.json (hand-verified, sorted by distance) plus rider-stations.json
(rider-added spots, resolved hourly by rider_stations.py; capped at 3 wind stations each, and station ids
are fetched once per run however many spots share them). Every row names its feed in
`kind`; docs/research/networks.md has each network's terms and cadence). Every kind returns the same row
shape with wind in knots; a wave-only row (CDIP) carries wvht_ft and spd null, so nothing downstream ever
scores it as wind. A kind that fails is skipped, never fatal. One request per station per run (plus one
per Caltrans district file and one for the JPL Tahoe page, shared), well under NDBC's "keep retrievals
minimal" ask.

Kinds:
  nws      api.weather.gov /stations/{id}/observations/latest (airports only; km/h -> kn)
  coops    NOAA CO-OPS datagetter product=wind (6-min, already knots, gusts); NDBC realtime2 fallback
  ndbc     NDBC realtime2 text (buoys; m/s -> kn, wave height m -> ft)
  raws     IEM obhistory.json, network CA_DCP / NV_DCP (RAWS hourly; SHEF keys, mph -> kn)
  iem      same IEM endpoint (GOES/HADS stations such as the Golden Gate Bridge deck, which reads high)
  cencoos  CeNCOOS ERDDAP tabledap (per-dataset variable names in the row's `vars`; m/s -> kn)
  cdec     CDEC JSONDataServlet sensors 9/10/77 (15-min; mph -> kn; -9999 = missing)
  caltrans cwwp2.dot.ca.gov district RWIS file (NTCIP ESS units: tenths of m/s, 65535 = missing)
  jpl      laketahoe.jpl.nasa.gov/getweather HTML (Tahoe buoys; "min:avg:max" m/s -> kn)
  cdip     CDIP justdar (wave only: Hs m -> ft; never a wind sample)

Run hourly by .github/workflows/observations.yml; the page reads obs.json same-origin."""
import json
import os
import re
import sys
import time
import datetime
import urllib.request
import zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "WindwardMark/1.0 (github.com/mikestoneapps/windward-mark)", "Accept": "application/geo+json, application/json, text/plain, text/html"}
LA = zoneinfo.ZoneInfo("America/Los_Angeles")
MS2KN = 1.94384
MPH2KN = 0.868976
KMH2KN = 1 / 1.852
M2FT = 3.28084


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 + 2 * i)


def load_stations():
    return json.load(open(os.path.join(HERE, "stations.json"), encoding="utf-8"))


def load_rider_stations(path=None):
    """rider-stations.json ({spotId: {name, lat, lon, stations: [rows]}}), the hourly job's cache of
    resolved stations for rider-added spots (rider_stations.py). Missing or unreadable -> {}."""
    try:
        d = json.load(open(path or os.path.join(HERE, "rider-stations.json"), encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def all_stations(rider_path=None):
    """stations.json plus the rider-spot rows, capped at 3 wind stations (and 1 wave row) per rider spot.
    Station ids repeat across spots; fetch_obs() requests each id once per run regardless."""
    st = load_stations()
    for sid, e in load_rider_stations(rider_path).items():
        rows = e.get("stations") if isinstance(e, dict) else None
        if sid in st or not isinstance(rows, list) or not rows:
            continue
        wind = [x for x in rows if not x.get("wave_only") and x.get("kind") != "cdip"][:3]
        wave = [x for x in rows if x.get("wave_only") or x.get("kind") == "cdip"][:1]
        st[sid] = sorted(wind + wave, key=lambda x: x.get("dist_mi", 99))
    return st


def iso_utc(t):
    return t.astimezone(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def age_min(now, t):
    return int((now - t).total_seconds() / 60)


def knots(v, factor):
    return None if v is None else round(float(v) * factor, 1)


# ---------- one parser per kind; each takes the raw text so it can be unit-tested offline ----------

def parse_nws(text, now):
    d = json.loads(text)["properties"]
    t = datetime.datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00"))
    spd = d["windSpeed"]["value"]; gst = d["windGust"]["value"]
    return {"time": d["timestamp"], "spd": knots(spd, KMH2KN), "gst": knots(gst, KMH2KN),
            "dir": d["windDirection"]["value"], "age_min": age_min(now, t)}


def parse_coops(text, now):
    d = json.loads(text)
    row = (d.get("data") or [None])[-1]
    if not row or row.get("s") in (None, ""):
        return None
    t = datetime.datetime.strptime(row["t"], "%Y-%m-%d %H:%M").replace(tzinfo=datetime.timezone.utc)  # time_zone=gmt
    g = row.get("g")
    return {"time": iso_utc(t), "spd": round(float(row["s"]), 1),
            "gst": None if g in (None, "") else round(float(g), 1),
            "dir": None if row.get("d") in (None, "") else float(row["d"]), "age_min": age_min(now, t)}


NDBC_COLS = ["YY", "MM", "DD", "hh", "mm", "WDIR", "WSPD", "GST", "WVHT", "DPD", "APD", "MWD", "PRES", "ATMP", "WTMP", "DEWP", "VIS", "PTDY", "TIDE"]


def parse_ndbc(text, now, wave_ok=False):
    """Latest realtime2 line with a wind value — or, with wave_ok (the CDIP mirrors, which carry no
    anemometer), the latest line with a wave height, returned as a wave-only row (spd null)."""
    lines = [l for l in text.splitlines() if l and not l.startswith("#")]
    for l in lines[:8]:
        v = dict(zip(NDBC_COLS, l.split()))
        has_wind = v.get("WSPD", "MM") != "MM"
        if not has_wind and not (wave_ok and v.get("WVHT", "MM") != "MM"):
            continue
        t = datetime.datetime(int(v["YY"]), int(v["MM"]), int(v["DD"]), int(v["hh"]), int(v["mm"]), tzinfo=datetime.timezone.utc)
        f = lambda k: None if v.get(k, "MM") == "MM" else float(v[k])
        return {"time": iso_utc(t), "spd": knots(f("WSPD"), MS2KN), "gst": knots(f("GST"), MS2KN),
                "dir": f("WDIR"), "wvht_ft": None if f("WVHT") is None else round(f("WVHT") * M2FT, 1),
                "wtmp_f": None if f("WTMP") is None else round(f("WTMP") * 9 / 5 + 32), "age_min": age_min(now, t)}
    return None


def parse_iem(text, now):
    """IEM obhistory for a GOES/HADS (RAWS, bridge, Point Reyes) station: hourly SHEF decodes, values mph.
    USIRGZZ = speed, UDIRGZZ = direction, UPHRGZZ (or UPVRGZZ) = peak gust."""
    rows = json.loads(text).get("data") or []
    for r in reversed(rows):
        spd = r.get("USIRGZZ")
        if spd is None:
            continue
        ts = r.get("utc_valid") or r.get("valid")
        if not ts:
            continue
        t = datetime.datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=datetime.timezone.utc)
        gst = r.get("UPHRGZZ") if r.get("UPHRGZZ") is not None else r.get("UPVRGZZ")
        return {"time": iso_utc(t), "spd": knots(spd, MPH2KN), "gst": knots(gst, MPH2KN),
                "dir": r.get("UDIRGZZ"), "age_min": age_min(now, t)}
    return None


def parse_cencoos(text, vars_, now):
    """ERDDAP tabledap .json with orderByMax("time"): one row, columns time + the dataset's wind names (m/s)."""
    tab = json.loads(text)["table"]
    cols, rows = tab["columnNames"], tab["rows"]
    if not rows:
        return None
    r = dict(zip(cols, rows[-1]))
    t = datetime.datetime.fromisoformat(str(r["time"]).replace("Z", "+00:00"))
    spd = r.get(vars_["spd"])
    if spd is None:
        return None
    return {"time": iso_utc(t), "spd": knots(spd, MS2KN), "gst": knots(r.get(vars_.get("gst", "")), MS2KN),
            "dir": r.get(vars_["dir"]), "age_min": age_min(now, t)}


def _cdec_time(ts):
    """CDEC stamps are California local with the hour NOT zero-padded ('2026-10-26 9:45'), so they must
    never be ordered as strings ('9:45' sorts after '16:14'; the first live runs picked a 9:45 AM row
    over the 4 PM ones that way). Parsed datetime, or None."""
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})[ T](\d{1,2}):(\d{2})", str(ts))
    if not m:
        return None
    try:
        return datetime.datetime(*(int(x) for x in m.groups()), tzinfo=LA)
    except ValueError:
        return None


def parse_cdec(text, now):
    """CDEC JSONDataServlet, sensors 9 (speed, mph), 10 (direction), 77 (peak, mph); -9999 = missing
    (Delta stations sometimes return it). Timestamps are California local time, ordered via _cdec_time."""
    rows = json.loads(text)
    byt = {}
    for r in rows if isinstance(rows, list) else []:
        sn = r.get("SENSOR_NUM") or r.get("sensorNumber") or r.get("sensorNum")
        t = _cdec_time(r.get("date") or r.get("obsDate"))
        v = r.get("value")
        if sn is None or t is None or v is None or float(v) <= -9998:
            continue
        byt.setdefault(t, {})[int(sn)] = float(v)
    for t in sorted(byt, reverse=True):
        v = byt[t]
        if 9 not in v or v[9] < 0:
            continue
        o = {"time": iso_utc(t), "spd": knots(v[9], MPH2KN), "gst": knots(v.get(77), MPH2KN) if v.get(77, -1) >= 0 else None,
             "dir": v.get(10) if 0 <= v.get(10, -1) <= 360 else None, "age_min": age_min(now, t)}
        if o["age_min"] > 180:   # a genuinely stale station: say what the newest usable stamp was
            print(f"obs cdec: latest usable row is from {o['time']} ({o['age_min']} min old)", file=sys.stderr)
        return o
    return None


def _walk(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk(v)


def _find_key(node, key):
    for d in _walk(node):
        if key in d and d[key] not in (None, ""):
            return d[key]
    return None


def parse_caltrans(text, match, now):
    """One district RWIS file; pick the site whose location text carries every word of `match`.
    NTCIP ESS wind units: tenths of m/s, 65535 = missing; directions in degrees, >360 = missing."""
    doc = json.loads(text)
    site, misses = None, []
    for d in _walk(doc):
        if "windData" not in d:
            continue
        hay = re.sub(r"[^a-z0-9]+", " ", json.dumps(d).lower())
        if all(m in hay for m in match):
            site = d
            break
        misses.append(d)
    if not site:
        # Show a sample site verbatim (the 2026-10-27 run proved these dicts carry no locationName where
        # we looked), so the log settles what the location fields are called and where the station lives.
        head = json.dumps(misses[0], separators=(",", ":"))[:300] if misses else "none"
        print(f"obs caltrans: no site matching {match} among {len(misses)} wind site(s); first site: {head}", file=sys.stderr)
        return None
    w = site["windData"] if isinstance(site["windData"], dict) else {}
    def ess(k):
        v = w.get(k)
        try:
            v = float(v)
        except (TypeError, ValueError):
            return None
        return None if v >= 65535 else v
    spd = ess("essAvgWindSpeed") if ess("essAvgWindSpeed") is not None else ess("essSpotWindSpeed")
    if spd is None:
        return None
    gst = ess("essMaxWindGustSpeed")
    dr = ess("essAvgWindDirection") if ess("essAvgWindDirection") is not None else ess("essSpotWindDirection")
    epoch = _find_key(site, "recordEpoch")
    if epoch:
        t = datetime.datetime.fromtimestamp(int(epoch), datetime.timezone.utc)
    else:
        rd, rt = _find_key(site, "recordDate"), _find_key(site, "recordTime")
        if not (rd and rt):
            return None  # no timestamp, no way to age the reading
        t = datetime.datetime.strptime(f"{rd} {rt}"[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=LA)
    return {"time": iso_utc(t), "spd": knots(spd / 10, MS2KN), "gst": None if gst is None else knots(gst / 10, MS2KN),
            "dir": dr if dr is not None and dr <= 360 else None, "age_min": age_min(now, t)}


def parse_jpl(text, buoy, now):
    """laketahoe.jpl.nasa.gov/getweather: an HTML table, one column per buoy (TB1..TB4), updated at :30
    past each hour with the previous hour's last 30 minutes; wind cells are "min:avg:max" (max = gust).
    The unit is read off the Wind Speed row's own label; the page's toggle says "Switch to Metric", so
    the default is mph (the first live run, 2026-10-27, read ~2x the neighbouring RAWS when converted
    as m/s). Cells are matched per row; the page carries no per-reading timestamp, so the reading is
    stamped at the top of the previous hour (what the page says it shows)."""
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S | re.I)
    header, speed, direction = None, None, None
    for tr in rows:
        cells = [re.sub(r"<[^>]+>", " ", c).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S | re.I)]
        if not cells:
            continue
        joined = " ".join(cells).lower()
        if header is None and "tb1" in joined:
            header = [c.strip().upper() for c in cells]
        elif "wind speed" in cells[0].lower():
            speed = cells
        elif "wind dir" in cells[0].lower():
            direction = cells
    if not header or not speed:
        return None
    label = speed[0].lower()
    unit = MS2KN if ("m/s" in label or "m s" in label or "mps" in label) else MPH2KN   # mph unless the label says metric
    if "mph" not in label and unit is MPH2KN:
        print(f"obs jpl: Wind Speed label carries no unit ({speed[0][:40]!r}); assuming mph", file=sys.stderr)
    try:
        col = [h.split()[0] for h in header].index(buoy.upper())
    except ValueError:
        return None
    def mam(cells):   # "min:avg:max" -> (avg, max), or None
        if not cells or col >= len(cells):
            return None
        m = re.findall(r"-?\d+(?:\.\d+)?", cells[col])
        if not m:
            return None
        v = [float(x) for x in m]
        if any(x <= -90 for x in v):   # -99 = missing
            return None
        return (v[1] if len(v) >= 2 else v[0], v[-1])
    sp = mam(speed)
    if not sp:
        return None
    dr = mam(direction) if direction else None
    # The page updates at :30 with the last 30 min of the previous hour, so the newest reading's window
    # ENDS at the most recent top of the hour once :30 has passed — an hour earlier before that. Stamping
    # the window's end keeps a fresh fetch from looking ~60 min stale (the first live runs aged 97 min).
    top = now.replace(minute=0, second=0, microsecond=0)
    t = top if now.minute >= 30 else top - datetime.timedelta(hours=1)
    return {"time": iso_utc(t), "spd": knots(sp[0], unit), "gst": knots(sp[1], unit),
            "dir": None if dr is None else round(dr[0]), "age_min": age_min(now, t)}


def parse_cdip(text, now):
    """CDIP justdar "pm" page (wave parameters only — never a wind sample): a columnar table, as the
    2026-10-27 run's log showed —

        <pre>YEAR MO DY HR MN   Hs   Tp   Dp    Depth   Ta    Pres   Wspd Wdir Temp   Temp
              UTC           m   sec  deg     m     sec    mB     m/s  deg Air(C) Sf...
        2026 10 27 03 26  1.19 11.76  285 ...

    Take the newest data row's Hs (m), Tp (s), Dp (deg); times are UTC; the Wspd column is ignored by
    design (these rows are wave-only). A labelled "Hs: 1.52 m" page still parses as a fallback. None when
    nothing matches — the fetch loop then logs the page head and reads the buoy's NDBC realtime2 mirror."""
    lines = [re.sub(r"<[^>]+>", " ", l) for l in text.splitlines()]
    hdr = next((l for l in lines if re.search(r"\bYEAR\b.*\bHs\b", l)), None)
    if hdr:
        cols = hdr.split()
        try:
            iHs, iTp, iDp = cols.index("Hs"), cols.index("Tp"), cols.index("Dp")
        except ValueError:
            iHs = None
        best = None
        if iHs is not None:
            for l in lines:
                tk = l.split()
                if len(tk) <= max(iHs, iTp, iDp) or not re.fullmatch(r"\d{4}", tk[0]):
                    continue
                try:
                    t = datetime.datetime(int(tk[0]), int(tk[1]), int(tk[2]), int(tk[3]), int(tk[4]), tzinfo=datetime.timezone.utc)
                    hs_m = float(tk[iHs])
                except (ValueError, IndexError):
                    continue
                if not 0 < hs_m < 30:   # -999 sentinels and garbage
                    continue
                if best is None or t > best[0]:
                    best = (t, hs_m, tk)
        if best:
            t, hs_m, tk = best
            def num(i):
                try:
                    return float(tk[i])
                except (ValueError, IndexError):
                    return None
            dp = num(iDp)
            return {"time": iso_utc(t), "spd": None, "gst": None, "dir": None,
                    "wvht_ft": round(hs_m * M2FT, 1), "dpd": num(iTp),
                    "mwd": None if dp is None or not 0 <= dp <= 360 else int(dp),
                    "age_min": age_min(now, t)}
    hs = re.search(r"Hs\s*(?:\((m|ft)\))?\s*[=:]\s*([\d.]+)\s*(m|ft)?\b", text, re.I)
    tp = re.search(r"Tp\s*(?:\(s\))?\s*[=:]\s*([\d.]+)", text, re.I)
    dp = re.search(r"Dp\s*(?:\(deg\))?\s*[=:]\s*(\d+)", text, re.I)
    tm = re.search(r"(\d{2}):(\d{2})\s+(\d{2})/(\d{2})/(\d{4})", text) or re.search(r"(\d{4})(\d{2})(\d{2})\s+(\d{2})(\d{2})", text)
    if not hs:
        return None
    unit = ((hs.group(1) or hs.group(3)) or "m").lower()
    hs_ft = round(float(hs.group(2)) * (1 if unit == "ft" else M2FT), 1)
    if tm and len(tm.groups()) == 5 and "/" in tm.group(0):
        h, mi_, mo, dd, yy = tm.groups()
        t = datetime.datetime(int(yy), int(mo), int(dd), int(h), int(mi_), tzinfo=datetime.timezone.utc)
    elif tm:
        yy, mo, dd, h, mi_ = tm.groups()
        t = datetime.datetime(int(yy), int(mo), int(dd), int(h), int(mi_), tzinfo=datetime.timezone.utc)
    else:
        t = now
    return {"time": iso_utc(t), "spd": None, "gst": None, "dir": None,
            "wvht_ft": hs_ft,
            "dpd": None if not tp else float(tp.group(1)), "mwd": None if not dp else int(dp.group(1)),
            "age_min": age_min(now, t)}


# ---------- the fetch loop: one request per station (district files and the JPL page shared) ----------

IEM_API = "https://mesonet.agron.iastate.edu/api/1/obhistory.json"
ERDDAP = "https://erddap.cencoos.org/erddap/tabledap"


def fetch_obs(stations, now=None, getter=get, out_file=None):
    out_file = out_file or os.path.join(HERE, "obs.json")
    now = now or datetime.datetime.now(datetime.timezone.utc)
    cache, shared = {}, {}

    def once(key, fn):
        """One fetch per station id (or shared resource) per run; a failure is cached as None."""
        if key in cache:
            return cache[key]
        try:
            cache[key] = fn()
        except Exception as e:
            print(f"obs {key} failed:", e, file=sys.stderr)
            cache[key] = None
        return cache[key]

    def shared_text(key, url):
        if key not in shared:
            try:
                shared[key] = getter(url)
            except Exception as e:
                print(f"obs {key} failed:", e, file=sys.stderr)
                shared[key] = None
        return shared[key]

    def iem(st):
        net = st.get("network", "CA_DCP")
        for day in (now.astimezone(LA).date(), now.astimezone(LA).date() - datetime.timedelta(days=1)):
            o = parse_iem(getter(f"{IEM_API}?station={st['id']}&network={net}&date={day.isoformat()}"), now)
            if o:
                return o
        return None

    def reader(st):
        kind = st["kind"]
        if kind == "nws":
            return parse_nws(getter(f"https://api.weather.gov/stations/{st['id']}/observations/latest"), now)
        if kind == "coops":
            try:
                o = parse_coops(getter("https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=wind"
                                       f"&station={st['nos']}&date=latest&units=english&time_zone=gmt&format=json"), now)
                if o:
                    return o
            except Exception as e:
                print(f"obs {st['id']} coops failed, trying NDBC:", e, file=sys.stderr)
            return parse_ndbc(getter(f"https://www.ndbc.noaa.gov/data/realtime2/{st['id']}.txt"), now)
        if kind == "ndbc":
            return parse_ndbc(getter(f"https://www.ndbc.noaa.gov/data/realtime2/{st['id']}.txt"), now)
        if kind in ("raws", "iem"):
            return iem(st)
        if kind == "cencoos":
            cols = ",".join(["time", st["vars"]["spd"], st["vars"]["dir"]] + ([st["vars"]["gst"]] if "gst" in st["vars"] else []))
            return parse_cencoos(getter(f"{ERDDAP}/{st['dataset']}.json?{cols}&orderByMax(%22time%22)"), st["vars"], now)
        if kind == "cdec":
            d0 = (now.astimezone(LA).date() - datetime.timedelta(days=1)).isoformat()
            d1 = (now.astimezone(LA).date() + datetime.timedelta(days=1)).isoformat()
            return parse_cdec(getter("https://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet"
                                     f"?Stations={st['id']}&SensorNums=9,10,77&dur_code=E&Start={d0}&End={d1}"), now)
        if kind == "caltrans":
            dist = st.get("district", "d3")
            text = shared_text("caltrans-" + dist, f"https://cwwp2.dot.ca.gov/data/{dist}/rwis/rwisStatus{dist.upper().replace('D', 'D0')}.json")
            return None if text is None else parse_caltrans(text, st.get("match", [st["id"].lower()]), now)
        if kind == "jpl":
            text = shared_text("jpl", "https://laketahoe.jpl.nasa.gov/getweather")
            return None if text is None else parse_jpl(text, st["id"], now)
        if kind == "cdip":
            try:
                text = getter(f"https://cdip.ucsd.edu/data_access/justdar.cdip?{st['cdip']}+pm")
                o = parse_cdip(text, now)
                if o:
                    return o
                print(f"obs {st['id']} cdip: no Hs in the justdar answer (head: {text[:160]!r}); trying the NDBC mirror", file=sys.stderr)
            except Exception as e:
                print(f"obs {st['id']} cdip justdar failed, trying the NDBC mirror:", e, file=sys.stderr)
            return parse_ndbc(getter(f"https://www.ndbc.noaa.gov/data/realtime2/{st['id']}.txt"), now, wave_ok=True)
        print("obs: unknown kind", kind, st["id"], file=sys.stderr)
        return None

    out = {}
    for sid, lst in stations.items():
        rows = []
        for st in lst:
            o = once(st["id"], lambda st=st: reader(st))
            if o:
                row = {**{k: st[k] for k in ("id", "name", "kind", "dist_mi")}, **o}
                if st.get("wave_only"):
                    row["wave_only"] = True
                    row["spd"] = row["gst"] = row["dir"] = None   # belt and braces: never a wind sample
                rows.append(row)
            time.sleep(0.2)
        out[sid] = rows
    with open(out_file, "w") as fh:
        json.dump({"fetchedAt": now.isoformat(timespec="seconds"), "obs": out}, fh, separators=(",", ":"))
        fh.write("\n")
    return out


if __name__ == "__main__":
    obs = fetch_obs(all_stations(), out_file=sys.argv[1] if len(sys.argv) > 1 else None)
    for k, v in obs.items():
        print(k, [(r["id"], r["dist_mi"], r["spd"], r["dir"], r["age_min"]) for r in v])
