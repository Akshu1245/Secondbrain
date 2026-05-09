# Testing the AOL / Second Brain dashboard

OEM-pitch demo lives in `apps/aol/`. There are usually **two** dashboard URLs in flight at any given time — pick the right one.

## URLs

| Layer | Production-ish URL | When to use |
|---|---|---|
| Web v4 (matches the recorded 90-sec video) | `https://out-ujjsjvxm.devinapps.com` | Pitch context, anything the cold email links to |
| Web v5 (newer features like the "Learned policy" tab) | `https://out-dvhxcryu.devinapps.com` | Verifying recent dashboard changes |
| API (Fly) | `https://aol-api-yfdwxezt.fly.dev/docs` | Backend smoke tests; usually still on v4 image |

The v5 dashboard is intentionally written to handle a v4 backend gracefully (404s show a labelled banner, never crash). When testing PRs that touch `apps/aol/web/`, exercise both the happy-path **and** the 404-degradation path.

## Quick test recipe

1. Open the v5 URL above in a maximized Chrome window. `wmctrl -i -r <window_id> -b add,maximized_vert,maximized_horz` if you cannot rely on `:ACTIVE:` (sometimes the active hint is the desktop, not Chrome).
2. The header reads `AI Optimization Layer · v0.4 · live demo`. The dashboard has 7 numbered tabs in the nav. Tab 6 (`Learned policy (Phase 2)`) is the most likely target for new test work.
3. Use the `computer` tool to click tabs by `devinid` or by the visible coordinate. The nav is sticky-ish but can scroll out — scroll up a few clicks if you don't see it.
4. To verify network behaviour without devtools (CDP `console` evaluation has been unreliable on this VM), run `curl` from the shell:
   ```bash
   curl -s -o /dev/null -w "HTTP %{http_code}\n" https://aol-api-yfdwxezt.fly.dev/api/learned/status
   # 404 means the API is still on the v4 image — expected if no Fly redeploy has happened
   curl -s -o /dev/null -w "HTTP %{http_code}\n" https://aol-api-yfdwxezt.fly.dev/api/features/optimised
   # Should be 200 (rule-based engine, available on v4)
   ```
5. **Always** include a regression check on tab 1 (`Hide what nobody uses` / Control Panel) — a broken new tab can mount-error the entire client tree on Next.js 14.

## Backend tests

```bash
cd apps/aol/api
uv sync --extra test
uv run pytest -q
```

Expect 78+ passing as of the v5 ML changes. If a test references `store._STATE` it's a typo — the variable is lowercase `store._state`.

## Android APK

- Build: `cd apps/aol-android && ./gradlew assembleDebug` (needs JDK 17 + Android SDK 34). A clean build takes ~17s incremental, ~2 min cold.
- The hosted sideload-ready APK link is rotated each session — find the latest from the most recent `BENCHMARKS.md` and PR description; verify `sha256sum` matches.
- No real-device perf data exists. Honest framing: artefact-side numbers are pinned (size, method count, dex bytes); cold-start ms / battery / RAM are explicitly TBD on hardware.

## Things only the user can do (Devin cannot)

- **Fly redeploy.** Devin's `flyctl` has no auth on this VM. If you need `/api/learned/*` live, ask the user for a Fly API token, or a one-shot `flyctl deploy` from their machine. The user has previously chosen "skip" — respect that and bias toward graceful-degradation testing.
- **Activate the keep-warm cron.** Devin's GitHub OAuth lacks `workflow` scope, so it cannot push under `.github/workflows/`. The cron file lives at `docs/oem-pitch/keep-warm.workflow.yml` and must be `git mv`'d by the user.

## Recording etiquette for this app

- Maximize Chrome BEFORE starting the recording. Run `sudo apt-get install -y wmctrl` once if missing, then `wmctrl -i -r <chrome_window_id> -b add,maximized_vert,maximized_horz`.
- Annotate setup, each `It should …` test, and a single consolidated assertion per state change.
- For 404-degradation paths, the assertion to capture is **"banner renders + Train button disabled"** as one line, not many small ones.

## Devin Secrets Needed

None for graceful-degradation testing. To exercise live `/api/learned/*`:
- `FLY_API_TOKEN` (org or app scope) — would unlock `flyctl deploy` for `aol-api-yfdwxezt`. The user has historically declined this; do not request it again unsolicited.
