# OEM outreach plan

A concrete week-by-week playbook. The goal: get to 15-minute meetings, not
"likes". Everything below is reusable across OEMs by swapping the company
name and the *one* personalised hook.

## Roles to target (in order)

For each OEM, pick **two** of the four roles below — one technical, one
business — and send each a personalised version of the templates below.

| Role | LinkedIn search query | Why |
|---|---|---|
| **VP / Head of AI Product** | *Head of AI* OR *VP AI* OR *Director AI* `+ <OEM>` | Sets AI roadmap, controls partnerships budget |
| **Head of Software / OS** | *Head of Software* OR *VP Engineering* `+ <OEM>` | Owns OS-level integration decisions |
| **Director of Developer Relations** | *Developer Relations* OR *DevRel* OR *Partner Engineering* `+ <OEM>` | The right "front door" for 3rd-party SDKs |
| **Head of Product, AI Assistant** | *Product Manager AI Assistant* OR *Head of Product Moto AI* `+ <OEM>` | Owns user-facing AI feature decisions |

For Motorola specifically, also search *"Motorola India"* (not just
"Motorola"), because the India team has historically had more autonomy on
software differentiation.

## LinkedIn filters (copy/paste)

Sales Navigator (or free LinkedIn search):

- **Geography:** India, Singapore, Taiwan, UK (depending on OEM HQ).
- **Company:** the OEM + parent (e.g. *Lenovo* + *Motorola*).
- **Title:** the strings in the table above, OR-joined.
- **Past 30 days posting:** sort by recent posts to find people who are
  *actively talking publicly* about AI on phones — they're 5× more likely to
  reply.

## Cold email — Template A (technical / engineer-to-engineer)

> Subject: Saw the [Moto AI] memory gap. Built a 90-sec demo of the fix.
>
> Hi [Name],
>
> I'm an independent AI engineer, building Second Brain (live demo + open repo + buildable APK).
> I've been using a [Motorola Edge / OnePlus 13 / etc.] for [N] months and
> kept hitting the same wall: [specific feature — e.g. "Remember This sessions
> don't link"]. I went and built the system-layer fix.
>
> The result is **AOL — the AI Optimization Layer**: middleware that filters
> low-value features, routes compute between local and cloud per-call, and
> exposes a Control Panel users actually own. There's a working demo:
>
> - Live dashboard: <https://out-gwumfbso.devinapps.com>
> - API: <https://aol-api-enqcpqaq.fly.dev/docs>
> - 60-second walkthrough: [Loom link — see README]
>
> On the test corpus (24 representative AI features, 30 days of simulated
> usage), AOL hides ~25% of the surface and routes ~45% of calls
> on-device. At a 10K-device pilot scale, that eliminates
> ~6.75M cloud-AI calls/month — **a low-five-figure $/month off your
> cloud-AI bill** at realistic OEM cost-per-call.
>
> Worth 15 minutes? I'm happy to walk an engineer through the integration
> AIDL stub (it's a single Foreground Service, drops in beside Moto AI).
>
> — Akshay K S

## Cold email — Template B (product / business angle)

> Subject: A measurable cut to your AI cloud bill. 15 minutes?
>
> Hi [Name],
>
> Quick context: 73% of iPhone users + 87% of Galaxy AI users say built-in AI
> features add little to no value, and 86% of them won't pay for AI at all
> (TechRadar, May 2025). That's a problem for every flagship roadmap right
> now, [OEM] included.
>
> I've built a system-layer middleware called **AOL** whose explicit success
> metric is **$ saved per device per month**, not "features shipped". It runs
> rule-based, on-device, behind a single AIDL service. On a 10K-device pilot,
> the math suggests low-five-figure $/month off the cloud bill, plus a measurable lift in
> daily AI feature engagement (because we hide the long tail of features
> users never touch).
>
> Live demo + numbers: <https://out-gwumfbso.devinapps.com>
>
> Could I get 15 minutes with whoever owns AI product / platform strategy at
> [OEM]?
>
> — Akshay K S
> rashisolutions1245@gmail.com

## LinkedIn DM (short version)

> Hey [Name] — independent AI engineer, just built an on-device middleware
> that cuts cloud-AI spend and hides the OEM-AI feature clutter (the #1 user
> complaint about Moto / Galaxy / OnePlus AI). 90-second demo: [link].
> Worth 15 min?

## Action timeline

| Week | Action |
|---|---|
| **1** | Finalise demo + this repo. Record 90-sec Loom. Ship pitch deck PDF. |
| **2 (Mon)** | Send Template A to a *technical* contact at Motorola India + OnePlus India. |
| **2 (Wed)** | Send Template B to a *product* contact at Motorola + OnePlus. |
| **2 (Fri)** | LinkedIn DM (short form) to Carl Pei + Nothing dev-relations. |
| **3 (Mon)** | Follow up Week 2 emails with a 1-line nudge ("Bumping this — anything I can clarify?"). |
| **3 (Wed)** | If no reply: send Template A/B to ASUS / ROG and Jio. |
| **3 (Fri)** | Submit AOL to next available hackathon: Lenovo Innovation World, MWC Innovation Award, Snapdragon On-Device AI Challenge. |
| **4** | Iterate based on responses. Negotiate first 15-minute call. |

## Conversion mechanics

The funnel we're aiming for:

```
~30 personalised emails
    → ~6 replies                (20% — cold-email industry baseline)
        → ~3 first calls         (50% conversion of replies)
            → ~1 pilot           (33% conversion of first calls)
```

If we don't hit one pilot in 30 emails, the bottleneck is *the demo + the
positioning*, not the volume. We re-cut the Loom and try again.

## What success looks like

- A 15-minute call with a Motorola India / OnePlus India / Nothing AI lead.
- Concrete questions about the AIDL surface (`docs/integration/`).
- An ask for either (a) a paid 90-day pilot, (b) a referral to whoever owns
  the cloud-AI cost line, or (c) a hackathon-track invitation.

If we don't get any of (a)/(b)/(c) on the first call, we leave with the three
most-pressing technical objections and we ship answers within 72 hours.
