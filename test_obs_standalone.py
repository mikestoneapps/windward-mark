#!/usr/bin/env python3
"""Offline tests for obs_standalone.py: one canned payload per feed kind (shapes from the live probes in
docs/research/networks.md, 2026-10-26), the shared row shape, the wave-only rule and the one-request-per-
station rule. `python3 test_obs_standalone.py`."""
import datetime as dt
import json
import os
import tempfile
import unittest

import obs_standalone as O

NOW = dt.datetime(2026, 10, 27, 0, 30, tzinfo=dt.timezone.utc)


class TestParsers(unittest.TestCase):
    def test_nws(self):
        payload = json.dumps({"properties": {"timestamp": "2026-10-27T00:15:00+00:00",
                                             "windSpeed": {"value": 18.52}, "windGust": {"value": 27.78}, "windDirection": {"value": 290}}})
        o = O.parse_nws(payload, NOW)
        self.assertEqual((o["spd"], o["gst"], o["dir"], o["age_min"]), (10.0, 15.0, 290, 15), "km/h -> knots")

    def test_coops(self):
        payload = json.dumps({"data": [{"t": "2026-10-27 00:24", "s": "9.72", "d": "258.0", "dr": "WSW", "g": "18.66", "f": "0,0"}]})
        o = O.parse_coops(payload, NOW.replace(hour=0, minute=30))
        self.assertEqual((o["spd"], o["gst"], o["dir"]), (9.7, 18.7, 258.0), "CO-OPS english units are knots already")
        self.assertEqual(o["time"], "2026-10-27T00:24:00Z", "time_zone=gmt timestamps read as UTC")
        self.assertIsNone(O.parse_coops(json.dumps({"data": [{"t": "2026-10-27 00:24", "s": ""}]}), NOW), "an empty speed is no reading")

    def test_ndbc(self):
        txt = ("#YY  MM DD hh mm WDIR WSPD GST  WVHT   DPD   APD MWD   PRES  ATMP  WTMP  DEWP  VIS PTDY  TIDE\n"
               "#yr  mo dy hr mn degT m/s  m/s     m   sec   sec degT   hPa  degC  degC  degC  nmi  hPa    ft\n"
               "2026 10 27 00 10 300  5.0  7.0   1.5    11   9.1 285 1015.1  14.0  13.5  11.1  MM +0.1    MM\n")
        o = O.parse_ndbc(txt, NOW)
        self.assertEqual((o["spd"], o["gst"], o["dir"], o["wvht_ft"]), (9.7, 13.6, 300.0, 4.9), "m/s -> knots, m -> ft")

    def test_iem_raws(self):
        payload = json.dumps({"data": [
            {"utc_valid": "2026-10-26T22:00:00Z", "USIRGZZ": 10.0, "UDIRGZZ": 280, "UPHRGZZ": 16.0},
            {"utc_valid": "2026-10-26T23:00:00Z", "USIRGZZ": None},
            {"utc_valid": "2026-10-26T23:00:00Z", "USIRGZZ": 11.5, "UDIRGZZ": 290, "UPVRGZZ": 18.4},
        ]})
        o = O.parse_iem(payload, NOW)
        self.assertEqual((o["spd"], o["gst"], o["dir"]), (10.0, 16.0, 290), "latest row with a speed wins; mph -> knots; UPVRGZZ accepted as the peak")
        self.assertEqual(o["age_min"], 90, "hourly RAWS decode ages off utc_valid")

    def test_cencoos(self):
        payload = json.dumps({"table": {"columnNames": ["time", "wind_speed", "wind_from_direction", "wind_speed_of_gust"],
                                        "columnTypes": ["String", "float", "float", "float"],
                                        "rows": [["2026-10-27T00:10:00Z", 7.72, 295.0, 10.29]]}})
        o = O.parse_cencoos(payload, {"spd": "wind_speed", "dir": "wind_from_direction", "gst": "wind_speed_of_gust"}, NOW)
        self.assertEqual((o["spd"], o["gst"], o["dir"], o["age_min"]), (15.0, 20.0, 295.0, 20), "ERDDAP m/s -> knots")

    def test_cdec(self):
        rows = [{"stationId": "FLD", "SENSOR_NUM": 9, "date": "2026-10-26 16:14", "value": 8.0},
                {"stationId": "FLD", "SENSOR_NUM": 10, "date": "2026-10-26 16:14", "value": 169.0},
                {"stationId": "FLD", "SENSOR_NUM": 9, "date": "2026-10-26 17:14", "value": -9999.0}]
        o = O.parse_cdec(json.dumps(rows), NOW)
        self.assertEqual((o["spd"], o["dir"], o["gst"]), (7.0, 169.0, None), "mph -> knots; a -9999 row (Delta CDEC) is missing, not zero")
        self.assertEqual(o["time"], "2026-10-26T23:14:00Z", "CDEC timestamps are California local time")

    def test_caltrans(self):
        site = {"location": {"locationName": "SR-12 - SR-160 (Rio Vista Bridge)"},
                "recordTimestamp": {"recordDate": "2026-10-26", "recordTime": "17:14:00"},
                "windData": {"essAvgWindSpeed": "109", "essMaxWindGustSpeed": "164", "essAvgWindDirection": "250"}}
        payload = json.dumps({"data": [{"rwis": site}]})
        o = O.parse_caltrans(payload, ["sr 12", "sr 160"], NOW)
        self.assertEqual((o["spd"], o["gst"], o["dir"]), (21.2, 31.9, 250.0), "ESS tenths of m/s -> knots")
        bad = json.dumps({"data": [{"rwis": {**site, "windData": {"essAvgWindSpeed": "65535"}}}]})
        self.assertIsNone(O.parse_caltrans(bad, ["sr 12", "sr 160"], NOW), "65535 is the ESS missing sentinel")
        self.assertIsNone(O.parse_caltrans(payload, ["sr 12", "brannan"], NOW), "a site that doesn't match the words is not picked")

    def test_jpl(self):
        html = ("<table><tr><th>Measurement</th><th>TB1</th><th>TB2</th><th>TB3</th><th>TB4</th></tr>"
                "<tr><td>Wind Speed (m/s)</td><td>2.0:4.0:6.0</td><td>-99</td><td>1:2:3</td><td>3.0:5.0:8.0</td></tr>"
                "<tr><td>Wind Direction (deg)</td><td>200:210:220</td><td>-99</td><td>0:0:0</td><td>190:205:220</td></tr></table>")
        o = O.parse_jpl(html, "TB1", NOW)
        self.assertEqual((o["spd"], o["gst"], o["dir"]), (7.8, 11.7, 210), '"min:avg:max" m/s: avg is the wind, max the gust')
        o4 = O.parse_jpl(html, "TB4", NOW)
        self.assertEqual((o4["spd"], o4["gst"]), (9.7, 15.6), "each buoy reads its own column")
        self.assertIsNone(O.parse_jpl(html, "TB2", NOW), "-99 = missing")
        self.assertEqual(o["time"], "2026-10-26T23:00:00Z", "stamped at the top of the previous hour (what the page shows)")

    def test_cdip_wave_only(self):
        txt = "Station 142p1 San Francisco Bar\n00:00 10/27/2026  Hs(m): 1.52  Tp(s): 11.76  Dp(deg): 285\n"
        o = O.parse_cdip(txt, NOW)
        self.assertEqual((o["wvht_ft"], o["dpd"], o["mwd"]), (5.0, 11.76, 285))
        self.assertTrue(o["spd"] is None and o["gst"] is None and o["dir"] is None, "a CDIP row is never a wind sample")


class TestFetchLoop(unittest.TestCase):
    def test_one_request_per_station_and_row_shape(self):
        stations = {
            "crissy": [{"id": "FTPC1", "name": "Fort Point", "kind": "coops", "dist_mi": 0.6, "nos": "9414290"},
                       {"id": "46026", "name": "SF buoy", "kind": "ndbc", "dist_mi": 21.3}],
            "oceanbeach": [{"id": "FTPC1", "name": "Fort Point", "kind": "coops", "dist_mi": 3.4, "nos": "9414290"},
                           {"id": "46237", "name": "SF Bar CDIP 142", "kind": "cdip", "dist_mi": 6.7, "cdip": "142", "wave_only": True}],
        }
        calls = []

        def getter(url):
            calls.append(url)
            if "tidesandcurrents" in url:
                return json.dumps({"data": [{"t": "2026-10-27 00:24", "s": "9.72", "d": "258.0", "g": "18.66"}]})
            if "realtime2" in url:
                return ("#hdr\n#hdr\n2026 10 27 00 10 300  5.0  7.0   1.5    11   9.1 285 1015.1  14.0  13.5  11.1  MM +0.1    MM\n")
            if "justdar" in url:
                return "00:00 10/27/2026  Hs(m): 1.52  Tp(s): 11.76  Dp(deg): 285\n"
            raise AssertionError("unexpected url " + url)

        with tempfile.TemporaryDirectory() as td:
            out_path = os.path.join(td, "obs.json")
            out = O.fetch_obs(stations, now=NOW, getter=getter, out_file=out_path)
            doc = json.load(open(out_path))
        self.assertEqual(len([c for c in calls if "tidesandcurrents" in c]), 1, "FTPC1 fetched once for both spots")
        self.assertEqual(len(calls), 3, "three stations, three requests")
        self.assertEqual([r["id"] for r in out["oceanbeach"]], ["FTPC1", "46237"])
        for rows in out.values():
            for r in rows:
                self.assertTrue({"id", "name", "kind", "dist_mi", "time", "spd", "age_min"} <= set(r), "the shared row shape")
        wave = out["oceanbeach"][1]
        self.assertTrue(wave["wave_only"] and wave["spd"] is None and wave["wvht_ft"] == 5.0, "wave-only row: swell line only, never wind")
        self.assertEqual(doc["obs"]["crissy"][0]["spd"], 9.7, "obs.json carries the same rows")

    def test_a_failing_kind_is_skipped_never_fatal(self):
        stations = {"crissy": [{"id": "FTPC1", "name": "Fort Point", "kind": "coops", "dist_mi": 0.6, "nos": "9414290"},
                               {"id": "GGBC1", "name": "Golden Gate Bridge", "kind": "iem", "dist_mi": 1.7, "network": "CA_DCP"}]}

        def getter(url):
            raise OSError("network down")

        with tempfile.TemporaryDirectory() as td:
            out = O.fetch_obs(stations, now=NOW, getter=getter, out_file=os.path.join(td, "obs.json"))
        self.assertEqual(out, {"crissy": []}, "every station failing still writes an (empty) obs.json")

    def test_catalogue_covers_every_spot_and_kinds_are_known(self):
        here = os.path.dirname(os.path.abspath(__file__))
        stations = json.load(open(os.path.join(here, "stations.json")))
        spots = json.load(open(os.path.join(here, "spots.json")))
        kinds = {"nws", "coops", "ndbc", "raws", "iem", "cencoos", "cdec", "caltrans", "jpl", "cdip"}
        for s in spots:
            self.assertIn(s["id"], stations, s["id"] + " has a station list")
        for sid, rows in stations.items():
            self.assertEqual([r["dist_mi"] for r in rows], sorted(r["dist_mi"] for r in rows), sid + " sorted by distance")
            for r in rows:
                self.assertIn(r["kind"], kinds, f"{sid}/{r['id']}: known kind")
                if r["kind"] == "coops":
                    self.assertRegex(r["nos"], r"^\d{7}$", f"{sid}/{r['id']}: CO-OPS rows carry the 7-digit NOS id")
                if r["kind"] == "cdip":
                    self.assertTrue(r.get("wave_only"), f"{sid}/{r['id']}: CDIP is wave-only by definition")
        total = len({r["id"] for rows in stations.values() for r in rows})
        self.assertLess(total, 80, f"{total} unique stations: one request each stays well under ~90 a run")


if __name__ == "__main__":
    unittest.main()
