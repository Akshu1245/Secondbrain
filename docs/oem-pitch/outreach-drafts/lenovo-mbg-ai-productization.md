# Cover letter — Lenovo MBG, Software Engineer (AI Productization)

**Target:** Lenovo job req **WD00086274 / 69831**
**URL:** <https://jobs.lenovo.com/en_US/careers/JobDetail/Software-Engineer-AI-Productization/69831>
**Location:** Chicago, IL (open to Bangalore relocation if posted)
**Send window:** **Thursday, May 7, 2026, 10:00–11:00 AM IST** (Jupiter day; date 7 = Mercury / Ketu — research-favoured)

---

## Subject line (when paste-applying via email or referral channel)

> Software Engineer, AI Productization (req 69831) — shipped a Moto AI optimiser (45 % calls on-device, 131-LOC AIDL drop-in)

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

* **AOL — AI Optimization Layer** (system-layer middleware between user
  and OEM AI assistant). Six rule-based modules: Usage Tracker, Smart
  Feature Filter, Context Engine, Compute Optimizer, Control Panel,
  Feedback Loop. Live demo + Swagger:
    * Demo: <https://out-ujjsjvxm.devinapps.com>
    * API + docs: <https://aol-api-yfdwxezt.fly.dev/docs>
  * Cuts feature-surface noise by 25% and routes 45% of cloud-AI calls
    on-device on the seeded dataset. Includes a drop-in **AIDL +
    Kotlin reference** so an MBG Android engineer can integrate it in
    &lt; 150 lines of code.
* **Second Brain** — companion on-device memory layer (consolidation,
  decay, distillation, multi-hop recall, episodic provenance, MCP
  surface for agents). v0 → v2 shipped in 3 PRs.
* Both projects in the same monorepo:
  <https://github.com/Akshu1245/Secondbrain>

**Why these projects map to AI Productization:**

* Moto AI's pillars (*Catch Me Up*, *Pay Attention*, *Remember This*)
  are a memory product on top of a compute pipeline. AOL's optimiser
  reduces the cloud-spend on that pipeline; Second Brain's memory layer
  makes Remember-This actually persist + recall across sessions. They
  are exactly the two gaps in the current Moto AI surface — sourced
  from a per-platform Reddit / press / OzBargain crawl I documented at
  <https://github.com/Akshu1245/Secondbrain/blob/main/docs/oem-pitch/user-pain-audit.md>.
* Per-feature mapping of *which Moto AI feature each AOL module
  improves* (Catch Me Up → local; Pay Attention → stays cloud but
  context-suggested; Smart Reply → local; etc.) plus dollar-savings
  calibrated to Lenovo-Motorola's 14.5 M Q2 2025 shipments:
  <https://github.com/Akshu1245/Secondbrain/blob/main/docs/oem-pitch/moto-specific.md>
* The AOL Compute Optimizer is the same kind of rule-based local-vs-
  cloud routing decision a productization team has to make every
  sprint. The decision log is auditable per call — built so a Lenovo
  legal/security team can review without ML expertise.

**Credentials:**

* **4 provisional AI patents** in adjacent territory:
    * `[PATENT 1 TITLE]`
    * `[PATENT 2 TITLE]`
    * `[PATENT 3 TITLE]`
    * `[PATENT 4 TITLE]`
* Solo-shipped 4 PRs of working code on the project before this
  application landed (link above) — not a course project, deployed
  infrastructure with public URLs.
* `[BRIEF EDUCATION + ANY RELEVANT INTERNSHIPS — 1 line]`

**What I'd want to do in the first 90 days at MBG:**

* Take AOL's Python reference rules and port them into the Kotlin
  service skeleton in `docs/oem-pitch/integration/`.
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
`rashisolutions1245@gmail.com`
LinkedIn: `[YOUR LINKEDIN URL]`
GitHub: <https://github.com/Akshu1245>
Repo for this application: <https://github.com/Akshu1245/Secondbrain>
Live demo: <https://out-ujjsjvxm.devinapps.com>

---

## Resume / portfolio insert (use this exact bullet on top of page 1)

> **AOL — AI Optimization Layer** (solo project, open-source). System-
> layer middleware between user and OEM AI assistant. Six rule-based
> modules (Usage Tracker, Smart Feature Filter, Context Engine, Compute
> Optimizer, Control Panel, Feedback Loop). Cut feature-surface noise
> 25% and routed 45% of cloud-AI calls on-device on the seeded dataset.
> Shipped a drop-in AIDL + Kotlin reference for native Android
> integration. **Live demo: out-ujjsjvxm.devinapps.com.** **Repo:
> github.com/Akshu1245/Secondbrain.**

---

## Personalisation checklist before sending

- [ ] Confirm req **69831** is still posted at the Lenovo careers
      portal. If not, find the closest equivalent on the same team and
      update the subject line + opening paragraph.
- [ ] Replace `[PATENT 1–4 TITLE]` with your actual patent titles.
- [ ] Replace `[BRIEF EDUCATION + ANY RELEVANT INTERNSHIPS]`.
- [ ] Replace `[YOUR LINKEDIN URL]`.
- [ ] If the application form has a 200-character "why this role" box,
      paste this short version: *"I built AOL — the missing memory +
      optimisation layer for Moto AI — as a solo project. Live demo:
      out-ujjsjvxm.devinapps.com. Want to bring it inside the AI
      Productization team."*
- [ ] If the form has a "ready to relocate" question — answer **yes**
      to Chicago and Bangalore (both reqs are MBG and the same team).
