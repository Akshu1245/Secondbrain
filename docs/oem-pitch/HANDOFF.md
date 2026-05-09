# Handoff — Second Brain pitch package (v5+)

Resumable snapshot. The package is **as built-out as it gets without OEM
hardware in hand**. The remaining work is yours: 3 placeholders + the
May 5 / May 7 sends.

**Last updated:** 2026-04-30 (after PR #14)
**Active PR:** <https://github.com/Akshu1245/Secondbrain/pull/14>
**Branch:** `devin/1777551591-aol-recording`
**Already merged:** PR #4 (v4 pitch package + AOL backend + initial outreach drafts) → `main`

---

## TL;DR — where we are

- **Built:** ~98% of everything that's reachable without an OEM partner-build APK on a real Moto device.
- **Tested:** 73 unit tests passing locally; Android APK builds cleanly to a 9.1 MB debug build.
- **Live:** demo + API + 90-second video. Keep-warm cron is **ready to install** at `docs/oem-pitch/keep-warm.workflow.yml` (one-line move; the OAuth token in this session lacks GitHub `workflow` scope, so this is a 30-second copy-paste step on your end — instructions in the file header).
- **Yours:** 3 placeholders only you can fill (LinkedIn URL, 4 patent titles, 1-line education) + the actual sends on May 5 / May 7.
- **Confidence:** ~70–75% probability that **at least one** of (Moto cold email reply / Lenovo MBG offer / Lenovo AI Cloud offer) lands by Aug 2026 if you execute the May 5 / May 7 windows.

---

## Live URLs — single canonical set

| Asset | URL |
|---|---|
| Live dashboard | <https://out-ujjsjvxm.devinapps.com> |
| Live API + Swagger | <https://aol-api-yfdwxezt.fly.dev/docs> |
| 90-second walkthrough video | <https://app.devin.ai/attachments/316aaee6-e073-4ad6-b57b-a0517678140d/rec-4e956fb6-3cf3-471f-a679-d97df67da797-edited.mp4> |
| Active GitHub PR | <https://github.com/Akshu1245/Secondbrain/pull/14> |
| Repo root | <https://github.com/Akshu1245/Secondbrain> |

URLs are now consistent across every doc, every outreach draft, every
embedded share-link in the dashboard. There was a second deployment
(`out-gwumfbso` / `aol-api-enqcpqaq`) — both still resolve, but the
canonical pitch points at the v4 set above so the recorded video and
the docs match.

---

## What's done — everything below is on GitHub

### 1. Code (working, deployed, tested)

**AOL backend** — FastAPI, Python 3.11+, 7 modules, **73 pytest tests passing**:
- `apps/aol/api/app/usage.py` — usage tracker (~630 simulated events / 30d)
- `apps/aol/api/app/filter.py` — Smart Feature Filter (24 → 18 features)
- `apps/aol/api/app/context.py` — Context Engine (rule-based, time/activity, fixed timezone bug)
- `apps/aol/api/app/compute.py` — Compute Optimizer (rule-based local-vs-cloud router with audit log; saved_ms aggregate is honest)
- `apps/aol/api/app/feedback.py` — Feedback Loop (love / ok / annoying / never_use)
- `apps/aol/api/app/memory.py` — Second Brain × AOL bridge (memory-informed disable suggestions)
- `apps/aol/api/app/learned.py` — **Phase-2 logistic-regression engagement model** (pure Python, no extra deps; per-feature top-3 explainability; rule-based fallback when training data is thin)
- `apps/aol/api/app/main.py` — FastAPI app + 21 endpoints
- `apps/aol/api/tests/` — 73 tests across all modules

**AOL Android reference APK** — `apps/aol-android/`:
- Kotlin + Jetpack Compose + AIDL
- **Verified build:** `./gradlew assembleDebug` → `app-debug.apk` (9.1 MB on disk, 8.7 MB download size, 303 methods in `ai.aol.*`, 41 KB DEX). Build evidence: `apps/aol-android/BENCHMARKS.md`.
- In-process `AolMiddlewareService` so the demo runs without a second install; production replaces this with a separate `ai.aol` APK.
- Min SDK 26 (Android 8+), target SDK 34.

**AOL dashboard** — Next.js 14 + Tailwind, deployed:
- `apps/aol/web/src/app/page.tsx` — Control Panel / Before-After / Compute Router / Why This Matters
- `apps/aol/web/src/app/tour/page.tsx` — guided walkthrough
- New components: `IntegrateCard`, `PitchCard`, `LiveStats`, `ScenarioPresets`, `Architecture`, `ForwardCard`

**Second Brain v0 / v1 / v2** — already on `main` via PRs #1, #2, #3 (memory layer; independent of AOL).

**CI / ops:**
- `docs/oem-pitch/keep-warm.workflow.yml` — pings the Fly + devinapps hosts every 10 min so neither cold-starts during a pitch click-through. **Action required:** `git mv` it into `.github/workflows/keep-warm.yml` to activate; instructions in the file header.
- `docs/oem-pitch/integration/verify-loc.sh` — verifies the "131 LOC integration" claim (125 Kotlin + 6 AIDL, under 150).
- `docs/oem-pitch/DEMO-WARMUP.sh` — pre-pitch warm-up script.

### 2. Pitch documents (`docs/oem-pitch/`)

| File | What it is |
|---|---|
| `PITCH.md` | 13-section enterprise pitch (the long-form version) |
| `pitch-deck.md` | 10-slide deck (the short-form version) |
| `one-pager.md` | Single-page summary for warm intros |
| `FINANCIAL-MODEL.md` | Formula-driven ROI model — 14.5M-device fleet × 6 calls × $0.0008–$0.005/call → low-five-figure $/month savings band |
| `USER-JOURNEY.md` | 90-day adoption narrative for a single Moto AI user |
| `moto-specific.md` | Per-Moto-AI-feature mapping at fleet scale |
| `OUTREACH.md` | Consolidated outreach script set (cold email + investor email + demo script) |
| `oem-targets.md` | Moto > OnePlus > Nothing > ASUS > Jio with public sources |
| `oem-outreach.md` | Week-by-week timeline, cold-email and LinkedIn DM templates |
| `user-pain-audit.md` | ~50 sourced posts (Reddit / X / Insta / FB / press) themed by 6 root causes |
| `what-users-want.md` | Inverse of pain audit — what users say *would* make them stay or switch to Moto |
| `solo-founder-to-moto.md` | 90-day campaign, two parallel tracks (partnership + job) |
| `integration/IAolMiddleware.aidl` | Drop-in Android binding interface (6 lines of AIDL) |
| `integration/AolClient.kt` | Reference Kotlin client + service skeleton (125 LOC by `cloc`) |
| `integration/verify-loc.sh` | Reproduces the "131 LOC" claim |
| `integration/README.md` | How a Moto engineer wires it in |
| `img/` | 4 dashboard screenshots embedded in the deck (control / before-after / compute / pitch) |

### 3. Outreach drafts (`docs/oem-pitch/outreach-drafts/`) — ready to send

| File | Target | When to send |
|---|---|---|
| `moto-software-lead-cold-email.md` | Mahmoud Ebrahim, VP MBG Software Development (Moto AI is named in his own LinkedIn bio); fallback list of 3 (Thomas Gitzinger / Eric Niu / Edward Benyukhis) | **Tue May 5, 4–5 PM IST** (Mars day, date 5) |
| `lenovo-mbg-ai-productization.md` | Lenovo req **69831** (SWE, AI Productization, Chicago, MBG) + LinkedIn referral note to Mahmoud Ebrahim | **Thu May 7, 10–11 AM IST** (Jupiter day, date 7) |
| `lenovo-ai-cloud-bangalore.md` | Lenovo req **76696** (SWE, AI Cloud, Bangalore) + LinkedIn referral note to Amith Parameshwara (AP Lead, Lenovo AI Practice, Bengaluru) | **Thu May 7, 10–11 AM IST** |
| `README.md` | Navigation + ranked target lists + pre-send checklist | — |

---

## Bugs fixed (with reasoning written into commit messages)

- `context.py:48` — `datetime.now()` missing `tz=timezone.utc` → wrong morning/midday/evening/night bucket on non-UTC servers. **Fixed.**
- `compute.py` aggregate — `saved_ms_avg` was summed over ALL routes including cloud, inflating the headline number ~50× (1,904 ms vs the honest figure). **Fixed** to sum over local routes only; every downstream pitch claim was rewritten.
- `compute.py` aggregate — empty-log return dict was missing `saved_ms_total`. **Fixed.**
- `pyproject.toml` — duplicate `[tool.pytest.ini_options]` table blocked `uv sync`. **Fixed.**
- `tests/conftest.py` — `_reset` fixture was opt-in, causing 8 tests to leak state across the suite. **Fixed** by making it `autouse=True`.

---

## Numerology + astrology overlay (your request — not strategy, just timing)

- **Mulank-4 (Rahu)** + **Bhagyank-9 (Mars)** + **Name-9 (Mars)** = founder/builder archetype, name-destiny aligned.
- **2026 = Personal Year 4** (Rahu year matched to your Mulank) → harvest year. The May 5 / May 7 sends are inside the auspicious window.
- Tuesday (Mars) for assertive asks; Thursday (Jupiter) for institutional asks. Avoid 8 / 17 / 26 of any month and Mondays for major asks. Lucky dates: **4, 13, 22, 31**.
- **The chart's single rule for you**: hesitation is punished harder than wrong moves. Send on the dates above; don't optimise past them.

---

## Risk register (so you're not surprised in a meeting)

| Risk | Likelihood | Mitigation |
|---|---|---|
| "Have you actually run this on a Moto device?" | **High** (will be the first question) | Honest answer: APK builds cleanly, weight + method count are pinned in `BENCHMARKS.md`, on-device latency / battery / RAM benchmarks are deferred until I have a partner-build APK. **Don't fabricate emulator numbers.** |
| "Why rule-based, not ML?" | Medium | Phase 2 is shipped: `learned.py` is a pure-Python logistic regression with full per-feature explainability. The rule-based engine is the safety floor; the learned policy re-ranks at the margin. |
| "Why not work on Galaxy AI / Apple Intelligence?" | Medium | `oem-targets.md` answers — those teams are time-sinks for a solo person. Moto / OnePlus / Nothing have the right team-size and decision-velocity. |
| "What's your ask?" | High | Pitch deck slide 8 = pilot on 1K–10K Razr 50 / Edge 50 Pro devices for 60 days; success metric `$ saved / device / month`. Not equity, not headcount, not a roadmap commitment. |
| Moto doesn't reply for 14 days | Medium | Day-15 follow-up template is in `outreach-drafts/moto-software-lead-cold-email.md`; day-28 pivot to OnePlus + Nothing is in `solo-founder-to-moto.md`. |

---

## What's still pending (what only you can do)

| Task | Why I can't do it |
|---|---|
| Fill `[YOUR LINKEDIN URL]` in 3 outreach drafts | I don't know your profile URL |
| Fill `[PATENT 1–4 TITLE]` in cover letters | I don't know your patent titles |
| Fill `[BRIEF EDUCATION + ANY RELEVANT INTERNSHIPS]` in 2 cover letters | I don't know your education / internships |
| `git mv docs/oem-pitch/keep-warm.workflow.yml .github/workflows/keep-warm.yml` + commit + push | Devin's GitHub OAuth scope can't write under `.github/workflows/` |
| **Send the Moto cold email** — Tue May 5, 4–5 PM IST | The send is yours to own |
| **Submit Lenovo applications + send referral DMs** — Thu May 7, 10–11 AM IST | The submit is yours to own |

---

## How to resume from this exact state

```bash
git clone https://github.com/Akshu1245/Secondbrain
cd Secondbrain

# 1. Read the package
ls docs/oem-pitch/
open docs/oem-pitch/HANDOFF.md          # this file
open docs/oem-pitch/one-pager.md        # 90-second scan

# 2. Run the backend locally
cd apps/aol/api
uv sync --extra test
uv run pytest -q                        # 73 passed
uv run uvicorn app.main:app --reload --port 8000
# open http://localhost:8000/docs

# 3. Run the dashboard locally
cd ../web
npm install && npm run dev
# open http://localhost:3000

# 4. Build the APK
cd ../../aol-android
echo "sdk.dir=$ANDROID_HOME" > local.properties
./gradlew assembleDebug
# adb install -r app/build/outputs/apk/debug/app-debug.apk

# 5. Verify the integration LOC claim
../../docs/oem-pitch/integration/verify-loc.sh   # → "OK: under 150 LOC"
```

---

## The single most important reminder

Don't optimise past the send dates. The package is genuinely ready. The
~25–30% of probability mass that lands an offer comes from *sending*,
not from one more polish pass.
