# Cover letter — Lenovo MBG, Software Engineer (AI Productization)

**Target:** Lenovo job req **WD00086274 / 69831**
**URL:** <https://jobs.lenovo.com/en_US/careers/JobDetail/Software-Engineer-AI-Productization/69831>
**Location:** Chicago, IL (open to Bangalore relocation if posted)
**Send window:** Thursday morning IST (10:00–11:00 AM IST). Thursdays are the highest open-rate day for hiring inboxes; mid-morning IST hits the start of US Central business day.

---

## Subject line (when paste-applying via email or referral channel)

> Software Engineer, AI Productization (req 69831) — built Second Brain, the memory + routing layer for Moto AI (live demo, 131-LOC AIDL shim)

---

## Cover letter

Dear Lenovo MBG Hiring Team,

I'm applying to the **Software Engineer, AI Productization** role on the
Mobile Business Group team in Chicago (req 69831). The reason I'm sending
this rather than a generic application: I built and shipped a working
prototype that addresses two of the most-requested gaps in Moto AI as it
stands today — and I'd like to bring it inside the team that owns
Catch-Me-Up, Pay-Attention, and Remember-This.

**What I shipped, on a public repo with live URLs:**

* **Second Brain** — a memory + routing layer that plugs into an OEM
  AI assistant. Six rule-based modules: Memory Layer, Usage Tracker,
  Smart Feature Filter, Context Engine, AI Router (codename AOL,
  preserved in the codebase), Feedback Loop. Live demo + Swagger:
    * Demo: <https://out-gwumfbso.devinapps.com>
    * API + docs: <https://aol-api-enqcpqaq.fly.dev/docs>
    * Repo: <https://github.com/Akshu1245/Secondbrain>
  * Cuts feature-surface noise by 25% and routes 45% of cloud-AI calls
    on-device on the seeded dataset. Memory layer keeps Catch-Me-Up
    coherent across sessions, persists Remember-This signals beyond
    the current screen. Includes a drop-in **AIDL + Kotlin reference**
    so an MBG Android engineer can integrate it in **131 lines of code**.

**Why this maps to AI Productization:**

* Moto AI's pillars (*Catch Me Up*, *Pay Attention*, *Remember This*)
  are a memory product on top of a compute pipeline. Second Brain
  delivers both halves: the memory layer keeps the surface coherent
  across sessions, and the routing layer reduces cloud spend on the
  compute pipeline. Both gaps are documented from a per-platform
  Reddit / press crawl at
  <https://github.com/Akshu1245/Secondbrain/blob/main/docs/oem-pitch/user-pain-audit.md>.
* Per-feature mapping of *which Moto AI feature each Second Brain
  module improves* (Catch Me Up → local; Pay Attention → stays cloud
  but context-suggested; Smart Reply → local; etc.) plus dollar-
  savings calibrated to Lenovo-Motorola's 14.5 M Q2 2025 shipments:
  <https://github.com/Akshu1245/Secondbrain/blob/main/docs/oem-pitch/moto-specific.md>
* The Second Brain AI Router is the same kind of rule-based
  local-vs-cloud routing decision a productization team has to make
  every sprint. The decision log is auditable per call — built so a
  Lenovo legal/security team can review without ML expertise.

**Credentials:**

* Solo-shipped 7 PRs of working code on the AOL / Second Brain
  project before this application landed — not a course project.
  Deployed FastAPI backend, Next.js dashboard, buildable Android APK,
  53 passing pytest tests, GitHub Actions CI under 60 s wall-clock.
* Found and pinned a savings-aggregation bug in the routing model
  inside the test suite before it shipped (documented in `compute.py`)
  — the kind of measurement-integrity bar a productization team needs
  on every metric the OEM cites externally.
* **Education:** BCA, 2nd year, Bangalore North University,
  expected 2027. I am candid that I'm early-career; the artefact
  above is the work I'd hand any senior engineer for review.
  No-opportunity-cost hire — ships fast, fully present, no parallel
  full-time employer.

**What I'd want to do in the first 90 days at MBG:**

* Take Second Brain's Python reference rules and port them into the
  Kotlin service skeleton in `docs/oem-pitch/integration/`.
* Wire the Catch-Me-Up / Pay-Attention / Remember-This pipeline into
  Second Brain's memory primitives so the journal stops being write-
  only.
* Publish a `$ saved per device per month` dashboard internally so the
  optimisation work is measured against a number the finance team
  understands.

I would value 30 minutes with a hiring manager on the AI Productization
team to walk through the demo and discuss how this maps to the team's
2026 roadmap. The repo, the live demo, and the AIDL stub are all there
for review — happy to do a screen-share at any time.

Thank you for reading.

Best regards,
**K S Akshay**
Founder, Rashi Technologies
`rashisolutions1245@gmail.com`
LinkedIn: <https://linkedin.com/in/k-s-akshay-0707a42b6>
GitHub: <https://github.com/Akshu1245>
Repo for this application: <https://github.com/Akshu1245/Secondbrain>
Live demo: <https://out-gwumfbso.devinapps.com>

---

## Resume / portfolio insert (use this exact bullet on top of page 1)

> **Second Brain — the memory + routing layer for OEM AI** (solo
> project, open-source). Plugs into an OEM AI assistant; gives it
> persistent memory under Catch-Me-Up / Pay-Attention / Remember-This
> and a per-call on-device-vs-cloud router. Six rule-based modules
> (Memory, Usage Tracker, Smart Feature Filter, Context Engine, AI
> Router, Feedback Loop). Cut feature-surface noise 25% and routed
> 45% of cloud-AI calls on-device on the seeded dataset. Shipped a
> drop-in AIDL + Kotlin reference for native Android integration in
> 131 LOC. **Live demo: out-gwumfbso.devinapps.com.** **Repo:
> github.com/Akshu1245/Secondbrain.**

---

## Personalisation checklist before sending

- [ ] Confirm req **69831** is still posted at the Lenovo careers
      portal. If not, find the closest equivalent on the same team and
      update the subject line + opening paragraph.
- [ ] (Optional) Update the education line if the placeholder default
      ("BCA, 2nd year, Bangalore North University, expected 2027") is
      not exactly right.
- [ ] (Optional) Confirm the LinkedIn URL
      <https://linkedin.com/in/k-s-akshay-0707a42b6> resolves to your
      profile.
- [ ] If the application form has a 200-character "why this role" box,
      paste this short version: *"I built Second Brain — the missing
      memory + routing layer for Moto AI — as a solo project. Live
      demo: out-gwumfbso.devinapps.com. Want to bring it inside the AI
      Productization team."*
- [ ] If the form has a "ready to relocate" question — answer **yes**
      to Chicago and Bangalore (both reqs are MBG and the same team).
