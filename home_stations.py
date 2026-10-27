#!/usr/bin/env python3
"""Personal / home weather stations: the third class of sensor beside the hand-verified public catalogue.
Run right after obs_standalone.py in the hourly job (.github/workflows/observations.yml):

    python3 home_stations.py [obs.json]

Two keyless-or-free feeds, both read server-side only (the page never talks to them):

  cwop     CWOP citizen stations over APRS-IS (kind "cwop"): one read-only TCP connection to rotate.aprs2.net:14580,
           logged in as N0CALL (passcode -1 = receive only, the documented way to listen), one `r/lat/lon/km` range
           filter per cluster of spots (RANGE_KM 24 km ~ 15 mi around every curated and rider-added spot), listening
           LISTEN_S seconds and keeping the newest weather packet per callsign. APRS-IS ORs its filters together, so a
           `t/w` type filter beside the ranges would admit every weather packet on Earth; the weather test is done here
           instead (parse_aprs() keeps only packets with usable wind). Any socket error skips the kind — never fatal.
           Fallback when APRS-IS is unreachable from Actions: findu.com's raw-packet page per callsign, only for
           callsigns already in the catalogue and only up to FINDU_MAX requests.
  netatmo  Netatmo public weather map (kind "netatmo"): GET api.netatmo.com/api/getpublicdata with required_data=wind,
           one call per bounding box (one box per spot cluster, padded NETATMO_PAD_KM), OAuth token from a refresh token
           (scope read_station; secrets NETATMO_CLIENT_ID / NETATMO_CLIENT_SECRET / NETATMO_REFRESH_TOKEN, docs/SETUP-NETATMO.md).
           Netatmo rotates refresh tokens: the newest one is kept in the sync Worker's KV (PUT /v1/admin/vars/netatmo_refresh_token)
           when SYNC_URL / SYNC_ADMIN_TOKEN exist, else the limitation is printed. Only modules with a wind gauge; wind and gust
           km/h -> knots; the station id is the device MAC; only its location rounded to 3 decimals is ever committed.
           Skipped silently when the secrets are absent, like the alerts job.

Every station ever heard lands permanently in home-stations.json ({"stations": {id: {id, kind, lat, lon, place?, firstSeen,
lastSeen}}}) — documented once found, never dropped. Each spot (curated, from spots.json, and rider-added, from
rider-stations.json) is given the nearest up to ATTACH_MAX home stations within ATTACH_MI that read this run, as rows in
the ordinary obs.json shape {id, name, kind, dist_mi, time, spd, gst, dir, age_min} plus class:"home" (every public row
carries class:"reliable") and trusted:true/false from home-trust.json (home_trust.py). The page shows them as a labelled
hint from day one; alerts and the bias correction use a home station only once it is trusted and no official station is
within HOME_GAP_MI (home_trust.py). Nothing here can fail the job: any error is printed and the exit status stays 0, and
obs.json is only rewritten (atomically) when the home rows are ready. `python3 test_home_stations.py` tests it offline."""
import datetime as dt
import json
import math
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOGUE = os.path.join(HERE, "home-stations.json")
TRUST = os.path.join(HERE, "home-trust.json")
UA = {"User-Agent": "WindwardMark/1.0 (github.com/mikestoneapps/windward-mark)", "Accept": "application/json, text/html, text/plain"}

APRS_HOST, APRS_PORT = "rotate.aprs2.net", 14580
APRS_LOGIN = "user N0CALL pass -1 vers WindwardMark 1.0"   # receive-only login (passcode -1): we never transmit
LISTEN_S = int(os.environ.get("CWOP_LISTEN_S") or 90)       # how long to listen per run (CWOP stations report every 5–15 min)
CLUSTER_KM = 20          # spots closer than this share one range filter / one Netatmo box
RANGE_KM = 24            # ~15 mi: the APRS range filter radius beyond each cluster's own extent
NETATMO_PAD_KM = 15      # Netatmo box padding beyond each cluster's extent
ATTACH_MI, ATTACH_MAX = 10, 3   # a spot lists the nearest ATTACH_MAX home stations within ATTACH_MI
FINDU_MAX = 60           # findu fallback: at most this many callsign pages per run
MAX_MPH, MAX_GUST_MPH = 150, 200   # beyond these a packet is garbage, not wind
MPH2KN = 0.868976
KMH2KN = 1 / 1.852
NETATMO_TOKEN_KEY = "netatmo_refresh_token"   # the Worker KV var that carries the newest refresh token


def say(*a, file=None):
    print(*a, file=file or sys.stdout)


def mi(a, b, c, d):
    r = math.pi / 180
    x = math.sin((c - a) * r / 2) ** 2 + math.cos(a * r) * math.cos(c * r) * math.sin((d - b) * r / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(x))


def km(a, b, c, d):
    return mi(a, b, c, d) * 1.609344


def iso_utc(t):
    return t.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_time(s):
    try:
        t = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)
    except Exception:
        return None


def rnd(v):
    return None if v is None else round(float(v), 3)


# ---------- the spots to cover: curated + rider-added, and how they cluster into areas ----------

def spot_points(spots_path=None, rider_path=None):
    """[{id, name, lat, lon}] for every curated spot and every rider-added spot the hourly job knows (rider-stations.json)."""
    out = []
    try:
        for s in json.load(open(spots_path or os.path.join(HERE, "spots.json"), encoding="utf-8")):
            if s.get("lat") is not None and s.get("lon") is not None:
                out.append({"id": s["id"], "name": s.get("name") or s["id"], "lat": float(s["lat"]), "lon": float(s["lon"])})
    except Exception as e:
        print("home stations: spots.json unreadable:", repr(e), file=sys.stderr)
    seen = {p["id"] for p in out}
    try:
        rider = json.load(open(rider_path or os.path.join(HERE, "rider-stations.json"), encoding="utf-8"))
    except Exception:
        rider = {}
    for sid, e in (rider.items() if isinstance(rider, dict) else []):
        if sid in seen or not isinstance(e, dict) or e.get("lat") is None or e.get("lon") is None:
            continue
        out.append({"id": sid, "name": str(e.get("name") or sid), "lat": float(e["lat"]), "lon": float(e["lon"])})
    return out


def clusters(points, merge_km=CLUSTER_KM):
    """Greedy areas: a point joins the first cluster whose centre is within merge_km, else starts one.
    Each is {lat, lon (centre), r_km (farthest member from the centre), ids}. Deterministic for a given order."""
    out = []
    for p in sorted(points, key=lambda p: (p["lat"], p["lon"], p["id"])):
        for c in out:
            if km(p["lat"], p["lon"], c["lat"], c["lon"]) <= merge_km:
                c["ids"].append(p["id"]); c["pts"].append((p["lat"], p["lon"]))
                c["lat"] = sum(x for x, _ in c["pts"]) / len(c["pts"]); c["lon"] = sum(y for _, y in c["pts"]) / len(c["pts"])
                break
        else:
            out.append({"lat": p["lat"], "lon": p["lon"], "ids": [p["id"]], "pts": [(p["lat"], p["lon"])]})
    for c in out:
        c["r_km"] = max(km(c["lat"], c["lon"], x, y) for x, y in c["pts"])
        del c["pts"]
    return out


def aprs_filter(areas, range_km=RANGE_KM):
    """The login's filter: one range filter per cluster, radius = the cluster's extent plus range_km (so every spot in it
    is covered to range_km). No t/w: APRS-IS ORs filters, so a type filter would admit every weather packet worldwide."""
    return " ".join(f"r/{c['lat']:.3f}/{c['lon']:.3f}/{int(math.ceil(c['r_km'] + range_km))}" for c in areas)


def netatmo_boxes(areas, pad_km=NETATMO_PAD_KM):
    """[(lat_ne, lon_ne, lat_sw, lon_sw)] per cluster: its extent plus pad_km on every side."""
    out = []
    for c in areas:
        dlat = (c["r_km"] + pad_km) / 111.2
        dlon = (c["r_km"] + pad_km) / (111.2 * max(0.2, math.cos(c["lat"] * math.pi / 180)))
        out.append((round(c["lat"] + dlat, 4), round(c["lon"] + dlon, 4), round(c["lat"] - dlat, 4), round(c["lon"] - dlon, 4)))
    return out


# ---------- APRS weather packets ----------

_POS = re.compile(r"^(\d{2})(\d{2}\.\d{2})([NS])(.)(\d{3})(\d{2}\.\d{2})([EW])(.)")
_CS = re.compile(r"^(\d{3}|\.{3}|\s{3})/(\d{3}|\.{3}|\s{3})")
_CSG = re.compile(r"c(\d{3}|\.{3})s(\d{3}|\.{3})")
_GUST = re.compile(r"g(\d{3}|\.{3})")


def _aprs_time(stamp, now):
    """An APRS timestamp (DDHHMMz zulu, DDHHMM/ local, HHMMSSh zulu, MMDDHHMM positionless zulu) as an aware UTC
    datetime, the most recent one not more than an hour after `now`; None when it cannot be placed."""
    now = now.astimezone(dt.timezone.utc)
    try:
        if len(stamp) == 7 and stamp[-1] in "z/":
            d, h, m = int(stamp[0:2]), int(stamp[2:4]), int(stamp[4:6])
            cands = []
            for back in (0, 1, 2):
                y, mo = now.year, now.month - back
                while mo < 1:
                    mo += 12; y -= 1
                try:
                    cands.append(dt.datetime(y, mo, d, h, m, tzinfo=dt.timezone.utc))
                except ValueError:
                    pass
        elif len(stamp) == 7 and stamp[-1] == "h":
            h, m, s = int(stamp[0:2]), int(stamp[2:4]), int(stamp[4:6])
            cands = [(now - dt.timedelta(days=back)).replace(hour=h, minute=m, second=s, microsecond=0) for back in (0, 1)]
        elif len(stamp) == 8 and stamp.isdigit():
            mo, d, h, m = int(stamp[0:2]), int(stamp[2:4]), int(stamp[4:6]), int(stamp[6:8])
            cands = []
            for back in (0, 1):
                try:
                    cands.append(dt.datetime(now.year - back, mo, d, h, m, tzinfo=dt.timezone.utc))
                except ValueError:
                    pass
        else:
            return None
    except ValueError:
        return None
    ok = [c for c in cands if c <= now + dt.timedelta(hours=1)]
    return max(ok) if ok else None


def _num(s):
    return None if s is None or not s.strip().isdigit() else int(s)


def parse_aprs(line, now):
    """One APRS-IS line -> {call, lat, lon, dir, spd, gst, time} (knots; lat/lon None for a positionless report; time
    None when the packet carries no timestamp) or None for anything that is not a usable wind report: server comments,
    third-party and message packets, compressed or ambiguous positions, missing wind ('...'), impossible values."""
    if not line or line.startswith("#") or ">" not in line or ":" not in line:
        return None
    head, _, body = line.partition(":")
    call = head.split(">", 1)[0].strip()
    if not call or len(call) > 9 or not re.fullmatch(r"[A-Za-z0-9-]+", call) or not body:
        return None
    kind, rest = body[0], body[1:]
    t = None
    lat = lon = None
    if kind == "_":                                   # positionless weather: _MMDDHHMMc...s...g...
        if len(rest) < 8:
            return None
        t = _aprs_time(rest[:8], now)
        if t is None:
            return None
        rest = rest[8:]
        m = _CSG.search(rest[:16])
        if not m:
            return None
        d, s = _num(m.group(1)), _num(m.group(2))
        g = _GUST.search(rest[m.end():m.end() + 8])
        gst = _num(g.group(1)) if g else None
    elif kind in "!=@/":
        if kind in "@/":
            if len(rest) < 7:
                return None
            t = _aprs_time(rest[:7], now)
            rest = rest[7:]
        pm = _POS.match(rest)
        if not pm or pm.group(8) != "_":              # compressed / ambiguous position, or not a weather symbol
            return None
        lat = int(pm.group(1)) + float(pm.group(2)) / 60
        lon = int(pm.group(5)) + float(pm.group(6)) / 60
        if pm.group(3) == "S":
            lat = -lat
        if pm.group(7) == "W":
            lon = -lon
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return None
        rest = rest[pm.end():]
        cm = _CS.match(rest)
        if cm:
            d, s = _num(cm.group(1)), _num(cm.group(2))
            tail = rest[cm.end():]
        else:
            m = _CSG.search(rest[:16])
            if not m:
                return None
            d, s = _num(m.group(1)), _num(m.group(2))
            tail = rest[m.end():]
        g = _GUST.search(tail[:8])
        gst = _num(g.group(1)) if g else None
    else:
        return None
    if s is None or s > MAX_MPH or (gst is not None and (gst > MAX_GUST_MPH or gst < s)):
        return None
    if d is not None and not 0 <= d <= 360:
        return None
    return {"call": call, "lat": rnd(lat), "lon": rnd(lon), "dir": None if d is None else d % 360,
            "spd": round(s * MPH2KN, 1), "gst": None if gst is None else round(gst * MPH2KN, 1), "time": t}


def collect_aprs(lines, now, stamp_unstamped=True):
    """Newest usable wind report per callsign over an iterable of APRS-IS lines. On the live feed (stamp_unstamped
    True) arrival order is the truth — a later line replaces an earlier one whatever its own clock says — and a packet
    without a timestamp is stamped `now` (it just arrived). On findu's archived pages (stamp_unstamped False) the
    packet's own stamp orders them and an unstamped packet is dropped (there is no telling when it arrived)."""
    out = {}
    for ln in lines:
        p = parse_aprs(ln, now)
        if not p:
            continue
        if p["time"] is None:
            if not stamp_unstamped:
                continue
            p["time"] = now
        cur = out.get(p["call"])
        if not cur or stamp_unstamped or p["time"] > cur["time"]:
            if cur and p["lat"] is None and cur["lat"] is not None:
                p["lat"], p["lon"] = cur["lat"], cur["lon"]   # a positionless update keeps the position already heard
            out[p["call"]] = p
        elif cur and cur["lat"] is None and p["lat"] is not None:
            cur["lat"], cur["lon"] = p["lat"], p["lon"]
    return out


def aprs_listen(filt, seconds=LISTEN_S, host=APRS_HOST, port=APRS_PORT, now=None, connect=socket.create_connection):
    """Open one read-only APRS-IS connection, send the login with the filter, read for `seconds`, return the raw lines.
    Raises on any socket trouble (the caller skips the kind)."""
    now = now or dt.datetime.now(dt.timezone.utc)
    lines = []
    s = connect((host, port), timeout=15)
    try:
        s.sendall((APRS_LOGIN + " filter " + filt + "\r\n").encode("ascii"))
        s.settimeout(5)
        buf = b""
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            try:
                chunk = s.recv(65536)
            except socket.timeout:
                continue
            if not chunk:
                break
            buf += chunk
            while b"\n" in buf:
                raw, _, buf = buf.partition(b"\n")
                lines.append(raw.decode("utf-8", "replace").rstrip("\r"))
    finally:
        try:
            s.close()
        except Exception:
            pass
    return lines


def findu_url(call):
    return "https://www.findu.com/cgi-bin/raw.cgi?call=" + urllib.parse.quote(call) + "&start=1"


def parse_findu(text, now):
    """findu's raw-packet page for one callsign: the APRS lines inside the HTML, parsed like the live feed but with
    unstamped packets dropped (the page does not say when they arrived)."""
    plain = re.sub(r"<[^>]+>", "\n", text)
    found = collect_aprs((l.strip() for l in plain.splitlines() if ">" in l and ":" in l), now, stamp_unstamped=False)
    return next(iter(found.values()), None) if len(found) == 1 else (max(found.values(), key=lambda p: p["time"]) if found else None)


# ---------- Netatmo public data ----------

NETATMO_TOKEN_URL = "https://api.netatmo.com/oauth2/token"
NETATMO_PUBLIC_URL = "https://api.netatmo.com/api/getpublicdata"


def http(url, data=None, headers=None, tries=3):
    h = {**UA, **(headers or {})}
    body = None if data is None else (data if isinstance(data, bytes) else urllib.parse.urlencode(data).encode())
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=h), timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500 or i == tries - 1:
                raise
            time.sleep(2 + 2 * i)
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 + 2 * i)


def netatmo_token(client_id, client_secret, refresh_token, post=http):
    """(access_token, refresh_token) from a refresh token; the returned refresh token is the one to keep (Netatmo rotates them)."""
    d = json.loads(post(NETATMO_TOKEN_URL, data={"grant_type": "refresh_token", "refresh_token": refresh_token,
                                                  "client_id": client_id, "client_secret": client_secret},
                        headers={"Content-Type": "application/x-www-form-urlencoded"}))
    if not d.get("access_token"):
        raise RuntimeError("netatmo token answer without access_token")
    return d["access_token"], d.get("refresh_token") or refresh_token


def netatmo_public_url(box):
    lat_ne, lon_ne, lat_sw, lon_sw = box
    return NETATMO_PUBLIC_URL + "?" + urllib.parse.urlencode({"lat_ne": lat_ne, "lon_ne": lon_ne, "lat_sw": lat_sw, "lon_sw": lon_sw,
                                                              "required_data": "wind", "filter": "true"})


def parse_netatmo(text, now):
    """getpublicdata's answer -> {device MAC: {call, lat, lon, place, dir, spd, gst, time}} for devices with a wind gauge
    reading (wind_strength km/h, wind_angle, gust_strength, wind_timeutc). Everything else is left out."""
    d = json.loads(text)
    out = {}
    for dev in (d.get("body") or []) if isinstance(d, dict) else []:
        mac = dev.get("_id")
        loc = ((dev.get("place") or {}).get("location") or [None, None])
        if not mac or len(loc) < 2 or loc[0] is None or loc[1] is None:
            continue
        best = None
        for mod in (dev.get("measures") or {}).values():
            if not isinstance(mod, dict) or mod.get("wind_strength") is None:
                continue
            ts = mod.get("wind_timeutc")
            t = dt.datetime.fromtimestamp(int(ts), dt.timezone.utc) if ts else now
            if best is None or t > best["time"]:
                try:
                    kmh = float(mod["wind_strength"])
                    gkmh = None if mod.get("gust_strength") is None else float(mod["gust_strength"])
                    ang = None if mod.get("wind_angle") is None else float(mod["wind_angle"])
                except (TypeError, ValueError):
                    continue
                if not 0 <= kmh <= MAX_MPH * 1.609 or (gkmh is not None and not kmh <= gkmh <= MAX_GUST_MPH * 1.609):
                    continue
                if ang is not None and not 0 <= ang <= 360:
                    ang = None
                spd, gst = kmh * KMH2KN, None if gkmh is None else gkmh * KMH2KN
                best = {"call": mac, "lat": rnd(loc[1]), "lon": rnd(loc[0]), "place": (dev.get("place") or {}).get("city") or None,
                        "dir": ang, "spd": round(spd, 1), "gst": None if gst is None else round(gst, 1), "time": t}
        if best:
            out[mac] = best
    return out


class WorkerVars:
    """GET/PUT /v1/admin/vars/<name> on the sync Worker: where the newest Netatmo refresh token lives between runs."""

    def __init__(self, url, token, getter=http):
        self.url, self.token, self.getter = url.rstrip("/"), token, getter

    def get(self, name):
        try:
            return (json.loads(self.getter(f"{self.url}/v1/admin/vars/{name}", headers={"Authorization": "Bearer " + self.token})) or {}).get("value")
        except Exception:
            return None

    def put(self, name, value):
        self.getter(f"{self.url}/v1/admin/vars/{name}", data=json.dumps({"value": value}).encode(),
                    headers={"Authorization": "Bearer " + self.token, "Content-Type": "application/json"})


# ---------- the catalogue ----------

def load_catalogue(path=CATALOGUE):
    try:
        d = json.load(open(path, encoding="utf-8"))
        st = d.get("stations") if isinstance(d, dict) else None
        return {"stations": st if isinstance(st, dict) else {}}
    except Exception:
        return {"stations": {}}


def save_catalogue(path, cat):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump({"stations": dict(sorted(cat["stations"].items()))}, fh, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def load_trust(path=TRUST):
    try:
        d = json.load(open(path, encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def update_catalogue(cat, found, kind, now):
    """Every station heard this run enters (or refreshes) the catalogue: id, kind, rounded position, place when known,
    firstSeen / lastSeen. Nothing is ever removed. Returns the number of new stations."""
    stamp = iso_utc(now)
    new = 0
    for sid, p in found.items():
        e = cat["stations"].get(sid)
        if p.get("lat") is None:
            if not e:
                continue   # a positionless station we have never placed: wait for a positioned packet
        if not e:
            e = cat["stations"][sid] = {"id": sid, "kind": kind, "lat": p["lat"], "lon": p["lon"], "firstSeen": stamp}
            new += 1
        if p.get("lat") is not None:
            e["lat"], e["lon"] = p["lat"], p["lon"]
        if p.get("place"):
            e["place"] = p["place"]
        e["kind"] = kind
        e["lastSeen"] = stamp
    return new


def station_name(e):
    if e["kind"] == "netatmo":
        return "Home station (Netatmo)" + (f" · {e['place']}" if e.get("place") else "")
    return (f"{e['place']} home station" if e.get("place") else "Home station") + f" (CWOP {e['id']})"


def attach(points, cat, readings, trust, now):
    """{spotId: [home rows]} — per spot the nearest ATTACH_MAX catalogue stations within ATTACH_MI that read this run."""
    out = {}
    for p in points:
        rows = []
        for sid, e in cat["stations"].items():
            r = readings.get(sid)
            if not r or e.get("lat") is None:
                continue
            d = mi(p["lat"], p["lon"], e["lat"], e["lon"])
            if d > ATTACH_MI:
                continue
            tr = trust.get(sid) or {}
            rows.append({"id": sid, "name": station_name(e), "kind": e["kind"], "class": "home", "dist_mi": round(d, 1),
                         "time": iso_utc(r["time"]), "spd": r["spd"], "gst": r.get("gst"), "dir": r.get("dir"),
                         "age_min": int((now - r["time"]).total_seconds() / 60), "trusted": bool(tr.get("trusted"))})
        rows.sort(key=lambda x: x["dist_mi"])
        if rows:
            out[p["id"]] = rows[:ATTACH_MAX]
    return out


def merge_rows(obs, home):
    """The obs.json document with the home rows under each spot (replacing any older home rows) and every public row
    tagged class:"reliable"; rows sorted by distance as before."""
    out = {"fetchedAt": obs.get("fetchedAt"), "obs": {}}
    for sid in sorted(set(obs.get("obs") or {}) | set(home)):
        rows = [dict(r, **{"class": r.get("class") or "reliable"}) for r in (obs.get("obs") or {}).get(sid) or [] if r.get("class") != "home"]
        rows += home.get(sid, [])
        out["obs"][sid] = sorted(rows, key=lambda x: x.get("dist_mi") or 0)
    return out


# ---------- the run ----------

def fetch_cwop(filt, cat, now, listen=aprs_listen, getter=http, log=say):
    """Live APRS-IS readings, or the findu fallback for catalogued callsigns when the socket fails. (readings, source)."""
    try:
        lines = listen(filt, now=now)
        found = collect_aprs(lines, now)
        log(f"home stations: cwop heard {len(lines)} line(s), {len(found)} station(s) with wind in the areas")
        for l in [x for x in lines if x.startswith("#")][:4]: log(f"home stations: aprs-is says: {l[:160]}")
        return found, "aprs-is"
    except Exception as e:
        log(f"home stations: APRS-IS unreachable ({e!r}); trying findu for catalogued callsigns", file=sys.stderr)
    found = {}
    calls = sorted(sid for sid, e in cat["stations"].items() if e.get("kind") == "cwop")[:FINDU_MAX]
    for call in calls:
        try:
            p = parse_findu(getter(findu_url(call)), now)
            if p and (now - p["time"]).total_seconds() < 6 * 3600:
                found[call] = p
        except Exception as e:
            log(f"home stations: findu {call} failed: {e!r}", file=sys.stderr)
        time.sleep(0.2)
    log(f"home stations: findu gave {len(found)} of {len(calls)} catalogued callsign(s)")
    return found, "findu"


def fetch_netatmo(boxes, now, env=os.environ, getter=http, store=None, log=say):
    """Readings per device MAC over every box; {} without the three secrets (said once). The freshest refresh token
    wins: the Worker's stored one over the repository secret; the rotated one goes back to the Worker."""
    cid, sec, rt = env.get("NETATMO_CLIENT_ID"), env.get("NETATMO_CLIENT_SECRET"), env.get("NETATMO_REFRESH_TOKEN")
    if not (cid and sec and rt):
        log("home stations: Netatmo skipped (need NETATMO_CLIENT_ID, NETATMO_CLIENT_SECRET, NETATMO_REFRESH_TOKEN)")
        return {}
    stored = store.get(NETATMO_TOKEN_KEY) if store else None
    access, new_rt = netatmo_token(cid, sec, stored or rt, post=getter)
    if new_rt != (stored or rt):
        if store:
            try:
                store.put(NETATMO_TOKEN_KEY, new_rt)
                log("home stations: Netatmo rotated the refresh token; the new one is stored on the sync Worker")
            except Exception as e:
                log(f"home stations: could not store the rotated Netatmo refresh token ({e!r}); re-issue it per docs/SETUP-NETATMO.md if the next run fails", file=sys.stderr)
        else:
            log("home stations: Netatmo rotated the refresh token and there is no sync Worker to keep it; if the next run fails to log in, re-issue the token (docs/SETUP-NETATMO.md)", file=sys.stderr)
    found = {}
    for box in boxes:
        try:
            got = parse_netatmo(getter(netatmo_public_url(box), headers={"Authorization": "Bearer " + access}), now)
            found.update(got)
            log(f"home stations: netatmo box {box}: {len(got)} station(s) with wind")
        except Exception as e:
            log(f"home stations: netatmo box {box} failed: {e!r}", file=sys.stderr)
        time.sleep(0.5)
    return found


def run(obs_path, cat_path=CATALOGUE, trust_path=TRUST, now=None, points=None, cwop=None, netatmo=None, log=say):
    """One hourly pass. cwop / netatmo: injectable fetchers (filter_or_boxes, cat, now) -> readings dict, for the tests.
    Returns the home rows per spot."""
    now = now or dt.datetime.now(dt.timezone.utc)
    with open(obs_path, encoding="utf-8") as fh:   # first: without obs.json there is nothing to add to, so touch nothing
        obs = json.load(fh)
    points = points if points is not None else spot_points()
    areas = clusters(points)
    cat = load_catalogue(cat_path)
    trust = load_trust(trust_path)
    readings = {}
    counts = {}
    filt = aprs_filter(areas)
    log(f"home stations: {len(points)} spot(s) in {len(areas)} area(s); APRS filter: {filt}")
    try:
        found = cwop(filt, cat, now) if cwop else fetch_cwop(filt, cat, now, log=log)[0]
        counts["cwop"] = update_catalogue(cat, found, "cwop", now)
        readings.update({k: v for k, v in found.items() if cat["stations"].get(k)})
    except Exception as e:
        log(f"home stations: cwop skipped: {e!r}", file=sys.stderr)
    try:
        boxes = netatmo_boxes(areas)
        store = None
        url, tok = os.environ.get("SYNC_URL"), os.environ.get("SYNC_ADMIN_TOKEN")
        if url and tok:
            store = WorkerVars(url, tok)
        found = netatmo(boxes, cat, now) if netatmo else fetch_netatmo(boxes, now, store=store, log=log)
        counts["netatmo"] = update_catalogue(cat, found, "netatmo", now)
        readings.update(found)
    except Exception as e:
        log(f"home stations: netatmo skipped: {e!r}", file=sys.stderr)
    save_catalogue(cat_path, cat)
    home = attach(points, cat, readings, trust, now)
    doc = merge_rows(obs, home)
    tmp = obs_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, separators=(",", ":"))
        fh.write("\n")
    os.replace(tmp, obs_path)
    kinds = {k: sum(1 for e in cat["stations"].values() if e.get("kind") == k) for k in ("cwop", "netatmo")}
    per_area = {", ".join(c["ids"][:2]) + ("…" if len(c["ids"]) > 2 else ""):
                sum(1 for e in cat["stations"].values() if e.get("lat") is not None and km(c["lat"], c["lon"], e["lat"], e["lon"]) <= c["r_km"] + RANGE_KM) for c in areas}
    log(f"home stations: catalogue {kinds['cwop']} cwop + {kinds['netatmo']} netatmo (new this run: {counts}); "
        f"{len(readings)} reading(s); {len(home)} spot(s) with a home row; per area: {per_area}")
    return home


if __name__ == "__main__":
    obs_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "obs.json")
    try:
        run(obs_path)
    except Exception as e:   # the observations commit must not depend on this
        print("home stations skipped:", repr(e), file=sys.stderr)
    sys.exit(0)
