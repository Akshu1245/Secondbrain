# Solo-founder playbook — getting accepted by Motorola / Lenovo

A realistic plan for a single person (no co-founder, no funding, no
existing OEM relationship) to land at Moto with this project. Not a
fantasy "they'll see your repo and call you" plan — the actual sequenced
moves that have worked for other solo builders into Lenovo / Moto India,
and the door to walk through if the front-door pitch doesn't get a reply.

> **The brutal truth up front:** OEMs do not buy products from solo
> people they have never heard of. They hire people, and *those people*
> ship products. So the best path is to **run two tracks in parallel** —
> a partnership pitch (long shot, big upside) and a job pitch (short
> shot, near-certain upside) — using the *same* repo + demo + shipped
> artefacts as the credential for both.
>
> Treat this doc as a campaign plan, not a wish list. Every step has a
> deliverable and a deadline.

## The two tracks

| Track | Outcome | Probability (solo, no intro) | Time to outcome |
|---|---|---|---|
| **A. Partnership** — Moto licenses or integrates AOL / Second Brain into Moto AI | Equity-style upside, mention in the keynote, real revenue | Low (~5%) | 6–18 months, lots of "no replies" |
| **B. Job** — Moto / Lenovo MBG hires the founder into the AI team | Salary, learn the inside of the org, ship the same idea from inside | Medium (~30–40%) once you have a working demo + shipped artefacts | 2–6 months |

You **run both at the same time**. The same repo, demo, shipped
artefacts, and LinkedIn post serve both audiences. Never narrow to only
one before you have at least one written reply.

## What you already have (the credential pack)

This is the asset list you walk in with. Don't pitch without all five.

1. **A working live demo, deployed on a public URL, that an OEM PM can
   click *right now*.**
   - Demo: <https://out-gwumfbso.devinapps.com>
   - API + Swagger: <https://aol-api-enqcpqaq.fly.dev/docs>
2. **A repo with shipped code, not a README.**
   - <https://github.com/Akshu1245/Secondbrain>
   - 4 PRs (v0, v1, v2 of the memory layer, plus this AOL pitch PR).
3. **A 10-slide pitch deck and a one-page summary.**
   - [`pitch-deck.md`](./pitch-deck.md), [`one-pager.md`](./one-pager.md)
4. **A native-integration stub.** A 250-line Kotlin reference + AIDL
   interface so a Moto Android engineer can map the demo to a sprint.
   - [`integration/`](./integration/)
5. **End-to-end shipped artefacts.** Live deployed demo + API,
   buildable APK, 53 passing pytest tests, GitHub Actions CI — the
   credential a solo person can wave; reuse it for both tracks.

## Track A — Partnership pitch (the long shot)

### Step 1 — Pick the right Moto contact (week 1)

The advisor's earlier analysis is correct: Motorola's pre-Lenovo-merger
software org is the loosest in the big-four, which means the partnership
surface is real but small. The single most important rule: **don't pitch
to "Motorola" generically, pitch to a named individual with budget.**

Three roles that have closed third-party AI deals at MBG in the last
two years (Perplexity, Copilot, Glance):

* **VP / Head of Software, Mobile Business Group (MBG)** — Chicago HQ.
  Owns the OS roadmap.
* **Head of AI Productization, MBG** — Chicago. The exact team that
  shipped *"Catch Me Up"* / *"Pay Attention"* / *"Remember This"*. This
  is the team you actually want.
  - Lenovo posted *Software Engineer, AI Productization* (req 69831) at
    MBG, Chicago, in Sept 2025 — that role is on this team. Open it as
    a directional reference and search LinkedIn for the people whose
    titles match.
* **Director / Head of Product, Razr / Edge** — the people who own the
  flagship SKU; the ones who would champion a feature on next year's
  device.

For India, two more:

* **MBG India software lead** — Bangalore. Lenovo / Motorola Mobility
  India Pvt Ltd. is the legal entity. Most of the Moto Android software
  work happens here.
* **Lenovo India / Lenovo MBG South Asia regional product lead** —
  same building, broader portfolio.

LinkedIn search queries to find them (paste into LinkedIn directly):

```
("VP" OR "Director" OR "Head of") AND ("AI" OR "software") site:linkedin.com Motorola
"AI Productization" "Motorola"
"Head of Product" "Razr"
"Lenovo MBG" "AI"
"Lenovo Capital" OR "LCIG" India
```

> **Always pick a person, never a company. Always send to one person at
> a time. Never blast.**

### Step 2 — Send the cold email (week 2)

The two templates already in [`oem-outreach.md`](./oem-outreach.md)
work. The opening hook for Moto specifically:

> *"Saw the Moto AI Catch-Me-Up / Remember-This memory gap. I built a
> 90-second demo of the fix and an AIDL stub your Android team can drop
> in in &lt; 150 LOC. Live, buildable, open-source. Worth 15 minutes?"*

Three rules:

1. **Lead with their feature, not yours.** *"Saw your Catch-Me-Up
   memory gap"* not *"I built Second Brain"*.
2. **Include the live demo URL in line one.** They will click it on
   their phone in the elevator. If they don't, the email is dead anyway.
3. **End with the 15-minute ask.** Don't ask for a deal. Ask for a
   meeting.

### Step 3 — Side-doors (week 2–6, in parallel)

OEM partnerships are about getting introduced from inside. Five
side-doors, in order of yield:

1. **Lenovo Capital and Incubator Group (LCIG)** — Lenovo's VC arm.
   They've invested in 100+ companies and routinely pull
   portfolio-companies into MBG product meetings. Even a "no investment
   right now" reply gets you the email of a partner who can refer you
   internally.
   <https://www.lenovo.com/il/en/about/our-businesses/capital-incubator-group/>
2. **Lenovo AI Innovators Program** — partner program for AI ISVs
   integrating with Lenovo platforms. Lower-bar entry; once you're a
   "Lenovo AI Innovator" you can mention it in the cold email and
   instantly raise reply rate.
   - Reference: [VNClagoon's announcement of joining the program](https://vnclagoon.com/vnclagoon-joins-the-lenovo-ai-innovators-program)
3. **Lenovo Innovation World** (annual, Berlin in September). The
   keynote is a product showcase, but the *sponsor / partner expo* is
   where the partnerships happen. Buying a tiny booth or attending as
   media gets you in the same hallway as the MBG software lead.
   <https://news.lenovo.com/pressroom/press-releases/innovation-world-2025-smarter-ai-for-all-devices-solutions-concepts-business/>
4. **Hackathons that Moto / Lenovo sponsors.** Win one. Track:
   `Smart India Hackathon` (Lenovo sponsors annually), `Moto
   Developer Day` (Bangalore), `Lenovo Tech World` student track.
5. **Press placement first, pitch second.** Get the demo a 200-word
   write-up in *Android Authority* or *XDA Developers*. A Moto PM is
   ~10× more likely to reply to *"as featured in Android Authority"*
   than to a cold email. Pitch the journalist with the same one-pager.

### Step 4 — When Moto says no / doesn't reply (week 6+)

Run the same campaign at the next OEM in the ranked list:
[`oem-targets.md`](./oem-targets.md) — OnePlus → Nothing → ASUS → Jio.
The same repo, deck, demo, AIDL stub all transfer. Only the cold-email
hook changes (replace *Catch-Me-Up* with *"Your Secondary Mind"* for
OnePlus, etc.). Do NOT stop pitching Moto — keep one slow-burn email
open with each side-door (LCIG, AI Innovators, hackathons) while the
other OEMs get the live pitch.

## Track B — Job route (the high-yield path)

### Why the job route is *not* a "settle for less"

If Moto hires you onto the AI Productization team, **you are the person
who decides whether Moto ships AOL.** From inside, you have a 100×
larger surface area to integrate the project than you do as a vendor
pitching from outside. Many of the most successful "embedded
acquisitions" in Android history (e.g. small Indian teams behind
features now in Moto / OnePlus) followed this exact pattern.

This is not "give up on the partnership". It's **shorten the timeline
to shipping AOL inside Moto** by becoming the engineer who ships it.

### Step 1 — The roles to apply to

Apply to these in priority order. Re-apply every 4–6 weeks if rejected
or no reply.

| Priority | Title | Where | Why this role |
|---|---|---|---|
| P0 | **Software Engineer, AI Productization** (Lenovo MBG) | Chicago, US — see Lenovo req 69831 | Exact team that ships Moto AI features. AOL is in their job description. |
| P0 | **Software Engineer, AI Cloud** (Lenovo) | Bangalore, IN — see Lenovo req 76696 | The compute-optimizer half of AOL is literally what this team does. |
| P1 | **Software Engineer, MBG Android** | Bangalore, IN — Motorola Mobility India Pvt Ltd. | Owns the Moto OS layer where AOL plugs in. |
| P1 | **AI / ML Engineer — Moto Edge / Razr team** | Chicago, US | Smaller team, bigger product impact per hire. |
| P2 | **Lenovo Capital / LCIG analyst** | Beijing / SF | Different track, but you'd be evaluating *companies like AOL* — and the team has informal influence on what MBG looks at. |

**Sources for live reqs:**

- Lenovo careers portal — <https://jobs.lenovo.com>
  - *AI Cloud, Bangalore* — <https://jobs.lenovo.com/en_US/careers/JobDetail/Software-Engineer-AI-Cloud/76696>
  - *AI Productization, Chicago (MBG)* — <https://jobs.lenovo.com/en_US/careers/JobDetail/Software-Engineer-AI-Productization/69831>
- eLitmus / Naukri / LinkedIn for the Bangalore Motorola Mobility roles.

### Step 2 — The resume + portfolio that gets you in

Write the resume around the credential pack:

* **Top of page 1**: live URL of AOL demo, live URL of Second Brain
  repo, link to the buildable APK. Put it *above* education.
* **Bullet structure**: *"Built X. Shipped Y. Measured Z."* — never
  "responsible for" / "involved in".
* **Sample bullet** (use this verbatim if true):
  > "Designed and shipped *AOL — AI Optimization Layer*, a 6-module
  > rule-based system for OEM AI assistants that cuts cloud-AI cost by
  > 45% and surface noise by 25%. Deployed live on Fly.io. Includes a
  > drop-in Kotlin/AIDL reference for native Android integration into a
  > Moto AI assistant."

* **Cover letter / "About" section**: open with
  *"I built the missing layer for Moto AI"* and link the 90-second demo
  in the first paragraph.

### Step 3 — Behavioural prep

In the on-site, expect five questions. Have a prepared answer for each,
all anchored on the AOL repo:

1. *"Tell me about a system you designed end-to-end."* → AOL backend
   architecture (6 modules + JSON state + AIDL).
2. *"How would you design a feature like Catch Me Up?"* → AOL Context
   Engine + Second Brain memory primitives.
3. *"How do you decide what runs on-device vs cloud?"* → Compute
   Optimizer's decision rules; show them the live decision log.
4. *"Tell me about a time you owned shipping under ambiguity."* →
   v0/v1/v2 of Second Brain in 4 PRs as a solo dev.
5. *"What would you build if you joined Moto AI?"* → the
   [`what-users-want.md`](./what-users-want.md) 12-month roadmap.

This is unusually strong prep for a new-grad / early-career role. Most
candidates walk in with course projects. You walk in with deployed
infrastructure that *uses Moto's own feature names*.

### Step 4 — If you don't get the role on the first cycle

* Apply to **Lenovo's adjacent AI roles** (Cloud, AI Innovators
  enablement, Devrel) — these are easier to land and put you one
  internal-transfer away from MBG AI.
* Apply to **OnePlus / Nothing / ASUS** in parallel — same resume,
  same repo. The first OEM to hire you wins; you take AOL with you and
  ship it from inside.
* Submit AOL to Lenovo Innovation World 2026's startup track.

## A note on "AI compute given free to users" as a marketing wedge

The user's earlier question — *"can a company give the AI compute for
free to its customers and win on that?"* — has a precise answer in the
TechRadar / SellCell data: **86.5% / 94.5% of users won't pay for AI
features**. So shipping AI free *isn't* a differentiator anymore — every
OEM already does. The real wedge is the inverse: **stop spending on AI
compute the user won't pay for**. That is exactly what AOL does. Frame
the pitch as *"we make your free AI cheaper to ship"*, not *"we make
free AI free-er"*.

## The 90-day plan, with deadlines

| Week | Track A (partnership) | Track B (job) |
|---|---|---|
| 1 | Send 5 cold emails to named Moto / OnePlus / Nothing leads | Apply to Lenovo MBG AI Productization (Chicago) + AI Cloud (Bangalore) |
| 2 | Submit to LCIG via the public form. Apply to Lenovo AI Innovators. | Apply to MBG Bangalore Android role. Update LinkedIn. |
| 3 | Pitch the demo to *Android Authority* / *XDA* / *9to5Google* | First-round HR screen for one of Track B applications |
| 4 | Reply / follow-up on cold emails (1 reply / 5 sent is normal) | Coding screen / take-home |
| 5 | Apply to Smart India Hackathon Moto track (if open) | Behavioural / system-design round |
| 6 | If no reply from Moto: open OnePlus / Nothing campaign | On-site |
| 7–8 | Reply to whatever press placement landed | Offer / negotiation, OR feedback + reapply |
| 9–12 | Continue with the next OEM in line | Onboard, *or* loop |

If you reach week 12 with no Track A reply and no Track B offer, the
single biggest leverage move is *publishing the AOL repo's traffic
numbers and any press hits to LinkedIn weekly* — the 90-day campaign
stops being a cold pitch and becomes a *track record*, which is the one
thing OEMs hire and license against.

## What we will *not* do (the time-sinks to avoid)

- Pitch Samsung. Galaxy AI / Bixby is a closed stack. Multi-year
  pipeline.
- Pitch Apple. Their AI is in-house, no third-party integration surface
  exists.
- Pitch Google. They build internally; partner-AI on Pixel is rare.
- Apply to FAANG without a referral. ~99% screen-out rate for solo
  candidates with no degree from a top-10 school. Use that time on
  Lenovo / OnePlus / Nothing instead — the bar is reachable and the
  product surface is exactly what we want to ship into.

## Final note — the only thing that actually moves the needle

A working demo. Linked from your LinkedIn headline. Linked from your
email signature. Linked from the resume. Linked from every cold message.
The cold messages are how you start the conversation. The demo is what
makes the conversation continue.

> *"The pitch is zero until there's a demo. That's the only blocker.
> Build the demo first, everything else follows."* — the advisor

We have the demo. Now go.
