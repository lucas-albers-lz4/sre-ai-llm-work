---
source_url: https://sre.google/workbook/simplicity
source_type: documentation
title: "Google SRE: Simplicity — SRE Workbook Chapter 7"
author: "John Lunney, Robert van Gent, and Scott Ritchie (Google SRE), with Diane Bates and Niall Richard Murphy; Case Study 4 by Mike Curtis"
date_published: 2018
date_extracted: 2026-08-13
last_checked: 2026-08-13
status: current
confidence_overall: settled
issue: "#904"
---

# Google SRE: Simplicity — SRE Workbook Chapter 7

> The canonical Google SRE treatment of simplicity as an end-to-end operational
> goal: the code-level cyclomatic-complexity baseline, five practical proxies
> for systems-level complexity (training time, explanation time, administrative
> diversity, diversity of deployed configurations, age/Hyrum's Law), the
> "complexity is an externality → SRE as end-to-end simplicity champion" role
> pattern, the management apparatus for simplification (10% simplicity budget,
> celebrate code deletion, rotating whole-stack SRE group), diagramming to find
> amplification and cyclic dependencies, and five worked case studies (bag→
> Protocol Buffers, Borg→Omega rewrite, Display Ads spiderweb consolidation,
> shared microservices platform, pDNS self-dependency). This is the sibling
> chapter to Eliminating Toil (Ch6) and gives Ch04 a concrete complexity-
> measurement and simplification-lever framework comparable to the toil
> taxonomy and measurement methodology.

## Source Context

- **Type**: documentation — SRE Workbook (O'Reilly, 2018) Chapter 7 "Simplicity,"
  published at `sre.google/workbook/simplicity/`, the direct sibling of
  Workbook Chapter 6 "Eliminating Toil." This is a distinct chapter from the
  SRE Book Chapter 8 "Simplicity" (linked as further reading for the cyclomatic-
  complexity discussion); the workbook chapter adds the systems-level complexity
  proxies, the end-to-end/champion framing, the simplification-management
  apparatus, and the five case studies.
- **Author credibility**: Highest available. Written by three named Google SRE
  practitioners (John Lunney, Robert van Gent, Scott Ritchie) with editors
  Diane Bates and Niall Richard Murphy of the SRE Book/Workbook series, and one
  contributed case study (Case Study 4, shared microservices platform, by Mike
  Curtis). First-party practitioner accounts of systems the authors operated
  (Display Ads serving, the Borg/Omega ecosystem, pDNS, a social-networking
  microservices platform) — including one case study (Case Study 1) drawn from
  a chapter author's previous role at a startup, so the "abstract API shifts
  complexity to clients" lesson is not only a Google-scale observation.
- **Scope**: Covers (a) why simplicity correlates with reliability and why it
  must be end-to-end (code → architecture → tools/processes); (b) measuring
  complexity — cyclomatic complexity as the code-level standard, why CCN-type
  counting fails at system level, and the five practical proxies; (c) the
  externality argument and the SRE-as-end-to-end-simplicity-champion role with
  two reader actions (canonical system diagrams, SRE review of design docs);
  (d) regaining simplicity — simplification as removal work, the 10% simplicity
  budget, celebrating code deletion, the rotating whole-stack SRE group, and
  diagramming for amplification/cyclic dependencies; (e) five case studies with
  transferable lessons. Does NOT cover LLM/agent-specific workloads directly —
  the complexity proxies, the rewrite-vs-improve comparison rule, and the
  standardized-platform/tiered-engagement pattern are the guide's bridge to
  LLM-ops and agent-infrastructure content.

## Extracted Claims

### Claim 1: Simplicity strongly correlates with reliability — simple software breaks less often and is easier and faster to fix; for SREs, simplicity is an end-to-end goal extending beyond code to system architecture and the tools/processes used to manage the software lifecycle
- **Evidence**: The chapter intro states the correlation and defines the
  end-to-end scope directly, with the three-way framing ("easier to understand,
  easier to maintain, and easier to test").
- **Confidence**: settled
- **Quote**: "Simplicity is an important goal for SREs, as it strongly correlates with reliability: simple software breaks less often and is easier and faster to fix when it does break. Simple systems are easier to understand, easier to maintain, and easier to test." — and — "For SREs, simplicity is an end-to-end goal: it should extend beyond the code itself to the system architecture and the tools and processes used to manage the software lifecycle."
- **Our assessment**: The load-bearing thesis of the chapter and the reason the
  Prospector routed it to Ch04/Ch03/Ch05. The end-to-end scope (architecture and
  ops tooling, not just code) is what makes this chapter's proxies and levers
  applicable to the guide's agent/LLM infrastructure: an agent fleet's config
  corpora, model-serving stacks, and runbooks are part of the "tools and
  processes" a simplicity program must govern. We buy it fully — canonical
  first-party SRE doctrine.

### Claim 2: Code complexity is objectively measurable (cyclomatic complexity is the best-known standard), but teams are less adept at judging whether measured complexity is necessary or accidental, how one method's complexity influences a larger system, or which refactoring approaches work best
- **Evidence**: The "Measuring Complexity" section defines cyclomatic complexity
  (CCN) as "the number of distinct code paths through a specific set of
  statements," gives the no-loops/no-conditionals CCN-of-1 example, lists IDE
  tooling (Visual Studio, Eclipse, IntelliJ), and names the three gaps the
  software community is "less adept at."
- **Confidence**: settled
- **Quote**: "Perhaps the best-known and most widely available standard is cyclomatic code complexity, which measures the number of distinct code paths through a specific set of statements. For example, a block of code with no loops or conditionals has a cyclomatic complexity number (CCN) of 1." — and — "We're less adept at understanding whether the resulting measured complexity is necessary or accidental, how the complexity of one method might influence a larger system, and which approaches are best for refactoring."
- **Our assessment**: Sets the ceiling of what objective measurement can do:
  code-level CCN is available today (and an LLM can compute it), but the
  necessary-vs-accidental judgment and the system-level influence analysis are
  not automatable off the shelf. For the guide this warns against treating
  "reduced cyclomatic complexity" as a complete simplicity metric — the proxies
  in Claim 3 are the system-level complement. Settled.

### Claim 3: Formal system-level complexity measurement is rare and CCN-type counting (entities × communication paths) "grows hopelessly large" for sizable systems — so practical proxies are training time, explanation time, administrative diversity, diversity of deployed configurations, and age (Hyrum's Law)
- **Evidence**: The "Measuring Complexity" section gives the full five-proxy
  list with the concrete question each answers: training time ("How long does it
  take a new team member to go on-call?"), explanation time (whiteboard the
  architecture for a new team member), administrative diversity (how many ways
  are there to configure similar settings), diversity of deployed configurations
  (unique binaries/versions/flags/environments in production), and age (Hyrum's
  Law — "over time, the users of an API depend on every aspect of its
  implementation").
- **Confidence**: settled
- **Quote**: "You might be tempted to try a CCN-type approach of counting the number of distinct entities (e.g., microservices) and possible communication paths between them. However, for most sizable systems, that number can grow hopelessly large very quickly." — and — "How old is the system? Hyrum's Law states that over time, the users of an API depend on every aspect of its implementation, resulting in fragile and unpredictable behaviors."
- **Our assessment**: The highest-value extraction for Ch04/Ch03. The five
  proxies are the "complexity-reduction measurement framework" the Prospector's
  key question asked about: training time and explanation time are countable
  human-effort proxies an agent layer can partially tally (on-call readiness
  tracked per engineer); administrative diversity and diversity of deployed
  configurations are directly countable from a config corpus and deployment
  inventory. Hyrum's Law makes age a proxy with a named mechanism. We buy it —
  the proxies are pragmatic and each maps to an observable quantity.

### Claim 4: "In general, complexity will increase in living software systems unless there is a countervailing effort," and providing that effort is worthwhile — two observations with "no serious opposition"
- **Evidence**: The "Measuring Complexity" section closes with both observations
  stated as uncontroversial, framed as the justification for spending effort on
  complexity management despite measurement difficulty.
- **Confidence**: settled
- **Quote**: "In general, complexity will increase in living software systems unless there is a countervailing effort." — and — "Providing that effort is a worthwhile thing to do."
- **Our assessment**: The chapter's own justification for why simplification is
  a standing program rather than a one-time cleanup. This is the exact statement
  of the entropic-complexity view that the guide's Ch00 principles and Ch04 toil
  playbook need as their premise: any living system (including an agent fleet's
  config/tooling surface) accrues complexity without deliberate countervailing
  investment. Corroborates the embracing-complexity Prodcast's "complexity only
  ever grows" (see Cross-References) from the management side. Settled.

### Claim 5: The cost of complexity is an externality — it does not hit the individual/team/role that introduces it but those who work in and around the system afterward — so a champion for end-to-end simplicity is needed, and SREs are the natural fit because their work requires treating the system as a whole
- **Evidence**: The "Simplicity Is End-to-End, and SREs Are Good for That"
  section states the externality in economic terms, notes production systems
  "grow organically" and accumulate components (the single retry-in-one-
  component → overloaded-database example), and grounds the SRE fit in their
  cross-system visibility. Footnote 3 adds that product-development leads can
  treat SRE as "a useful investment" to attack "complexity as a proxy for
  technical debt."
- **Confidence**: settled
- **Quote**: "Frequently, the cost of complexity does not directly affect the individual, team, or role that introduces it—in economic terms, complexity is an externality. Instead, complexity impacts those who continue to work in and around it. Thus, it is important to have a champion for end-to-end system simplicity."
- **Our assessment**: The role-definition claim: it names *who* owns complexity
  reduction (a designated champion with whole-system scope) and *why* the
  introducer won't do it voluntarily (they don't pay the cost). For the guide
  this is the organizational answer to "who drives simplification of the
  agent/LLM toolchain" — a cross-cutting reliability role, not the owning team.
  The retry-in-one-component example is a compact, quotable illustration of how
  a locally-simple change creates system-level complexity. Settled.

### Claim 6: Product developers work in narrow subsystems and lack a system mental model, so the SRE team usually draws the system-level architecture diagrams; reader actions: have engineers draw (and redraw) system diagrams before first on-call and keep canonical diagrams in docs, and have SREs review all major design docs
- **Evidence**: The same section makes the "narrow subsystem" observation and
  the "SRE team draws the diagrams" observation, followed by the two `Note`
  boxes with the reader actions. The explanation-time proxy (Claim 3) is the
  measurement angle on the same whiteboard-diagram practice.
- **Confidence**: settled
- **Quote**: "In our experience, product developers usually end up working in a narrow subsystem or component. As a result, they don't have a mental model for the overall system, and their teams don't create system-level architecture diagrams." — and — "Reader action: Before an engineer goes on-call for the first time, encourage them to draw (and redraw) system diagrams. Keep a canonical set of diagrams in your documentation: they're useful to new engineers and help more experienced engineers keep up with changes."
- **Our assessment**: Concrete, adoptable practices with a training/on-call
  hook: the canonical-diagram requirement is a documentation artifact the guide
  can mandate for agent-owned services too (an agent that reasons about a system
  needs the same canonical diagram as the human on-caller — see the pDNS and
  Display Ads case studies where SREs' whole-stack view is the simplification
  lever). The "SRE reviews all major design docs" action is a process gate the
  guide's design-review section can cite directly. Settled.

### Claim 7: Case Study 1 (abstract key/value `bag` API vs Protocol Buffers/Thrift) — abstract general-purpose APIs shift complexity to clients, who must document and maintain key/value contracts informally; structured data types force upfront design decisions and documentation, yielding simpler end-to-end solutions
- **Evidence**: The case study's background describes the startup core library
  whose RPCs took and returned a `bag`, with "actual parameters stored as
  key/value pairs inside the bag"; the lesson states the trade explicitly, naming
  Protocol Buffers and Apache Thrift as the structured alternatives.
- **Confidence**: settled
- **Quote**: "Structured data types like Google's Protocol Buffers or Apache Thrift might seem more complex than their abstract general-purpose alternatives, but they result in simpler end-to-end solutions because they force upfront design decisions and documentation."
- **Our assessment**: The "complexity shifted to the interface boundary" pattern
  that maps directly to agent-facing service/API design: a generic free-form
  interface (a bag, an untyped `dict`, a free-text tool schema) looks simple but
  transfers the design burden to every client. For the guide's Ch03 this is the
  argument for structured, typed tool/service contracts over maximally flexible
  ones — and it corroborates the config chapters' "structured types beat
  general-purpose flexibility" stance from the API side. We buy it as a
  first-party lesson (from a startup context, so not scale-dependent).

### Claim 8: Case Study 2 (Borg→Omega rewrite) — compare a rewrite against improving the current system, not against today's status quo; the rewrite chased a moving target, migration cost was underestimated, and wide APIs with lots of users are very hard to migrate
- **Evidence**: The case study lists three serious problems with the planned
  Borg→Omega switch (Borg kept evolving → moving target; improvement of Borg
  proved less hard and Omega expectations overoptimistic — "the grass isn't
  always greener"; millions of lines of config across thousands of services made
  migration "extremely costly in terms of engineering and calendar time" with
  both systems supported for years). Resolution: ideas fed back into Borg and
  Omega's concepts "jump-started Kubernetes."
- **Confidence**: settled
- **Quote**: "Wide APIs with lots of users are very hard to migrate. Don't compare the expected result to your current system. Instead, compare the expected result to what your current system would look like if you invested the same effort in improving it." — and — "During the migration period, which would likely take years, we'd have to support and maintain both systems."
- **Our assessment**: The single most transferable claim for Ch05's legacy
  model-stack migration guidance and Ch03's infrastructure-churn advice: the
  rewrite-vs-improve comparison rule is a decision criterion the guide can state
  directly, and the moving-target problem is the risk of greenfield model
  platforms being built alongside evolving incumbent stacks. Note this is the
  same "rewrite costs are routinely underestimated" theme as the
  infrastructure-change-management and twenty-years-lessons notes (see
  Cross-References) — three independent Google statements of the same lesson.
  Settled.

### Claim 9: Simplification is efficiency — it saves engineering time and cognitive load rather than compute/network — so leadership must celebrate and explicitly prioritize it: treat simplification projects like feature launches and "measure and celebrate code addition and removal equally"
- **Evidence**: The "Regaining Simplicity" section contrasts simplification with
  resource-efficiency ("instead of saving compute or network resources, it saves
  engineering time and cognitive load"), prescribes the feature-launch treatment,
  and cites Google's intranet "Zombie Code Slayer" badge for engineers who
  delete significant amounts of code. Dijkstra's "lines spent" quote is cited in
  footnote 4.
- **Confidence**: settled
- **Quote**: "Treat successful simplification projects just as you treat useful feature launches, and measure and celebrate code addition and removal equally." — and — "For example, Google's intranet displays a "Zombie Code Slayer" badge for engineers that delete significant amounts of code."
- **Our assessment**: The cultural-incentive claim: simplification has no natural
  reward signal, so it must be manufactured (equal celebration, named badges).
  For the guide this is directly load-bearing for agent-era toil reduction —
  simplification is a non-automation toil lever (you can't automate your way out
  of complexity you could instead remove), which connects to eliminating-toil's
  "Reject the Toil" strategy. Settled.

### Claim 10: Simplification is a feature that must be prioritized and staffed — create a dedicated bucket of time, for example "reserve 10% of engineering project time for 'simplicity' projects," and make simplicity an explicit goal for complex systems or overloaded teams
- **Evidence**: The "Regaining Simplicity" section: if developers and SREs don't
  see simplification projects as career-beneficial "they won't undertake these
  projects"; the 10% figure is given as an example. Footnote 5 clarifies the 10%
  budget "doesn't mean the team has a green light to introduce complexity with
  the other 90%."
- **Confidence**: settled
- **Quote**: "Simplification is a feature. You need to prioritize and staff simplification projects and reserve time for SREs to work on them." — and — "For example, reserve 10% of engineering project time for "simplicity" projects."
- **Our assessment**: The budgeting claim Ch04's toil playbook lacks: a concrete,
  citable mechanism for making simplification a standing program rather than
  volunteer work. The footnote's anti-loophole clarification is important for
  the guide to carry — the budget is an allocation, not a license to introduce
  complexity elsewhere. The 10% figure is directional (an example, per the
  source), so we grade the *mechanism* settled and the *number* illustrative.
  Settled.

### Claim 11: As a system grows complex, resist splitting SRE teams into narrower scopes — a small rotating group of SREs who maintain working knowledge of the entire stack (likely with less depth) can push for conformity and simplification across it
- **Evidence**: The "Regaining Simplicity" section argues team-splitting is
  "sometimes necessary" but that reduced scope "might lessen their motivation or
  ability to drive larger simplification projects," then prescribes the rotating
  whole-stack group.
- **Confidence**: settled
- **Quote**: "Consider designating a small rotating group of SREs who maintain working knowledge of the entire stack (likely with less depth), and can push for conformity and simplification across it."
- **Our assessment**: The organizational-design counterweight to Conway's-law
  fragmentation: a deliberate whole-stack role is the structure that backs the
  end-to-end-simplicity champion (Claim 5). Directly relevant to how an LLM-ops
  org staffs platform/SRE ownership across many model-serving teams. Settled.

### Claim 12: Diagramming your system surfaces two named design problems: amplification (multi-level retries multiply the total number of RPCs) and cyclic dependencies (a component depending on itself, often indirectly, can make a cold start of the whole system impossible)
- **Evidence**: The "Regaining Simplicity" section introduces diagramming as a
  first-step simplification practice and defines both look-fors, each with its
  failure mechanism.
- **Confidence**: settled
- **Quote**: "Amplification: When a call returns an error or times out and is retried on several levels, it causes the total number of RPCs to multiply." — and — "Cyclic dependencies: When a component depends on itself (often indirectly), system integrity can be gravely compromised—in particular, a cold start of the whole system might become impossible."
- **Our assessment**: A cheap, concrete first step for simplification that the
  guide can prescribe before any removal work: draw the diagram, hunt for these
  two patterns. Amplification is a retry-hygiene claim that corroborates the
  corpus's thundering-herd/retry material from the complexity side; cyclic
  dependencies are the architectural form of the pDNS case study (Claim 15 here)
  and of the embracing-complexity note's aerodynamic-stability rule. Settled.

### Claim 13: Case Study 3 (Display Ads "spiderweb") — uniformity standards (single way to copy large data sets, single way to perform external data lookups, common monitoring/provisioning/config templates) plus incremental consolidation into unified backends removed redundant lookups, and "redundant lookups in a single request represent a 'system smell'"
- **Evidence**: The case study describes the interconnected acquired-product
  backends (DoubleClick, AdMob, Invite Media), the need to rewrite ad requests to
  meet each targeting system's expectations (adding "the possibility of
  undesirable loops" — at one point tests were added to ensure all infinite
  loops had been removed), the SRE-driven uniformity standards, and the
  consolidation into unified server backends where the auction server performs a
  data lookup once. Figure 7-1/7-2 show the before/after request path.
- **Confidence**: settled
- **Quote**: "Just as the presence of very similar functions in a single program represents a "code smell" that indicates deeper design problems, redundant lookups in a single request represent a "system smell."" — and — "It's best to integrate an already running system into your own infrastructure incrementally."
- **Our assessment**: Two transferable patterns: (1) the "system smell" concept
  — duplicate work in a request path is the system-level analog of duplicated
  code — a diagnostic an agent/observability layer could detect (repeated
  identical lookups per request); (2) incremental consolidation over big-bang
  unification. The uniformity-standards mechanism (standardize first, then
  consolidate) is the same convergence logic as the shared-platform case study
  (Claim 14) and the launch-checklist convergence claim in the corpus. Settled.

### Claim 14: Case Study 4 (hundreds of microservices on a shared platform) — bespoke per-service production stacks incur significant overhead, and a standardized managed microservices platform that bundles best practices lets developer teams "run hundreds of services without any deep SRE engagement," enabling tiered SRE engagement
- **Evidence**: The case study (by Mike Curtis) describes the bespoke-stack
  overhead (dedicated workflows, CI/CD cycles, monitoring, independent SRE
  engagement per vertical) and the social-networking SRE teams' convergence onto
  a single managed platform with UI/API/CLI tools, with new services required to
  use the platform and legacy services migrating or being phased out. Outcomes:
  the "hundreds of services without deep SRE engagement" benefit and tiered SRE
  engagement ("ranging from light consulting and design reviews to deep
  engagement (i.e., SREs share on-call duties)").
- **Confidence**: settled
- **Quote**: "The platform's high quality and feature set had an unexpected benefit: developer teams can run hundreds of services without any deep SRE engagement." — and — "Shifting from sparse or ill-defined standards to a highly standardized platform is a long-term investment. Each step might feel incremental, but ultimately, these steps reduce overhead and make running services at scale possible."
- **Our assessment**: The standardized-platform claim the guide's Ch04/Ch05
  engagement-model content needs: homogenization reduces per-service SRE load,
  and tiered engagement is the staffing consequence. The "incremental wins at
  each stage, don't sell a payoff-only-at-the-end refactor" sequencing advice is
  a concrete change-management rule. Corroborates the launch-checklist-converges-
  on-common-infrastructure theme and the uniform-control-surface claim in the
  corpus (see Cross-References). Settled.

### Claim 15: Case Study 5 (pDNS self-dependency) — a transitive circular dependency broke cold start ("cave dwellers who could only light fires by running with a torch lit from the last campfire"); the fix was a low-level local copy of Svelte server IPs plus an explicit whitelist of services allowed to communicate with pDNS
- **Evidence**: The case study traces the loop (clients look up Svelte via pDNS;
  pDNS's load balancer looks up pDNS server IPs via Svelte), notes lookups
  normally worked because "the pDNS service is replicated, and the data needed
  to break out of the dependency loop was always available somewhere" but "a cold
  start would have been impossible," then describes the fix: a low-level
  production component maintains a list of nearby Svelte server IPs in local
  storage for all production machines, breaking the circular dependency and
  removing an implicit pDNS dependency for most services; whitelisting then
  reduced the set of services allowed to talk to pDNS.
- **Confidence**: settled
- **Quote**: "We were like cave dwellers who could only light fires by running with a torch lit from the last campfire." — and — "Be careful about your service's dependencies—use an explicit whitelist to prevent accidental additions. Also, be on the lookout for circular dependencies."
- **Our assessment**: The cleanest real-world cyclic-dependency case study in
  the corpus and the concrete mechanism behind the Claim 12 look-for: a
  replication-masked cold-start failure that surfaces only at bootstrapping
  time. The two-part fix (break the loop at a low level + whitelist the
  dependency surface) is directly adoptable as dependency-hygiene guidance for
  agent/LLM infrastructure (bootstrap services must not depend on services that
  depend on them). The "cave dwellers" quote makes it memorable and quotable.
  Settled.

### Claim 16: Conclusion — SREs are in an excellent position to identify, prevent, and fix sources of complexity across software design, architecture, configuration, and deployment; they should be involved in design discussions early, proactively develop standards to homogenize production, and treat pushing for simplicity as part of the job — because systems "inevitably creep toward complexity"
- **Evidence**: The chapter conclusion synthesizes the externality/champion
  argument, the early-design-involvement recommendation, the standards-to-
  homogenize-production practice, and the continuous-effort framing, citing
  Gall's Law as the epigraph.
- **Confidence**: settled
- **Quote**: "Because of their end-to-end understanding of a system, SREs are in an excellent position to identify, prevent, and fix sources of complexity, whether they are found in software design, system architecture, configuration, deployment processes, or elsewhere." — and — "Systems inevitably creep toward complexity as they evolve, so the fight for simplicity requires continuous attention and commitment—but it is very much worth pursuing."
- **Our assessment**: The chapter's role summary, and the pairing of "SREs
  involved in design discussions early" with "proactively develop standards to
  homogenize production" is the process skeleton Ch04/Ch00 can cite: prevention
  at design time plus standardization as the standing simplification mechanism.
  Settled.

## Concrete Artifacts

### Artifact A — The five systems-level complexity proxies (verbatim from the chapter)

```
Training time
  How long does it take a new team member to go on-call? Poor or missing
  documentation can be a significant source of subjective complexity.

Explanation time
  How long does it take to explain a comprehensive high-level view of the
  service to a new team member (e.g., diagram the system architecture on a
  whiteboard and explain the functionality and dependencies of each component)?

Administrative diversity
  How many ways are there to configure similar settings in different parts of
  the system? Is configuration stored in a centralized place, or in multiple
  locations?

Diversity of deployed configurations
  How many unique configurations are deployed in production (including binaries,
  binary versions, flags, and environments)?

Age
  How old is the system? Hyrum's Law states that over time, the users of an API
  depend on every aspect of its implementation, resulting in fragile and
  unpredictable behaviors.
```

### Artifact B — The two reader actions (verbatim from the chapter)

```
Reader action: Before an engineer goes on-call for the first time, encourage
them to draw (and redraw) system diagrams. Keep a canonical set of diagrams in
your documentation: they're useful to new engineers and help more experienced
engineers keep up with changes.

Reader action: Ensure that an SRE reviews all major design docs, and that the
team documents show how the new design affects the system architecture. If a
design adds complexity, the SRE might be able to suggest alternatives that
simplify the system.
```

### Artifact C — Diagramming look-fors (verbatim from the chapter)

```
Amplification
  When a call returns an error or times out and is retried on several levels,
  it causes the total number of RPCs to multiply.

Cyclic dependencies
  When a component depends on itself (often indirectly), system integrity can
  be gravely compromised—in particular, a cold start of the whole system might
  become impossible.
```

### Artifact D — The simplification-management apparatus (verbatim-condensed from the chapter)

```
- "Treat successful simplification projects just as you treat useful feature
  launches, and measure and celebrate code addition and removal equally."
- "For example, Google's intranet displays a "Zombie Code Slayer" badge for
  engineers that delete significant amounts of code."
- "Simplification is a feature. You need to prioritize and staff simplification
  projects and reserve time for SREs to work on them."
- "For example, reserve 10% of engineering project time for "simplicity"
  projects." (Footnote 5: the 10% budget "doesn't mean the team has a green
  light to introduce complexity with the other 90%.")
- "Consider designating a small rotating group of SREs who maintain working
  knowledge of the entire stack (likely with less depth), and can push for
  conformity and simplification across it."
```

### Artifact E — Case Study 2 (Borg→Omega) problem list and lesson (verbatim-condensed)

```
The planned switch from Borg to Omega had a few serious problems:
- Borg continued to evolve as Omega was developed, so Omega was always chasing
  a moving target.
- Early estimates of the difficulty of improving Borg proved overly pessimistic,
  while the expectations for Omega proved overly optimistic (in practice, the
  grass isn't always greener).
- We didn't fully appreciate how difficult it would be to migrate from Borg to
  Omega. Millions of lines of configuration code across thousands of services
  and many SRE teams meant that the migration would be extremely costly in terms
  of engineering and calendar time. During the migration period, which would
  likely take years, we'd have to support and maintain both systems.

Lesson: "Wide APIs with lots of users are very hard to migrate. Don't compare
the expected result to your current system. Instead, compare the expected result
to what your current system would look like if you invested the same effort in
improving it." Resolution: ideas fed back into Borg; Omega's concepts
"jump-started Kubernetes."
```

### Artifact F — Case Study 5 (pDNS) problem, fix, and lesson (verbatim-condensed)

```
Problem: pDNS had a transitive dependency on itself (clients → Svelte → pDNS →
Svelte). "Lookups normally didn't run into issues because the pDNS service is
replicated, and the data needed to break out of the dependency loop was always
available somewhere in Google production. However, a cold start would have been
impossible."

Fix: "We modified a low-level component in Google production to maintain a list
of current IP addresses for nearby Svelte servers in local storage for all
Google production machines. In addition to breaking the circular dependency
described earlier, this change also eliminated an implicit dependency on pDNS
for most other Google services." Plus an explicit whitelist: "we also introduced
a method for whitelisting the set of services allowed to communicate with pDNS,
and slowly worked to reduce that set."

Lesson: "Be careful about your service's dependencies—use an explicit whitelist
to prevent accidental additions. Also, be on the lookout for circular
dependencies."
```

### Artifact G — Gall's Law epigraph (verbatim)

```
"A complex system that works is invariably found to have evolved from a simple
system that worked." — Gall's Law (epigraph to the chapter)
```

## Cross-References

### Candidates from miner-related-notes.md (lexical retrieval)

The following candidates from `miner-related-notes.md` were evaluated:

1. **`docs-google-sre-prodcast-03-11-embracing-complexity.md`** (score 0.3077) — **Corroborates** Claim 1 ("once a system won't fit on one whiteboard, you just don't understand anything that's outside the realm of that whiteboard... nothing ever gets less complicated") and Claim 17 (aerodynamic stability — remove dependency cycles so the top of the stack recovers without human interference). The Prodcast's "complexity only ever grows" is the cognitive-side statement of this chapter's "complexity will increase in living software systems unless there is a countervailing effort" (Claim 4 here); its whiteboard heuristic is the pessimistic framing of this chapter's explanation-time proxy and diagramming practice (Claim 3/Claim 6/Claim 12 here); its dependency-cycle removal rule is the same design goal as Case Study 5 (pDNS) and the cyclic-dependencies look-for (Claim 15/Claim 12 here). Also **Claim 3** (automation and abstraction don't simplify — they add new layers) is the cautionary complement to this chapter's simplification drive: this chapter measures and removes complexity; the Prodcast warns that the *fixes* (automation/abstraction) can add complexity. Principle-level corroboration; the two sources target reducible design complexity vs irreducible sociotechnical complexity respectively (a conditioning variable, see Contradicts).

2. **`docs-google-sre-configuration-specifics.md`** (score 0.3077) — **Corroborates** Claim 1 (replication toil vs complexity toil; "Freed from an overwhelming number of individual configs, the project (and its config corpus) grows with renewed energy"). This chapter's administrative-diversity and diversity-of-deployed-configurations proxies (Claim 3 here) are the measurement hooks for the config-specifics note's complexity-toil mechanism: a config corpus with many ways to configure similar settings is precisely where complexity toil materializes. Both are Workbook chapters (Ch7 here, Ch15 there) agreeing that config complexity is a first-class operational concern. See also the sibling Ch14 note below.

3. **`docs-google-sre-eliminating-toil.md`** (score 0.2821) — **Corroborates and Extends** — the closest sibling (Workbook Ch6). This chapter's Claim 4 (complexity increases without countervailing effort) is the complexity-side statement of the toil note's "Grows at least as fast as its source" characteristic (Eliminating Toil **Claim 1**); this chapter's simplification apparatus (Claims 9-11 here) is a *non-automation* toil-reduction lever that directly complements the toil note's "Reject the Toil" strategy (**Claim 7** there); and the five complexity proxies (Claim 3 here) give Ch04 a complexity-measurement framework *parallel to* the toil measurement methodology (**Claim 4** there). See Primary cross-references for the full mapping.

4. **`docs-google-sre-on-call.md`** (score 0.2821) — **Corroborates** Claim 16 (a new SRE team can bootstrap to on-call readiness within three months using a training checklist, lab drills, and shadowing). The on-call note's Claim 16 operationalizes this chapter's training-time proxy (Claim 3 here): the proxy asks "how long does it take a new team member to go on-call?", and the on-call chapter shows the readiness timeline is a manageable, trainable quantity (3 months vs the normal 3–9 months). The two chapters are adjacent (Ch8 on-call is the next workbook chapter) and consistent. Note: the on-call chapter's Claim 1 (at least 50% SRE time on project work, max two incidents per shift) corroborates the workload-budget theme but is not re-extracted here.

5. **`docs-google-sre-prodcast.md`** (score 0.2821) — **Dismissed.** Prodcast index page with episode listings; its Claim 4 (Season 1 episode-to-chapter map covering "risk/simplicity/toil") is a table-of-contents statement, not a simplicity claim. No substantive cross-reference.

6. **`docs-google-sre-data-processing-pipelines.md`** (score 0.2564) — **Corroborates** Claim 6 (pipeline documentation has three categories, including "system diagrams with live per-stage status links"). The data-processing note's system-diagram documentation category is an instance of this chapter's canonical-system-diagrams reader action (Claim 6 here): both prescribe kept-in-docs system diagrams as an operational artifact. The rest of that note (pipeline SLOs, checkpointing, hotspotting) is orthogonal and dismissed.

7. **`docs-google-sre-reliable-product-launches.md`** (score 0.2308) — **Corroborates** Claim 5 (the launch checklist can drive convergence on common infrastructure — "replacing long sections on custom solutions with single-line recommendations to use hardened internal platforms"). The launch-checklist convergence mechanism is the process-side instance of this chapter's Case Study 4 standardization (Claim 14 here) and its "proactively develop standards to homogenize production" conclusion (Claim 16 here): a review gate pushing teams onto shared platforms. The rest of that note (LCE consulting model, launch planning) is dismissed as orthogonal.

8. **`docs-google-sre-prodcast-03-06-incident-response-tooling.md`** (score 0.2308) — **Dismissed.** Incident-response tooling breadth and on-call collaboration ("clumsy automation," severity labels); no simplicity-measurement or simplification-management claims to corroborate or contradict.

9. **`docs-google-sre-prodcast-02-08-life-beyond-google.md`** (score 0.2308) — **Corroborates** Claim 4 (a uniform control surface — Kubernetes — is what finally enables portable, organization-transferable tooling, where heterogeneity made tooling hard). The "uniform control surface → portable tooling" claim is the outside-Google instance of this chapter's Case Study 4 shared-platform outcome (Claim 14 here) — and Case Study 2's note that Omega's concepts "jump-started Kubernetes" is the shared lineage. The rest of that note (scale shock, replication norms) is dismissed.

10. **`docs-google-sre-configuration-design.md`** (score 0.2308) — **Corroborates** Claim 3 (the configuration-philosophy ideal is "no configuration at all" — "it decreases both the surface area for error and cognitive load on the operator") and Claim 4 (user-centric config — fewer knobs; "limited configuration options can paradoxically lead to better adoption"). This chapter's own externality argument links to the configuration-design chapter (the "champion for end-to-end system simplicity" sentence links to `/workbook/configuration-design/`), and its administrative-diversity proxy (Claim 3 here) is the measurement angle on the config chapters' fewer-knobs doctrine. The two Workbook chapters are consistent halves of the same simplicity stance. See Primary cross-references.

### Primary cross-references (from the Prospector's triage and manual search)

- **Corroborates**:
  - `docs-google-sre-eliminating-toil.md` **Claim 4** (toil measurement: objective unit of human effort, continuous tracking, don't let measurement become toil) — this chapter's five complexity proxies (Claim 3 here) are the complexity-domain parallel: where the toil note measures *human effort on toil*, this chapter measures *system comprehension and config/deployment diversity*. Both are data-driven frameworks for tracking a reduction program. Also **Claim 7** (reject the toil first — analyze cost of responding vs not responding) — this chapter's simplification apparatus (Claims 9-11 here) is the "remove rather than automate" complement to rejection.
  - `docs-google-sre-infrastructure-change-management.md` **Claim 3** (the Moonshot GFS→Colossus migration was initially communicated as a 1-year project but took 2 years — the initial communication "completely undersold the effort, complexity, and difficulty") — independent Google evidence for Case Study 2's lesson that migration cost is routinely underestimated (Claim 8 here). The Prospector's triage flagged this note for Hyrum's Law, but the note has no Hyrum's Law claim; the migration-cost theme is the actual corroboration.
  - `docs-google-sre-twenty-years-lessons.md` **Claim 3** (a configuration change the team was "pretty sure" was safe "fully hobbled the service for 13 minutes" — canary all changes) — supports Case Study 2's "grass isn't always greener" caution (Claim 8 here): both are Google statements that changes you're confident in (including rewrites/migrations) can go wrong, so the costs must be weighed against a canaried, incremental path.
  - `docs-google-sre-on-call.md` **Claim 16**, `docs-google-sre-data-processing-pipelines.md` **Claim 6**, `docs-google-sre-reliable-product-launches.md` **Claim 5**, `docs-google-sre-prodcast-02-08-life-beyond-google.md` **Claim 4**, `docs-google-sre-configuration-design.md` **Claims 3 and 4**, `docs-google-sre-configuration-specifics.md` **Claim 1**, `docs-google-sre-prodcast-03-11-embracing-complexity.md` **Claims 1, 3, and 17** — see Candidates list above.

- **Contradicts**: None identified, and no contradiction issue filed. Tension points checked and resolved as conditioning variables:
  - (a) This chapter's "simplicity strongly correlates with reliability / pursue simplicity end-to-end" (Claim 1) vs the embracing-complexity Prodcast's "complexity only ever grows" and "you can't come up with a simple design for a complex problem" (Requisite Variety) — these target different objects. This chapter governs *reducible* (accidental) complexity — measured by CCN, config diversity, deploy diversity — and explicitly concedes system-level measurement is difficult; the Prodcast governs *irreducible* (essential) sociotechnical complexity of large operational systems. The two sources agree at the hinge point: complexity grows without countervailing effort (this chapter Claim 4 = the Prodcast's "nothing ever gets less complicated"). No real opposition.
  - (b) The simplicity chapter's uniformity drive (Case Studies 3-4, "proactively develop standards to homogenize production") vs the twenty-years-lessons note's hardware-diversity claim (Claim 11 there: "Maintaining a diverse infrastructure... can mean the difference between a troublesome outage and a total one") — these apply to different objects: *deployment/config* homogeneity (this chapter's proxy) vs *hardware fleet* diversity (a failure-isolation property). The chapter's own "diversity of deployed configurations" proxy measures how many distinct *configurations* run in production, not how many hardware vendors — no conflict.
  - (c) The chapter's celebration of simplification and removal (Claims 9-11) vs the corpus's "automation is a job in itself" / "automation adds layers" warnings (embracing-complexity Claim 3; eliminating-toil Claim 14) — this chapter's simplification is largely *non-automation* work (removal, consolidation, standardization), which is compatible with the automation-liability warnings rather than opposed to them.

- **Extends**:
  - `docs-google-sre-eliminating-toil.md` — the largest extension. The toil note supplies the toil taxonomy, measurement methodology, and management strategies; this chapter supplies the *complexity* half of the same workbook pair: the five proxies (Claim 3) as a measuring-complexity-reduction framework parallel to the toil-measurement framework, and simplification (Claims 9-11) as the non-automation lever alongside "Reject the Toil." Together they give Ch04 a complete reduce-complexity-and-toil playbook.
  - `docs-google-sre-configuration-design.md` — that note covers config *interface* design (fewer knobs, defaults, safe change); this chapter adds the measurement framing (administrative diversity / deployed-config diversity as complexity proxies) and the "SRE reviews design docs for simplicity" process gate that makes the config doctrine operational.
  - `docs-google-sre-prodcast-03-11-embracing-complexity.md` — that note covers the human/sociotechnical *experience* of complexity; this chapter covers the *management* of complexity (measure it, budget for its removal, staff a champion). The Prodcast's aerodynamic-stability/dependency-cycle rule gains its worked real-world case study in this chapter's pDNS story (Claim 15).
  - `docs-google-sre-infrastructure-change-management.md` — that note documents large-scale migration *execution* (ICM lifecycle, Preflight Checklist); this chapter's Case Study 2 supplies the *decision* layer before migration: the rewrite-vs-improve comparison rule and the wide-API migration-cost warning (Claim 8) that ICM assumes was already made.

- **Novel**: Material new to the corpus:
  - **The five systems-level complexity proxies** (Claim 3, Artifact A) — training time, explanation time, administrative diversity, diversity of deployed configurations, age/Hyrum's Law. No existing note offers a complexity-measurement framework; the corpus measures toil, not complexity.
  - **Complexity-as-externality and the SRE-as-end-to-end-simplicity-champion role** (Claim 5) — the economic argument for why the complexity introducer won't fix it, and the whole-system ownership justification.
  - **The simplification-management apparatus** (Claims 9-11, Artifact D) — the 10% simplicity budget, "measure and celebrate code addition and removal equally," the Zombie Code Slayer badge, and the rotating whole-stack SRE group. The corpus has no "how to fund and staff simplification" content.
  - **Diagramming as a first-step simplification practice with the amplification and cyclic-dependency look-fors** (Claim 12, Artifact C) — a named, reproducible first step.
  - **The "system smell" concept** (Claim 13) — redundant lookups in a request path as the system-level analog of duplicated-code smells.
  - **Case Study 2's rewrite-vs-improve comparison rule and wide-API migration warning** (Claim 8, Artifact E) — a decision criterion no existing note states.
  - **Case Study 4's standardized-shared-platform → tiered-SRE-engagement pattern** (Claim 14) — hundreds-of-services-without-deep-engagement as a platform outcome.
  - **Case Study 5's pDNS transitive self-dependency and the whitelist fix** (Claim 15, Artifact F) — the "cave dwellers" cold-start story and the explicit-dependency-whitelist practice.
  - **The SRE-reviews-design-docs and canonical-system-diagrams process gates** (Claim 6, Artifact B) — concrete design-review and documentation practices.

## Guide Impact

- **Chapter 04 (oncall-and-toil)**: The primary target per triage. (1) Add a *measuring complexity reduction* subsection to "Measuring toil reduction": the five complexity proxies (Claim 3, Artifact A) as the complexity-side analog of the toil-measurement methodology — training time and explanation time tracked per engineer/on-call readiness, administrative diversity and diversity of deployed configurations counted directly from the config corpus and deployment inventory (both countable by an agent layer, matching the toil note's countable units). (2) Add *simplification as a non-automation toil lever* to the toil-management playbook: the 10% simplicity budget (Claim 10), celebrate-code-deletion (Claim 9), and the rotating whole-stack SRE group (Claim 11) sit alongside "Reject the Toil" as levers that precede or replace automation. (3) Add *diagram-to-find-amplification-and-cycles* (Claim 12) as the cheap first step before removal work.
- **Chapter 03 (runbooks-and-agents)**: (1) Use the complexity proxies (Claim 3) as inputs to "which systems can an agent safely reason about": a service whose explanation time is low and whose config/deploy diversity is low is a system an agent can hold a complete-enough model of; a system failing the whiteboard test (per the embracing-complexity note) is not. (2) Add Case Study 1's lesson (Claim 7) as API/tool-interface guidance: agent-facing service interfaces should use structured, typed contracts that force design decisions rather than maximally flexible free-form ones. (3) Add Case Study 2's wide-API migration warning (Claim 8) to agent-infrastructure churn guidance: a wide tool/API surface is expensive to migrate, so compare churn against improving the current surface.
- **Chapter 05 (llm-ops-reliability)**: (1) Add Case Study 2's rewrite decision rule (Claim 8, Artifact E) to the legacy model-stack migration content: compare a model-stack rewrite against improving the current stack with the same effort, plan the full migration window (both systems supported during it), and expect wide-API (wide model/tool surface) migration to be hardest. (2) Add Case Study 4's shared-platform → tiered-engagement pattern (Claim 14) to the engagement-model content: a standardized model-serving platform is what makes "hundreds of services without deep SRE engagement" possible. (3) Add Case Study 5's dependency hygiene (Claim 15) to bootstrapping/dependency guidance: explicit whitelists for who may depend on core services, and watch for transitive circular dependencies that mask cold-start failure.
- **Chapter 00 (principles)**: Add the complexity-externality principle (Claim 5) and Gall's Law (Artifact G) to the principles that justify reliability investment: complexity is a cost paid by operators, so it needs a designated whole-system champion.
- **Chapter 01 (incident-response)**: Add the pDNS cyclic-dependency case study (Claim 15) to the dependency-hygiene / bootstrapping-reliability material — the "replicated so it works in steady state, impossible to cold start" failure mode is the canonical example of a dependency-cycle incident waiting to happen.

## Extraction Notes

- **Source read**: The chapter at `https://sre.google/workbook/simplicity/` was fetched and read end-to-end in a single WebFetch (full chapter text: intro, Measuring Complexity, Simplicity Is End-to-End, both reader-action Notes, all five case studies with backgrounds/decisions/lessons, conclusion, and all five footnotes). It is a single self-contained page; linked pages (SRE Book Ch8 simplicity, configuration-design Ch14, arXiv complexity review, AWS formal-reasoning slides) are references already partly covered by existing source notes and were not followed per the Prospector's guidance.
- **Quote verification**: All quotes were copied character-for-character from the fetched page text. Characters to note for the Assayer: the source uses em dashes ("—") inside quoted passages (e.g., the externality quote in Claim 5, the cyclic-dependencies quote in Claim 12) and inline double quotes inside quoted passages (e.g., the "system smell" passage in Claim 13, the Zombie Code Slayer passage in Claim 9); those inner double quotes are the page's own characters and were kept verbatim. Multi-part quotes are joined with "— and —" per the corpus convention; no two non-adjacent sentences were spliced into a single quoted passage.
- **Related-notes candidates (`miner-related-notes.md`) — dispositions**: All ten candidates are disposed of in the Cross-References → Candidates subsection (8 cited or cross-referenced, 2 dismissed: `docs-google-sre-prodcast.md` and `docs-google-sre-prodcast-03-06-incident-response-tooling.md`). The candidates file itself is not committed.
- **Prospector flag on Hyrum's Law**: The second triage comment listed `docs-google-sre-infrastructure-change-management.md` as overlapping on "Hyrum's Law / change side." That note has no Hyrum's Law claim; the actual overlap is the migration-cost theme (its Claim 3), cited under Primary cross-references. The age/Hyrum's Law proxy here (Claim 3) remains novel to the corpus.
- **Contradiction check**: No contradiction issue was filed. Three potential tensions were checked and resolved as conditioning variables (see Cross-References → Contradicts): the simplicity-chapter's simplicity drive vs the embracing-complexity Prodcast's complexity-is-irreducible view (different objects: reducible vs irreducible complexity); config/deploy homogeneity vs hardware diversity (different objects); and simplification-as-removal vs automation-adds-layers warnings (compatible levers). No open `contradiction`-labeled issues exist.
- **Cross-reference verification**: Per MINER.md §4b, every cited claim number was confirmed against the actual `### Claim:` headings in the cited notes before writing: prodcast-03-11 Claims 1, 3, 17; configuration-specifics Claim 1; eliminating-toil Claims 1, 4, 7; on-call Claim 16; data-processing-pipelines Claim 6; reliable-product-launches Claim 5; prodcast-02-08 Claim 4; configuration-design Claims 3, 4; infrastructure-change-management Claim 3; twenty-years-lessons Claim 3.
- **Confidence rationale**: `confidence_overall: settled`. The source is the canonical Google SRE Workbook, authored by named Google SRE practitioners, hosted on the official sre.google domain; the claims are prescriptive doctrine and first-party case-study lessons. The 10% simplicity budget (Claim 10) is graded settled for the *mechanism* with the number itself explicitly illustrative in the source (footnote 5).
- **WebFetch caveat**: the fast-model WebFetch of the sre.google page returned the chapter's full text in structured form. Spot-check any high-value quotes (especially Claims 3, 5, 8, 13, 15 and Artifacts A-F) against the live URL if the Assayer wants extra confidence.
