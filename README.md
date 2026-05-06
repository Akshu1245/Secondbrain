# Plexus — AI Orchestration Layer for OEMs

> **Repo note.** The repository is named `Secondbrain` for legacy
> reasons. The headline product being pitched is **Plexus** — a
> vendor-neutral AI orchestration middleware for smartphone OEMs.
> "AOL" and "Second Brain" appear inside the codebase as legacy
> module names; the brand-level rename is a tracked follow-up. The
> live demo, the AIDL integration shim, the financial model, and
> all outbound assets are written under the Plexus name.

---

## What this is

A vendor-neutral AI orchestration middleware that sits between an OEM
AI assistant (Moto AI · Galaxy AI · OxygenOS AI · Nothing AI · …) and
its compute backends. It decides — per call — which features reach
the user and whether inference runs on-device or in the cloud.

**Outcome on a 14.5 M-shipment quarterly fleet:** $9–24 M / year of
recoverable cloud inference spend, via a **131-line MVP integration
shim**.

---

## Where to read

| Document | Purpose |
|---|---|
| [`docs/oem-pitch/PITCH.md`](docs/oem-pitch/PITCH.md) | Master enterprise pitch — 13 sections, executive-ready. |
| [`docs/oem-pitch/one-pager.md`](docs/oem-pitch/one-pager.md) | One-page summary for inbox-attention scanners. |
| [`docs/oem-pitch/FINANCIAL-MODEL.md`](docs/oem-pitch/FINANCIAL-MODEL.md) | Formula-driven, three-tier ROI model with full assumption log. |
| [`docs/oem-pitch/USER-JOURNEY.md`](docs/oem-pitch/USER-JOURNEY.md) | 90-day adaptation narrative — how Plexus learns one user's behaviour and reduces cloud dependency. |
| [`docs/oem-pitch/OUTREACH.md`](docs/oem-pitch/OUTREACH.md) | Cold emails (OEM + investor), demo narration, taglines, naming shortlist, follow-up sequence. |
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
                             │  PLEXUS                        │
                             │   ├── Context Engine           │
                             │   ├── Feature Prioritizer      │
                             │   ├── AI Router                │
                             │   ├── Telemetry Engine         │
                             │   └── Learning Loop            │
                             └─────────┬───────────┬──────────┘
                                       │           │
                                  ON-DEVICE     CLOUD AI
```

Five rule-based modules, deterministic, per-call decision log,
fail-safe fallback if the Plexus APK is uninstalled.

---

## Repository layout

```
apps/
  aol/api/         — FastAPI backend (orchestration policy + decision log)
  aol/web/         — Next.js dashboard (live demo)
  aol-android/     — Android module (AIDL contract + Compose UI + buildable APK)
  api/             — Second Brain memory companion (legacy)

docs/
  oem-pitch/       — Master pitch package, financial model, outreach
  oem-pitch/integration/  — 131-line shim, drop-in for the OEM assistant
```

---

## Status

* Prototype, live, demoable end-to-end in under five minutes.
* First OEM pilot conversations in flight (Motorola MBG primary,
  OnePlus / Nothing / Samsung India in pipeline).
* Pre-seed raise opening to convert pilot → production.

---

— **K S Akshay** · Founder, Rashi Technologies · `rashisolutions1245@gmail.com`
