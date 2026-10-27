# Claude Code prompt — Windward Mark: 27 spots, real sensors, test notification

Repo: **mikestoneapps/windward-mark** (pick this repo explicitly; not coastal-kiteboarding). One PR, branch off `main`. Read CLAUDE.md, SPEC.md and `docs/research/STATUS.md`, `docs/research/sensor-catalogue.md`, `docs/research/stations-proposed.json`, `docs/research/networks.md` first. Keep the live page working at every commit; run `node alerts/test.mjs`, `python3 test_accuracy.py test_bias.py test_obs_recent.py` and `node away/test.mjs` before pushing.

## 1. Apply the 27-spot list
- Replace `spots.json` and the embedded `const SPOTS` in `index.html` with the spots in `bay-spots.json` (27, including the new home spot `paradisecay`). Keep the schema from SPEC.md §4; never rename an existing id. Regions: add "Monterey Bay", "Tahoe", "South Bay" to whatever region filter exists. Lakes (Tahoe, Folsom, Granite Bay) have `tideStation: null` and must not show a tide line. Delete `bay-spots.json` once applied. Photos: use the six already in `img/`; everything else gets the neutral tile.

## 2. Station observations: fix routing and add the free feeds
The current `stations.json` was hand-typed and most Bay stations return nothing. Replace it with `docs/research/stations-proposed.json` (already in the right shape, sorted by distance, with a new `kind` per feed) and teach `obs_standalone.py` / `stations.py` to read every kind. All are free, token-free, and verified live on 2026-10-26; cadence and field notes are in `networks.md` (appendix table) and each row's `how`.

| kind | read from | notes |
|---|---|---|
| `nws` | `https://api.weather.gov/stations/{id}/observations/latest` (User-Agent header required) | airports only (KSFO, KOAK, KSQL, KHAF, KOAR, KMRY, KSTS, KCCR, KMHR, KTRK). windSpeed/windGust are km/h → knots. |
| `coops` | `https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=wind&station={nos7}&date=latest&units=english&time_zone=gmt&format=json` | NOS PORTS/NWLON stations: FTPC1, AAMC1, RCMC1, PXOC1, RTYC1, LNDC1, OKXC1, PPXC1, OMHC1, PSBC1, PCOC1. Speed/gust already knots. Map the 5-char id to its 7-digit NOS id (listed in each row's `how`); fall back to `https://www.ndbc.noaa.gov/data/realtime2/{id}.txt` if CO-OPS fails. 6-minute cadence, gusts included — this is the Bay backbone. |
| `ndbc` | `https://www.ndbc.noaa.gov/data/realtime2/{id}.txt` (or one fetch of `data/latest_obs/latest_obs.txt` for all) | buoys 46026, 46013, 46012 (Saildrone-style, may be missing), 46042, 46092. m/s → knots. |
| `raws` | `https://mesonet.agron.iastate.edu/api/1/obhistory.json?station={id}&network=CA_DCP&date=YYYY-MM-DD` (Tahoe ids use `NV_DCP`) | RAWS hourly; SHEF keys USIRGZZ speed, UDIRGZZ dir, UPHRGZZ gust, values **mph**. Ids: MDEC1, BBEC1, HSPC1, BNDC1, LAHC1, XCDC1, KNXN2, LVYN2, HMDC1. Fallback: USFS FEMS CSV (URL in networks.md). |
| `iem` | same IEM obhistory endpoint, network `CA_DCP` | GOES/HADS stations GGBC1 (Golden Gate Bridge deck — reads high) and PRWC1 (Point Reyes). |
| `cencoos` | ERDDAP tabledap, dataset id = row id, e.g. `https://erddap.cencoos.org/erddap/tabledap/{id}.json?time,wind_speed,wind_gust,wind_from_direction&orderByMax("time")` — confirm variable names from each dataset's `.das` | bodega-marine-laboratory-weather, santa-cruz-wharf-weather-stat(ion), monterey-bay-aquarium-weather, MLSC1 (Moss Landing). m/s → knots. |
| `cdec` | `https://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet?Stations={id}&SensorNums=9,10,77&dur_code=E&Start=…&End=…` | FLD (Folsom, live), RVB (Rio Vista; Delta CDEC stations sometimes return -9999 → treat as missing). mph → knots. |
| `caltrans` | `https://cwwp2.dot.ca.gov/data/d3/rwis/rwisStatusD03.json` (CF105/CF106 are District 3; D1 file for the north coast) | one file per district, pick the station by id; decode ESS wind units per networks.md. |
| `jpl` | `https://laketahoe.jpl.nasa.gov/getweather` (HTML, hourly at :30) | Tahoe buoys TB1, TB4: parse "min:avg:max" m/s → knots. |
| `cdip` | `https://cdip.ucsd.edu/data_access/justdar.cdip?{n}+pm` (n = 142, 156, 029) | **wave only** (`wave_only: true`): Hs m → ft, Tp, Dp. Never a wind sample; feed the swell line only. |

Rules: every kind returns the same row shape `{id,name,kind,dist_mi,time,spd,gst,dir,wvht_ft,age_min}` in knots; a kind that fails is skipped, never fatal; one request per station per run (NDBC asks for minimal retrieval); total run stays under ~90 requests. `age_min > 90` ⇒ not "fresh" (so stale MADIS/CWOP copies, which lagged four days, must never enter the catalogue — they are deliberately excluded from stations-proposed.json; keep them out of `stations.py` auto-resolution too). Do **not** add Synoptic, WeatherFlow/iKitesurf, Weather Underground, Holfuy or Windy feeds: their terms forbid it (details in networks.md §5).

Also:
- `stations.py` auto-resolution: 35 mi radius for Delta, Ocean, Monterey Bay and Tahoe spots (25 mi elsewhere), exclude non-airport NWS ids (CWOP/MADIS), and add a `.github/workflows/resolve-stations.yml` (workflow_dispatch) that runs `python3 stations.py --resolve` live on GitHub and commits `stations.json` — but seed from stations-proposed.json so a resolve run only *adds*, never drops a hand-verified row.
- Paradise Cay has no live sensor within 5 mi (TIBC1 stale since Sept, the dock PWS is view-only): list RCMC1 (4 mi), FTPC1 (8 mi) and PXOC1 and let the UI say "nearest reading 4 mi away".
- The "Blowing now" alert (`alerts/lib.mjs blowingNow()`) and `accuracy.py` consume `obs-recent.json`/`obs.json` unchanged — verify with the tests that the new kinds flow through, and that wave-only rows are never treated as wind.
- Per-spot "Live" line in the tile: show the nearest fresh wind row with its distance and a link to the sensor's public page (CO-OPS, NDBC, IEM, ERDDAP, JPL). For the view-only sensors riders use (iKitesurf Berkeley Reef 175511, Pittsburg Marina 100721, Crissy/Anita Rock, Sherman #12/#14; WU KCABELVE30 at the Paradise Cay dock), add an optional `links` array on the spot with name+URL and render them as plain links under the Live line — no fetching.

## 3. "Send test notification"
In the Rider sheet under Alerts, add a button **Send test notification**. It sets `settings.alerts.testRequested = <ISO now>` and syncs. In `alerts/run.mjs`, for each rider whose settings carry `testRequested` newer than the last `testSent`, send one push ("Windward Mark test — alerts are working", opens the app on today) then clear the flag server-side (write `testSent`). The button shows "Requested — arrives within the hour (job runs hourly)" and disables itself for an hour. Add a rule test in `alerts/test.mjs`. (Hourly is fine; Mike knows the job cadence.)

## 4. Docs
Update `docs/BUILD-PLAN.md` "Bay edition" section: what changed, the new kinds, and open questions (Paradise Cay dock sectors from Mark; whether Rio Vista and Marina are spots he rides; Albany Bulb parking). Update CLAUDE.md's `stations.json` and `obs_standalone.py` lines to describe the new kinds. Keep STATUS.md current.

Open the PR against `main` with a description of the four parts and the test output.
