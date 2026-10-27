#!/usr/bin/env python3
"""Offline tests for rider_stations.py:  python3 test_rider_stations.py

Checks: kept spots read off the admin answer (only id/name/lat/lon, nothing about the rider), the station
mix per spot (catalogue within 15 mi, airports 25/35 mi, buoys 45 mi, 3 wind rows + 1 wave row), the
re-resolve-only-on-coordinate-change rule, pruning spots nobody keeps, curated ids skipped, and that a
resolve failure leaves the spot for the next run instead of caching a half answer."""
import json
import os
import tempfile
import unittest

import rider_stations as RS

# A small catalogue standing in for stations.json: two coops near the Bay point, one far, one wave-only CDIP.
CAT_STATIONS = {
    "crissy": [
        {"id": "FTPC1", "name": "San Francisco (Fort Point)", "kind": "coops", "lat": 37.8067, "lon": -122.465, "dist_mi": 0.6, "nos": "9414290"},
        {"id": "PXOC1", "name": "San Francisco Pier 1", "kind": "coops", "lat": 37.798, "lon": -122.393, "dist_mi": 3.3, "nos": "9414311"},
        {"id": "46237", "name": "San Francisco Bar CDIP 142", "kind": "cdip", "lat": 37.788, "lon": -122.634, "dist_mi": 6.7, "wave_only": True, "cdip": "142"},
    ],
    "sherman": [
        {"id": "PSBC1", "name": "Pittsburg (Suisun Bay)", "kind": "coops", "lat": 38.0416, "lon": -121.8867, "dist_mi": 4.4, "nos": "9415115"},
    ],
}
NEAR = {"lat": 37.81, "lon": -122.47}   # by the Golden Gate: FTPC1 and PXOC1 within 15 mi, PSBC1 not

RIDERS = [{"id": "a" * 64,
           "settings": {"kept": [
               {"id": "k-gate", "name": "Gate Beach", "lat": NEAR["lat"], "lon": NEAR["lon"], "waves": True, "addedAt": "x"},
               {"id": "k-nowhere", "name": "Dry Lake", "lat": 40.0, "lon": -119.0},
               {"id": "crissy", "name": "Crissy again", "lat": 37.8057, "lon": -122.4535},   # curated id: skipped
               {"id": "k-bad"},   # no coordinates: ignored
           ]},
           "subs": [{"endpoint": "https://push.example/secret"}], "state": {"alerted": {}}}]

AIRPORTS_NEAR = [{"id": "KSFO", "name": "San Francisco Intl", "kind": "nws", "lat": 37.6196, "lon": -122.3656, "dist_mi": 14.3}]
AIRPORTS_FAR_ONLY = [{"id": "KRNO", "name": "Reno", "kind": "nws", "lat": 39.5, "lon": -119.77, "dist_mi": 33.0}]
BUOY = [{"id": "46026", "name": "San Francisco buoy", "kind": "ndbc", "lat": 37.754, "lon": -122.839, "dist_mi": 20.5}]


class KeptSpots(unittest.TestCase):
    def test_extraction(self):
        kept = RS.kept_spots(RIDERS)
        self.assertEqual(set(kept), {"k-gate", "k-nowhere", "crissy"}, "rows without id or coordinates are ignored")
        self.assertEqual(kept["k-gate"], {"name": "Gate Beach", "lat": NEAR["lat"], "lon": NEAR["lon"], "waves": True},
                         "only name, coordinates and the waves flag survive — nothing about the rider")
        self.assertEqual(RS.kept_spots(None), {})
        self.assertEqual(RS.kept_spots([{"settings": None}, "junk"]), {})


class ResolveSpot(unittest.TestCase):
    def setUp(self):
        self.cat = RS.catalogue_rows(CAT_STATIONS)

    def test_mix_and_cap(self):
        rows = RS.resolve_spot({**NEAR, "waves": True}, self.cat, airports=AIRPORTS_NEAR, buoys=BUOY)
        ids = [r["id"] for r in rows]
        self.assertEqual(ids, ["FTPC1", "PXOC1", "46237", "KSFO"], "3 wind rows (nearest catalogue rows, then the airport) plus the wave row, sorted by distance")
        self.assertTrue(all(r["dist_mi"] == round(RS.ST.mi(NEAR["lat"], NEAR["lon"], r["lat"], r["lon"]), 1) for r in rows),
                        "dist_mi recomputed from the spot's own coordinates")

    def test_no_wave_row_without_waves(self):
        ids = [r["id"] for r in RS.resolve_spot({**NEAR, "waves": False}, self.cat, airports=[], buoys=[])]
        self.assertEqual(ids, ["FTPC1", "PXOC1"], "no wave row for a flat-water spot; PSBC1 is beyond 15 mi")

    def test_airports_widen_to_35(self):
        rows = RS.resolve_spot({"lat": 40.0, "lon": -119.0, "waves": False}, self.cat, airports=AIRPORTS_FAR_ONLY, buoys=[])
        self.assertEqual([r["id"] for r in rows], ["KRNO"], "nothing within 25 mi: the 35 mi search's airports are used")
        near = RS.resolve_spot({**NEAR, "waves": False}, self.cat, airports=AIRPORTS_NEAR + AIRPORTS_FAR_ONLY, buoys=[])
        self.assertNotIn("KRNO", [r["id"] for r in near], "with an airport within 25 mi, the farther ones are not")


class Run(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.cache = os.path.join(self.dir, "rider-stations.json")

    def read(self):
        with open(self.cache, encoding="utf-8") as fh:
            return json.load(fh)

    def resolver(self, calls):
        def f(spot, cat):
            calls.append(spot["name"])
            if spot["name"] == "Dry Lake":
                return []
            return RS.resolve_spot(spot, cat, airports=AIRPORTS_NEAR, buoys=BUOY)
        return f

    def test_resolve_cache_and_idempotence(self):
        calls = []
        cache, resolved, dropped = RS.run(RIDERS, self.cache, stations=CAT_STATIONS, resolver=self.resolver(calls))
        self.assertEqual((resolved, dropped, sorted(cache)), (2, 0, ["k-gate", "k-nowhere"]), "both rider spots resolved; the curated id skipped")
        self.assertEqual(sorted(calls), ["Dry Lake", "Gate Beach"])
        doc = self.read()
        self.assertEqual(set(doc["k-gate"]), {"name", "lat", "lon", "stations"}, "the file carries spot id, name, lat, lon and stations — nothing else")
        self.assertNotIn("secret", json.dumps(doc), "no rider identifiers or endpoints in the file")
        self.assertEqual(doc["k-nowhere"]["stations"], [], "a spot with nothing in range is cached empty, not retried hourly")
        # second run: same coordinates, nothing re-resolved
        calls.clear()
        _, resolved, _ = RS.run(RIDERS, self.cache, stations=CAT_STATIONS, resolver=self.resolver(calls))
        self.assertEqual((resolved, calls), (0, []), "idempotent: nothing re-resolved while the coordinates stand")
        # the spot moves: re-resolved; a spot nobody keeps any more is dropped
        moved = json.loads(json.dumps(RIDERS))
        moved[0]["settings"]["kept"] = [dict(moved[0]["settings"]["kept"][0], lat=37.9)]
        cache, resolved, dropped = RS.run(moved, self.cache, stations=CAT_STATIONS, resolver=self.resolver(calls))
        self.assertEqual((resolved, dropped, sorted(cache)), (1, 1, ["k-gate"]), "moved spot re-resolved; the dropped spot pruned")
        self.assertEqual(self.read()["k-gate"]["lat"], 37.9)

    def test_failure_leaves_the_spot_for_next_run(self):
        def boom(spot, cat):
            raise RuntimeError("api down")
        cache, resolved, _ = RS.run(RIDERS, self.cache, stations=CAT_STATIONS, resolver=boom)
        self.assertEqual((resolved, cache), (0, {}), "a failed resolve caches nothing, so the next run tries again")
        self.assertFalse(os.path.exists(self.cache), "nothing changed, nothing written")


if __name__ == "__main__":
    unittest.main(verbosity=2)
