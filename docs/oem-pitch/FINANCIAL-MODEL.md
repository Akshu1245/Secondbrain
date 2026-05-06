# Plexus — Financial Model

Conservative, formula-driven, single-page. All assumptions sourced or
flagged. No hand-waving.

---

## Inputs (defaults calibrated to Moto / Lenovo MBG)

| Symbol | Meaning | Default | Source |
|---|---|---|---|
| `D` | Devices in the deployed fleet (per quarter) | **14.5 M** | TechInsights, Sep 2025 — Lenovo-Motorola Q2 2025 shipments. |
| `C` | AI calls per device per day | **6** | Conservative. Internal seed-data avg = 8.2; Galaxy AI public benchmarks suggest 12–18. We use 6. |
| `R₀` | % of AI calls routed to cloud **today** (without Plexus) | **75 %** | Industry default. Galaxy AI / Pixel AI both ship cloud-first dispatch unless explicitly opted into on-device. |
| `R₁` | % of AI calls routed to cloud **with Plexus** | **45 %** | Live demo measured value across the 24-feature seed catalogue. |
| `H` | % of feature calls suppressed by the Feature Prioritizer (never fire at all) | **20 %** | Conservative. Live demo shows 25 % surface reduction; some of those features still fire if user navigates to them, so we discount by 5 pp. |
| `I_low` | Cost per cloud inference, low end | **$0.0008** | Public commodity-tier inference pricing. Floor case. |
| `I_mid` | Cost per cloud inference, mid case | **$0.002** | Realistic mobile-AI per-call cost (e.g., Gemini Nano fallback, Samsung Bixby cloud calls). |
| `I_high` | Cost per cloud inference, high end | **$0.005** | Frontier-model calls (LLM summarization, multi-modal vision). Ceiling realistic case. |

---

## Formula

Total AI calls / year (across the fleet):

```
Calls_total = D × C × 365
            = 14.5 M × 6 × 365
            = 31.76 B / year
```

Calls that actually fire after Plexus's Feature Prioritizer:

```
Calls_fired = Calls_total × (1 − H)
            = 31.76 B × 0.80
            = 25.41 B / year
```

Cloud calls **today** (no Plexus):

```
Cloud_before = Calls_total × R₀
             = 31.76 B × 0.75
             = 23.82 B / year
```

Cloud calls **with Plexus**:

```
Cloud_after = Calls_fired × R₁
            = 25.41 B × 0.45
            = 11.43 B / year
```

Cloud calls **eliminated per year**:

```
ΔCloud = Cloud_before − Cloud_after
       = 23.82 B − 11.43 B
       = 12.39 B / year
```

Annualized cost reduction at three pricing tiers:

```
Saving_low  = ΔCloud × I_low   = 12.39 B × $0.0008  = $9.91 M / year
Saving_mid  = ΔCloud × I_mid   = 12.39 B × $0.002   = $24.78 M / year
Saving_high = ΔCloud × I_high  = 12.39 B × $0.005   = $61.95 M / year
```

---

## Sensitivity table (annual cloud-AI saving, USD millions)

The conservative case is what we present in outbound. Mid-case is what
we expect the OEM to model internally. High-case is what we show
the CFO once the per-call cost data is unblinded.

|                    | `C = 4` | `C = 6` (default) | `C = 8` | `C = 12` |
|---|---|---|---|---|
| `I_low ($0.0008)`  | $6.6 M  | **$9.9 M**        | $13.2 M | $19.8 M |
| `I_mid ($0.002)`   | $16.5 M | **$24.8 M**       | $33.0 M | $49.5 M |
| `I_high ($0.005)`  | $41.3 M | **$62.0 M**       | $82.6 M | $123.9 M|

---

## Per-device economics

Mid-case, 14.5 M devices, $24.8 M / year cost recovery:

```
Saving_per_device_per_year   = $24.8 M / 14.5 M   = $1.71 / device / year
Saving_per_device_per_month  = $1.71 / 12         = $0.14 / device / month
```

This is the line the OEM CFO needs to see. **$0.14 / device / month**
in recovered cloud spend, on a feature surface that nobody asked the
finance team to budget for.

---

## Pricing model — what the OEM pays

Two-component, aligned to the OEM's incentive to drive the saving:

| Component | Amount | Logic |
|---|---|---|
| **Base licence** | $0.05 / device / year | Recovers Plexus engineering, support, policy authoring, audit-log certification. |
| **Shared savings** | 15–25 % of audited cloud-spend delta, post-pilot | Pure variable. Plexus only earns more if the OEM's bill goes down more. |

At mid-case ($1.71 / device / year saving):

```
OEM_keeps    = 75–85 % × $1.71 = $1.28 – $1.45 / device / year
Plexus_earns = 15–25 % × $1.71 + $0.05 base
             = $0.31 – $0.48 / device / year
```

The base licence is a rounding error against the saving. The
shared-savings tier is the number both sides care about, and it is
auditable from the per-call decision log.

---

## Pilot economics

| Phase | Length | Cost to OEM | What Plexus delivers |
|---|---|---|---|
| **Pilot** | 90 days, 250 K device cohort | **Capped fixed fee** (six-figure USD) | Live deployment, audit log, full delta vs control cohort, cost recovery report. |
| **Production** | 12-month renewal | Base licence + shared savings (above) | Production policy registry, anonymized cross-OEM learning, quarterly policy refresh. |

**Payback period at conservative tier: < 1 quarter post-pilot.**
At mid-case, the pilot fee is recovered in the first 30 days of
production.

---

## What this model deliberately does not include

We want the OEM to find the upside themselves, not have it sold to
them. The following levers are out of scope of the cloud-cost number
above and will compound in the OEM's favour:

* **Battery / thermal headroom** translating into reviewer scores and
  return-rate reduction.
* **Engagement uplift** on retained AI surfaces (we model 0 %; live
  data suggests +12–25 %).
* **Differentiation marketing value** of "uses less of your data and
  less of your battery for AI".
* **Compliance cost avoidance** under EU AI Act, DPDP, SB-1047. A
  per-call audit log is a five-figure line item in legal review even
  if Plexus is free.
* **Optionality value** of a clean orchestration substrate for
  wearables / automotive / laptops over the 24-month horizon.

These are real but harder to defend in a one-page model. The
cloud-cost number alone justifies the deployment.

---

## Assumptions log — what to challenge

If the OEM's internal numbers disagree with ours, here is where to
push:

1. **`R₀ = 75 %`** — we do not know each OEM's true baseline cloud
   share. Replace with the OEM's measured number.
2. **`I = $0.002`** — depends on the OEM's negotiated rate with their
   cloud-LLM vendor. Replace with the actual per-call cost from their
   latest invoice.
3. **`C = 6`** — depends on AI feature uptake. Replace with the
   OEM's measured calls / device / day from their telemetry.
4. **`H = 20 %`** — depends on the realism of the seed catalogue
   versus the OEM's actual feature surface. Replace with the OEM's
   measured 30-day disable rate.

The model is fully open in `apps/aol/api/app/finance.py` (planned
v0.5). Every parameter is a CLI flag.
