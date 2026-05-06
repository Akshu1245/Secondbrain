# Plexus — AI Orchestration Layer for OEMs

**One page. Read in 90 seconds.**

---

## Executive summary

Plexus is a vendor-neutral AI orchestration middleware for smartphone
OEMs. It sits between the OEM AI assistant and its compute backends
and decides — per call — which features reach the user and whether
inference runs on-device or in the cloud. **Outcome: $9–24 M / year
of recoverable cloud spend on a 14.5 M-shipment quarterly fleet, via
a 131-line MVP integration shim.**

---

## Problem

* 73 % of iPhone users + 87 % of Galaxy AI users say built-in AI
  features add little to no value (TechRadar, May 2025).
* 60 %+ of AI features are disabled within 30 days of activation.
* Every retained call is cloud-routed by default — the assistant has
  no orchestration primitive above the model layer.
* On-device silicon is 30+ TOPS-capable on flagship 2026 devices and
  effectively idle.

The model layer works. The orchestration layer above it does not
exist.

---

## Solution

Five rule-based modules, each with a single responsibility, all
auditable per call:

```
       USER → OEM ASSISTANT → ┌─────────────────────────────┐
                              │  PLEXUS                     │
                              │   ├── Context Engine        │
                              │   ├── Feature Prioritizer   │
                              │   ├── AI Router             │
                              │   ├── Telemetry Engine      │
                              │   └── Learning Loop         │
                              └────────┬───────────┬────────┘
                                       │           │
                                  ON-DEVICE     CLOUD AI
```

* **Integration:** AIDL contract (38 LOC) + Kotlin client (93 LOC) =
  131-line MVP integration shim. Drop in, bind once, wrap every AI
  call. Fail-safe fallback if Plexus is uninstalled.
* **Deployment:** Plexus ships as a separable APK. No model
  dependencies, no SDK, no third-party telemetry.
* **Compliance:** Per-call audit log designed for EU AI Act, DPDP,
  SB-1047 review without ML expertise.

---

## Business impact (conservative tier)

| Metric | Value |
|---|---|
| Devices in fleet | 14.5 M / quarter |
| AI calls / device / day | 6 (conservative) |
| Cloud-share before / after | 75 % → 45 % |
| Cloud calls eliminated / yr | 12.39 B |
| Annual cost recovery (low / mid / high) | **$9.9 M / $24.8 M / $62.0 M** |
| OEM integration cost | ~131 LOC, one sprint |
| Plexus pricing | $0.05 / device / yr base + 15–25 % shared savings |
| Payback period | < 1 quarter post-pilot |

Full formulas in `FINANCIAL-MODEL.md`. Live measurements at
<https://out-gwumfbso.devinapps.com/>.

---

## Why now

* Inference cost has stopped falling — every assistant call is an
  unhedged cost line.
* On-device silicon is ready; the assistant's dispatch logic is not.
* EU AI Act, DPDP, SB-1047 enforcement creates legal pressure for
  on-device-default routing with per-call audit.
* AI feature fatigue is measurable (60 %+ 30-day disable rate).
* AI is moving from "an app" to OS infrastructure across every
  flagship — the orchestration primitive becomes load-bearing.

---

## Why OEMs care

Cloud cost reduction · AI engagement & retention · privacy posture ·
regulatory compliance · differentiation · monetization optionality.
Detailed in `PITCH.md` § 6.

## Why not build internally?

Time-to-deploy · vendor neutrality · cross-OEM learning · modular
middleware · experimentation velocity · reusable substrate across
phones / wearables / automotive / laptops. Detailed in `PITCH.md` § 7.

---

## Status

* Live demo, public dashboard, FastAPI backend, buildable Android
  module, 53 deterministic tests.
* First OEM pilot conversations in flight (Motorola MBG primary).
* Pre-seed raise opening to convert pilot → production.

---

## Ask

20 minutes for an OEM walkthrough · 30 minutes for an investor call.
Demo, financial model, integration shim — all available in advance.

— **K S Akshay** · Founder, Rashi Technologies · `rashisolutions1245@gmail.com`
