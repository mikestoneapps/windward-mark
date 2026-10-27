#!/usr/bin/env python3
"""Tests for home_trust.py with synthetic accuracy logs:  python3 test_home_trust.py

Histories: a good station (reads like the official one) earns trust; one consistently 50 % low never does; an erratic
one never does; a trusted one that degrades loses it on the rolling window. Also: pairing only within 15 mi of an
official station that read 5+ kn, the 30-day window, uptime, the file shape, and the one selection rule
(HOME_GAP_MI) shared by obs_recent.py (pick) and bias.py (select_lines)."""
import datetime as dt
import json
import os
import random
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import home_trust as T  # noqa: E402

NOW = dt.datetime(2026, 10, 27, 21, 40, tzinfo=dt.timezone.utc)
HOME_POS = {"A1": (37.917, -122.478), "FAR": (38.2, -122.478)}            # A1 at Paradise Cay; FAR 19.5 mi north of it
OFFICIAL_POS = {"RCMC1": (37.9283, -122.4), "FTPC1": (37.8067, -122.465)}   # RCMC1 4.4 mi from A1, 23 mi from FAR


def hour(i):
    t = dt.datetime(2026, 10, 1, 6, tzinfo=dt.timezone.utc) + dt.timedelta(hours=i)
    return t.strftime("%Y-%m-%dT%H:00"), t


def official(spot, i, obs, station="RCMC1", dist=4.4):
    key, t = hour(i)
    return {"spot": spot, "time": key, "run": (t + dt.timedelta(minutes=50)).isoformat(), "station": station, "dist_mi": dist, "class": "reliable",
            "obs": obs, "fc": {"bm": obs - 1}, "median": obs - 1}


def home(spot, i, obs, station="A1", dist=0.3, median=None):
    key, t = hour(i)
    return {"spot": spot, "time": key, "run": (t + dt.timedelta(minutes=50)).isoformat(), "station": station, "dist_mi": dist, "class": "home",
            "obs": obs, "fc": {"bm": 10}, "median": median}


def history(n, factor, jitter=0.0, seed=1, start=0):
    """n hours of an official station reading 8–22 kn with the home station reading factor× that (± jitter×)."""
    rnd = random.Random(seed)
    lines = []
    for i in range(start, start + n):
        ref = 8 + (i * 7) % 15
        f = factor + rnd.uniform(-jitter, jitter)
        lines += [official("paradisecay", i, ref), home("paradisecay", i, round(ref * f, 1), median=ref - 1)]
    return lines


class Trust(unittest.TestCase):
    def test_good_station_is_trusted(self):
        rec = T.compute(history(60, 1.0, jitter=0.1), HOME_POS, OFFICIAL_POS, NOW)["A1"]
        self.assertTrue(rec["trusted"], rec)
        self.assertEqual(rec["n"], 60)
        self.assertTrue(0.9 <= rec["ratio"] <= 1.1 and rec["within"] == 1.0)
        self.assertEqual(rec["n_fc"], 60)
        self.assertAlmostEqual(rec["mae_fc"], 1.0, delta=1.2, msg="median |home − forecast| with the forecast 1 kn under the official reading")
        self.assertEqual(rec["uptime"], 1.0)

    def test_fifty_percent_low_is_never_trusted(self):
        rec = T.compute(history(200, 0.5, jitter=0.05), HOME_POS, OFFICIAL_POS, NOW)["A1"]
        self.assertFalse(rec["trusted"])
        self.assertTrue(0.45 <= rec["ratio"] <= 0.55 and rec["within"] == 0.0 and rec["n"] == 200, rec)

    def test_erratic_station_is_never_trusted(self):
        rec = T.compute(history(200, 1.0, jitter=0.8, seed=7), HOME_POS, OFFICIAL_POS, NOW)["A1"]
        self.assertFalse(rec["trusted"], rec)
        self.assertLess(rec["within"], T.MIN_WITHIN)

    def test_trusted_then_degraded_loses_trust(self):
        good = history(100, 1.0, jitter=0.05)
        self.assertTrue(T.compute(good, HOME_POS, OFFICIAL_POS, NOW)["A1"]["trusted"])
        # a tree grows: from hour 100 on the station reads 40 % low; the window still holds the old good hours for a while
        bad = history(100, 0.6, jitter=0.05, start=100)
        both = T.compute(good + bad, HOME_POS, OFFICIAL_POS, NOW)["A1"]
        self.assertEqual(both["n"], 200)
        later = dt.datetime(2026, 11, 4, 10, 0, tzinfo=dt.timezone.utc)   # the good hours (Oct 1 – Oct 5 09:00) have left the 30-day window; the bad ones (from Oct 5 10:00) remain
        rec = T.compute(good + bad, HOME_POS, OFFICIAL_POS, later)["A1"]
        self.assertFalse(rec["trusted"], rec)
        self.assertEqual(rec["n"], 100)
        self.assertLess(rec["ratio"], T.RATIO_LO)
        self.assertEqual(T.compute(good + bad, HOME_POS, OFFICIAL_POS, later + dt.timedelta(days=60)), {}, "nothing in the window: no record at all")

    def test_forty_samples_needed(self):
        self.assertFalse(T.compute(history(39, 1.0), HOME_POS, OFFICIAL_POS, NOW)["A1"]["trusted"])
        self.assertTrue(T.compute(history(40, 1.0), HOME_POS, OFFICIAL_POS, NOW)["A1"]["trusted"])
        self.assertEqual(T.MIN_N, 40)

    def test_pairing_rules(self):
        lines = history(50, 1.0)
        far = [home("paradisecay", i, 10.0, station="FAR", dist=9.0, median=9.0) for i in range(50)]   # 23 mi from RCMC1: no pair, forecast only
        rec = T.compute(lines + far, HOME_POS, OFFICIAL_POS, NOW)
        self.assertEqual((rec["FAR"]["n"], rec["FAR"]["ratio"], rec["FAR"]["trusted"], rec["FAR"]["n_fc"]), (0, None, False, 50), "no official station within 15 mi: tracked against the forecast, never trusted")
        calm = [official("paradisecay", i, 3.0) for i in range(100, 130)] + [home("paradisecay", i, 1.0) for i in range(100, 130)]
        rec = T.compute(lines + calm, HOME_POS, OFFICIAL_POS, NOW)["A1"]
        self.assertEqual(rec["n"], 50, "hours where the official station read under 5 kn make no pair")
        self.assertTrue(rec["trusted"])
        # two spots log the same home station the same hour: one sample, paired with the nearer official station
        dup = [official("crissy", 0, 20.0, station="FTPC1", dist=0.6), home("crissy", 0, 14.0, dist=7.7)]
        rec = T.compute(history(1, 1.0) + dup, HOME_POS, OFFICIAL_POS, NOW)["A1"]
        self.assertEqual(rec["n"], 1)
        self.assertEqual(rec["ratio"], 1.0, "paired with RCMC1 (4.4 mi from the home station), not FTPC1 (7.7 mi)")
        unknown = [home("paradisecay", 0, 9.0, station="NOWHERE")]
        self.assertEqual(T.compute(unknown, HOME_POS, OFFICIAL_POS, NOW)["NOWHERE"]["n"], 0, "a station the catalogue cannot place pairs with nothing")

    def test_uptime(self):
        lines = history(10, 1.0) + history(10, 1.0, start=30)   # 20 readings over a 40-hour span
        self.assertEqual(T.compute(lines, HOME_POS, OFFICIAL_POS, NOW)["A1"]["uptime"], 0.5)

    def test_run_writes_the_file_and_the_cli_exits_zero(self):
        d = tempfile.mkdtemp()
        log, out, cat = os.path.join(d, "accuracy.jsonl"), os.path.join(d, "home-trust.json"), os.path.join(d, "home-stations.json")
        with open(log, "w") as fh:
            for ln in history(45, 1.0):
                fh.write(json.dumps(ln) + "\n")
        json.dump({"stations": {"A1": {"id": "A1", "kind": "cwop", "lat": 37.917, "lon": -122.478}}}, open(cat, "w"))
        stations = {"paradisecay": [{"id": "RCMC1", "name": "Richmond", "kind": "coops", "lat": 37.9283, "lon": -122.4, "dist_mi": 4.4}]}
        doc = T.run(log, out, now=NOW, home_cat_path=cat, stations=stations, rider={})
        self.assertTrue(doc["A1"]["trusted"])
        self.assertEqual(json.load(open(out)), doc)
        self.assertEqual(T.load(out)["A1"]["n"], 45)
        self.assertEqual(T.load(os.path.join(d, "missing.json")), {})
        r = subprocess.run([sys.executable, os.path.join(ROOT, "home_trust.py"), os.path.join(d, "missing.jsonl"), os.path.join(d, "t2.json")], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.load(open(os.path.join(d, "t2.json"))), {}, "no log: an empty record")
        self.assertEqual(T.official_positions(stations, {"k-x": {"stations": [{"id": "KUKI", "lat": 39.1, "lon": -123.2}]}}), {"RCMC1": (37.9283, -122.4), "KUKI": (39.1, -123.2)})


class Rule(unittest.TestCase):
    TRUST = {"A1": {"trusted": True}, "B6": {"trusted": False}}

    def rows(self, rel_dist, home_dist=0.3, home_id="A1", rel_fresh=True):
        t = (NOW - dt.timedelta(minutes=20 if rel_fresh else 200)).isoformat()
        th = (NOW - dt.timedelta(minutes=15)).isoformat()
        return sorted([{"id": "RCMC1", "name": "Richmond", "kind": "coops", "class": "reliable", "dist_mi": rel_dist, "time": t, "spd": 9.0},
                       {"id": home_id, "name": "Home station (CWOP " + home_id + ")", "kind": "cwop", "class": "home", "dist_mi": home_dist, "time": th, "spd": 11.0, "trusted": self.TRUST.get(home_id, {}).get("trusted", False)}],
                      key=lambda r: r["dist_mi"])

    def test_pick(self):
        self.assertEqual(T.HOME_GAP_MI, 8)
        self.assertEqual(T.pick(self.rows(4.4), NOW, self.TRUST)["id"], "RCMC1", "an official station within 8 mi wins over a nearer trusted home station")
        self.assertEqual(T.pick(self.rows(8.0), NOW, self.TRUST)["id"], "RCMC1", "8.0 mi is still within")
        p = T.pick(self.rows(8.1), NOW, self.TRUST)
        self.assertEqual((p["id"], p["trusted"]), ("A1", True), "beyond 8 mi the trusted home station stands in")
        self.assertEqual(T.pick(self.rows(8.1, home_id="B6"), NOW, self.TRUST)["id"], "RCMC1", "an untrusted home station never does: the far official one is kept")
        self.assertEqual(T.pick(self.rows(8.1, home_id="B6"), NOW, {})["id"], "RCMC1")
        self.assertEqual(T.pick(self.rows(4.4, rel_fresh=False), NOW, self.TRUST)["id"], "A1", "no fresh official reading: the trusted home station stands in")
        self.assertIsNone(T.pick(self.rows(4.4, home_id="B6", rel_fresh=False), NOW, self.TRUST), "…but an untrusted one gives nothing")
        self.assertIsNone(T.pick([], NOW, self.TRUST))
        self.assertIsNone(T.pick([{"id": "X", "spd": 10, "time": NOW.isoformat(), "class": "home", "dist_mi": 1}], NOW, {"X": {"trusted": False}}))

    def test_select_lines(self):
        L = [official("paradisecay", 0, 9.0, dist=4.4), home("paradisecay", 0, 11.0), home("paradisecay", 0, 12.0, station="B6", dist=0.5),
             official("paradisecay", 1, 9.0, dist=9.0), home("paradisecay", 1, 11.0), home("paradisecay", 1, 12.0, station="B6", dist=0.2),
             official("paradisecay", 2, 9.0, dist=9.0), home("paradisecay", 2, 12.0, station="B6", dist=0.2),
             home("paradisecay", 3, 11.0),
             official("crissy", 0, 20.0, station="FTPC1", dist=0.6), official("crissy", 0, 21.0, station="PXOC1", dist=3.3)]
        out = T.select_lines(L, self.TRUST)
        got = {(l["spot"], l["time"]): sorted(x["station"] for x in out if (x["spot"], x["time"]) == (l["spot"], l["time"])) for l in L}
        self.assertEqual(got[("paradisecay", hour(0)[0])], ["RCMC1"], "official within 8 mi: its line only")
        self.assertEqual(got[("paradisecay", hour(1)[0])], ["A1"], "official 9 mi off: the trusted home line (never the nearer untrusted one)")
        self.assertEqual(got[("paradisecay", hour(2)[0])], ["RCMC1"], "official 9 mi off but only an untrusted home station: the official line")
        self.assertEqual(got[("paradisecay", hour(3)[0])], ["A1"], "no official line that hour: the trusted home line")
        self.assertEqual(got[("crissy", hour(0)[0])], ["FTPC1", "PXOC1"], "two official lines in one hour are both kept, as before")
        self.assertEqual(len(T.select_lines(L, {})), 5, "with no trust record home lines never feed the bias (hour 3 has nothing left)")


if __name__ == "__main__":
    unittest.main()
