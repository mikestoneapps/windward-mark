# Windward Mark

**Windward Mark** — where to kite today: San Francisco Bay, the Delta or the ocean coast, scored 0–10 and ranked by drive time. The Bay Area edition for Mark, derived from Bistué Boarding (coastal-kiteboarding).

Live: https://mikestoneapps.github.io/windward-mark/
On an iPhone: open the link in Safari → Share → **Add to Home Screen**.

- Forecasts: Open-Meteo, five models in one call (best match, ECMWF, NBM, GFS, ICON) + marine model, seven days (the last two a trend), fetched on every open. The score runs on the hourly median of best match, ECMWF and NBM over that day's sunrise-to-sunset hours; all five vote on confidence. Knots by default, mph under Rider.
- Tides: NOAA CO-OPS predictions for the nearest tide station, drawn under each spot's hourly chart (display only; the lakes carry none).
- Live wind: a hand-verified catalogue of free public sensors per spot — NOAA CO-OPS 6-minute stations and airports fetched by the page itself, plus NDBC buoys, RAWS/IEM, CeNCOOS ERDDAP, CDEC, Caltrans and the JPL Tahoe buoys via the hourly job (CDIP wave buoys feed the swell line only).
- Scoring, spot rules, alerts and roadmap: see `SPEC.md` and `docs/BUILD-PLAN.md`.
- For Claude Code: read `CLAUDE.md` first.

Photos are CC-licensed from Wikimedia Commons; credits in `img/credits.json`.
