#!/usr/bin/env python3
"""Offline tests for home_stations.py:  python3 test_home_stations.py

Checks: APRS weather packets (positioned, positionless, timestamps, missing wind, compressed positions, impossible values,
server comments), the newest-per-callsign rule, the APRS range filter from clustered spots (no t/w), findu's page as the
fallback only for catalogued callsigns and only when the socket fails, Netatmo's public-data answer (km/h -> knots, wind
modules only, rounded positions, the city as the place), the rotated refresh token going to the Worker, the permanent
catalogue (never dropped, rounded, first/last seen), attaching the nearest up-to-3 within 10 mi with trusted flags, the
class tag on every obs.json row, and that a failing feed never fails the run."""
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import home_stations as H  # noqa: E402

NOW = dt.datetime(2026, 10, 27, 21, 40, tzinfo=dt.timezone.utc)
quiet = lambda *a, **k: None   # noqa: E731

# Paradise Cay 37.9168,-122.4785; a station 1 mi away, one 6 mi, one 9.8 mi, one 12 mi
POS1 = "3755.00N/12228.70W_"     # 37.9167, -122.4783
POS6 = "3800.00N/12228.70W_"     # 38.0000: 5.7 mi north
POS10 = "3803.50N/12228.70W_"    # 38.0583: 9.8 mi
POS12 = "3805.40N/12228.70W_"    # 38.09: 12 mi


class Aprs(unittest.TestCase):
    def test_positioned_packet(self):
        p = H.parse_aprs("CW1234>APRS,TCPIP*,qAC,T2SYDNEY:@272130z" + POS1 + "225/012g018t061r000p000P000h55b10170", NOW)
        self.assertEqual((p["call"], p["lat"], p["lon"], p["dir"]), ("CW1234", 37.917, -122.478, 225))
        self.assertAlmostEqual(p["spd"], 10.4, 1, "12 mph -> 10.4 kn")
        self.assertAlmostEqual(p["gst"], 15.6, 1, "18 mph -> 15.6 kn")
        self.assertEqual(p["time"], dt.datetime(2026, 10, 27, 21, 30, tzinfo=dt.timezone.utc), "DDHHMMz is the day/hour/minute in UTC")

    def test_positioned_without_timestamp_and_hms(self):
        p = H.parse_aprs("DW3499>APRS:!" + POS1 + "090/005g008t060", NOW)
        self.assertEqual((p["dir"], p["time"]), (90, None), "a ! packet carries no time: the listener stamps it")
        p = H.parse_aprs("DW3499>APRS:=" + POS1 + "090/005g008t060", NOW)
        self.assertEqual(p["dir"], 90)
        p = H.parse_aprs("DW3499>APRS:/213005h" + POS1 + "090/005g008t060", NOW)
        self.assertEqual(p["time"], NOW.replace(hour=21, minute=30, second=5), "HHMMSSh is a UTC time of day")
        p = H.parse_aprs("DW3499>APRS:@010500z" + POS1 + "090/005g008t060", NOW)
        self.assertEqual(p["time"], dt.datetime(2026, 10, 1, 5, 0, tzinfo=dt.timezone.utc), "day 01 on the 27th is this month's 1st")
        p = H.parse_aprs("DW3499>APRS:@280500z" + POS1 + "090/005g008t060", NOW)
        self.assertEqual(p["time"], dt.datetime(2026, 9, 28, 5, 0, tzinfo=dt.timezone.utc), "day 28 at 21:40 on the 27th is last month's 28th, never the future")

    def test_positionless_packet(self):
        p = H.parse_aprs("FW2543>APRS,TCPIP*:_10272135c270s015g022t058r000p000P000h60b10150", NOW)
        self.assertEqual((p["lat"], p["lon"], p["dir"]), (None, None, 270))
        self.assertAlmostEqual(p["spd"], 13.0, 1)
        self.assertEqual(p["time"], dt.datetime(2026, 10, 27, 21, 35, tzinfo=dt.timezone.utc))

    def test_rejects(self):
        bad = ["# aprsc 2.1.15 server", "# logresp N0CALL unverified, server T2SYDNEY",
               "CW1234>APRS:@272130z" + POS1 + ".../...g...t061",                         # wind missing
               "CW1234>APRS:@272130z" + POS1 + "225/012g005t061",                         # gust under the average: garbage
               "CW1234>APRS:@272130z" + POS1 + "225/180g200t061",                         # 180 mph
               "CW1234>APRS:@272130z" + POS1 + "400/010g012t061",                         # direction 400
               "CW1234>APRS:@272130z/5L!!<*e7_7P[",                                       # compressed position
               "CW1234>APRS:@272130z3755.  N/12228.  W_225/012g018",                      # ambiguous position
               "CW1234>APRS:@272130z3755.00N/12228.70W>225/012g018",                      # not a weather symbol
               "CW1234>APRS:}FW1>APRS,TCPIP:@272130z" + POS1 + "225/012",                 # third-party
               "CW1234>APRS::N0CALL   :hello{1",                                          # message
               "CW1234>APRS:_1027213c270s015",                                            # short positionless stamp
               "", "nonsense"]
        for ln in bad:
            self.assertIsNone(H.parse_aprs(ln, NOW), ln)

    def test_collect_keeps_the_newest_per_callsign_and_remembers_positions(self):
        lines = ["# server", "CW1234>APRS:@272100z" + POS1 + "225/012g018t061", "CW1234>APRS:@272120z" + POS1 + "200/008g010t061",
                 "CW1234>APRS:@272130z" + POS1 + "230/014g020t061",
                 "FW2543>APRS:!" + POS6 + "090/005g008t060", "FW2543>APRS:_10272135c270s015g022t058"]   # a positionless update keeps the position just heard
        got = H.collect_aprs(lines, NOW)
        self.assertEqual(set(got), {"CW1234", "FW2543"})
        self.assertEqual((got["CW1234"]["dir"], got["CW1234"]["time"].minute), (230, 30), "the last line heard wins")
        self.assertEqual((got["FW2543"]["lat"], got["FW2543"]["dir"], got["FW2543"]["time"].minute), (38.0, 270, 35))
        got = H.collect_aprs(["CW1234>APRS:@272130z" + POS1 + "230/014g020t061", "CW1234>APRS:@272100z" + POS1 + "225/012g018t061"], NOW)
        self.assertEqual(got["CW1234"]["dir"], 225, "live feed: arrival order is the truth even when the station's clock disagrees")
        arch = ["CW1234>APRS:@272130z" + POS1 + "230/014g020t061", "CW1234>APRS:@272100z" + POS1 + "225/012g018t061", "FW2543>APRS:!" + POS6 + "090/005g008t060"]
        got = H.collect_aprs(arch, NOW, stamp_unstamped=False)
        self.assertEqual((got["CW1234"]["dir"], "FW2543" in got), (230, False), "findu pages: the packet's own stamp orders them and an unstamped packet cannot be aged, so it is dropped")


class Areas(unittest.TestCase):
    PTS = [{"id": "paradisecay", "name": "PC", "lat": 37.9168, "lon": -122.4785}, {"id": "crissy", "name": "C", "lat": 37.8057, "lon": -122.4535},
           {"id": "sherman", "name": "S", "lat": 38.04, "lon": -121.78}, {"id": "kingsbeach", "name": "K", "lat": 39.237, "lon": -120.026}]

    def test_clusters_and_filter(self):
        areas = H.clusters(self.PTS)
        self.assertEqual([sorted(c["ids"]) for c in areas], [["crissy", "paradisecay"], ["sherman"], ["kingsbeach"]], "the two Bay spots share an area; the Delta and Tahoe spots stand alone")
        f = H.aprs_filter(areas)
        self.assertEqual(f.count("r/"), 3)
        self.assertNotIn("t/w", f, "no type filter: APRS-IS ORs filters, so t/w would admit every weather packet on Earth")
        self.assertRegex(f, r"^r/37\.861/-122\.466/\d+ r/38\.040/-121\.780/24 r/39\.237/-120\.026/24$")
        self.assertGreaterEqual(int(f.split()[0].split("/")[-1]), 24 + 3, "the Bay area's radius covers both spots plus 24 km")

    def test_netatmo_boxes(self):
        boxes = H.netatmo_boxes(H.clusters(self.PTS[2:3]))
        self.assertEqual(len(boxes), 1)
        lat_ne, lon_ne, lat_sw, lon_sw = boxes[0]
        self.assertTrue(lat_ne > 38.04 > lat_sw and lon_ne > -121.78 > lon_sw)
        self.assertAlmostEqual((lat_ne - lat_sw) * 111.2, 30, delta=0.5, msg="15 km of padding each side")

    def test_spot_points_cover_curated_and_rider_spots(self):
        d = tempfile.mkdtemp()
        rider = os.path.join(d, "rider-stations.json")
        json.dump({"k-far": {"name": "Far", "lat": 39.4, "lon": -123.3, "stations": []}, "crissy": {"name": "dup", "lat": 1, "lon": 2, "stations": []}}, open(rider, "w"))
        pts = H.spot_points(rider_path=rider)
        ids = [p["id"] for p in pts]
        self.assertEqual(ids.count("crissy"), 1, "a curated id in rider-stations.json is not doubled")
        self.assertIn("k-far", ids)
        self.assertEqual(len(pts), 28, "27 curated spots plus the rider spot")


class Netatmo(unittest.TestCase):
    ANSWER = {"body": [
        {"_id": "70:ee:50:00:00:01", "place": {"location": [-122.46412, 37.87299], "city": "Belvedere", "country": "US"},
         "measures": {"02:00:00:00:00:01": {"res": {"1700000000": [12.3, 60]}, "type": ["temperature", "humidity"]},
                      "06:00:00:00:00:01": {"wind_strength": 20, "wind_angle": 240, "gust_strength": 33, "gust_angle": 250, "wind_timeutc": 1793569200}}},
        {"_id": "70:ee:50:00:00:02", "place": {"location": [-122.5, 37.9]}, "measures": {"02:x": {"res": {}, "type": ["temperature"]}}},   # no wind gauge
        {"_id": "70:ee:50:00:00:03", "place": {"location": [-122.5, 37.9]}, "measures": {"06:x": {"wind_strength": 999, "wind_angle": 1, "wind_timeutc": 1793569200}}},   # 999 km/h
        {"_id": "70:ee:50:00:00:04", "place": {}, "measures": {"06:x": {"wind_strength": 5, "wind_angle": 1}}},   # no location
    ]}

    def test_parse(self):
        got = H.parse_netatmo(json.dumps(self.ANSWER), NOW)
        self.assertEqual(list(got), ["70:ee:50:00:00:01"], "only the device with a wind gauge and a sane reading")
        s = got["70:ee:50:00:00:01"]
        self.assertEqual((s["lat"], s["lon"], s["place"], s["dir"]), (37.873, -122.464, "Belvedere", 240), "position rounded to 3 decimals, city as the place")
        self.assertAlmostEqual(s["spd"], 10.8, 1, "20 km/h -> 10.8 kn")
        self.assertAlmostEqual(s["gst"], 17.8, 1)
        self.assertEqual(s["time"], dt.datetime.fromtimestamp(1793569200, dt.timezone.utc))

    def test_token_and_rotation(self):
        calls = []

        def post(url, data=None, headers=None):
            calls.append((url, data, headers))
            return json.dumps({"access_token": "acc", "refresh_token": "rt2", "expires_in": 10800})
        self.assertEqual(H.netatmo_token("id", "sec", "rt1", post=post), ("acc", "rt2"))
        self.assertEqual(calls[0][1]["grant_type"], "refresh_token")
        self.assertEqual(calls[0][1]["refresh_token"], "rt1")

    def test_fetch_uses_the_stored_token_and_stores_the_rotated_one(self):
        store = {"netatmo_refresh_token": "rt-stored"}

        class Vars:
            def get(self, k): return store.get(k)
            def put(self, k, v): store[k] = v
        seen = []

        def getter(url, data=None, headers=None):
            seen.append((url, data))
            if url == H.NETATMO_TOKEN_URL:
                return json.dumps({"access_token": "acc", "refresh_token": "rt-new"})
            self.assertEqual(headers["Authorization"], "Bearer acc")
            return json.dumps(self.ANSWER)
        env = {"NETATMO_CLIENT_ID": "i", "NETATMO_CLIENT_SECRET": "s", "NETATMO_REFRESH_TOKEN": "rt-secret"}
        boxes = H.netatmo_boxes(H.clusters(Areas.PTS[:2]))
        got = H.fetch_netatmo(boxes, NOW, env=env, getter=getter, store=Vars(), log=quiet)
        self.assertEqual(list(got), ["70:ee:50:00:00:01"])
        self.assertEqual(seen[0][1]["refresh_token"], "rt-stored", "the Worker's stored token wins over the repository secret")
        self.assertEqual(store["netatmo_refresh_token"], "rt-new", "the rotated token is stored for the next run")
        self.assertEqual(len(seen), 2, "one token call and one public-data call per box")
        self.assertEqual(H.fetch_netatmo(boxes, NOW, env={}, getter=getter, store=None, log=quiet), {}, "no secrets: skipped silently")


class Catalogue(unittest.TestCase):
    def test_update_never_drops_and_keeps_first_seen(self):
        cat = {"stations": {"OLD1": {"id": "OLD1", "kind": "cwop", "lat": 38.0, "lon": -122.0, "firstSeen": "2026-09-01T00:00:00Z", "lastSeen": "2026-09-01T00:00:00Z"}}}
        found = {"CW1234": {"call": "CW1234", "lat": 37.917, "lon": -122.478, "spd": 10, "time": NOW},
                 "NOPOS": {"call": "NOPOS", "lat": None, "lon": None, "spd": 10, "time": NOW}}
        self.assertEqual(H.update_catalogue(cat, found, "cwop", NOW), 1)
        self.assertIn("OLD1", cat["stations"], "a station not heard this run stays documented")
        self.assertNotIn("NOPOS", cat["stations"], "a positionless station we have never placed waits for a positioned packet")
        e = cat["stations"]["CW1234"]
        self.assertEqual((e["firstSeen"], e["lastSeen"], e["kind"]), (H.iso_utc(NOW), H.iso_utc(NOW), "cwop"))
        later = NOW + dt.timedelta(hours=2)
        H.update_catalogue(cat, {"CW1234": {"call": "CW1234", "lat": 37.918, "lon": -122.479, "spd": 11, "time": later}}, "cwop", later)
        self.assertEqual((e["firstSeen"], e["lastSeen"], e["lat"]), (H.iso_utc(NOW), H.iso_utc(later), 37.918), "first seen is kept, last seen and position move")
        H.update_catalogue(cat, {"NOPOS": {"call": "NOPOS", "lat": 38.1, "lon": -122.1, "spd": 10, "time": later}}, "cwop", later)
        H.update_catalogue(cat, {"NOPOS": {"call": "NOPOS", "lat": None, "lon": None, "spd": 10, "time": later}}, "cwop", later)
        self.assertEqual(cat["stations"]["NOPOS"]["lat"], 38.1, "once placed, positionless updates keep the position")
        d = tempfile.mkdtemp()
        path = os.path.join(d, "home-stations.json")
        H.save_catalogue(path, cat)
        self.assertEqual(H.load_catalogue(path), {"stations": dict(sorted(cat["stations"].items()))})
        self.assertEqual(H.load_catalogue(os.path.join(d, "missing.json")), {"stations": {}})

    def test_names(self):
        self.assertEqual(H.station_name({"id": "WB6TTB", "kind": "cwop", "place": "Tiburon"}), "Tiburon home station (CWOP WB6TTB)")
        self.assertEqual(H.station_name({"id": "CW1234", "kind": "cwop"}), "Home station (CWOP CW1234)")
        self.assertEqual(H.station_name({"id": "70:ee", "kind": "netatmo", "place": "Belvedere"}), "Home station (Netatmo) · Belvedere")
        self.assertEqual(H.station_name({"id": "70:ee", "kind": "netatmo"}), "Home station (Netatmo)")


def cat_near_pc():
    """Four CWOP stations north of Paradise Cay at 0, 5.7, 9.8 and 12 mi, one Netatmo at 0.1 mi."""
    st = {"A1": (37.917, -122.478), "B6": (38.0, -122.478), "C10": (38.058, -122.478), "D12": (38.09, -122.478)}
    cat = {"stations": {k: {"id": k, "kind": "cwop", "lat": v[0], "lon": v[1], "firstSeen": "x", "lastSeen": "x"} for k, v in st.items()}}
    cat["stations"]["70:ee:50:00:00:01"] = {"id": "70:ee:50:00:00:01", "kind": "netatmo", "lat": 37.918, "lon": -122.479, "place": "Belvedere", "firstSeen": "x", "lastSeen": "x"}
    return cat


class Attach(unittest.TestCase):
    PC = [{"id": "paradisecay", "name": "Paradise Cay", "lat": 37.9168, "lon": -122.4785}]

    def test_nearest_three_within_ten_miles_with_trust(self):
        cat = cat_near_pc()
        t = NOW - dt.timedelta(minutes=20)
        rd = lambda spd: {"spd": spd, "gst": spd + 3, "dir": 250, "time": t}   # noqa: E731
        readings = {k: rd(10 + i) for i, k in enumerate(["A1", "B6", "C10", "D12", "70:ee:50:00:00:01"])}
        trust = {"A1": {"trusted": True}, "D12": {"trusted": True}}
        home = H.attach(self.PC, cat, readings, trust, NOW)
        rows = home["paradisecay"]
        self.assertEqual([r["id"] for r in rows], ["A1", "70:ee:50:00:00:01", "B6"], "nearest three within 10 mi (C10 at 9.8 mi is fourth, D12 beyond)")
        self.assertEqual([r["trusted"] for r in rows], [True, False, False])
        a = rows[0]
        self.assertEqual((a["class"], a["kind"], a["name"], a["dist_mi"], a["age_min"], a["spd"], a["gst"], a["dir"], a["time"]),
                         ("home", "cwop", "Home station (CWOP A1)", 0.0, 20, 10, 13, 250, H.iso_utc(t)))
        self.assertEqual(rows[1]["name"], "Home station (Netatmo) · Belvedere")
        self.assertEqual(H.attach(self.PC, cat, {"C10": rd(5)}, {}, NOW)["paradisecay"][0]["dist_mi"], 9.8, "within 10 mi counts")
        self.assertEqual(H.attach(self.PC, cat, {"D12": rd(5)}, {}, NOW), {}, "a station without a reading this run, or beyond 10 mi, gives no row")

    def test_merge_rows_tags_classes_and_replaces_old_home_rows(self):
        obs = {"fetchedAt": "2026-10-27T21:40:00+00:00", "obs": {
            "paradisecay": [{"id": "RCMC1", "name": "Richmond", "kind": "coops", "dist_mi": 4.4, "spd": 9.0},
                            {"id": "OLDHOME", "name": "x", "kind": "cwop", "class": "home", "dist_mi": 1.0, "spd": 1.0}],
            "crissy": [{"id": "FTPC1", "name": "Fort Point", "kind": "coops", "class": "reliable", "dist_mi": 0.6, "spd": 12.0}]}}
        home = {"paradisecay": [{"id": "A1", "name": "Home station (CWOP A1)", "kind": "cwop", "class": "home", "dist_mi": 0.0, "spd": 10}],
                "k-new": [{"id": "A1", "name": "Home station (CWOP A1)", "kind": "cwop", "class": "home", "dist_mi": 2.0, "spd": 10}]}
        doc = H.merge_rows(obs, home)
        self.assertEqual(doc["fetchedAt"], obs["fetchedAt"])
        self.assertEqual([(r["id"], r["class"]) for r in doc["obs"]["paradisecay"]], [("A1", "home"), ("RCMC1", "reliable")], "sorted by distance, the public row tagged reliable, last run's home row replaced")
        self.assertEqual([(r["id"], r["class"]) for r in doc["obs"]["crissy"]], [("FTPC1", "reliable")])
        self.assertEqual([r["id"] for r in doc["obs"]["k-new"]], ["A1"], "a spot with only home rows still gets an entry")


class Run(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.obs = os.path.join(self.dir, "obs.json")
        self.cat = os.path.join(self.dir, "home-stations.json")
        self.trust = os.path.join(self.dir, "home-trust.json")
        json.dump({"fetchedAt": H.iso_utc(NOW), "obs": {"paradisecay": [{"id": "RCMC1", "name": "Richmond", "kind": "coops", "dist_mi": 4.4, "time": H.iso_utc(NOW), "spd": 9.0, "gst": 11.0, "dir": 250, "age_min": 5}]}}, open(self.obs, "w"))
        json.dump({"A1": {"trusted": True, "n": 50}}, open(self.trust, "w"))

    def test_live_run_writes_catalogue_and_home_rows(self):
        t = NOW - dt.timedelta(minutes=10)
        cwop = lambda filt, cat, now: {"A1": {"call": "A1", "lat": 37.917, "lon": -122.478, "dir": 250, "spd": 10.0, "gst": 13.0, "time": t}}   # noqa: E731
        netatmo = lambda boxes, cat, now: {"70:ee:50:00:00:01": {"call": "70:ee:50:00:00:01", "lat": 37.918, "lon": -122.479, "place": "Belvedere", "dir": 240, "spd": 8.0, "gst": None, "time": t}}   # noqa: E731
        home = H.run(self.obs, self.cat, self.trust, now=NOW, points=Attach.PC, cwop=cwop, netatmo=netatmo, log=quiet)
        self.assertEqual([r["id"] for r in home["paradisecay"]], ["A1", "70:ee:50:00:00:01"])
        cat = H.load_catalogue(self.cat)
        self.assertEqual(set(cat["stations"]), {"A1", "70:ee:50:00:00:01"})
        self.assertEqual(cat["stations"]["70:ee:50:00:00:01"]["place"], "Belvedere")
        doc = json.load(open(self.obs))
        rows = doc["obs"]["paradisecay"]
        self.assertEqual([(r["id"], r["class"], r.get("trusted")) for r in rows], [("A1", "home", True), ("70:ee:50:00:00:01", "home", False), ("RCMC1", "reliable", None)])
        self.assertEqual(doc["fetchedAt"], H.iso_utc(NOW), "fetchedAt untouched")
        # next run: nothing heard — the catalogue keeps both, obs.json carries no home rows
        H.run(self.obs, self.cat, self.trust, now=NOW + dt.timedelta(hours=1), points=Attach.PC, cwop=lambda *a: {}, netatmo=lambda *a: {}, log=quiet)
        self.assertEqual(set(H.load_catalogue(self.cat)["stations"]), {"A1", "70:ee:50:00:00:01"}, "never dropped")
        self.assertEqual([r["class"] for r in json.load(open(self.obs))["obs"]["paradisecay"]], ["reliable"])

    def test_a_failing_feed_is_skipped_never_fatal(self):
        def boom(*a):
            raise OSError("no route")
        t = NOW - dt.timedelta(minutes=10)
        netatmo = lambda boxes, cat, now: {"70:ee:50:00:00:01": {"call": "70:ee:50:00:00:01", "lat": 37.918, "lon": -122.479, "dir": 240, "spd": 8.0, "gst": None, "time": t}}   # noqa: E731
        home = H.run(self.obs, self.cat, self.trust, now=NOW, points=Attach.PC, cwop=boom, netatmo=netatmo, log=quiet)
        self.assertEqual([r["id"] for r in home["paradisecay"]], ["70:ee:50:00:00:01"], "Netatmo rows still land when CWOP fails")
        home = H.run(self.obs, self.cat, self.trust, now=NOW, points=Attach.PC, cwop=boom, netatmo=boom, log=quiet)
        self.assertEqual(home, {})
        self.assertEqual([r["class"] for r in json.load(open(self.obs))["obs"]["paradisecay"]], ["reliable"], "obs.json still valid, rows tagged")

    def test_findu_fallback_only_for_catalogued_callsigns(self):
        H.save_catalogue(self.cat, {"stations": {"A1": {"id": "A1", "kind": "cwop", "lat": 37.917, "lon": -122.478, "firstSeen": "x", "lastSeen": "x"},
                                                 "70:ee:50:00:00:01": {"id": "70:ee:50:00:00:01", "kind": "netatmo", "lat": 37.918, "lon": -122.479, "firstSeen": "x", "lastSeen": "x"}}})
        urls = []

        def listen(filt, now=None):
            raise ConnectionRefusedError("down")

        def getter(url, data=None, headers=None):
            urls.append(url)
            return "<html><body><pre>A1>APRS,TCPIP*,qAS,FINDU:@272120z" + POS1 + "250/011g015t061r000<br>A1>APRS:!" + POS1 + "250/020g030t061</pre></body></html>"
        found, source = H.fetch_cwop("r/37.9/-122.5/30", H.load_catalogue(self.cat), NOW, listen=listen, getter=getter, log=quiet)
        self.assertEqual(source, "findu")
        self.assertEqual(urls, [H.findu_url("A1")], "one findu page per catalogued CWOP callsign, never for Netatmo ids or unknown calls")
        self.assertEqual((found["A1"]["dir"], found["A1"]["time"].minute), (250, 20), "the stamped packet; the unstamped one is dropped")
        ok = lambda filt, now=None: ["A1>APRS:@272130z" + POS1 + "225/012g018t061"]   # noqa: E731
        found, source = H.fetch_cwop("r/", H.load_catalogue(self.cat), NOW, listen=ok, getter=getter, log=quiet)
        self.assertEqual((source, len(urls)), ("aprs-is", 1), "with the socket up, findu is never asked")

    def test_listen_sends_the_readonly_login_and_reads_until_the_deadline(self):
        sent = []

        class Sock:
            def __init__(self): self.chunks = [b"# aprsc\r\n# logresp N0CALL unverified\r\nA1>APRS:@272130z" + POS1.encode() + b"225/012g018t061\r\n", b""]
            def sendall(self, b): sent.append(b)
            def settimeout(self, t): pass
            def recv(self, n): return self.chunks.pop(0)
            def close(self): pass
        lines = H.aprs_listen("r/37.9/-122.5/30", seconds=1, now=NOW, connect=lambda addr, timeout: Sock())
        self.assertEqual(sent, [b"user N0CALL pass -1 vers WindwardMark 1.0 filter r/37.9/-122.5/30\r\n"], "receive-only login, never a passcode")
        self.assertEqual(len(lines), 3)
        self.assertEqual(len(H.collect_aprs(lines, NOW)), 1)

    def test_cli_exits_zero_without_an_obs_file(self):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "home_stations.py"), os.path.join(self.dir, "missing.json")], capture_output=True, text=True, timeout=60,
                           env={**os.environ, "CWOP_LISTEN_S": "1"})
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
