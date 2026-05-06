# Second Brain (the repo) · AOL (the product being pitched)

> **Heads up:** the repo is named *Second Brain* because it started as a
> memory-layer project. The headline product being pitched to OEMs is
> **AOL — AI Optimization Layer** (in [`apps/aol/`](apps/aol/)). Second
> Brain is the on-device memory companion that AOL's Feedback Loop
> reads from. Two artefacts, one repo, one pitch.

A two-layer AI infrastructure for smartphones. Built for the OEM AI pitch
(Motorola, OnePlus, Nothing, ASUS, Jio).

| Layer | What it is | Where to read |
|---|---|---|
| **Optimisation layer** — AOL (AI Optimization Layer) — **★ headline product** | System-layer middleware between user and OEM AI assistant. Filters low-value features, surfaces context-relevant ones, routes compute between local and cloud, ships a Control Panel. Live demo + AIDL drop-in (~131 LOC) + buildable Android APK. | [`apps/aol/`](apps/aol/) |
| **Memory layer** — Second Brain — companion | On-device knowledge memory: capture (reels, screenshots, conversations), embed, dedupe, consolidate, decay, multi-hop recall, episodic provenance. Exposed to agents via MCP. AOL's Feedback Loop reads from it (≥2 durable signals → auto-hide recommendation). | [`apps/api/`](apps/api/) |

**Live AOL demo:** <https://out-gwumfbso.devinapps.com> · **AOL API:** <https://aol-api-enqcpqaq.fly.dev/docs> · **Pitch package:** [`docs/oem-pitch/`](docs/oem-pitch/)

## Why both layers exist

Phone AI is broken. The numbers from independent surveys say so:

* 73% of iPhone users + 87% of Galaxy AI users say built-in AI features add
  little to no value.
* 86.5% / 94.5% of those users won't pay for AI features.
* 11% of US adults would upgrade their phone for AI — **down 7 pts YoY**.
* Top complaints across Reddit / Twitter / press: bloatware, irrelevance,
  cloud cost, no persistence.

Every flagship is shipping more AI features. None of them is solving the
two structural problems behind those numbers: there's no **memory layer**
(features can't remember what the user did last week) and there's no
**optimisation layer** (everything fires regardless of context, and most
of it goes to the cloud unnecessarily).

This repo ships both — as one pitch, two technical artefacts.

## OEM pitch package

| File | What it is |
|---|---|
| [`docs/oem-pitch/pitch-deck.md`](docs/oem-pitch/pitch-deck.md) | 10-slide deck. Read in &lt; 5 min. |
| [`docs/oem-pitch/one-pager.md`](docs/oem-pitch/one-pager.md) | One-pager for warm intros. |
| [`docs/oem-pitch/oem-targets.md`](docs/oem-pitch/oem-targets.md) | Ranked OEM targets (Moto → OnePlus → Nothing → ASUS → Jio) with entry points and sourced citations. |
| [`docs/oem-pitch/oem-outreach.md`](docs/oem-pitch/oem-outreach.md) | Week-by-week outreach playbook + 2 cold-email templates + LinkedIn DM. |
| [`docs/oem-pitch/user-pain-audit.md`](docs/oem-pitch/user-pain-audit.md) | Reddit / Twitter / Instagram / Facebook pain audit with direct links to public complaints. |
| [`docs/oem-pitch/what-users-want.md`](docs/oem-pitch/what-users-want.md) | The mirror of the pain audit — what users explicitly say *would* make them stay or switch to Moto. The doc to put in front of a Moto Product Lead. |
| [`docs/oem-pitch/solo-founder-to-moto.md`](docs/oem-pitch/solo-founder-to-moto.md) | 90-day campaign plan for a solo founder to land at Moto — partnership track + job track in parallel, with named roles and live req IDs. |
| [`docs/oem-pitch/integration/`](docs/oem-pitch/integration/) | `IAolMiddleware.aidl` + `AolClient.kt` — drop-in Kotlin reference for native integration into a Moto / OnePlus / Nothing AI assistant. |

## Repo layout

```
Secondbrain/
├── apps/
│   ├── api/                         Second Brain memory layer (FastAPI + MCP)
│   │   └── app/                     ingestion, embeddings, recall, episodes,
│   │                                consolidation, decay, distillation,
│   │                                reflection, GraphRAG rollups, skills,
│   │                                conversation import, multi-hop recall
│   └── aol/                         AOL — AI Optimization Layer
│       ├── api/                     FastAPI middleware (6 modules)
│       ├── web/                     Next.js dashboard (Control Panel)
│       └── README.md                AOL-specific quickstart
└── docs/
    └── oem-pitch/                   one-stop pitch package for OEM outreach
```

## Status

| Item | Status |
|---|---|
| Memory layer v0 (FastAPI + Next.js PWA scaffold) | shipped — PR [#1](https://github.com/Akshu1245/Secondbrain/pull/1) |
| Memory layer v1 (Agent Memory Edition: MCP + Tool Attention + facts/episodes/correction) | shipped — PR [#2](https://github.com/Akshu1245/Secondbrain/pull/2) |
| Memory layer v2 (Stronger Memory: consolidation, decay, distill, reflect, rollups, multi-hop, skills, conversation import) | shipped — PR [#3](https://github.com/Akshu1245/Secondbrain/pull/3) |
| AOL backend (6 modules, 14 endpoints) | shipped — this PR |
| AOL dashboard (6-tab Next.js) | shipped — this PR |
| AOL deployed (live demo URL) | live — <https://out-gwumfbso.devinapps.com> |
| AOL deployed (live API URL) | live — <https://aol-api-enqcpqaq.fly.dev> |
| Pitch deck + one-pager + OEM targets + outreach + user-pain audit + AIDL stub | shipped — this PR |

## Author

Akshay K S — `rashisolutions1245@gmail.com` — 4 provisional patents in
adjacent AI territory.
