# AOL — AI Optimization Layer

A pitch deck for OEM AI / Software / Product leaders. 10 slides. Read in &lt; 5
minutes. Every claim has a source.

---

## Slide 1 — Title

**AOL: the AI Optimization Layer for smartphones.**

Middleware that sits between the user and the OEM AI assistant. Cuts cloud-AI
spend, hides feature clutter, surfaces context-relevant capabilities, and ships
a Control Panel users actually own.

Live demo: <https://out-ujjsjvxm.devinapps.com>
API: <https://aol-api-yfdwxezt.fly.dev/docs>

---

## Slide 2 — The problem nobody on stage will say out loud

> Every OEM is paying for cloud AI compute that users won't pay for.

| Stat | Source |
|---|---|
| **73% of iPhone users + 87% of Samsung users** say AI features add *little to no value* | [TechRadar](https://www.techradar.com), May 2025 |
| **86.5% of iPhone AI users + 94.5% of Galaxy AI users** *would not pay* to use AI features | TechRadar / SellCell |
| Only **11% of US adults** would upgrade their phone for AI — down 7 pts YoY | [ITC.ua](https://itc.ua), 2025 |
| #1 Moto AI user complaint: *"forced installation as bloatware after system updates"* + Perplexity pre-install rejection | [MakeUseOf](https://www.makeuseof.com) / Chrome-Stats |

The market is screaming the same thing in three languages: AI features are
*surface noise* on top of an unsustainable compute subsidy.

---

## Slide 3 — The diagnosis (so the fix is obvious)

Every flagship phone now ships with the same shape of AI:

1. A handful of features users **actually love** (Smart Reply, Spam Call
   Filter, Screenshot Text, Live Caption).
2. A long tail of features users **never touch** (AI Wallpaper Studio,
   Story-Maker, Generative Fill, Emoji Kitchen, AI Music Remix).
3. A **cloud bill** that scales with both — and a **homescreen** that surfaces
   them with equal weight.

OEMs ship more, users use less, and the cloud bill grows month-over-month.

---

## Slide 4 — The product (in one sentence)

**AOL is the system layer that decides which AI feature to show, when to show
it, and where to run it.**

| Module | What it does | The win |
|---|---|---|
| 1. Usage Tracker | Counts which features fire vs. sit idle | Evidence-based prioritisation |
| 2. Smart Feature Filter | Hides &lt; 3-events-per-30d features outside priority categories | Cleaner homescreen, less bloatware perception |
| 3. Context Engine | (time-of-day × activity) → top-3 surfaced features | "Right tool, right moment" without ML |
| 4. Compute Optimizer | Rule-based local vs. cloud routing per call | **$ saved on cloud bill, observable per call** |
| 5. Control Panel | Per-user toggles + priority categories + battery / data / private modes | Users feel ownership; OEM gets feedback |
| 6. Feedback Loop | "love / ok / annoying / never_use" → auto-disable / re-enable suggestions | Continuous improvement, no model retraining |

All rule-based by default, runs on-device, logs every decision. Phase-2
optional: a 150-line pure-Python logistic-regression engagement model
(`apps/aol/api/app/learned.py`) that re-ranks the Smart Filter's output
using the user's own usage + feedback log — with per-feature top-3
explainability and an automatic fallback to the rule-based engagement
estimate when training data is thin or the model would underperform the
baseline. Plugs into a real OEM AI via an Android Service (AIDL stub at
`docs/oem-pitch/integration/`; buildable reference APK at
`apps/aol-android/`).

---

## Slide 5 — Demo metrics (from the deployed MVP, not slides)

Numbers below are **live** from <https://out-ujjsjvxm.devinapps.com>.

- **Surface size: 24 → 17 features (–25%)** after AOL applies the filter.
- **Compute router on a sample run of 11 invocations:** ~45% local,
  ~55% cloud. Latency savings come from the locally-routed light
  tasks (the cloud round-trip is avoided); the headline value is the
  **eliminated cloud-AI call count**.
- **Per-call cloud cost** (`$0.0008` per cloud call, seed-data
  illustrative — real OEM cost-per-call is typically 3–10× higher).
  At a *10,000-device × 50-invocation/day* pilot, AOL's local routing
  eliminates ~6.75M cloud calls/month, equating to **~$5K/month at
  the seed-data cost** and into the **low-five-figure $/month range**
  at realistic OEM cost-per-call. Surface hiding stacks on top.
- **Demo:** click "Before / After" on the live dashboard. Click "Compute
  Router" → "Run routing". Click "Why This Matters" for the citations.

---

## Slide 6 — The integration story

AOL is a Foreground Service exposing a single AIDL interface ([`docs/oem-pitch/integration/`](./integration/)):

```aidl
interface IAolMiddleware {
    Bundle filterSurface(in List<String> featureIds, in Bundle context);
    OptimisationDecision routeCompute(String featureId, in Bundle hints);
    void recordOutcome(in OutcomeEvent ev);
}
```

The Moto AI assistant — or any OEM AI — calls AOL **before** rendering its
home strip and **before** dispatching a feature to its compute backend. AOL
returns a smaller, ordered list and a routing verdict.

That's it. No model retraining, no UX rewrite, no risk to the existing
Gemini / Perplexity contracts.

---

## Slide 7 — Why now / why this team

**Why now**

- AI on phones has hit the trough of disillusionment. The *next* differentiator
  is who removes friction, not who adds features.
- OnePlus is publicly calling its 2025 roadmap *"Your Secondary Mind"* — exactly
  what AOL + Second Brain (companion product) deliver.
  ([Digital Trends](https://www.digitaltrends.com))
- Moto AI's own positioning (*"Catch Me Up"*, *"Pay Attention"*, *"Remember
  This"*) is begging for a memory layer it doesn't yet have.
  ([Motorola News](https://news.motorola.com))

**Why this team**

- Already shipped `Second Brain` v0 → v2 (memory consolidation, decay,
  multi-hop recall, episodic provenance) on a public repo with 3 PRs and 7+
  commits before this pitch landed. (Ask for the repo URL — it's not the empty
  README the advisor saw.)

---

## Slide 8 — Business model

We don't try to monetise the user. We monetise the OEM's *cost line*.

| Tier | What we sell | Pricing |
|---|---|---|
| **Pilot** | AOL drop-in, 1 SKU, 10K devices, 90 days | Flat fee, capped, success-criteria-based |
| **Per-device licence** | AOL on a device family | Low five-figure annual base + ~$0.05/device/yr |
| **Compute rev-share** | We get a slice of the *measured* cloud-spend reduction | 15–25% of audited delta |
| **Bundled with Second Brain** | Memory + optimisation as a single AI-platform layer | Negotiated, partnership-tier |

The pitch in one line: *"You're already spending the money. Pay us a fraction
of what we save you."*

---

## Slide 9 — The 3-step ask

1. **15 minutes** with the AI / Software / Product lead. We screen-share the
   demo and walk the integration path.
2. **A 90-day pilot** on a single device family. We measure cloud-call
   reduction, surface-noise reduction, and feature engagement against control.
3. **Either an integration deal or a referral to the next-best OEM** — we win
   either way; you've spent 15 minutes and walked away with three numbers you
   didn't have before.

---

## Slide 10 — Closing

Everyone is shipping more AI features. The differentiator isn't more features.
It's the system layer that makes the features users already have feel less
bloated and cost less to run.

That's AOL.

- Live demo: <https://out-ujjsjvxm.devinapps.com>
- API: <https://aol-api-yfdwxezt.fly.dev/docs>
- Integration stub: [`docs/oem-pitch/integration/`](./integration/)
- One-pager: [`docs/oem-pitch/one-pager.md`](./one-pager.md)
- OEM targets + outreach: [`docs/oem-pitch/oem-targets.md`](./oem-targets.md), [`docs/oem-pitch/oem-outreach.md`](./oem-outreach.md)
- User pain audit: [`docs/oem-pitch/user-pain-audit.md`](./user-pain-audit.md)
- Code: [`apps/aol/`](../../apps/aol/) (this monorepo)
