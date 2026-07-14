---
source_url: https://sre.google/prodcast/transcripts/sre-prodcast-04-02/
source_type: docs
title: "The One With Data Centers and Peter Pellerzi (SRE Prodcast S4E2)"
author: "Peter Pellerzi (Distinguished Engineer, Google — physical infrastructure / construction team), with host Steve McGhee and co-host Matt Siegler (Google SRE Prodcast)"
date_published: 2025 (approximate; Season 4 episode — page carries no explicit publication date; mining occurred 2026-07-14)
date_extracted: 2026-07-14
last_checked: 2026-07-14
status: current
confidence_overall: emerging
issue: "#84"
---

# The One With Data Centers and Peter Pellerzi (SRE Prodcast S4E2)

> A practitioner primary source on the *physical-infrastructure* side of SRE: data-center
> scale, the community-based incident-response model for power outages (Chile case study),
> disaster testing that actually fails things off (DiRT / ISON), the limits of MTTR/MTBF at
> fleet scale, and Google's seven-year ML/DeepMind cooling-plant optimization (15–40% PUE
> savings with a two-hour weather look-ahead).

## Source Context

- **Type**: docs (podcast transcript — SRE Prodcast Season 4, Episode 2)
- **Author credibility**: High for practice. Peter Pellerzi is a Google Distinguished
  Engineer assigned to the construction team, an electrical engineer by training who builds
  Google's substations, electrical, and cooling infrastructure ("we're the ones who
  physically pour the concrete"). He states 25+ years in the data-center industry
  (IBM before Google). The cooling-ML and liquid-cooling claims are presented as first-hand
  program history, not second-hand. This is the authoritative Google-SRE voice on physical
  infrastructure, not a casual mention.
- **Scope**: A wide-ranging conversation about physical data-center operations — scale and
  community siting; on-site staffing vs automation; incident response for power outages
  (Chile); real-world fuel-logistics testing; DiRT/ISON disaster testing; power-density and
  the shift to liquid cooling; ML/DeepMind cooling optimization; and the meaning of
  MTTR/MTBF/availability at fleet scale. It does NOT cover software-side SRE practices
  (coding, CI/CD, alerting pipelines) except insofar as the physical layer feeds them.
- **Novelty in corpus**: This is the only transcript-level source on *physical-infrastructure*
  incident response and disaster testing. The AI/LLM content is narrow and, per the triage,
  largely a re-telling of Google's long-public DeepMind cooling story (published years ago) —
  so it is corroborating, not novel, on the AI point, but the *verbatim specifics* (predictive
  weather with a two-hour look-ahead, 15–40% PUE range, real-time + predictive data fusion)
  are worth pinning down. The data-center IR and DiRT/ISON practices are new to the corpus.
  `docs-google-sre-prodcast.md` lists S4E2 in its Season 4 catalog but **omits it from the
  AI-episode table** (lines 294–296 list only S4E3/S4E4/S4E9/S4E10) — this note supplies the
  missing transcript-level detail and flags the omission.

## Extracted Claims

### Claim 1: Google uses ML (built with DeepMind) to optimize data-center cooling plants, achieving roughly 15–40% PUE reduction by fusing real-time device/operating data with *predictive* weather data on a ~2-hour look-ahead
- **Evidence**: Peter describes a multi-year collaboration with DeepMind (London): "they came
  up with this ML approach to say, look, we can not only take all the inputs from all these
  devices and find an optimal running point for each one, but we can also take predictive
  weather data." He states the savings range and the mechanism (anticipating weather two
  hours out to pre-emptively adjust refrigeration vs fans/pumps). Steve confirms it dropped
  the PUE rating overall.
- **Confidence**: emerging
- **Quote**: "I think it was between 15% and 40%, if I recall." / "they came up with this ML approach to say, look, we can not only take all the inputs from all these devices and find an optimal running point for each one, but we can also take predictive weather data." / "I can make adjustments now based on what the weather will be two hours from now." / "it starts to turn down the refrigeration because it anticipates the weather two hours from now."
- **Our assessment**: The public DeepMind cooling-optimization story is well established (the
  triage flags it as known since publication years ago), so the *existence* claim is
  corroborating, not novel. What is useful here is the verbatim, practitioner-level detail:
  a *control/optimization* ML system (not failure detection) that closes the loop using a
  predictive weather feed two hours ahead, trading refrigeration for fan/pump speed. That
  distinguishes it from `docs-google-sre-prodcast-03-03-treynor-ai-ml.md` Claim 7 (ML for
  *electrical-failure detection* in data centers) — same family ("ML applied to physical
  data-center ops"), different job. The 15–40% range is given as a recollection ("if I
  recall"), so treat the upper bound as anecdotal; the lower bound is the safer cite.

### Claim 2: Physical-infrastructure incident response runs on a "don't strand anyone" community model — an immediate global video bridge (facility managers + SRE), no one left alone, coordination by judgment not playbook
- **Evidence**: Peter describes the standing protocol for any failure: "we open up a video
  chat immediately, a common video chat between anybody who wants to get on. But usually,
  it's between facility managers, SRE, and so on... we never strand someone at a data center
  and say, well, you're on your own, see what you can do." Support is global ("You'll have
  SRE London, you'll have SRE-- everybody will chime in"). He frames the differentiator as:
  "Things will break everywhere. It's how you deal with the break. That's the
  differentiator."
- **Confidence**: emerging
- **Quote**: "we open up a video chat immediately, a common video chat between anybody who wants to get on. But usually, it's between facility managers, SRE, and so on... So we never strand someone at a data center and say, well, you're on your own, see what you can do. Not at all. And this is the differentiator, we behave like a community." / "Things will break everywhere. It's how you deal with the break. That's the differentiator, at least what I've seen here at Google."
- **Our assessment**: This is the highest-value *novel* contribution of the episode: a
  physical-infrastructure mirror of the software IR norms the corpus already documents. It
  directly corroborates `docs-google-sre-prodcast-03-06-incident-response-tooling.md` Claim 3
  ("if the on-caller needs your help, you drop what you're doing and help the on-caller") and
  `docs-google-sre-prodcast-01-08-incident-management.md` Claim 12 (cross-team/multi-pager
  coordination via a common protocol) — here extended to cross-*site* physical coordination.
  The "community, not playbook" emphasis is consistent with incident-management Claim 13
  (internalize best practices as habits so responders don't rely on looking up a playbook).
  We buy it; it is practitioner-account evidence (anecdotal in the formal sense) but
  internally coherent and consistent with the rest of the corpus.

### Claim 3: For a countrywide outage with no written procedure, success comes from empowered people making adaptive calls ("get a hold of refueling, let's start refueling right away") rather than a script
- **Evidence**: The Chile case study — the entire country lost power; Google had multiple
  data centers there and experienced no outage. Peter: "what's the strategy when you have a
  countrywide outage? You don't have that written down anywhere, but you have enough people
  with enough authority to say, yeah, why don't you get a hold of refueling? Let's start
  refueling right away, because we don't know how long this is going to last." Steve calls it
  "cooperative adaptation."
- **Confidence**: emerging
- **Quote**: "we had multiple data centers down there, and they lost power through the whole country. So what's the strategy when you have a countrywide outage? You don't have that written down anywhere, but you have enough people with enough authority to say, yeah, why don't you get a hold of refueling? Let's start refueling right away, because we don't know how long this is going to last."
- **Our assessment**: A concrete incident-response vignette showing the doctrine from Claim 2
  under real load. Useful for the guide's Ch04 as evidence that *preparedness + empowered
  responders* beats a playbook for novel, large-blast-radius events. Steve's parallel
  anecdote (a pre-built spreadsheet of "how many fuel trucks in flight" that "totally saved
  the day") reinforces "know your capabilities" as the durable prep. We buy it as a
  well-told, credible account.

### Claim 4: Disaster testing must be *real* — DiRT simulates failures, but ISON actually shuts things off ("we actually fail things off... this is where we walk the talk")
- **Evidence**: Peter defines both: DiRT is "simulated failures... What happens if this goes
  really bad? How do we recover the customers, the data"; ISON is "where we actually fail
  things off. We actually shut things off and say, what happens if this shuts off? But
  basically, it's a real shut off. And this is where we walk the talk." Steve links it to
  software "chaos testing."
- **Confidence**: emerging
- **Quote**: "DiRT is simulated failures." / "ISON testing is where we actually fail things off. We actually shut things off and say, what happens if this shuts off? But basically, it's a real shut off. And this is where we walk the talk."
- **Our assessment**: A physical-infrastructure articulation of chaos engineering — novel to
  the corpus, which otherwise treats chaos/DiRT only in software-failure terms. The key
  insight ("we actually shut things off") is a strong, quotable mandate for real (not just
  simulated) failure injection. Consistent with the guide's testing culture but adds the
  *physical* dimension (utilities, generators) and the motivation Peter gives: "we never want
  to run on diesel generators... so even more important to actually test it because it's
  something you don't do very often, which means, oh, it'll be fine. Really, it won't be
  fine." We buy it.

### Claim 5: The math of real-world logistics lies — offloading a 7,200-gallon fuel truck is capped at 300 gallons/minute, and the offloading time (plus hose/setup/security) was far longer than the back-of-envelope estimate assumed
- **Evidence**: Peter challenges listeners to do real-world testing and recounts: "We learned
  that the most you can get out of a truck is 300 gallons per minute. That's it. That's all
  they can pump... You have to drain 7,200 gallons out of that truck at 300 gallons per
  minute, max." And: "that doesn't include setup time with the hoses, connection,
  disconnection, clean up, chocking the tires on the truck, getting the drive-- none of that
  was included, and we were very surprised at how long it took."
- **Confidence**: emerging
- **Quote**: "We learned that the most you can get out of a truck is 300 gallons per minute. That's it. That's all they can pump." / "You have to drain 7,200 gallons out of that truck at 300 gallons per minute, max." / "that doesn't include setup time with the hoses, connection, disconnection, clean up, chocking the tires on the truck, getting the drive-- none of that was included, and we were very surprised at how long it took."
- **Our assessment**: A vivid, concrete artifact (a mini failure-report embedded in the
  interview) for the "test against reality, not the spreadsheet" lesson. Steve's framing —
  "the math... you can do enough math and just totally convince yourself, and then it hits
  reality" — is a reusable teaching line for Ch05's testing culture. The numbers are specific
  and quotable; we buy them as a first-hand account. This is the episode's cleanest
  "don't trust the model, test the system" example.

### Claim 6: MTTR/MTBF are weak at fleet scale because failures are novel and non-normal, so Google optimizes for *availability* (99.999%) via fault-tolerant design + a robust spare-parts program + vendor partnerships that exploit fleet-scale failure data
- **Evidence**: Steve opens the critique: "they like to cite MTTR and MTBF... those numbers
  actually aren't meaningful to us because it's not a large, homogeneous set of components
  that all have similar failure domains or failure modes that we actually have novel
  failures. So like treating this as it's not a normal distribution." Peter agrees the layered
  metric that matters is "availability, 99.999, whatever, five nines of availability. That's
  our target," reached by minimizing failures + fast MTTR, enabled by fault tolerance,
  spares, and better-than-vendor data: "if you have 600 of anything, and you have a 0.001
  failure rate, we're going to lose one every two years." Steve: "at Google scale, a million
  to one odds happens all the time."
- **Confidence**: emerging
- **Quote**: "they like to cite MTTR and MTBF... those numbers actually aren't meaningful to us because it's not a large, homogeneous set of components that all have similar failure domains or failure modes that we actually have novel failures. So like treating this is not a normal distribution." / "the metric that we look at is availability, 99.999, whatever, five nines of availability. That's our target." / "We have a very, very robust spare parts program so that if something fails, A, we can recover very quickly using a fault tolerant design, and then B, we have the spare part in hand." / "if you have 600 of anything, and you have a 0.001 failure rate, we're going to lose one every two years."
- **Our assessment**: Steve's critique corroborates `docs-google-sre-prodcast-03-06-incident-response-tooling.md`
  Claim 15 ("the field is moving away from MTTR as the single be-all metric, toward richer
  insights"). Note the nuance Peter adds: at the *component* layer MTTR/MTBF still earn their
  keep (you can't hit five-nines without fast repair), but the differentiator is designing
  failures out and pre-positioning spares — i.e., the corpus's recurring "prevention >
  response" theme (incident-management Claim 10: "do as little incident response as
  possible"). The fleet-scale-data point ("we have better data than the manufacturers... they
  don't have a concentrated pool of equipment that we have") is a genuinely novel, concrete
  argument for vendor collaboration. We buy it.

### Claim 7: Air cooling hits a hard thermal limit at higher chip densities, forcing direct-to-chip liquid cooling (water has ~3,000× the heat capacity of air per volume); Google invested ~7 years ahead of the curve to perfect it
- **Evidence**: Peter: "You're going to reach a thermal limit. You simply cannot get the heat
  out of that integrated circuit using the traditional aluminum heat sink and a fan." On the
  fix: "you're going to pump cold water in one side and out the other, and remove that heat
  using water, which has 3,000 times the heat capacity as air does per volume." On lead time:
  "We've spent the last seven years, a lot of really good, sharp people spending a lot of
  sweat perfecting this." Foundational constraint stated as physical law: "Power goes in,
  does work, work turns into heat. That's the way it goes."
- **Confidence**: emerging
- **Quote**: "You're going to reach a thermal limit. You simply cannot get the heat out of that integrated circuit using the traditional aluminum heat sink and a fan." / "remove that heat using water, which has 3,000 times the heat capacity as air does per volume." / "We've spent the last seven years, a lot of really good, sharp people spending a lot of sweat perfecting this."
- **Our assessment**: Context-setting for the guide's AI-infrastructure chapter rather than a
  process claim. The density→liquid-cooling shift is what makes AI chips (NVIDIA GPUs)
  physically runnable, so it is relevant background for any "reliability of AI compute"
  guidance. The "plan 4–5 years ahead" leadership lesson ("you need to look four or five
  years ahead of time") reinforces the forward-looking-investment theme. Lowest direct
  guide-relevance of the claims, but useful as infrastructure context. The 3,000× figure is a
  memorable, quotable anchor.

## Concrete Artifacts

Fuel-truck offload math (verbatim from Peter's account; S4E2 transcript):

```
Truck capacity:   7,200 gallons (full tanker)
Max pump rate:    300 gallons / minute  (MAX — "That's all they can pump")
=> Pump time:     ~24 minutes of pure transfer (7,200 / 300), BEFORE:
   - hose connection / disconnection
   - setup time
   - clean up
   - chocking the tires on the truck
   - getting the driver
   - getting the truck in/out of the gate through security
Peter: "we were very surprised at how long it took."
Lesson: back-of-envelope fuel-burn math omitted offloading + overhead; only
        real-world testing exposed it.
```

Chile refueling prep (Steve's parallel anecdote; S4E2 transcript):

```
A pre-built spreadsheet tracked "how many trucks needed to be in flight at any
given time to keep [the generators] going" — knowing round-trip time to the fuel
depot vs tank-empty time. "That spreadsheet totally saved the day." The point:
you don't predict the exact outage, you "know your capabilities... what you can
do" — i.e., inventory your "shed of possibilities" before the incident.
```

Cooling-ML control loop (verbatim mechanism; S4E2 transcript):

```
Inputs:  all device/operating data (real time)  +  predictive weather data
Look-ahead: ~2 hours ("I can make adjustments now based on what the weather
             will be two hours from now")
Action:  find optimal setpoint per device; pre-emptively trade refrigeration
         (chiller) for fan/pump speed as weather is anticipated to cool
Result:  15-40% PUE reduction (Peter: "between 15% and 40%, if I recall")
Built with: DeepMind (London) collaboration, "several years" in production
```

Availability / fleet-scale arithmetic (verbatim; S4E2 transcript):

```
Target:       99.999% ("five nines of availability")
Enablers:     fault-tolerant design  +  robust spare-parts program
              +  vendor partnerships leveraging Google's fleet-scale failure data
Fleet math:   "if you have 600 of anything, and you have a 0.001 failure rate,
              we're going to lose one every two years"
Scale remark: "at Google scale, a million to one odds happens all the time"
```

## Cross-References

- **Corroborates**:
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` **Claim 3** ("if the
    on-caller needs your help, you drop what you're doing and help the on-caller" — the
    community-help norm). S4E2's "we never strand someone... we behave like a community"
    (Claim 2) is the *physical-infrastructure* embodiment of that same norm.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` **Claim 15** ("the field
    is moving away from MTTR as the single be-all metric, toward richer insights"). Steve's
    MTTR/MTBF critique (Claim 6) is a direct, on-record endorsement of exactly that shift.
  - `docs-google-sre-prodcast.md` (index note) — this episode (S4E2) is part of the Season 4
    corpus the index tracks; this note fills the transcript-level gap the index left for it.
- **Extends**:
  - `docs-google-sre-prodcast-03-03-treynor-ai-ml.md` **Claim 7** (ML in production for
    *electrical-failure detection* in data centers). S4E2 adds a second, distinct in-production
    ML data-center deployment — *cooling-plant optimization/control* (Claim 1) — same family
    ("ML applied to physical data-center ops"), different job. Together they broaden the
    corpus's evidence that Google runs ML on the physical plant, not just on software telemetry.
  - `docs-google-sre-prodcast-01-08-incident-management.md` **Claim 12** (cross-team /
    multi-pager incidents coordinated via the common protocol). S4E2 extends this to
    *cross-site physical* coordination (global video bridge, countrywide-outage refueling).
  - `docs-google-sre-prodcast-01-08-incident-management.md` **Claim 10** ("do as little
    incident response as possible" — prevention > response). Peter's availability strategy
    (fault-tolerant design + spares, Claim 6) is the physical-infra version of that thesis.
- **Contradicts**: None. Steve's MTTR/MTBF critique is consistent with (not opposed to)
  incident-response-tooling Claim 15; the episode does not dispute any existing source note.
  No contradiction issue was filed. (Note: the index note *omits* S4E2 from its AI-episode
  table at lines 294–296 — that is a cataloging gap, not a contradiction.)
- **Novel**:
  - First transcript-level treatment of **physical-infrastructure incident response**
    (community video bridge, "don't strand anyone," countrywide-outage refueling) — prior IR
    notes are software-side only.
  - First source documenting **DiRT (simulated) + ISON (actual shut-off) disaster testing**
    as a physical-infrastructure chaos-engineering practice.
  - Concrete **fuel-offload failure vignette** (7,200 gal @ 300 gpm + overhead) as a
    "math ≠ reality" testing lesson — no equivalent artifact elsewhere in the corpus.
  - Verbatim specifics of the **DeepMind cooling system**: predictive-weather 2-hour
    look-ahead, 15–40% PUE range, real-time+predictive data fusion (the public story is
    known; these specifics are now pinned to a primary-source quote).

## Guide Impact

- **Chapter 04 (Incident Management)**: Add a physical-infrastructure IR pattern — the
  "don't strand anyone" global video bridge and empowered, playbook-free coordination for
  novel large-blast-radius events (Claims 2–3). This complements the software-side IR norms
  the chapter already cites (incident-response-tooling Claim 3; incident-management Claim 12)
  and gives the "community, not playbook" doctrine a concrete, high-stakes example. Also add
  the MTTR/MTBF caveat (Claim 6, corroborating incident-response-tooling Claim 15): at fleet
  scale, optimize for availability via fault tolerance + spares + vendor fleet-data, not just
  repair time.
- **Chapter 05 (Automation & Toil)**: Add the cooling-plant ML case (Claim 1) as a concrete,
  in-production example of ML *optimizing* (not just detecting) infrastructure — a useful
  counterpoint to the failure-detection framing in treynor-ai-ml Claim 7. Add DiRT/ISON real
  failure-injection (Claim 4) and the fuel-offload "test against reality" lesson (Claim 5) to
  the testing-culture material. The liquid-cooling density shift (Claim 7) is useful
  background if/when the guide develops an AI-compute-reliability section.
- **Chapter 02 (SRE Fundamentals / metrics)**: The MTTR/MTBF-vs-availability discussion
  (Claim 6) reinforces the corpus's move away from MTTR as the be-all metric; cite S4E2
  alongside incident-response-tooling Claim 15.

## Extraction Notes

- Source is a full podcast transcript (563 lines of extracted text; ~40 KB HTML). Read end to
  end. No sub-pages were followed — this is a single self-contained transcript page.
- The page carries no explicit publication date; `date_published` is estimated as a Season 4
  episode (circa 2025), consistent with the sibling S4E7 note's handling.
- Per the triage, the AI/LLM content is narrow and largely re-tells Google's public DeepMind
  cooling story; I extracted the verbatim specifics anyway (they are the durable, citable
  part) but flagged the public/known status in Claim 1's assessment so the Smith doesn't
  over-weight novelty. The genuinely novel material is the physical-infrastructure IR and
  DiRT/ISON testing content (Claims 2–5).
- No contradiction surfaced; §4a of MINER.md did not trigger, so no contradiction issue was
  filed. The index note's omission of S4E2 from its AI-episode table (lines 294–296) is a
  cataloging gap for the Smith/index to revisit, not a contradiction.
