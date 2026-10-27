# Netatmo home stations — one-time setup

Windward Mark can show readings from Netatmo backyard weather stations near each spot (the public Netatmo
Weathermap). Nothing is needed for CWOP stations: those are heard over the public APRS-IS network with no
account. Netatmo's public data needs a free developer app, which takes about ten minutes, once. Until the
three secrets below exist, the hourly job simply skips Netatmo and says so in its log.

Everything here is free. Netatmo's developer terms allow apps that read the public map; the app never
reads anyone's private station, never writes anything, and only the rounded (3-decimal) location of a
station is ever stored in the repository.

## 1. Create the Netatmo developer app

1. Go to **https://dev.netatmo.com** and sign in with a Netatmo account (any free account works; you do
   not need to own a station). Create one at https://auth.netatmo.com if you have none.
2. Click your name (top right) → **My apps** → **Create an app**.
3. Fill in the form: **App name** `Windward Mark`, **Description** `Reads public wind readings near
   kiteboarding spots`, **Data protection officer / Developer** your own name and email. Tick the terms
   box. **Save**.
4. The app page now shows a **Client ID** and a **Client secret**. Keep this page open.

## 2. Get a refresh token

1. On the same app page scroll to **Token generator**.
2. In the scopes list tick **`read_station`** only.
3. Click **Generate token**, approve the consent screen.
4. Copy the **Refresh token** (a long string). Ignore the access token; the job makes its own from the
   refresh token every run.

## 3. Put the three values into GitHub

1. Open the repository on GitHub → **Settings** → **Secrets and variables** → **Actions**.
2. **New repository secret** three times:

   | Name                    | Value                              |
   |-------------------------|------------------------------------|
   | `NETATMO_CLIENT_ID`     | the Client ID from step 1          |
   | `NETATMO_CLIENT_SECRET` | the Client secret from step 1      |
   | `NETATMO_REFRESH_TOKEN` | the Refresh token from step 2      |

3. Done. The next hourly **Station observations** run picks them up; or start one now under **Actions →
   Station observations → Run workflow**. Its log has a line per area such as
   `home stations: netatmo box (...): 4 station(s) with wind`.

## About the rotating refresh token

Netatmo hands out a **new** refresh token every time one is used and may retire the old one. GitHub
Actions cannot rewrite its own secrets, so the job keeps the newest token on the settings-sync Worker
(`PUT /v1/admin/vars/netatmo_refresh_token`, admin token only; see `docs/SETUP-SYNC.md`). With the
`SYNC_URL` and `SYNC_ADMIN_TOKEN` secrets in place this is automatic: the stored token wins over the
repository secret from then on, and the secret only matters for the very first run.

Without the sync Worker the job still works as long as Netatmo keeps accepting the original token. If a
run logs `home stations: netatmo skipped` with an `invalid_grant` error, the token has been retired:
repeat step 2 and update the `NETATMO_REFRESH_TOKEN` secret (step 3). That is the whole repair.

## What the job does with it

- One `getpublicdata` call per area (the Bay, the Delta, the coast, Monterey, Tahoe, and a box around any
  rider-added spot far from those), `required_data=wind`, once an hour: a few calls per run, far inside
  Netatmo's limits.
- Only devices with a wind gauge count; wind and gust (km/h) are converted to knots.
- Every station seen is documented in `home-stations.json` (device id, rounded location, city, first and
  last seen) and shown as a **home station** hint on the spots within 10 miles. It never changes a score;
  after a month of reading like a nearby official station it can be marked **trusted** (`home_trust.py`)
  and then stands in for alerts and the bias correction only where no official station is close by.
