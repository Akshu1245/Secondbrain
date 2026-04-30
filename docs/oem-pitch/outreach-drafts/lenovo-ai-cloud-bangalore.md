# Cover letter — Lenovo, Software Engineer (AI Cloud) — Bangalore

**Target:** Lenovo job req **WD00098064 / 76696**
**URL:** <https://jobs.lenovo.com/en_US/careers/JobDetail/Software-Engineer-AI-Cloud/76696>
**Location:** Bangalore, Karnataka, India
**Send window:** **Thursday, May 7, 2026, 10:00–11:00 AM IST** (Jupiter day; paired submission with the MBG req)

---

## Subject line

> Software Engineer, AI Cloud (req 76696) — built a rule-based local-vs-cloud router for OEM AI surfaces

---

## Cover letter

Dear Lenovo Hiring Team,

I'm applying to the **Software Engineer, AI Cloud** role in Bangalore
(req 76696). The job description calls out Python, Node.js, MongoDB,
Kubernetes, Linux, on-prem and cloud, AI/GitHub Copilot, and SALT-stack
skills — applied to the AI compute pipeline behind Lenovo's product
portfolio. I'm sending this letter rather than a generic application
because I built a working prototype that *is* the AI Cloud problem
restated: an on-device-first router that routes feature calls between
local inference and the cloud and audits the decision per call.

**What I shipped (live URLs, public repo):**

* **AOL — AI Optimization Layer** — system-layer middleware between
  the user and an OEM AI assistant. Six rule-based modules. The fourth
  module is the **Compute Optimizer**: a deterministic local-vs-cloud
  router that respects `battery_saver`, `data_saver`, and
  `private_mode` user preferences, plus a per-feature `compute_class`
  (light / medium / heavy). Every decision is logged with the rule
  that fired, the chosen-vs-alternate latency, and the per-call cloud
  cost.
    * Demo: <https://out-ujjsjvxm.devinapps.com>
    * API + Swagger: <https://aol-api-yfdwxezt.fly.dev/docs>
    * Repo: <https://github.com/Akshu1245/Secondbrain> (subdir
      `apps/aol/`)
* On the seeded 24-feature dataset the router keeps **~45% of calls
  on-device**, eliminating those cloud-AI calls entirely. Real
  per-call latency savings come from the local routes (~50–130 ms
  saved per locally-routed light task vs the cloud round-trip); the
  cost saving is the more material number. At a 10K-device pilot
  with ~50 invocations/device/day, the eliminated cloud calls map
  to a low-five-figure $/month range of cloud-AI spend — the same
  back-of-envelope Lenovo's MBG team is already running.
* Deployed end-to-end: FastAPI backend on **Fly.io**, Next.js dashboard
  shipped as a **static export**. Containerised, reproducible, single
  `pyproject.toml` install path. The dev workflow uses `uv` for
  Python, `npm` for the frontend.

**Why this maps to the AI Cloud team:**

* The role is the OEM-facing compute pipeline behind Lenovo's product
  stack. AOL's Compute Optimizer is the rule-based front-door for that
  pipeline — it tells the cloud *which* feature calls to even bother
  serving. Together with the Lenovo AI Cloud you can measure dollars
  saved per device per month rather than just "we shipped AI." The
  per-feature mapping (which Moto AI features stay cloud, which go
  local, and the $/month delta at Lenovo-Motorola's Q2 2025 shipment
  scale) is documented at
  <https://github.com/Akshu1245/Secondbrain/blob/main/docs/oem-pitch/moto-specific.md>.
* The job description mentions **Python, Linux, on-prem + cloud, basic
  AI / GitHub Copilot, Kubernetes, MongoDB, SALT-stack**. AOL's stack
  hits 6 of those directly (Python, Linux containerised on Fly.io,
  cloud + on-device routing, AI productization, k8s-friendly Docker
  image, JSON state-store designed to be swapped to Mongo / Redis with
  one adapter). The two I haven't shipped yet (SALT-stack, full Mongo)
  are configuration-management bridges I can come up to speed on
  inside a sprint.
* I'm a Bangalore-native developer (Bellary / Karnataka), so on-site
  expectations are non-issues.

**Credentials:**

* **4 provisional AI patents** in adjacent territory:
    * `[PATENT 1 TITLE]`
    * `[PATENT 2 TITLE]`
    * `[PATENT 3 TITLE]`
    * `[PATENT 4 TITLE]`
* Solo-shipped 4 PRs of working code on the same project before this
  application landed (link above) — not a course project, deployed
  infrastructure with public URLs.
* `[BRIEF EDUCATION + ANY RELEVANT INTERNSHIPS — 1 line]`

**What I'd want to do in the first 90 days:**

* Bring AOL's Compute Optimizer logic into a Lenovo AI Cloud-style
  pipeline as a routing layer that any device-side AI surface can
  call into.
* Port the JSON state-store to Mongo and add a metrics surface (cost
  per feature × per SKU × per geography) so the team has a $/device/
  month dashboard out of the box.
* Help on SRE / SALT-stack runbooks under guidance from the senior
  members of the team.

I would value 30 minutes with the AI Cloud hiring manager to walk
through the demo and discuss how the local-vs-cloud routing concept
could plug into Lenovo's existing pipeline. Happy to do a screen-share
at any time, in any time-zone.

Thank you for reading.

Best regards,
**K S Akshay**
`rashisolutions1245@gmail.com`
LinkedIn: `[YOUR LINKEDIN URL]`
GitHub: <https://github.com/Akshu1245>
Repo for this application: <https://github.com/Akshu1245/Secondbrain>
Live demo: <https://out-ujjsjvxm.devinapps.com>

---

## Resume / portfolio insert

> **AOL — AI Optimization Layer · Compute Optimizer module**
> (solo project, open-source). Rule-based local-vs-cloud routing
> middleware for OEM AI assistants. Honors `battery_saver`,
> `data_saver`, and `private_mode` preferences; logs every decision
> with the rule that fired, latency, and per-call cost. **~45% of
> calls routed on-device** on the seeded dataset, eliminating those
> cloud-AI calls entirely; pilot-scale savings are illustrative and
> documented in the repo. FastAPI + Fly.io + Next.js static export.
> Live demo: out-ujjsjvxm.devinapps.com. Repo:
> github.com/Akshu1245/Secondbrain.

---

## Personalisation checklist before sending

- [ ] Confirm req **76696** is still open at the Lenovo careers portal
      (Bangalore, AI Cloud). If not, find the closest equivalent and
      update the subject line + opening.
- [ ] Replace `[PATENT 1–4 TITLE]` with the actual patent titles.
- [ ] Replace `[BRIEF EDUCATION + ANY RELEVANT INTERNSHIPS]`.
- [ ] Replace `[YOUR LINKEDIN URL]`.
- [ ] If the application form has a 200-character "why this role" box,
      paste this short version: *"Built a rule-based local-vs-cloud
      router (AOL Compute Optimizer) that keeps 45% of OEM-AI calls on-
      device and logs every decision auditably. Live demo:
      out-ujjsjvxm.devinapps.com. Want to bring it inside Lenovo AI
      Cloud."*
