# What users actually want — and what Moto should do to win them

The mirror of [`user-pain-audit.md`](./user-pain-audit.md). Same source
threads, but flipped: instead of the complaints, the explicit *"if Moto
just did X I'd come back"* signals.

This is the document a Moto Product Lead should read first. It tells
them what to build (and what to *stop* building) to convert the
complaining users back into buyers.

## The five things users explicitly say they want

Sourced from the same Reddit / press / forum threads cited in
[`user-pain-audit.md`](./user-pain-audit.md) — these are not our
guesses, they are quotes from the threads.

### 1. **A real off switch** — *one* place to turn AI off completely

Users repeatedly try to *uninstall*, not just disable, the AI surface.
Today disabling Moto AI / Galaxy AI / Apple Intelligence / Essential
Space requires multiple settings flips, ADB tricks, or third-party
debloater scripts. The product win is a single toggle that:

- removes the AI surface from the launcher / lock screen,
- stops background services,
- frees the storage,
- *does not silently re-enable itself on the next OTA*.

> *"I don't want to turn it off, I want it purged from my phone."*
> — r/motorola

> *"It's a system app… You can uninstall it but it reinstalls itself
> again and the option to uninstall it disappears."*
> — r/motorola

**What AOL ships that solves this:** Control Panel + Smart Filter. Per
feature, the user gets `on / off / hidden`, the `off` state is binding
across OTA updates, and the storage / background services for hidden
features are reclaimed by the OEM image.

### 2. **The AI shouldn't fire when I didn't ask** — context, not gestures

The biggest complaint about Nothing's Essential Space and Moto's AI
swipe-up is *the feature firing by accident*. Users do not want a
dedicated AI button that they hit by accident — they want the AI to
appear when *they* are doing something the AI can help with.

> *"It's just the world's most annoying app that screenshots whatever
> is currently on the display, every time you pick up the phone."*
> — r/NOTHING (Essential Space)

> *"It popped up as soon as I woke up."* — r/motorola

**What AOL ships that solves this:** Context Engine. `(time_of_day,
activity)` → top-3 surfaced features. Morning + commute → Morning
Briefing, Spam Call Filter, Smart Navigation. Evening + winddown →
Sleep Soundscape, Photo Cleanup. Nothing fires unless the (time,
activity) tuple matches a rule the OEM authored.

### 3. **Don't make me pay (in battery / data / cloud cost) for things I
   won't pay money for**

The TechRadar / SellCell numbers — 86.5% of iPhone AI users and 94.5%
of Galaxy AI users say they *won't pay* for AI features — are the
single most important data point in this whole pitch. The
implication: any AI feature that costs the OEM real cloud-compute money
to run, but that the user won't pay to keep, is a structural loss.

> *"I'm sure I'm not the only one that's weighted up the cost (10gb of
> disk space) vs benefit (none) and have turned it off."*
> — r/apple

> *"Insane battery life… 1 hour 52 mins, consumed 43%."*
> — r/motorola (battery thread tail)

**What AOL ships that solves this:** Compute Optimizer. Every cloud call
goes through a rule-based local-vs-cloud router. `battery_saver=on`
forces local for non-heavy tasks. `data_saver=on` forces local for
anything with a viable on-device path. `private_mode=on` is a hard rule
that *always* keeps it local. The decision log is auditable per call.

### 4. **Stop preloading partner AI apps as bloatware**

The Perplexity-on-Moto fiasco is the canonical example, but Glance,
CrystalTalk, Live Lockscreen, and the "swipe-left for discover" surface
all share the same shape: a partner-deal that ships as a non-removable
default and is read by users as bloatware.

> *"The less AI apps I have on my phone, the better — especially when
> the app is installed right out of the box."* — MakeUseOf

> *"It's a Motorola bloatware app, I've just uninstalled it."*
> — r/motorola

**What Moto should do**: replace the "ship partner X as a default app"
strategy with a "ship the AOL Control Panel as a default surface, and
put partner X in the catalogue *behind* it." The user opts in with one
tap, and now Perplexity / Glance / etc. are *features* not *bloatware*.
The partner deal still works — Moto just stops paying the user-trust
tax for it.

### 5. **AI features that actually remember**

The Moto AI pillar called *"Remember This"* doesn't, in the user's
experience, remember. Users expect the captured info to *show up*
later, in context, without being asked.

> *"How about they actually deliver the Apple Intelligence they demoed
> two years ago."* — r/apple

> *"Apple Intelligence Notification Summaries got the news headline
> 100% wrong."* — X / Twitter (paraphrased, common theme)

**What Second Brain (companion product, this same repo) ships that
solves this:** the on-device memory layer (consolidation, decay,
multi-hop recall, episodic provenance, skills). When Moto's "Remember
This" captures a meeting note, Second Brain links it to the previous
five meetings with the same person, the email thread that triggered it,
and surfaces the link the next time that contact texts you. Without a
memory layer, *Remember This* is a journal app. With a memory layer,
it's *the killer app on the phone* the press is asking for.

## What Moto should ship in the next 12 months

In priority order, derived from the complaint surface and the data:

| Priority | Ship | Why | Lift |
|---|---|---|---|
| **P0** | A single AI on/off switch that is binding across OTA, with the storage / services freed when off | Removes the #1 complaint (forced installation), takes the bloatware label off Moto AI overnight | 1 sprint |
| **P0** | The AOL Control Panel as a system app | Gives users the granular control they keep asking for, without forcing each PM to ship their own settings page | 6 weeks |
| **P0** | Compute Optimizer with `battery_saver` / `private_mode` honoured by every Moto AI surface | Cuts the cloud bill *and* answers the privacy complaint at the same time | 6 weeks |
| **P1** | Replace the "preload Perplexity / Glance" strategy with an opt-in catalogue inside the AOL Control Panel | Salvages the partner economics without paying the user-trust tax | 1 quarter |
| **P1** | Wire *"Remember This"* / *"Pay Attention"* / *"Catch Me Up"* into the Second Brain memory layer | Makes Moto AI's three flagship features actually deliver on their names | 1–2 quarters |
| **P2** | Publish a public Moto AI engagement dashboard ("X% of users use feature Y monthly") so users see the OEM is listening | Closes the loop the Reddit threads are screaming about — that nobody at Moto reads them | 1 sprint |

## What Moto should *stop* shipping

In equal priority, the explicit list of things to kill or hide-by-default:

1. **Glance / Live Lockscreen** as a default-on surface. Move it to
   opt-in behind the Control Panel.
2. **Pre-installed third-party AI apps** marketed as Moto AI features
   (Perplexity, Copilot, etc.). Same fix — opt-in catalogue.
3. **Multi-assistant defaults**. Pick *one* default assistant per device
   family. The Android-Authority poll says 43% of users use *zero* AI
   assistants — shipping with three is actively harmful.
4. **Hidden AI services that re-enable on OTA**. Whatever the user said
   "off" to, OTA must respect.

## Why this matters commercially

At 10K-device pilot scale (the AOL pitch) the Compute Optimizer alone
eliminates ~**6.75M cloud-AI calls / month**. At the seed-data
illustrative cost ($0.0008/call) that's ~$5K/month; at the realistic
OEM cost-per-call (typically 3–10× higher because flagship LLM calls
cost more than the seed bound), it lands in the **low-five-figure
$/month range**. At a Moto India SKU run-rate (low-millions of devices
/ year) the same savings extrapolate into the **seven-to-eight-figure
annual range** — not in revenue, but in *cost the OEM is already
spending and getting nothing back for*. That is the line the finance
team understands.

The user-trust win is harder to quantify but bigger: shipping a single
binding off-switch flips the press narrative from *"Moto adds more
bloatware"* to *"Moto is the OEM that respects your phone"* — and
that's the only kind of differentiator the Android-Authority poll
above is leaving room for.

## How this connects back to the AOL + Second Brain pitch

| User want | AOL module | Second Brain primitive |
|---|---|---|
| Real off switch | Control Panel + Smart Feature Filter | — |
| Don't fire when not asked | Context Engine | — |
| Don't pay battery / cloud | Compute Optimizer | — |
| Stop the partner-bloatware pattern | Control Panel (catalogue) | — |
| Features that remember | — | Memory layer (consolidation, decay, multi-hop) |

This document is the bridge: it's *what users said*, mapped to *what we
already built*. A Moto PM should be able to read it in five minutes,
match each user-want to a module, and walk away with a 12-month
roadmap.
