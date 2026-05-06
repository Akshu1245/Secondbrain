# AOL Demo — Android

A buildable Android app that exercises the **AI Optimisation Layer** middleware
end-to-end on-device:

- The OEM AI assistant (here: this APK) **binds via AIDL** to the AOL middleware
  service (also in this APK for the demo; in production a separate `ai.aol`
  APK).
- The launcher screen calls `filterSurface()` to decide which Moto AI features
  to show, calls `routeCompute()` to pick local-vs-cloud per feature, and calls
  `recordOutcome()` to feed the nightly improvement loop.
- The same six AOL modules — Usage Tracker, Smart Filter, Context Engine,
  Compute Optimiser, Control Panel, Feedback Loop — that the dashboard demo at
  https://out-ujjsjvxm.devinapps.com renders, but running directly on the
  device.

The thresholds and per-feature latency / cost numbers mirror the Python
reference implementation under `apps/aol/api/` — so a Moto AI call here lands
local at the same ~45 % rate as the dashboard advertises in
`docs/oem-pitch/moto-specific.md`.

## Build

```bash
cd apps/aol-android
echo "sdk.dir=$ANDROID_HOME" > local.properties     # if not already set
./gradlew assembleDebug
```

The resulting APK lands at `app/build/outputs/apk/debug/app-debug.apk` (~9 MB).

Verified building on:

- JDK 17 (Temurin / OpenJDK both fine)
- Android SDK 34 + build-tools 34.0.0 + platform-tools
- Gradle 8.7 (downloaded by the wrapper, no host install required)
- Android Gradle Plugin 8.5.2 + Kotlin 1.9.24 + Jetpack Compose BOM 2024.06.00

## Run

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n ai.aol.demo/.MainActivity
```

The launcher screen offers:

- **Context controls** — flip battery, data-saver, private mode and watch the
  surface change.
- **Surface card** — visible vs auto-hidden Moto AI features (Module 2 + 3).
- **Route buttons** — tap a feature with 64 kb or 512 kb payload and see local
  / cloud, latency and \$ saved (Module 4).
- **Decision log** — last 20 routing decisions with the human-readable reason
  string (Module 6).

## Architecture

```
┌─────────────────────────────┐         AIDL          ┌────────────────────┐
│  MainActivity (Compose)     │ ◀──── IAolMiddleware ──▶│ AolMiddlewareSvc │
│  AolViewModel               │                        │  (in-process for │
│  AolClient                  │                        │   the demo)      │
└─────────────────────────────┘                        └────────────────────┘
       ▲                                                      │
       │ in production these halves live in two APKs:         │
       │   1. OEM AI assistant (Moto AI launcher)             │
       │   2. AOL middleware (`ai.aol`, ships separately)     │
       │ Bound across processes via the same AIDL surface.    │
       └──────────────────────────────────────────────────────┘
```

The AIDL surface (`app/src/main/aidl/ai/aol/IAolMiddleware.aidl`) is the
**only** integration contract between the OEM assistant and AOL. Three
methods, no chatty per-frame calls:

```
Bundle filterSurface(in List<String> featureIds, in Bundle context);
Bundle routeCompute(String featureId, in Bundle hints);
oneway void recordOutcome(in Bundle event);
```

`Bundle` (rather than `@Parcelable` data classes) is used so that fields can
be added forward-compatibly without recompiling the OEM AI assistant.

## File map

```
apps/aol-android/
├── settings.gradle.kts
├── build.gradle.kts                   # plugins (AGP 8.5.2, Kotlin 1.9.24)
├── gradle.properties
├── gradle/wrapper/                    # gradlew bootstrap
├── gradlew, gradlew.bat
└── app/
    ├── build.gradle.kts               # Compose + serialization + okhttp
    ├── proguard-rules.pro
    └── src/main/
        ├── AndroidManifest.xml        # registers MainActivity + AolMiddlewareService
        ├── aidl/ai/aol/
        │   └── IAolMiddleware.aidl    # AIDL contract (38 LOC, the entire integration surface)
        ├── kotlin/ai/aol/demo/
        │   ├── MainActivity.kt        # Compose UI
        │   ├── AolViewModel.kt        # state + business logic
        │   ├── AolClient.kt           # AIDL-bound client (the file an OEM assistant copies in)
        │   ├── AolMiddlewareService.kt# AIDL service implementation (the AOL APK side)
        │   └── FeatureCatalog.kt      # per-Moto-feature thresholds (mirrors apps/aol/api/)
        └── res/values/{strings,themes}.xml
```

## Drop-in for an OEM AI assistant

The two files an OEM AI assistant copies into its existing module:

1. `app/src/main/aidl/ai/aol/IAolMiddleware.aidl` (38 LOC)
2. `app/src/main/kotlin/ai/aol/demo/AolClient.kt` (≈ 100 LOC)

Both are unchanged from the reference under `docs/oem-pitch/integration/`,
just placed in their canonical Android source-set locations so the project
builds. Total: 131 semantic LOC, reproducibly verified by
`docs/oem-pitch/integration/verify-loc.sh`.

## Why this exists

The dashboard demo (https://out-ujjsjvxm.devinapps.com) shows the *server-side*
of AOL — the rules engine, the Control Panel, the metrics. This module shows
the *device-side*: a real Android app, real AIDL bind, real Kotlin client,
that an MBG software lead can build with `./gradlew` and read in 10 minutes.

For the Moto AI specifics — which features map to which AOL module, $/month
saved at Q2 2025 shipment volume, pilot ask — see
`docs/oem-pitch/moto-specific.md`.
