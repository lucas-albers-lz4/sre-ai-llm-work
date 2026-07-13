---
source_url: https://sre.google/classroom/
source_type: docs
title: "SRE Classroom: NALSD and SRE Workshops"
author: "Google SRE (Salim Virji, James Youngman, Henry Robertson, Stephen Thorne, Dave Rensin, Zoltan Egyed, Richard Bondi for the NALSD chapter)"
date_published: 2021
date_extracted: 2026-07-13
last_checked: 2026-07-13
status: current
confidence_overall: settled
issue: "#13"
---

# SRE Classroom: NALSD and SRE Workshops

> An index page for Google's SRE Classroom workshops, accompanied by the
> substantive NALSD (Non-Abstract Large System Design) chapter from the SRE
> Workbook. The classroom page itself is a thin landing page; the NALSD
> workbook chapter provides the actual methodology: an iterative system design
> process combining capacity planning, component isolation, and graceful
> degradation, with a full worked example (AdWords CTR) spanning five design
> iterations. Established SRE fundamentals from the definitive authority.
> Direct AI/LLM relevance is low — this is foundational SRE education, not
> AI-specific patterns.

## Source Context

- **Type**: docs (Google SRE Classroom index page + linked SRE Workbook chapter)
- **Author credibility**: Google SRE — the originators of the SRE discipline.
  The NALSD workbook chapter is attributed to seven named Google SREs (Salim
  Virji, James Youngman, Henry Robertson, Stephen Thorne, Dave Rensin, Zoltan
  Egyed, with Richard Bondi) and published as Chapter 12 of *The Site
  Reliability Workbook* (O'Reilly). The Art of SLOs workshop was developed by
  Google's Customer Reliability Engineering (CRE) team. All materials are
  released under Creative Commons CC-BY-4.0.
- **Scope**: The classroom landing page (the filed source) indexes three
  workshops — Distributed PubSub, Distributed ImageServer, and The Art of SLOs
  — and links to supplementary NALSD resources. The page itself contains no
  code, metrics, configs, or deep patterns. Two linked pages were followed per
  MINER.md §1: the NALSD workbook chapter (`/workbook/non-abstract-design/`,
  Chapter 12 of the SRE Workbook) which provides the full NALSD methodology and
  a worked example; and the Art of SLOs resource page
  (`/resources/practices-and-processes/art-of-slos/`) which describes the SLO
  workshop format and links to PDF materials. The workshop sub-pages
  (Distributed PubSub, Distributed ImageServer) are separately filed as issues
  #14 and #15 and were not followed — their substantive content is mined
  independently.
- **Does NOT cover**: AI/LLM operations, agent reliability, LLM observability,
  generative system failure modes, or any AI-specific patterns. The source
  describes general-purpose SRE methodology applicable to any large distributed
  system.

## Extracted Claims

### Claim 1: NALSD combines capacity planning, component isolation, and graceful degradation into an iterative design methodology that produces robust, scalable systems with low operational costs
- **Evidence**: Authoritative — described as the core definition in the
  official SRE Workbook chapter, authored by seven Google SREs. The full
  worked example (AdWords CTR) demonstrates each element: capacity planning
  (resource calculations at each iteration), component isolation (separate
  QueryStore, LogJoiner, ClickMap, QueryMap), and graceful degradation
  (duplicate shards, Paxos replication, stale-data fallback).
- **Confidence**: settled
- **Quote**: "By following an iterative style of system design and
  implementation, we arrive at robust and scalable designs with low operational
  costs. We call this style Non-Abstract Large System Design (NALSD)."
- **Our assessment**: This is a canonical definition from the definitive
  source. The three elements (capacity planning, component isolation, graceful
  degradation) form a coherent framework that generalizes beyond Google. The
  claim is well-supported by the worked example that follows in the chapter.

### Claim 2: The "non-abstract" requirement — that designs must translate to real hardware and real networks — is the distinguishing feature of NALSD, and skipping it leads to systems that cannot be physically realized
- **Evidence**: Google's operational experience. The chapter states this
  requirement emerged from observing that designers who don't practice
  converting abstract designs to concrete resource estimates create systems
  that can't run on real infrastructure. Each iteration in the AdWords example
  includes concrete resource calculations (disk IOPS, RAM, network bandwidth)
  rather than remaining at the whiteboard level.
- **Confidence**: settled
- **Quote**: "All systems will eventually have to run on real computers in real
  datacenters using real networks."
- **Our assessment**: This is the core pedagogical insight of NALSD and what
  distinguishes it from abstract system design interviews. The requirement for
  concrete resource estimates (machine counts, RAM, network throughput) forces
  designers to confront physical constraints early. This is well-established
  SRE practice at Google and the reasoning is sound: abstract designs hide
  infeasibility; concrete estimates reveal it.

### Claim 3: The NALSD design process has two phases and five questions: (Phase 1) Is it possible? Can we do better? (Phase 2) Is it feasible? Is it resilient? Can we do better?
- **Evidence**: The chapter explicitly structures the process this way and
  applies it throughout the AdWords CTR worked example. Phase 1 (Basic Design)
  assumes no resource constraints; Phase 2 (Scaling) introduces real
  constraints on money, hardware, and failure domains. The "Can we do better?"
  question is asked in both phases as a recurring optimization check.
- **Confidence**: settled
- **Quote**: "Phase 1: Basic Design Phase — 1. Is it possible? 2. Can we do
  better? Phase 2: Scaling Phase — 3. Is it feasible? 4. Is it resilient? 5.
  Can we do better?"
- **Our assessment**: The two-phase structure is a practical mental model for
  system design. Phase 1 prevents premature optimization by removing resource
  constraints; Phase 2 introduces reality. The repetition of "Can we do
  better?" at both phases creates a built-in optimization checkpoint. This
  framework is directly teachable and applies beyond Google.

### Claim 4: Starting with a single-machine design and iterating through bottlenecks is the recommended NALSD approach — it reveals constraints that abstract multi-machine designs hide
- **Evidence**: The AdWords CTR worked example begins with a single-machine
  baseline (Iteration 1), calculates concrete bottlenecks (86.4 TB/day storage,
  2,500 disks for IOPS, 1,563 machines for RAM), and only then progresses to
  distributed designs. Each subsequent iteration adds one new concern: Iteration
  2 (MapReduce/batching), Iteration 3 (LogJoiner/streaming), Iteration 4
  (sharding), Iteration 5 (multi-datacenter with Paxos).
- **Confidence**: settled
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The single-machine baseline pattern is pedagogically
  powerful — it forces designers to see which resource is the bottleneck (disk
  IOPS? RAM? network?) before distributing the system. This prevents the common
  antipattern of proposing a distributed architecture without understanding
  which constraint actually drives the distribution. The iterative,
  one-concern-at-a-time approach is a teachable methodology.

### Claim 5: Components should be separated by expected growth patterns to enable independent scaling, and removing dependencies on single hardware or software instances is a core NALSD outcome
- **Evidence**: In the final AdWords design, QueryStore, QueryMap, ClickMap, and
  LogJoiner are separate components because each has different growth
  characteristics (QueryStore grows linearly with query volume; ClickMap grows
  with click volume at ~2% of query volume; LogJoiner throughput is bounded by
  click rate). The chapter explicitly states this separation criterion.
- **Confidence**: settled
- **Quote**: "Throughout this process, we separated software components based
  on how we expected the system to grow." "This strategy allowed us to scale
  different parts of the system independently" and "removed dependencies on
  single pieces of hardware or single instances of software, thereby producing
  a more reliable system."
- **Our assessment**: "Separate by growth axis" is a concise, actionable design
  heuristic. It's more specific than "separate concerns" — it tells the
  designer *which* dimension to separate on. The independent scaling and
  removal of single-hardware/software dependencies are the concrete benefits
  the source identifies. This principle generalizes well beyond the AdWords
  example and is directly applicable to any system design exercise.

### Claim 6: NALSD is a learned skill requiring regular practice, not a one-time exercise — Google's experience shows that reasoning from abstract requirements to concrete resource approximations is "critical to building healthy and long-lived systems"
- **Evidence**: The chapter states this explicitly in its conclusion. The SRE
  Classroom workshops exist specifically to provide hands-on NALSD practice
  (Distributed PubSub, Distributed ImageServer). The classroom page frames the
  workshops as providing "hands-on experiences with applying these principles
  to the design and evaluation of these systems."
- **Confidence**: settled
- **Quote**: "NALSD is a learned skill. As with any skill, you need to practice
  it regularly to maintain your proficiency."
- **Our assessment**: This claim is significant because it positions NALSD as a
  practiced discipline rather than a memorized checklist. The existence of
  multiple workshops (PubSub, ImageServer, SLOs) with different domain problems
  supports the claim that varied practice is needed. The classroom format
  (interactive workshops, not lectures) reinforces the hands-on learning model.

### Claim 7: The Art of SLOs workshop teaches a four-step process for developing SLIs, applied to user-server interactions, and frames error budgets as a mechanism to resolve organizational tension between dev and ops teams
- **Evidence**: From the Art of SLOs resource page. The page states the
  workshop was developed by Google's CRE team and covers: (1) setting
  reliability targets to resolve organizational tension, (2) data-driven and
  user-focused SLOs and error budgets, (3) qualities of good SLIs, (4) a
  four-step SLI development process. The actual methodology details are in the
  linked PDF slide decks and handbooks, not on the page itself.
- **Confidence**: settled (the workshop exists and covers these topics;
  anecdotal for the specific four-step process since the details are in linked
  PDFs not extracted here)
- **Quote**: "it is far easier to have a meaningful conversation about the
  reliability of a service when you have an objective way of measuring that
  reliability."
- **Our assessment**: The Art of SLOs page is, like the classroom landing page,
  an index to workshop materials rather than self-contained content. The claim
  about error budgets resolving organizational tension is a core SRE principle
  (documented extensively in the SRE books). The four-step SLI process is
  referenced but not detailed on this page — the substance is in the PDF slide
  decks. For this reason, this claim is noted but not deeply extracted.

### Claim 8: The classroom landing page positions NALSD as "fundamental to SRE" and asserts that understanding its principles "provides a basis for having meaningful conversations about the design and operation of large software systems"
- **Evidence**: Direct statement from the classroom landing page. The page
  frames the workshops as introductory ("introduce participants to the
  principles of NALSD") with hands-on practice.
- **Confidence**: settled
- **Quote**: "NALSD is a concept fundamental to SRE, and understanding its
  principles provides a basis for having meaningful conversations about the
  design and operation of large software systems."
- **Our assessment**: This is Google SRE's own positioning of NALSD's
  importance — it's not just a design exercise but a prerequisite for
  meaningful engineering discussions about large systems. This framing
  explains why Google invests in classroom workshops rather than just
  publishing the methodology.

## Concrete Artifacts

### The NALSD Two-Phase, Five-Question Framework

From the SRE Workbook Chapter 12 ("Introducing Non-Abstract Large System
Design"):

```
Phase 1: Basic Design Phase (no resource constraints)
  1. Is it possible?
     → If no constraints on RAM, CPU, network bandwidth existed,
       what design would satisfy requirements?
  2. Can we do better?
     → Can the system be faster, smaller, more efficient?
     → If O(N), can it become O(ln(N))?

Phase 2: Scaling Phase (real constraints on money and hardware)
  3. Is it feasible?
     → Can this design scale given real constraints?
     → If needed, what distributed design works?
  4. Is it resilient?
     → Can the design fail gracefully?
     → What happens when a component fails? A datacenter fails?
  5. Can we do better?
     → Optimization check applied again at this phase
```

The process is iterative — practitioners "bounce around between the questions
and phases," and iteration continues until a design passes all phases.

### AdWords CTR Design Iterations

From the NALSD workbook chapter. A complete worked example spanning five
iterations:

```
Iteration 1: Single Machine
  - Storage: 86.4 TB/day query logs + click logs → ~100 TB/day
  - IOPS: 500K queries/sec ÷ 200 IOPS/disk = 2,500 disks
  - RAM: 100 TB ÷ 64 GB/machine = 1,563 machines
  - Verdict: Unfeasible — multiple single points of failure

Iteration 2: Distributed — MapReduce
  - Batch processing of query and click logs
  - Verdict: Scales horizontally but cannot meet 5-minute freshness SLO
    (batch boundary problem: query in batch 1, click in batch 2)

Iteration 3: LogJoiner Design (Streaming)
  - QueryStore: full query log, keyed by query_id (~100 TB/day)
  - LogJoiner: continuous click-stream join against QueryStore
  - ClickMap: ad_id → clicks (20 GB/day)
  - QueryMap: ad_id → query_ids (2 TB/day)
  - Network: ~400 Mbps aggregate (manageable)
  - Verdict: Feasible single-datacenter, but checkpointing at scale
    is unresolved

Iteration 4: Sharded LogJoiner
  - Shard by hash(query_id) mod N for LogJoiner consistency
  - Shard by ad_id for QueryMap serving
  - Duplicate shards for reliability (two LogJoiners per shard)
  - Verdict: Handles machine failures within datacenter,
    but whole-datacenter failure is unaddressed

Iteration 5: Multi-Datacenter with Paxos
  - 3-5 Paxos replicas of shared state per datacenter
  - ~25 ms per Paxos operation (cross-DC latency)
  - 40 ops/sec per sequential process
  - 10K clicks/sec → 250+ processes × 5 datacenters = 25,500 tasks
  - 4 TB RAM per datacenter → 64 machines × 64 GB each
  - Network: 256 Mbps per machine (25% of 1 Gbps link)
  - Verdict: Meets all requirements (10K clicks/sec, 500K queries/sec,
    99.9% dashboard < 1 sec, data < 5 min old)
```

### NALSD Component Separation Heuristic

From the NALSD workbook chapter conclusion:

Components are separated by expected growth patterns — each component has a
different scaling characteristic:
- **QueryStore**: grows with total query volume
- **ClickMap**: grows with click volume (~2% of query volume)
- **QueryMap**: grows with (queries × ads per query)
- **LogJoiner**: throughput bounded by click rate, horizontally scalable

This enables independent scaling and removes single-hardware/software
dependencies.

### SRE Classroom Workshop Descriptions

From the classroom landing page — the three workshops offered:

1. **Distributed PubSub**: "Build a planet scale distributed PubSub system
   using NALSD principles." Topics: correctness, reliability, performance,
   inter-system communication styles. (Separately filed as issue #14)

2. **Distributed ImageServer**: "Build a planet scale distributed ImageServer
   system using NALSD principles." Topics: sharding, replication, latency,
   load balancing. (Separately filed as issue #15)

3. **The Art of SLOs**: Introduces SLIs and SLOs measurement with hands-on
   practice. Topics: setting reliability targets, error budgets, four-step
   SLI development process, proxy measures for user expectations.

### Supplementary NALSD Resources

From the classroom landing page:

- NALSD Flash Cards (A4 and US Letter PDFs)
- NALSD chapter in the SRE Workbook (`/workbook/non-abstract-design/`)
- All materials released under Creative Commons CC-BY-4.0

## Cross-References

- **Corroborates**: None. No existing source notes cover general SRE
  fundamentals or design methodology. The existing corpus
  (`blog-pagerduty-sre-agent-architecture.md`,
  `blog-pagerduty-production-ai-agent-gaps.md`,
  `blog-incidentio-ai-sre-incident-run.md`,
  `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`) all cover
  AI-specific agent engineering, observability, and incident response —
  a separate domain from the general SRE design methodology in this source.

- **Contradicts**: None identified. This source describes foundational SRE
  methodology; the existing notes describe AI agent engineering. The domains
  are complementary rather than overlapping.

- **Extends**: None directly. This source establishes a new domain of coverage
  (SRE fundamentals and system design methodology) that future AI-specific
  design notes could build on — e.g., a source on "applying NALSD to LLM
  agent architecture design" would extend this note.

- **Novel**: The following elements are new to the corpus:
  - **NALSD methodology**: The two-phase, five-question iterative design
    framework with concrete resource estimation
  - **Single-machine baseline pattern**: Start with one machine, calculate
    bottlenecks, iterate — as a teachable design approach
  - **Separate-by-growth-axis heuristic**: Component decomposition based on
    expected scaling characteristics
  - **Error budgets as organizational tension resolution**: The framing of
    SLOs/error budgets as a mechanism to resolve dev/ops conflict, not just
    a reliability metric
  - **The NALSD concept itself**: The requirement that system designs must
    translate to real hardware with concrete resource estimates

## Guide Impact

This source has **low direct AI/LLM relevance**. The Prospector's triage
assessment correctly identifies that "none of these specifically address
AI/LLM operations, agent reliability, LLM observability, or the failure modes
unique to generative systems." The following are the best-available mappings,
but they are general principles applied to a domain the source doesn't
address:

- **Chapter 00 (Principles)**: The NALSD iterative design approach (start
  simple → identify bottlenecks → add complexity one concern at a time →
  verify against concrete constraints) provides a methodological template for
  designing AI agent architectures. However, this is a general engineering
  principle applied by analogy, not a claim the source itself makes about
  AI systems.

- **Chapter 03 (Runbooks and Agents)**: The "separate by growth axis"
  heuristic could inform agent decomposition — e.g., separating an agent
  system into components based on which resources each agent type consumes
  (LLM calls, tool calls, memory). The iterative design pattern (single agent
  → identify bottlenecks → distribute) could parallel the architecture
  evolution patterns already documented in
  `blog-pagerduty-sre-agent-architecture.md` (Claim 16, building distributed-first as methodology)
  and `blog-pagerduty-production-ai-agent-gaps.md` (Claim 8, earn complexity).

- **Chapter 05 (LLM Ops Reliability)**: The SLO/SLI methodology (Claim 7)
  provides the general framework for setting reliability targets, which could
  be applied to LLM service SLOs. However, the source does not address
  LLM-specific SLO challenges (non-deterministic outputs, semantic
  correctness, hallucination rates).

**Recommendation**: This source is best treated as **prerequisite knowledge**
rather than guide content. The NALSD methodology underpins how Google SREs
think about system design, and the guide can assume this knowledge rather than
teach it. If the guide needs a reference for "what is NALSD" or "how does SRE
approach system design," this source note provides the canonical definition.
But it should not drive specific AI/LLM recommendations — the domain gap is
too wide.

## Extraction Notes

- The primary source (`sre.google/classroom/`) is a thin landing page — it
  indexes three workshops and links to supplementary resources. It contains no
  code, no metrics, no detailed patterns, and no AI-specific content. The
  Prospector's second triage comment correctly assessed this: "This is a
  landing page/index for Google's SRE Classroom workshops. It does not contain
  deep patterns, code, configs, metrics, or failure details to extract."

- Two linked pages were followed per MINER.md §1:
  1. `/workbook/non-abstract-design/` (Chapter 12 of the SRE Workbook) —
     substantive; provided the NALSD methodology, five-iteration worked
     example, and component separation heuristic extracted as Claims 1-6
     and Concrete Artifacts.
  2. `/resources/practices-and-processes/art-of-slos/` — moderate; describes
     the SLO workshop format and links to PDF materials. The actual SLO
     methodology details are in the linked Google Slides and PDFs, which were
     not fetched (they are presentation files, not web pages). Claim 7 is
     extracted at summary level only.

- The workshop sub-pages (`distributed-pubsub/`, `imageserver/`) are separately
  filed as issues #14 and #15 and were deliberately not followed — they are
  being mined independently. Cross-references to those notes should be added
  once they are extracted.

- Quotes were extracted via WebFetch. All quotes marked as direct were copied
  from the fetched page content. The Assayer should verify these against the
  live URLs at `sre.google/classroom/` and `sre.google/workbook/non-abstract-design/`.

- The source is authoritative (Google SRE) and the NALSD methodology is
  published in the official SRE Workbook. The resource calculations in the
  AdWords example use aggressive rounding (e.g., 86.4 TB/day rounded to 100
  TB) and the chapter explicitly notes that "examples of sound reasoning and
  assumption making are more important than any final values."

- The confidence_overall of "settled" reflects the canonical nature of this
  content — NALSD is a published Google SRE methodology, not an emerging or
  anecdotal practice. This confidence applies to the NALSD content itself, not
  to its applicability to AI/LLM systems (which is low).

- No part of the source was paywalled. All pages are publicly accessible under
  Creative Commons CC-BY-4.0.

- If future issues file the NALSD workbook chapter as a separate source, this
  note should be cross-referenced with that deeper extraction. The current
  extraction covers the classroom page + the NALSD chapter at reasonable depth
  for a source note originally filed against the classroom landing page.
