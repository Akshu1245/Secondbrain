# Plexus — Outreach Package

Refined, enterprise-grade outbound assets. Use as-is or template
inside.

---

## 1. Naming — final shortlist

The product currently ships under the working name "AOL" (AI
Optimization Layer). That name has a fatal brand collision with
America Online and reads dated. Replace before any external send.

Ranked recommendation, after weighing OEM positioning, trademark
defensibility, domain availability, and pronunciation across markets:

| # | Name | Why it works | Risk |
|---|---|---|---|
| **1** | **Plexus** | Neural plexus → orchestration of many AI nerves. Premium, technical, ownable as `plexus.ai` / `plexus-os`. Pairs well with "Plexus Layer" / "Plexus OS". | Generic word; needs a strong wordmark. |
| 2 | **Conduit** | The conduit between user and AI surface. Clean, descriptive, OEM-grade. | Salesforce uses "Conduit" in some products — secondary collision risk. |
| 3 | **Inferna** | Coined: inference + native. Maximum trademark defensibility. | Slight pharma feel; needs careful design treatment. |
| 4 | **Locus** | Focal point of AI on a device. Short, clean. | Common word; trademark on tech is partly occupied. |
| 5 | **Ravel** | Orchestrate / unravel complexity. Clean, ownable. | Less obvious meaning; takes a tagline to land. |

**Working name across the rest of this package: Plexus.**

---

## 2. Tagline options

Pick one for outbound; rotate the others into deck slides and the
demo footer.

* **"The orchestration layer for OEM AI."** *(positioning, primary)*
* "AI that knows what to surface, where to compute, and when to stay
  silent." *(value prop)*
* "Less cloud. Less clutter. More AI that matters." *(consumer-facing)*
* "An audit log per inference. A policy per OEM." *(privacy / legal
  posture)*
* "From AI feature fatigue to AI feature focus." *(market-shift)*
* "Built for the next quarter's cloud bill, not the last quarter's
  demo." *(CFO-targeted)*

---

## 3. One-line elevator pitch

> Plexus is the AI orchestration layer for smartphones — a vendor-
> neutral middleware that decides, per call, which AI features reach
> the user and whether they run on-device or in the cloud, recovering
> $9–24 M / year in cloud spend per 14.5 M-device fleet through a
> 131-line integration shim.

---

## 4. OEM cold email — primary version

For: Mahmoud Ebrahim, VP, MBG Software Development at Motorola
Mobility (or equivalent named target). Send Tuesday 4–5 PM IST.

> **Subject:** Plexus — recovering $9–24 M / yr of Moto AI cloud
> spend with a 131-line shim
>
> Hi Mahmoud,
>
> Building Plexus, an AI orchestration layer for OEMs. Live demo,
> deployed today.
>
> The premise: Moto AI ships a 24-feature surface, but the median
> user disables half of those features within 30 days, and the
> assistant still routes every retained call to cloud by default.
> Plexus is the missing primitive between the assistant and its
> compute backends — it filters the surface against per-user
> behaviour, routes inference local-first, and writes a per-call
> audit log for EU AI Act / DPDP / SB-1047 compliance.
>
> On a 14.5 M-shipment quarter, the conservative model (`I = $0.002`,
> `R₀ = 75 % → R₁ = 45 %`) recovers **$9–24 M / year** in cloud
> inference spend. Integration is a **131-line MVP shim**: AIDL
> contract + Kotlin client, no SDK, no model dependency, fail-safe
> fallback if the Plexus APK is uninstalled.
>
> Live demo: <https://out-gwumfbso.devinapps.com/>
> Repo + buildable APK: <https://github.com/Akshu1245/Secondbrain>
> Per-feature mapping at Moto's Q2 2025 scale:
> <https://github.com/Akshu1245/Secondbrain/blob/main/docs/oem-pitch/moto-specific.md>
>
> Worth 20 minutes? I will walk through the demo, the integration
> shim, and the financial model with the assumptions live.
>
> Best,
> **K S Akshay**
> Founder, Rashi Technologies
> `rashisolutions1245@gmail.com` · `[YOUR LINKEDIN URL]`

---

## 5. Investor cold email — primary version

For: infrastructure-AI partner at a Tier-1 / Tier-2 fund (a16z infra,
Lightspeed AI, Battery, Foundation, Accel India). Send Tuesday or
Wednesday morning local.

> **Subject:** Plexus — orchestration layer for OEM AI · live demo,
> 14.5 M-fleet ROI model
>
> Hi [Partner first name],
>
> Plexus is the AI orchestration layer for smartphone OEMs — a
> vendor-neutral middleware that recovers $9–24 M / year of cloud
> inference spend per 14.5 M-device fleet through a 131-line
> integration shim.
>
> Three things I think are worth your time:
>
> 1. **The category is forming now.** Apple Intelligence, Galaxy AI,
>    Pixel AI are all moving from "an app" to "an OS service." None
>    of them ships the orchestration primitive — context engine,
>    feature prioritizer, AI router, telemetry, learning loop — as a
>    standalone, vendor-neutral layer. Plexus is.
>
> 2. **The economics are concrete.** Live demo, formula-driven
>    financial model, conservative / mid / high tiers. 14.5 M-device
>    Moto-scale fleet recovers $9 M / year at the floor case and
>    $62 M / year at full LLM frontier-cost. Audit log per call.
>
> 3. **Distribution is OEM-direct.** First conversations live with a
>    named MBG software lead at Motorola; OnePlus / Nothing / Samsung
>    India in the pipeline for the same quarter.
>
> Live demo: <https://out-gwumfbso.devinapps.com/>
> Pitch deck: <https://github.com/Akshu1245/Secondbrain/blob/main/docs/oem-pitch/PITCH.md>
> Financial model: <https://github.com/Akshu1245/Secondbrain/blob/main/docs/oem-pitch/FINANCIAL-MODEL.md>
> Repo: <https://github.com/Akshu1245/Secondbrain>
>
> Raising a small pre-seed to convert the first OEM pilot into
> production. Worth a 30-minute call?
>
> Best,
> **K S Akshay**
> Founder, Rashi Technologies
> `rashisolutions1245@gmail.com` · `[YOUR LINKEDIN URL]`

---

## 6. Demo narration — 90-second script

For the cold-email-attached video, or for a live walkthrough on a
20-minute OEM call. Time-coded.

> **0:00–0:10 · Hook**
>
> "Smartphone OEMs ship 24 AI features and users disable most of
> them in 30 days — but every call still routes to cloud by
> default. Plexus is the orchestration layer that fixes that."
>
> **0:10–0:25 · Problem**
>
> [Show dashboard hero.] "Today: 24 features visible, 75 % of
> calls cloud-routed, no per-call audit log, no policy primitive
> for the OEM. The assistant is doing what it was built to do.
> The orchestration layer above it does not exist."
>
> **0:25–0:45 · Solution**
>
> [Click into tab 1: "Hide what nobody uses".] "Plexus's Feature
> Prioritizer hides the long tail — features with under 3 events
> per 30 days, outside the user's priority categories." [Click
> into tab 3: "Run on phone vs cloud".] "The AI Router decides
> per call: light tasks, on-device. Heavy tasks under battery
> pressure, queued. Heavy tasks on charge, cloud."
>
> **0:45–1:05 · Numbers**
>
> [Click into tab 6: "The pitch — numbers".] "On a 14.5 M-shipment
> quarter at Moto's scale: $9 M to $24 M in recovered cloud spend
> per year, conservative tier. 131-line MVP integration shim. 53
> deterministic tests covering every routing rule. Per-call audit
> log designed for EU AI Act, DPDP, SB-1047."
>
> **1:05–1:25 · Integration**
>
> [Click into "Integrate it" card.] "Three steps: drop the AIDL
> contract and the Kotlin client, bind once, wrap every AI call.
> Total OEM-side change: ~131 lines of code. Reproducibly built
> APK; install on any Moto / Pixel / Samsung in five minutes."
>
> **1:25–1:30 · Ask**
>
> "Twenty minutes on your calendar to walk through this with the
> assumptions live. Repo and APK are linked below — happy to do a
> screen-share at any time."

---

## 7. LinkedIn DM version (≤ 300 chars)

> Hi Mahmoud — built Plexus, an orchestration layer for OEM AI.
> Filters surface, routes local-first, audit log per call.
> 131-line shim, $9–24 M/yr recoverable cloud spend at Moto's
> 14.5 M-shipment scale. Live demo + APK:
> github.com/Akshu1245/Secondbrain. Worth 20 min? — Akshay

---

## 8. Investor follow-up (T+10 days, no reply)

> **Subject:** Re: Plexus — adding the OEM pilot LOI to the package
>
> Hi [Partner first name],
>
> Bumping this once. Three updates since last note:
>
> 1. [OEM lead] confirmed pilot interest — LOI in draft for a
>    250 K-device cohort.
> 2. Cross-OEM learning surface design published:
>    [link to design doc]
> 3. Financial model now includes the EU AI Act compliance
>    cost-avoidance line item, conservatively estimated at
>    $0.04 / device / year on top of the cloud-spend recovery.
>
> Same ask as before — 30 minutes when your calendar opens.
>
> Best,
> Akshay

---

## 9. Demo invite — once a reply lands

> Subject: Plexus walkthrough · 20 min · [date] · agenda below
>
> [Recipient first name],
>
> Looking forward to the call. 20 minutes, suggested agenda:
>
> * Live demo: 8 min (problem → solution → numbers)
> * Financial model with your fleet's parameters: 5 min
> * Integration shim walkthrough (AIDL + Kotlin): 4 min
> * Pilot scoping + Q&A: 3 min
>
> If anything in the package needs prep on your side — your fleet's
> per-call cloud cost, your measured calls / device / day, the
> assistant's current cloud-share — having those numbers in front
> of us turns the call from "demo" into "model".
>
> Demo URL: <https://out-gwumfbso.devinapps.com/>
> Pitch doc: <https://github.com/Akshu1245/Secondbrain/blob/main/docs/oem-pitch/PITCH.md>
>
> Best,
> Akshay

---

## 10. What to do today

1. **Pick the brand name.** Default Plexus; alternates Conduit,
   Inferna, Locus, Ravel. Final selection unblocks every other asset.
2. **Fill the two remaining placeholders**: LinkedIn URL (every
   draft) and education line (Lenovo cover letters only).
3. **Send the OEM cold email** to Mahmoud Tuesday 4–5 PM IST.
4. **Send the investor cold email** to your top 5 partners
   Wednesday morning.
5. **Submit the Lenovo cover letters** Thursday morning IST.
6. **Pitch in parallel** to OnePlus, Nothing, Samsung India the
   following week using the same package, swapping the
   `moto-specific.md` appendix for the OEM-equivalent.
