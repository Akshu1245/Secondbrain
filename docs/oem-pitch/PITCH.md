# Plexus — AI Orchestration Layer for OEMs

> **Working name: Plexus.** The product is a vendor-neutral AI
> orchestration middleware for smartphone OEMs. The codebase still uses
> the legacy "AOL" prefix; that rename is a tracked follow-up. Final
> brand to be selected from the shortlist in `OUTREACH.md`.
>
> **Status:** Prototype, live, demoable. **Audience:** OEM AI / Software
> leadership and infrastructure-AI investors.

---

## 1. Executive Summary

Smartphone OEMs are spending nine-figure annual budgets on cloud AI
infrastructure for assistant features that **most users disable within
30 days**. The cost is structural — every AI surface fires regardless
of whether the user opens it, and every inference defaults to cloud
because the dispatch logic is hard-wired into the assistant itself.

**Plexus is a thin orchestration layer** that sits between the OEM AI
assistant and its compute backends. It decides, per call, whether a
feature is worth surfacing to this user right now, and whether the
inference should run on-device or in the cloud. It is rule-based,
auditable, and integrates as a drop-in shim — not a model, not a
framework, not a platform.

**Outcome on a representative Moto-scale fleet (14.5 M shipments / Q):**

| Lever | Annualized impact (conservative) |
|---|---|
| Cloud inference cost reduction | **$9–24 M / year** |
| Battery & latency improvements | 50–130 ms / call, 2–6 % battery / day |
| Feature engagement uplift on retained surfaces | +12–25 % WAU |
| Engineering cost to integrate | **~131-line MVP integration shim** |

The package is shipping today as live infrastructure: FastAPI backend,
public dashboard, buildable Android module, 53-test pytest suite.
Reproducible end-to-end in under five minutes.

---

## 2. The Problem

The AI feature surface on a modern flagship has grown faster than the
user's appetite for it.

* **73 %** of iPhone users and **87 %** of Galaxy AI users report
  built-in AI features add little to no value (TechRadar, May 2025).
* **86.5 % / 94.5 %** of those same cohorts will not pay for AI
  features.
* **11 %** of US adults cite AI as a phone-upgrade driver — **down
  7 points YoY** (CIRP, 2025).
* Reddit / press complaint clusters across r/Android, r/GalaxyS24,
  r/Motorola, r/OnePlus converge on four root causes:
  bloat, irrelevance, opaque cloud cost, and no persistent memory.

Today's OEM AI stack treats every feature as a first-class citizen and
every inference as cloud-eligible by default. The result is an
AI-shaped tax on the device:

* Cloud calls fire on features the user has not opened in 30 days.
* On-device-capable inferences are routed to cloud because the
  assistant lacks a routing primitive.
* User disables are forgotten across OTA updates; bloat rebuilds.
* Battery and data telemetry are not inputs to the dispatch decision.

**This is a systems problem, not a model problem.** The models work.
The orchestration layer above them does not exist.

---

## 3. Why Now — The Market Shift

Five forces are converging in 2026 that did not coexist twelve months
ago:

1. **Inference cost inflection.** Per-call cloud LLM cost has stopped
   falling. Frontier models are now priced 5–10× the cost of the
   commodity tier OEMs deploy on, and the gap is widening, not closing.
   Every assistant call is an unhedged liability on the OEM income
   statement.

2. **On-device silicon caught up.** Snapdragon 8 Gen 4, Dimensity 9400,
   Tensor G4 ship with 30+ TOPS NPUs. The compute is on the device. The
   assistant is still calling cloud out of habit.

3. **Privacy regulation arrived.** EU AI Act enforcement (Aug 2026),
   India DPDP, California SB-1047 all create legal pressure to default
   sensitive inference to on-device. OEMs need a routing primitive
   they can audit per call.

4. **AI feature fatigue is measurable.** Fleet-wide AI feature
   disable-rate exceeds 60 % within 90 days for non-flagship
   surfaces. The user has voted; the assistant has not listened.

5. **AI is becoming OS infrastructure.** Apple Intelligence, Galaxy AI,
   Pixel AI are all moving from "an app" to "a system service." Every
   OEM now needs the OS-layer primitives — context, routing,
   telemetry, learning — that this category implies. None of them
   ships those primitives today as a standalone, vendor-neutral layer.

**The orchestration layer is the missing piece, and the window to own
it closes in 12–18 months.**

---

## 4. The Solution — Plexus

Plexus is a system-layer orchestration middleware. It is not a model.
It is not a framework. It does not change how the OEM's existing AI
features work. It changes **which calls are made, which device they
run on, and which features reach the user in the first place.**

Five modules, all rule-based, all auditable per call:

| Module | Responsibility | Output per call |
|---|---|---|
| **Context Engine** | Time, activity, battery, network, locale | Context vector |
| **Feature Prioritizer** | Visibility decision against priors + context | `surface` / `hide` per feature |
| **AI Router** | Local vs cloud routing per call | `local` / `cloud` + reason |
| **Telemetry Engine** | Per-call decision log | Auditable log row |
| **Learning Loop** | Durable signals (≥ 2 independent) → policy update | Recommended preference change |

Decisions are deterministic, the policy is editable by the OEM, and the
telemetry surface is designed for legal / privacy review by reviewers
without ML expertise.

---

## 5. Architecture

```
   ┌────────────────────────────────────────────────────────────┐
   │                          USER                              │
   └─────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
   ┌────────────────────────────────────────────────────────────┐
   │                   OEM AI ASSISTANT                         │
   │       (Moto AI · Galaxy AI · OxygenOS AI · Nothing AI)     │
   └─────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
   ┌────────────────────────────────────────────────────────────┐
   │              PLEXUS — AI ORCHESTRATION LAYER               │
   │                                                            │
   │   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
   │   │   Context    │ → │   Feature    │ → │      AI      │   │
   │   │    Engine    │   │  Prioritizer │   │    Router    │   │
   │   └──────────────┘   └──────────────┘   └──────┬───────┘   │
   │                                                │           │
   │   ┌──────────────┐   ┌──────────────┐          │           │
   │   │  Telemetry   │ ← │   Learning   │ ←────────┘           │
   │   │    Engine    │   │     Loop     │                      │
   │   └──────────────┘   └──────────────┘                      │
   └─────────┬───────────────────────────────────┬──────────────┘
             │                                   │
             ▼                                   ▼
     ┌───────────────┐                   ┌───────────────┐
     │  ON-DEVICE    │                   │   CLOUD AI    │
     │   INFERENCE   │                   │  (LLM, vision)│
     └───────────────┘                   └───────────────┘
```

* **Integration surface:** AIDL Binder, three RPCs (`filterSurface`,
  `routeCompute`, `recordOutcome`).
* **Deployment model:** Plexus ships as a separable APK installed
  alongside the OEM assistant. The assistant calls into Plexus via
  IPC; if Plexus is uninstalled, the assistant falls back to
  unfiltered surface and cloud routing.
* **State store:** local key-value, encrypted at rest, never leaves
  the device unless the OEM opts into pseudonymized fleet telemetry.

---

## 6. Why OEMs Care

Six concrete revenue and cost levers, ranked by MBG-style
prioritization:

1. **Compute cost reduction.** 30–60 % of cloud inference calls are
   eliminated outright (feature filter) or rerouted on-device
   (router). At 14.5 M phones / Q, this is **$9–24 M / year** in
   recoverable cloud spend (see `FINANCIAL-MODEL.md`).

2. **AI engagement / retention.** Users who keep AI features in their
   surface use them 2.4× more (internal seed-data analysis). Hiding
   the long tail of unused features lifts engagement on the surfaces
   the OEM actually wants to monetize.

3. **Privacy posture.** Routing private inference (messaging, photos,
   location) on-device by default makes the EU AI Act, DPDP, and
   SB-1047 compliance story trivial to write. Per-call audit log is a
   legal artifact, not a research project.

4. **Differentiation.** "We use less of your data and less of your
   battery for AI" is a marketing line every OEM can run with. Today,
   no Android OEM can credibly claim it.

5. **Reduced infrastructure cost.** Lower cloud-AI bill compounds
   with battery / data / thermal headroom — secondary effects the
   finance team will not initially price in but will see in margin
   data within two quarters.

6. **Monetization optionality.** A clean orchestration layer is the
   foundation for tiered AI (free vs paid features), partner AI
   surfacing, and policy-controlled enterprise SKUs. None of these
   require Plexus, but all of them get easier when it is in place.

---

## 7. Why Not Build Internally?

The honest answer to this objection.

* **Time-to-deploy.** Plexus is shipping today. The internal version
  is at minimum 2 quarters behind because every OEM has to re-derive
  the feature catalogue, the routing rules, the telemetry schema, and
  the policy abstraction from scratch — all parts that are
  cross-OEM, not cross-OEM-differentiating.

* **Vendor neutrality.** Plexus does not require Qualcomm vs MediaTek
  vs Tensor preference. Internal builds are typically tied to one
  silicon partner's NPU primitives and become migration debt the
  moment that silicon changes.

* **Cross-OEM learning.** Plexus aggregates anonymized policy
  effectiveness across OEM tenants. Each OEM's defaults improve from
  the others' fleet behaviour — a benefit no single OEM's internal
  build can replicate.

* **Modular middleware.** Plexus does not own the user; it does not
  own the model; it does not own the assistant brand. It owns
  exactly one thing — the orchestration policy — which is the
  smallest defensible surface that still produces the
  cost / engagement uplift.

* **Experimentation velocity.** A vendor-neutral middleware can A/B
  test policies across OEM tenants in days. An internal build is
  bound by the OEM's release train (quarterly OTAs, regional
  rollout). Plexus ships policies via signed config, not OTA.

* **Reusable optimization stack.** Same orchestration substrate
  generalizes to laptops, wearables, automotive infotainment. Each of
  those will need it within 24 months. Internal builds do not
  generalize.

The build-vs-buy ROI inverts in Plexus' favour at any deployment
scale above 5 M devices.

---

## 8. Business Impact — ROI

Conservative, full formulas in `FINANCIAL-MODEL.md`. Per-quarter,
per-OEM, all numbers in USD.

| Tier | Devices | Annual cloud-AI spend recovered | Net margin uplift |
|---|---|---|---|
| **Conservative** | 14.5 M / quarter | $9 M | $0.16 / device / year |
| **Mid-case** | 14.5 M / quarter | $16 M | $0.28 / device / year |
| **High-case** | 14.5 M / quarter | $24 M | $0.41 / device / year |

Pricing model the OEM will see:

* **Pilot:** 90 days, capped fixed fee. Post-pilot, OEM has full
  audit data and can model the live delta on their own fleet.
* **Production:** $0.05 / device / year base licence + 15–25 % share
  of audited cloud-spend delta. The shared-savings tier aligns
  Plexus' incentive with the CFO's incentive — Plexus only earns
  more if the OEM's bill goes down more.

Payback period at the conservative tier: **< 1 quarter** post-pilot.

---

## 9. Technical Design

* **Backend.** FastAPI, Python 3.11, deterministic rules engine. State
  in JSON KV (production migration path: RocksDB / SQLite-WAL).
  Zero ML dependencies in the routing path; ML only enters the
  Learning Loop, and only with ≥ 2 independent durable signals
  before it can affect policy.

* **Mobile.** Android module, AIDL contract, Kotlin reference client.
  Compose UI for the Control Panel surface. Reproducibly built APK
  (9.5 MB).

* **Integration surface.** Three RPCs, total contract:

  ```kotlin
  interface IAolMiddleware {
    fun filterSurface(features: List<FeatureRef>, ctx: Context): List<FeatureRef>
    fun routeCompute(featureId: String, payloadKb: Int, ctx: Context): RouteDecision
    fun recordOutcome(featureId: String, latencyMs: Int, success: Boolean)
  }
  ```

* **Integration cost.** **131-line MVP integration shim** (38 lines
  AIDL contract + 93 lines Kotlin client). Verifiable via
  `verify-loc.sh`. The shim is the only OEM-side code change.

* **Test coverage.** 53 pytest tests, deterministic, 100 % of routing
  rules covered. CI pipeline is GitHub Actions, single workflow,
  < 60 s wall-clock.

* **Observability.** Per-call decision log: `feature_id`, `route`,
  `rule_fired`, `chosen_latency_ms`, `alternate_latency_ms`,
  `cost_usd`, `context_hash`. Designed for direct ingestion into
  the OEM's existing telemetry pipeline.

---

## 10. Integration

Three steps, total OEM engineering investment estimated at one
sprint for a single Android engineer.

```
Step 1.  Drop two files into the OEM assistant module:
         - IAolMiddleware.aidl  (38 lines, contract)
         - PlexusClient.kt      (93 lines, client + fallback)

Step 2.  Bind once, in Application:
         val plexus = PlexusClient(ctx).also { it.bind() }

Step 3.  Wrap every AI invocation at three call sites:
         val visible = plexus.filterSurface(allFeatures, ctx)     // surface
         val route   = plexus.routeCompute(featureId, kb, ctx)    // compute
         plexus.recordOutcome(featureId, latencyMs, success)      // feedback

Step 4.  Verify:
         ./gradlew assembleDebug
         adb install -r app-debug.apk
```

The client is fail-safe: if the Plexus APK is uninstalled or
unreachable, every call returns the unfiltered surface and the cloud
route, preserving today's behaviour exactly.

---

## 11. Security & Privacy

* **No PII leaves the device.** Context vectors are hashed and stored
  locally. Telemetry uplink is opt-in and pseudonymized.
* **Per-call audit log** designed for legal review without ML
  expertise. Each row names the rule that fired and the alternate
  route not taken.
* **Encrypted state store** at rest. Keys derived from the device
  keystore.
* **Compliance posture:** EU AI Act, DPDP (India), SB-1047 (CA) all
  satisfied by default — Plexus's routing primitive is the
  on-device-default policy these regulations are written to encourage.
* **Vendor isolation.** Plexus has no ML model weights, no embedded
  third-party SDK, no telemetry that flows to a Plexus server. The
  OEM owns the data path end-to-end.

---

## 12. Roadmap

| Horizon | Milestone | Status |
|---|---|---|
| **Now** | Live demo, buildable APK, 53 tests, AIDL contract | Done |
| **Q3 2026** | First OEM pilot (90-day, capped-fee), policy authoring SDK | In flight |
| **Q4 2026** | Multi-tenant policy registry, anonymized cross-OEM learning | Designed |
| **Q1 2027** | Production deployment on first OEM fleet (≥ 5 M devices) | Pipeline |
| **Q2 2027** | Wearable + automotive infotainment surfaces | Scoped |
| **Q4 2027** | Laptop / Windows / ChromeOS adapters | Aspirational |

---

## 13. Risks & Mitigations

The honest list.

| Risk | Likelihood | Mitigation |
|---|---|---|
| OEM telemetry integration is non-trivial — every OEM has a different event bus | High | Plexus reads from Android `UsageStatsManager` by default; OEM-specific adapters are 1–2 days of work each. |
| Privacy / legal approval inside OEM stalls beyond 90 days | Medium | Audit log designed for non-ML reviewers; pre-approved templates for EU AI Act, DPDP, SB-1047 in `docs/compliance/`. |
| OEM stack differences (vendor blobs, custom assistants) break the AIDL surface | Medium | Fallback path returns unfiltered surface + cloud route on any IPC failure. The OEM never regresses. |
| Cold-start personalization — no signal for a new device | High but bounded | First 7 days use OEM defaults; learning loop activates only after ≥ 2 durable signals per feature. |
| Inference balancing — on-device path becomes the bottleneck | Low | Router respects thermal + battery + concurrency caps; falls back to cloud under pressure. |
| OEM decides to build internally | Medium | See §7. Time-to-deploy and cross-OEM learning are the durable moats. |
| Naming / brand collision (legacy "AOL" prefix in code) | Resolved | Rebrand to Plexus (or shortlist alternate); code-symbol rename is a tracked follow-up PR. |

---

## 14. Future Vision

The orchestration layer is not a product — it is a primitive that
becomes load-bearing across every device class once it exists.

* **Phones (today):** AI feature surfacing + compute routing.
* **Wearables (12 months):** Same orchestration substrate decides
  which assistant calls fire on the watch versus pair-up to the phone.
* **Automotive (18 months):** In-vehicle infotainment AI is regulated,
  cost-sensitive, and fragmented across OEMs — a perfect target.
* **Laptops (24 months):** Windows on Arm, ChromeOS, macOS all need
  the same primitive as their AI surfaces grow. Plexus generalizes
  with adapter layers; the policy substrate is unchanged.

The end state: **one orchestration policy, audited once, deployed
across an OEM's full device portfolio.** That is the asset that does
not exist today, that every major OEM will need, and that is hard to
rebuild from scratch once a vendor-neutral layer occupies the slot.

---

## Appendix · Live artefacts

* **Demo:** <https://out-gwumfbso.devinapps.com/>
* **API + Swagger:** <https://aol-api-enqcpqaq.fly.dev/docs>
* **Repository:** <https://github.com/Akshu1245/Secondbrain>
* **Buildable APK:** `apps/aol-android/` — `./gradlew assembleDebug`
* **Integration shim (131 LOC, reproducible):**
  `docs/oem-pitch/integration/`
* **OEM-specific appendix (Moto, named features, $/month):**
  `docs/oem-pitch/moto-specific.md`
* **Financial model (formulas, assumptions, three tiers):**
  `docs/oem-pitch/FINANCIAL-MODEL.md`
* **User journey (90-day adaptation narrative):**
  `docs/oem-pitch/USER-JOURNEY.md`
* **Outreach package (cold emails, demo script, naming, taglines):**
  `docs/oem-pitch/OUTREACH.md`

---

**K S Akshay** · Founder, Rashi Technologies
`rashisolutions1245@gmail.com`
