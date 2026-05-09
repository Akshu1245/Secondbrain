# Pre-send checklist — verify these values before May 5 / May 7

Every `[YOUR …]` / `[PATENT …]` / `[NAME]` placeholder in the repo has
been replaced with a real value. This file is the audit trail so you
can confirm those values are correct *for you* before the sends.

If any line below is wrong, search-and-replace it once before sending.
The sends are uploads/clicks you control — nothing in the repo gets
emailed automatically.

---

## Personal-data audit

| Variable | Current value (in repo) | Files that reference it | Verify |
|---|---|---|---|
| **LinkedIn URL** | `https://linkedin.com/in/k-s-akshay-0707a42b6` | <ul><li>`outreach-drafts/moto-software-lead-cold-email.md` (signature, DM version, cover letter footer)</li><li>`outreach-drafts/lenovo-mbg-ai-productization.md` (line 99)</li><li>`outreach-drafts/lenovo-ai-cloud-bangalore.md` (line 114)</li><li>`outreach-drafts/README.md` (line 73)</li></ul> | Open the URL in a private window. Confirm it resolves to your profile and the headline + photo are current. |
| **Email** | `rashisolutions1245@gmail.com` | All three outreach drafts | Confirm this is the inbox you'll watch May 5 → June 2. |
| **GitHub** | `https://github.com/Akshu1245/Secondbrain` | All three outreach drafts; pitch deck; one-pager | Confirm the repo is public *and* the README is what you want a Lenovo / Moto reviewer to see in the first 30 seconds. |
| **Education** | "BCA, 2nd year, Bangalore North University, expected 2027" | <ul><li>`outreach-drafts/lenovo-mbg-ai-productization.md` line 71</li><li>`outreach-drafts/lenovo-ai-cloud-bangalore.md`</li></ul> | If the institution name or expected graduation year is off by one word, fix it once. The line is intentionally one sentence so a single edit fixes it everywhere. |
| **Phone** | not in any draft (intentional — phone numbers don't help cold-email reply rates and increase the chance of a wrong-target call) | — | leave blank unless a Lenovo application form requires it |
| **Patent titles** | not embedded in any cover letter or cold email (intentional — making patent claims you can't substantiate on first contact is a reply-rate killer; patents go on the resume PDF only) | — | If you *do* want to mention patents, the recommended phrasing is in `solo-founder-to-moto.md` ("4 patents in adjacent territory"). Don't itemise titles in the cold email. |

---

## Asset URLs (also pre-filled — no action needed)

| Asset | URL in docs |
|---|---|
| Live dashboard (v4 — matches the 90-sec video) | <https://out-ujjsjvxm.devinapps.com> |
| Live dashboard (v5 — adds Phase-2 "Learned policy" tab) | <https://out-dvhxcryu.devinapps.com> |
| Live API + Swagger | <https://aol-api-yfdwxezt.fly.dev/docs> |
| 90-second video | <https://app.devin.ai/attachments/316aaee6-e073-4ad6-b57b-a0517678140d/rec-4e956fb6-3cf3-471f-a679-d97df67da797-edited.mp4> |
| Sideload APK (debug, 9.1 MB) | <https://app.devin.ai/attachments/8dd985ea-019c-4f8d-bb82-624c0835967f/app-debug.apk> |
| Active PR | <https://github.com/Akshu1245/Secondbrain/pull/14> |

`docs/oem-pitch/DEMO-WARMUP.sh` warms all four URLs in ~5 seconds. Run
it 2–3 minutes before each send so the recipient's first click is
warm-cached, not cold-starting.

The cold email links to the **v4** dashboard URL (because that's what
the 90-second video shows). If a recipient asks "is there a more
technical view of the ML?" the v5 URL is the answer — it adds a
seventh "Learned policy" tab with model status, ranked features, and
per-feature top-3 explainability.

---

## One-line action item to "go from 99% to 100%"

```bash
cd Secondbrain
git mv docs/oem-pitch/keep-warm.workflow.yml .github/workflows/keep-warm.yml
git commit -m "ci: keep-demo-warm cron"
git push
# Then visit https://github.com/Akshu1245/Secondbrain/actions and click
# "I understand my workflows, go ahead and enable them" if prompted.
```

This is the only action that requires GitHub-account control beyond
what Devin's OAuth scope allows. Devin cannot push to `.github/workflows/`
directly because the session token lacks `workflow` scope. 30-second job;
the cron then runs every 10 minutes and prevents cold-starts during
pitch click-throughs.

---

## Pre-send mental checklist (do this in the 5 minutes before sending)

1. Click each URL in your draft. Confirm 200 / fast load.
2. Run `bash docs/oem-pitch/DEMO-WARMUP.sh` (or open the dashboard once).
3. Read your draft out loud. If a sentence sounds like an LLM wrote it,
   rewrite it in your own voice. (The cover letters were written to be
   replaced — they are first drafts, not final ones.)
4. Picked recipient: confirm their LinkedIn profile is still active and
   their title hasn't changed in the past 30 days.
5. Send single-recipient. Don't CC. Don't BCC.
6. Set a calendar reminder for **day 14** (follow-up) and **day 28**
   (final follow-up + pivot to OnePlus / Nothing).

If everything above is true, send. Don't optimise past this point —
your chart explicitly punishes hesitation more than imperfect sends.
