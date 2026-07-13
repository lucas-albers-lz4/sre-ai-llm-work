---
source_url: https://sre.google/prodcast/transcripts/sre-prodcast-01-04/
source_type: discussion
title: "Rethinking SLOs with Narayan Desai (SRE Prodcast S1E4)"
author: "Narayan Desai (Uber Tech Lead, Google Cloud Platform data-analytics reliability), interviewed by Viv and MP (Prodcast hosts)"
date_published: 2022-03-31
date_extracted: 2026-07-13
last_checked: 2026-07-13
status: current
confidence_overall: emerging
issue: "#37"
---

# Rethinking SLOs with Narayan Desai (SRE Prodcast S1E4)

> A primary-source Google SRE practitioner critique of canonical SLOs at B2B
> cloud scale. Narayan Desai argues SLOs/error budgets — designed for Google's
> aggregate B2C core (Search/Gmail) — break at GCP scale with differentiated,
> paying customers and wide API surfaces; he proposes a "stationarity" model of
> reliability (availability + correctness + performance-consistency over time)
> and a performance-distribution "surprise detector." Directly relevant to the
> guide's SLO/error-budget material (Ch00) and to framing reliability targets
> for AI agents (Ch05); it is the transcript-level mining the prodcast index note
> anticipated for S1E4 ("entirely refram[es] the topic").

## Source Context

- **Type**: discussion (podcast transcript / interview published on the official
  Google SRE site). Season 1 Episode 4 of the SRE Prodcast, a chapter-by-chapter
  walkthrough of the SRE Book (S1E4 → Ch4 Service Level Objectives).
- **Author credibility**: Narayan Desai is a Google SRE **Uber Tech Lead (UTL)**
  responsible for the reliability of GCP's data-analytics products (BigQuery and
  similar). He states "I've been at Google for about five years. And prior to
  that, I did a lot of work in high performance computing." He is therefore
  speaking from direct ownership of large-scale, multi-tenant, B2B cloud
  reliability — the exact regime in which he argues canonical SLOs fail. The
  hosts (Viv, MP) are the Prodcast's regular hosts. This is a named,
  senior-practitioner primary account from the organization that originated SRE
  — high credibility for *how SLOs actually behave at cloud scale*, though it is
  a single practitioner's view, delivered conversationally, and partly
  speculative on the proposed replacement framework.
- **Scope**: Focuses narrowly on *the limitations of SLOs/error budgets and what
  to do instead*. Covers: why SLOs were designed for aggregate B2C reliability,
  why error budgets are "problematic" for paying B2B customers, why SLOs fail on
  wide API surfaces and performance, the need to analyze errors/performance
  discretely, SLO skepticism + narrow-SLO guidance, SLOs as a stale
  point-in-time "normal," the SLO-proliferation / "always out of SLO" /
  "page-someone-to-death" failure mode, B2B-vs-B2C differences and request
  weighting, circular SLO definitions, the proposed "stationarity" definition of
  reliability (availability + correctness + performance-consistency), variance as
  a core property and the "surprise detector" analytics, the errors≈performance
  insight, and the difficulty of measuring correctness.
- **Does NOT cover**: concrete code, config, dashboards, or SLO math; any
  AI/LLM operations (pre-LLM-era source). The proposed replacement analytics are
  described conceptually, not implemented or benchmarked — Desai explicitly says
  his team's primary work "has been focused on errors and performance" and that
  the correctness strategies are "spitballed." The AI/LLM relevance is indirect
  — it supplies the *SLO-skeptic* counterweight the guide needs when it sets
  reliability targets for AI agents, and a *stationarity/drift* framing that
  maps onto agent-reliability monitoring.

## Extracted Claims

### Claim 1: SLOs were designed for Google's historical core B2C businesses (Search/Gmail) that could only afford to approach reliability in the aggregate, not targeting individual users — and that aggregate model breaks at GCP B2B scale where every customer must have a good experience
- **Evidence**: Desai's opening framing of the "business scenario that SLOs were
  designed in," contrasting it with GCP's situation where "each of our customers
  counts on us to provide infrastructure that they use to build their businesses"
  and "all of them need to have a good experience." He notes customers "don't
  necessarily have the same value to the business."
- **Confidence**: settled
- **Quote**: "if you think about the business scenario that SLOs were designed in,
  Google's historical core businesses were very large, had large numbers of
  customers, and could only afford to approach reliability in the aggregate,
  right? Not necessarily targeting individual users of high scale services like
  Search or Gmail."
- **Our assessment**: This is the foundational scope-boundary claim of the
  episode and it is sound: SLOs are an *aggregation* tool, and aggregation
  silently averages away the experience of individual (especially high-value)
  customers. For the guide, this is the key caveat on the canonical error-budget
  view (see Cross-References → Contradicts conditioning variable): SLOs work
  where the population is homogeneous and the "average user" is representative,
  and degrade where it is not. It is exactly the argument the customer-centric
  monitoring note makes from the measurement side.

### Claim 2: Error budgets built on top of SLOs are "problematic" in B2B because no paying customer wants to be "in the error budget"
- **Evidence**: Desai extends the scope argument to error budgets specifically:
  "no one wants to be in the error budget, and it's understandable, right?
  They're paying money for a service that they depend on." He concludes "it's
  been tricky to apply SLOs uniformly across GCP."
- **Confidence**: settled
- **Quote**: "these core notions, like error budgets and so forth that are built
  on top of SLOs, end up being kind of problematic, right? Because no one wants
  to be in the error budget, and it's understandable, right? They're paying money
  for a service that they depend on."
- **Our assessment**: This directly challenges the canonical error-budget
  mechanism (Treynor interview, Claim 3/9) — but only at B2B/paying-customer
  scale, which is the conditioning variable MINER.md §4a excludes from
  contradiction filing (see Cross-References). The insight is real and
  under-discussed: error budgets assume the *customer* is comfortable sharing the
  risk with the provider; a paying B2B customer who depends on the service to run
  their own business is not. For AI agents this maps to: don't model a critical
  agent journey's reliability as a shared "budget" the customer is expected to
  tolerate — they won't.

### Claim 3: SLOs struggle to provide meaningful performance insight for services with a wide API surface and a wide range of customer workloads (e.g., GCE as a "data center in a box")
- **Evidence**: Desai contrasts core Google services' "pretty narrow" use cases
  with GCE, which is "basically a data center in a box" with "a really large API
  surface, there's a large number of degrees of freedom that customers have,"
  on top of which customers "build very, very, very complex workflows."
- **Confidence**: settled
- **Quote**: "SLOs really struggle to provide meaningful insights when you need to
  analyze the performance delivered by a service with a wide range of workloads
  that customers might request from you."
- **Our assessment**: A sharp, generalizable point: SLOs are a *rate* abstraction
  (fraction of bad outcomes) and rate abstractions lose information about *which*
  workload or *which* API operation is failing. For AI agents, an aggregate
  "agent success rate" SLO hides which journey/tool path is degrading — the same
  averaging-away problem at smaller scale. Reinforces the per-journey-SLO
  guidance from the customer-centric monitoring note (Claim 15).

### Claim 4: Errors and performance should be analyzed discretely; SLOs are much better at analyzing errors than performance
- **Evidence**: Desai's first recommendation when asked how to fill the SLO gap:
  "it's worth considering errors and performance discretely… It's a lot easier to
  analyze errors using SLOs than it is to analyze performance using SLOs."
- **Confidence**: settled
- **Quote**: "I think that it's worth considering errors and performance
  discretely, right? It's a lot easier to analyze errors using SLOs than it is to
  analyze performance using SLOs."
- **Our assessment**: Useful decomposition. Errors are naturally binary
  (success/fail) and fit SLO rate math; performance is a *distribution* and
  collapses badly into a single threshold. This is the conceptual seed of his
  later "take variance seriously" argument (Claim 16) and the
  errors≈performance synthesis (Claim 18). For agent monitoring: track
  agent *correctness/hallucination* (binary-ish, SLO-friendly) separately from
  agent *latency/distribution* (needs the variance treatment).

### Claim 5: Be skeptical of claims that SLOs solve everything — multiple use cases built on the same SLOs are not guaranteed to be compatible
- **Evidence**: Desai critiques SLO over-adoption: "you'll frequently see people
  saying that they're actually useful for everything… I personally think this is
  pretty problematic, because there's no guarantee that multiple use cases that
  you try to build on top of the same SLOs will be compatible."
- **Confidence**: settled
- **Quote**: "there's no guarantee that multiple use cases that you try to build
  on top of the same SLOs will be compatible, right?"
- **Our assessment**: A healthy anti-dogma point. For the guide this is a
  standing caveat whenever it recommends "set an SLO for your agent": one SLO
  cannot safely serve multiple, differently-shaped questions. Pairs with the
  alerting note's Claim 14 (no one-size-fits-all; owners must specify what
  matters).

### Claim 6: Make SLOs as narrow as possible — each should answer a single question well rather than answer many questions poorly
- **Evidence**: Desai's second recommendation: "try to make these SLOs as narrow
  as possible so that they can be used to answer a single question well, as
  opposed to answering a variety of questions sort of poorly." He adds "I'm a big
  believer in the need for high fidelity insights."
- **Confidence**: settled
- **Quote**: "try to make these SLOs as narrow as possible so that they can be
  used to answer a single question well, as opposed to answering a variety of
  questions sort of poorly."
- **Our assessment**: The practical mitigation Desai offers for the SLO skeptics.
  Narrow SLOs are the operational bridge between his critique and the canonical
  view — they preserve the SLO tool while escaping the "answer everything poorly"
  trap. For AI agents this is the per-journey / per-tool-call SLO guidance (one
  SLO per question: "does the agent execute the rollback tool correctly?", not
  "is the agent good?").

### Claim 7: SLOs are a point-in-time approximation of "normal" derived from a historical window, and they go stale as the system changes
- **Evidence**: Desai describes how SLOs are usually set: "an expert in the
  system will go and examine the delivery performance of the system over some
  historical window… and then say, 'Oh, well, for this API operation, usually
  it's some number of nines… should finish in less than 500 milliseconds.'" He
  calls this "a point-in-time approximation of normal" and gives the 30%/400ms
  example below.
- **Confidence**: settled
- **Quote**: "imagine your source system speeds up by 30%. Now the estimate that
  you have normal at 500 milliseconds for 99.99% of requests is suddenly off
  because 99.99% of requests should actually only take 400 milliseconds now."
- **Our assessment**: This is the *drift* half of the SLO problem (the other half
  is proliferation, Claim 9). The "normal" a threshold encodes is a snapshot; the
  system evolves and the threshold silently lies. This is the SLO analog of the
  alerting note's "alert-threshold rot" (Claim 12) and of the AI-agent "context
  rot" pattern — Desai explicitly says you need "a verification step" to re-examine
  the data over time.

### Claim 8: Three top recommendations for using SLOs: be skeptical, be very specific about the question you're answering, and validate/iterate over time so estimates still fit real behavior
- **Evidence**: Desai's synthesized advice: "be skeptical. Be very specific about
  the questions that you're trying to answer, and then validate and iterate over
  time to make sure that your estimates still make sense and fit the way that the
  system behaves. Because you don't want a de-tuned alert, or an overly aggressive
  alert."
- **Confidence**: settled
- **Quote**: "So the three top things that I would recommend are: sort of be
  skeptical. Be very specific about the questions that you're trying to answer,
  and then validate and iterate over time to make sure that your estimates still
  make sense and fit the way that the system behaves."
- **Our assessment**: The episode's actionable core. The "validate and iterate"
  step is precisely what the customer-centric monitoring note calls "monitoring
  as continuous verification" (Claim 7) and what the alerting note encodes as
  "validate your monitoring like unit tests" (Claim 9) and threshold
  recalibration (Claim 12). All three Google SRE practitioner notes converge on:
  SLOs/alerts are hypotheses that must be re-verified, not set-and-forget.

### Claim 9: The SLO maintenance lifecycle is underdeveloped, causing SLO proliferation — one internal Google service has ~250,000 parameterized SLOs
- **Evidence**: Desai and MP discuss the maintenance burden; Desai: "we have one
  service internal to Google, that has— it may have grown since the last time I
  spoke with this particular team, but they have about a quarter million
  parameterized SLOs." He frames this as "SLO proliferation, right? You end up
  with more and more SLOs."
- **Confidence**: settled (the anecdote is his direct account; the precise count
  is approximate and may have grown)
- **Quote**: "we have one service internal to Google, that has— it may have grown
  since the last time I spoke with this particular team, but they have about a
  quarter million parameterized SLOs."
- **Our assessment**: A striking, concrete data point that anchors the
  proliferation argument. The "quarter million parameterized SLOs" figure is the
  single most citable artifact in the episode and a strong illustration of why
  "narrow SLOs" (Claim 6) without a maintenance discipline explodes. For the
  guide, this is the cautionary scale at which per-journey agent SLOs would also
  blow up without central platform support (cf. the alerting note's
  "alerting as a service," Claim 10).

### Claim 10: With SLO proliferation you are "always out of SLO"; paging on every out-of-SLO state "pages someone to death," and the incentives drive teams to make SLOs less aggressive
- **Evidence**: Desai: with that many SLOs "you're always out of SLO. What does
  that mean?… How do you combine those signals together into something that's
  meaningful?" On paging: "if you're gonna page someone whenever you're out of
  SLO, and you have even a moderate… service that has little hundreds of SLOs,
  you will page someone to death if you use SLOs in that way." He adds "there are
  a lot of reasonable incentives that cause people to make their SLOs less
  aggressive, as well."
- **Confidence**: settled
- **Quote**: "if you're gonna page someone whenever you're out of SLO, and you have
  even a moderate—like, let's forget the quarter million case here for a minute—
  and you just have a service that has little hundreds of SLOs, you will page
  someone to death if you use SLOs in that way, right?"
- **Our assessment**: This is the operational failure mode of SLO proliferation and
  it corroborates the alerting note's Claim 7 ("existing pager load is a
  conditioning variable… don't pile preemptive pages onto a high-load rotation")
  from the *SLO* side: too many SLOs = too many pages = desensitized on-call =
  weaker SLOs. The guide should treat "page someone to death" as the canonical
  anti-pattern for both alert sprawl and SLO sprawl.

### Claim 11: SLOs codify expectations but incorporate no flexible model of service behavior, producing brittle representations with unclear maintenance cadence and low precision
- **Evidence**: Desai: "SLOs kind of codify what is expected, but it doesn't
  incorporate any model of what the service behavior should be that's flexible in
  any way. So you end up with these very brittle representations of what
  performance should look like." He adds you never have "good confidence of where
  you are" because you don't know the maintenance cadence.
- **Confidence**: settled
- **Quote**: "SLOs kind of codify what is expected, but it doesn't incorporate any
  model of what the service behavior should be that's flexible in any way. So you
  end up with these very brittle representations of what performance should look
  like."
- **Our assessment**: The architectural critique: an SLO is a *static number*, not
  a *model* of expected behavior. This is the precise gap his proposed "stationarity"
  model (Claim 15–16) is meant to fill. For AI agents, a static "95% success" SLO
  is equally brittle — it encodes no model of *what correct agent behavior looks
  like*, so it can't tell a benign change from a regression.

### Claim 12: There is a radical difference between B2B and B2C for SLOs — the high-level problem (limited reliability resources, where to spend them) is identical, but the specifics differ
- **Evidence**: MP raises that the concerns "arise most in the case of a cloud
  provider that's indirect, like a more B2B… instead of B2C." Desai: "I would
  definitely say the details are different. I definitely think that there is a
  really radical difference between B2C and B2B." He then says "from that
  50,000 foot perspective, the problems are exactly the same whether you're doing
  B2B or B2C" (limited reliability resources, where to engage on-call/incident
  response).
- **Confidence**: settled
- **Quote**: "I would definitely say the details are different. I definitely think
  that there is a really radical difference between B2C and B2B."
- **Our assessment**: The scoping statement that reframes the whole episode as a
  *conditioning variable* rather than a wholesale rejection of SLOs. This is the
  hinge of the (non-filed) tension with the Treynor canonical view: Treynor's
  error budget was described for Google's aggregate core (effectively B2C);
  Desai critiques it for B2B. Same tool, different population — exactly the
  MINER.md §4a "use X for small / Y for large" exclusion. No contradiction issue
  is filed (see Cross-References).

### Claim 13: In B2B the canonical SLO calculation (failed requests ÷ total requests) must be replaced by weighting — not all requests are equally important, and alternative normalizations yield different insights
- **Evidence**: Desai: the "quintessential SLO calculation is to take all the
  requests that you had, and count up the number of them that failed and divide
  that by the number of requests that were there." In B2B: "you need to start
  considering these questions of: what sort of weighting do you wanna use? Do you
  want to consider all requests the same? Do you wanna consider some requests to
  be more important?"
- **Confidence**: settled
- **Quote**: "In B2B, you need to start considering these questions of: what sort
  of weighting do you wanna use? Do you want to consider all requests the same?
  Do you wanna consider some requests to be more important?"
- **Our assessment**: This is the B2B extension of the customer-centric monitoring
  note's Claim 3 ("who is observing those errors? Is this user a critical user?")
  and Claim 15 (different workflows need different latency/accuracy tolerances).
  Where Esparrachiari argues *measure* the long tail, Desai argues *weight* the
  requests. Together they imply: a flat error ratio is invalid for differentiated
  customers — you must weight by customer/journey criticality. For AI agents,
  weight by journey criticality (a failed trivial query ≠ a failed
  production-incident remediation).

### Claim 14: Canonical SLO definitions are circular — "a service is reliable if it meets its SLOs, and meets its SLOs if it's reliable" — producing a self-referential mess; instead define reliability from first principles
- **Evidence**: Desai: "we've ended up with these circular definitions where your
  service is reliable if it meets its SLOs. And a service meets its SLOs if it's
  reliable, right? And then you sort of pick some arbitrary sort of numerical
  thresholds for that, and you end up with this self-referential mess." He
  advocates starting "from the ground up" with a core definition of reliability.
- **Confidence**: settled
- **Quote**: "we've ended up with these circular definitions where your service is
  reliable if it meets its SLOs. And a service meets its SLOs if it's reliable,
  right? And then you sort of pick some arbitrary sort of numerical thresholds for
  that, and you end up with this self-referential mess."
- **Our assessment**: A precise philosophical critique. The circularity is real:
  SLOs are often *defined* as the reliability target and then *cited* as evidence
  of reliability. The guide must avoid this when it sets AI-agent reliability
  targets — "the agent is reliable because it passes its eval; it passes its eval
  because it's reliable" is the same trap. Define agent reliability from first
  principles (correctness, availability, latency-consistency — see Claim 15) and
  let the eval/SLO be a *measurement* of it, not its definition.

### Claim 15: Proposed first-principles definition of reliability = stationarity across three dimensions: availability (the service is there when needed), correctness (API contract met), and performance consistency (today ≈ yesterday)
- **Evidence**: Desai's alternative definition: "the definition that we've begun
  to use is a combination of effectively, stationarity… Customers expect that
  they continue to get the service that they got yesterday." He enumerates the
  three dimensions explicitly: availability, correctness ("some API contract for
  the service"), and performance consistency ("if it took roughly 300 milliseconds
  yesterday, it'll probably take about 300 milliseconds today").
- **Confidence**: emerging (a definition his team "has begun to use"; presented as
  a working proposal, not an established standard)
- **Quote**: "the definition that we've begun to use is a combination of
  effectively, stationarity, right? Customers expect that they continue to get the
  service that they got yesterday. And they expect this continuity— or
  stationarity, if you think about it from a statistical perspective— in three
  dimensions. They expect that the service will be available… They expect that
  these results will be correct… And they expect that the performance will be
  consistent…"
- **Our assessment**: This is the episode's most original contribution and the
  strongest bridge to AI-agent reliability. *Stationarity* — "the service I got
  yesterday is the service I get today" — is exactly the property you want from a
  production AI agent: not a fixed 99.9% number, but a *stable distribution* of
  behavior over time. An agent that is correct 95% of the time but whose error
  rate swings weekly is, under Desai's definition, *unreliable* even if its SLO
  number looks fine. This directly informs Ch05 agent-reliability targets.

### Claim 16: Mathematically, reliability is a stationary distribution of delivered performance over time — and variance is a core property that should be taken "more seriously"; a lower-variance service with the same mean is perceived as more reliable
- **Evidence**: Desai: "what you're really looking for is a situation where you can
  make an assertion that the performance that's delivered from a service results
  in a stationary distribution over time." He gives the two-graphs example (level
  low-variance vs. low-mean-with-spikes, same mean) and concludes "the most
  important here is that we need to start taking variance more seriously as a core
  property of our distributed systems."
- **Confidence**: emerging (proposed analytical framing; the two-graph intuition
  is his illustrative example, not a cited study)
- **Quote**: "what you're really looking for is a situation where you can make an
  assertion that the performance that's delivered from a service results in a
  stationary distribution over time, right?"
- **Also**: "one of the things that is the most important here is that we need to
  start taking variance more seriously as a core property of our distributed
  systems."
- **Our assessment**: The single most transferable idea for agent monitoring.
  Variance, not just the mean error rate, is the reliability signal. An AI agent
  whose latency or hallucination rate has a stable low variance is more trustworthy
  than one with the same mean but occasional catastrophic spikes — yet a
  mean-only SLO cannot see the difference. This is the conceptual foundation for
  agent *drift detection* (see Guide Impact, Ch05; cf. the S5E6 Parker Barnes
  "drift detection" theme the index note flags).

### Claim 17: Built performance-distribution analytics as a "customer surprise" detector — break the workload into self-similar pieces and use rates of unlikely events to spot misbehavior that is not a function of customer workload changes
- **Evidence**: Desai: "these are good indicators of customer surprise… if you're
  able to break up your workload into pieces that are self-similar, then many of
  these behave consistently over time and you can use rates of unlikely events to
  spot situations where your service isn't behaving properly, and it is not a
  function of customer changes to their workloads."
- **Confidence**: emerging (describes internal Google analytics his team built;
  presented as working but not benchmarked in the episode)
- **Quote**: "if you're able to break up your workload into pieces that are
  self-similar, then many of these behave consistently over time and you can use
  rates of unlikely events to spot situations where your service isn't behaving
  properly, and it is not a function of customer changes to their workloads."
- **Our assessment**: This is the operationalization of the stationarity idea:
  model expected behavior per self-similar workload slice, then alert on the
  *rate of unlikely events* (distribution shift) rather than on a static
  threshold. It is the SRE-native ancestor of ML model-drift detection and maps
  directly onto monitoring an AI agent's behavior distribution for unexpected
  deviations. Corroborates the alerting note's Claim 13 (generalized anomaly
  detection on raw metrics fails, but curated, model-aware signals work) — Desai's
  "self-similar pieces" are the curation step that makes the signal meaningful.

### Claim 18: Errors and performance are more synonymous than commonly thought — many large outages show performance blips (subsystems slowing) before errors, and a timed-out RPC is just "an RPC that hasn't responded yet"; a large percentage of outages are visible in the performance domain
- **Evidence**: Desai: prior to "large scale mayhem, you often see performance
  blips… there are subsystems or dependencies that start to get slower" and then
  "that bad performance gets helpfully translated into an error for you." He
  states: "what is a timed-out RPC, but an RPC that hasn't responded yet? That's
  sort of a performance problem" and "we have some evidence that you can see a
  really large percentage of your outages in the performance domain."
- **Confidence**: settled (the empirical observation about pre-outage performance
  blips); emerging (the "large percentage" quantification is his team's
  preliminary evidence, not a published figure)
- **Quote**: "what is a timed-out RPC, but an RPC that hasn't responded yet?
  That's sort of a performance problem."
- **Also**: "we have some evidence that you can see a really large percentage of
  your outages in the performance domain."
- **Our assessment**: A genuinely useful reframing with direct incident-response
  value: latency degradation is often the *leading indicator* of an impending
  error/outage, so performance monitoring is not secondary to error monitoring —
  it is upstream of it. For AI agents this is critical: an agent whose tool-call
  latency or reasoning time is creeping up is showing the same pre-failure
  signature; watch the latency *distribution* (Claim 16), not just success/fail.
  This is the incident-early-warning argument the guide's Ch04 should adopt.

### Claim 19: Measuring correctness is "fiendishly hard" and circular (the only way to know a correct response is the system's own behavior); partial strategies exist — checksums for storage, and "running important things twice" via multiple implementations/releases
- **Evidence**: MP: "the only way to know what the response to a given request is
  is the system behavior itself. It's sort of definitional and it gets back to
  that circular logic." Narayan: "Yeah.… correctness is a fiendishly hard
  problem." On strategies: "check sums are an example where you can detect some
  failure modes," and a "wilder idea… is: there is some sort of historical
  precedent for multiple implementations of core logic… running important things
  twice."
- **Confidence**: settled (the difficulty/circularity is asserted by both
  participants); emerging (the "running important things twice" idea is explicitly
  "spitballed," not something his team is doing)
- **Quote**: "MP: In my mind, the only way to know what the response to a given
  request is is the system behavior itself. It's sort of definitional and it gets
  back to that circular logic. Narayan: Yeah."
- **Our assessment**: Honest about the hardest dimension of the stationarity
  definition (correctness). The "running important things twice" idea is a real,
  if expensive, technique with a direct AI analog: run a critical agent action
  through two models/prompts and compare (a form of self-consistency / ensemble
  verification). The guide's Ch05 should cite this as a known-hard problem and a
  candidate verification pattern for high-stakes agent actions — not as settled
  practice.

### Claim 20: SLOs are the simplest possible solution for producing summary statistics about reliability, but much more complex analytics — using models of expected behavior/invariants — will dominate over the next several years
- **Evidence**: Desai's forward look: "SLOs in my mind really represent the
  simplest possible solution to producing summary statistics about the reliability
  of a service, but I see much more complex analytics happening over the next
  several years. And I think that these complex analytics are really gonna tell us
  a lot of very important things." He predicts finding/fixing problems "before
  customers notice them."
- **Confidence**: emerging (explicit prediction/"crystal ball" framing)
- **Quote**: "SLOs in my mind really represent the simplest possible solution to
  producing summary statistics about the reliability of a service, but I see much
  more complex analytics happening over the next several years."
- **Our assessment**: A measured verdict, not a rejection: SLOs are the *floor*,
  not the ceiling. This is the right framing for the guide — present SLOs as a
  useful but insufficient baseline, and layer the stationarity/distribution/drift
  analytics on top for systems (including AI agents) where the average hides the
  thing that matters. This is consistent with the prodcast index note's framing
  that S1E4 "entirely refram[es] the topic" rather than discards it.

## Concrete Artifacts

### The SLO-was-designed-for / breaks-at-GCP scope contrast (Desai's framing)

```
DESIGNED FOR (Google core B2C):
  - very large, many customers
  - reliability approached "in the aggregate"
  - not targeting individual users (Search, Gmail)

GCP B2B REALITY:
  - each customer builds their business on the infra
  - every customer must have a good experience
  - customers have unequal business value
  → aggregate SLOs get "a lot harder"
```

### The "normal is a point-in-time snapshot" example (verbatim scenario)

```
SLO set:   API op should finish in < 500ms for 99.99% of requests
Basis:     expert examines delivery over previous 1-2 months (a snapshot)
Drift:     source system speeds up 30%
Result:    99.99% of requests now take ~400ms, but SLO still says 500ms
→ estimate is "suddenly off"; needs a verification/re-examination step
— Narayan Desai, SRE Prodcast S1E4
```

### The SLO-proliferation anecdote (verbatim scale figure)

```
One internal Google service: ~250,000 parameterized SLOs
("may have grown since the last time I spoke with this particular team")
Consequence: "you're always out of SLO"
Paging:      a service with "little hundreds of SLOs" →
             "you will page someone to death if you use SLOs in that way"
— Narayan Desai, SRE Prodcast S1E4
```

### The proposed "stationarity" definition of reliability (Desai's three dimensions)

```
reliability := stationarity of delivered behavior over time
               ("the service they got yesterday is the service they get today")

  Dimension 1 — AVAILABILITY:
      when they need it, it is there;
      send a request → you respond, not just an error.

  Dimension 2 — CORRECTNESS:
      results are correct; there is "some API contract for the service."

  Dimension 3 — PERFORMANCE CONSISTENCY:
      if an RPC took ~300ms yesterday, it takes ~300ms today.

Mathematical target: delivered performance "results in a stationary
distribution over time" (range/distribution stays self-consistent,
not every request identical).
— Narayan Desai, SRE Prodcast S1E4
```

### The two-graphs intuition (low-variance vs. low-mean-with-spikes, same mean)

```
Graph A: relatively level, very small variance
Graph B: lower trendline, occasional large spikes  (same mean as A)

User perception: A (low variance) is "easier to use" and viewed as
more reliable — even though B has the same mean.
→ "take variance more seriously as a core property of our distributed
   systems."
— Narayan Desai, SRE Prodcast S1E4
```

### The "surprise detector" analytics (Desai's built approach)

```
Break workload into PIECES THAT ARE SELF-SIMILAR
  → each piece behaves consistently over time
Alert on: RATE OF UNLIKELY EVENTS within a piece
  → spots misbehavior "not a function of customer changes to their workloads"
Goal: indicator of "customer surprise" (surprise ≈ bad in this infra)
— Narayan Desai, SRE Prodcast S1E4
```

### The errors≈performance insight (verbatim)

```
Pre-outage signature: subsystems/dependencies "start to get slower"
  → load up, bog down → hit a deadline → bad performance is
    "helpfully translated into an error"
"what is a timed-out RPC, but an RPC that hasn't responded yet?
 That's sort of a performance problem."
Evidence: "you can see a really large percentage of your outages
          in the performance domain."
— Narayan Desai, SRE Prodcast S1E4
```

## Cross-References

- **Corroborates**:
  - `discussion-google-sre-prodcast-customer-centric-monitoring.md` (issue #35) —
    Desai's B2B weighting argument (Claim 13) is the *analytical* counterpart to
    Esparrachiari's measurement argument. Her Claim 3 ("who is observing those
    errors? Is this user a critical user?") and Claim 11 ("five 9s no longer
    assumed to represent all customers… examine the long tail") both assert that a
    flat error ratio misleads for differentiated users; Desai supplies the
    *mechanism* (weight requests; the canonical failures÷total calc is invalid in
    B2B). Her Claim 15 ("one workflow may require lower latency, but not so much
    accuracy… another may require exceptional accuracy but tolerate staleness")
    is the per-journey-specificity Desai reaches via narrow SLOs (Claim 6) and
    self-similar workload slices (Claim 17). No conflict — measurement and
    weighting are complementary halves of the same "averaging hides the important
    user" thesis.
  - `docs-google-sre-prodcast-01-03-alerting.md` (issue #36) — Desai's
    "page someone to death" / always-out-of-SLO failure mode (Claim 10) is the
    *SLO-side* instance of Amelia Harrison's Claim 7 ("existing pager load is a
    conditioning variable… don't pile preemptive pages onto a high-load rotation").
    Desai's "validate and iterate" (Claim 8) and stale-"normal" (Claim 7) are the
    SLO analogs of Harrison's Claim 12 (alert-threshold rot) and Claim 9 (validate
    monitoring like unit tests). And Desai's "surprise detector" using curated,
    model-aware signals (Claim 17) corroborates Harrison's Claim 13 (generalized
    anomaly detection on raw metrics fails; alert on curated SLIs).

- **Contradicts**: None that meets the MINER.md §4a bar — but one *conditioning
  variable* tension must be surfaced prominently. Desai's critique of
  error budgets (Claim 2) and of SLOs as brittle/always-out-of-SLO (Claims 9–11)
  appears to oppose `discussion-google-sre-ben-treynor-interview.md` (issue #17),
  specifically:
    - Treynor Claim 3 — error budgets (1 − availability target) are a shared
      objective mechanism that aligns dev and SRE incentives around launch
      velocity and reliability.
    - Treynor Claim 9 — when the error budget is exhausted, the only reliable
      recovery is a launch freeze.
    - Treynor Claim 8 — the right reliability target "is a product question, not a
      technical question."
  Desai does NOT actually oppose these *in form*; he opposes their *universal
  applicability*. His scope argument (Claim 1, Claim 12) is explicit that the
  problem is B2B/multi-tenant/paying-customer scale with differentiated value and
  wide API surfaces — precisely the MINER.md §4a exclusion: "Claims differ only in
  *context*… that's not a contradiction, that's a conditioning variable."
  Treynor's error budget was described for Google's aggregate core (effectively
  B2C, Search/Gmail), where the average user is representative and the customer
  shares risk; Desai critiques it where the average user is *not* representative
  and the customer won't share the risk. This is the same "evolution, not
  opposition" pattern the corpus already applied to Treynor ↔ Esparrachiari (see
  customer-centric monitoring note, Claim 11 cross-reference). **No contradiction
  issue is filed.** The prodcast index note (`docs-google-sre-prodcast.md`) itself
  flags this in Claim 6 ("SLOs can be problematic," S1E4 "entirely refram[es] the
  topic") as a deviation the Smith should *weigh against* the book's prescriptions
  — i.e., it is an anticipated, documented tension, not a newly-filed one. The
  guide should present SLOs/error budgets with explicit scope boundaries rather
  than as universally valid.

- **Extends**:
  - `docs-google-sre-prodcast.md` (issue #32) — the prodcast *index* note maps
    S1E4 → Ch4 Service Level Objectives and, in Claim 6, singles out this episode
    as the one that "entirely refram[es] the topic" of SLOs. This note *is* the
    transcript-level mining the index anticipated ("the SLOs reframing… would need
    to be extracted from the S1E4 transcript to assess against the guide's SLO
    material"). It supplies the actual claims behind the index's one-line S1E4
    pointer.
  - `discussion-google-sre-ben-treynor-interview.md` (issue #17) — Desai takes
    Treynor's canonical SLO/error-budget foundation (Claims 3, 8, 9) and extends
    it upward: he keeps the "reliability target is a product question" point
    (Treynor Claim 8) but adds *who the customer is* as the decisive variable
    (Claims 12–13), and proposes the "stationarity" first-principles definition
    (Claim 15) as the replacement for the circular SLO definition (Claim 14).
    Treynor supplies *what* an SLO is; Desai supplies *where it breaks and what to
    use instead*.
  - `discussion-google-sre-prodcast-customer-centric-monitoring.md` (issue #35) —
    extends Esparrachiari's long-tail/B2B argument with the *statistical*
    "stationarity" framing (Claim 15–16) and the performance-distribution
    "surprise detector" (Claim 17), moving her philosophical monitoring guidance
    toward an implementable analytics design.

- **Novel** (new to the corpus from this source):
  - The **"stationarity" three-dimensional definition of reliability**
    (availability + correctness + performance-consistency over time) as a
    first-principles replacement for circular SLO definitions.
  - The **circular-SLO-definition critique** ("reliable if meets SLOs; meets SLOs
    if reliable → self-referential mess") — a meta-point no existing note makes.
  - The **~250,000-parameterized-SLO proliferation** anecdote and the
    "always out of SLO" / "page someone to death" failure mode — the single most
    concrete scale data point in the corpus on SLO over-adoption.
  - The **"take variance seriously as a core property"** framing and the
    low-variance-vs-low-mean-with-spikes (same mean) intuition — variance as the
    true reliability signal.
  - The **"surprise detector"** analytics design: self-similar workload slices +
    rate-of-unlikely-events, decoupled from customer-driven workload change.
  - The **errors≈performance synthesis**: pre-outage performance blips and
    "a timed-out RPC is an RPC that hasn't responded yet" — performance monitoring
    as the *upstream* leading indicator of outages.
  - The **B2B-vs-B2C SLO weighting** argument (weight requests by importance in
    B2B; the failures÷total calc is invalid there).

## Guide Impact

> NOTE: This source contains **zero AI/LLM content** (pre-LLM-era). The SRE SLO
> claims below are cited directly from the transcript (primary-source Google SRE
> practitioner account). Every AI/LLM extension is the Miner's analytical
> synthesis and should be reviewed by the Smith for fidelity — flagged explicitly
> as such.

- **Chapter 00 (Principles — SLOs / error budgets)**: This is the needed
  *counterweight* to the canonical error-budget presentation (Treynor interview,
  Claims 3/8/9). Recommend the guide present SLOs/error budgets with **explicit
  scope boundaries**:
  1. State that SLOs/error budgets were designed for *aggregate, homogeneous,
     risk-sharing* populations (Search/Gmail) and **degrade** where the
     population is *heterogeneous, differentiated, and paying* (B2B/multi-tenant)
     — cite Desai Claims 1, 2, 12. This is a conditioning variable, not a
     rejection; present both the canonical view and its boundary (no
     contradiction filed).
  2. Add a "**SLO proliferation / page-someone-to-death**" anti-pattern callout
     (Claims 9–10) — relevant wherever the guide suggests "set an SLO for X":
     without a maintenance discipline and central tuning, per-journey SLOs
     explode exactly as Desai's 250k-SLO anecdote shows.
  3. Adopt Desai's **three recommendations** (Claim 8) as the standing SLO
     hygiene rule: be skeptical, be specific (narrow SLOs, Claim 6), validate and
     iterate (the drift/threshold-rot obligation, Claim 7) — these unify with the
     alerting note's threshold-rot (Claim 12) and the customer-centric note's
     continuous-verification (Claim 7).
  4. Warn against **circular reliability definitions** (Claim 14): define
     reliability from first principles, then let the SLO be its *measurement*.

- **Chapter 05 (LLM Ops Reliability / SLOs for AI agents)** — Miner's synthesis,
  for Smith review: This episode is unusually directly applicable to agent
  reliability targets:
  1. **Model agent reliability as stationarity, not a fixed number** (Claim 15):
     a production AI agent is reliable if its *behavior distribution is stationary
     over time* (consistent correctness, availability, latency) — not if it hits a
     static "95% success" SLO. An agent whose error rate swings weekly is
     unreliable even with a fine mean. This reframes the PagerDuty "March of 9s"
     discussion (blog-pagerduty-production-ai-agent-gaps) from "how many 9s" to
     "how stable is the distribution."
  2. **Track variance, not just the mean** (Claim 16): monitor the *variance* of
     agent latency, tool-call success, and hallucination rate; a stable-low-
     variance agent is more trustworthy than one with the same mean but
     catastrophic spikes. This is the conceptual basis for **agent drift
     detection** — the S5E6 Parker Barnes "drift detection" theme the index note
     (Claim 8) flags as AI-relevant.
  3. **Use the "surprise detector" for agents** (Claim 17): break agent traffic
     into self-similar journeys, model expected behavior per slice, and alert on
     the *rate of unlikely events* (distribution shift) — the SRE-native ancestor
     of model-drift monitoring; corroborates the alerting note's Claim 13
     (curated, model-aware signals beat raw anomaly detection).
  4. **Performance/latency as a leading incident indicator for agents** (Claim 18):
     creeping agent reasoning-time or tool-call latency often *precedes* a
     correctness/outage event; watch the latency distribution (Claim 16) as
     early warning, not just success/fail.
  5. **Per-journey / weighted agent SLOs** (Claims 6, 13): don't aggregate all
     agent journeys into one SLO (it will be "always out of SLO" and "page
     someone to death"); weight by journey criticality (a failed trivial query ≠ a
     failed incident remediation), extending the customer-centric note's
     per-workflow-SLO guidance (Claim 15).
  6. **Correctness is hard/circular — use ensemble verification for high stakes**
     (Claim 19): for critical agent actions, the "running important things twice"
     idea maps to dual-model/dual-prompt self-consistency checks — cite as a
     candidate pattern, not settled practice.

- **Cross-cutting**: This transcript is the transcript-level fulfillment of the
  `docs-google-sre-prodcast.md` index's S1E4 pointer (Ch4 Service Level
  Objectives). The Smith should treat the index note as the table of contents and
  this note (plus the other S1 transcript notes) as the substance for Ch00/Ch04
  SLO and alerting content. The SLO-skeptic thread here should be weighed against
  the book's prescriptions per the index note's Claim 6 guidance.

## Extraction Notes

- The source is a single HTML transcript page on the official sre.google domain
  (`/prodcast/transcripts/sre-prodcast-01-04/`, on-page title "Rethinking
  SLOs"). The page carries `release-date="2022-03-31"` (the Prodcast series
  launch date, also used by the sibling S1E2/S1E3 notes), so `date_published` is
  set to `2022-03-31` (season/series year, approximate for the episode itself).
  Raw HTML (71 KB) was fetched with `curl` and converted to plain text; the full
  transcript (≈137 lines of dialogue + nav) was read end-to-end — no skimming.
  No sub-pages were needed; the transcript is self-contained.

- **`confidence_overall: emerging`**: The episode is a single practitioner's
  conversational account. The *critiques* of SLOs (Claims 1–14, 18) are settled
  observations about real failure modes; the *proposed replacement* (the
  "stationarity" definition, the "surprise detector" analytics, the variance
  framing, Claim 19's correctness strategies) is explicitly a working proposal /
  "spitballed" and is marked emerging throughout. The overall confidence reflects
  that the source's highest-value content is its *critique* (settled) more than
  its *prescription* (emerging).

- **Quotes**: All `Quote` fields were copied character-for-character from the
  extracted transcript text (lines cited inline). Minor transcript artifacts were
  preserved as-is (e.g., "sort of," doubled spacing). The only non-verbatim
  elements are the structured "Concrete Artifacts" models, which are the Miner's
  faithful paraphrase/structuring of Desai's framing and are labeled as such. The
  Assayer should spot-check key quotes against the live URL.

- **Contradiction analysis (per MINER.md §4a)**: The apparent opposition between
  this source (error budgets "problematic," SLOs "brittle") and
  `discussion-google-sre-ben-treynor-interview.md` (error budgets as the canonical
  alignment mechanism) was evaluated and **rejected as a contradiction**. The
  conflict resolves to a *conditioning variable* — Treynor describes error budgets
  for Google's aggregate B2C core; Desai critiques them for B2B/multi-tenant cloud
  with differentiated, paying customers. This is exactly the MINER.md §4a
  "use X for small / Y for large" exclusion, and it matches the corpus's prior
  handling of Treynor ↔ Esparrachiari (customer-centric monitoring note, Claim 11
  cross-reference, no contradiction filed). No contradiction issue was opened, and
  `CONTRADICTIONS.md` had no open entries at extraction time. No existing
  `contradiction`-labeled issue covers this tension.

- **No code/config/metrics**: As the triage predicted, this conversational source
  contains no code, configs, dashboards, or failure telemetry — only conceptual
  claims, one scale anecdote (~250k SLOs), and illustrative examples. The
  "Concrete Artifacts" section is faithful transcription of Desai's definitions
  and examples (verbatim where quoted; structured where he described a contrast or
  scenario), not invented artifacts.

- **AI/LLM relevance**: None in the source itself (pre-LLM-era). The relevance is
  as the *SLO-skeptic / stationarity* foundation the guide's AI-agent reliability
  material needs when it sets targets for AI agents — the extrapolations in "Guide
  Impact" and "Our assessment" are the Miner's analytical synthesis and should be
  reviewed by the Smith for fidelity to the source's intent.
