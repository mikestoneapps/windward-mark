# Windward Mark — build status (2026-10-26 17:35 PT)

Done: repo, Pages, Claude App access, Bay edition applied (PR #1), Worker windward-mark deployed via workflow with KV windward_settings, ADMIN_TOKEN set, GitHub secrets (CLOUDFLARE_*, SYNC_URL, SYNC_ADMIN_TOKEN, VAPID_PRIVATE_KEY rotated in PR #3), first observations run green, Mike's phone subscribed (1 rider), 27-spot list in bay-spots.json (batch 1 + batch 2 + Paradise Cay home dock).

In progress: sensor research (networks inventory; nearest sensors per spot for Bay/Delta and coast/Tahoe) → files in this folder when complete.

Next Claude Code session (one PR), after the sensor research is folded in:
1. Apply bay-spots.json (27 spots) to spots.json + embedded SPOTS; regions Monterey Bay / Tahoe / South Bay; lakes tideStation null; delete bay-spots.json.
2. Stations: NOS C1 stations are kind "ndbc" (realtime2), not "nws"; route non-airport/non-CWOP 5-char ids via NDBC; extend NDBC catalogue (46026, 46214, 46236, 46240, 46239; OBXC1, PXOC1, RTYC1, LNDC1, PSBC1, MTYC1, PXSC1); 35 mi radius for Delta/Ocean/Monterey Bay/Tahoe; add "Resolve stations" workflow_dispatch that runs stations.py live on GitHub and commits stations.json; plus whatever extra networks the sensor research recommends (likely Synoptic free tier with a token secret, CWOP via api.weather.gov, CDEC for the Delta).
3. "Send test notification" button (settings.alerts.testRequested → alerts/run.mjs sends a test on next run, clears flag).
4. BUILD-PLAN "Bay edition" open questions (Paradise Cay dock sectors, Rio Vista/Marina status, Albany parking).

After merge: Actions → Resolve stations → Run workflow; Station observations → Run workflow; audit per-spot sensors. Then gift card, Mike unlinks phone. Later: windwardmark domain (optional, paid) — remind Mike.
