# Real-time wind (and wave) sensors for the NorCal coast, Monterey Bay and Lake Tahoe spots

All checks were made live on 2026-10-26 (UTC 23:00–00:30) from a script; "live" below means the feed returned data stamped within the previous hour on that check. Distances are great-circle miles from the spot coordinates given in the assignment. Machine-readable copy: `coast_tahoe_stations.json` in this folder (shape `{spotId: [{id, network, name, lat, lon, dist_mi, height_m_or_null, reports_gust, reports_dir, how_to_read, notes}]}`, sorted by distance).

## Which networks are actually scriptable for free (applies to every spot)

### Takeaway
Four free, keyless, hourly-or-better feeds cover every spot: NDBC `realtime2` text (buoys and NOS PORTS stations), the NWS API (airport METAR/AWOS), IEM's `obhistory.json` decode of GOES/HADS (RAWS fire-weather stations, live within the hour), and CeNCOOS ERDDAP (UC Davis Bodega Marine Lab, Santa Cruz Wharf, Monterey Bay Aquarium, Moss Landing, MBARI M1). Lake Tahoe's only on-water sensors are the four NASA/JPL–UC Davis buoys, published as an hourly HTML table. The commercial sensor networks the kite community uses (iKitesurf/WeatherFlow, Windfinder, Weather Underground, Tempest) are display products without a free scriptable feed, and I did not attempt to pull from their token-gated APIs.

### Cited Findings
- NDBC serves every buoy and C-MAN/PORTS station as `https://www.ndbc.noaa.gov/data/realtime2/<ID>.txt` (columns WDIR WSPD GST WVHT DPD APD MWD …, m/s, `MM` = missing); the station table at `https://www.ndbc.noaa.gov/data/stations/station_table.txt` gives owner, type and coordinates for all 1,900+ stations — [NDBC station table](https://www.ndbc.noaa.gov/data/stations/station_table.txt); [NDBC realtime2 example 46026](https://www.ndbc.noaa.gov/data/realtime2/46026.txt)
- NWS API `points/{lat},{lon}` → `observationStations` lists up to ~160 stations per gridpoint, and `stations/{ID}/observations/latest` returns `windSpeed`/`windGust` in km/h and `windDirection` in degrees; it needs a User-Agent header and is free — [api.weather.gov](https://api.weather.gov/points/37.096,-122.2772)
- On 2026-10-26 the NWS API's copies of non-airport (MADIS mesonet/RAWS/CWOP) stations were all stamped 2026-10-22 (four days stale: MDEC1, XCDC1, BNDC1, NV001, LIB32, AR323, D9019, LAHC1 …) while the airports (KHAF, KMRY, KTRK, KSTS, KDVO, KOAR) were current — my checks of `https://api.weather.gov/stations/<ID>/observations/latest`
- The same RAWS stations are current to the hour in the Iowa Environmental Mesonet decode of the GOES/HADS feed: `https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=XCDC1&network=CA_DCP&date=2026-10-26` returned an ob at 23:09Z with SHEF keys `USIRGZZ` (speed), `UDIRGZZ` (direction) and `UPHRGZZ` (hourly peak gust) — [IEM obhistory XCDC1](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=XCDC1&network=CA_DCP&date=2026-10-26); network catalogue at [IEM networks](https://mesonet.agron.iastate.edu/api/1/networks.json)
- CeNCOOS ERDDAP exposes shore stations as CSV with `orderByMax("time")` for the latest row, e.g. `https://erddap.cencoos.org/erddap/tabledap/bodega-marine-laboratory-weather.csv?time,wind_speed,wind_from_direction&orderByMax(%22time%22)` (units m/s, degrees) — [CeNCOOS ERDDAP BML info](https://erddap.cencoos.org/erddap/info/bodega-marine-laboratory-weather/index.csv); dataset search [`searchFor=wind_speed`](https://erddap.cencoos.org/erddap/search/index.csv?searchFor=wind_speed&page=1&itemsPerPage=200)
- NOS/CO-OPS also serves its met stations 6-minute via `api.tidesandcurrents.noaa.gov/api/prod/datagetter?station=9414290&product=wind&date=latest&units=english&format=json`; the mdapi `sensors.json` call shows which stations have a `Wind` sensor: 9414290 San Francisco yes; 9413450 Monterey and 9415020 Point Reyes no (water temp, pressure and water level only); 9414131 Pillar Point and 9415625 Bodega returned `sensors: null` — [CO-OPS mdapi 9414290](https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9414290/sensors.json); [9415020](https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9415020/sensors.json)
- Synoptic/MesoWest requires a (free-tier) API token; the old `demotoken` is rejected ("Invalid token") — [Synoptic API](https://api.synopticdata.com/v2/stations/metadata?token=demotoken&radius=37.096,-122.2772,15)
- CDIP wave buoys: 30-minute text at `https://cdip.ucsd.edu/data_access/justdar.cdip?<stn>+pm` (Hs m, Tp s, Dp deg, Ta s) and NetCDF at `https://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/realtime/<stn>p1_rt.nc`. The realtime THREDDS catalogue on 2026-10-26 listed, for this coast, only 029 (Point Reyes), 142 (San Francisco Bar) and 156 (Monterey Canyon Outer) — [CDIP realtime catalog](https://thredds.cdip.ucsd.edu/thredds/catalog/cdip/realtime/catalog.html); [CDIP 142 justdar](https://cdip.ucsd.edu/data_access/justdar.cdip?142+pm)
- iKitesurf/SailFlow (WeatherFlow-Tempest) sensors are referenced by the forecasters only by name ("the Waddell sensor … near a bluff, northeast winds above the bluff can affect its readings") and the public blog does not give ids, owners or an open feed — [Tempest/iKitesurf blog, Waddell forecast post](https://blog.tempest.earth/was-the-waddell-forecast-bust-or-boom/); [iKitesurf brand page](https://tempest.earth/brands/ikitesurf-com)
- Windfinder publishes "Report from local weather station" pages for Bodega Harbor (15 kts WNW at 16:30 local on 2026-10-26, elevation 30 m), Dillon Beach, Waddell Creek and "Lake Tahoe Buoy West", but the pages are JS-rendered and do not name the source station; note that Windfinder's `kings_beach` slug is Kings Beach, Port Elizabeth, South Africa, not Tahoe — [Windfinder Bodega Harbor report](https://www.windfinder.com/report/bodega_harbor); [Windfinder Kings Beach statistics (South Africa)](https://www.windfinder.com/windstatistics/kings_beach); [Windfinder Lake Tahoe Buoy West](https://www.windfinder.com/windstatistics/lake-tahoe-buoy_west)

### Inferences
- For the app's hourly observations job, the free stack per spot is: NDBC text (buoys, FTPC1, PXOC1, MLSC1), NWS API (airports only), IEM CA_DCP/NV_DCP (RAWS, Golden Gate Bridge, Point Reyes RCA), CeNCOOS ERDDAP (BML, SC Wharf, MBA, MLML, M1), JPL table scrape (Tahoe buoys). Mesonet/CWOP stations should come from Synoptic (free token) or IEM rather than the NWS API, which lags days.
- RAWS wind in SHEF is mph (standard for RAWS `US`/`UP`); NWS API is km/h; NDBC/ERDDAP are m/s. The app stores knots, so each source needs its own conversion.

### Gaps
- I could not enumerate CWOP, Weather Underground PWS, Tempest or Netatmo stations near each beach: findu's `wxnear.cgi` returned an empty page, MesoWest's station-finder CGI is gone (404), aprs.fi and Synoptic need API keys, and sensoto.io/opensnow lookups returned snow stations or the wrong Kings Beach. The NWS API shows a few CWOP ids (D7094 Mill Valley, AR323 Sebastopol, AP803 and C9585 Santa Cruz, AW020 Mountain View, D9019 Olympic Valley, D9413 Homewood) but none is on a beach and all were 4 days stale there.
- The iKitesurf/WeatherFlow sensor ids for "Waddell Creek", "Stinson", "Kings Beach", "Marina", etc. remain unverified; their map API is token-gated and I did not scrape it.
- No UCSC Long Marine Lab station appears in CeNCOOS ERDDAP, NDBC or the NWS API; the Santa Cruz Municipal Wharf station is the public Santa Cruz shore sensor.
- Bodega Marine Lab's ERDDAP dataset has no gust variable and no published anemometer height (z = 0 in metadata).

---

## stinson — Stinson Beach (37.8975, -122.644)

### Takeaway
There is no public live anemometer on the beach. The closest wind sensors are Middle Peak RAWS on Mt Tamalpais (3.7 mi, ridge-top) and Fort Point FTPC1 at the Golden Gate (11.6 mi, Gate jet); the offshore reference is NDBC 46026 (14.7 mi). Swell comes from CDIP 142 / NDBC 46237 San Francisco Bar, 7.6 mi SSE and directly offshore.

### Cited Findings
- MDEC1 "Middle Peak" RAWS, 37.9308 -122.5908, 587 m elevation, 3.7 mi NE; hourly speed/dir/peak gust; live 2026-10-26 23:36Z (8 mph, gust 14, 316°) — [IEM obhistory MDEC1](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=MDEC1&network=CA_DCP&date=2026-10-26); [NWS station MDEC1](https://api.weather.gov/stations/MDEC1/observations/latest) (stale copy)
- BBEC1 "Barnaby" RAWS, 38.0281 -122.7022, 247 m, 9.6 mi NW on Bolinas Ridge; live 2026-10-26 (3 mph, gust 18, 295°) — [IEM obhistory BBEC1](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=BBEC1&network=CA_DCP&date=2026-10-26)
- FTPC1 / NOS 9414290 Fort Point, 37.806 -122.466, anemometer 7 m; 6-minute wind, gust, direction; live 2026-10-26 23:30Z (260° 4.1 m/s G 7.2) — [NDBC FTPC1](https://www.ndbc.noaa.gov/data/realtime2/FTPC1.txt); [NDBC station page FTPC1](https://www.ndbc.noaa.gov/station_page.php?station=FTPC1)
- GGBC1 Golden Gate Bridge center, 37.8187 -122.4784 (IEM CA_DCP metadata), hourly speed/dir/peak via GOES; live 2026-10-26 23:30Z (18.7 / peak 19.9 from 103°; units not documented) — [IEM obhistory GGBC1](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=GGBC1&network=CA_DCP&date=2026-10-26); metadata in [IEM CA_DCP geojson](https://mesonet.agron.iastate.edu/geojson/network/CA_DCP.geojson)
- 46026 San Francisco buoy, 37.750 -122.838, 3-m foam buoy, anemometer 4 m; wind, gust, waves; live 2026-10-26 23:20Z (320° 7 m/s G 9, WVHT 1.0 m, DPD 13 s, MWD 273°) — [NDBC 46026](https://www.ndbc.noaa.gov/data/realtime2/46026.txt); [station page](https://www.ndbc.noaa.gov/station_page.php?station=46026)
- Wave: CDIP 142 / NDBC 46237 "San Francisco Bar", 37.788 -122.634, Datawell directional, 16 m depth; 30-min Hs/Tp/Dp; live 2026-10-26 (Hs 0.85–1.1 m, Tp 13–14 s, Dp 230–278°). NDBC copy has no wind (WDIR/WSPD `MM`) — [NDBC 46237](https://www.ndbc.noaa.gov/data/realtime2/46237.txt); [CDIP 142](https://cdip.ucsd.edu/data_access/justdar.cdip?142+pm)
- Nearby NDBC entries TIBC1 (Tiburon) last reported 2026-09-24 and carries only water temperature on NDBC; its CeNCOOS copy ("tiburon-weather-tibc1", 37.8915 -122.4466, speed/dir/gust) also ends 2026-09-24 — [NDBC TIBC1](https://www.ndbc.noaa.gov/data/realtime2/TIBC1.txt); [CeNCOOS tibc1 info](https://erddap.cencoos.org/erddap/info/tiburon-weather-tibc1/index.csv)

### Inferences
- Use MDEC1 only as a gradient/gust indicator (it sat at 8 mph while KHAF/KDVO showed 16–18 km/h sustained); the beach-level number is best approximated from 46026 plus CDIP 142. If the app needs a single "nearest" id for Stinson, MDEC1 (3.7 mi) is the honest answer, flagged as ridge-top.

### Gaps
- No CWOP/PWS on the Stinson/Bolinas sandspit could be identified from scriptable sources; the Windfinder report slug `stinson_beach` returned 404.

---

## oceanbeach — Ocean Beach SF, north end (37.774, -122.5125)

### Takeaway
Fort Point FTPC1 (3.4 mi, 6-minute, with gusts) is the closest public live anemometer; the Golden Gate Bridge GGBC1 (3.6 mi) and offshore 46026 (17.9 mi) complete the picture. Swell: CDIP 142 San Francisco Bar, 6.7 mi WNW.

### Cited Findings
- FTPC1 / 9414290, 37.806 -122.466, anemometer 7 m, 6-min wind/gust/dir, live 2026-10-26 — [NDBC FTPC1](https://www.ndbc.noaa.gov/data/realtime2/FTPC1.txt); CO-OPS wind product for 9414290 — [CO-OPS sensors 9414290](https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9414290/sensors.json)
- GGBC1 Golden Gate Bridge center, hourly speed/dir/peak, live 2026-10-26 — [IEM obhistory GGBC1](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=GGBC1&network=CA_DCP&date=2026-10-26)
- SFOC1 "San Francisco Downtown" (37.7706 -122.4269, 4.7 mi) is in the NWS list but its latest ob had null wind fields — [NWS SFOC1](https://api.weather.gov/stations/SFOC1/observations/latest)
- KSFO ASOS (37.6196 -122.3656, 13.4 mi) `latest` returned null wind; the observations list works — [NWS KSFO latest](https://api.weather.gov/stations/KSFO/observations/latest)
- PXOC1 (SF Pier 1, 37.798 -122.393, anemometer 16 m) reports 6-min wind/gust but is bayside, 6.7 mi — [NDBC PXOC1](https://www.ndbc.noaa.gov/data/realtime2/PXOC1.txt)
- 46026 and CDIP 142 as above — [NDBC 46026](https://www.ndbc.noaa.gov/data/realtime2/46026.txt); [NDBC 46237](https://www.ndbc.noaa.gov/data/realtime2/46237.txt)

### Inferences
- FTPC1 sits at the Gate mouth and over-reads the westerly funnel relative to the open beach; 46026 under-reads the beach sea breeze. Averaging the two is a reasonable Ocean Beach proxy until a beach PWS is found.

### Gaps
- No Ocean Beach / Sunset District CWOP or PWS id could be verified from scriptable sources.

---

## hmb — Half Moon Bay, Dunes Beach (37.4878, -122.4522)

### Takeaway
KHAF Half Moon Bay Airport (3.2 mi, 20-minute METAR with gusts, on the coastal flat) is the primary sensor; Spring Valley RAWS HSPC1 (5.2 mi, hilltop) is the gust/gradient backup. Offshore wind: 46012 — but it is currently a Saildrone, not the fixed buoy. Swell: CDIP 142 (23 mi N); no closer wave buoy is live.

### Cited Findings
- KHAF, 37.5136 -122.4996, elev 19.8 m; latest 2026-10-26 22:55Z: 16.6 km/h gust 27.7 km/h from 320°; 20-minute cadence (22:15, 22:35, 22:55) — [NWS KHAF latest](https://api.weather.gov/stations/KHAF/observations/latest); [NWS KHAF list](https://api.weather.gov/stations/KHAF/observations?limit=3)
- HSPC1 "Spring Valley RAWS", 37.5625 -122.4364, 314 m, hourly, live 2026-10-26 23:18Z (9 mph, gust 20, 252°) — [IEM obhistory HSPC1](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=HSPC1&network=CA_DCP&date=2026-10-26)
- 46012 "Half Moon Bay – 24 NM SSW of SF": the NDBC station table lists it as type "Uncrewed Surface Vehicle", payload DataXplorer, at 37.356 -122.881; the station page says data are provided by a Saildrone, anemometer 1.3 m, watch-circle radius 20,254 yd, with deployments SD-1073/1077/1063 since 2023; live 2026-10-26 23:00Z (310° 7 m/s G 9, WVHT 1.1 m) — [NDBC station table](https://www.ndbc.noaa.gov/data/stations/station_table.txt); [NDBC station page 46012](https://www.ndbc.noaa.gov/station_page.php?station=46012); [NDBC 46012 data](https://www.ndbc.noaa.gov/data/realtime2/46012.txt)
- NOS 9414131 Pillar Point Harbor has no met sensors listed (`sensors: null`) — [CO-OPS mdapi 9414131](https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9414131/sensors.json)
- MBWC1 "Montara – Montara Beach" (37.5352 -122.5192) exists in the HADS catalogue but last reported 2025-09-23 and shows no wind — [IEM current MBWC1](https://mesonet.agron.iastate.edu/json/current.py?station=MBWC1&network=CA_DCP)
- 46026 (27.8 mi) and CDIP 142 (23 mi) as above.

### Inferences
- KHAF is one of the best beach proxies on the whole list: sea-level, 0.5 mi from the harbor, 20-min with gusts. Dunes Beach is 3 mi south on the same open bight, so expect similar direction and slightly more wind than the airport (which is behind Pillar Point for NW).

### Gaps
- No live wave buoy within 20 mi (CDIP has none between the SF Bar and Monterey Bay that is currently in realtime).

---

## pillarpoint — Pillar Point Harbor (37.5035, -122.489)

### Takeaway
KHAF is 0.9 mi away — the closest airport-to-spot pairing of all eleven spots — and is the sensor to use; HSPC1 RAWS (5.0 mi) and the 46012 Saildrone (23.8 mi) are secondary. Swell: CDIP 142 (21.2 mi).

### Cited Findings
- KHAF 0.9 mi, details as for hmb — [NWS KHAF](https://api.weather.gov/stations/KHAF/observations/latest)
- HSPC1 5.0 mi, details as for hmb — [IEM HSPC1](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=HSPC1&network=CA_DCP&date=2026-10-26)
- 46012 Saildrone and 46026 as above — [NDBC 46012 station page](https://www.ndbc.noaa.gov/station_page.php?station=46012)
- Wave: CDIP 142 / 46237 — [NDBC 46237](https://www.ndbc.noaa.gov/data/realtime2/46237.txt)

### Inferences
- Inside the harbor the breakwater and Pillar Point bluff shelter the water from NW; KHAF (just east of the harbor on the flat) will read close to the inner-harbor launch, and higher than the water behind the bluff.

### Gaps
- None beyond the general PWS/CWOP gap.

---

## gazos — Gazos Creek State Beach (37.1715, -122.3635)

### Takeaway
This is the thinnest spot: the nearest public live anemometers are all RAWS in the hills 11–14 mi away (BNDC1 Ben Lomond, LAHC1 La Honda, XCDC1 Coast Dairies); the offshore references are 46042 (26.7 mi) and the 46012 Saildrone (31 mi). The ideal wave buoy, CDIP 254 Point Santa Cruz, is offline; CDIP 156 (36.5 mi) is the live fallback.

### Cited Findings
- XCDC1 "Coast Dairies" RAWS, 37.0308 -122.1878, 198 m, 13.7 mi SE on the Davenport terrace; live 2026-10-26 23:09Z (13 mph, gust 27, 294°) — [IEM XCDC1](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=XCDC1&network=CA_DCP&date=2026-10-26)
- BNDC1 "Ben Lomond RAWS", 37.1310 -122.1727, 800 m, 10.9 mi E; live (3 mph, gust 12, 336°) — [IEM BNDC1](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=BNDC1&network=CA_DCP&date=2026-10-26)
- LAHC1 "La Honda" RAWS, 37.3052 -122.2553, 245 m, 11.0 mi NE; live (2 mph, gust 10, 241°) — [IEM LAHC1](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=LAHC1&network=CA_DCP&date=2026-10-26)
- HADS stations closer to Gazos (BUXC1/BPXC1 Butano Creek 4.3 mi, XCAC1 Pescadero Creek 5.9 mi, SZCC1 Scott Creek 9.0 mi) are stream/rain gauges with no wind elements (SZCC1 keys: PC/PP only) — [IEM SZCC1](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=SZCC1&network=CA_DCP&date=2026-10-26); [IEM CA_DCP geojson](https://mesonet.agron.iastate.edu/geojson/network/CA_DCP.geojson)
- 46042 Monterey buoy, 36.787 -122.408, anemometer 4 m; wind, gust, waves; live 2026-10-26 23:20Z (320° 10 m/s G 14, WVHT 1.7 m, DPD 11 s, MWD 324°) — [NDBC 46042](https://www.ndbc.noaa.gov/data/realtime2/46042.txt); [station page](https://www.ndbc.noaa.gov/station_page.php?station=46042)
- Wave: CDIP 254 / NDBC 46269 Point Santa Cruz (36.934 -122.034, 20 m depth) is in NDBC's station table but `realtime2/46269.txt` returned 404 and 254 is absent from CDIP's realtime catalogue — [NDBC station table](https://www.ndbc.noaa.gov/data/stations/station_table.txt); [CDIP realtime catalog](https://thredds.cdip.ucsd.edu/thredds/catalog/cdip/realtime/catalog.html)
- Wave fallback: CDIP 156 / NDBC 46236 Monterey Canyon Outer, 36.759 -121.950, live (Hs 1.1 m, DPD 11 s, MWD 298°) — [NDBC 46236](https://www.ndbc.noaa.gov/data/realtime2/46236.txt)

### Inferences
- Gazos, Waddell and Davenport share the same NW-facing open coast north of the Santa Cruz lee; XCDC1 (a marine-terrace RAWS) is the best single live number for all three despite being 200 m up. Expect beach wind to run higher than XCDC1 sustained and close to its hourly peak.

### Gaps
- No sea-level public sensor exists between Half Moon Bay Airport and Davenport. The Pescadero RAWS mentioned in the brief could not be found under that name in HADS/NWS lists (the closest RAWS are La Honda and Coast Dairies).

---

## waddell — Waddell Creek (37.096, -122.2772)

### Takeaway
Closest live public anemometers are Ben Lomond RAWS (6.2 mi, 800 m up, low value) and Coast Dairies RAWS XCDC1 (6.7 mi, terrace, the useful one); the Santa Cruz Wharf station (17 mi) and 46042 (22.5 mi) frame it. The famous "Waddell sensor" is an iKitesurf/WeatherFlow unit with no open feed. Wave: CDIP 254 offline; use CDIP 156 (29.5 mi).

### Cited Findings
- XCDC1 and BNDC1 as above, 6.7 and 6.2 mi — [IEM XCDC1](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=XCDC1&network=CA_DCP&date=2026-10-26); [IEM BNDC1](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=BNDC1&network=CA_DCP&date=2026-10-26)
- Santa Cruz Municipal Wharf weather station, 36.960278 -122.020278, hourly mean speed/dir plus gust (m/s), live 2026-10-26 23:00Z (1.44 m/s @107°, gust 3.8) — [CeNCOOS SC Wharf info](https://erddap.cencoos.org/erddap/info/santa-cruz-wharf-weather-stat/index.csv); [latest row](https://erddap.cencoos.org/erddap/tabledap/santa-cruz-wharf-weather-stat.csv?time,wind_speed_cm_time__mean_over_pt1h,wind_from_direction_cm_time__mean_over_pt1h,wind_speed_of_gust&orderByMax(%22time%22))
- 46042 (22.5 mi) live with wind/gust/waves — [NDBC 46042](https://www.ndbc.noaa.gov/data/realtime2/46042.txt)
- MBARI M1 / NDBC 46092, 36.751 -122.029, anemometer 4 m; NDBC feed had WSPD+WDIR, no gust/waves, 2026-10-26 23:08Z; ERDDAP copy ended 2026-10-23 — [NDBC 46092](https://www.ndbc.noaa.gov/data/realtime2/46092.txt); [NDBC 46092 page](https://www.ndbc.noaa.gov/station_page.php?station=46092); [CeNCOOS org_mbari_m1](https://erddap.cencoos.org/erddap/info/org_mbari_m1/index.csv)
- iKitesurf "Waddell sensor": forecaster notes it is near a bluff and NE winds above the bluff affect it; no id/owner/API given — [Tempest blog](https://blog.tempest.earth/was-the-waddell-forecast-bust-or-boom/)
- Windfinder has a "Waddell Creek" live report page (source station unnamed, JS-rendered) — [Windfinder Waddell Creek report](https://www.windfinder.com/report/waddell_creek)
- Wave: CDIP 254/46269 offline; CDIP 156/46236 live — [NDBC 46236](https://www.ndbc.noaa.gov/data/realtime2/46236.txt)

### Inferences
- The Santa Cruz Wharf reading (1.4 m/s) versus XCDC1 (13 mph, G27) at the same hour illustrates the Santa Cruz lee: never use the wharf as a Waddell proxy, only as a "is the wind wrapping into the bay" check.

### Gaps
- The WeatherFlow/iKitesurf Waddell sensor id and coordinates are unverified (token-gated map API not queried).

---

## davenport — Davenport / Scott Creek (37.0405, -122.2305)

### Takeaway
Coast Dairies RAWS XCDC1 is 2.4 mi away and live hourly with gusts — the best RAWS-to-beach match on this coast. Backups: BNDC1 (7.0 mi), Santa Cruz Wharf (12.9 mi), 46042 (20.1 mi), M1 (22.9 mi). Wave: CDIP 254 (13.1 mi) when it returns; CDIP 156 (24.9 mi) now.

### Cited Findings
- XCDC1 Coast Dairies, 37.0308 -122.1878, 198 m (IEM) / 214 m (NWS), 2.4 mi ESE; live 2026-10-26 23:09Z, 13 mph G27 @294° — [IEM XCDC1](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=XCDC1&network=CA_DCP&date=2026-10-26); [NWS XCDC1 (stale)](https://api.weather.gov/stations/XCDC1/observations/latest)
- DAPC1 "Davenport ALERT #1981" (37.0197 -122.1917, 2.6 mi) and LDLC1 "Davenport 4WSW – Liddel" are rain gauges in HADS, no wind — [IEM CA_DCP geojson](https://mesonet.agron.iastate.edu/geojson/network/CA_DCP.geojson)
- Remaining stations as for waddell — [NDBC 46042](https://www.ndbc.noaa.gov/data/realtime2/46042.txt); [CeNCOOS SC Wharf](https://erddap.cencoos.org/erddap/info/santa-cruz-wharf-weather-stat/index.csv); [NDBC 46236](https://www.ndbc.noaa.gov/data/realtime2/46236.txt)

### Inferences
- XCDC1's 294° at 13 G27 mph while 46042 showed 320° at 10 G14 m/s (19 G27 kn) is consistent with the terrace station reading a bit below the open-ocean wind; a per-station bias will settle quickly in the app's accuracy log.

### Gaps
- No sea-level sensor at Scott Creek or Davenport Landing in any public network found.

---

## marina — Marina State Beach, Monterey Bay (36.6839, -121.8128)

### Takeaway
Marina has the richest sensor set: KOAR Marina Municipal Airport (3.1 mi, 20-minute, gusts, on the dune flat), Monterey Bay Aquarium (6.7 mi, 15-min, gusts), KMRY (6.8 mi), Moss Landing MLSC1 (8.2 mi, 10 m mast, gusts) and MBARI M1 mid-bay (12.8 mi). Wave: CDIP 156 / NDBC 46236 Monterey Canyon Outer, 9.2 mi NW, live.

### Cited Findings
- KOAR "Fort Ord Fritzsche AAF" (now Marina Municipal), 36.6815 -121.7574, elev 43 m, 3.1 mi; 20-minute obs with gusts, 2026-10-26 22:55Z 20.5 km/h G 25.9 @290° — [NWS KOAR observations](https://api.weather.gov/stations/KOAR/observations?limit=3); [IEM CA_ASOS geojson](https://mesonet.agron.iastate.edu/geojson/network/CA_ASOS.geojson)
- KMRY Monterey Regional, 36.5905 -121.8487, 6.8 mi; 5-minute obs in NWS list (18.5 km/h @280° 2026-10-27 00:05Z), gust often null — [NWS KMRY](https://api.weather.gov/stations/KMRY/observations?limit=3)
- Monterey Bay Aquarium weather station, 36.618808 -121.901489, ~15-min, speed/dir/gust (m/s), live 2026-10-26 23:46Z (6.66 m/s @317°, gust 8.92) — [CeNCOOS MBA info](https://erddap.cencoos.org/erddap/info/monterey-bay-aquarium-weather/index.csv); [latest row](https://erddap.cencoos.org/erddap/tabledap/monterey-bay-aquarium-weather.csv?time,wind_speed,wind_from_direction,wind_speed_of_gust__m_s&orderByMax(%22time%22))
- MLSC1 Moss Landing Marine Labs, 36.8004 -121.78842, anemometer 10 m; ERDDAP live 2026-10-27 00:21Z (4.5 m/s @297°, gust 10.0); NDBC copy had WSPD only — [CeNCOOS mlml_mlml_met](https://erddap.cencoos.org/erddap/info/mlml_mlml_met/index.csv); [NDBC MLSC1](https://www.ndbc.noaa.gov/data/realtime2/MLSC1.txt); [NDBC MLSC1 page](https://www.ndbc.noaa.gov/station_page.php?station=MLSC1)
- MBARI M1 / 46092 as above (12.8 mi) — [NDBC 46092](https://www.ndbc.noaa.gov/data/realtime2/46092.txt)
- NOS 9413450 Monterey (MTYC1/MEYC1) has no wind sensor (pressure, water temp, water level only); NDBC MEYC1 confirms all wind fields `MM` — [CO-OPS 9413450 sensors](https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9413450/sensors.json); [NDBC MEYC1](https://www.ndbc.noaa.gov/data/realtime2/MEYC1.txt)
- FOMC1 "Marina 2E – Fort Ord" (36.6821 -121.7754, 2.1 mi) is a HADS rain/temp gauge, no wind — [IEM FOMC1 history](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=FOMC1&network=CA_DCP&date=2026-10-26)
- ELXC1 Elkhorn Slough "Caspian" NERRS weather station (36.815 -121.738, 10 mi) reports wind/dir on NDBC but is inland in the slough — [NDBC ELXC1](https://www.ndbc.noaa.gov/data/realtime2/ELXC1.txt)
- Wave: CDIP 156 / 46236, 36.759 -121.950, 133 m depth, live (Hs 1.1 m, DPD 11 s, MWD 298°). CDIP 158 / 46240 Cabrillo Point (36.626 -121.907, 6.6 mi) and 185 / 46114 West Monterey Bay are in the NDBC table but 404 on realtime2 and absent from CDIP realtime — [NDBC 46236](https://www.ndbc.noaa.gov/data/realtime2/46236.txt); [CDIP 156](https://cdip.ucsd.edu/data_access/justdar.cdip?156+pm); [CDIP realtime catalog](https://thredds.cdip.ucsd.edu/thredds/catalog/cdip/realtime/catalog.html)

### Inferences
- KOAR should be the primary: same NW exposure as the beach, sea-breeze fetch across the dunes, and it was reporting 3–4 km/h more than KMRY at the same hour. MBA and KMRY are in the peninsula lee and will read low on classic NW days.

### Gaps
- No live wave buoy inside the south bay now that CDIP 158 is off; 46236 is 9 mi out over the canyon.

---

## dillon — Dillon Beach (38.2495, -122.966)

### Takeaway
Dillon has no live wind sensor of its own (DBEC1 "Dillon Beach" in HADS is temperature only). The nearest live anemometers are the UC Davis Bodega Marine Lab station on Bodega Head (7.3 mi, 5-min, no gust) and the Point Reyes RCA station PRWC1 at the head of Tomales Bay (10.8 mi, hourly with peak). Offshore: NDBC 46013 (19.1 mi, wind live, waves missing). Wave: CDIP 029 Point Reyes (34.4 mi), live.

### Cited Findings
- DBEC1 "DILLON BEACH", 38.2575 -122.9578, 128 m, 0.7 mi: HADS keys are `TAIRRZZ` (air temp) only, last 2026-10-26 14:38 — [IEM DBEC1 history](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=DBEC1&network=CA_DCP&date=2026-10-26)
- Bodega Marine Laboratory weather station, 38.31652 -123.0709, 5-min `wind_speed` and `wind_from_direction` (m/s), no gust variable, z = 0; live 2026-10-26 23:55Z (9.92 m/s @313°) — [CeNCOOS BML info](https://erddap.cencoos.org/erddap/info/bodega-marine-laboratory-weather/index.csv); [latest row](https://erddap.cencoos.org/erddap/tabledap/bodega-marine-laboratory-weather.csv?time,wind_speed,wind_from_direction,z&orderByMax(%22time%22)); [data.ioos.us record](https://data.ioos.us/dataset/bodega-marine-laboratory-weather-station1)
- PRWC1 "Port[sic] Reyes RCA", 38.0942 -122.9500, 26 m (IEM CA_DCP); hourly `USIRGZZ`/`UDIRGZZ`/`UPVRGZZ`; live 2026-10-26 23:20Z (15.47 / peak 20.46 from 326°; units undocumented). CeNCOOS also lists "Point Reyes RCA (PRWC1)" at 38.1001 -122.9313 but that dataset ended 2012 — [IEM PRWC1 history](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=PRWC1&network=CA_DCP&date=2026-10-26); [CeNCOOS saic_ptrca info](https://erddap.cencoos.org/erddap/info/saic_ptrca/index.csv)
- NOS PRYC1 / 9415020 Point Reyes has no wind sensor; 10,467 rows of NDBC realtime history contained no non-missing wind — [CO-OPS 9415020 sensors](https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9415020/sensors.json); [NDBC PRYC1](https://www.ndbc.noaa.gov/data/realtime2/PRYC1.txt)
- 46013 Bodega Bay buoy, 38.235 -123.317, 3-m discus, anemometer ~3 m; wind/gust live 2026-10-26 23:30Z (300° 8 m/s G 11) but WVHT/DPD/MWD `MM` — [NDBC 46013](https://www.ndbc.noaa.gov/data/realtime2/46013.txt); [station page](https://www.ndbc.noaa.gov/station_page.php?station=46013)
- KSTS Santa Rosa ASOS, 38.5 -122.8167, 19.1 mi inland, live — [NWS KSTS](https://api.weather.gov/stations/KSTS/observations?limit=3)
- Windfinder "Dillon Beach" live report page exists (source unnamed) — [Windfinder Dillon Beach report](https://www.windfinder.com/report/dillon_beach)
- Wave: CDIP 029 / NDBC 46214 Point Reyes, 37.944 -123.466, 600 m depth, live (Hs 2.1 m, Tp 12–15 s); NDBC copy has no wind — [CDIP 029](https://cdip.ucsd.edu/data_access/justdar.cdip?029+pm); [NDBC 46214](https://www.ndbc.noaa.gov/data/realtime2/46214.txt)

### Inferences
- Dillon faces WNW at the mouth of Tomales Bay; BML on Bodega Head is the same air mass 7 mi north and is the right primary, with PRWC1 giving the down-bay NW confirmation. Because BML lacks a gust field, pair it with 46013's GST for the gust factor.

### Gaps
- No Dillon Beach / Lawson's Landing PWS found in scriptable sources; Windfinder's source for its Dillon Beach report is unknown.

---

## bodega — Bodega Harbor / Doran Beach (38.3222, -123.04)

### Takeaway
The Bodega Marine Lab station is 1.7 mi away on Bodega Head and is the obvious primary (5-min, free CSV), with 46013 offshore (16.2 mi), PRWC1 (16.5 mi) and KSTS (17.2 mi) as backups. Wave: CDIP 029 Point Reyes (34.9 mi).

### Cited Findings
- BML station 38.31652 -123.0709, 5-min speed/dir, live — [CeNCOOS BML](https://erddap.cencoos.org/erddap/tabledap/bodega-marine-laboratory-weather.csv?time,wind_speed,wind_from_direction,z&orderByMax(%22time%22)); the NDBC entry for the same site (BDXC1 "Bodega, CA", 38.317 -123.071) carries only water temperature — [NDBC BDXC1](https://www.ndbc.noaa.gov/data/realtime2/BDXC1.txt)
- BDZC1 "Bodega Marine Reserve" (38.3139 -123.0603) and BBYC1 "Bodega Bay 6 WSW" in HADS are rain/temp only (BBYC1 last 2026-08-21) — [IEM BDZC1 history](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=BDZC1&network=CA_DCP&date=2026-10-26); [IEM current BBYC1](https://mesonet.agron.iastate.edu/json/current.py?station=BBYC1&network=CA_DCP)
- NOS 9415625 Bodega Harbor: `sensors: null` — [CO-OPS 9415625](https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9415625/sensors.json)
- Windfinder "Bodega Harbor" report showed 15 kts WNW at 16:30 local on 2026-10-26, "Elevation 30 m", source unnamed — [Windfinder Bodega Harbor](https://www.windfinder.com/report/bodega_harbor)
- 46013, PRWC1, KSTS, CDIP 029 as under dillon.

### Inferences
- Doran Beach is on the harbor's south side and rides the NW wind side-shore; BML on the exposed head will read higher than Doran, so a negative per-spot bias is expected. Windfinder's Bodega Harbor "30 m elevation" station is probably a different (private) sensor than BML; unverified.

### Gaps
- No gust from BML; no public anemometer on Doran spit itself.

---

## kingsbeach — Kings Beach, Lake Tahoe (39.2365, -120.0255)

### Takeaway
The closest on-water sensor is NASA/JPL–UC Davis buoy TB1 (5.7 mi SSW off the NE shore), hourly with 30-min min/avg/max (max ≈ gust), scraped from an HTML table. Lake-level shore stations NV001 Incline Village Lakeshore Blvd (4.3 mi) and LIB32 Lake Forest (5.7 mi) are live only via Synoptic/MesoWest or weather.gov timeseries (the NWS API copy lags days). Knox 2 RAWS (4.2 mi, 2,300 m) and KTRK Truckee (8.0 mi) give the gradient. No wave buoy (lake).

### Cited Findings
- JPL "Lake Tahoe Weather Now": four NASA/JPL–UCD buoys TB1–TB4; data downloaded hourly on the hour, page updated at :30 past; each value is min:average:max over the last 30 minutes of the previous hour from 2-minute samples; raw, unchecked; −99 = missing; wind in mph with a "Switch to Metric" option. On 2026-10-27 00:12Z TB1 read 18.8:26.6:32.7 mph from 192:218:241°, TB4 11.4:20.5:28.9 mph — [JPL getweather](https://laketahoe.jpl.nasa.gov/getweather)
- Buoy positions (JPL "Measurements" table, current period): TB1 39.155111 −120.004128 (since 2015-07-27), TB2 39.108767 −120.006167 (since 2002), TB3 39.111983 −120.070617 (since 2002), TB4 39.155481 −120.070740 (since 2019-10-14); each measures wind speed/dir, pressure, air temp, RH, net radiation and skin temperature — [JPL measurements](https://laketahoe.jpl.nasa.gov/measurements)
- UC Davis TERC: six buoys/rafts with JPL plus six land stations measuring wind speed, direction and gust; near-real-time via the JPL page — [TERC real-time data](https://tahoe.ucdavis.edu/real-time-data)
- NV001 "Incline Village (Lakeshore Blvd)", 39.2401 −119.9458, elev 1,898 m, reports gust; NWS API latest stamped 2026-10-22 (stale) — [NWS NV001](https://api.weather.gov/stations/NV001/observations/latest)
- LIB32 "TAH-5201 Lake Forest", 39.1888 −120.1128, 1,928 m, reports gust; also stale in NWS API — [NWS LIB32](https://api.weather.gov/stations/LIB32/observations/latest)
- KNXN2 "Knox 2 / Incline Village" RAWS, 39.2728 −119.9630, 2,299 m; live hourly via IEM NV_DCP 2026-10-26 23:19Z (7 mph, gust 21, 251°) — [IEM KNXN2](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=KNXN2&network=NV_DCP&date=2026-10-26)
- LVYN2 "Little Valley WRCC RAWS", 39.2444 −119.8808, 1,982 m, live (13 mph G48 @260°) — [IEM LVYN2](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=LVYN2&network=NV_DCP&date=2026-10-26)
- HMDC1 "Homewood" RAWS, 39.0841 −120.1707, 2,170 m, live (11 mph G31 @239°) — [IEM HMDC1](https://mesonet.agron.iastate.edu/api/1/obhistory.json?station=HMDC1&network=CA_DCP&date=2026-10-26)
- KTRK Truckee-Tahoe AWOS, 39.3167 −120.1333, 1,798 m; 20-min with gusts (2026-10-26 20:47Z 25.9 km/h G 48.2 @220°; 22:49Z gust 44.6, speed null) — [NWS KTRK](https://api.weather.gov/stations/KTRK/observations?limit=3)
- KTVL South Lake Tahoe ASOS (38.8939 −119.9953, 23.7 mi), KRNO (21.8 mi) live but distant — [NWS KTVL](https://api.weather.gov/stations/KTVL/observations?limit=3); [IEM NV_ASOS geojson](https://mesonet.agron.iastate.edu/geojson/network/NV_ASOS.geojson)
- SLIDE "Slide Mountain" (39.3072 −119.8839, 2,941 m, 9 mi) reports gust in the NWS list (stale copy) — [NWS SLIDE](https://api.weather.gov/stations/SLIDE/observations/latest)
- Windfinder offers "Lake Tahoe Buoy West" (and the South-African "Kings Beach") report pages — [Windfinder Lake Tahoe Buoy West](https://www.windfinder.com/windstatistics/lake-tahoe-buoy_west)
- OpenSnow's Kings Beach station list is SNOTEL/snow stations with no wind — [OpenSnow Kings Beach stations](https://opensnow.com/location/kings-beach-ca-us/weather-stations)

### Inferences
- TB1 is the sensor Kings Beach riders care about: it sits in the NE basin where the afternoon SW wind arrives, and its "max" column gives a 2-minute gust. Scraping the JPL table hourly is trivial (fixed column order TB1, TB1a, TB2, TB2a, TB3, TB3a, TB4, TB4a; the "a" columns are duplicate sensors).
- NV001 is the closest lake-level shore anemometer and is worth a Synoptic free token on its own.

### Gaps
- Northstar and Palisades Tahoe summit anemometers: not found in any public network list (resort pages only); unverified.
- No CWOP/PWS in Kings Beach or Tahoe Vista could be identified from scriptable sources (D9019 Olympic Valley and D9413 Homewood are the nearest CWOP ids in the NWS list, 11–12 mi away, and D9413 reported null wind).
- TB buoy mast height is not published.
