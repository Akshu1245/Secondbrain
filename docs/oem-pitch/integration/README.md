# Integrating AOL into an OEM AI assistant

This directory contains the minimum the OEM integration team needs to bolt
AOL onto their existing AI assistant launcher in a single sprint.

## Contents

| File | What it is |
|---|---|
| [`IAolMiddleware.aidl`](./IAolMiddleware.aidl) | The Binder interface the AOL Foreground Service exposes. Three RPCs — filter / route / record. |
| [`AolClient.kt`](./AolClient.kt) | Drop-in Kotlin client showing how to bind to the service, call each RPC, and gracefully fall back if AOL is uninstalled. End-to-end usage example included at the bottom. |

## Architecture

```
 ┌───────────────────────────────────────────────────────────────────────┐
 │                       OEM AI Assistant                                │
 │  (Moto AI / Galaxy AI / OxygenOS AI / Nothing AI / Bixby ...)         │
 │                                                                       │
 │   ┌──────────────────┐    1. before render → filterSurface()          │
 │   │  Home strip      │ ─────────────────────────┐                     │
 │   │  (the "AI tab")  │                          ▼                     │
 │   └────────┬─────────┘                   ┌──────────────┐             │
 │            │ 2. tap feature              │  AolClient   │             │
 │            ▼ → routeCompute()            │  (Kotlin)    │             │
 │   ┌──────────────────┐                   └──────┬───────┘             │
 │   │  Cloud backend   │                          │ Binder              │
 │   │ (Gemini / Perplx)│                          │ IPC                 │
 │   └──────────────────┘                          │                     │
 │                                                 ▼                     │
 └─────────────────────────────────────────────────┼─────────────────────┘
                                                   │
 ┌─────────────────────────────────────────────────▼─────────────────────┐
 │                  AolMiddlewareService (this APK)                      │
 │   ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐  │
 │   │ Usage Tracker   │  │ Smart Filter     │  │ Compute Optimizer  │  │
 │   └─────────────────┘  └──────────────────┘  └────────────────────┘  │
 │   ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐  │
 │   │ Context Engine  │  │ Control Panel    │  │ Feedback Loop      │  │
 │   └─────────────────┘  └──────────────────┘  └────────────────────┘  │
 └───────────────────────────────────────────────────────────────────────┘
```

## Integration steps

1. Drop `IAolMiddleware.aidl` into the OEM assistant module's `aidl/` source set.
2. Drop `AolClient.kt` into the same module's `kotlin/` source set.
3. Add 3 call sites:
   * Before rendering the AI feature strip → `AolClient.filterSurface(...)`
   * Right before dispatching a feature → `AolClient.routeCompute(...)`
   * After the feature finishes → `AolClient.recordOutcome(...)`
4. (Optional) Surface the AOL Control Panel from a deep link in the OEM AI
   assistant Settings page.

That's the full integration. Total diff size on a typical OEM AI launcher is
**131 LOC** (`AolClient.kt` 125 + `IAolMiddleware.aidl` 6, semantic lines of
code, block comments and the end-of-file usage example excluded). Reproduce
with [`./verify-loc.sh`](./verify-loc.sh) — the script fails the moment
integration LOC stops being strictly under 150, so the pitch claim stays
honest.

## Failure modes

* AOL not installed / service crashed → `AolClient` returns the original
  unfiltered list and a `cloud` route. The OEM assistant keeps working
  exactly as it does today.
* AOL APK upgraded mid-session → Binder reconnects automatically.
* AOL background work paused (Doze / battery saver) → the three RPCs are
  cheap rule-based reads; they work in any state the service is alive.

## Where the rules live

The reference rule set is implemented in `apps/aol/api/app/` (Python prototype).
For shipping, the same rules are reimplemented in Kotlin inside the
`AolMiddlewareService` (not included in this stub — it's a 2-week port from
the Python reference). The rules are intentionally simple to make them
auditable by the OEM legal/security teams without ML review.
