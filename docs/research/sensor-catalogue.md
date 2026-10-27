# Windward Mark — per-spot sensor catalogue (research synthesis, 2026-10-26)

Merged from `bay_delta_stations.*`, `coast_tahoe_stations.*` and `networks.md`. Every row was live-checked on 2026-10-26 unless marked. 
**Status** = what a free hourly GitHub Actions job can do with it: `live` = read it now, token-free; `wave` = wave-only (no wind); `stale` = free but the only scripted copy (NWS/MADIS) lagged ~4 days at probe time; `view` = owner/subscription API, use as a link only; `offline` = not reporting.

`stations-proposed.json` holds the `live`+`wave` rows in the app's `stations.json` shape with a new `kind` per feed (`nws`, `ndbc`, `coops`, `raws`, `cencoos`, `jpl`, `cdec`, `iem`, `caltrans`, `cdip`).
Totals: {'view': 10, 'stale': 28, 'live': 97, 'wave': 11, 'offline': 3}. Spots with no research rows: none.

## Paradise Cay (home dock) (`paradisecay`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **KCABELVE30** Tiburon Yacht Club | Weather Underground PWS (view-only) | view | 0.1 | y | y | Ambient Weather WS-2902 at 3 ft elevation on the Paradise Cay waterfront (coords as WU shows, ~3 decimals); reported 13.2 gust 13.6 from 291 at 17:27 PDT 2026-10-26 (WU does not label units; PWS default is mph). Best pro |
| **KCATIBUR4** Mt. Tiburon | Weather Underground PWS (view-only) | view | 2.3 | y | y | Davis Vantage Pro2 at 565 ft on the Tiburon ridge; live 2026-10-26. Ridge-top, overreads the water on some days; view-only. |
| **WB6TTB** WB6TTB Tiburon | CWOP (view at aprs.fi; MADIS copy lagged) | stale | 2.4 | y | y | Hillside home station at ~172 m elevation on the Tiburon peninsula; live (00:18 UTC 2026-10-27, W 3.1 m/s gust 4.9). Terrain-sheltered; use for direction/trend only. |
| **TIBC1** Tiburon Pier (Romberg Tiburon Center), ERDDAP dataset tiburon-weather-tibc1 | CeNCOOS / SFSU Romberg Tiburon Center (NDBC-relayed) (stale at probe) | stale | 2.5 | y | y | Pier-mounted station on Richardson/Raccoon Strait shore of Tiburon, anemometer 10 m. STALE: ERDDAP time coverage ends 2026-09-24 and TIBC1 was absent from NDBC latest_obs on 2026-10-26. Check before relying on it. |
| **RCMC1** Richmond (Chevron Long Wharf / Berth 5) | NOAA CO-OPS 9414863 | live | 4.4 | y | y | On the Richmond Long Wharf across the channel from Paradise Cay; open-water exposure to W/SW. Best free scriptable sensor for this launch. |

## Crissy Field (`crissy`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **IKITESURF_CRISSY_ANITA_ROCK** Crissy Field (Anita Rock) sensor | iKitesurf/WeatherFlow (subscription) | view | 0.1 | y | y | COORDS APPROXIMATE (placed at Anita Rock off the beach; exact mount and spot id not found). Per Mike Godsey (WeatherFlow) it is accurate in NW ocean wind but reads well above the beach in WSW/eddy/marine-surge flow becau |
| **FTPC1** San Francisco (Fort Point) | NOAA CO-OPS 9414290 | live | 0.6 | y | y | On the Fort Point / Crissy Field seawall at the Golden Gate, 0.6 mi W of the launch; the station Windfinder labels "Crissy Field". Reads the ocean-wind side of the beach; the beach itself sits in the Presidio wind shadow |
| **GGBC1** Golden Gate Bridge | GOES/HADS via IEM | live | 1.7 | y | y | Bridge-mounted anemometer (NWS lists 82 m elevation); reports wind and gust at 15-min cadence. High above the water, so it overreads surface wind; good for gradient/eddy direction. |
| **PXOC1** San Francisco Pier 1 | NOAA CO-OPS 9414311 | live | 3.3 | y | y | Ferry Building waterfront, 3.3 mi E; 16 m anemometer, city-side wind. Secondary. |
| **46026** San Francisco (18 NM W of SF) | NDBC | live | 21.3 | y | y | Offshore ocean reference 21 mi W; shows the NW ocean wind feeding the Gate, not the beach. Note 46237 (SF Bar) reports waves only, no wind. |

## Candlestick Point (`candlestick`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **GW3010** GW3010 San Francisco (Bayview) | CWOP (view at aprs.fi; MADIS copy lagged) | stale | 1.7 | y | y | Ambient-Weather home station at ~53 m elevation 1.7 mi NW, inland of the point; readings near zero while PORTS stations showed 10-15 kn, so sheltered. Trend only. |
| **K6POO-1** K6POO-1 Brisbane | CWOP (view at aprs.fi; MADIS copy lagged) | stale | 2.0 | y | y | 2.0 mi S in Brisbane at ~37 m; sheltered (near-zero readings on a windy afternoon). Trend only. |
| **KSFO** San Francisco International Airport | NWS/FAA airport (METAR) | live | 6.1 | y | y | Bayside airport 6 mi S; standard 10 m ASOS (height assumed per ASOS siting, not confirmed). Hourly METAR; gust only in strong wind. Closest well-exposed free sensor; Candlestick is usually windier than SFO in the W-NW ga |
| **PXOC1** San Francisco Pier 1 | NOAA CO-OPS 9414311 | live | 6.3 | y | y | 6.3 mi N on the Embarcadero; 6-min with gusts. Different exposure (city waterfront). |
| **AAMC1** Alameda (former NAS Alameda) | NOAA CO-OPS 9414750 | live | 6.5 | y | y | Across the bay 6.5 mi NE; same W sea-breeze regime. 6-min with gusts. |

## Third Avenue (Baywinds Park) (`thirdave`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **N6OL** N6OL San Mateo (bayfront) | CWOP (view at aprs.fi; MADIS copy lagged) | stale | 1.7 | y | y | Davis/Cumulus home station at 4 m elevation on the San Mateo bayfront between Coyote Point and 3rd Ave, 1.7 mi W; live with gusts. Reads lower than open water (2.7 m/s when SFO had ~10 kn). |
| **DW3499** DW3499 Foster City | CWOP (view at aprs.fi; MADIS copy lagged) | stale | 2.6 | y | y | Davis VP2 at 2 m elevation in residential Foster City 2.6 mi S; reported 0 wind during a windy afternoon, so badly sheltered. Not useful for wind; listed for completeness. |
| **KSQL** San Carlos Airport | NWS/FAA airport (METAR) | live | 4.8 | y | y | Bayside airport 4.8 mi SE; hourly METAR (gust only when reported); NW channel wind reaches it. Height assumed 10 m. |
| **KSFO** San Francisco International Airport | NWS/FAA airport (METAR) | live | 5.2 | y | y | 5.2 mi NW; the upwind airport for the 3rd Ave/Coyote W-NW sea breeze. |
| **RTYC1** Redwood City (Port of Redwood City) | NOAA CO-OPS 9414523 | live | 6.5 | y | y | Only on-the-water PORTS sensor in the South Bay, 6.4 mi SE at the port; 6-min with gusts. NOTE: RTYC1 is Redwood City, not Richmond YC. Locals read the paid iKitesurf "3rd Ave" (beach) and "3rd Ave Channel" sensors; the  |

## Coyote Point (`coyote`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **N6OL** N6OL San Mateo (bayfront) | CWOP (view at aprs.fi; MADIS copy lagged) | stale | 0.6 | y | y | 0.6 mi SE of the Coyote Point launch at 4 m elevation; live with gusts. Closest sensor of any network; sheltered relative to the water. |
| **KM6RDV** KM6RDV San Mateo | CWOP (view at aprs.fi; MADIS copy lagged) | stale | 1.8 | y | y | 1.8 mi S at ~10 m; near-zero readings on a windy afternoon, sheltered. Trend only. |
| **KSFO** San Francisco International Airport | NWS/FAA airport (METAR) | live | 3.3 | y | y | 3.3 mi NW, directly upwind in the NW sea breeze; best free scriptable proxy for Coyote Point. |
| **KSQL** San Carlos Airport | NWS/FAA airport (METAR) | live | 6.3 | y | y | 6.6 mi SE, downwind airport. |
| **RTYC1** Redwood City | NOAA CO-OPS 9414523 | live | 8.3 | y | y | 8.2 mi SE on the water; 6-min with gusts. Paid iKitesurf "Coyote Point" sensor exists (location/id not found). |

## Alameda (Crown Beach) (`alameda`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **AAMC1** Alameda (former NAS Alameda, Oakland estuary mouth) | NOAA CO-OPS 9414750 | live | 1.8 | y | y | 1.8 mi NW of Crown Beach on the old Navy pier; open W exposure; 6-min with gusts. Best free sensor for Crown Beach. |
| **DW9579** DW9579 Alameda | CWOP (view at aprs.fi; MADIS copy lagged) | stale | 2.0 | y | y | Davis station at 4 m elevation on Alameda Point 2.0 mi NW; live (W 5.8 m/s gust 8.0 at 00:19 UTC 2026-10-27, vs AAMC1 12 kn). Reads ~0.5x the pier. |
| **LNDC1** Oakland Berth 67 | NOAA CO-OPS 9414763 | live | 2.6 | y | y | Inner-harbor berth 2.6 mi N; sheltered by port cranes. NOTE: LNDC1 is Oakland Berth 67, not Mare Island. |
| **KOAK** Oakland International Airport | NWS/FAA airport (METAR) | live | 3.7 | y | y | 3.7 mi SE on the bay shore; hourly METAR. Paid iKitesurf "Alameda" sensor exists (location/id not found). |

## Berkeley Marina (Hs Lordships beach) (`berkeley`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **KJ6WEG** KJ6WEG Berkeley | CWOP (view at aprs.fi; MADIS copy lagged) | stale | 1.7 | y | y | Residential station 1.7 mi E at ~32 m; near-zero readings while the bay blew 10-15 kn, so sheltered. Direction/trend only. |
| **IKITESURF_BERKELEY_REEF** Berkeley Reef (Olympic Circle) sensor | iKitesurf/WeatherFlow (subscription) | view | 1.9 | y | y | COORDS APPROXIMATE (on a metal marker over the rocky reef off the Berkeley Marina; exact position not published). WeatherFlow says it is often the best reading for the Olympic Circle; repairs need a boat and USCG permiss |
| **OKXC1** Oakland Berth 34 | NOAA CO-OPS 9414776 | live | 3.8 | y | y | Outer-harbor berth 3.8 mi S, open to the W through the Gate gap; 6-min with gusts. Best free scriptable sensor for the Berkeley/Emeryville shore. |
| **PPXC1** Point Potrero, Richmond | NOAA CO-OPS 9414847 | live | 4.0 | y | y | 4.0 mi NW on the Richmond harbor entrance; 6-min with gusts; anemometer height not published. On NDBC/CO-OPS only (not on api.weather.gov). |
| **RCMC1** Richmond (Chevron Long Wharf) | NOAA CO-OPS 9414863 | live | 6.5 | y | y | 6.6 mi NW; upwind of the Berkeley flats in NW flow. |

## Point Isabel (`pointisabel`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **GW5483** GW5483 Richmond | CWOP (view at aprs.fi; MADIS copy lagged) | stale | 1.1 | y | y | 1.1 mi NE at 7 m, inland of the shoreline; near-zero readings on a windy afternoon, sheltered. Trend only. |
| **DW7213** DW7213 Richmond (Marina Bay waterfront) | CWOP (view at aprs.fi; MADIS copy lagged) | stale | 2.0 | y | y | Davis station at 0 m elevation on the Richmond Marina Bay shoreline 1.7 mi W; live with gusts (W 256 5.4 m/s gust 7.6 at 00:15 UTC 2026-10-27) and tracks the PORTS stations, so apparently well exposed. Closest useful fre |
| **PPXC1** Point Potrero, Richmond | NOAA CO-OPS 9414847 | live | 2.3 | y | y | 2.3 mi W at the Richmond harbor mouth; 6-min with gusts; best free scriptable sensor. Height not published. |
| **KCACALIF93** Richmond Yacht Club (Brickyard Cove) | Weather Underground PWS (view-only) | view | 3.2 | y | y | Davis VP2 run by the yacht club at Brickyard Cove 3.3 mi W; live with gusts (12 g14 from 248 at 17:25 PDT 2026-10-26). View-only. |
| **RCMC1** Richmond (Chevron Long Wharf) | NOAA CO-OPS 9414863 | live | 4.6 | y | y | 4.6 mi W, upwind on the Long Wharf. Paid iKitesurf "Pt. Isabel" sensor exists (location/id not found). |

## Toll Plaza (Radio Beach) (`tollplaza`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **OKXC1** Oakland Berth 34 | NOAA CO-OPS 9414776 | live | 1.7 | y | y | 1.7 mi S at the outer harbor, same W exposure as Radio Beach; 6-min with gusts. Best free sensor. |
| **OMHC1** Oakland Middle Harbor Met | NOAA CO-OPS 9414769 | live | 2.2 | y | y | 2.2 mi S; met-only PORTS site, 6-min with gusts; also on api.weather.gov. |
| **LNDC1** Oakland Berth 67 | NOAA CO-OPS 9414763 | live | 2.7 | y | y | 2.7 mi SE in the inner harbor; more sheltered. |
| **AAMC1** Alameda | NOAA CO-OPS 9414750 | live | 3.9 | y | y | 3.9 mi S. Paid iKitesurf "Treasure Island" sensor is the local reference for this stretch (location/id not found). OBXC1 Berth 38 is visibility-only (no wind). |

## Racetrack (Albany Beach) (`racetrack`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **GW5483** GW5483 Richmond | CWOP (view at aprs.fi; MADIS copy lagged) | stale | 1.6 | y | y | 1.6 mi N, inland and sheltered; trend only. |
| **IKITESURF_BERKELEY_REEF** Berkeley Reef (Olympic Circle) sensor | iKitesurf/WeatherFlow (subscription) | view | 2.8 | y | y | COORDS APPROXIMATE. On-the-water reef marker; view-only. |
| **DW7213** DW7213 Richmond (Marina Bay waterfront) | CWOP (view at aprs.fi; MADIS copy lagged) | stale | 2.9 | y | y | 2.7 mi NW on the shoreline, live with gusts; closest exposed free sensor. |
| **PPXC1** Point Potrero, Richmond | NOAA CO-OPS 9414847 | live | 3.2 | y | y | 3.2 mi NW; 6-min with gusts; best free scriptable sensor. |
| **OKXC1** Oakland Berth 34 | NOAA CO-OPS 9414776 | live | 5.4 | y | y | 5.4 mi S; 6-min with gusts. |

## Point Emery (`pointemery`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **KJ6WEG** KJ6WEG Berkeley | CWOP (view at aprs.fi; MADIS copy lagged) | stale | 2.0 | y | y | 2.0 mi NE, residential and sheltered; trend only. A4539 "Berkeley Aquatic Park" (37.8648,-122.3027, 1.7 mi) is listed by NWS but returns no observations; unverified. |
| **OKXC1** Oakland Berth 34 | NOAA CO-OPS 9414776 | live | 2.6 | y | y | 2.6 mi S across the Emeryville flats; 6-min with gusts. Best free sensor. |
| **OMHC1** Oakland Middle Harbor Met | NOAA CO-OPS 9414769 | live | 3.1 | y | y | 3.1 mi S; 6-min with gusts. |
| **LNDC1** Oakland Berth 67 | NOAA CO-OPS 9414763 | live | 3.3 | y | y | 3.3 mi S, inner harbor, more sheltered. |
| **AAMC1** Alameda | NOAA CO-OPS 9414750 | live | 4.7 | y | y | 4.7 mi S; 6-min with gusts. |

## Sherman Island (County Park) (`sherman`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **IKITESURF_SHERMAN_12_14** Sherman Island sensors #12 and #14 | iKitesurf/WeatherFlow (subscription) | view | 0.0 | y | y | COORDS = launch (sensor positions not published). Two WeatherFlow sensors on the river; forum users say #12 is nearer the main kiting area, and the sensors can read WSW when kiters feel SW. The sensor locals actually use |
| **519PG** Bridgehead (Antioch) | mesonet via NWS/MADIS (lagged days) | stale | 3.6 | y | y | 3.6 mi SE near the Antioch Bridge approach at 12 m; 10-min wind/gust/dir. Land station; use with the PORTS reading. |
| **606PG** Pittsburg 3rd Ave | mesonet via NWS/MADIS (lagged days) | stale | 4.0 | y | y | 4.0 mi W at 4 m elevation in Pittsburg; 10-min wind/gust. |
| **IKITESURF_100721** Pittsburg Marina sensor | iKitesurf/WeatherFlow (subscription) | view | 4.3 | y | y | COORDS APPROXIMATE (Windfinder lists "Pittsburg Marina" 5.5 km from Antioch marina). Free iKitesurf account shows the current reading. Recommended on bayareakiteboarding.com for Bay Point; also upwind of Sherman. CDEC AN |
| **PSBC1** Pittsburg (Suisun Bay) | NOAA CO-OPS 9415115 | live | 4.4 | y | y | 4.4 mi W on the Pittsburg waterfront, upwind in the W-SW Delta flow; 6-min with gusts. Best free scriptable sensor for Sherman Island. NOTE: PSBC1 is Pittsburg, not San Mateo Bridge. |

## Rio Vista (Windy Cove / Sandy Beach) (`windycove`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **RVB** Sacramento River at Rio Vista Bridge | CDEC | live | 1.3 | - | y | 1.3 mi N at the bridge; CDEC lists wind speed (9) and direction (10) sensors but every 15-min and hourly value on 2026-10-26 was -9999 (no data). Same for ANH, MAL, GZL, FRK, MRZ, BDL. Treat DWR Delta wind as not live. |
| **CF105** SR-12 - SR-160 (Rio Vista Bridge) | Caltrans RWIS | live | 1.4 | y | y | 1.4 mi NE at the Rio Vista bridge, right on the river. UNVERIFIED LIVE: wind fields were null in the NWS feed the week of 2026-10-22 and Windfinder showed "no data"; the Caltrans endpoint was down. Check before use. |
| **TCICA** Twitchell Island | mesonet via NWS/MADIS (lagged days) | stale | 2.6 | - | y | COORDS from NWS CI140 entry (CIMIS lists 140 Twitchell Island nearby). Agricultural station, 2 m anemometer, hourly mean, no gust. 2.6-3.8 mi S across the river; flat Delta exposure. |
| **CF106** SR-12 - Brannan Island Road | Caltrans RWIS | live | 6.0 | y | y | 6.0 mi E on SR-12 at Brannan Island Rd; reported wind + gust + dir at 10-min cadence (7.2 km/h g8.6 at 13:10Z 2026-10-22). Roadside, flat Delta exposure. |
| **493PG** Grand Island | mesonet via NWS/MADIS (lagged days) | stale | 6.5 | y | y | 6.5 mi NE in the Delta islands at 6 m; 10-min wind/gust. Also 495PG Birds Landing Road (38.1381,-121.8341, 74 m, 7.6 mi W). A paid iKitesurf "Rio Vista" sensor is believed to exist but was not verified. |

## Bay Point (McAvoy Rd) (`baypoint`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **EW9715** EW9715 Pittsburg (Bay Point area) | CWOP (view at aprs.fi; MADIS copy lagged) | stale | 2.0 | y | y | 2.0 mi SE at 25 m in a residential area; near-zero readings while PORTS showed 13 kn; sheltered, trend only. |
| **PSBC1** Pittsburg (Suisun Bay) | NOAA CO-OPS 9415115 | live | 4.1 | y | y | 4.1 mi E on the Pittsburg waterfront, downwind; 6-min with gusts. |
| **IKITESURF_100721** Pittsburg Marina sensor | iKitesurf/WeatherFlow (subscription) | view | 4.3 | y | y | COORDS APPROXIMATE. The sensor bayareakiteboarding.com recommends for Bay Point/McAvoy; free account shows the current reading, no API. |
| **PCOC1** Port Chicago | NOAA CO-OPS 9415144 | live | 4.3 | y | y | 4.3 mi W on the Suisun Bay pier, upwind of McAvoy in W flow; 6-min with gusts; also on api.weather.gov. Best free sensor. |
| **KCCR** Concord, Buchanan Field | NWS/FAA airport (METAR) | live | 6.3 | y | y | 6.3 mi SW inland; hourly METAR. CDEC MAL (Mallard Island, 38.0428,-121.9201, 2.3 mi) lists wind but returned -9999 on 2026-10-26. |

## Folsom Lake - Granite Bay (`granitebay`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **KCAGRANI20** Granite Bay mixed rural, residential | Weather Underground PWS (view-only) | view | 0.4 | y | y | 0.4 mi W, Davis VP2 Plus at 390 ft, but OFFLINE on 2026-10-26 (no wind data). View-only when up. |
| **PG882** Quinn Place (Granite Bay) | mesonet via NWS/MADIS (lagged days) | stale | 2.9 | y | y | 2.9 mi N at 143 m; 10-min wind/gust/dir (9.3 km/h g18.5 at 13:10Z 2026-10-22). Land station in oak foothills. |
| **FLD** Folsom Dam - Folsom Point (Dyke 8) | CDEC | live | 3.8 | - | y | On the dam dyke at the lake shore 3.9 mi S; the only live free wind sensor on Folsom Lake found. No gust. Elevation 350 ft; anemometer height not published. |
| **144PG** Atlantic Gold Hill (Folsom) | mesonet via NWS/MADIS (lagged days) | stale | 5.9 | y | y | 5.9 mi S at 109 m; 10-min wind/gust. |
| **KMHR** Sacramento Mather Airport | NWS/FAA airport (METAR) | live | 13.9 | y | y | 13.9 mi SW on the valley floor; hourly METAR; gradient reference only. Locals use a paid iKitesurf "Folsom Lake" sensor (per bayareakiteboarding: fair in N wind until the 20s; add ~5 mph in S wind); its location/id was n |

## Folsom Lake - Folsom Point (`folsompoint`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **FLD** Folsom Dam - Folsom Point (Dyke 8) | CDEC | live | 0.8 | - | y | 0.9 mi SW on Dyke 8 beside the Folsom Point launch; live 15-min wind and direction, no gust. Closest sensor of any network. |
| **144PG** Atlantic Gold Hill (Folsom) | mesonet via NWS/MADIS (lagged days) | stale | 3.3 | y | y | 3.3 mi S at 109 m; 10-min wind/gust/dir. |
| **GW6439** GW6439 Folsom | CWOP (view at aprs.fi; MADIS copy lagged) | stale | 4.0 | - | y | 4.0 mi SE residential; near-zero readings; trend only. |
| **PG111** Arroyo Vista (El Dorado Hills) | mesonet via NWS/MADIS (lagged days) | stale | 4.3 | y | y | 4.3 mi E at 329 m on the El Dorado Hills ridge; 10-min wind/gust; hilltop overreads the lake. |
| **PG882** Quinn Place (Granite Bay) | mesonet via NWS/MADIS (lagged days) | stale | 5.6 | y | y | 5.9 mi NW; 10-min wind/gust. |

## Stinson Beach (`stinson`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **MDEC1** Middle Peak RAWS (Mt Tamalpais) | RAWS via IEM/FEMS | live | 3.7 | y | y | Hourly RAWS, live 2026-10-26 23:36Z (8 mph G14 @316). 587 m up on Tam, 3.7 mi NE of Stinson: a ridge-top gradient/gust indicator, not the beach-level sea breeze. |
| **CDIP 142 / NDBC 46237** San Francisco Bar CDIP 142 (Datawell directional) | CDIP wave buoy | wave | 7.6 | - | y | WAVE SENSOR, no wind. Reports Hs, peak period Tp, peak direction Dp every 30 min. Live 2026-10-26 (Hs 0.85-1.1 m, Tp 13-14 s, Dp 230-278). 16 m depth just outside the Golden Gate bar; directly off Stinson/Ocean Beach so  |
| **BBEC1** Barnaby RAWS (Bolinas Ridge / Olema) | RAWS via IEM/FEMS | live | 9.6 | y | y | Hourly RAWS, live 2026-10-26 (3 mph G18 @295), 247 m, 9.6 mi NW of Stinson on Bolinas Ridge. NW-exposed ridge; backup. |
| **GGBC1** Golden Gate Bridge center span | GOES/HADS via IEM | live | 10.5 | y | y | Bridge-deck anemometer (~70 m above water, roughly; height unverified). Live hourly in IEM CA_DCP 2026-10-26 (USIRGZZ, UDIRGZZ, UPCRGZZ). Units not documented in the feed (looked like mph/knots); verify against FTPC1 bef |
| **FTPC1 (NOS 9414290)** Fort Point / Crissy Field, Golden Gate | NOAA CO-OPS | live | 11.6 | y | y | Anemometer 7 m. 6-minute wind, gust, direction. Measures the Gate's westerly jet, not the open-coast NW wind, but it is the closest fully-public live anemometer to Ocean Beach north end (3.4 mi). |
| **46026** San Francisco buoy, 18 NM W of SF | NDBC | live | 14.7 | y | y | Offshore 3-m foam buoy, anemometer 4 m. Open-ocean wind; good NW-wind proxy for the whole SF-Marin coast but 15+ mi offshore so it misses the sea-breeze acceleration on the beach. Also reports WVHT/DPD/MWD (waves). Live  |
| **CDIP 029 / NDBC 46214** Point Reyes CDIP 029 (Datawell directional) | CDIP wave buoy | wave | 44.9 | - | y | WAVE SENSOR, no wind. Reports Hs, peak period Tp, peak direction Dp every 30 min. Live 2026-10-26 (Hs 2.1 m, Tp 12-15 s, Dp ~171-311). 600 m depth, 34 mi W of Bodega/Dillon; the reference offshore swell buoy for the Sono |

## Ocean Beach (north end) (`oceanbeach`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **FTPC1 (NOS 9414290)** Fort Point / Crissy Field, Golden Gate | NOAA CO-OPS | live | 3.4 | y | y | Anemometer 7 m. 6-minute wind, gust, direction. Measures the Gate's westerly jet, not the open-coast NW wind, but it is the closest fully-public live anemometer to Ocean Beach north end (3.4 mi). |
| **GGBC1** Golden Gate Bridge center span | GOES/HADS via IEM | live | 3.6 | y | y | Bridge-deck anemometer (~70 m above water, roughly; height unverified). Live hourly in IEM CA_DCP 2026-10-26 (USIRGZZ, UDIRGZZ, UPCRGZZ). Units not documented in the feed (looked like mph/knots); verify against FTPC1 bef |
| **CDIP 142 / NDBC 46237** San Francisco Bar CDIP 142 (Datawell directional) | CDIP wave buoy | wave | 6.7 | - | y | WAVE SENSOR, no wind. Reports Hs, peak period Tp, peak direction Dp every 30 min. Live 2026-10-26 (Hs 0.85-1.1 m, Tp 13-14 s, Dp 230-278). 16 m depth just outside the Golden Gate bar; directly off Stinson/Ocean Beach so  |
| **MDEC1** Middle Peak RAWS (Mt Tamalpais) | RAWS via IEM/FEMS | live | 11.6 | y | y | Hourly RAWS, live 2026-10-26 23:36Z (8 mph G14 @316). 587 m up on Tam, 3.7 mi NE of Stinson: a ridge-top gradient/gust indicator, not the beach-level sea breeze. |
| **KSFO** San Francisco Intl Airport | NWS/FAA airport (METAR) | live | 13.4 | y | y | Hourly METAR + specials, gusts. Bayside, not coastal; the NWS API 'latest' showed null wind on 2026-10-26 (use the observations list, not latest). Backup only. |
| **46026** San Francisco buoy, 18 NM W of SF | NDBC | live | 17.9 | y | y | Offshore 3-m foam buoy, anemometer 4 m. Open-ocean wind; good NW-wind proxy for the whole SF-Marin coast but 15+ mi offshore so it misses the sea-breeze acceleration on the beach. Also reports WVHT/DPD/MWD (waves). Live  |

## Half Moon Bay (Dunes Beach) (`hmb`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **KHAF** Half Moon Bay Airport | NWS/FAA airport (METAR) | live | 3.2 | y | y | ASOS/AWOS 20-min METAR, ~10 m mast (standard; height not published), gusts reported (27.7 km/h gust 2026-10-26 22:55Z). Sits on the flat behind Pillar Point Harbor, 0.5 mi from the water; excellent proxy for Pillar Point |
| **HSPC1** Spring Valley RAWS (above Half Moon Bay) | RAWS via IEM/FEMS | live | 5.2 | y | y | Hourly RAWS, live 2026-10-26 23:18Z (9 mph G20 @252), 314 m on Montara Mountain's south flank, 5 mi NE of Pillar Point. Hilltop gust reference; secondary. |
| **CDIP 142 / NDBC 46237** San Francisco Bar CDIP 142 (Datawell directional) | CDIP wave buoy | wave | 23.0 | - | y | WAVE SENSOR, no wind. Reports Hs, peak period Tp, peak direction Dp every 30 min. Live 2026-10-26 (Hs 0.85-1.1 m, Tp 13-14 s, Dp 230-278). 16 m depth just outside the Golden Gate bar; directly off Stinson/Ocean Beach so  |
| **46012** Half Moon Bay buoy (currently a Saildrone USV), 24 NM SSW of SF | NDBC | live | 25.2 | y | y | CAUTION: the fixed 46012 buoy is not on station; NDBC serves 46012 from a Saildrone uncrewed surface vehicle (anemometer 1.3 m, watch circle ~20,000 yd) since 2023-24; position drifts and data have gaps between deploymen |
| **46026** San Francisco buoy, 18 NM W of SF | NDBC | live | 27.8 | y | y | Offshore 3-m foam buoy, anemometer 4 m. Open-ocean wind; good NW-wind proxy for the whole SF-Marin coast but 15+ mi offshore so it misses the sea-breeze acceleration on the beach. Also reports WVHT/DPD/MWD (waves). Live  |

## Pillar Point Harbor (winter south) (`pillarpoint`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **KHAF** Half Moon Bay Airport | NWS/FAA airport (METAR) | live | 0.9 | y | y | ASOS/AWOS 20-min METAR, ~10 m mast (standard; height not published), gusts reported (27.7 km/h gust 2026-10-26 22:55Z). Sits on the flat behind Pillar Point Harbor, 0.5 mi from the water; excellent proxy for Pillar Point |
| **HSPC1** Spring Valley RAWS (above Half Moon Bay) | RAWS via IEM/FEMS | live | 5.0 | y | y | Hourly RAWS, live 2026-10-26 23:18Z (9 mph G20 @252), 314 m on Montara Mountain's south flank, 5 mi NE of Pillar Point. Hilltop gust reference; secondary. |
| **CDIP 142 / NDBC 46237** San Francisco Bar CDIP 142 (Datawell directional) | CDIP wave buoy | wave | 21.2 | - | y | WAVE SENSOR, no wind. Reports Hs, peak period Tp, peak direction Dp every 30 min. Live 2026-10-26 (Hs 0.85-1.1 m, Tp 13-14 s, Dp 230-278). 16 m depth just outside the Golden Gate bar; directly off Stinson/Ocean Beach so  |
| **46012** Half Moon Bay buoy (currently a Saildrone USV), 24 NM SSW of SF | NDBC | live | 23.8 | y | y | CAUTION: the fixed 46012 buoy is not on station; NDBC serves 46012 from a Saildrone uncrewed surface vehicle (anemometer 1.3 m, watch circle ~20,000 yd) since 2023-24; position drifts and data have gaps between deploymen |
| **46026** San Francisco buoy, 18 NM W of SF | NDBC | live | 25.6 | y | y | Offshore 3-m foam buoy, anemometer 4 m. Open-ocean wind; good NW-wind proxy for the whole SF-Marin coast but 15+ mi offshore so it misses the sea-breeze acceleration on the beach. Also reports WVHT/DPD/MWD (waves). Live  |

## Gazos Creek State Beach (`gazos`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **BNDC1** Ben Lomond RAWS | RAWS via IEM/FEMS | live | 10.9 | y | y | Hourly RAWS (3 mph G12 @336 on 2026-10-26), 800 m up in the Santa Cruz Mountains behind Waddell; shows ridge gradient only, often calm when the coast is nuking. Low value for beach wind. |
| **LAHC1** La Honda RAWS | RAWS via IEM/FEMS | live | 11.0 | y | y | Hourly RAWS (2 mph G10 on 2026-10-26), 245 m inland at La Honda; backup only. |
| **XCDC1** Coast Dairies RAWS (Davenport) | RAWS via IEM/FEMS | live | 13.7 | y | y | Hourly RAWS, live 2026-10-26 23:09Z (13 mph G27 @294), 198 m on the coastal terrace/hills 2.4 mi E of Davenport. The closest public live anemometer to Davenport/Scott Creek; on the marine terrace so it sees the NW sea br |
| **CDIP 254 / NDBC 46269** Point Santa Cruz CDIP 254 | CDIP (offline) | offline | 24.5 | - | y | 20 m depth off Lighthouse Point, Santa Cruz; the ideal nearshore wave reference for Waddell/Davenport/Gazos when it is deployed. Same status (404/absent) for CDIP 158 / NDBC 46240 Cabrillo Point, CDIP 185 / NDBC 46114 We |
| **KHAF** Half Moon Bay Airport | NWS/FAA airport (METAR) | live | 24.8 | y | y | ASOS/AWOS 20-min METAR, ~10 m mast (standard; height not published), gusts reported (27.7 km/h gust 2026-10-26 22:55Z). Sits on the flat behind Pillar Point Harbor, 0.5 mi from the water; excellent proxy for Pillar Point |
| **46042** Monterey buoy, 27 NM WNW of Monterey | NDBC | live | 26.7 | y | y | Offshore 3-m foam buoy, anemometer 4 m. Wind, gust, waves (WVHT/DPD/MWD) live 2026-10-26. The standard open-ocean reference for Monterey Bay; 20+ mi offshore. |
| **46012** Half Moon Bay buoy (currently a Saildrone USV), 24 NM SSW of SF | NDBC | live | 31.2 | y | y | CAUTION: the fixed 46012 buoy is not on station; NDBC serves 46012 from a Saildrone uncrewed surface vehicle (anemometer 1.3 m, watch circle ~20,000 yd) since 2023-24; position drifts and data have gaps between deploymen |
| **CDIP 156 / NDBC 46236** Monterey Canyon Outer CDIP 156 (Datawell directional) | CDIP wave buoy | wave | 36.5 | - | y | WAVE SENSOR, no wind. Reports Hs, peak period Tp, peak direction Dp every 30 min. Live 2026-10-26 (Hs 0.85-1.1 m, Tp 9.5-11 s, Dp 294-298). 133 m depth in mid-bay, 9 mi NW of Marina; the only CDIP buoy in Monterey Bay cu |

## Waddell Creek (`waddell`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **BNDC1** Ben Lomond RAWS | RAWS via IEM/FEMS | live | 6.2 | y | y | Hourly RAWS (3 mph G12 @336 on 2026-10-26), 800 m up in the Santa Cruz Mountains behind Waddell; shows ridge gradient only, often calm when the coast is nuking. Low value for beach wind. |
| **XCDC1** Coast Dairies RAWS (Davenport) | RAWS via IEM/FEMS | live | 6.7 | y | y | Hourly RAWS, live 2026-10-26 23:09Z (13 mph G27 @294), 198 m on the coastal terrace/hills 2.4 mi E of Davenport. The closest public live anemometer to Davenport/Scott Creek; on the marine terrace so it sees the NW sea br |
| **santa-cruz-wharf-weather-stat** Santa Cruz Municipal Wharf weather station | CeNCOOS ERDDAP | live | 17.0 | y | y | Hourly mean + gust, m/s. Live 2026-10-26 23:00Z. End of the wharf, inside Monterey Bay's north shelter; it under-reads the NW wind that Waddell/Davenport/Gazos ride (those are outside the Santa Cruz lee). Height not publ |
| **CDIP 254 / NDBC 46269** Point Santa Cruz CDIP 254 | CDIP (offline) | offline | 17.5 | - | y | 20 m depth off Lighthouse Point, Santa Cruz; the ideal nearshore wave reference for Waddell/Davenport/Gazos when it is deployed. Same status (404/absent) for CDIP 158 / NDBC 46240 Cabrillo Point, CDIP 185 / NDBC 46114 We |
| **46042** Monterey buoy, 27 NM WNW of Monterey | NDBC | live | 22.5 | y | y | Offshore 3-m foam buoy, anemometer 4 m. Wind, gust, waves (WVHT/DPD/MWD) live 2026-10-26. The standard open-ocean reference for Monterey Bay; 20+ mi offshore. |
| **46092 (MBARI M1)** MBARI M1 mooring, central Monterey Bay | NDBC | live | 27.5 | - | y | Anemometer 4 m. NDBC feed had WSPD+WDIR but no gust and no waves on 2026-10-26; ERDDAP copy lagged ~3 days. Mid-bay wind, upwind of Marina on a NW day. |
| **CDIP 156 / NDBC 46236** Monterey Canyon Outer CDIP 156 (Datawell directional) | CDIP wave buoy | wave | 29.5 | - | y | WAVE SENSOR, no wind. Reports Hs, peak period Tp, peak direction Dp every 30 min. Live 2026-10-26 (Hs 0.85-1.1 m, Tp 9.5-11 s, Dp 294-298). 133 m depth in mid-bay, 9 mi NW of Marina; the only CDIP buoy in Monterey Bay cu |

## Davenport (Scott Creek) (`davenport`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **XCDC1** Coast Dairies RAWS (Davenport) | RAWS via IEM/FEMS | live | 2.4 | y | y | Hourly RAWS, live 2026-10-26 23:09Z (13 mph G27 @294), 198 m on the coastal terrace/hills 2.4 mi E of Davenport. The closest public live anemometer to Davenport/Scott Creek; on the marine terrace so it sees the NW sea br |
| **BNDC1** Ben Lomond RAWS | RAWS via IEM/FEMS | live | 7.0 | y | y | Hourly RAWS (3 mph G12 @336 on 2026-10-26), 800 m up in the Santa Cruz Mountains behind Waddell; shows ridge gradient only, often calm when the coast is nuking. Low value for beach wind. |
| **santa-cruz-wharf-weather-stat** Santa Cruz Municipal Wharf weather station | CeNCOOS ERDDAP | live | 12.9 | y | y | Hourly mean + gust, m/s. Live 2026-10-26 23:00Z. End of the wharf, inside Monterey Bay's north shelter; it under-reads the NW wind that Waddell/Davenport/Gazos ride (those are outside the Santa Cruz lee). Height not publ |
| **CDIP 254 / NDBC 46269** Point Santa Cruz CDIP 254 | CDIP (offline) | offline | 13.1 | - | y | 20 m depth off Lighthouse Point, Santa Cruz; the ideal nearshore wave reference for Waddell/Davenport/Gazos when it is deployed. Same status (404/absent) for CDIP 158 / NDBC 46240 Cabrillo Point, CDIP 185 / NDBC 46114 We |
| **46042** Monterey buoy, 27 NM WNW of Monterey | NDBC | live | 20.1 | y | y | Offshore 3-m foam buoy, anemometer 4 m. Wind, gust, waves (WVHT/DPD/MWD) live 2026-10-26. The standard open-ocean reference for Monterey Bay; 20+ mi offshore. |
| **46092 (MBARI M1)** MBARI M1 mooring, central Monterey Bay | NDBC | live | 22.9 | - | y | Anemometer 4 m. NDBC feed had WSPD+WDIR but no gust and no waves on 2026-10-26; ERDDAP copy lagged ~3 days. Mid-bay wind, upwind of Marina on a NW day. |
| **CDIP 156 / NDBC 46236** Monterey Canyon Outer CDIP 156 (Datawell directional) | CDIP wave buoy | wave | 24.9 | - | y | WAVE SENSOR, no wind. Reports Hs, peak period Tp, peak direction Dp every 30 min. Live 2026-10-26 (Hs 0.85-1.1 m, Tp 9.5-11 s, Dp 294-298). 133 m depth in mid-bay, 9 mi NW of Marina; the only CDIP buoy in Monterey Bay cu |

## Marina State Beach (`marina`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **KOAR** Marina Municipal Airport (ex Fort Ord Fritzsche AAF) | NWS/FAA airport (METAR) | live | 3.1 | y | y | AWOS 20-min with gusts (20.5 km/h G 25.9 @290 on 2026-10-26 22:55Z). 2 mi inland from Marina State Beach on the dune flat: the closest live anemometer to the beach and open to the NW sea breeze. Primary for Marina. |
| **monterey-bay-aquarium-weather** Monterey Bay Aquarium weather station (Cannery Row) | CeNCOOS ERDDAP | live | 6.7 | y | y | ~15-min updates, m/s, gust. Live 2026-10-26. On the Monterey Peninsula shore, in the lee for NW wind; useful as a 'south bay is lit' check, not as the Marina beach number. |
| **KMRY** Monterey Regional Airport | NWS/FAA airport (METAR) | live | 6.8 | y | y | ASOS, 5-min via NWS API list (18.5 km/h @280 on 2026-10-27 00:05Z), gust field often null. On the Monterey Peninsula, partly in the lee for NW; KOAR is the better Marina proxy. |
| **MLSC1** Moss Landing Marine Labs weather station | CeNCOOS ERDDAP | live | 8.2 | y | y | Anemometer 10 m (NDBC page). Also on NDBC as MLSC1 (realtime2 had WSPD but WDIR/GST 'MM' on 2026-10-26; ERDDAP copy had speed+dir+gust at 00:21Z). Shore station at Moss Landing harbor, 8 mi N of Marina on the same beach  |
| **CDIP 156 / NDBC 46236** Monterey Canyon Outer CDIP 156 (Datawell directional) | CDIP wave buoy | wave | 9.2 | - | y | WAVE SENSOR, no wind. Reports Hs, peak period Tp, peak direction Dp every 30 min. Live 2026-10-26 (Hs 0.85-1.1 m, Tp 9.5-11 s, Dp 294-298). 133 m depth in mid-bay, 9 mi NW of Marina; the only CDIP buoy in Monterey Bay cu |
| **46092 (MBARI M1)** MBARI M1 mooring, central Monterey Bay | NDBC | live | 12.8 | - | y | Anemometer 4 m. NDBC feed had WSPD+WDIR but no gust and no waves on 2026-10-26; ERDDAP copy lagged ~3 days. Mid-bay wind, upwind of Marina on a NW day. |
| **46042** Monterey buoy, 27 NM WNW of Monterey | NDBC | live | 33.7 | y | y | Offshore 3-m foam buoy, anemometer 4 m. Wind, gust, waves (WVHT/DPD/MWD) live 2026-10-26. The standard open-ocean reference for Monterey Bay; 20+ mi offshore. |

## Dillon Beach (`dillon`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **bodega-marine-laboratory-weather** UC Davis Bodega Marine Laboratory weather station | CeNCOOS ERDDAP | live | 7.3 | - | y | 5-min, m/s, speed+direction (no gust variable in the dataset). Live 2026-10-26 23:55Z (9.9 m/s @313). On Bodega Head's exposed west side; the best live NW-wind number for Bodega/Dillon. Height not published (z=0 in metad |
| **PRWC1** Point Reyes RCA station (near Point Reyes Station/Inverness) | GOES/HADS via IEM | live | 10.8 | y | y | Live 2026-10-26 23:20Z (15.5 / peak 20.5 from 326 deg; units undocumented, likely mph). Elevation 26 m near the head of Tomales Bay, NOT the Point Reyes headland (the NOS PRYC1 at the lighthouse area has no wind sensor). |
| **46013** Bodega Bay buoy, 48 NM NNW of SF | NDBC | live | 19.1 | y | y | Offshore 3-m discus buoy, anemometer ~3 m (station page). Wind + pressure live 2026-10-26; wave fields were 'MM' (missing) on that check, so do not rely on it for swell. Best open-ocean reference for Bodega/Dillon. |
| **KSTS** Santa Rosa / Sonoma County Airport | NWS/FAA airport (METAR) | live | 19.1 | y | y | ASOS hourly; inland. Backup only for Bodega/Dillon. |
| **CDIP 029 / NDBC 46214** Point Reyes CDIP 029 (Datawell directional) | CDIP wave buoy | wave | 34.4 | - | y | WAVE SENSOR, no wind. Reports Hs, peak period Tp, peak direction Dp every 30 min. Live 2026-10-26 (Hs 2.1 m, Tp 12-15 s, Dp ~171-311). 600 m depth, 34 mi W of Bodega/Dillon; the reference offshore swell buoy for the Sono |
| **46026** San Francisco buoy, 18 NM W of SF | NDBC | live | 35.2 | y | y | Offshore 3-m foam buoy, anemometer 4 m. Open-ocean wind; good NW-wind proxy for the whole SF-Marin coast but 15+ mi offshore so it misses the sea-breeze acceleration on the beach. Also reports WVHT/DPD/MWD (waves). Live  |

## Bodega Harbor (Doran) (`bodega`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **bodega-marine-laboratory-weather** UC Davis Bodega Marine Laboratory weather station | CeNCOOS ERDDAP | live | 1.7 | - | y | 5-min, m/s, speed+direction (no gust variable in the dataset). Live 2026-10-26 23:55Z (9.9 m/s @313). On Bodega Head 1.7 mi W of Doran; exposed to the NW wind that Doran rides side-on, so expect Doran to read lower. Heig |
| **46013** Bodega Bay buoy, 48 NM NNW of SF | NDBC | live | 16.2 | y | y | Offshore 3-m discus buoy, anemometer ~3 m (station page). Wind + pressure live 2026-10-26; wave fields were 'MM' (missing) on that check, so do not rely on it for swell. Best open-ocean reference for Bodega/Dillon. |
| **PRWC1** Point Reyes RCA station (near Point Reyes Station/Inverness) | GOES/HADS via IEM | live | 16.5 | y | y | Live 2026-10-26 23:20Z (15.5 / peak 20.5 from 326 deg; units undocumented, likely mph). Elevation 26 m near the head of Tomales Bay, NOT the Point Reyes headland (the NOS PRYC1 at the lighthouse area has no wind sensor). |
| **KSTS** Santa Rosa / Sonoma County Airport | NWS/FAA airport (METAR) | live | 17.2 | y | y | ASOS hourly; inland. Backup only for Bodega/Dillon. |
| **CDIP 029 / NDBC 46214** Point Reyes CDIP 029 (Datawell directional) | CDIP wave buoy | wave | 34.9 | - | y | WAVE SENSOR, no wind. Reports Hs, peak period Tp, peak direction Dp every 30 min. Live 2026-10-26 (Hs 2.1 m, Tp 12-15 s, Dp ~171-311). 600 m depth, 34 mi W of Bodega/Dillon; the reference offshore swell buoy for the Sono |

## Kings Beach (Lake Tahoe) (`kingsbeach`)

| Sensor | Network | Status | mi | Gust | Dir | Notes |
|---|---|---|---|---|---|---|
| **KNXN2** Knox 2 RAWS (Incline Village) | RAWS via IEM/FEMS | live | 4.2 | y | y | Hourly RAWS (live 2026-10-26 23:19Z via IEM NV_DCP: 7 mph, gust 21, 251 deg), 6 m standard RAWS mast, 2,300 m elevation on the slope above Incline: ridge-top gusts, not lake-level wind. |
| **NV001** Incline Village (Lakeshore Blvd) - Washoe County | Washoe County mesonet (via MADIS) (stale at probe) | stale | 4.3 | y | y | Lakeshore mesonet station 4.3 mi E of Kings Beach, reports gust. In the NWS API its data were 4 days stale on 2026-10-26 (mesonet lag); the live copy is on Synoptic/MesoWest (free token, station NV001) or NWS 'timeseries |
| **TB1** Lake Tahoe buoy TB1 (NE lake, off Incline/Kings Beach) | JPL Tahoe buoy | live | 5.7 | y | y | Nearest on-water sensor to Kings Beach (5.6 mi SSW). Position per JPL 'Measurements' table (since 2015-07-27). Reports wind speed/dir, air temp, RH, pressure, lake surface temp. 'max' column is effectively a 2-min gust.  |
| **LIB32** TAH-5201 Lake Forest (Tahoe City) - Tahoe RCD/Lahontan | mesonet via NWS/MADIS (lagged days) | stale | 5.7 | y | y | Lake-shore station near Lake Forest/Tahoe City, 5.7 mi WSW. Reports gust. Same ~4-day lag in the NWS API; use Synoptic/MesoWest (LIB32) or weather.gov/wrh/timeseries?site=LIB32 for live data. |
| **TB4** Lake Tahoe buoy TB4 (NW lake, off Tahoe City/Dollar Point) | JPL Tahoe buoy | live | 6.1 | y | y | Second northern buoy, 7 mi SW of Kings Beach; with TB1 it shows the along-lake gradient. Position since 2019-10-14. TB2 (39.108767,-120.006167) and TB3 (39.111983,-120.070617) are the mid-lake pair, 9 mi south. |
| **LVYN2** Little Valley RAWS | RAWS via IEM/FEMS | live | 7.8 | y | y | Hourly RAWS (live 2026-10-26: 13 mph G48 @260) east of the Carson Range crest; shows the SW gradient but is over the ridge from the lake. Backup only. |
| **KTRK** Truckee-Tahoe Airport | NWS/FAA airport (METAR) | live | 8.0 | y | y | AWOS 20-min with gusts (G 44.6 km/h 2026-10-26 22:49Z; speed null in that ob). Martis Valley, 1,200 ft lower than the lake and 8 mi NW; SW gradient winds show here before Kings Beach, but it does not see the lake's therm |
| **HMDC1** Homewood RAWS (west shore) | RAWS via IEM/FEMS | live | 13.1 | y | y | Hourly RAWS (live 2026-10-26: 11 mph G31 @239), 2,170 m elevation on the west-shore ski hill; cross-lake reference for a south/west-wind day, 13 mi from Kings Beach. |
