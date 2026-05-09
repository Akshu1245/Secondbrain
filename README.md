# Second Brain — the memory + routing layer for OEM AI

> **Repo note.** The repository is named `Secondbrain` because that
> *is* the product. Inside the codebase you will see legacy module
> names (`aol/`, references to "AOL", an earlier "Plexus" working
> name) — those are subsystems and historical positioning attempts.
> The headline product, the brand on every outbound asset, and the
> name on the cold email is **Second Brain**.

---

## What this is

Second Brain is a memory + routing layer that plugs into an OEM AI
assistant (Moto AI · Galaxy AI · OxygenOS AI · Nothing AI · …) and
gives it two things that current first-party AI assistants ship
half-built:

1. **Persistent memory.** Catch-Me-Up, Pay-Attention, and Remember-
   This are the right product surface, but the persistence layer
   underneath is missing — sessions don't carry, signals don't
   reinforce. Second Brain is that persistence layer.
2. **Per-call routing.** A rule-based system layer (codename "AOL"
   in the codebase) decides per inference whether the call runs
   on-device or in the cloud, with full audit trail.

**Outcome on a 14.5 M-shipment quarterly fleet:** $9–24 M / year
of recoverable cloud inference spend, via a **131-line MVP
integration shim**.

---

## Where to read

| Document | Purpose |
|---|---|
| [`docs/oem-pitch/PITCH.md`](docs/oem-pitch/PITCH.md) | Master enterprise pitch — 13 sections, executive-ready. |
| [`docs/oem-pitch/one-pager.md`](docs/oem-pitch/one-pager.md) | One-page summary for inbox-attention scanners. |
| [`docs/oem-pitch/FINANCIAL-MODEL.md`](docs/oem-pitch/FINANCIAL-MODEL.md) | Formula-driven, three-tier ROI model with full assumption log. |
| [`docs/oem-pitch/USER-JOURNEY.md`](docs/oem-pitch/USER-JOURNEY.md) | 90-day adaptation narrative — how Second Brain learns one user's behaviour and reduces cloud dependency. |
| [`docs/oem-pitch/OUTREACH.md`](docs/oem-pitch/OUTREACH.md) | Cold emails (OEM + investor), demo narration, taglines, follow-up sequence. |
| [`docs/oem-pitch/moto-specific.md`](docs/oem-pitch/moto-specific.md) | Per-OEM appendix — named Moto AI features, $/month at Lenovo-Motorola Q2 2025 scale. |
| [`docs/oem-pitch/integration/`](docs/oem-pitch/integration/) | The 131-line integration shim — AIDL contract + Kotlin client + reproducibility script. |

---

## Live artefacts

* **Demo:** <https://out-gwumfbso.devinapps.com/>
* **API + Swagger:** <https://aol-api-enqcpqaq.fly.dev/docs>
* **Buildable APK:** `apps/aol-android/` → `./gradlew assembleDebug`

---

## Architecture

```
   USER → OEM AI ASSISTANT → ┌────────────────────────────────┐
                             │  SECOND BRAIN                  │
                             │   ├── Memory Layer             │
                             │   ├── Context Engine           │
                             │   ├── Feature Prioritizer      │
                             │   ├── AI Router (codename AOL) │
                             │   ├── Telemetry Engine         │
                             │   └── Learning Loop            │
                             └─────────┬───────────┬──────────┘
                                       │           │
                                  ON-DEVICE     CLOUD AI
```

Six rule-based modules, deterministic, per-call decision log,
fail-safe fallback if the Second Brain APK is uninstalled.

---

## Repository layout

```
apps/
  aol/api/         — FastAPI backend (memory + routing policy + decision log)
  aol/web/         — Next.js dashboard (live demo)
  aol-android/     — Android module (AIDL contract + Compose UI + buildable APK)
  api/             — Second Brain memory companion (earlier prototype)

docs/
  oem-pitch/       — Master pitch package, financial model, outreach
  oem-pitch/integration/  — 131-line shim, drop-in for the OEM assistant
```

The `aol/` directory prefix is internal naming for the routing
subsystem and is preserved to keep the live demo + APK builds
working unchanged. Brand-level code rename is a tracked follow-up.

---

## Status

* Prototype, live, demoable end-to-end in under five minutes.
* First OEM pilot conversations in flight (Motorola MBG primary,
  OnePlus / Nothing / Samsung India in pipeline).
* Pre-seed raise opening to convert pilot → production.

---

— **K S Akshay** · Founder, Rashi Technologies · `rashisolutions1245@gmail.com`
