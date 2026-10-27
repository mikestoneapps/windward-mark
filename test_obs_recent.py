#!/usr/bin/env python3
"""Tests for obs_recent.py:  python3 test_obs_recent.py

Checks: the nearest fresh reading per curated spot is kept (the stale, empty and kept-spot rows are not), the trimmed
fields, one entry per fetchedAt, oldest first, the KEEP_RUNS cap, an unreadable old file is replaced, and the CLI exits 0
on a missing obs.json."""
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import obs_recent as R  # noqa: E402
from test_accuracy import NOW, ISO, obs_doc  # noqa: E402


class ObsRecent(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.obs = os.path.join(self.dir, "obs.json")
        self.out = os.path.join(self.dir, "obs-recent.json")
        with open(self.obs, "w") as fh:
            json.dump(obs_doc(), fh)

    def read(self):
        with open(self.out, encoding="utf-8") as fh:
            return json.load(fh)

    def test_snapshot_keeps_the_nearest_fresh_reading(self):
        doc = R.run(self.obs, self.out, now=NOW)
        self.assertEqual(len(doc["runs"]), 1)
        run = doc["runs"][0]
        self.assertEqual(run["at"], ISO(NOW))
        self.assertEqual(set(run["obs"]), {"alameda", "oceanbeach", "crissy"}, "stale sherman, empty candlestick and the kept spot are absent")
        self.assertEqual((run["obs"]["crissy"]["kind"], run["obs"]["oceanbeach"]["kind"]), ("coops", "ndbc"), "new kinds flow through; the wave-only CDIP row is never picked as wind")
        self.assertEqual(run["obs"]["alameda"], {"id": "AAMC1", "name": "ALAMEDA", "kind": "nws", "dist_mi": 1.8, "time": ISO(NOW - dt.timedelta(minutes=35)), "spd": 12.3, "gst": 15.1, "dir": 290})
        self.assertEqual(run["obs"]["oceanbeach"]["id"], "46237", "second station when the nearest has no wind")
        self.assertNotIn("age_min", run["obs"]["crissy"], "only the listed fields, age is read off the timestamp later")
        self.assertEqual(self.read(), doc)

    def test_rider_spot_with_a_rider_stations_entry_is_kept(self):
        rider = os.path.join(self.dir, "rider-stations.json")
        with open(rider, "w") as fh:
            json.dump({"k-somewhere": {"name": "Somewhere", "lat": 37.5, "lon": -122.5, "stations": []}}, fh)
        doc = R.run(self.obs, self.out, now=NOW, rider_path=rider)
        self.assertIn("k-somewhere", doc["runs"][0]["obs"], "a rider spot named by rider-stations.json carries its reading, for Blowing now")
        self.assertEqual(doc["runs"][0]["obs"]["k-somewhere"]["id"], "X")

    def test_trusted_home_station_stands_in_only_beyond_the_gap(self):
        d = obs_doc()
        t = ISO(NOW - dt.timedelta(minutes=12))
        home = lambda sid, dist, trusted: {"id": sid, "name": f"Home station (CWOP {sid})", "kind": "cwop", "class": "home", "dist_mi": dist, "time": t, "spd": 15.0, "gst": 18.0, "dir": 280, "age_min": 12, "trusted": trusted}   # noqa: E731
        d["obs"]["alameda"] = [home("CW1", 0.4, True), {"id": "AAMC1", "name": "ALAMEDA", "kind": "coops", "class": "reliable", "dist_mi": 1.8, "time": t, "spd": 12.3, "gst": 15.1, "dir": 290}]
        d["obs"]["sherman"] = [home("CW2", 0.9, True), {"id": "PCOC1", "name": "Port Chicago", "kind": "coops", "class": "reliable", "dist_mi": 12.7, "time": t, "spd": 20.0, "gst": 25.0, "dir": 270}]
        d["obs"]["crissy"] = [home("CW3", 0.9, False), {"id": "FTPC1", "name": "Fort Point", "kind": "coops", "class": "reliable", "dist_mi": 9.0, "time": t, "spd": 9.0, "gst": None, "dir": 300}]
        d["obs"]["candlestick"] = [home("CW4", 1.2, False)]
        d["obs"]["berkeley"] = [home("CW5", 1.2, True)]
        with open(self.obs, "w") as fh:
            json.dump(d, fh)
        trust = os.path.join(self.dir, "home-trust.json")
        with open(trust, "w") as fh:
            json.dump({"CW1": {"trusted": True}, "CW2": {"trusted": True}, "CW5": {"trusted": True}, "CW3": {"trusted": False}}, fh)
        run = R.run(self.obs, self.out, now=NOW, trust_path=trust)["runs"][0]["obs"]
        self.assertEqual(run["alameda"]["id"], "AAMC1", "an official station within 8 mi wins over a nearer trusted home station")
        self.assertNotIn("class", run["alameda"], "official rows keep the old shape exactly")
        self.assertEqual((run["sherman"]["id"], run["sherman"]["class"], run["sherman"]["trusted"], run["sherman"]["spd"]), ("CW2", "home", True, 15.0), "official 12.7 mi off: the trusted home station stands in, tagged for the alert job")
        self.assertEqual(run["crissy"]["id"], "FTPC1", "an untrusted home station never stands in")
        self.assertNotIn("candlestick", run, "only an untrusted home reading: nothing")
        self.assertEqual(run["berkeley"]["id"], "CW5", "only a trusted home reading: it stands in")
        run = R.run(self.obs, self.out, now=NOW + dt.timedelta(minutes=1))["runs"][0]["obs"]
        self.assertEqual((run["sherman"]["id"], "berkeley" in run), ("PCOC1", False), "without the trust file no home station counts")

    def test_rolling_history(self):
        R.run(self.obs, self.out, now=NOW)
        R.run(self.obs, self.out, now=NOW + dt.timedelta(hours=1))
        self.assertEqual(len(self.read()["runs"]), 1, "the same obs.json (same fetchedAt) is not recorded twice")
        for h in range(1, 9):
            d = obs_doc()
            d["fetchedAt"] = ISO(NOW + dt.timedelta(hours=h))
            for rows in d["obs"].values():
                for o in rows:
                    o["time"] = ISO(NOW + dt.timedelta(hours=h, minutes=-20))
            with open(self.obs, "w") as fh:
                json.dump(d, fh)
            R.run(self.obs, self.out, now=NOW + dt.timedelta(hours=h))
        runs = self.read()["runs"]
        self.assertEqual(len(runs), R.KEEP_RUNS)
        self.assertEqual([r["at"] for r in runs], [ISO(NOW + dt.timedelta(hours=h)) for h in range(9 - R.KEEP_RUNS, 9)], "the last KEEP_RUNS runs, oldest first")
        self.assertIn("sherman", runs[-1]["obs"], "sherman's reading is fresh in the later runs")

    def test_unreadable_old_file_is_replaced(self):
        with open(self.out, "w") as fh:
            fh.write("{not json")
        doc = R.run(self.obs, self.out, now=NOW)
        self.assertEqual(len(doc["runs"]), 1)
        with open(self.out, "w") as fh:
            json.dump({"runs": [{"bogus": 1}, {"at": ISO(NOW - dt.timedelta(hours=1)), "obs": {}}]}, fh)
        doc = R.run(self.obs, self.out, now=NOW)
        self.assertEqual([r["at"] for r in doc["runs"]], [ISO(NOW - dt.timedelta(hours=1)), ISO(NOW)], "entries without at/obs are dropped, the rest kept in order")

    def test_cli_never_fails(self):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "obs_recent.py"), os.path.join(self.dir, "missing.json"), self.out], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("obs-recent skipped", r.stderr)
        self.assertFalse(os.path.exists(self.out))
        r = subprocess.run([sys.executable, os.path.join(ROOT, "obs_recent.py"), self.obs, self.out], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("spot(s) with a fresh reading", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=1)
