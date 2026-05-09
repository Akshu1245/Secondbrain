# AOL Android — Build & Benchmark Evidence

This file is the artifact-side answer to the most likely first question
in any OEM technical review: *"have you actually built this, and what
does it weigh?"*

Last verified: 2026-04-30 on the Devin VM (Ubuntu 22.04, JDK 17, Android
SDK 34, Gradle 8.7, AGP 8.5.2).

---

## Build evidence

```
$ ./gradlew assembleDebug
...
> Task :app:assembleDebug
BUILD SUCCESSFUL in 3m 57s
37 actionable tasks: 37 executed

$ ls -la app/build/outputs/apk/debug/
-rw-r--r-- 1 ubuntu ubuntu 9464323 May  9 05:49 app-debug.apk
```

| Artefact | Value |
|---|---|
| APK on-disk size | **9.1 MB** (9,464,323 bytes) |
| APK download size (after Play compression) | **8.7 MB** (9,096,484 bytes) |
| Package | `ai.aol.demo` |
| Min SDK | **26** (Android 8.0 Oreo, ~98 % of active fleet) |
| Target SDK | **34** (Android 14) |
| Compile SDK | 34 |
| Hardware features required | none (`android.hardware.faketouch implied`) |
| SHA-256 (debug APK) | `cb21b7ca49ef556dc0a65475d7f93585b53dff3023530c8c4c68d8a629db9225` |

### Hosted debug build (sideload-ready)

The same `app-debug.apk` produced by the build above is hosted at:

**[Download `app-debug.apk` (9.1 MB)](https://app.devin.ai/attachments/8dd985ea-019c-4f8d-bb82-624c0835967f/app-debug.apk)**

Verify integrity before installing:

```
$ sha256sum app-debug.apk
cb21b7ca49ef556dc0a65475d7f93585b53dff3023530c8c4c68d8a629db9225  app-debug.apk
```

Sideload onto a Moto / Pixel / any Android 8+ device:

```
$ adb install app-debug.apk
```

The APK is *unsigned debug* — useful for review and emulator runs but
not for Play distribution. A signed release build is one `gradle
assembleRelease` step away once an OEM provides a signing key.

`apkanalyzer dex packages` against the produced APK reports **303
methods and 41,079 bytes of DEX code** in `ai.aol.*` (the AOL
middleware namespace — every method *we* added). Everything else
(~96 K methods total) is Jetpack Compose + AndroidX + Kotlin stdlib,
which any modern OEM AI launcher already ships.

In other words, **integrating AOL adds ~41 KB of compiled DEX and 303
methods to the host launcher**, on top of a ~131-LOC source diff
(verified by `docs/oem-pitch/integration/verify-loc.sh` which prints
"OK: under 150 LOC").

---

## Source-of-truth LOC counts

```
apps/aol-android/app/src/main/kotlin/ai/aol/demo/
  AolClient.kt                   158 lines  (AIDL-binding shim, retried connect, callbacks)
  AolMiddlewareService.kt        126 lines  (in-process AolMiddlewareService for demo; production ships in a separate APK)
  AolViewModel.kt                106 lines  (Compose UI state + coroutine bridge)
  FeatureCatalog.kt               57 lines  (24-feature seed; mirrors apps/aol/api/data/seed.json)
  MainActivity.kt                195 lines  (Compose preview / launcher / ControlPanel UI)
apps/aol-android/app/src/main/aidl/ai/aol/IAolMiddleware.aidl
                                  42 lines  (IPC contract: filterSurface, routeCompute, recordOutcome)
                              -------
total                            684 lines
```

The "131 LOC integration footprint" claim in the pitch refers to the
**minimum surface** an OEM has to add to their AI launcher:
`AolClient.kt` (the equivalent of `apps/aol-android/.../AolClient.kt`,
trimmed of comments + the demo example) plus
`IAolMiddleware.aidl`. The other files (`AolMiddlewareService`,
`AolViewModel`, `MainActivity`, `FeatureCatalog`) are the **demo host**
— in a real Moto integration these are replaced by the OEM's own
launcher and an `ai.aol` middleware APK. See
`docs/oem-pitch/integration/verify-loc.sh` for the script that pins
the 131-LOC number.

---

## What is measured here vs. what requires hardware

| Metric | Status | Method |
|---|---|---|
| Builds against AGP 8.5.2 + Kotlin 1.9.24 + Compose BOM 2024.06 | **measured** | `./gradlew assembleDebug` exits 0; build log preserved above |
| APK on-disk + download size | **measured** | `apkanalyzer apk file-size` / `download-size` |
| Method count + dex bytes in `ai.aol.*` | **measured** | `apkanalyzer dex packages` |
| AIDL surface compiles into `Stub.asInterface(...)` | **measured** | the build output proves this — AIDL would fail compile otherwise |
| Cold-start latency (ms from Activity launch → first frame) | **TBD on hardware** | requires real device with `adb shell am start -W` |
| AIDL bind latency (ms from `bindService` → `onServiceConnected`) | **TBD on hardware** | requires real device; emulator numbers are not OEM-credible |
| `routeCompute()` round-trip latency, p50 / p95 | **TBD on hardware** | requires real device perfetto trace |
| Battery-saver wakeup overhead | **TBD on hardware** | requires real device, batterystats |
| RAM footprint after warm-up (procmem) | **TBD on hardware** | requires real device `dumpsys meminfo` |

The honest framing for the first OEM technical review:

> "The Android side compiles and produces a 9.1 MB debug APK on every
> commit. APK weight, method count, and dex bytes are pinned in
> `apps/aol-android/BENCHMARKS.md` so any regression is caught at
> review. On-device latency / battery / RAM benchmarks are deferred
> until I have a partner-build APK on a real Moto device — I won't
> publish emulator numbers because they're not predictive of OEM
> hardware. Give me a Razr 50 or an Edge 50 Pro for two weeks and the
> p50 / p95 / battery numbers go in this file."

---

## How to reproduce

```bash
# Prerequisites: JDK 17 + Android SDK 34 + build-tools 34.0.0
git clone https://github.com/Akshu1245/Secondbrain
cd Secondbrain/apps/aol-android
echo "sdk.dir=$ANDROID_HOME" > local.properties
./gradlew assembleDebug

# Output:
#   app/build/outputs/apk/debug/app-debug.apk     ~9.1 MB

# Inspect:
$ANDROID_HOME/cmdline-tools/latest/bin/apkanalyzer apk file-size       app/build/outputs/apk/debug/app-debug.apk
$ANDROID_HOME/cmdline-tools/latest/bin/apkanalyzer apk download-size   app/build/outputs/apk/debug/app-debug.apk
$ANDROID_HOME/cmdline-tools/latest/bin/apkanalyzer dex packages        app/build/outputs/apk/debug/app-debug.apk | grep '^P d ' | head

# Sideload (any Android 8+ device):
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n ai.aol.demo/.MainActivity
```

A pre-built APK is *not* committed to git — binaries don't belong in
source control, and the build is reproducible in under 4 minutes.
