# Real-time wind sensor networks, Northern California (Eureka to Monterey) + Lake Tahoe, as of 2026-10-26

Scope: every public/semi-public network of real-time wind sensors in the region, and how a free hourly GitHub Actions job (Python) or a browser page can read each. Live checks below were run on 2026-10-26 ~23:00–00:30 UTC from a cloud container (curl / urllib). Where a claim comes from a live probe rather than a published document it is marked **[live probe 2026-10-26]**; treat those as point-in-time evidence.

Bounding box used for station counts: lat 36.4–41.2, lon −124.6 to −121.0, plus Tahoe lat 38.85–39.35, lon −120.25 to −119.85.

## Compact per-network summary (essentials; detail and citations in the sections below)

| Network | Coverage here | Free + token-free live data? | Feed for a Python urllib job | Cadence | CORS | ToS caveats |
|---|---|---|---|---|---|---|
| **NOS CO-OPS met** (NOAA) | 21 CA met stations Humboldt→Monterey; Bay piers: FTPC1/9414290 Crissy, AAMC1/9414750 Alameda, RTYC1/9414523 Redwood City, RCMC1/9414863 Richmond, PSBC1/9415115 Pittsburg, PCOC1/9415144, PRYC1/9415020 Pt Reyes, MTYC1/9413450 Monterey | **Yes** | `https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=wind&station=9414290&date=latest&units=english&time_zone=gmt&format=json` (s, g in kn, d); station list `…/mdapi/prod/webapi/stations.json?type=met` | 6 min | `*` (browser OK) | US Gov open data; Pier 17 (9414296/PXSC1) and Berth 38 (9414797/OBXC1) have no anemometer |
| **NDBC** buoys/C-MAN + same NOS stations | Buoys 46012/13/14/22/26/42/92; all `xxxxC1` NOS ids above | **Yes** | `https://www.ndbc.noaa.gov/data/realtime2/FTPC1.txt` (6-min rows WDIR WSPD GST m/s); all-in-one `https://www.ndbc.noaa.gov/data/latest_obs/latest_obs.txt` | buoys hourly (~:25), NOS 6 min | **none** (server-side only) | "keep retrievals minimal"; latest_obs.txt is undocumented |
| **api.weather.gov** (ASOS/AWOS + MADIS mirror) | 44 airports (KSFO, KOAK, KHAF, KSQL, KPAO, KMRY, KACV, KTVL, KTRK…), NOS stations, + 2,400 MADIS mesonet ids | **Yes** (User-Agent header required) | `https://api.weather.gov/stations/KHAF/observations/latest`; list `…/stations?state=CA,NV&limit=500` (cursor paging); `…/points/{lat},{lon}` → observationStations; header `Feature-Flags: obs_station_provider` reveals network | ASOS 20–60 min; NOS 6 min; MADIS nominal ~20 min but **all MADIS stations were 4.5 days stale at probe** | `*` | Open data; rate limit unpublished; 7-day retention; wind in km/h |
| **Synoptic / MesoWest** | Aggregates PG&E, Caltrans, RAWS, CWOP, CDEC/HADS, UCNRS, CW3E, Liberty, NV Energy, Tempest | **No** — token required; free "Open Access" is .edu-only (application, 1 concurrent request, attribution, internal use only); others 14-day trial then quote | `https://api.synopticdata.com/v2/stations/latest?token=…&stid=…&vars=wind_speed,wind_gust,wind_direction` | per network (5–60 min) | untested | T&C: "internal purposes" only, public map needs written consent, restricted networks not redistributable |
| **CWOP/APRS via MADIS** | ~1,225 CWOP ids in bbox (D3499 Foster City, D9579 Alameda, G3010 Candlestick, G0254 Incline…) | Yes, only through api.weather.gov (above) — MADIS itself needs registration | same as api.weather.gov; provider tag `APRSWXNET` | 5–15 min at source; stale at probe | `*` | backyard siting, unknown heights; staleness risk |
| **RAWS** (interagency fire wx) | Hundreds (MDEC1 Middle Peak/Mt Tam, BBEC1, SBMC1…; ridge sites) | **Yes** via USFS FEMS; also CDEC mirrors and api.weather.gov (`provider: RAWS`) | `https://fems.fs2c.usda.gov/api/climatology/download-weather?stationIds=<RAWS id>&dataFormat=csv&dataset=observation&dataIncrement=hourly&startDate=…Z&endDate=…Z&fuelModels=Y&fuelMoisture=Y&stationStatus=A&timeZone=America/Los_Angeles` (WindSpeed mph, WindAzimuth, GustSpeed, GustAzimuth). IEM `obhistory` (`https://mesonet.agron.iastate.edu/request/asos/…` / `/sites/obhistory.php?station=…&network=CA_RAWS`) was **not probed**—unverified | hourly | FEMS echoes Origin (works in browser) | FEMS station-id scheme and ToS unverified; raws.dri.edu is HTML only |
| **CDEC** (CA DWR) | 206 active wind stations in bbox: Delta/Bay tide-met MAL Mallard Is., ANH Antioch, RVB Rio Vista, GZL, FRK, MRZ Martinez, BBY Bodega; many RAWS mirrors | **Yes** | `https://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet?Stations=MAL,ANH,RVB&SensorNums=9,10,77&dur_code=E&Start=2026-10-26&End=2026-10-27` (9=WIND SP mph, 10=DIR, 77=PEAK mph; missing = −9999 / `---`) | 15 min (E) / hourly (H) | **none** | no published ToS/limits; timestamp TZ unconfirmed |
| **CIMIS** (ag ET stations) | Inland valleys, 2 m masts | Free but needs registered appKey | `https://et.water.ca.gov/api/data?appKey=…&targets=<station>&startDate=…&endDate=…&dataItems=hly-wind-spd` (from wrapper docs; not probed) | hourly | unknown | not shoreline; low value for kiting |
| **Caltrans RWIS** | Districts 1 (North Coast), 3 (Tahoe/Sac: Hwy 28 Dollar Point lakeshore, Hwy 89 Rampart, Brockway Summit, Donner, Echo Summit); **no District 4 (Bay Area) file** | **Yes** ("no charge") | `https://cwwp2.dot.ca.gov/data/d3/rwis/rwisStatusD03.json` (and `d1`); `windData.essAvgWindSpeed/essSpotWindSpeed/essMaxWindGustSpeed` + directions | file rewritten every minute; check `recordTimestamp` | `*` | NTCIP ESS units (tenths m/s; 0/1/65535 sentinels) need decoding; Conditions of Use page not read |
| **PG&E mesonet** | 435 `nnnPG`/`PGnnn` sites in bbox (ridge/pole fire-weather: 229PG Last Chance Rd near Waddell, 514PG Ridgecrest near Stinson, 519PG Bridgehead near Sherman Is.) | Only via api.weather.gov MADIS mirror (stale at probe) or Synoptic (token) | api.weather.gov as above; provider `MesoWest/PGE` | 10 min at source | `*` | PG&E offers no download; 1–2 min avg, 3–5 s gusts |
| **BAAQMD** | Air-district met sites | No live feed found; only CEQA/AERMOD archives | — | — | — | gap |
| **WeatherFlow Tempest / iKitesurf–SailFlow** | The kite-specific sensors (Crissy Anita Rock, 3rd Ave, Coyote, Sherman Is., GGB towers) | **No** — API limited to stations you own; iKitesurf Plus/Pro/Gold subscription for "more stations incl. exclusive Pro stations" | none legitimate | 1–5 min | — | Commercial terms forbid making data "publicly accessible"; redisplaying = ToS breach; link out instead |
| **Weather Underground PWS** | Dense PWS map | **No** — keys only for active PWS uploaders; page scraping un-licensed | `https://api.weather.com/v2/pws/observations/current?stationId=…&format=json&units=e&apiKey=…` (owner key) | 5 min | — | owner-only key; "Data Expired" after 60 min |
| **CeNCOOS ERDDAP** | Hosts GGBC1 Golden Gate mid-span record (NWS-attributed, CC0) | Yes, keyless | `https://erddap.cencoos.org/erddap/tabledap/gov_noaa_nws_ggbc1.json?…` — but dataset maxTime is **2012-12-31**; live GGBC1 is in api.weather.gov (provider MesoWest/MTRWFO, elev 82 m, speed+gust+dir) | n/a (archive) | ERDDAP normally `*` (not probed) | CC0; not live |
| **Lake Tahoe — JPL/UC Davis TERC** | 4 NASA/JPL–UCD buoys TB1–TB4 mid-lake; TERC also runs 6 land met stations | **Yes** (HTML scrape) | `https://laketahoe.jpl.nasa.gov/getweather` (table; wind as `min:avg:max` m/s from previous hour's last 30 min; −99 = missing) | hourly at :30 | **none** | raw, unQC'd, "not for scientific studies"; no API |
| **Tahoe others** | Caltrans D3 Dollar Point (free, CORS); NV Energy NV028, Liberty LIB04, CWOP G0254 via MADIS; airports KTVL/KTRK (ASOS) | mixed (see rows) | as above | — | — | no ski-area summit feed found |

**Ranking for a free hourly job:** CO-OPS → NDBC → api.weather.gov (ASOS+NOS) → CDEC → Caltrans D1/D3 → FEMS RAWS → JPL Tahoe → api.weather.gov MADIS (free but unreliable). **Unusable without paying/owning:** Synoptic (non-.edu), Tempest/iKitesurf, WU, Holfuy, Ambient/Netatmo, Windfinder/Windy.

---

## Key Question 1: Which networks exist here, what do they carry, and how is each read (endpoints, access terms, CORS, licence, caveats)?

### Takeaway
Three sources give free, keyless, CORS-enabled, shore-level wind with gusts at 6-minute cadence in the Bay: NOAA CO-OPS (`api.tidesandcurrents.noaa.gov`, product=wind), NDBC `realtime2` (no CORS, server-side only), and api.weather.gov for ASOS airports and the same NOS stations. Everything else (RAWS, CWOP, PG&E, Caltrans, UC reserves, NV Energy, Liberty) is aggregated by Synoptic (token required; no free hobby tier any more) and mirrored into api.weather.gov via MADIS, where it was stale by 4+ days at probe time. Commercial sensor networks (WeatherFlow/iKitesurf, WU, Tempest, Holfuy, Windfinder) are either owner-only APIs or subscription-walled; CDEC, Caltrans RWIS and FEMS (RAWS) are the under-appreciated free feeds.

### Cited Findings

#### 1. NOAA NDBC — buoys, C-MAN, and NOS/CO-OPS PORTS stations relayed through NDBC
- Real-time file pattern is `https://www.ndbc.noaa.gov/data/realtime2/<STATION>.<type>`; `.txt` = standard met, `.cwind` = continuous winds; other types `.spec`, `.ocean`, `.tide`, etc. C-MAN/land stations use uppercase 5-character ids. The realtime2 directory holds the last 45 days. NDBC asks users to "keep retrievals to a minimal level", prefers HTTPS over FTP, and says most stations report hourly with data available ~25 min after the hour — [NDBC Real Time Data Access FAQ](https://www.ndbc.noaa.gov/faq/rt_data_access.shtml)
- All-station snapshot file `https://www.ndbc.noaa.gov/data/latest_obs/latest_obs.txt` (820 lines, columns `#STN LAT LON YYYY MM DD hh mm WDIR WSPD GST WVHT ... TIDE`, wind in m/s) — **[live probe 2026-10-26]**; the FAQ page does not document this file, so treat it as a de-facto, not published, interface.
- NOS/CO-OPS PORTS stations in the region that were reporting WDIR/WSPD in `latest_obs.txt` at probe time: **AAMC1** (Alameda), **FTPC1** (SF / Crissy, 37.806 −122.466), **LNDC1** (Oakland Berth 67), **OKXC1** (Oakland Berth 34), **OMHC1** (Oakland Middle Harbor), **PCOC1** (Port Chicago), **PPXC1** (Pt Potrero Richmond), **PSBC1** (Pittsburg), **PXOC1** (SF Pier 1), **RCMC1** (Richmond), **RTYC1** (Redwood City), **SFXC1** (Davis Point), **UPBC1** (UP RR bridge), **MZXC1** (Martinez), **ANVC1** (Arena Cove), **ELXC1** (Elkhorn Slough), **MLSC1** (Moss Landing). Showing `MM` (missing) for wind at probe time: **OBXC1** (Oakland Berth 38 visibility), **PXSC1** (SF Pier 17 visibility), **PRYC1** (Point Reyes), **MEYC1** (Monterey), **HBXC1**, **HBYC1** (Humboldt), **TDPC1** (Trinidad), **BDXC1** (Bodega) and CDIP wave buoys 46214/46236/46237/46244 — **[live probe 2026-10-26]**
- NDBC station pages list anemometer heights: FTPC1 7.4 m, AAMC1 6.9 m, RTYC1 7.6 m, PSBC1 7.6 m, PRYC1 8.7 m, MEYC1 8.4 m, MTYC1 8.5 m, buoy 46026 4.1 m; **OBXC1 and PXSC1 list no anemometer** (visibility sensors only), so the `MM` for those two is permanent, not an outage — [NDBC station pages, e.g. FTPC1](https://www.ndbc.noaa.gov/station_page.php?station=ftpc1) **[live probe 2026-10-26]**
- `realtime2/FTPC1.txt` carries 6-minute rows (23:48, 23:42, …) with WDIR, WSPD and GST; `FTPC1.cwind` returns 404 (NOS stations have no separate cwind file); `46026.cwind` exists — **[live probe 2026-10-26]**
- Buoys with wind in region at probe time: 46012 (Half Moon Bay), 46013 (Bodega), 46014 (Pt Arena), 46022 (Eel River), 46026 (SF Bar), 46042 (Monterey), 46092 (MBARI M1). **[live probe 2026-10-26]**
- CORS: `realtime2/FTPC1.txt` returned no `Access-Control-Allow-Origin` header → browser pages cannot read NDBC directly; fetch server-side (matches the existing CLAUDE.md note) — **[live probe 2026-10-26]**
- Licence: US Government work; NWS API doc states its data "is intended to be open data, free to use for any purpose" — [NWS API docs](https://www.weather.gov/documentation/services-web-api)

#### 2. NOAA CO-OPS Data API (the same NOS stations, better interface)
- `https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=wind&station=9414290&date=latest&units=english&time_zone=gmt&format=json` returned `{"t":"2026-10-27 00:24","s":"9.72","d":"258.0","dr":"WSW","g":"18.66","f":"0,0"}` (speed and gust in knots with `units=english`) with `access-control-allow-origin: *` — no key, **browser-callable** — **[live probe 2026-10-26]**
- Station metadata `https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?type=met` lists the NorCal met stations: 9413450 Monterey, 9414290 San Francisco (FTPC1), 9414296 Pier 17 Visibility, 9414311 SF Pier 1, 9414523 Redwood City, 9414750 Alameda, 9414763 Oakland Berth 67, 9414769 Oakland Middle Harbor, 9414776 Oakland Berth 34, 9414797 Oakland Berth 38 Visibility, 9414847 Pt Potrero Richmond, 9414863 Richmond, 9415020 Point Reyes, 9415102 Martinez-Amorco, 9415115 Pittsburg, 9415118 UP RR Bridge, 9415141 Davis Point, 9415144 Port Chicago, 9416841 Arena Cove, 9418767 North Spit, 9418768 North Jetty Landing Humboldt — **[live probe 2026-10-26]**

#### 3. api.weather.gov (NWS/FAA ASOS/AWOS + everything MADIS ingests)
- No key; a `User-Agent` header identifying the app (ideally with contact email) is required and "will be replaced with an API key in the future"; rate limit exists but "is not public information"; only 7 days of observations retained; "Most stations are not maintained by the NWS, except the ASOS stations"; MADIS ingest adds ~20 min latency; wind-gust null bug fixed 2 Oct 2025 — [NWS API docs](https://www.weather.gov/documentation/services-web-api)
- Endpoints: `/stations?state=CA,NV&limit=500` (cursor-paginated), `/stations/{id}/observations/latest`, `/stations/{id}/observations?limit=N`, `/points/{lat},{lon}` → `observationStations` URL (`/gridpoints/MTR/83,107/stations` for Crissy) — [NWS API docs](https://www.weather.gov/documentation/services-web-api) and **[live probe 2026-10-26]**
- Feature flag header `Feature-Flags: obs_station_provider` adds `provider`/`subProvider` to `/stations/{id}` — [NWS API docs](https://www.weather.gov/documentation/services-web-api). Probe results: GGBC1 = MesoWest/MTRWFO, 514PG = MesoWest/PGE, D3499 = APRSWXNET (CWOP), BBYCA = MAP/PSD (NOAA PSL), UCBM = MesoWest/DRI, C3BBY = MesoWest/CW3E, LIB04 = MesoWest/LIBERTY (Liberty Utilities, Tahoe), NV028 = MesoWest/NV-ENERGY, CF048 = MesoWest/CALTRANS, KTVL = ASOS-HFM, AAMC1 = MARITIME, SFOC1 = HADS, MDEC1 = RAWS — **[live probe 2026-10-26]**
- CORS: `access-control-allow-origin: *` on `/stations/KSFO/observations/latest`; `cache-control: public, max-age=82, s-maxage=300` — **browser-callable** — **[live probe 2026-10-26]**
- Station census in the bbox (8,621 CA+NV stations paged; 2,441 in bbox): 1,225 CWOP-style ids, 435 PG&E (`nnnPG`/`PGnnn`), 44 ICAO airports, ~728 other (HADS/CDEC `xxxxC1`, RAWS, VEIA/ALERTWildfire, LIBnn, NTCS/NTCHB, etc.) — **[live probe 2026-10-26]**
- ICAO airports in bbox: KACV, KAPC, KAUN, KBAB, KCCR, KCIC, KCVH, KDVO, KDWA, KEDU, KFOT, KGOO, KHAF, KHWD, KLHM, KLLR, KLVK, KMCC, KMHR, KMRY, KMYV, KNUQ, KOAK, KOAR, KOVE, KPAO, KRBL, KRDD, KRHV, KSAC, KSCK, KSFO, KSJC, KSMF, KSNS, KSQL, KSTS, KSUU, KTCY, KTRK, KTVL, KUKI, KVCB, KWVI — **[live probe 2026-10-26]**
- **Critical caveat:** at probe time every MADIS-sourced non-NWS station returned a last observation of 2026-10-22 ~13:20Z (GGBC1, NV028, 229PG, 514PG, 604PG, LIB04, UCBM, D3499, G0254, AX472, BBYCA, C3BBY), i.e. ~4.5 days stale, while ASOS (KSFO, KHAF, KTVL) and NOS (AAMC1, FTPC1) were current. Several MADIS stations also returned `windSpeed: null` with a non-null `windGust` (possible field mapping issue). Some listed ids 404 on `/observations/latest` (SIDC1, CF048, A4539, ITLC1, SBMC1, NSPO) — **[live probe 2026-10-26]**. I found no NWS status post explaining this; it may be a transient outage, but it shows api.weather.gov cannot be the sole path to mesonet data.
- Wind units: `wmoUnit:km_h-1`; gusts present for ASOS and NOS stations — **[live probe 2026-10-26]**

#### 4. CWOP / APRS citizen stations
- In api.weather.gov they appear as `APRSWXNET` provider with ids like `D3499` ("DW3499 Foster City"), `G0254`, `AX472` (ham callsign KM6RDV), `E8284`, etc. Nearest to launches: Third Ave → D3499 (1.7 mi), AX472, AV354, AU221; Candlestick → G3010 (1.8 mi), AW038; Alameda → D9579 (1.6 mi); Berkeley → A4539 "Berkeley Aquatic Park" (1.0 mi; 404 on latest obs); Kings Beach → G0254 Incline Village (2.8 mi) — **[live probe 2026-10-26]**
- Density: 1,225 CWOP-style ids in the bbox listing — **[live probe 2026-10-26]**
- WeatherFlow says Tempest data already reaches NOAA via the National Mesonet Program (Synoptic), so Tempest owners need not forward to CWOP, and that doing both creates duplicates — [Tempest community, dsj](https://community.tempest.earth/t/cwop-link-for-public-data/2390/9)
- Synoptic exposes CWOP as a network selectable via `network=` short name — [Synoptic Latest docs](https://docs.synopticdata.com/services/latest)

#### 5. RAWS (interagency fire-weather) — via FEMS, Synoptic, CDEC, api.weather.gov
- FEMS (USFS Fire Environment Mapping System) has a public download API at `https://fems.fs2c.usda.gov/api/climatology/download-weather?stationIds=<id>&dataFormat=csv&startDate=…Z&endDate=…Z&dataset=observation&dataIncrement=hourly&fuelModels=Y&fuelMoisture=Y&stationStatus=A&timeZone=America/Los_Angeles`; it returned HTTP 200 with CSV columns `StationName, DateTime, ObservationType, Temperature(F), RelativeHumidity(%), Precipitation(in), WindSpeed(mph), WindAzimuth(degrees), GustSpeed(mph), GustAzimuth(degrees), …` and no key; CORS header echoed the Origin (`access-control-allow-origin: https://x.y`, `allow-credentials: true`) — **[live probe 2026-10-26]**; base URL confirmed by a third-party client ([pkg.go.dev firewx/fems](https://pkg.go.dev/alpineworks.io/firewx/fetch/fems)). Master station list: [FEMS 3.0 RAWS Master Station List](https://www-wfweb.fs2c.usda.gov/page/raws-data) (page content could not be fetched; unverified).
- WRCC/DRI RAWS inventory page: [wrcc.dri.edu raws_inventory](https://wrcc.dri.edu/Monitoring/Stations/raws_inventory.php); CEFA NorCal RAWS list: [cefa.dri.edu raws_ncal](https://cefa.dri.edu/Cefa_Products/RAWS/raws_ncal.php). These are HTML pages (scrape only); no machine API found.
- RAWS near launches (from api.weather.gov listing): MDEC1 "Middle Peak" (Mt Tam, 3.5 mi from Stinson, provider RAWS), SBMC1, BBEC1 Barnaby, LOAC1 etc. — **[live probe 2026-10-26]**. CDEC also mirrors many RAWS (station names with "RAWS"/"(CDF)"/"(USFS)") — see §7.
- Unverified: FEMS station-id scheme (my test id 45713 returned an empty row), FEMS rate limits and ToS.

#### 6. Synoptic Data (ex-MesoWest) — the aggregator
- Latest service: `https://api.synopticdata.com/v2/stations/latest?token=…` with selectors `stid`, `state`, `county`, `cwa`, `network`, `vars=wind_speed,wind_gust,wind_direction`, `radius`, `bbox`, `within`; requests limited to 75,000 stations and must include a selector — [Synoptic Latest docs](https://docs.synopticdata.com/services/latest)
- Networks service `https://api.synopticdata.com/v2/networks?token=…` returns network ids/short names and `TOTAL_RESTRICTED`/`ACTIVE_RESTRICTED` counts ("may see networks that will require an upgraded service account") — [Synoptic Networks docs](https://docs.synopticdata.com/services/networks)
- Limits: Timeseries 100,000 station-hours/request; default concurrency 1; Open Access shares a pool and "performance can vary widely"; spatial and 1-year historical limits apply by tier — [Synoptic API Performance and Limits](https://docs.synopticdata.com/services/api-performance-and-limits)
- **Open Access tier (2026) is academic-only**: requires a `.edu` email, application review, 1 concurrent request, 1 year history, attribution to Synoptic required, renew annually, non-commercial; "networks not covered by the standard Open Access tier" need a custom request — [Synoptic Open Access Program](https://synopticdata.com/pricing/open-access-pricing/) (page last modified 2026-03-27)
- Everyone else: 14-day free trial then commercial quote ("Request a Quote"); no public price list on the pricing pages — [Synoptic pricing](https://synopticdata.com/pricing/), [commercial pricing](https://synopticdata.com/pricing/commercial-pricing/) **[live fetch 2026-10-26; JS-rendered page showed only 'Free Trial / Request a Quote']**
- Historical note: Synoptic launched Open Access in March 2022 as a free public-data service — [BusinessWire 2022](https://www.businesswire.com/news/home/20220315005424/en/Synoptic-Data-PBC-Launches-New-Open-Access-Weather-Data-Service); the 2026 page narrows it to .edu.
- T&C: Public Data Content licence allows display and derivative works but "all usage of Public Data Content is limited to internal purposes unless prior written consent is received"; a non-commercial public map needs Synoptic's written consent plus attribution; Restricted Data Content (private sources, e.g. utility networks) may not be redistributed without approval; any redistribution via "an online page, tool or application" is subject to §6.2/Attachment A item 9 — [Synoptic Terms and Conditions](https://synopticdata.com/tcs/)
- Aggregated networks relevant here (evidence from provider tags seen through api.weather.gov, which gets them via MADIS/MesoWest): PG&E (`PGE`), Caltrans (`CALTRANS`), DRI/UCNRS, CW3E, Liberty Utilities (`LIBERTY`), NV Energy (`NV-ENERGY`), RAWS, CWOP, HADS/CDEC, ALERTWildfire-style VEIA ids — **[live probe 2026-10-26]**; PG&E's own fact sheet points the public to the "Synoptic Weather Viewer" for live/historical PG&E station data — [PG&E CWSP fact sheet](https://www.pge.com/assets/pge/docs/outages-and-safety/outage-preparedness-and-support/cwsp-weather-station-fact-sheet.pdf)
- CORS: not tested (needs token). Synoptic docs do not mention CORS. Gap.

#### 7. California CDEC (cdec.water.ca.gov)
- Keyless CSV/JSON endpoints: `https://cdec.water.ca.gov/dynamicapp/req/CSVDataServlet?Stations=MAL,ANH,RVB&SensorNums=9,10,77&dur_code=E&Start=2026-10-25&End=2026-10-27` and `…/JSONDataServlet?…`. Sensor 9 = WIND SP (MPH), 10 = WIND DR (DEG), 77 = PEAK WS (MPH). `dur_code=E` gave 15-minute rows for Delta/Bay stations (MAL Mallard Island 14 mph/295°, MRZ Martinez 15 mph/267°, ANH Antioch, RVB Rio Vista; BBY Bodega Marine Lab 15 mph/289° at 15:45), `dur_code=H` gave hourly rows incl. gust (BKD Black Diamond Mines 17 mph, peak 25). Missing values are `---` (CSV) / `-9999` (JSON). Headers carried no `Access-Control-Allow-Origin` → server-side only — **[live probe 2026-10-26]**
- Station search for active event-wind stations in the bbox returned 206 stations (mostly RAWS mirrors plus Delta/Bay tide-and-met sites: MAL, ANH, RVB, GZL Grizzly Bay, FRK Franks Tract, BDL Beldon Landing, SRH Hood, MRZ, BBY, TAF Travis) via `https://cdec.water.ca.gov/dynamicapp/staSearch?...sensor=9&dur=E&active=Y&loc_chk=on&lon1=…` — **[live probe 2026-10-26]**
- R wrapper documentation for the same servlet: [cder package](https://cran.r-project.org/web/packages/cder/refman/cder.html)
- Caveat/gap: CDEC time zone of timestamps not confirmed (latest rows were stamped 17:15 on a probe made at ~17:30 PDT, suggesting local PDT, but CDEC documentation was not checked); no published rate limit or ToS found; Sherman Island (SIDC1 in NWS listing) did not appear in the CDEC active-wind search.

#### 8. CIMIS (agricultural ET stations)
- CIMIS has a REST API needing a free `appKey` registered at cimis.water.ca.gov, with hourly data including wind speed; documented by the R wrapper [cimir quick start](https://cran.r-project.org/web/packages/cimir/vignettes/quickstart.html) and the open dataset listing [CIMIS Weather Station Data (data.gov)](https://catalog.data.gov/dataset/cimis-weather-station-data). Stations are agricultural (inland valleys), 2 m anemometers. Not probed; rate limits/CORS unknown.

#### 9. Caltrans RWIS (road weather)
- Caltrans publishes ~150 RWIS units free, "no charge", in CSV/JSON/TXT/XML, updated once a minute, by district: D1 (Eureka/North Coast), D2, D3 (Sacramento/Tahoe), D6, D8, D9, D10. **No District 4 (Bay Area) file is listed**; a D4 URL returned HTTP 500 — [Caltrans CWWP2 RWIS docs](https://cwwp2.dot.ca.gov/documentation/rwis/rwis.htm) and **[live probe 2026-10-26]**
- D3 JSON (`https://cwwp2.dot.ca.gov/data/d3/rwis/rwisStatusD03.json`) returned 17 sites with `windData` (`essAvgWindSpeed`, `essSpotWindSpeed`, `essMaxWindGustSpeed`, directions) and `Access-Control-Allow-Origin: *` → **browser-callable**. Tahoe-relevant sites: Hwy 28 at Dollar Point (39.194, −120.104, lakeshore), Hwy 89 at Rampart, Hwy 267 at Brockway Summit (stale: 2026-10-19), Hwy 267 Truckee Bypass, I-80 Donner Lake/Donner Summit/Truckee Scales/Floriston, Hwy 50 Echo Summit — **[live probe 2026-10-26]**
- Caveat: values follow NTCIP ESS conventions (e.g. Donner Summit `essSpotWindSpeed 109`, `essMaxWindGustSpeed 164`, i.e. tenths of m/s; several sites report 0/1 sentinel values). Unit decoding should be confirmed against the Caltrans "Field description" document linked on the docs page (not fetched). Conditions of Use page not fetched.

#### 10. PG&E weather station network
- PG&E says wind is averaged over 1–2 min and gusts over 3–5 s, and directs the public to the Synoptic Weather Viewer and the NWS Weather and Hazards Data Viewer; no download or API is offered — [PG&E CWSP fact sheet](https://www.pge.com/assets/pge/docs/outages-and-safety/outage-preparedness-and-support/cwsp-weather-station-fact-sheet.pdf)
- 435 PG&E ids in the bbox appear in api.weather.gov (`provider: MesoWest, subProvider: PGE`), e.g. 229PG "Last Chance Road" 1.3 mi from Waddell, 069PG "Ano Nuevo", 514PG "Ridgecrest" 1.4 mi from Stinson, 604PG "Golden Gate Park", 519PG "Bridgehead" 2.4 mi from Sherman Island, 071PG "Pillar Point" — but all were stale (last obs 2026-10-22) at probe time — **[live probe 2026-10-26]**
- Scale: >300 stations installed in 2020 alone — [BusinessWire 2020](https://www.businesswire.com/news/home/20201006005990/en); ridge-top/pole-mounted fire-weather siting, not shoreline.

#### 11. BAAQMD met stations
- BAAQMD publishes CEQA modeling (AERMOD) met datasets, not a live feed — [BAAQMD CEQA Modeling Data](https://www.baaqmd.gov/es-MX/Plans-and-Climate/California-Environmental-Quality-Act-CEQA/CEQA-Tools/CEQA-Modeling-Data). No real-time wind API found. Gap: whether BAAQMD sites are in Synoptic (not verified).

#### 12. WeatherFlow / Tempest / iKitesurf–SailFlow
- iKitesurf (developer WeatherFlow/Tempest) is free to install; paid Plus/Pro/Gold tiers (App Store IAP prices from $3.99–$21.99 monthly-style and $44.99–$179.99 yearly-style) unlock "more weather stations, including exclusive Pro stations", pro forecasts, history — [App Store: iKitesurf](https://apps.apple.com/US/app/id555643284)
- Tempest REST API: WeatherFlow staff (Peter) say "access to the data is restricted to stations you personally own"; reading others' public stations requires Enterprise access; owners get unlimited non-commercial access to their own data; commercial licences start at $100/month; a user reports WeatherFlow removing its public token — [Tempest community thread](https://community.tempest.earth/t/tempest-api-for-all-public-tempest-stations/10155)
- Commercial T&C forbid making "the Data and Software Products publicly accessible", sharing tokens, or using the data as a substantial component of a >$50k/yr product — [Tempest Commercial Terms](https://help.tempest.earth/hc/en-us/articles/214935288-Terms-Conditions-for-Commercial-Services)
- Public sharing: a station set to "Share Publicly" gets a guest-viewable web page; hardware binds to one account — [Tempest help: Share Station Data](https://help.tempest.earth/hc/en-us/articles/115005397948)
- Tempest data flows to NOAA via Synoptic/National Mesonet Program (so Tempest PWS may surface in Synoptic/MADIS rather than CWOP) — [Tempest community, dsj](https://community.tempest.earth/t/cwop-link-for-public-data/2390/9)
- WeatherFlow installed two stations on the Golden Gate Bridge south tower (base and ~746 ft) for the America's Cup, served through DataScope — [Tempest blog](https://tempest.earth/weatherflow-installs-golden-gate-bridge-sensors-to-support-americas-cup/)
- The Crissy "Anita Rock" sensor (WeatherFlow-maintained per the blog's "our sensor repair crew") over-reads in WSW/eddy/fog conditions because it sits just above the Presidio wind shadow; a south-tower cofferdam sensor was removed after the Cup — [Mike Godsey, Tempest blog](https://blog.tempest.earth/?p=34384)

#### 13. Weather Underground PWS
- "Free API keys are only issued to registered and active Weather Underground personal weather station users"; key requested at wunderground.com/member/api-keys; a per-key rate limit exists (unnumbered); integrations poll every 5 min — [Home-Assistant wundergroundpws README](https://github.com/cytech/Home-Assistant-wundergroundpws/blob/master/README.md)
- The PWS current-conditions API returns the latest record within 60 minutes, else "Data Expired"; units e/m/h — [The Weather Company PWS Observations doc](https://developer.weather.com/docs/openapi/pws-observations-current-conditions-2-0)
- Gap: whether an owner's key may query other people's station IDs is not stated in the docs I could read; weather.com ToS text on scraping was not retrieved (search returned only unrelated sites). Treat page scraping as a ToS risk.

#### 14. Ambient Weather Network
- API keys: developer key 3 req/s, individual key 1 req/s — [Ambient Weather FAQ](https://ambientweather.com/faqs/question/view/id/2362/); the API serves the account's own devices (docs at [ambientweather.docs.apiary.io](https://ambientweather.docs.apiary.io/), page is JS-only). Gap: public-station read access not confirmed.

#### 15. Netatmo Weathermap
- `getpublicdata` requires OAuth client id/secret from dev.netatmo.com; a wrapper warns to keep batches under 500 requests to avoid HTTP 429; public-station wind availability not documented there — [netatmo.weather README](https://github.com/dimfalk/netatmo.weather). Netatmo's own guideline page lists a "Rate limit" section (JS-rendered, not readable). Gap: wind exposure and ToS.

#### 16. Holfuy
- "Currently we can generate new API keys only for station admins/owners" and support ignores 3rd-party API questions; endpoints `api.holfuy.com/live/` and `/archive/` — [Holfuy API](https://api.holfuy.com)

#### 17. Windy.com station layer
- Windy accepts user-pushed station data (community threads on reporting WU/Ambient/Tempest/Holfuy data to Windy) — [Windy community](https://community.windy.com/topic/33054/send-your-station-data-to-windy-and-others-from-wunderground-myacurite-davis-weatherlink-weatherflow-tempest-or-ambient-weather/12); no public read API for the station layer was found. Gap.

#### 18. Windfinder
- The Crissy Field report page shows "Report from local weather station" plus nearby stations such as FW2543 San Francisco (a CWOP id), Golden Gate Park, Sausalito (Tide), i.e. it re-displays public CWOP/NOAA feeds; Windfinder sells historical data and has a "For businesses / API" page — [Windfinder report Crissy Field](https://www.windfinder.com/report/crissy_field) **[live fetch 2026-10-26]**. No free read API; scraping is subject to their Terms of use.

#### 19. Lake Tahoe-specific
- NASA/JPL–UC Davis buoys TB1–TB4: HTML table at `https://laketahoe.jpl.nasa.gov/getweather`, updated at :30 past each hour with the previous hour's last 30 min, wind speed as `min:avg:max` (max = gust), raw 2-minute samples, "should not be used for scientific studies"; no CORS header returned — [JPL Lake Tahoe Weather Now](https://laketahoe.jpl.nasa.gov/getweather) **[live fetch 2026-10-26]**
- UC Davis TERC: 6 moored buoys/rafts (wind speed/direction) and 6 land met stations (wind, gusts) in the basin, NRT via the JPL site; no API — [TERC Real-Time Data](https://tahoe.ucdavis.edu/real-time-data)
- api.weather.gov stations near Kings Beach: NV028 West Incline Village (NV Energy, 1.7 mi), G0254 CWOP Incline (2.8 mi), CF048 Caltrans Brockway Summit (3.0 mi), LIB04 "BKY4201-Summit" Liberty Utilities (3.0 mi), KNXN2, NV001; airports KTVL (South Lake) and KTRK (Truckee) are current ASOS — **[live probe 2026-10-26]**
- Caltrans D3 "Hwy 28 at Dollar Point" is the only lakeshore road sensor found — **[live probe 2026-10-26]**
- Gap: ski-area summit sensors (Palisades, Northstar, Heavenly) — no open feed found; LIB04 ids suggest Liberty Utilities fire-weather sites via Synoptic.

#### 20. Yacht clubs and bridges
- Golden Gate Bridge mid-span **GGBC1** is in api.weather.gov (provider MesoWest, subProvider MTRWFO, elev 82 m) with speed, gust and direction; the data.gov/ERDDAP record (NWS-attributed, CC0) only spans 2011–2012 — [data.gov GGBC1](https://catalog.data.gov/dataset/mid-span-golden-gate-bridge-ggbc1) and **[live probe 2026-10-26]**
- St Francis YC, Sausalito YC and Cal Sailing pages linked from Latitude 38 are webcams, not open wind feeds — [Latitude 38 weather links](https://www.latitude38.com/weather). Gap: no open API for StFYC/RYC/SFYC anemometers found; the Bay Bridge sensor was not found in any public listing.

### Inferences
- The Crissy launch is uniquely well instrumented: FTPC1/9414290 sits at 37.806, −122.466 (0.1 mi from the launch), 7.4 m anemometer, 6-min wind+gust, readable keyless from a browser via CO-OPS.
- For Third Ave the only true shore sensors are the WeatherFlow/iKitesurf ones (paywalled); the free fallbacks are RTYC1 (Redwood City, 4 mi S, 7.6 m) and CWOP D3499 Foster City (1.7 mi), the latter subject to MADIS staleness.
- CDEC Delta tide-and-met stations (MAL, ANH, RVB, GZL, FRK) are the free shore-level source for Sherman Island; PSBC1 (Pittsburg) and PCOC1 via CO-OPS are the keyless, CORS-enabled alternative.
- Caltrans D3 is the only free, CORS-enabled feed at Tahoe lakeshore (Dollar Point); JPL buoys need HTML scraping server-side.

### Gaps
- Synoptic commercial price list (JS-only page); whether Synoptic API sets CORS headers.
- Why MADIS-fed stations in api.weather.gov were 4+ days stale on 2026-10-26 (no NWS notice found).
- FEMS station-id scheme, rate limits and terms; Caltrans ESS unit decoding; CDEC timestamp time zone and ToS.
- WU: whether an owner's key may query arbitrary station IDs; weather.com ToS text.
- Ambient/Netatmo public-station read terms; any BAAQMD live feed; ski-area and yacht-club anemometer feeds; Bay Bridge sensor.

---

## Key Question 2: Which networks give kiteboarders the most useful shore-level wind at specific launches, and which are inland airports?

### Takeaway
NOS/CO-OPS stations are the shore-level gold standard where they exist (Crissy, Alameda, Redwood City, Richmond, Pittsburg/Port Chicago); CDEC covers the Delta; Caltrans covers Tahoe's north shore road; everything else near Waddell, Stinson and Kings Beach is a ridge-top PG&E/RAWS/utility site or a CWOP backyard station. Airports (KSFO, KOAK, KHAF, KSQL, KPAO, KTVL, KTRK) are 2–5 miles inland of launches and bias low for sea breeze.

### Cited Findings
- Crissy Field: FTPC1 (0.1 mi), GGBC1 (1.2 mi, 82 m elev), CWOP F2543 (3.2 mi), PG&E 604PG Golden Gate Park (3.3 mi) — **[live probe 2026-10-26]**; WeatherFlow Anita Rock sensor over-reads in WSW eddy/fog — [Godsey](https://blog.tempest.earth/?p=34384)
- Third Ave: CWOP D3499 Foster City 1.7 mi; KSQL airport 3.9 mi; RTYC1 Redwood City (NOS) — **[live probe 2026-10-26]**; locals say the 3rd Ave beach reading matches the channel in NW/WNW, under-reads in W, and is gusty/offshore in SW–S — [bayareakiteboarding forum](https://www.bayareakiteboarding.com/forum/viewtopic.php?p=17818)
- Alameda: AAMC1 (NOS, 1.3 mi, 6.9 m), CWOP D9579 (1.6 mi) — **[live probe 2026-10-26]**
- Sherman Island: NWS listing SIDC1 (1.9 mi, 404 on obs), PG&E 519PG Bridgehead (2.4 mi); CDEC MAL/ANH/RVB 15-min wind; PSBC1 Pittsburg (NOS) — **[live probe 2026-10-26]**
- Waddell: PG&E 229PG Last Chance Road 1.3 mi, 069PG Ano Nuevo 3.6 mi, VEIA856 Chalk Mtn Lookout 4.5 mi — all ridge/fire-weather, all stale via MADIS at probe time — **[live probe 2026-10-26]**
- Stinson: 514PG Ridgecrest 1.4 mi, MDEC1 Middle Peak RAWS 3.5 mi (713 m), 355PG Bolinas Fire Station 3.5 mi — **[live probe 2026-10-26]**
- Kings Beach: NV028 West Incline (NV Energy) 1.7 mi, G0254 CWOP 2.8 mi, CF048 Caltrans Brockway Summit 3.0 mi, LIB04 Liberty summit 3.0 mi; Caltrans Dollar Point lakeshore ~6 mi W — **[live probe 2026-10-26]**
- Bodega: UCBM Bodega Marine Reserve (DRI/UCNRS) 0.6 mi, BBYCA (NOAA PSL) 1.3 mi, C3BBY (CW3E) 1.4 mi, CDEC BBY (15-min) — **[live probe 2026-10-26]**
- Airports in bbox (44 ICAO ids listed above) are ASOS/AWOS "maintained by the NWS" and current; "Data quality can vary by provider" for the rest — [NWS API docs](https://www.weather.gov/documentation/services-web-api)

### Inferences
- Rank for shore-level usefulness: NOS/CO-OPS (6-min, gusts, 7–9 m masts on piers) > CDEC Delta/Bodega (15-min) > Caltrans Dollar Point (1-min, road height) > CWOP backyard stations (height unknown, sheltered) > PG&E/RAWS/utility ridge sites (represent ridge wind, not beach) > airports (inland).

### Gaps
- Exact siting/height of WeatherFlow iKitesurf sensors at Third Ave, Coyote, Sherman Island (paywalled; not documented publicly).

---

## Key Question 3: Which can be read free, legitimately, hourly from a script with no paid plan? Ranked.

### Takeaway
Ranked by legitimacy, coverage and robustness: (1) NOAA CO-OPS API, (2) NDBC realtime2/latest_obs, (3) api.weather.gov ASOS + NOS, (4) CDEC CSV/JSON, (5) Caltrans RWIS D1/D3, (6) FEMS RAWS, (7) JPL Tahoe buoys (HTML scrape), (8) api.weather.gov MADIS mesonet (free but stale/unreliable), (9) CIMIS (free key, inland). Not usable without a paid plan or station ownership: Synoptic (non-.edu), WeatherFlow/Tempest/iKitesurf, WU, Holfuy, Ambient/Netatmo (own-station only), Windfinder/Windy.

### Cited Findings
- CO-OPS: keyless, JSON, CORS `*`, 6-min wind with gust — **[live probe 2026-10-26]**
- NDBC: keyless; "keep retrievals to a minimal level" — [NDBC FAQ](https://www.ndbc.noaa.gov/faq/rt_data_access.shtml)
- api.weather.gov: free "for any purpose", User-Agent required, non-public rate limit — [NWS API docs](https://www.weather.gov/documentation/services-web-api)
- CDEC: keyless servlet, 15-min/hourly — **[live probe 2026-10-26]**; [cder docs](https://cran.r-project.org/web/packages/cder/refman/cder.html)
- Caltrans: "There is no charge for the use of this data", once-a-minute files — [Caltrans RWIS docs](https://cwwp2.dot.ca.gov/documentation/rwis/rwis.htm)
- FEMS: keyless CSV with wind/gust — **[live probe 2026-10-26]**
- JPL buoys: public HTML, hourly — [JPL](https://laketahoe.jpl.nasa.gov/getweather)
- Synoptic: .edu only for free; 14-day trial otherwise — [Open Access](https://synopticdata.com/pricing/open-access-pricing/), [pricing](https://synopticdata.com/pricing/)
- Tempest: own stations only via API — [community](https://community.tempest.earth/t/tempest-api-for-all-public-tempest-stations/10155); WU: owners only — [HA README](https://github.com/cytech/Home-Assistant-wundergroundpws/blob/master/README.md); Holfuy: owners only — [Holfuy API](https://api.holfuy.com)

### Inferences
- An hourly job that pulls `latest_obs.txt` once (one request for all NDBC/NOS stations) plus a handful of CO-OPS, CDEC and Caltrans calls is well inside every stated or implied limit.

### Gaps
- No published numeric rate limits for NDBC, CDEC, Caltrans or FEMS.

---

## Key Question 4: Best aggregator for the region, and what it costs/requires

### Takeaway
Synoptic is the only aggregator carrying PG&E, Caltrans, RAWS, CWOP, CDEC/HADS, utility and Tempest data together, but in 2026 its free tier is restricted to .edu academic projects with attribution, 1 concurrent request and internal-use-only terms; a hobbyist must take a 14-day trial then a commercial quote. The free substitute is api.weather.gov's MADIS mirror, which carries the same stations but was stale at probe time.

### Cited Findings
- Open Access eligibility and limits — [Synoptic Open Access](https://synopticdata.com/pricing/open-access-pricing/)
- Trial/quote only for others — [Synoptic pricing](https://synopticdata.com/pricing/)
- Internal-use and map-consent clauses; Restricted Data no-redistribution — [Synoptic T&C](https://synopticdata.com/tcs/)
- Synoptic feeds NOAA under the National Mesonet Program; NOAA staff get access with a noaa.gov email — [Synoptic pricing](https://synopticdata.com/pricing/)
- api.weather.gov tags MADIS/MesoWest providers (PGE, CALTRANS, DRI, CW3E, LIBERTY, NV-ENERGY, RAWS, APRSWXNET) — **[live probe 2026-10-26]**

### Inferences
- For this app (free-tier rule in CLAUDE.md), Synoptic is out unless Mike qualifies for Open Access through an academic affiliation; even then the "internal purposes" clause conflicts with a public GitHub Pages app.

### Gaps
- Actual commercial price for a single-user, ~50-station hourly feed (quote only).

---

## Key Question 5: Legal/ToS traps

### Takeaway
The traps are: Synoptic "internal purposes only" and map-consent clauses; Tempest's ban on making data "publicly accessible" and token sharing; WU keys being owner-only (and page scraping un-licensed); Holfuy/Ambient/Netatmo owner-only APIs; Windfinder/Windy terms. US federal feeds (NDBC, CO-OPS, NWS, FEMS), Caltrans and CDEC are the safe ones.

### Cited Findings
- Synoptic: usage "limited to internal purposes unless prior written consent"; public map needs consent + attribution; commercial use without consent → termination — [Synoptic T&C](https://synopticdata.com/tcs/)
- Tempest: may not "make the Data and Software Products publicly accessible", no token sharing, no >$50k product use — [Tempest Commercial Terms](https://help.tempest.earth/hc/en-us/articles/214935288-Terms-Conditions-for-Commercial-Services); API restricted to owned stations — [community](https://community.tempest.earth/t/tempest-api-for-all-public-tempest-stations/10155)
- WU: keys "only issued to registered and active … personal weather station users" — [HA README](https://github.com/cytech/Home-Assistant-wundergroundpws/blob/master/README.md)
- Holfuy: keys only for owners — [Holfuy API](https://api.holfuy.com)
- NWS: open data, free for any purpose — [NWS API docs](https://www.weather.gov/documentation/services-web-api); GGBC1 record CC0 — [data.gov](https://catalog.data.gov/dataset/mid-span-golden-gate-bridge-ggbc1)
- Caltrans: free, subject to a Conditions of Use page — [Caltrans RWIS docs](https://cwwp2.dot.ca.gov/documentation/rwis/rwis.htm)
- NDBC: asks for minimal retrieval volume — [NDBC FAQ](https://www.ndbc.noaa.gov/faq/rt_data_access.shtml)

### Inferences
- Displaying iKitesurf/WeatherFlow sensor readings in a third-party app (even by scraping) is the clearest ToS violation in this list; linking out to iKitesurf is the safe alternative.

### Gaps
- Caltrans Conditions of Use and weather.com/Windfinder/Windy ToS texts were not retrieved.

---

## Appendix: quick-reference endpoints (all verified live 2026-10-26 unless noted)

| Network | Endpoint | Key | CORS | Cadence | Wind fields |
|---|---|---|---|---|---|
| NOAA CO-OPS | `https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=wind&station=9414290&date=latest&units=english&time_zone=gmt&format=json` | none | `*` | 6 min | s, g (kn), d, dr |
| NDBC all stations | `https://www.ndbc.noaa.gov/data/latest_obs/latest_obs.txt` | none | none | hourly file, NOS rows 6-min | WDIR WSPD GST (m/s) |
| NDBC one station | `https://www.ndbc.noaa.gov/data/realtime2/FTPC1.txt` | none | none | 6 min (NOS) / hourly (buoys) | WDIR WSPD GST |
| NWS API | `https://api.weather.gov/stations/KHAF/observations/latest` | User-Agent | `*` | ASOS 20 min–hourly; NOS 6 min; MADIS ~hourly (stale at probe) | windSpeed, windGust (km/h), windDirection |
| CDEC | `https://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet?Stations=MAL&SensorNums=9,10,77&dur_code=E&Start=…&End=…` | none | none | 15 min / hourly | 9 WIND SP mph, 10 DEG, 77 PEAK mph |
| Caltrans RWIS | `https://cwwp2.dot.ca.gov/data/d3/rwis/rwisStatusD03.json` (also d1) | none | `*` | 1 min file | essAvg/Spot/MaxGust (ESS units, decode needed) |
| FEMS RAWS | `https://fems.fs2c.usda.gov/api/climatology/download-weather?stationIds=<id>&dataFormat=csv&dataset=observation&dataIncrement=hourly&startDate=…&endDate=…&fuelModels=Y&fuelMoisture=Y&stationStatus=A&timeZone=America/Los_Angeles` | none | echoes Origin | hourly | WindSpeed(mph), WindAzimuth, GustSpeed, GustAzimuth |
| JPL Tahoe buoys | `https://laketahoe.jpl.nasa.gov/getweather` (HTML) | none | none | hourly (:30) | min:avg:max m/s |
| Synoptic | `https://api.synopticdata.com/v2/stations/latest?token=…&stid=…&vars=wind_speed,wind_gust,wind_direction` | token (.edu free / paid) | untested | ~5–60 min by network | wind_speed, wind_gust, wind_direction |
