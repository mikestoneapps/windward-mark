# Real-time wind sensors for the SF Bay and Delta kite spots (Windward Mark)

Researched 2026-10-26 from a container that can reach NOAA, aprs.fi, CDEC and the open web. Distances are haversine miles from the spot coordinates given in the assignment; coordinates marked APPROX are not published by the operator. Machine-readable version: `bay_delta_stations.json` beside this file (shape `{spotId: [{id, network, name, lat, lon, dist_mi, height_m_or_null, reports_gust, reports_dir, how_to_read, notes}]}`).

Corrections to the ids suggested in the brief (all verified against the NDBC station table): **RTYC1 is Redwood City, not Richmond YC**; **LNDC1 is Oakland Berth 67, not Mare Island**; **PSBC1 is Pittsburg (Suisun Bay), not San Mateo Bridge**; **PXSC1 (Pier 17) and OBXC1 (Oakland Berth 38) are visibility-only and report no wind**; **buoy 46237 (SF Bar) reports waves only, no wind** — [NDBC station table](https://www.ndbc.noaa.gov/data/stations/station_table.txt), [NDBC latest_obs](https://www.ndbc.noaa.gov/data/latest_obs/latest_obs.txt).

## Which sensor is closest to each launch and actually represents its exposure?

### Takeaway
For every Bay spot the best *free, scriptable* reading is a NOAA CO-OPS PORTS/NWLON station on the water (FTPC1, RCMC1, PPXC1, OKXC1, OMHC1, LNDC1, AAMC1, PXOC1, RTYC1, PSBC1, PCOC1); the sensors locals actually watch are the paid WeatherFlow/iKitesurf ones (Crissy "Anita Rock", Berkeley Reef, 3rd Ave/3rd Ave Channel, Sherman #12/#14, Pittsburg Marina), which have no free API. The Delta and Folsom Lake are thin: Rio Vista has no verified live sensor on the river, and Folsom Lake's only live free sensor is CDEC FLD on Dyke 8.

### Cited Findings (per spot, nearest first; full rows in the JSON)

**paradisecay — Paradise Cay home dock (37.9168, -122.4785)**
- KCABELVE30 "Tiburon Yacht Club", WU PWS, 37.917/-122.476, 0.1 mi, 3 ft elevation, Ambient WS-2902, live with gusts (13.2 g13.6 from 291°, 17:27 PDT 2026-10-26) — [WU dashboard](https://www.wunderground.com/dashboard/pws/KCABELVE30)
- KCATIBUR4 "Mt. Tiburon", WU PWS, 37.888/-122.458, 2.3 mi, 565 ft, Davis VP2, live with gusts; ridge-top — [WU dashboard](https://www.wunderground.com/dashboard/pws/KCATIBUR4)
- WB6TTB (NWS id AU915) CWOP Tiburon, 37.8862/-122.4575, 2.4 mi, ~172 m elevation, live 00:18Z 2026-10-27 with gusts — [aprs.fi](https://aprs.fi/weather/a/WB6TTB), [api.weather.gov station list](https://api.weather.gov/stations?state=CA)
- TIBC1 Romberg Tiburon Center pier (CeNCOOS/SFSU), 37.8915/-122.4466, 2.5 mi, anemometer 10 m, wind + gust + dir; **stale: ERDDAP coverage ends 2026-09-24 and TIBC1 was missing from NDBC latest_obs on 2026-10-26** — [ERDDAP info](https://erddap.operational.sensors.axds.co/erddap/info/tiburon-weather-tibc1/index.html), [NDBC TIBC1](https://www.ndbc.noaa.gov/station_page.php?station=tibc1)
- RCMC1 / 9414863 Richmond (Chevron Long Wharf), 37.9283/-122.4000, 4.4 mi, anemometer 7.2 m, 6-min with gust — [NDBC RCMC1](https://www.ndbc.noaa.gov/station_page.php?station=rcmc1), [CO-OPS wind API](https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=wind&station=9414863&date=latest&units=english&time_zone=lst_ldt&format=json)

**crissy — Crissy Field (37.8057, -122.4535)**
- FTPC1 / 9414290 San Francisco (Fort Point), 37.8067/-122.4650, 0.6 mi, anemometer 7.4 m, 6-min with gust; this is the station Windfinder shows as "Crissy Field" (map point 37.8066/-122.4650) — [NDBC FTPC1](https://www.ndbc.noaa.gov/station_page.php?station=ftpc1), [Windfinder Crissy Field report](https://es.windfinder.com/report/crissy_field)
- iKitesurf/WeatherFlow "Crissy Field" sensor at Anita Rock (APPROX 37.807/-122.455): accurate in NW ocean wind, reads well above the beach in WSW/eddy/marine-surge flow because it sits just above the Presidio wind shadow — [Tempest blog, Mike Godsey](https://blog.tempest.earth/?p=34384)
- GGBC1 Golden Gate Bridge, 37.8197/-122.4790, 1.7 mi, NWS elevation 82 m, wind + gust at 15-min cadence in the MADIS feed — [api.weather.gov GGBC1](https://api.weather.gov/stations/GGBC1/observations); Windfinder lists "Golden Gate Bridge" 1.9 km from Crissy with live measurements — [Windfinder](https://es.windfinder.com/report/crissy_field)
- PXOC1 / 9414311 SF Pier 1, 37.7980/-122.3930, 3.3 mi, anemometer 16.2 m, 6-min with gust — [NDBC PXOC1](https://www.ndbc.noaa.gov/station_page.php?station=pxoc1)
- 46026 SF buoy, 37.750/-122.838, 21 mi W, anemometer 4.1 m, hourly with gust — [NDBC 46026](https://www.ndbc.noaa.gov/station_page.php?station=46026)

**candlestick — Candlestick Point (37.7068, -122.3855)**
- No on-the-water sensor within 6 mi. GW3010 (G3010) CWOP, 37.7225/-122.4100, 1.7 mi, ~53 m, and K6POO-1 (AW038) Brisbane, 37.6810/-122.4027, 2.0 mi, both read near zero while PORTS stations showed 10–15 kn — [aprs.fi GW3010](https://aprs.fi/weather/a/GW3010), [aprs.fi K6POO-1](https://aprs.fi/weather/a/K6POO-1)
- KSFO ASOS, 37.6196/-122.3656, 6.1 mi, hourly METAR — [api.weather.gov KSFO](https://api.weather.gov/stations/KSFO/observations/latest)
- PXOC1 (6.3 mi) and AAMC1 / 9414750 Alameda, 37.7717/-122.2983, 6.5 mi, anemometer 6.9 m — [NDBC AAMC1](https://www.ndbc.noaa.gov/station_page.php?station=aamc1)

**thirdave — Third Avenue / Foster City (37.5802, -122.2838)**
- N6OL (AU221) CWOP San Mateo bayfront, 37.5805/-122.3155, 1.7 mi, 4 m elevation, live with gusts (2.7 m/s g5.8 at 00:20Z 2026-10-27) — [aprs.fi N6OL](https://aprs.fi/weather/a/N6OL)
- DW3499 (D3499) CWOP Foster City, 37.5488/-122.2587, 2.6 mi, 2 m, Davis VP2; reported 0 wind on a windy afternoon (sheltered) — [aprs.fi DW3499](https://aprs.fi/weather/a/DW3499)
- KSQL San Carlos AWOS, 37.5167/-122.2500, 4.8 mi; KSFO 5.2 mi — [api.weather.gov KSQL](https://api.weather.gov/stations/KSQL/observations/latest)
- RTYC1 / 9414523 Redwood City, 37.5067/-122.2100, 6.5 mi, anemometer 7.6 m, 6-min with gust — [NDBC RTYC1](https://www.ndbc.noaa.gov/station_page.php?station=rtyc1)
- Locals read the paid iKitesurf "3rd Ave" (beach) and "3rd Ave Channel" sensors; the channel "is usually much windier than the launch, especially with W winds", and the launch is "generally pretty windy" when either reads 20 mph+ — [bayareakiteboarding thread](https://www.bayareakiteboarding.com/forum/viewtopic.php?p=17818)
- KCAFOSTE5 "Neighborhood 4" WU PWS, 37.5488/-122.2589, 2 ft elevation, live but shows 0 wind and no gusts (sheltered lagoon-side; not included in JSON) — [WU](https://wu-next-prod.wunderground.com/weather/us/ca/redwood-city/KCAFOSTE5)

**coyote — Coyote Point (37.5893, -122.319)**
- N6OL CWOP, 0.6 mi (see above); KM6RDV (AX472) CWOP San Mateo, 37.5640/-122.3140, 1.8 mi, ~10 m, near-zero readings — [aprs.fi KM6RDV](https://aprs.fi/weather/a/KM6RDV)
- KSFO, 3.3 mi, directly upwind in NW sea breeze — [api.weather.gov KSFO](https://api.weather.gov/stations/KSFO/observations/latest)
- KSQL 6.3 mi; RTYC1 8.3 mi. A paid iKitesurf "Coyote Point" sensor exists ("Coyote Point reading") — [bayareakiteboarding thread](https://www.bayareakiteboarding.com/forum/viewtopic.php?p=17818)

**alameda — Crown Beach (37.758, -122.2712)**
- AAMC1 / 9414750 Alameda (former NAS pier), 37.7717/-122.2983, 1.8 mi, anemometer 6.9 m, 6-min with gust — [NDBC AAMC1](https://www.ndbc.noaa.gov/station_page.php?station=aamc1), [api.weather.gov AAMC1](https://api.weather.gov/stations/AAMC1/observations/latest)
- DW9579 (D9579) CWOP Alameda Point, 37.7788/-122.2962, 2.0 mi, 4 m, live with gusts (W 5.8 m/s g8.0 at 00:19Z 2026-10-27 while AAMC1 read 12.4 kn) — [aprs.fi DW9579](https://aprs.fi/weather/a/DW9579)
- LNDC1 / 9414763 Oakland Berth 67, 37.7950/-122.2830, 2.6 mi, anemometer 7.6 m — [NDBC LNDC1](https://www.ndbc.noaa.gov/station_page.php?station=lndc1)
- KOAK ASOS, 37.7213/-122.2211, 3.7 mi — [api.weather.gov KOAK](https://api.weather.gov/stations/KOAK/observations/latest)
- Windfinder lists "Alameda, San Francisco Bay" (2.4 km), "Alameda NAS" (2.5 km) and "Ferry Point" (2.7 km) as live stations near Crown Beach — [Windfinder Alameda Beach](https://es.windfinder.com/report/alameda_beach)

**berkeley — Berkeley Marina / Hs Lordships (37.8632, -122.3152)**
- KJ6WEG (AV737) CWOP Berkeley, 37.8642/-122.2845, 1.7 mi, ~32 m, near-zero readings (sheltered) — [aprs.fi KJ6WEG](https://aprs.fi/weather/a/KJ6WEG)
- iKitesurf/WeatherFlow "Berkeley Reef" spot 175511 (APPROX 37.86/-122.35) on a metal marker over the rocky reef; "often the best reading for the Olympic Circle"; repairs need a boat and Coast Guard permission — [iWindsurf forum, WeatherFlow support](https://www.iwindsurf.com/forums/viewtopic.php?p=362535)
- OKXC1 / 9414776 Oakland Berth 34, 37.8106/-122.3331, 3.8 mi, anemometer 7.6 m, 6-min with gust — [NDBC OKXC1](https://www.ndbc.noaa.gov/station_page.php?station=okxc1)
- PPXC1 / 9414847 Point Potrero, 37.9058/-122.3650, 4.0 mi, 6-min with gust, anemometer height not published, not on api.weather.gov — [NDBC PPXC1](https://www.ndbc.noaa.gov/station_page.php?station=ppxc1), [CO-OPS wind 9414847](https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=wind&station=9414847&date=latest&units=english&time_zone=lst_ldt&format=json)
- RCMC1 6.5 mi. NWS lists A4539 "Berkeley Aquatic Park" (37.8648/-122.3027, 0.7 mi) but it returns no observations — [api.weather.gov A4539](https://api.weather.gov/stations/A4539/observations)

**pointisabel — Point Isabel (37.8984, -122.3245)**
- GW5483 (G5483) CWOP Richmond, 37.9108/-122.3128, 1.1 mi, 7 m, near-zero readings (sheltered) — [aprs.fi GW5483](https://aprs.fi/weather/a/GW5483)
- DW7213 (D7213) CWOP Richmond Marina Bay shoreline, 37.9137/-122.3547, 2.0 mi, 0 m elevation, live with gusts (W 256° 5.4 m/s g7.6 at 00:15Z 2026-10-27) — [aprs.fi DW7213](https://aprs.fi/weather/a/DW7213)
- PPXC1 Point Potrero, 2.3 mi (above)
- KCACALIF93 "Richmond Yacht Club" WU PWS (Brickyard Cove), 37.907/-122.383, 3.2 mi, Davis VP2, live with gusts (12 g14 from 248°, 17:25 PDT 2026-10-26) — [WU dashboard](https://www.wunderground.com/dashboard/pws/KCACALIF93)
- RCMC1 4.6 mi; Windfinder "Richmond / Point Potrero" report exists — [Windfinder](https://es.windfinder.com/report/richmond_point_potrero)

**tollplaza — Radio Beach / Toll Plaza (37.8272, -122.3095)**
- OKXC1 Oakland Berth 34, 1.7 mi; OMHC1 / 9414769 Oakland Middle Harbor Met, 37.8000/-122.3300, 2.2 mi, anemometer 6.7 m, also on api.weather.gov; LNDC1 2.7 mi; AAMC1 3.9 mi — [NDBC OMHC1](https://www.ndbc.noaa.gov/station_page.php?station=omhc1), [api.weather.gov OMHC1](https://api.weather.gov/stations/OMHC1/observations/latest)
- OBXC1 Berth 38 is visibility-only — [NDBC latest_obs](https://www.ndbc.noaa.gov/data/latest_obs/latest_obs.txt)

**racetrack — Albany Beach (37.8875, -122.312)**: GW5483 1.6 mi (sheltered), Berkeley Reef APPROX 2.8 mi (paid), DW7213 2.9 mi, PPXC1 3.2 mi, OKXC1 5.4 mi (sources as above).

**pointemery — Point Emery (37.8402, -122.3042)**: KJ6WEG 2.0 mi (sheltered), OKXC1 2.6 mi, OMHC1 3.1 mi, LNDC1 3.3 mi, AAMC1 4.7 mi (sources as above).

**sherman — Sherman Island County Park (38.0437, -121.8061)**
- iKitesurf/WeatherFlow Sherman Island sensors "#12" and "#14" (positions not published): "#12 is closer to where most people kite than #14"; sensors are "iwindsurf.com owned and installed" and "not available elsewhere"; one read WSW all afternoon while riders felt SSW/SW — [bayareakiteboarding "New Sensor @ sherman??"](https://www.bayareakiteboarding.com/forum/viewtopic.php?p=18128)
- 519PG "Bridgehead" PG&E station, 38.0053/-121.7604, 3.6 mi, 12 m elevation, 10-min wind/gust/dir — [api.weather.gov 519PG](https://api.weather.gov/stations/519PG/observations)
- 606PG "Pittsburg 3rd Ave" PG&E, 38.0323/-121.8785, 4.0 mi, 4 m — [api.weather.gov 606PG](https://api.weather.gov/stations/606PG/observations)
- iKitesurf "Pittsburg Marina" spot 100721 (APPROX 38.035/-121.885; Windfinder puts "Pittsburg Marina" 5.5 km from Antioch marina) — [bayareakiteboarding Bay Point thread](https://www.bayareakiteboarding.com/forum/viewtopic.php?p=93801), [Windfinder Marina Antioch](https://www.windfinder.com/report/marina_antioch)
- PSBC1 / 9415115 Pittsburg (Suisun Bay), 38.0416/-121.8867, 4.4 mi, anemometer 7.6 m, 6-min with gust (13.0 g15.9 kn NW at 17:12 PDT 2026-10-26) — [NDBC PSBC1](https://www.ndbc.noaa.gov/station_page.php?station=psbc1), [CO-OPS wind 9415115](https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=wind&station=9415115&date=latest&units=english&time_zone=lst_ldt&format=json)
- CDEC ANH "San Joaquin River at Antioch", 38.0178/-121.8030, 1.8 mi, lists wind speed/direction sensors but every value on 2026-10-26 was -9999 — [CDEC station search](https://cdec.water.ca.gov/dynamicapp/staSearch?sta=&sensor_chk=on&sensor=9&collect=NONE+SPECIFIED&dur=&active_chk=on&active=Y&loc_chk=on&lon1=-122.15&lon2=-121.55&lat1=37.95&lat2=38.30&elev1=-5&elev2=99999&nearby=&basin=NONE+SPECIFIED&hydro=NONE+SPECIFIED&county=NONE+SPECIFIED&agency_num=160&display=sta), [CDEC JSON ANH](https://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet?Stations=ANH&SensorNums=9,10&dur_code=E&Start=2026-10-26&End=2026-10-27)
- SIDC1 "SHERMAN ISLAND" (38.0578/-121.7861, 1.5 mi) is in the NWS station list but returns no observations (likely a DWR stage gauge) — [api.weather.gov SIDC1](https://api.weather.gov/stations/SIDC1/observations)

**windycove — Rio Vista / Windy Cove (38.1414, -121.6947)**
- CDEC RVB "Sacramento River at Rio Vista Bridge", 38.1597/-121.6864, 1.3 mi, wind sensors listed but all -9999 on 2026-10-26 — [CDEC RVB metadata](https://cdec.water.ca.gov/dynamicapp/staMeta?station_id=RVB), [CDEC JSON RVB](https://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet?Stations=RVB&SensorNums=9,10&dur_code=E&Start=2026-10-26&End=2026-10-27)
- CF105 Caltrans RWIS "SR-12 - SR-160" (Rio Vista Bridge), 38.1546/-121.6755, 1.4 mi; wind fields null in the NWS feed the week of 2026-10-22; Caltrans feed https://cwwp2.dot.ca.gov/data/d4/rwisStatusD04.json returned HTTP 500 on 2026-10-26; Windfinder's "Rio Vista / Delta" report (map point 38.1551/-121.6762, matching CF105) showed "no data available" — [api.weather.gov CF105](https://api.weather.gov/stations/CF105/observations), [Caltrans RWIS field description](https://cwwp2.dot.ca.gov/documentation/rwis/rwis-field-description.htm), [Windfinder Rio Vista / Delta](https://es.windfinder.com/report/rio_vista_delta)
- TCICA / CI140 Twitchell Island (CIMIS station 140), 38.1170/-121.6580, 2.6 mi, hourly wind speed and direction, no gust (6.4 km/h at 12:56Z 2026-10-22) — [api.weather.gov TCICA](https://api.weather.gov/stations/TCICA/observations)
- CF106 Caltrans RWIS "SR-12 - Brannan Island Road", 38.1282/-121.5856, 6.0 mi, wind + gust + dir at 10-min (7.2 km/h g8.6 at 13:10Z 2026-10-22) — [api.weather.gov CF106](https://api.weather.gov/stations/CF106/observations)
- 493PG "Grand Island" PG&E, 38.2079/-121.6091, 6.5 mi; 495PG "Birds Landing Road", 38.1381/-121.8341, 74 m, 7.6 mi — [api.weather.gov 493PG](https://api.weather.gov/stations/493PG/observations)
- Windfinder's nearby-station list for Rio Vista: Ryer Island/Walnut Grove 3.9 km, Rio Vista Airport 4.5 km, Twitchell Island 6.5 km, Grand Island 8.3 km, SR-12 Brannan Island Rd 8.5 km, Birds Landing Rd 13.9 km — [Windfinder Rio Vista / Delta](https://es.windfinder.com/report/rio_vista_delta)

**baypoint — Bay Point / McAvoy (38.0479, -121.9618)**
- EW9715 (E9715) CWOP Pittsburg, 38.0240/-121.9407, 2.0 mi, ~25 m, near-zero readings while PORTS showed 13 kn — [aprs.fi EW9715](https://aprs.fi/weather/a/EW9715)
- PSBC1 Pittsburg 4.1 mi (above); iKitesurf "Pittsburg Marina" spot 100721 APPROX 4.3 mi, recommended for Bay Point with a free account — [bayareakiteboarding Bay Point thread](https://www.bayareakiteboarding.com/forum/viewtopic.php?p=93801)
- PCOC1 / 9415144 Port Chicago, 38.0560/-122.0395, 4.3 mi, anemometer 8.4 m, 6-min with gust, also on api.weather.gov (24.1 km/h g29.9 at 22:48Z 2026-10-26) — [NDBC PCOC1](https://www.ndbc.noaa.gov/station_page.php?station=pcoc1), [api.weather.gov PCOC1](https://api.weather.gov/stations/PCOC1/observations/latest)
- KCCR Concord ASOS, 37.9917/-122.0519, 6.3 mi — [api.weather.gov KCCR](https://api.weather.gov/stations/KCCR/observations/latest)
- CDEC MAL "Mallard Island", 38.0428/-121.9201, 2.3 mi, wind listed but -9999 on 2026-10-26 — [CDEC JSON MAL](https://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet?Stations=MAL&SensorNums=9,10&dur_code=E&Start=2026-10-26&End=2026-10-27)

**granitebay — Folsom Lake Granite Bay (38.7395, -121.169)**
- KCAGRANI20 "Granite Bay mixed rural, residential" WU PWS, 38.741/-121.176, 0.4 mi, 390 ft, Davis VP2 Plus, **offline** on 2026-10-26 — [WU dashboard](https://www.wunderground.com/dashboard/pws/KCAGRANI20)
- PG882 "Quinn Place" PG&E, 38.7814/-121.1632, 2.9 mi, 143 m, 10-min wind/gust/dir (9.3 km/h g18.5 at 13:10Z 2026-10-22) — [api.weather.gov PG882](https://api.weather.gov/stations/PG882/observations)
- CDEC FLD "Folsom Dam - Folsom Point (Dyke 8)" (NWS id FSLC1), 38.6931/-121.1297, 3.8 mi, 350 ft, live 15-min wind speed and direction, no gust (8 mph / 169° at 16:14 PDT 2026-10-26) — [CDEC station search (Folsom box)](https://cdec.water.ca.gov/dynamicapp/staSearch?sta=&sensor_chk=on&sensor=9&collect=NONE+SPECIFIED&dur=&active_chk=on&active=Y&loc_chk=on&lon1=-121.30&lon2=-121.00&lat1=38.60&lat2=38.85&elev1=-5&elev2=99999&nearby=&basin=NONE+SPECIFIED&hydro=NONE+SPECIFIED&county=NONE+SPECIFIED&agency_num=160&display=sta), [CDEC JSON FLD](https://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet?Stations=FLD&SensorNums=9,10&dur_code=E&Start=2026-10-26&End=2026-10-27)
- 144PG "Atlantic Gold Hill" PG&E, 38.6578/-121.1350, 5.9 mi — [api.weather.gov 144PG](https://api.weather.gov/stations/144PG/observations)
- KMHR Mather ASOS 13.9 mi; KAUN Auburn 15.6 mi — [api.weather.gov KMHR](https://api.weather.gov/stations/KMHR/observations/latest)
- Locals use "the ikite wind sensor": "reasonably accurate for north winds until readings reach the 20s"; "for south winds, add roughly 5 mph" — [bayareakiteboarding Folsom Lake thread](https://www.bayareakiteboarding.com/forum/viewtopic.php?p=27810)
- Windfinder has no live station at Folsom Lake; nearest it lists are Atlantic Gold Hill 3.8 km, GW6439 Folsom 5.4 km, K1FIE El Dorado Hills 6 km — [Windfinder Folsom Lake](https://www.windfinder.com/report/folsom_lake)

**folsompoint — Folsom Lake Folsom Point (38.705, -121.127)**
- CDEC FLD / FSLC1 Dyke 8, 0.8 mi (above) — closest sensor of any network, live, no gust
- 144PG Atlantic Gold Hill 3.3 mi; GW6439 (G6439) CWOP Folsom, 38.6547/-121.0905, 4.0 mi, near-zero readings — [aprs.fi GW6439](https://aprs.fi/weather/a/GW6439)
- PG111 "Arroyo Vista" PG&E, 38.7304/-121.0545, 4.3 mi, 329 m ridge, 10-min wind/gust — [api.weather.gov PG111](https://api.weather.gov/stations/PG111/observations)
- PG882 Quinn Place 5.6 mi

### Inferences
- CWOP home stations around the Bay are almost all terrain- or building-sheltered: on an afternoon when PORTS stations read 10–15 kn, GW3010, K6POO-1, DW3499, KM6RDV, KJ6WEG, GW5483, EW9715 and GW6439 read 0–1.5 m/s. Only DW7213 (Richmond Marina Bay shoreline, 0 m) and DW9579 (Alameda Point, 4 m) tracked the water, and even DW9579 read about half of AAMC1.
- The WU "Tiburon Yacht Club" PWS is effectively at the Paradise Cay dock and the best representation of that launch, but it is view-only; RCMC1 across the channel is the scriptable stand-in.
- For Candlestick nothing represents the point; KSFO is the least-bad free sensor and will under-read the point in W-NW gap flow.
- For the Delta launches the on-water PORTS pair PSBC1/PCOC1 plus PG&E 519PG/606PG are the only free live readings; CDEC's DWR water-quality stations advertise wind but are returning no data.

### Gaps
- iKitesurf/WeatherFlow sensor coordinates and spot ids for Crissy (Anita Rock), 3rd Ave, 3rd Ave Channel, Coyote Point, Alameda, Pt. Isabel, Treasure Island, Sherman #12/#14, Rio Vista and Folsom Lake were not found (only Berkeley Reef = 175511 and Pittsburg Marina = 100721 are confirmed); `wx.ikitesurf.com/spot/100721` could not be fetched (provenance block).
- Anemometer height for PPXC1 is not published on NDBC; CO-OPS mdapi returns null sensorHeight for all wind sensors.
- A4539 "Berkeley Aquatic Park" and SIDC1 "Sherman Island" exist in the NWS station list but return no observations; whether they have anemometers is unverified.
- Windfinder's "Ferry Point" station near Alameda and "Ryer Island / Walnut Grove" and "Rio Vista Airport" stations near Rio Vista were not identified to a network/id.
- Tempest public-station map, Ambient Weather Network, Netatmo and Holfuy maps are JavaScript-only and were not enumerated; no Holfuy or Netatmo station near any spot was found by search.
- St. Francis YC, SF YC (Belvedere), Sequoia YC and Folsom Lake YC: no public live wind feed found by search.

## Which are free to read hourly from a script, and which are view-only?

### Takeaway
NOAA CO-OPS (6-min, knots, with gust), NWS METAR airports, NDBC buoys, CDEC and CeNCOOS ERDDAP are free, keyless and scriptable; CWOP is free via aprs.fi/findu pages or Synoptic; PG&E, Caltrans and Golden Gate Bridge stations are reachable only through MADIS relays (api.weather.gov, which was four days behind on 2026-10-26, or Synoptic with a free token); WU, Tempest/iKitesurf are view-only.

### Cited Findings
- CO-OPS wind product returns 6-min speed/dir/gust in knots with `units=english`, e.g. FTPC1 8.94 kn g15.75 at 17:12 PDT 2026-10-26, for all of 9414290, 9414750, 9414863, 9414847, 9414776, 9414769, 9414763, 9414311, 9414523, 9415115, 9415144, 9415118, 9415102; 9414296, 9414797 and 9415141 return "No data" — [CO-OPS datagetter](https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=wind&station=9414290&date=latest&units=english&time_zone=lst_ldt&format=json)
- NDBC realtime2 / latest_obs carries the same PORTS stations in m/s (RCMC1, PPXC1, FTPC1, PXOC1, OKXC1, OMHC1, LNDC1, AAMC1, RTYC1, PSBC1, PCOC1, UPBC1, MZXC1) — [NDBC latest_obs](https://www.ndbc.noaa.gov/data/latest_obs/latest_obs.txt)
- api.weather.gov serves FTPC1, AAMC1, RCMC1, RTYC1, PCOC1, OMHC1, UPBC1, MZXC1 and all METAR airports with current timestamps, but **not** PPXC1, OKXC1, LNDC1, PXOC1, PSBC1 (404) — [api.weather.gov FTPC1](https://api.weather.gov/stations/FTPC1/observations/latest), [api.weather.gov PPXC1](https://api.weather.gov/stations/PPXC1/observations/latest)
- api.weather.gov's MADIS-fed non-NOAA stations (CWOP, PG&E, Caltrans, GGBC1, RAWS) all had latest timestamps of 2026-10-22 when queried 2026-10-26, i.e. the feed was ~4 days stale — [api.weather.gov D7213](https://api.weather.gov/stations/D7213/observations), [api.weather.gov 519PG](https://api.weather.gov/stations/519PG/observations)
- aprs.fi shows CWOP reports within minutes (DW7213 "4m51s ago") with wind and gust in m/s — [aprs.fi DW7213](https://aprs.fi/weather/a/DW7213)
- Synoptic API rejects `demotoken` with HTTP 401; a free account token is required — [Synoptic metadata endpoint](https://api.synopticdata.com/v2/stations/metadata?token=demotoken&radius=37.8057,-122.4535,10)
- Caltrans RWIS district JSON feeds (d3, d4, d10) returned HTTP 500 on 2026-10-26; field layout documented at Caltrans — [Caltrans RWIS field description](https://cwwp2.dot.ca.gov/documentation/rwis/rwis-field-description.htm)
- CDEC JSONDataServlet returns 15-min ("E") and hourly ("H") wind in mph without a key; FLD is live, the DWR Delta stations return -9999 — [CDEC JSON FLD](https://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet?Stations=FLD&SensorNums=9,10&dur_code=E&Start=2026-10-26&End=2026-10-27)
- TIBC1 is served as CSV/JSON from Axiom's ERDDAP (`tiburon-weather-tibc1`) with wind_speed, wind_speed_of_gust and wind_from_direction — [ERDDAP info](https://erddap.operational.sensors.axds.co/erddap/info/tiburon-weather-tibc1/index.html)
- iKitesurf access costs about $10/month; Pro Forecast updates three times a day; "Wind Alerts" push when a spot meets chosen speed/direction — [bayareakiteboarding resources thread](https://bayareakiteboarding.com/forum/viewtopic.php?p=95878); the Pittsburg Marina sensor is "publicly available through a free iKitesurf account" — [bayareakiteboarding Bay Point thread](https://www.bayareakiteboarding.com/forum/viewtopic.php?p=93801)
- WeatherFlow says the green spots on iWindsurf/iKitesurf maps are "Nowcast spots" (model estimates adjusted with nearby observations), not live stations, so not every green dot is a sensor — [iWindsurf forum](https://www.iwindsurf.com/forums/viewtopic.php?p=370450)
- WU PWS dashboards show live values with gusts but no units label; KCABELVE30 and KCACALIF93 updated within seconds/minutes on 2026-10-26 — [WU KCABELVE30](https://www.wunderground.com/dashboard/pws/KCABELVE30), [WU KCACALIF93](https://www.wunderground.com/dashboard/pws/KCACALIF93)

### Inferences
- For the hourly observations job, poll CO-OPS (primary, 6-min, knots) and fall back to NDBC realtime2 for the same ids; use api.weather.gov only for METAR airports and the few PORTS ids it serves. Do not rely on api.weather.gov for CWOP/PG&E/Caltrans; use aprs.fi (CWOP) or a free Synoptic token (everything else) if those networks are wanted.
- WU values are almost certainly mph (PWS default) but the dashboard does not say; treat as display-only.

### Gaps
- Whether the WU PWS API (needs an owner key) or Tempest's per-station API could be obtained for KCABELVE30 was not tested; both require the station owner's cooperation.
- iKitesurf's internal WeatherFlow API (`api.weatherflow.com/wxengine`) was not probed; it is token-gated and against terms for scraping.

## Update interval and whether gusts are reported

### Takeaway
PORTS/NWLON: 6-min with gust. METAR: hourly (plus SPECI), gust only when the ASOS flags one. CWOP: 5–10 min with gust. PG&E: 10-min with gust. Caltrans RWIS: 10-min with gust (when alive). CDEC FLD: 15-min, no gust. CIMIS Twitchell: hourly mean, no gust. 46026 buoy: hourly with gust. GGBC1: 15-min with gust.

### Cited Findings
- CO-OPS wind timestamps step every 6 minutes (17:06, 17:12 PDT) with speed, direction and gust fields — [CO-OPS datagetter RCMC1](https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=wind&station=9414863&date=latest&units=english&time_zone=lst_ldt&format=json)
- Anemometer heights (NDBC station pages): FTPC1 7.4 m, AAMC1 6.9 m, RCMC1 7.2 m, PCOC1 8.4 m, PSBC1 7.6 m, RTYC1 7.6 m, OKXC1 7.6 m, OMHC1 6.7 m, LNDC1 7.6 m, PXOC1 16.2 m, MZXC1 6.4 m, UPBC1 100 m (rail bridge), 46026 4.1 m, TIBC1 10 m, SFXC1 7.5 m — e.g. [NDBC FTPC1](https://www.ndbc.noaa.gov/station_page.php?station=ftpc1), [NDBC PXOC1](https://www.ndbc.noaa.gov/station_page.php?station=pxoc1), [NDBC UPBC1](https://www.ndbc.noaa.gov/station_page.php?station=upbc1)
- KSFO, KOAK, KSQL, KPAO, KSJC, KCCR, KAPC, KSUU, KLVK, KSAC, KMHR, KAUN, KSMF, KSTS, KSCK, KVCB all returned observations on 2026-10-26; gusts appeared only at KHWD (35.2 km/h), KDVO (31.7), KHAF (27.7) — [api.weather.gov KHWD](https://api.weather.gov/stations/KHWD/observations/latest)
- PG&E stations report at :00/:10/:20 with gust values (e.g. PG882 9.3 km/h g18.5 at 13:10Z) — [api.weather.gov PG882](https://api.weather.gov/stations/PG882/observations)
- CF106 reports at 10-min with gust; CF105 reported nulls — [api.weather.gov CF106](https://api.weather.gov/stations/CF106/observations)
- GGBC1 reports at :30/:15 with gust (2.1 km/h g11.6 at 12:15Z 2026-10-22) — [api.weather.gov GGBC1](https://api.weather.gov/stations/GGBC1/observations)
- CDEC FLD event data is 15-min (16:14 PDT) with sensors 9 (speed) and 10 (direction) only — [CDEC JSON FLD](https://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet?Stations=FLD&SensorNums=9,10&dur_code=E&Start=2026-10-26&End=2026-10-27)
- TCICA (CIMIS Twitchell Island) reports wind speed and direction without gust — [api.weather.gov TCICA](https://api.weather.gov/stations/TCICA/observations)
- Windfinder's Rio Vista / Delta and Crissy Field reports plot average and gust lines — [Windfinder Rio Vista / Delta](https://es.windfinder.com/report/rio_vista_delta)

### Inferences
- The PORTS anemometers at ~7 m are close enough to the 10 m standard that no height correction is needed for scoring; PXOC1 (16 m) and GGBC1 (bridge deck) will read high relative to the water, and the 2 m CIMIS station will read low.

### Gaps
- KRIU (Rancho Murieta) and KLHM (Lincoln) returned no current observations on api.weather.gov; KNUQ and KSFO had null wind in the single latest record (likely a missing-field artefact), so METAR gust availability should be checked on the aviationweather.gov feed rather than assumed.
- The NWS/MADIS lag means the cadence figures for PG&E/Caltrans/GGBC1 were read from 2026-10-22 records, not live ones.

## Addendum: feed/cadence/live-check fields and regional references (coordinator request)
- Every JSON row now carries `feed`, `cadence` and `live_check` (what was verified on 2026-10-26 and what is "unverified"). A `_regional_reference` key lists the buoys/C-MAN/PORTS stations that are not within 5 mi of any spot: 46026 (live, wind), 46013 (live, wind), 46237 and 46214 (waves only, no wind — [NDBC latest_obs](https://www.ndbc.noaa.gov/data/latest_obs/latest_obs.txt)), PRYC1 (no wind fields in its 23:30Z record — sensor apparently down), UPBC1 (100 m rail-bridge anemometer) and MZXC1 (Martinez pier) as the nearest live sensors to Benicia — [NDBC UPBC1](https://www.ndbc.noaa.gov/station_page.php?station=upbc1), [NDBC MZXC1](https://www.ndbc.noaa.gov/station_page.php?station=mzxc1); PTGC1 is Point Arguello (not Bay Area, unchecked).
- RAWS on the Marin/East Bay hills (MDEC1 Middle Peak 713 m, BBEC1 Barnaby, PIBC1 Black Diamond 488 m, LTRC1 Las Trampas, PLTC1 Pilot Hill) appear in the NWS station list with hourly wind/gust but were only seen in the lagged MADIS feed; the IEM obhistory page (`mesonet.agron.iastate.edu/sites/obhistory.php?station=<id>&network=CA_RAWS`) was not checked — unverified — [api.weather.gov MDEC1](https://api.weather.gov/stations/MDEC1/observations/latest).
- No CWOP/PWS at Benicia was checked (unverified); KAPC Napa (live, 27.8 km/h at 23:50Z) and KCCR Concord are the nearest METARs — [api.weather.gov KAPC](https://api.weather.gov/stations/KAPC/observations/latest).
