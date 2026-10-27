# Windward Mark — build status (2026-10-27)

Done: repo, Pages, Claude App access, Bay edition applied (PR #1), Worker windward-mark deployed via workflow with KV windward_settings, ADMIN_TOKEN set, GitHub secrets (CLOUDFLARE_*, SYNC_URL, SYNC_ADMIN_TOKEN, VAPID_PRIVATE_KEY rotated in PR #3), first observations run green, Mike's phone subscribed (1 rider).

Sensor research complete (2026-10-26 19:30 PT): networks.md, bay_delta_stations.*, coast_tahoe_stations.*, merged into sensor-catalogue.md and stations-proposed.json.

Sensor PR (2026-10-27, this branch): 27-spot list applied to spots.json + embedded SPOTS (bay-spots.json deleted; regions Monterey Bay / Tahoe added where region logic exists); stations.json replaced by the verified catalogue with a `kind` per feed (nws, coops, ndbc, raws, iem, cencoos, cdec, caltrans, jpl, cdip wave-only) and obs_standalone.py/stations.py reading every kind; `.github/workflows/resolve-stations.yml` (workflow_dispatch, adds-only resolve live on GitHub); Live line links to each sensor's public page + per-spot `links` for the view-only iKitesurf/WU sensors; "Send test notification" button (settings.alerts.testRequested → one test push next hourly run → state.testSent). Open questions for Mark are in docs/BUILD-PLAN.md "Bay edition".

After merge: Actions → Resolve stations → Run workflow; Station observations → Run workflow; audit per-spot sensors on the live page (the build container cannot reach any of the feeds). Then gift card, Mike unlinks phone. Later: windwardmark domain (optional, paid) — remind Mike.
