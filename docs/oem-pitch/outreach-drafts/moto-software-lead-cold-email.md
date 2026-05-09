# Cold email — Moto / Lenovo MBG software lead

**Target:** A named software / AI lead on the Moto AI team (Catch-Me-Up,
Pay-Attention, Remember-This).

### Ranked targets (verified May 2026 via public LinkedIn search)

| # | Name | Title | LinkedIn | Why this person |
|---|---|---|---|---|
| 1 | **Mahmoud Ebrahim** | VP, MBG Software Development at Motorola Mobility (Lenovo) | <https://linkedin.com/in/mahmoudebrahim> | His own LinkedIn bio names *"Moto AI — our next-gen AI platform"* as a key achievement. Direct decision-maker. Roselle, IL. **PRIMARY.** |
| 2 | **Thomas Gitzinger** | Director & Principal Engineer, Innovation and Architecture at Motorola Mobility | <https://linkedin.com/in/thomas-gitzinger-94a61912> | Innovation/architecture remit — closest engineering counterpart. Libertyville, IL. **TECH-FIRST FALLBACK.** |
| 3 | **Eric Niu** | Distinguished Staff Engineer & Tech Leader at Motorola Mobile Devices | <https://linkedin.com/in/eric-niu-aa316318> | Distinguished engineer level; Sunnyvale, CA — useful if you want a US west-coast technical opinion. |
| 4 | **Edward Benyukhis** | Director, SW/FW Engineering, Platform Software (Android products) at Motorola | (search by name on LinkedIn) | Owns the Platform Software layer where AOL would integrate. Strong fit if Mahmoud's calendar is closed. |
| 5 | **Robert Yesudass Divya** | Engineering Lead SME at Motorola Mobility | <https://linkedin.com/in/robertydivya> | IC-level lead; useful only as a *referral source* into the org, not as a primary recipient. |

**Send order:** **Mahmoud first.** If no reply within ~2 weeks (14 days), send follow-up #1 to Mahmoud and a *fresh first-touch* to Thomas Gitzinger on the same day. If neither replies by ~4 weeks (28 days), pivot to OnePlus / Nothing per [`../solo-founder-to-moto.md`](../solo-founder-to-moto.md). **Do not** send to all five at once — Moto is a relatively small org and they will see the cross-CC.

*Typical title pattern to confirm: Director / Sr. Director of Software Engineering, Mobile AI; Principal Engineer, Mobile AI; VP, MBG Software Development.*

**Send window:** A Tuesday, **4:00–5:00 PM IST**. Tuesday is the day VPs
clear inbox backlog from Monday and reply same-day; 4–5 PM IST is
mid-morning US Central (Mahmoud's tz).

**Pick 1–2 leads from `oem-targets.md` and send to them first.** Do
**not** mass-blast. One quality send beats five generic sends.

---

## Cold email — primary version (3 sentences, ≤ 120 words)

> Subject: Moto AI memory — the persistence + routing layer it's missing (90-sec demo)

> Hi Mahmoud,
>
> The Catch-Me-Up / Pay-Attention / Remember-This surface in Moto AI
> is the right product direction — it's the persistence underneath
> that's currently missing (sessions don't carry, signals don't
> reinforce). I built **Second Brain** — a memory + routing layer
> that plugs into the OEM AI assistant and (a) keeps Catch-Me-Up
> coherent across sessions, (b) routes ~45% of inferences on-device
> per call, (c) ships as a 131-line MVP integration shim (AIDL +
> Kotlin). At Moto's 14.5 M phones / quarter that's ~$1.6 M/yr in
> cloud-AI bills before counting battery + churn.
>
> Live demo: <https://out-ujjsjvxm.devinapps.com> ·
> Per-feature mapping at Moto's scale:
> <https://github.com/Akshu1245/Secondbrain/blob/main/docs/oem-pitch/moto-specific.md> ·
> Repo + buildable APK: <https://github.com/Akshu1245/Secondbrain>.
>
> Solo founder — demo, API, Android shim, and 53-test pytest suite
> are end-to-end deployed before this email.
>
> Worth 15 minutes on the calendar?
>
> Best,
> **K S Akshay** · Founder, Rashi Technologies
> `rashisolutions1245@gmail.com` · <https://linkedin.com/in/k-s-akshay-0707a42b6>

*If sending to a different target from the table above, change "Mahmoud" to that recipient's first name. **Do not** keep "Mahmoud" if you're sending to Thomas / Eric / Edward.*

---

## LinkedIn DM version (≤ 300 chars — fits the connection-request limit)

> Hi Mahmoud — built Second Brain, the persistence + routing layer
> the Catch-Me-Up / Remember-This surface is missing. ~45% of calls
> on-device, 131-LOC AIDL shim, live demo + buildable APK:
> out-ujjsjvxm.devinapps.com ·
> github.com/Akshu1245/Secondbrain. Worth 15 min? — Akshay

(287 chars including spaces. Drop "+ an AIDL stub for Android in &lt;150
LOC" if your target's profile suggests they'd rather see the product
side first.)

---

## Follow-up #1 (send only if no reply ~14 days after the original)

> Subject: Re: 90-second demo — the missing memory + optimisation layer for Moto AI

> Hi Mahmoud,
>
> Bumping this once. The demo is still up at
> out-ujjsjvxm.devinapps.com and I added an OEM-pain audit that maps
> Reddit / press complaints 1:1 onto the fixes:
> <https://github.com/Akshu1245/Secondbrain/blob/devin/1777538026-aol-pitch/docs/oem-pitch/user-pain-audit.md>
>
> If now isn't the right time, who on the Moto AI team would you
> recommend I reach? Happy to send the 1-pager instead of a meeting.
>
> Best,
> Akshay

(Avoid "just checking in." The follow-up adds *new value* — a sourced
audit doc — so it isn't a nag.)

---

## Follow-up #2 (send only if no reply ~28 days after the original, then stop and move to OnePlus / Nothing)

> Subject: Last note — open-sourcing the Moto-AI optimisation layer

> Hi Mahmoud,
>
> Last note from me — I'm planning to open the discussion with OnePlus
> / Nothing in the next 2 weeks since Moto's the natural first home
> for this. Final ask: 15 minutes on the calendar this week or next?
> If a hard no — totally fine, I'll leave you alone after this.
>
> Demo still live: out-ujjsjvxm.devinapps.com.
>
> Best,
> Akshay

---

## Why these specific words

* **Subject line ≤ 60 chars** — Gmail truncates beyond that on mobile.
  The "90-second demo" framing pre-commits a small ask.
* **Sentence 1: name a *specific* gap they ship.** "Remember-This
  doesn't persist" is the most-complained-about Moto AI bug per the
  pain audit. Showing you know the surface is the credibility shortcut.
* **Sentence 2: link the demo + the AIDL stub immediately.** No "I've
  attached a deck." Decks are time-asks. Demo + repo is a 30-sec
  glance.
* **Sentence 3: solo founder, ships fast — show, don't tell.** Use
  end-to-end shipped artefacts (demo, API, APK, tests) as the credential.
  No fabricated counts, no patent claims that don't apply to this product.
* **CTA: "15 minutes" not "a meeting."** Specific small ask converts
  ~3× higher on cold outbound.
* **No "I'm passionate about AI" or "I admire your work at Moto."**
  Both are spam-flag phrases. Show, don't tell.

---

## Personalisation checklist before sending

- [ ] **Picked: Mahmoud Ebrahim** (VP MBG Software Development — Moto
      AI is named in his own bio). If you'd rather avoid VPs and go
      Director-level technical, switch to Thomas Gitzinger (#2 above)
      and replace "Mahmoud" with "Thomas" everywhere.
- [ ] Replace recipient name *only if changing from Mahmoud* (Lenovo /
      Moto culture is first-name in email).
- [ ] Confirm the demo URL <https://out-ujjsjvxm.devinapps.com> is
      still live the morning of send. (It's deployed on Devin Apps —
      free tier; if it's down, redeploy from the dashboard.)
- [ ] Confirm the repo URL <https://github.com/Akshu1245/Secondbrain>
      is public (it is) and that the README on `main` leads with the
      Second Brain headline (it does).
- [ ] (Optional) Confirm the LinkedIn URL
      <https://linkedin.com/in/k-s-akshay-0707a42b6> resolves to your
      profile.
- [ ] Run `bash docs/oem-pitch/DEMO-WARMUP.sh` 2-3 minutes before
      sending to wake the free-tier hosts.
- [ ] **Do not CC anyone.** Single recipient. If you want a second
      person in the loop, send a separate email — never CC on the
      first send.

---

## Where to find the email vs. the LinkedIn DM

* **Email** is preferred if you can find it. Tools: Hunter.io free
  tier (5 lookups/month), Apollo.io free tier, or just guess
  `firstname.lastname@motorola.com` / `@lenovo.com` (Moto = Motorola
  Mobility, owned by Lenovo).
* **LinkedIn DM** is the fallback if no email and you don't have a
  Sales Navigator account. Send a *connection request with a note* —
  the note field accepts ~300 chars (see DM version above).
* **InMail** (paid LinkedIn) only if you already have Premium. Don't
  pay just for one send.
