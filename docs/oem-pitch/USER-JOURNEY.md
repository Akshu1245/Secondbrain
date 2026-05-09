# Second Brain — User Journey

A 90-day narrative of how Second Brain adapts to one user, on one Moto-class
device, from first boot to steady-state. Numbers are illustrative but
match the seed-data behaviour observable in the live demo.

---

## Persona

**Priya, 28, marketing manager, Bangalore.** Buys a new Moto Edge 60
in early February. She uses her phone for messaging (WhatsApp, Slack),
photography (~15 shots / day), navigation, and reading newsletters in
the evening. She has been on a Galaxy device for three years and has
opinions about AI features — most of them mildly negative.

The Moto Edge 60 ships with 24 named AI features in the assistant
surface: Catch Me Up, Smart Reply, Magic Eraser, Image Studio, Live
Translate, Pay Attention, Remember This, and 17 others.

---

## Day 0 — First boot

Priya powers on the device. The Moto AI assistant shows the full
24-feature surface. Second Brain is installed but in **cold-start mode** —
no per-user signal yet, so the assistant displays the OEM-default
priority list.

Behind the scenes, Second Brain has already received the device context:
Asia/Kolkata locale, English + Hindi keyboards, default carrier APN,
a Snapdragon 7s Gen 3, and the OEM's seed-default policy. No
inferences have been routed yet.

> **Second Brain state:** cold-start. All routing decisions follow OEM
> defaults. Telemetry collection begins.

---

## Day 1–7 — Observation window

Priya uses the phone normally:

* **Messaging:** Smart Reply fires 12–18 times / day. She accepts
  ~4 / day; she dismisses or types over the rest.
* **Photography:** Magic Eraser fires once when she long-presses a
  photo. She uses it. Image Studio fires twice as a suggestion; she
  ignores both.
* **Navigation:** No AI surface engagement.
* **Reading:** Catch Me Up fires nightly; she opens it twice all week.
* **Pay Attention** fires three times — context-detected events
  (calendar invites, OTP reads). She does not engage.
* **Live Translate** fires once when a Hindi WhatsApp voice note
  arrives. She uses it.

Second Brain's Telemetry Engine is logging all of this — feature ID, when
it fired, whether the user engaged, latency, and which compute path
(local / cloud) the call took. Nothing has changed in Priya's
experience yet.

> **Second Brain state:** observing. No policy changes. Decision log
> growing at ~120 rows / day.

---

## Day 8 — First adaptive shift

By day 8, the Learning Loop has accumulated **two independent durable
signals** for three features:

| Feature | Signal 1 | Signal 2 | Action |
|---|---|---|---|
| Image Studio | 14 fires, 0 engagements | User's "never use" feedback in Control Panel | Auto-hide |
| Catch Me Up | 7 fires, 2 engagements | Engagement only when battery > 50 % | Surface only on charge |
| Pay Attention | 21 fires, 0 engagements | Disabled in Control Panel after day 5 | Hide entirely |

Priya wakes up on day 8 to a slightly cleaner assistant surface. She
does not notice anything is missing — the features she did not use are
gone; the ones she did use are still there. **She does not need to
have configured anything.**

The decisions are auditable. If Priya opens Settings → Second Brain → Why,
she sees the rule that fired and the alternate she could have had. If
she disagrees, she clicks "bring back" and the policy is reverted with
a manual-override marker.

> **Second Brain state:** active personalization. Surface size: 24 → 18
> features. Cloud-AI calls / day: 21 → 13.

---

## Day 30 — Steady state

By day 30, Second Brain has converged on Priya's behaviour:

* **Visible features:** 11 of the original 24. Surface size has
  shrunk by 54 %. Smart Reply, Magic Eraser, Live Translate,
  Remember This, and 7 others remain. The rest are suppressed
  unless she explicitly navigates to them.
* **Compute routing:** ~52 % of her remaining AI calls now run
  on-device. Smart Reply (small model), Live Translate (cached
  Hindi/English pair), and Remember This (local index) are local.
  Catch Me Up (multi-doc summarization) and Magic Eraser (large
  vision model) stay cloud.
* **Battery & data:** Daily AI-attributable battery drain has dropped
  from ~7 % to ~3 %. Daily AI-attributable cellular data has dropped
  from ~140 MB to ~55 MB. Priya does not know these numbers; she just
  notices the phone "feels lighter."
* **Engagement on retained surfaces:** Smart Reply acceptance rate is
  up 18 % vs day 1. Live Translate is now her most-used AI feature
  by daily-active count.

> **Second Brain state:** steady-state. Surface 11 / 24. Local-route
> share 52 %. Cloud-AI calls eliminated vs day-0 baseline: ~63 %.

---

## Day 75 — Edge case: Priya travels to Singapore

Priya flies to Singapore for a week of meetings. The Context Engine
detects:

* New timezone (Asia/Singapore).
* Roaming carrier.
* New language environment (English-only signage).
* Battery saver toggled on during a long taxi ride.

Second Brain reacts in three places:

1. **Live Translate** is re-elevated to the top of the surface for
   the duration of the trip — language-shift rule fires.
2. **Cloud routing is throttled** under battery saver and roaming
   data — `routeCompute` returns `local` for any call with a
   reasonable on-device fallback. Magic Eraser, which only has a
   cloud path, is queued until charge / Wi-Fi.
3. **Pay Attention** is temporarily re-elevated (calendar event
   density up 4× during the trip). It is auto-hidden again on day
   83 when Priya returns home and the calendar density falls.

None of this required Priya to do anything. None of this required the
OEM to ship a custom policy. The rules are deterministic and the
decision log is auditable.

> **Second Brain state:** context-shifted. Live Translate temporarily
> re-elevated. Cloud routing reduced under roaming.

---

## Day 90 — What Second Brain has actually delivered

**For Priya:**

* A phone that feels lighter and more relevant. Surface clutter is
  gone. The features she uses are surfaced; the features she does not
  use are not.
* Better battery (~4 %/day better) and data (~60 % less AI data)
  with no perceived loss of capability.
* Continuity across context shifts (travel, low battery, roaming)
  without manual settings churn.

**For Moto:**

* ~63 % cloud-AI call reduction on Priya's device, audited per
  call, attributable to Second Brain's per-feature decisions.
* No engineering changes to the Moto AI assistant beyond the
  131-line integration shim.
* A telemetry stream the legal team can use as the audit log for EU
  AI Act, DPDP, and SB-1047.
* Engagement uplift on retained surfaces — measurable in the
  assistant's own metrics, no Second Brain-side magic required.

**For Second Brain:**

* One more device's worth of anonymized policy effectiveness data,
  feeding the cross-OEM learning surface. Future OEMs benefit from
  the policy-effectiveness priors learned on this fleet, with no
  PII leaving any device.

The orchestration layer worked. Priya has no idea it exists. Moto
has the audit log to prove it shipped. The CFO sees the line item in
the next quarterly cloud bill.

This is the steady state we are selling.
