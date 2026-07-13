---
source_url: https://sre.google/prodcast/transcripts/sre-prodcast-01-03/
source_type: docs
title: "Effective alerting on SLOs with Amelia Harrison (SRE Prodcast S1E3)"
author: "Amelia Harrison (Google SRE, AutoAlert), interviewed by MP English and Viv on the SRE Prodcast"
date_published: 2022-03-31
date_extracted: 2026-07-13
last_checked: 2026-07-13
status: current
confidence_overall: settled
issue: "#36"
---

# Effective alerting on SLOs with Amelia Harrison (SRE Prodcast S1E3)

> A primary-source Google SRE practitioner account of *when and how to alert* —
> the monitoring/alerting timing split, the 48-hour urgency heuristic for paging
> vs. ticketing, the "alerting as a service" vision with centralized data-driven
> threshold tuning, the failure of generalized anomaly detection for alerting,
> the "implicit SLO" concept, and the "alert-threshold rot" pattern. Foundational
> SRE alerting practice; zero AI/LLM content, so all AI extensions below are the
> Miner's analytical work connecting classic alerting to AI-agent monitoring.

## Source Context

- **Type**: docs (an official Google SRE podcast transcript published on
  sre.google). It is a verbatim conversation — host MP English and co-host Viv
  interview Amelia Harrison — so it reads as a discussion, but it is hosted as
  SRE documentation and is mined here for its operational claims.
- **Author credibility**: Amelia Harrison works on **AutoAlert**, Google's
  internal service that does alerting *as a service* across Google. She is
  therefore speaking from direct ownership of a large-scale, centralized
  alerting system, not as a commentator. The hosts (MP English, Viv) are
  practicing Google SREs. This is a primary-source practitioner account of the
  highest credibility for SRE alerting practice.
- **Scope**: Covers the design of alerting specifically — distinguishing
  alerting from monitoring, the service-specific vs. infrastructure-level split,
  when to alert (how early), the implicit-SLO concept, what an "alert" is
  (pages/tickets/email), the 48-hour paging heuristic, alerting-as-a-service,
  the failure of generalized anomaly detection, and alert-threshold rot. Does
  NOT cover: any AI/LLM operations, concrete code/config artifacts, dashboards,
  or metrics other than the illustrative "two 9s vs four 9s" example. This is
  transcript-level mining of S1E3, the episode the `docs-google-sre-prodcast.md`
  index note (S1E3 → Ch10 Practical Alerting) points to.

## Extracted Claims

### Claim 1: Monitoring is asynchronous (pull: you go look at dashboards), while alerting is synchronous (push: timing matters and you must be told when something is actionable)
- **Evidence**: Amelia's opening definition of the two concepts, contrasting
  pull-based monitoring with push-based, time-sensitive alerting.
- **Confidence**: settled
- **Quote**: "monitoring is fundamentally asynchronous: at any point as a service
  owner, you should be able to go look at some graphs, some dashboards, and
  answer questions that might arise about your service. On the other hand,
  alerting is synchronous, so timing really matters."
- **Our assessment**: A clean, canonical statement of the monitoring-vs-alerting
  timing distinction. Directly reusable as the Ch02 framing for "alerting is for
  action, monitoring is for understanding." Settled — it is the standard Google
  SRE position and is consistent with the SRE Book's *Practical Alerting* (Ch10).

### Claim 2: Alerting has two layers — service-specific coverage (user journeys, SLOs) and an infrastructure-level "alerting as a service" for common building blocks (storage, load balancers, probes)
- **Evidence**: Amelia describes the "two sides to this coin": service owners
  thinking about user journeys and SLOs, versus common infrastructure resources
  that should come pre-wired with alerting "as a service."
- **Confidence**: settled
- **Quote**: "there's a sort of infrastructure level of alerting that ideally is
  somewhat service-independent... if you are using common infrastructure
  resources, like database storage or load balancers, or if you're using a common
  probing solution, then by virtue of using those resources, ideally you'll have
  sort of 'alerting as a service' set up for those resources to let you know when
  things go wrong"
- **Our assessment**: This is the seed of the alerting-as-a-service thesis that
  recurs throughout the episode. The split is sound: ride-along alerting for
  shared infrastructure removes the burden of every team re-deriving failure
  modes for the same building block. Relevant to Ch02/Ch04 as a pattern for
  shared-platform reliability.

### Claim 3: When to alert is failure-mode-dependent — catch issues before user impact when reasonable (e.g., approaching storage quota), but for dependency-caused outages you often cannot catch them pre-impact
- **Evidence**: Amelia's answer to "when is too early?" — she calls it
  "controversial," acknowledges the purist view ("if you're alerting before you
  have a user issue, it's too early"), but argues pre-impact alerting is
  reasonable for some failure modes and infeasible for others (especially
  external dependencies).
- **Confidence**: settled
- **Quote**: "If you're alerting before you have a user issue, it's too early. I
  mean, ideally we'd like to avoid all outages, which is why, for example,
  alerting when you are approaching storage quota is a reasonable thing to do."
  and "There are certain failure modes that you can reasonably expect to catch
  before they impact users, but there are others where that's a less reasonable
  expectation."
- **Our assessment**: A nuanced, correct position that resists a universal rule.
  The storage-quota example is the canonical "lead indicator" case. The
  dependency-caused-outage caveat is important and often overlooked: pre-impact
  alerting is bounded by what your service can actually observe. Useful for Ch04
  as a guardrail against over-promising on pre-emptive alerting.

### Claim 4: "Implicit SLOs" arise from real user behavior — when many users repeatedly use a path that normally works, an unstated expectation forms, and because it was never explicitly defined it is hard to get alerting coverage for
- **Evidence**: Amelia's response to MP's story of a client-side crash that
  "lurked in our data all along" — she generalizes it into the implicit-SLO
  concept.
- **Confidence**: settled
- **Quote**: "even if you haven't explicitly set an SLO on a certain way that a
  user interacts with your service— if a bunch of people are doing it and it's,
  like, normally working, then there is an implicit sort of expectation there.
  There's almost an implicit SLO, right? And I guess that these can be the ones
  that are issues— these implicit SLOs are the ones that can be really hard to
  get ahead of because you haven't explicitly defined an objective for the
  service with respect to that interaction."
- **Our assessment**: A genuinely useful, named concept. Implicit SLOs are the
  gap between what you declared and what users came to expect; they are exactly
  the failure modes that evade static alerting. This is novel to our corpus and
  directly transferable to AI-agent monitoring (see Guide Impact).

### Claim 5: An "alert" is any monitoring-generated notification (page, ticket, email, chat) — the delivery channel is secondary; a paging alert must be both urgent AND actionable by the responder
- **Evidence**: Amelia reframes "alert" as an umbrella term, then states the
  hard requirement for the paging subset.
- **Confidence**: settled
- **Quote**: "I don't think of alerts as just being pages, but I think of them as
  being any automation generated—so any automatic monitoring-generated
  notifications. It could be bugs. It could be emails. It could be pages."
  and "if you have a paging alert, it's really important that it be urgent and
  that it be actionable. So reflecting an issue that needs to be addressed
  quickly, and that can be addressed by the person who's responding."
- **Our assessment**: Refines the Treynor alerts/tickets/logs taxonomy
  (see Cross-References) by adding the *urgent AND actionable* acceptance test
  for paging specifically. The "actionable by the person who's responding" clause
  is the one most often violated in practice (pages that require info the
  responder doesn't have). Strong, reusable guidance for Ch04.

### Claim 6: The 48-hour heuristic decides paging vs. ticketing — if an alert that fires Friday 5pm cannot wait until Monday without becoming a major outage, it should page; urgent means "can't wait the weekend," not "this minute"
- **Evidence**: Amelia's answer to Viv's paging-vs-ticket question: the team's
  rule of thumb is the 48-hour reaction window.
- **Confidence**: settled
- **Quote**: "if this alert fires on Friday evening at 5pm, will you have enough
  time to react and prevent it from becoming a major outage in the next 48 hours?
  Like, is it actually okay if it waits till Monday? So you need that 48-hour
  window... if it's less than 48, then it probably should be paging because it
  can't wait the weekend, essentially."
- **Our assessment**: This is the single most operational, reusable heuristic in
  the episode and the highest-value extraction for Ch04. It resolves the
  page-vs-ticket ambiguity with a concrete test ("can it wait the weekend?").
  Note it deliberately decouples "urgent" from "immediate" — a page can tolerate
  a few hours, not a weekend. Excellent decision rule to put in front of on-call
  designers.

### Claim 7: Existing pager load is a conditioning variable — if an on-call rotation is already high-load, adding preemptive "will break in N hours" alerts to the pager may not make sense; fix reliability to bring the load down instead
- **Evidence**: Amelia's caveat that alerting decisions are "service-dependent"
  and that high existing pager load argues against piling on preemptive pages.
- **Confidence**: settled
- **Quote**: "If your on-call rotation includes a whole bunch of different
  services and the load is very high, then it might not make sense to add these
  sort of preemptive, 'nothing is broken right this moment, but it will be broken
  in 36 hours if nobody takes any action.' It might not make sense to add those
  to the pager load... there's some more fundamental rethinking of how to increase
  the service reliability to bring down the pager load so that you can catch those
  things earlier."
- **Our assessment**: An important guardrail against the naive "add more pages"
  reflex. Pager load is a budget; preemptive pages compete with it. The prescribed
  remedy (reduce load by improving reliability) is the correct long-term move.
  Directly relevant to Ch04 (on-call/toil) and a useful counterweight to any
  "more alerting = more safety" instinct.

### Claim 8: Email alerts are where alerts go to die — email/chat-based monitoring that requires a human to poll is effectively non-functional
- **Evidence**: MP and Amelia's exchange on email alerting ("email filter hell").
- **Confidence**: settled
- **Quote**: "I feel like email alerts are where alerts go to die." / "They might
  as well not exist, probably."
- **Our assessment**: Corroborates and sharpens Treynor's critique of
  email-based monitoring (Cross-References). The mechanism: email pushes the
  triage decision back onto a human who must poll a mailbox, which does not
  scale. Reusable as a Ch04 anti-pattern: don't route actionable signal to email.

### Claim 9: Per-team manual threshold tuning is not data-driven — each team re-explores the same threshold "parameter space" and cannot leverage other teams' learning to converge on good alerting
- **Evidence**: Amelia's description of the "painfully familiar" current state:
  set up alerts, find them noisy, tune, miss an outage, add sensitivity, repeat —
  independently per team.
- **Confidence**: settled
- **Quote**: "individually exploring the threshold space, you know, the parameter
  space for an individual alert, we're not able to make really data-driven
  decisions about what good alerting looks like. And we're not able to leverage
  other people going through the same exercise to sort of converge on good
  alerting."
- **Our assessment**: Names the core inefficiency alerting-as-a-service is meant
  to solve: threshold tuning is currently localized and non-convergent. This is
  the problem statement for the centralized approach in Claim 10/11. Relevant to
  Ch02/Ch04 as the rationale for shared alerting infrastructure.

### Claim 10: The "alerting as a service" vision — service owners set SLOs/SLIs and a centralized service handles threshold tuning and parameter detail to uphold those objectives
- **Evidence**: Amelia's "perfect alerting system" sketch: you set objectives,
  the service does the tuning using cross-service visibility.
- **Confidence**: emerging
- **Confidence note**: The vision is presented as aspirational ("a foothold,
  moving in the right direction"), so the *claim that this is achievable/desirable*
  is settled among Google SRE, but the *maturity of the realized system* is
  emerging.
- **Quote**: "you have alerting as a service and you're able to set various SLOs
  for your service, but beyond that, you don't really have to think about the
  details or tune the parameters for the alerting to make sure that you're able
  to uphold those SLOs. That can be handled separately by the alerting service,
  right? And that service will have visibility into alerting across a whole bunch
  of different services and, as a result, is able to leverage all of the data
  that you get from that sort of high-level visibility."
- **Our assessment**: The central thesis of the episode and of Amelia's AutoAlert
  work. The "centralized service tunes thresholds using cross-service data" model
  is the natural analog for how a centralized AI-evaluation/harness layer could
  tune agent behavior across services (see Guide Impact). Confidence is emerging
  for the realized system, settled for the desirability of the pattern.

### Claim 11: A centralized alerting service handles common failure modes (e.g., monitoring-data blips, time-series-database drops) once, instead of every team rediscovering them
- **Evidence**: Amelia gives the concrete example of false positives caused by
  monitoring-pipeline failures (dropped data, export-server outages) that page
  everyone — and argues a central team fixes the root cause once.
- **Confidence**: settled
- **Quote**: "When you have a centrally-provided alerting as a service, then that
  team has the resources to think about that common failure mode and make sure
  that the alerts that they're developing are robust to it. Versus every single
  team having to discover that for themselves and then tune all of the alerts or
  make modifications to all of the alerts that they own to make them robust to
  this monitoring failure mode."
- **Our assessment**: A concrete, persuasive argument for centralization: the
  *monitoring system's own* failure modes are shared and should be solved once.
  Transfers cleanly to AI-agent observability — agent-framework/telemetry
  failures are shared and belong in a central platform, not per-team rework.

### Claim 12: Alert thresholds rot — an alert written years ago may have meaningless thresholds; if too loose you silently miss big problems, and if the service improved (two 9s → four 9s) but alerts stayed at two 9s, regressions go unnoticed until users complain
- **Evidence**: MP's "alert I wrote three years ago" worry, and his concrete
  two-9s-to-four-9s regression scenario; Amelia agrees.
- **Confidence**: settled
- **Quote**: "you launch your service and you're like, 'okay, we're gonna start
  at two 9s' and you launch your service and you set up everything for two 9s and
  then you spend the next year working on availability improvements. And now
  you're running at four 9s but your alerting is still stuck at two 9s and now
  users have come to who expect four 9s and now your alert's not gonna fire until
  it's really bad."
- **Our assessment**: Names a pervasive, under-discussed failure mode —
  threshold/sensitivity drift as the service evolves. This is the alerting analog
  of "context rot" in AI-agent configs (see Guide Impact). Directly relevant to
  Ch02/Ch04 as a maintenance obligation: alert SLOs must be recalibrated as the
  service's real SLO improves.

### Claim 13: Generalized anomaly detection for alerting does not generally work — metrics are not created equal, and most anomalies are noise that leads to "wild goose chases" and distraction
- **Evidence**: Amelia states what "doesn't work" based on Google's experience
  with AutoAlert, and explains the mechanism (unequal metrics, inherent signal
  noise).
- **Confidence**: settled
- **Quote**: "generalized anomaly detection for alerting doesn't generally work...
  metrics are not created equal, right? There are important service level
  indicators that really tell you something about the overall service health, and
  then there's a whole bunch of other metrics that may be useful for monitoring
  that you're probably retaining somehow, but anomalies— they are likely to just
  lead to wild goose chases and be a distraction."
- **Our assessment**: A strong, evidence-backed claim that directly counters the
  common "just alert on anomalies" intuition. The mechanism — only curated SLIs
  carry signal, the rest is distraction — is the same reasoning behind the
  evaluation/golden-dataset discipline in the guide's AI source notes (see Guide
  Impact). Novel to our corpus; high value for Ch02.

### Claim 14: Service-owner input on which metrics matter is irreducible — there is no one-size-fits-all solution and you cannot get away from owners identifying and instrumenting the health indicators they care about
- **Evidence**: Amelia's close: even with good anomaly detection and AaaS, the
  owner must specify what matters.
- **Confidence**: settled
- **Quote**: "you'll never really get away from the need for service owners to
  have input about what they care about, right? Like, service owners identifying
  the important metrics that really reflect the health of the service... in
  general, not a one-size-fits-all solution to that problem."
- **Our assessment**: An important limit on automation hubris — the semantic
  mapping from "what users care about" to "which SLIs to watch" stays a human
  responsibility. For AI-agent monitoring this means: a platform can tune
  thresholds, but the *definition* of agent health still needs the service owner.
  Pairs with Claim 4 (implicit SLOs): owners must make implicit expectations
  explicit.

## Concrete Artifacts

### The 48-hour paging decision rule (verbatim heuristic)

```
Test:  Alert fires Friday 5pm.
Q:      Can you react and prevent a major outage in the next 48 hours?
        Is it OK to wait until Monday?
If < 48h to the problem  → PAGE (it can't wait the weekend)
If >= 48h / can wait      → TICKET (or handle in normal flow)
"urgent" ≠ "this minute"; urgent = "cannot wait the weekend."
```
— Amelia Harrison, SRE Prodcast S1E3 (transcript lines ~112)

### The "alerting as a service" two-layer model (paraphrase of Amelia's framing)

```
Layer 1 — Service-specific alerting (owner responsibility):
  • Identify critical user journeys
  • Set user-centric SLOs / specify SLIs
  • Ensure alerting coverage for those journeys

Layer 2 — Infrastructure "alerting as a service" (central platform):
  • Common building blocks (storage, load balancers, probing)
  • Centrally tuned thresholds using cross-service visibility
  • Robust to shared monitoring-pipeline failure modes (one fix, all teams)
  • Can suggest SLO/SLI adjustments from observed behavior
```

### The threshold-rot scenario (verbatim example)

```
Launch at two 9s  → alerting configured for two 9s
Improve to four 9s → alerting still stuck at two 9s
Users now expect four 9s
→ alert won't fire until it's "really bad"
→ you find out about the regression from users, not monitoring
```
— Amelia Harrison / MP English, SRE Prodcast S1E3

### Implicit-SLO formation (verbatim)

```
If many users repeatedly use a path that normally works,
an unstated expectation forms ("almost an implicit SLO").
Because it was never explicitly defined as an objective,
it is hard to get alerting coverage for — and hard to get ahead of.
```

## Cross-References

- **Corroborates**:
  - **discussion-google-sre-ben-treynor-interview.md (Claim 4)** — Treynor's
    alerts/tickets/logs taxonomy. Amelia's episode *operationalizes* that
    taxonomy: her 48-hour heuristic (Claim 6) is the concrete rule for drawing
    the alerts-vs-tickets line Treynor asserts, and her "email alerts are where
    alerts go to die" (Claim 8) sharpens Treynor's critique that "requiring a
    human to read the email and decide whether something needs to be done ... is
    a mistake." No conflict — Amelia extends Treynor's three categories with the
    judgment calls for applying them.
  - **docs-google-sre-prodcast.md (Claim 5, Claim 4)** — that index note stated
    transcripts would be mined separately and that S1E3 → Ch10 Practical Alerting
    (guest Amelia Harrison). This note *is* that deeper mining; it fills the
    structural pointer with the actual claims.

- **Contradicts**: None. No claim in this transcript opposes any claim in an
  existing source note. The one terminological difference — Treynor treats
  "alerts" as one of three disjoint categories (alerts/tickets/logs), while
  Amelia uses "alert" as an umbrella covering pages/tickets/emails — is a
  *conditioning variable* (scope of the word), not a contradiction: Amelia's
  paging-vs-ticketing split maps directly onto Treynor's alerts-vs-tickets, and
  her "logs = never an alert" is implicit in both. No contradiction issue is
  filed.

- **Extends**:
  - **discussion-google-sre-ben-treynor-interview.md** — Provides the missing
    *operational detail* behind Treynor's foundational taxonomy: the 48-hour
    page/test (Claim 6), the urgent-AND-actionable page criterion (Claim 5), and
    the high-pager-load guardrail (Claim 7). Where Treynor defines the three
    categories, Amelia supplies the engineering judgment for drawing the lines.
  - **docs-google-sre-prodcast.md** — Converts the index's S1E3 pointer into
    substantive claims; together they let the Smith cite both "episode exists /
    maps to Ch10" (index) and "here are the specific alerting practices" (this
    note).

- **Novel** (new to the corpus):
  - The **48-hour paging heuristic** (Claim 6) — a concrete, named decision rule
    for page-vs-ticket that no existing note contains.
  - The **"implicit SLO"** concept (Claim 4) — user-behavior-created unstated
    expectations; absent from the corpus.
  - The **"alerting as a service"** centralized-tuning model (Claims 2, 10, 11)
    — distinct from the Treynor taxonomy; a platform-owns-tuning pattern.
  - The **failure of generalized anomaly detection for alerting** (Claim 13) —
    no existing note makes this claim; it is a useful counter to the common
    anomaly-alerting intuition.
  - The **alert-threshold-rot** pattern (Claim 12) — thresholds drift as the
    service's real SLO improves; the alerting analog of AI "context rot."
  - The **irreducibility of service-owner input on SLIs** (Claim 14) — a limit
    on full automation of alerting.

## Guide Impact

> NOTE: This source contains **zero AI/LLM content**. The SRE alerting claims
> below are cited directly from the transcript (settled, primary-source Google
> SRE practice). Every AI/LLM extension is the Miner's analytical synthesis and
> should be reviewed by the Smith for fidelity — flagged explicitly as such.

- **Chapter 02 (Observability / Alerting)**: Add a "when to alert / page vs.
  ticket" subsection built on Amelia's claims:
  1. **The monitoring-vs-alerting timing split** (Claim 1) as the definitional
     opener: monitoring = pull/async for understanding, alerting = push/sync for
     action.
  2. **The 48-hour paging heuristic** (Claim 6) as the concrete page-vs-ticket
     decision rule — "can it wait the weekend?" This is the highest-value,
     directly adoptable artifact.
  3. **The urgent-AND-actionable page criterion** (Claim 5) — a page must be
     both.
  4. **Anomaly-detection caveat** (Claim 13) — generalize anomaly detection does
     not work for alerting; alert on curated SLIs, not raw anomalies. This
     corroborates the evaluation/golden-dataset discipline already in the AI
     notes and gives Ch02 a non-AI grounding for it.

- **Chapter 04 (On-call and Toil)**:
  1. **Pager-load as a budget** (Claim 7) — do not add preemptive pages to an
     already-high-load rotation; reduce load by improving reliability. Use as a
     guardrail against alert-sprawl toil.
  2. **Email alerts are dead** (Claim 8) — anti-pattern; route actionable signal
     to paging/ticketing, never email.
  3. **Alert-threshold maintenance obligation** (Claim 12) — recalibrate alert
     SLOs as the service's real SLO improves, or regressions evade detection.
     Frame this as recurring toil that AaaS / centralized platforms can absorb.

- **Cross-cutting (AI in SRE) — Miner's synthesis, for Smith review**:
  1. **Centralized agent-tuning analog** (Claims 10–11): Just as AutoAlert
     centrally tunes alert thresholds using cross-service data, a centralized
     AI-evaluation/harness layer could tune agent behavior across services rather
     than each team hand-tuning prompts per agent. This extends the
     PagerDuty/incident.io "shared platform" theme with a concrete SRE precedent.
  2. **Implicit SLOs for agents** (Claim 4): Users develop unstated expectations
     of an AI agent's behavior from real usage; monitor actual agent interaction
     patterns to surface these implicit SLOs before they become outages.
  3. **Agent "anomaly" alerts need curated SLIs** (Claim 13): Generic anomaly
     detection on agent traces would be a "wild goose chase"; alert on curated
     agent-health SLIs (tool-call success, hallucination rate) — exactly the
     evaluation discipline the existing AI notes advocate.
  4. **Agent alert-threshold rot** (Claim 12): As an agent/system improves, its
     alert thresholds (e.g., "escalate if error rate > X%") rot just like SRE
     alert thresholds; this is the alerting analog of the "context rot" pattern
     in blog-pagerduty-production-ai-agent-gaps and should be called out as a
     maintenance obligation for production AI agents.

## Extraction Notes

- The source is a single transcript page on the official sre.google domain
  (`/prodcast/transcripts/sre-prodcast-01-03/`, title "Effective alerting on
  SLOs with Amelia Harrison"). Fetched via `curl` (68 KB HTML), scripts/styles
  stripped, and converted to plain text (153 lines). The full transcript was read
  end-to-end — no skimming. It is a short, single-topic episode (one speaker,
  Amelia Harrison), so the whole thing is within scope.
- **`date_published`**: The page carries `data-release-date="2022-03-31"` (the
  same series/index date used by `docs-google-sre-prodcast.md`). Season 1 of the
  Prodcast aired in 2021; individual episode air dates are not published on the
  transcript page, so 2022-03-31 is the verifiable page-metadata date and is
  approximate for the episode itself. Flagged here for the Smith to refine.
- All `Quote` fields were copied character-for-character from the extracted
  transcript text (lines cited in the artifact block). Spot-check against the
  live URL. The only non-verbatim passages are the structured "Concrete Artifacts"
  models, which are the Miner's faithful paraphrase of Amelia's framing and are
  labeled as such.
- No part of the source was paywalled; the transcript is publicly accessible.
- This note is the transcript-level mining of S1E3 that the `docs-google-sre-prodcast.md`
  index note anticipated (its Claim 5). It does not re-extract the index's
  structural facts; it extends them with the episode's specific alerting claims.
- No contradiction issue was filed: the only terminological difference from the
  Treynor interview (alert-as-umbrella vs. alert-as-category) is a conditioning
  variable, not an opposition, per MINER.md §4a.
