# Windward Mark — Bay Area edition (handoff for Claude Code)

This repository is a snapshot of Bistué Boarding (coastal-kiteboarding) to be turned into **Windward Mark**, the same app for Mark, who lives in Paradise Cay (Tiburon, CA) and often rides from Candlestick Point in San Francisco. Keep every feature; change the data and the identity. German's app lives in a different repository and is not affected by anything here.

## Identity
- App, tab and home-screen name: **Windward Mark**. Short name: **Windward**.
- Repo and URL: `windward-mark` → https://mikestoneapps.github.io/windward-mark/ (a custom domain may come later).
- Icons: replace `icon-512.png` / `icon-192.png` with `icon-512-windward.png` / `icon-192-windward.png` (then delete the -windward copies). Theme colour can stay Harbor teal.
- Heading inside the app: "Windward Mark". Card/README/SPEC/CLAUDE.md: Bay Area edition, rider Mark, no mention of German, Oregon, Gorge, Lake Oswego, Pacific City or Bay City except in a one-line "derived from" note.

## Homes (replace both)
- `LO` → **Paradise Cay** (Tiburon): 37.9180, -122.4820. Keep the internal key `LO` and field `driveLO` so saved settings keep working; only the label and coordinates change.
- `BC` → **Candlestick Point**: 37.7107, -122.3850. Keep key `BC` / `driveBC`.
- Away mode's "far from both houses" threshold (AWAY_MI) stays.

## Spots
- Replace `spots.json` and the embedded `SPOTS` in `index.html` with `bay-spots.json` (16 spots). Map its fields: `driveHome` → `driveLO`, `driveSF` → `driveBC`. Keep `tideStation`, `waves`, `pass`, `dir`, `notes`, `parking`, `plat/plon` as they are. Spot ids are final.
- Region labels used: "SF Bay", "Peninsula", "East Bay", "Delta", "North Bay", "Ocean". Anywhere the page or alerts text says "the Gorge" / "the coast" by region, generalise: Delta spots are "the Delta", Ocean spots "the coast", everything else "the Bay".
- Remove the Gorge NBM preference: no spot gets `model: "nbm"` by default. (Bay thermals may want it later; the accuracy log will say.)
- Photos: move `img-bay/*.jpg` and `img-bay/credits.json` to `img/`, delete the old Oregon photos. Missing photos (coyote, sherman, windycove, baypoint, stinson, bodega, waddell, hmb, oceanbeach, davenport may be missing) show the neutral tile by design.
- Regenerate `stations.json` with `stations.py` for the new spots (NWS stations + NDBC buoys; 46026 SF Bar, 46012 Half Moon Bay, 46013 Bodega, 46237 SF Bay entrance, 46042 Monterey are the relevant buoys). If the sandbox cannot reach NOAA, write stations.json from the NWS station list you can infer and note it in docs/BUILD-PLAN.md for a live check.
- Reset generated data that is Oregon-specific: `obs.json`, `obs-recent.json`, `accuracy.jsonl`, `bias.json` → empty/initial structures so the first hourly run starts clean. Keep `away-spots.json` (worldwide; still valid).

## Worker and jobs
- `sync/wrangler.toml`: name `windward-mark`; KV id and VAPID public key will be filled in later by Mike's chat session (leave placeholders). `ALLOWED_ORIGINS` stays `https://mikestoneapps.github.io,...`.
- Alerts text: house names come from HOMES, so they follow automatically; check alerts/lib.mjs and tests for hard-coded "Lake Oswego"/"Pacific City" and replace with the new names.
- Workflows unchanged.

## Tests
- All existing suites must pass after the change (alerts parity, away, worker, python tests). Update fixtures that name Oregon spots or houses.
- Headless browser test at 390 px: home mode with Paradise Cay selected shows 16 Bay spots sorted by score; Candlestick selected shows drive times from there; a Delta spot and an Ocean spot open without errors.

## Docs
- Rewrite CLAUDE.md "What this is" and the README for Windward Mark; SPEC §1 and §4 for the new rider and spots; docs/BUILD-PLAN.md gets a "Bay edition" note with the open questions (Mark's quiver, weight, favourite spots; Rio Vista launch status; Candlestick suitability).
- Delete this file once applied.
