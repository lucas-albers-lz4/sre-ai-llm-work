---
source_url: https://sre.google/prodcast/transcripts/sre-prodcast-01-05/
source_type: docs
title: "Maintaining client transparency while migrating with Pavan Adharapurapu (SRE Prodcast S1E5)"
author: "Pavan Adharapurapu (Google API Platform tech lead/manager), interviewed by MP English and Viv on the SRE Prodcast"
date_published: 2022-03-31
date_extracted: 2026-07-13
last_checked: 2026-07-13
status: current
confidence_overall: settled
issue: "#38"
---

# Maintaining client transparency while migrating with Pavan Adharapurapu (SRE Prodcast S1E5)

> A primary-source Google SRE practitioner account of *client-transparent backend
> migrations* — the three-component definition (compatible responses, compatible
> state changes, comparable latency), the finite-state-machine justification,
> Hyrum's Law as the core driver of migration complexity, the production-traffic
> replay / dark-launch validation technique, and the gradual rollout + fast-rollback
> cutover playbook (0.001% → 5% → 15%, random selection, seconds-to-minutes
> rollback). Foundational SRE migration practice; zero AI/LLM content, so all AI
> extensions below are the Miner's analytical work connecting classic migration
> engineering to AI-agent deployment.

## Source Context

- **Type**: docs (an official Google SRE podcast transcript published on
  sre.google). It is a verbatim conversation — host MP English and co-host Viv
  interview Pavan Adharapurapu — so it reads as a discussion, but it is hosted as
  SRE documentation and is mined here for its operational claims.
- **Author credibility**: Pavan Adharapurapu is a software engineering tech lead
  and manager in Google's **API Platform** group, 9+ years at Google, where he
  **led a successful multi-year migration of hundreds of Google web APIs** to a
  newer API platform, done invisibly to millions of applications and users. He is
  therefore speaking from direct ownership of a large-scale, real migration — not
  as a commentator. The hosts (MP, Viv) are practicing Google SREs. This is a
  primary-source practitioner account of the highest credibility for SRE migration
  practice.
- **Scope**: Covers the *design and execution* of client-transparent backend
  migrations specifically — what "client-transparent" means (and does not mean),
  why migrations are hard (Hyrum's Law, the four challenges), the pre-migration
  mindset, the validation methodology (production traffic replay / dark launch),
  and the cutover playbook (gradual rollout, random selection, fast rollback).
  Does NOT cover: any AI/LLM operations, concrete code/config artifacts (it is a
  conversational transcript, so no config is shown), or dashboards/metrics beyond
  the illustrative rollout percentages. It is the transcript-level mining of S1E5
  that the `docs-google-sre-prodcast.md` index note (S1E5 → Ch17 Testing for
  Reliability, Ch27 Reliable Product Launches at Scale) points to.

## Extracted Claims

### Claim 1: Client transparency is NOT byte-for-byte response matching — it is the source and target behaving the same way for all user-observable aspects of all existing traffic
- **Evidence**: Pavan's direct correction of MP's "is it just byte-for-byte
  identical responses?" frame; he defines it as a property arising from behavioral
  equivalence, with explicit qualifiers ("for all user-observable aspects, for all
  the existing traffic").
- **Confidence**: settled
- **Quote**: "Client transparency is a property of a migration that comes about by
  the source and target system behaving the same way for all user-observable
  aspects, for all the existing traffic. These qualifiers are important. We don't
  care if two systems do not match in behavior for non-user-observable aspects, or
  for requests that are not part of the current production traffic set."
- **Our assessment**: A precise, defensible definition. The two qualifiers are
  doing real work: (a) non-user-observable behavior is out of scope, and (b) only
  *currently-observed* traffic must match — future/never-seen requests are not a
  transparency obligation. This bounds the problem and is the seed of the
  "current system's behavior is the spec" claim (Claim 5).

### Claim 2: Client transparency has exactly three components — compatible responses, compatible state changes, and comparable latency — and these are both necessary and sufficient
- **Evidence**: Pavan enumerates the three and then derives sufficiency from a
  finite-state-machine model of software (Claim 2 below). Viv explicitly asks
  "are these the top three, or is this all we need?" and Pavan answers they are
  sufficient.
- **Confidence**: settled
- **Quote**: "So what are the user-observable aspects? Having a compatible response
  for every existing request is definitely one of the aspects, but there are two
  other aspects that make up client transparency: namely, compatible state changes
  and comparable latency."
- **Our assessment**: The three-component decomposition is the structural backbone
  of the whole episode and directly transferable: most migration plans only check
  responses, but Pavan insists state changes and latency are co-equal. The
  "comparable latency" clause is the one most often forgotten and the one that
  bites users first.

### Claim 3: Any real-world software can be modeled as a finite state machine with non-zero propagation delay, so output, state transition, and propagation delay are the only measurable things — which is why the three components are necessary and sufficient
- **Evidence**: Pavan's answer to Viv's "how do we know three is enough?" — a
  first-principles derivation rather than an appeal to authority.
- **Confidence**: settled
- **Quote**: "every real world software can be modeled as a finite state machine
  with non-zero propagation delay. For a given input, the only things that can be
  measured for such a finite state machine are the output, the state transition,
  and propagation delay. And therefore it's enough for us to just make sure that
  these three components are matching between the two systems and client
  transparency follows from that."
- **Our assessment**: An elegant, reusable mental model. The FSM framing is what
  makes the otherwise-handwavy "transparency" claim operational and testable — and
  it is exactly the model that justifies the production-traffic-replay technique
  (Claim 10): you can prove equivalence by replaying inputs and diffing
  output/state/delay.

### Claim 4: "User-observable state" includes far more than resource state — billing state, rate-limiting state, telemetry state, and any logs/error messages exposed to users all count and must match
- **Evidence**: Pavan's expansion of "state" beyond the database resource, with
  concrete examples (invoice at month-end = billing state; charts/console =
  telemetry state) and the rule that anything exposed to the user is in scope.
- **Confidence**: settled
- **Quote**: "when we talk about the state, it is all pieces of the state that is
  accessible to the user. So that certainly includes the underlying resource
  state. Every service has an underlying resource that it manages, but it also
  includes other parts of the state— like billing state, rate limiting state,
  telemetry state— because these are all accessible to the users."
- **Our assessment**: This is the single most under-appreciated claim in the
  episode. Migrators who only diff the database resource state will be blindsided
  by "my dashboards are behaving funkily" / "my billing is off" tickets (Pavan's
  own words). The acid test: "does the user see it in one form or another?" — if
  yes, it is user-observable state. Directly relevant to enumerating what an AI
  agent deployment must hold stable (see Guide Impact).

### Claim 5: Hyrum's Law — "the implementation is the interface for large systems" — means clients depend on undocumented behaviors, bugs, and implementation idiosyncrasies, and client transparency must cover those too, not just documented features
- **Evidence**: Pavan names Hyrum's Law explicitly and states that transparency
  requires sequencing behavior "for accidental features, implementation
  idiosyncrasies, and bugs as well," because users will have come to depend on them.
- **Confidence**: settled
- **Quote**: "It's called the Hyrum's Law. It's shortened as, 'the implementation is
  the interface for large systems.' It is important to point out that client
  transparency requires sequencing of behavior not just for documented features, but
  also for accidental features, implementation idiosyncrasies, and bugs as well.
  Since, as the Hyrum's Law says, there will be users who would inadvertently come
  to depend upon them."
- **Our assessment**: This is the *core* driver of migration complexity and the
  reason pure spec/code analysis cannot prove transparency. Hyrum's Law is the
  mechanism that makes production-traffic replay (Claim 10) necessary: you cannot
  enumerate the behaviors users depend on from the spec, so you must observe real
  traffic. Transfers directly to AI agents, whose users also depend on quirks
  (see Guide Impact).

### Claim 6: "No user left behind" — the current system's behavior is always the spec; even off-label / small-percentage usage can be mission-critical and must be carried over
- **Evidence**: Pavan states the current system's behavior is "always correct" and
  that a small-percentage off-label usage "can be the basis of a mission-critical
  workflow for that user."
- **Confidence**: settled
- **Quote**: "when it comes to client-transparent migrations, the behavior of the
  current system is always correct. That's what you assume. It's the spec, and
  that's what you have to ensure is carried over to the new system, as well."
  and "those users have to be cared for. You cannot just ignore those use cases
  just because they're a small percentage of it, because what is an off-label usage
  of your system can be the basis of a mission-critical workflow for that user."
- **Our assessment**: A strong user-primacy stance that reframes "edge case" (from
  the backend's view) as "mission-critical use case" (from the customer's view).
  This is the ethical/operational center of the episode and pairs tightly with the
  customer-centric monitoring episode (Cross-References) — both insist that
  aggregate "the system is fine" numbers hide individual broken users.

### Claim 7: There is an extremely high bar for asking customers to change code; the only defensible exception is when porting the behavior is orders of magnitude harder than the customer making the change — "never burden the customer" is the default mindset
- **Evidence**: Pavan sets a near-absolute rule, then carves a narrow exception
  (one user, massive complexity, with generous time/docs), and MP summarizes the
  trade-off as "orders of magnitude easier for the customer."
- **Confidence**: settled
- **Quote**: "It's almost like you have to have this mindset that you will never
  burden the customer, and the exception has to be so clear that it proves that
  rule."
- **Our assessment**: A concrete decision rule for the "do we port this buggy
  behavior?" question. The "orders of magnitude" bar is the operational test —
  porting a quirk is almost always cheaper than coordinating a fleet of mobile/TV
  app updates the customer doesn't even control. Useful guardrail against
  readability-driven breaking changes.

### Claim 8: There are four major challenges in client-transparent migrations — (1) knowing the full set of disparities, (2) testing the two systems for parity, (3) knowing when you broke a customer (server-side detection is limited), (4) bloating the new system with parity fixes that hurt maintainability
- **Evidence**: Pavan enumerates the four after MP calls the problem "really hard to
  know what you don't know." Challenge 3 is the deepest: "not all compatibility
  issues can be detected server-side" (e.g., a client that chokes on added
  whitespace), and without client-side telemetry you cannot know server-side.
- **Confidence**: settled
- **Quote**: "there are four major challenges we found during our migrations. The
  first one is knowing the complete set of disparities between the two systems...
  The second challenge is testing two systems for parity... The third challenge we
  found was that it is hard to know when you broke the customer, because not all
  compatibility issues can be detected server-side... And the final challenge... is
  that we could end up bloating the new system with parity fixes— especially the
  old system idiosyncrasies— and this could reduce the maintainability of the new
  system for all users, current and new."
- **Our assessment**: Challenge 3 (undetectable breakage) and Challenge 4
  (maintainability debt from parity fixes) are the two most original and
  under-discussed. Challenge 4 is the "Hyrum's Law tax" — the new system accretes
  cruft to emulate old bugs, hurting all future users. Both are worth surfacing in
  the guide as migration failure modes.

### Claim 9: Pre-migration mindset — avoid large migrations unless long-term user benefit >> cost; embrace risk; plan with "constructive pessimism"; prevent backsliding (no new usage on the old system); make client transparency a P0 constraint; keep a plan B; beware the sunk-cost fallacy
- **Evidence**: Pavan's pre-strategy framing, including the "pumping water out of a
  pool being simultaneously filled" analogy for allowing new old-system usage, and
  an explicit sunk-cost-fallacy warning.
- **Confidence**: settled
- **Quote**: "It is immaterial that you spent a lot of effort, a lot of hard work,
  in taking the migration up to a certain point. That cost is meaningless if in
  going further you're going to inconvenience your users even more, right? So you
  should be careful of the sunk cost fallacy, as you said. What matters is from
  this point onwards, what is good for your users, for your customers?"
- **Our assessment**: The "prevent backsliding" point is a concrete, often-missed
  tactic (freeze new old-system usage so the parity surface doesn't keep growing).
  The sunk-cost warning is the same psychological trap the alerting and on-call
  notes touch on; here it is applied to *stopping a failing migration*. High value
  for Ch05 (migrations).

### Claim 10: Step 1 of the strategy — enumerate ALL user-observable state before migrating; if you don't know what can break the user, you can never guarantee transparency
- **Evidence**: Pavan's first concrete step, with the warning that if you only
  focus on resource state "you would be surprised by customer tickets that says,
  'Hey, my dashboards are behaving funkily', or 'my billing is off'."
- **Confidence**: settled
- **Quote**: "if you don't know what can break the user, then you can never
  guarantee client transparency. If you only focus on the most important state like
  the resource state in the database— if that's all you care about, that's all you
  focus on— then you would be surprised by customer tickets..."
- **Our assessment**: The natural pairing of Claim 4 (what counts as state) with an
  *action*: sit down and enumerate it during planning, before any code. This is the
  migration analog of "define your SLIs / Critical User Journeys before you build"
  (see Cross-References) — you cannot protect what you haven't named.

### Claim 11: Step 2 — quantify disparity via production traffic replay / dark launch: sample production traffic to the old system, capture request + response + state change, replay the same requests through the new system, and diff; zero diff = safe to migrate
- **Evidence**: Pavan presents this as "the only practical way" to quantify
  compatibility, and gives the basic mechanism end-to-end.
- **Confidence**: settled
- **Quote**: "This is where production traffic to the old system is simultaneously
  run through the new system, and the responses and state changes are compared
  between both the systems."
- **Our assessment**: The centerpiece validation technique and the closest thing in
  the corpus to a non-AI "golden dataset" pattern (see Cross-References / Guide
  Impact). It is exactly "run real inputs through the candidate system and diff
  outputs against the known-good system" — the SRE ancestor of evaluating an AI
  agent against a golden dataset before promotion.

### Claim 12: Production-traffic-replay engineering constraints — "do no harm" to the live system, never let replay traffic change state, follow privacy, sample with no gaps, cover infrequent clients, and handle timing/token-expiry windows
- **Evidence**: Pavan lists the hard-won lessons from building the replay system,
  including the Hippocratic "do no harm" framing and the DB-isolation trick (capture
  values crossing the unchanged layer boundary and replay those, so the new system's
  DB is never actually mutated).
- **Confidence**: settled
- **Quote**: "It's like the equivalent of the Hippocratic Oath: do no harm. You
  don't disrupt the existing traffic on the existing system in your attempts to
  create a pathway for a safe migration."
  and "we should ensure that no state change happens due to replay traffic. It's
  very important."
- **Our assessment**: The "don't change state during replay" constraint is the
  subtle, load-bearing engineering detail (MP intuited it via idempotency). The
  DB-boundary-capture trick is the concrete solution and is exactly how you get
  state-change diffs without side effects. This is the most reusable *how-to* in
  the episode for anyone building a replay harness — including an AI-agent eval
  harness (replay against a captured fixture, never mutate prod).

### Claim 13: Production traffic replay is not sufficient alone — it is poor at proving comparable latency (use load tests), integration tests establish a baseline before replay, and error-fallback / second-chance forwarding to the old system adds confidence
- **Evidence**: Pavan on the blind spots: replay can't mimic the production load
  profile, so latency equivalence needs load tests; integration tests are a
  pre-replay baseline; reactive error-fallback (forward new-system errors to the
  old system for reprocessing pre-state-change) is a safety net.
- **Confidence**: settled
- **Quote**: "production traffic replay, as good as it is in ensuring that responses
  and state changes are compatible, is not so great at proving that they have
  comparable latency, because it's hard to mimic [the] production load profile when
  doing sampling."
- **Our assessment**: An honest "know your tool's limits" claim. The latency gap is
  the same reason an AI-agent golden-dataset eval (offline replay) cannot alone
  prove production latency/throughput — you still need a load test. The
  second-chance error-fallback is a cheap, high-value safety net worth copying.

### Claim 14: Cutover blast radius is quantitatively AND qualitatively larger than a new-product launch — established traffic you didn't grow organically — so cutover goals are low MTBF, low blast radius/impact, and low MTTR
- **Evidence**: Pavan's contrast with "new product or feature launches": migration
  traffic is already there (quantitatively larger) and is established,
  decade-old-customer traffic (qualitatively larger — "request for request, the
  blast radius is huge").
- **Confidence**: settled
- **Quote**: "the blast radius for migration cutover is quantitatively and
  qualitatively larger. It's quantitatively larger because you have a large amount
  of existing traffic. There is no organically increasing traffic that starts at
  zero, like for new product launches. It's already there. It's qualitatively
  larger because this is established traffic."
- **Our assessment**: A clean, important distinction often collapsed in generic
  "rollout" advice. It justifies the extra conservatism of migration rollout vs.
  feature launch. Pairs directly with Treynor's availability = MTBF × MTTR framing
  (Cross-References): Pavan's three cutover goals *are* Treynor's availability
  levers applied to the cutover phase.

### Claim 15: Gradual rollout specifics — "fast" means multi-hour not multi-day; start at ≤0.001% and below the error budget, hold a week; accelerate after 5%; cap each step at ≤15%; "rare to see new issues after crossing 5%"
- **Evidence**: Pavan's concrete ramp schedule, with the explicit "less than your
  error budget" ceiling and the week-long soak at the tiny starting percentage.
- **Confidence**: settled
- **Quote**: "Fast means multi-hour, not multi-day. If it's multi-day, then it's
  hard to track the health of the incremental ramp up."
  and "even within the gradual rollout, it should be very slow and very small in the
  beginning, and it can be accelerated somewhat after reaching 5%. We generally
  notice that it's very rare to see new issues after crossing 5%. Still, you should
  not move more than, let's say, 15% maximum traffic between every step, and in the
  beginning we generally start at something very small, like 0.001% or less.
  Definitely less than your error budget for your service. And leave it there for a
  week... And then we gradually increase the increments, and after we reach 5%, we
  go 15% every three days."
- **Our assessment**: This is the highest-value, directly-adoptable artifact in the
  episode — a concrete canary schedule with numbers. The "start < error budget" rule
  is a direct application of Treynor's error budget (Cross-References). The
  "rare after 5%" empirical observation is a great "when can I speed up?" signal.
  Maps cleanly onto AI-agent canary deployment (see Guide Impact).

### Claim 16: Diverted traffic must be randomly selected (not hashed by IP/ID) so every customer sees a gradual rollout and avoids a large late-shift that would concentrate blast radius
- **Evidence**: Pavan explains that hashing by IP/ID means late-migrated customers
  suddenly see a large shift "from the old system to new system" — the opposite of
  gradual from their perspective.
- **Confidence**: settled
- **Quote**: "the diverted traffic must be randomly selected. This is so that every
  customer sees a gradual rollout from their point of view. If it's not random— for
  example, if you hash by IP address or some sort of ID— then what happens is that
  the customers whose traffic is migrated at the end of your rollout suddenly see a
  large shift in traffic from the old system to new system, and in case of any
  incompatibilities, suddenly a large part of their traffic is getting affected, and
  random selection avoids that."
- **Our assessment**: A subtle but important rollout-correctness point: "gradual
  globally" is not enough; it must be gradual *per customer*. Random selection makes
  the experience uniform across customers and avoids the correlated-failure trap of
  attribute hashing. Directly relevant to any per-tenant AI-agent rollout.

### Claim 17: Fast rollback is the "big red button" — to the previous split or 100% old, in seconds/minutes, built before migration starts; "in case of doubt, roll back"; the migration plan is always packaged with the rollback plan, with entry/exit criteria per stage
- **Evidence**: Pavan makes rollback a precondition ("build such a fast rollback
  mechanism before you even start migration") and states the "in case of doubt, roll
  back, and then investigate" maxim; MP sums it as "a migration plan should always
  come packaged with the rollback plan."
- **Confidence**: settled
- **Quote**: "It's your big red button. You should be able to roll back to either
  the previous state, the previous split between the old and new system, or maybe
  rolling back 100% to the old system. You should be able to do it very fast— like
  in seconds or minutes. And so it's important to build such a fast rollback
  mechanism before you even start migration. As they say, in case of doubt, roll
  back, and then investigate."
  and "a migration plan should always come packaged with the rollback plan."
  and "it should have both an entry and exit criteria for different rollout stages so
  that there's a clear signal that we are good to go on to the next stage or when we
  have to roll back from that stage."
- **Our assessment**: The MTTR lever made explicit (pairs with Claim 14's low-MTTR
  goal). "Built before you start" and "packaged with the plan" are the two
  discipline points most teams skip. The entry/exit-criteria-per-stage pattern is a
  reusable rollout-control structure. Core Ch04/Ch05 material.

### Claim 18: Client transparency is NOT the goal for security/privacy vulnerabilities (don't silently port them — inform customers and plug the gap) or for services past their support window (courtesy notice); otherwise it is a P0 requirement
- **Evidence**: Pavan's two explicit exceptions to the "always transparent" rule,
  framed as "surprisingly, yes" there are cases.
- **Confidence**: settled
- **Quote**: "you should not give priority to client transparency for security and
  privacy issues. If that's part of migration— you realize that there is a security
  vulnerability in the old system that could be exploited and that could hurt your
  customers— then it's important that you don't silently port that security issue to
  the new system, because in the long term it causes more cost to your customers."
- **Our assessment**: A necessary, often-forgotten carve-out: transparency is a
  *user-experience* goal and must yield to a *user-safety* goal. The security
  exception is the right call and should be stated plainly in any migration
  checklist (don't let "don't break the client" become "silently inherit the CVE").

### Claim 19: Migration complexity scales with surface area + diverse usage, not raw traffic volume — a high-traffic single-client service was the easiest migration because the request pattern was known and uniform
- **Evidence**: Pavan's closing nuance: "a lot of these challenges... really come
  about for systems with large surface area and large and diverse usage"; cites a
  very-high-traffic but single-Google-owned-client service as "one of the easiest
  services to migrate."
- **Confidence**: settled
- **Quote**: "we migrated a service that had a very large amount of traffic, but it
  was one of the easiest services to migrate. And the reason was, all of the traffic
  was coming from one client that was owned by Google itself, so we knew exactly the
  pattern of requests that would be coming to the service."
- **Our assessment**: A useful conditioning variable that prevents over-applying
  the heavy methodology to simple/uniform systems. The risk driver is *diversity of
  clients and behaviors* (Hyrum's Law surface), not QPS. Helps the guide scopes when
  the full replay+random-rollout apparatus is warranted vs. a lighter touch.

## Concrete Artifacts

### The client-transparency definition (verbatim)

```
Client transparency = source & target systems behave the same way for
ALL user-observable aspects, of ALL existing production traffic.

Three necessary-and-sufficient components (derived from the FSM model):
  1. Compatible responses     — for every existing request
  2. Compatible state changes — resource + billing + rate-limiting + telemetry
                                 + any user-exposed logs/error messages
  3. Comparable latency       — degraded latency is user-noticeable

A system "modeled as a finite state machine with non-zero propagation delay":
only output, state transition, and propagation delay are measurable →
matching all three ⇒ client transparency follows.
```
— Pavan Adharapurapu, SRE Prodcast S1E5 (transcript)

### The four migration challenges (verbatim enumeration)

```
1. Knowing the complete set of disparities between the two systems
   (easy at the feature level; hard for bugs & implementation traits).
2. Testing the two systems for parity
   (unit/integration tests cannot cover all accidental features/bugs).
3. Knowing when you broke the customer
   (not all compat issues are detectable server-side;
    e.g. new whitespace breaks a poorly-written client — invisible server-side).
4. Bloating the new system with parity fixes
   (old-system idiosyncrasies reduce maintainability for ALL users).
```
— Pavan Adharapurapu, SRE Prodcast S1E5

### The migration strategy / cutover playbook (paraphrase of Pavan's steps, with verbatim anchors)

```
PRE-MIGRATION MINDSET
  • Avoid the migration unless long-term user benefit >> cost (get sign-off).
  • Prevent backsliding: allow NO new usage on the old system ("don't pump
    water into a pool you're draining").
  • Client transparency as a P0 / overarching constraint.
  • Keep a plan B for when the migration becomes intractable.
  • Beware the sunk-cost fallacy ("what matters is from this point onwards").

STRATEGY STEPS
  1. Enumerate ALL user-observable state (resource, billing, rate-limit,
     telemetry, user-exposed logs/errors). "If you don't know what can break
     the user, you can never guarantee client transparency."
  2. Quantify disparity via production traffic replay / dark launch
     (sample old-system traffic; capture request+response+state change;
     replay same requests through new system; diff; zero diff ⇒ safe).
  3. Limit blast radius via gradual rollout.
  4. Detect incompatibilities: server-side monitoring for new-system errors;
     monitor customer-support channels ONLY as a precaution (never depend on
     the customer to find breaks).
  5. Mitigate via fast rollback to previous state / 100% old system.
  6. Correct + postmortem; review the plan; proceed if clean.

CUTOVER RAMP SCHEDULE (verbatim numbers)
  • "Fast" = multi-hour, not multi-day.
  • Start: ≤ 0.001% (or less), and < your error budget. Hold a week.
  • Accelerate after 5% (rare to see new issues past 5%).
  • Cap each step at ≤ 15% of traffic.
  • After 5%: +15% every three days.
  • Diverted traffic MUST be randomly selected (not hashed by IP/ID).
  • Rollback "big red button": seconds-to-minutes, built BEFORE migration.
  • Plan always packaged with rollback plan; entry/exit criteria per stage.
```
— paraphrase of Pavan Adharapurapu, SRE Prodcast S1E5; quotes per Claims 10/15/16/17

### The production-traffic-replay mechanism (paraphrase, with verbatim anchors)

```
Capture phase:
  continuously sample production traffic to the OLD system
  → capture (user request, old-system response, old-system state change)

Replay phase:
  replay the SAME user requests through the NEW system
  → capture (new-system response, new-system state change)
  → diff responses and state changes

Key engineering constraints (verbatim):
  • "do no harm" — never disrupt existing production traffic.
  • "no state change happens due to replay traffic" — isolate unchanged layers
    (e.g. the DB stays put; capture values crossing that boundary and replay
    the captured values, so the new system's DB is never mutated).
  • follow all privacy principles when diffing responses.
  • sample ALL traffic classes with NO gaps (infrequent clients: weekly/monthly).
  • handle timing windows (e.g. token expiry) and network flakiness.

Blind spots (use complementary techniques):
  • latency equivalence → load tests (replay can't mimic prod load profile).
  • baseline compatibility → integration tests (before replay).
  • safety net → error-fallback / second-chance forwarding to old system
    (pre-state-change) when new system throws.
```
— paraphrase of Pavan Adharapurapu, SRE Prodcast S1E5; quotes per Claims 11/12/13

## Cross-References

- **Corroborates**:
  - **docs-google-sre-prodcast.md (Claim 8, Claim 4, episode table line 273)** —
    that index note states S1E5 maps to *Ch17 Testing for Reliability* and *Ch27
    Reliable Product Launches at Scale*, and that Prodcast episodes describe
    AI-assisted-SRE practice including "golden data sets" for validation. This note
    *is* the deeper mining the index promised: Pavan's production-traffic-replay /
    dark-launch (Claim 11) is precisely the SRE ancestor of the "golden data set"
    validation pattern the index's Claim 8 cites. No conflict — this note fills the
    structural pointer with the episode's actual claims.
  - **discussion-google-sre-ben-treynor-interview.md (Claim 3, Claim 13, Claim 9)** —
    Treynor defines error budgets (1 − availability target) as the dev/SRE launch
    incentive and availability as MTBF × MTTR. Pavan *applies* both: his "start the
    ramp below your error budget" (Claim 15) is a direct use of Treynor's error
    budget, and his three cutover goals — low MTBF, low blast radius, low MTTR
    (Claim 14) — are Treynor's availability levers instantiated for the cutover
    phase. Treynor's "launch freeze when budget exhausted" (Claim 9) is the
    escalation counterpart to Pavan's "in case of doubt, roll back" (Claim 17).
    Corroboration, not contradiction.

- **Contradicts**: None. No claim in this transcript opposes any claim in an
  existing source note. The one apparent tension — Pavan says client-side
  telemetry is generally *unavailable* for public APIs with diverse clients (so you
  monitor support channels only as a precaution), while
  `discussion-google-sre-prodcast-customer-centric-monitoring.md` advocates
  *client-side monitoring* — is a **conditioning variable**, not an opposition:
  client-side monitoring is valuable *where you control the client*; for open public
  APIs you usually don't, so it's a gap to acknowledge. No contradiction issue filed
  (per MINER.md §4a).

- **Extends**:
  - **docs-google-sre-prodcast.md** — converts the index's S1E5 pointer (Ch17/Ch27)
    into substantive claims; together they let the Smith cite both "episode exists /
    maps to Ch17+Ch27" (index) and "here are the specific migration practices" (this
    note).
  - **discussion-google-sre-prodcast-customer-centric-monitoring.md (Claim 3, Claim 4,
    Claim 11, Claim 12, Claim 13, Claim 5)** — that episode insists a broad
    availability number hides *who* is broken and that you must understand "user
    creativity" and aggregate by Critical User Journeys (CUJs). Pavan *operationalizes*
    that user-primacy for migrations: "no user left behind" (Claim 6), enumerate
    user-observable state (Claim 4/10), and the random-selection rule (Claim 16) is
    the rollout-level expression of "every user/workflow matters, not just the
    aggregate." His server-side-detection limit (Claim 8, challenge 3) explains *why*
    the customer-centric episode's client-side monitoring is so valuable when you can
    get it.
  - **discussion-google-sre-ben-treynor-interview.md** — extends Treynor's foundational
    taxonomy (error budgets, MTBF/MTTR, launch freeze) with the concrete migration
    engineering that those principles imply.
  - **docs-google-sre-nalsd-classroom.md (Claim 7)** — complementary, not overlapping:
    NALSD designs systems for reliability *before* deployment (capacity isolation,
    graceful degradation, SLO/error-budget framing); this note covers preserving
    reliability *during* a backend change/cutover. Same sre.google domain, adjacent
    lifecycle stage. Listed by the Prospector as an overlapping note; content is
    distinct (system design methodology vs. migration execution).
  - **docs-google-sre-prodcast-01-03-alerting.md** — sibling S1 episode (S1E3) mined
    by this repo; same series/style, different topic (alerting). No claim overlap;
    listed here only to mark the sibling relationship.

- **Novel** (new to the corpus):
  - The **three-component definition of client transparency** (responses + state
    changes + latency) and the **FSM derivation** (Claim 1/2/3) — a precise,
    testable model of "don't break the client" absent from the corpus.
  - **Hyrum's Law as the driver of migration complexity** (Claim 5) — named, with the
    implication that spec/code analysis can't prove transparency.
  - The **production-traffic-replay / dark-launch technique** with its engineering
    constraints — especially "never let replay mutate state; capture DB-boundary
    values and replay those" (Claim 11/12) — the closest non-AI analog to a golden
    dataset in the corpus.
  - The **concrete canary ramp schedule** (0.001% → 5% → 15%, hold a week, < error
    budget, random selection, seconds-minutes rollback) (Claim 15/16/17) — a directly
    adoptable rollout recipe with real numbers.
  - The **four migration challenges** (Claim 8), especially undetectable breakage
    (challenge 3) and parity-fix maintainability debt (challenge 4).
  - The **security/privacy carve-out** to the transparency rule (Claim 18).

## Guide Impact

> NOTE: This source contains **zero AI/LLM content**. The SRE migration claims below
> are cited directly from the transcript (settled, primary-source Google SRE
> practice). Every AI/LLM extension is the Miner's analytical synthesis and should be
> reviewed by the Smith for fidelity — flagged explicitly as such. The source maps to
> SRE Book **Ch17 Testing for Reliability** and **Ch27 Reliable Product Launches at
> Scale** (per `docs-google-sre-prodcast.md` line 273); in this guide's own chapter
> scheme the relevant targets are Ch02 (Deployment), Ch04 (On-call/Toil), and Ch05
> (Incident Response & Migrations / LLM Ops Reliability).

- **Chapter 02 (Deployment)**: Add a "safe backend change / migration" subsection
  built on Pavan's methodology:
  1. **Dark launch / production-traffic replay as pre-cutover validation**
     (Claim 11) — the SRE analog of golden-dataset evaluation: run real prod inputs
     through the candidate system and diff responses + state changes; zero diff ⇒
     safe. Pair with the "never let replay mutate state" constraint (Claim 12) as the
     how-to.
  2. **The concrete canary ramp** (Claim 15) — 0.001% → 5% → 15%, hold a week at
     start, cap steps at 15%, start *below the error budget*. This is a
     ready-to-paste rollout recipe.
  3. **Random selection, not attribute hashing** (Claim 16) — gradual must hold
     *per customer/tenant*, or you concentrate blast radius.
  4. **Fast rollback as a precondition** (Claim 17) — build the "big red button"
     before you start; package rollback with the plan; entry/exit criteria per stage.

- **Chapter 04 (On-call and Toil)**:
  1. **Rollback is the MTTR lever** (Claim 17) — seconds-to-minutes rollback is the
     practical realization of Treynor's MTTR-half of availability. Make "rollback
     built before cutover" a toil-reducing, incident-limiting discipline.
  2. **Blast-radius management during change** (Claim 14/16) — migration cutover has
     a larger blast radius than a launch; the random-selection + small-step rules are
     the mitigation. Reusable beyond migrations.
  3. **Sunk-cost-fallacy awareness** (Claim 9) — during a failing rollout, stop and
     invoke plan B rather than pressing on; a psychological guardrail for on-call
     during change.

- **Chapter 05 (Incident Response & Migrations / LLM Ops Reliability)**:
  1. **Enumerate user-observable state before any migration** (Claim 4/10) — the
     migration analog of "define SLIs / Critical User Journeys first." You cannot
     protect what you haven't named (resource, billing, rate-limit, telemetry,
     user-exposed logs/errors).
  2. **The four migration challenges as a pre-flight checklist** (Claim 8) — esp.
     undetectable breakage (monitor support channels as precaution) and parity-fix
     maintainability debt.
  3. **Security/privacy carve-out** (Claim 18) — a migration checklist item: never
     silently port a vulnerability in the name of transparency.

- **Cross-cutting (AI in SRE) — Miner's synthesis, for Smith review**:
  1. **Dark launch → agent golden-dataset eval** (Claim 11): Just as Pavan replays
     prod API traffic through the new backend and diffs, an AI-agent change should be
     validated against a golden dataset / captured production agent traces *before*
     it sees real users — and, critically, the eval must not mutate production state
     (Claim 12's "replay must not change state" maps to: eval against fixtures, never
     live tools). This is the non-AI precedent for the golden-dataset discipline the
     Prodcast index (Claim 8) and the AI blog notes already advocate.
  2. **Agent canary = Pavan's ramp** (Claim 15/16): A model/agent update rolls out
     exactly like Pavan's migration — 0.001%-scale shadow first, random traffic
     selection per tenant, fast rollback. The "rare to see new issues after 5%"
     empirical signal is a useful "when to accelerate" cue for agent rollouts too.
  3. **Hyrum's Law for agents** (Claim 5): Users come to depend on an agent's quirks
     and bugs; "the current system's behavior is always the spec" (Claim 6) means an
     agent update must treat the *existing* agent's emitted behavior as the
     compatibility baseline, not the prompt's intent.
  4. **Replay can't prove latency** (Claim 13): An offline agent golden-dataset eval
     validates correctness but not production latency/throughput — you still need a
     load test, exactly as Pavan says. Pairs with the AI notes' call for realistic
     agent evaluation.

## Extraction Notes

- The source is a single transcript page on the official sre.google domain
  (`/prodcast/transcripts/sre-prodcast-01-05/`, title "Maintaining client
  transparency while migrating with Pavan Adharapurapu"). Fetched via `curl` (83 KB
  HTML), scripts/styles stripped, tags removed, and converted to plain text (183
  lines). The full transcript was read end-to-end — no skimming. It is a single-topic
  episode (one guest, Pavan Adharapurapu) covering client-transparent migrations
  end-to-end, so the whole thing is within scope.
- **`date_published`**: The page carries `data-release-date="2022-03-31"` and a meta
  description dated 2022-03-31 (the same series/index date used by
  `docs-google-sre-prodcast.md`). Season 1 of the Prodcast aired across 2021–2022;
  individual episode air dates are not published on the transcript page, so
  2022-03-31 is the verifiable page-metadata date and is approximate for the episode
  itself. Flagged here for the Smith to refine (mirrors the convention used in
  `docs-google-sre-prodcast-01-03-alerting.md`).
- All `Quote` fields were copied character-for-character from the extracted
  transcript text (verbatim passages cited inline; the only bracketed editorial marker
  in the source, "mimic [the] production load profile" in Claim 13, is reproduced as
  written). Spot-check against the live URL. The `Concrete Artifacts` blocks are the
  Miner's faithful structured paraphrase of Pavan's framing and are labeled as such;
  every verbatim anchor inside them is quoted per the claims above.
- No part of the source was paywalled; the transcript is publicly accessible.
- This note is the transcript-level mining of S1E5 that the `docs-google-sre-prodcast.md`
  index note anticipated (its line-273 episode→chapter map and Claim 8 golden-dataset
  pointer). It does not re-extract the index's structural facts; it extends them with
  the episode's specific migration claims. Sibling episode S1E3 is mined separately as
  `docs-google-sre-prodcast-01-03-alerting.md`.
- No contradiction issue was filed: the only apparent tension (Pavan's "client-side
  telemetry generally unavailable for public APIs" vs. the customer-centric-monitoring
  episode's advocacy of client-side monitoring) is a conditioning variable (controlled
  client vs. open public API), not an opposition, per MINER.md §4a.
