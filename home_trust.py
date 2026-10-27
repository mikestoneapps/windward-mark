#!/usr/bin/env python3
"""Earned trust for home weather stations, and the one rule for when a trusted one may stand in for an official station.
Run right after accuracy.py in the hourly job (.github/workflows/observations.yml), before obs_recent.py and bias.py:

    python3 home_trust.py [accuracy.jsonl] [home-trust.json]

Per home station (class "home" lines in accuracy.jsonl, written by accuracy.py for every fresh CWOP / Netatmo row), over
the last WINDOW_DAYS of lines:

  n        paired samples: the home reading beside the nearest official ("reliable") station within PAIR_MI of it that
           read the same hour at the same spot, counted only when the official station read PAIR_MIN_KN or more (a ratio
           against a 1-knot reading says nothing)
  ratio    median of home ÷ official over those pairs
  within   share of those pairs with the home reading inside ±WITHIN of the official one
  mae_fc   median |home − consensus forecast| over the hours the forecast is known (n_fc of them)
  uptime   hours with a reading ÷ hours spanned by its lines in the window (capped at 1)
  trusted  n >= MIN_N and RATIO_LO <= ratio <= RATIO_HI and within >= MIN_WITHIN

Re-evaluated every run on the rolling window, so a station that degrades (a new obstruction, a moved sensor) loses
trust and a sheltered or low-reading one stays a hint forever unless it improves. The file is {stationId: {...}} and
starts empty; obs_standalone.py / home_stations.py tag obs.json rows trusted:true/false from it for the page.

Where a trusted station is used — pick() for obs_recent.py ("Blowing now") and select_lines() for bias.py — the rule is:
the nearest fresh official station wins when it is within HOME_GAP_MI of the spot; beyond that (or with no official
reading at all) the nearest fresh trusted home station stands in; an untrusted home station never counts. The forecast
score itself never reads a home station (SPEC §3 stays model-based); only bias.json carries their influence, under this
rule. Nothing here can fail the job: any error is printed and the exit status stays 0. `python3 test_home_trust.py`."""
import datetime as dt
import json
import os
import sys

import accuracy        # read_lines(), parse_time(), median(), MAX_AGE_MIN
import home_stations   # mi(), load_catalogue(): the home stations' positions
import obs_standalone  # load_stations(), load_rider_stations(): the official stations' positions

HERE = os.path.dirname(os.path.abspath(__file__))
WINDOW_DAYS = 30     # the trust record is rolling: only the last 30 days of lines count
MIN_N = 40           # paired samples before a station can be trusted
RATIO_LO, RATIO_HI = 0.75, 1.3   # median home ÷ official must sit here
WITHIN = 0.30        # a pair "agrees" when the home reading is inside ±30 % of the official one
MIN_WITHIN = 0.60    # and at least this share of pairs must agree
PAIR_MI = 15         # the official station must be within this of the home station
PAIR_MIN_KN = 5      # pairs only when the official station read at least this (ratios near zero are noise)
HOME_GAP_MI = 8      # a trusted home station stands in only when no fresh official station is within this of the spot


def is_home(row):
    return (row or {}).get("class") == "home"


def official_positions(stations=None, rider=None):
    """{stationId: (lat, lon)} over stations.json and rider-stations.json (first occurrence wins)."""
    out = {}
    for lst in list((stations if stations is not None else obs_standalone.load_stations()).values()) + \
               [e.get("stations") or [] for e in (rider if rider is not None else obs_standalone.load_rider_stations()).values() if isinstance(e, dict)]:
        for x in lst:
            if x.get("id") and x.get("lat") is not None and x.get("lon") is not None and x["id"] not in out:
                out[x["id"]] = (float(x["lat"]), float(x["lon"]))
    return out


def samples(lines, home_pos, official_pos, now, window_days=WINDOW_DAYS):
    """{homeId: {hour: {obs, fc, ref, ref_mi}}} — one sample per station per hour; ref is the nearest official
    station's reading within PAIR_MI of the home station that hour (None when there is none)."""
    cutoff = now - dt.timedelta(days=window_days)
    recent = [ln for ln in lines if (accuracy.parse_time(ln.get("run")) or now) >= cutoff and isinstance(ln.get("obs"), (int, float))]
    official = {}
    for ln in recent:
        if not is_home(ln) and ln.get("station"):
            official.setdefault((ln.get("spot"), ln.get("time")), []).append(ln)
    out = {}
    for ln in recent:
        if not is_home(ln) or not ln.get("station"):
            continue
        sid, key = ln["station"], ln.get("time")
        pos = home_pos.get(sid)
        s = out.setdefault(sid, {}).get(key) or {"obs": ln["obs"], "fc": ln.get("median"), "ref": None, "ref_mi": None}
        if pos:
            for o in official.get((ln.get("spot"), key), []):
                p = official_pos.get(o.get("station"))
                if not p or not isinstance(o.get("obs"), (int, float)):
                    continue
                d = home_stations.mi(pos[0], pos[1], p[0], p[1])
                if d <= PAIR_MI and (s["ref_mi"] is None or d < s["ref_mi"]):
                    s["ref"], s["ref_mi"] = o["obs"], round(d, 1)
        if s["fc"] is None and ln.get("median") is not None:
            s["fc"] = ln["median"]
        out[sid][key] = s
    return out


def evaluate(by_hour, now):
    """One station's record from its {hour: sample} map."""
    pairs = [(s["obs"], s["ref"]) for s in by_hour.values() if isinstance(s.get("ref"), (int, float)) and s["ref"] >= PAIR_MIN_KN]
    ratios = [o / r for o, r in pairs]
    within = [abs(o - r) <= WITHIN * r for o, r in pairs]
    fc = [abs(s["obs"] - s["fc"]) for s in by_hour.values() if isinstance(s.get("fc"), (int, float))]
    hours = sorted(h for h in by_hour if isinstance(h, str))
    span = 1
    if len(hours) >= 2:
        try:
            a, b = (dt.datetime.fromisoformat(hours[0]), dt.datetime.fromisoformat(hours[-1]))
            span = max(1, int((b - a).total_seconds() // 3600) + 1)
        except ValueError:
            span = len(hours)
    n = len(pairs)
    ratio = round(accuracy.median(ratios), 2) if ratios else None
    share = round(sum(within) / n, 2) if n else None
    rec = {"n": n, "ratio": ratio, "within": share,
           "mae_fc": round(accuracy.median(fc), 1) if fc else None, "n_fc": len(fc),
           "uptime": round(min(1.0, len(hours) / span), 2) if hours else 0,
           "evaluatedAt": home_stations.iso_utc(now)}
    rec["trusted"] = bool(n >= MIN_N and ratio is not None and RATIO_LO <= ratio <= RATIO_HI and share is not None and share >= MIN_WITHIN)
    return rec


def compute(lines, home_pos, official_pos, now, window_days=WINDOW_DAYS):
    return {sid: evaluate(by_hour, now) for sid, by_hour in sorted(samples(lines, home_pos, official_pos, now, window_days).items())}


def write(path, doc):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def load(path=None):
    """home-trust.json as written, or {} (no file yet, or unreadable)."""
    try:
        d = json.load(open(path or os.path.join(HERE, "home-trust.json"), encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def trusted(trust, station_id):
    return bool(((trust or {}).get(station_id) or {}).get("trusted"))


# ---------- the one rule: which reading stands for the spot ----------

def prefer(reliable, home):
    """reliable: the nearest fresh official reading (or None); home: the nearest fresh TRUSTED home reading (or None).
    The official one wins within HOME_GAP_MI of the spot; beyond that the trusted home station stands in."""
    if reliable is not None and (reliable.get("dist_mi") is None or reliable["dist_mi"] <= HOME_GAP_MI):
        return reliable
    return home if home is not None else reliable


def pick(rows, now, trust, max_age_min=None):
    """The reading obs_recent.py keeps for a spot from its obs.json rows (nearest first): accuracy.freshest()'s official
    pick, or a trusted home row under the rule above. Home rows are tagged trusted from the trust record given here."""
    max_age = accuracy.MAX_AGE_MIN if max_age_min is None else max_age_min
    reliable = accuracy.freshest(rows, now, max_age_min=max_age)
    home = None
    for o in sorted((o for o in accuracy.fresh_home(rows, now, max_age_min=max_age) if trusted(trust, o.get("id"))), key=lambda o: o.get("dist_mi") or 0):
        home = dict(o, trusted=True)
        break
    return prefer(reliable, home)


def select_lines(lines, trust):
    """accuracy.jsonl lines for bias.py: per (spot, hour) the official line(s) when the nearest official station is
    within HOME_GAP_MI, else the nearest trusted home line, else the official line(s); untrusted home lines are dropped."""
    groups = {}
    for ln in lines:
        groups.setdefault((ln.get("spot"), ln.get("time")), []).append(ln)
    out = []
    for key, grp in groups.items():
        rel = sorted((l for l in grp if not is_home(l)), key=lambda l: l.get("dist_mi") if isinstance(l.get("dist_mi"), (int, float)) else 1e9)
        home = sorted((l for l in grp if is_home(l) and trusted(trust, l.get("station"))), key=lambda l: l.get("dist_mi") if isinstance(l.get("dist_mi"), (int, float)) else 1e9)
        chosen = prefer(rel[0] if rel else None, home[0] if home else None)
        if chosen is None:
            continue
        out += [chosen] if is_home(chosen) else rel   # an official hour keeps every official line it had (as before this rule existed)
    return out


def run(log_path, out_path, now=None, home_cat_path=None, stations=None, rider=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    lines = accuracy.read_lines(log_path)
    cat = home_stations.load_catalogue(home_cat_path or home_stations.CATALOGUE)
    home_pos = {sid: (e["lat"], e["lon"]) for sid, e in cat["stations"].items() if e.get("lat") is not None and e.get("lon") is not None}
    doc = compute(lines, home_pos, official_positions(stations, rider), now)
    write(out_path, doc)
    n_tr = sum(1 for v in doc.values() if v.get("trusted"))
    print(f"home trust: {len(doc)} home station(s) with lines in the last {WINDOW_DAYS} days, {n_tr} trusted (n>={MIN_N}, ratio {RATIO_LO}–{RATIO_HI}, within ±{int(WITHIN * 100)} % on {int(MIN_WITHIN * 100)} %+)")
    return doc


if __name__ == "__main__":
    log_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "accuracy.jsonl")
    out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "home-trust.json")
    try:
        run(log_path, out_path)
    except Exception as e:   # the observations commit must not depend on this
        print("home trust skipped:", repr(e), file=sys.stderr)
    sys.exit(0)
