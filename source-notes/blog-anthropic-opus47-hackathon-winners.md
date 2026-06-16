---
source_url: https://claude.com/blog/meet-the-winners-of-built-with-opus-4-7-claude-code-hackathon
source_type: blog-post
title: "Meet the winners of the Built with Opus 4.7 Claude Code hackathon"
author: Anthropic (Claude team)
date_published: 2026-06-15
date_extracted: 2026-06-16
last_checked: 2026-06-16
status: current
confidence_overall: emerging
issue: "#1190"
---

# Meet the winners of the Built with Opus 4.7 Claude Code hackathon

> A six-project hackathon showcase that extends the Opus 4.6 accessibility
> pattern into new domains (medical education, electronics repair, factory
> maintenance, home repair) while documenting three capabilities new since
> April 2026: Opus 4.7 visual schematic reasoning, Claude Managed Agents as
> infrastructure accelerant, and structured JSON context injection that raised
> eval scores from 74% to 81% without touching the system prompt.

## Source Context

- **Type**: blog-post (official claude.com/blog, June 15 2026; post-hackathon
  winner announcement with six prize categories)
- **Author credibility**: First-party Anthropic editorial post featuring six
  winning projects from a structured, judged competition. Claims about what was
  built are grounded in named individuals with verifiable backgrounds (an
  Istanbul-based physician, a France-based electronics repair technician, a
  Chilean computer science instructor, a 20-year-old with no programming
  experience). Evidence quality is concrete — named metrics (74%→81% eval
  improvement, five agents in parallel, four separate Claude Code sessions),
  named institutions (three medical faculties, a pharma company), and direct
  winner quotes. Treat as high-credibility anecdotal evidence from a structured
  competition, not as a controlled study.
- **Scope**: Covers six prize categories and six winners/teams: Medkit (1st
  place, medical education), Wrench Board (2nd, electronics repair diagnostics),
  Maieutic (3rd, CS education IDE), Virtual Puppet Theater (Most Creative Use of
  Opus 4.7), MaestrIA (Keep Thinking Prize, home repair diagnostics), ARIA (Best
  Use of Claude Managed Agents, factory maintenance). Includes direct quotes from
  winners and specific technical metrics. Does NOT cover: competition scale
  (participant count not stated in this post), architecture diagrams, model-level
  details, cost, or failure cases encountered during development. All six projects
  completed within a hackathon week.

## Extracted Claims

### Claim 1: Injecting domain knowledge as a structured JSON configuration — without modifying the system prompt — raised a home-repair diagnostic tool's eval score from 74% to 81%

- **Evidence**: Named project (MaestrIA), named winner (Benjamin Torralbo),
  specific injection contents: 17 diagnostic rules, 7 native woods, 16 trade
  dialect terms, 19 benchmark prices, and 9 common craft mistakes distilled
  from interviews with his father (a master carpenter). Quantified outcome: eval
  score rose from 74% to 81% against a human master's judgment. Real-time
  streaming diagnostics with animated bounding boxes also described.
- **Confidence**: anecdotal (single project report; improvement vs. human
  master's judgment is domain-specific and not independently verified)
- **Quote**: (no direct quote from winner on the JSON technique itself; see
  paraphrase in Our assessment)
- **Our assessment**: This is the most concrete context engineering data point
  in the hackathon — a before/after improvement (74%→81%) attributed entirely
  to structured domain knowledge injection in configuration, not prompt tuning.
  The mechanism: Torralbo interviewed his father, extracted domain vocabulary and
  heuristics, and encoded them as JSON. The system prompt was unchanged. For the
  guide, this is the clearest demonstration that context engineering (what you
  put in the context) is separable from prompt engineering (how you word the
  instructions), and that domain-expert-sourced content can substitute for
  sophisticated prompt design. The pattern is directly replicable: interview a
  domain expert, enumerate their decision rules and vocabulary, inject as config.

### Claim 2: ARIA's builders explicitly credit Claude Managed Agents as the reason a factory-maintenance agent system was completable in a hackathon week — without it, infrastructure alone would have taken five weeks

- **Evidence**: Named project (ARIA), named team (Idriss Benguezzou, French
  industrial-software engineer with Master's in data/AI; Adam Hnaien,
  self-taught, Claude Code experienced). Five agents continuously watch factory
  machines, detecting failures and predicting imminent breakdowns. Managed Agents
  handled sandboxed Python environment, session persistence, and MCP dispatching.
  Claude Code wrote approximately 80% of raw code lines; builders handled domain
  logic and design decisions.
- **Confidence**: anecdotal (single team's assessment; but both builders are
  technically credible — one with formal data/AI credentials, one self-taught
  with existing Claude Code experience — and the infrastructure list they cite
  as "what Managed Agents handled" is accurate per independent corpus knowledge)
- **Quote**: "Without Claude Managed Agents, we'd have spent the week building
  infrastructure...instead, we spent that week building the product."
- **Our assessment**: ARIA provides the clearest practitioner statement in the
  corpus of the infrastructure-vs-product tradeoff that Managed Agents is
  designed to resolve. The five-weeks estimate (for infrastructure alone) is
  consistent with the Managed Agents announcement post's claim that production
  agents previously required "months" of infrastructure work. The ARIA quote
  belongs alongside the Sentry and Atlassian testimonials from the Managed
  Agents launch post as primary evidence for this tradeoff. Critically, ARIA
  is an industrial IoT domain — factory machine predictive maintenance — which
  extends the Managed Agents evidence base beyond enterprise software into
  operational technology and hardware-adjacent domains.

### Claim 3: Wrench Board uses Opus 4.7's visual understanding of electronic schematics and boardviews to generate diagnostics — a capability the builders explicitly describe as new in Opus 4.7

- **Evidence**: Named project (Wrench Board), named winner (Alexis Chapellier,
  Reignier-Ésery, France, independent electronics repair technician). Users upload
  schematics and boardviews describing symptoms; the agent creates unified
  electrical graphs, identifies exact points to probe, processes measurements, and
  iterates diagnoses. Screenshot-based feedback loops used for spatial reasoning.
  Five to six agents running in parallel during debugging.
- **Confidence**: anecdotal (single project report; visual schematic understanding
  is documented as an Opus 4.7 capability in the Opus 4.7 best practices note, but
  the diagnostics quality and the specific schematics/boardview understanding claim
  are not independently benchmarked here)
- **Quote**: "I watched Wrench Board's boardview light up step by step, arrows
  appearing, components getting pointed at, names surfacing."
- **Our assessment**: The Chapellier quote describes a qualitative outcome —
  the agent navigating a boardview graphically, not just textually. This is
  qualitatively different from the vision capabilities documented in the Opus 4.6
  hackathon (which used vision for road infrastructure photos, not technical
  engineering schematics). The specific combination — boardview spatial understanding
  + schematic tracing + diagnostic graph generation — is a use of Opus 4.7's visual
  reasoning in a dense, domain-specific technical document type (PCB boardviews)
  that does not appear elsewhere in the corpus. The 5-6 parallel agents used during
  development (benchmarking in parallel per domain) is a concrete development
  methodology worth documenting separately.

### Claim 4: Maieutic implements an Intent-Diff Review — an automated comparison of student code against a prior specification that classifies divergence as drift, revision, or bug

- **Evidence**: Named project (Maieutic), named winner (Paula Vásquez-Henríquez,
  computer science instructor, Universidad del Desarrollo, Chile). IDE features:
  locked editor until spec is detailed, disabled autocomplete, redirected reasoning
  questions, and Intent-Diff Review as the core feedback mechanism. Claude compares
  specs against code and classifies divergences. Live instructor dashboard with
  cognitive summaries per student; cohort-wide misunderstanding identification also
  described.
- **Confidence**: anecdotal (single practitioner-educator's implementation; not
  independently evaluated for educational effectiveness)
- **Quote**: "Those two days of spec felt slow at the time...but they were what
  let the rest of the week move fast."
- **Our assessment**: Intent-Diff Review is the most architecturally novel
  mechanism in this hackathon. It is not a grader (which evaluates correctness) —
  it is a metacognitive loop that surfaces the gap between what the student intended
  (the spec) and what they built (the code), classified by type of gap. The
  three-way classification (drift: student moved away from spec without realizing;
  revision: deliberate spec change; bug: code doesn't implement spec as intended)
  is a structured taxonomy that could be applied beyond CS education to any workflow
  where spec-to-implementation fidelity matters (requirements tracking, acceptance
  criteria validation, etc.). The quote documents the development-time evidence for
  spec-first approaches — which the guide already covers via McBee (Opus 4.6
  hackathon) but now has an educator's first-person confirmation.

### Claim 5: Medkit uses an agentic grader to evaluate medical residents' simulated-patient encounters against published clinical guidelines — a domain-specific evaluation architecture for complex, judgment-heavy outputs

- **Evidence**: Named project (Medkit), named winner (Bedirhan Keskin,
  Istanbul-based physician-turned-software engineer). Students practice diagnosis,
  medical history-taking, lab ordering, imaging review, and treatment prescription
  against simulated patients. The agentic grader evaluates each encounter against
  published clinical guidelines. Three medical faculties and a pharma company in
  Istanbul are planning pilots.
- **Confidence**: anecdotal (single practitioner report; grader quality against
  clinical guidelines not independently audited; but the rapid pilot adoption by
  three medical faculties is a notable real-world signal)
- **Quote**: "What I value most about Claude is it's not just a code generator,
  but a thought partner helping me see options I'd otherwise miss."
- **Our assessment**: The Medkit grader pattern — an agent evaluating a complex,
  multi-step domain interaction against a formal published standard — is directly
  analogous to the generator-verifier pattern described in the multi-agent
  coordination patterns note, but applied to clinical education rather than code
  output. The key design challenge is that clinical guidelines are complex, often
  conditional, and context-specific — making "explicit criteria" for the verifier
  harder to specify than in a code correctness checker. The fact that three medical
  faculties are planning pilots within weeks of the hackathon is the strongest
  post-hackathon adoption signal in the Opus 4.7 cohort — comparable to the
  institutional interest signals documented for PostVisit.ai in the Opus 4.6 cohort.

### Claim 6: Voice-first development ("talk, don't type") across four separate Claude Code sessions was the primary development modality for a physician building a medical education platform

- **Evidence**: Named project (Medkit), named winner (Bedirhan Keskin,
  physician). Built across four separate Claude Code sessions using Claude Managed
  Agents. "Talk, don't type" is described as the development approach.
- **Confidence**: anecdotal (single practitioner's reported development workflow)
- **Quote**: (no direct quote on the voice-first method itself; see paraphrase)
- **Our assessment**: "Talk, don't type" as a development modality inverts the
  typical assumption that AI coding tools primarily benefit typist-developers. For
  domain experts whose primary fluency is verbal (clinical rounds, case discussion),
  voice-as-code-input removes the keyboard barrier entirely. The four-session
  structure also documents how multi-session context management works in practice
  for a non-developer builder: Managed Agents handling session persistence meant
  Keskin did not have to manage state continuity manually between sessions. This
  is a concrete example of the Managed Agents session-persistence claim from the
  launch post — here attributed to a specific project where session continuity
  was a prerequisite for a non-developer to complete the build.

### Claim 7: A 20-year-old with no prior programming experience (Benjamin Torralbo, Chile) won a prize by encoding his father's master-carpenter expertise as JSON configuration

- **Evidence**: Named winner (Benjamin Torralbo, 20 years old, from Chiloé,
  Chile, no prior programming experience). Domain knowledge source: interviews
  with his father. Encoding mechanism: JSON config (17 diagnostic rules, 7 native
  woods, 16 trade dialect terms, 19 benchmark prices, 9 craft mistakes). Outcome:
  74%→81% eval improvement. Named prize: Keep Thinking Prize.
- **Confidence**: anecdotal (single reported outcome; winner background stated
  by Anthropic's editorial post)
- **Quote**: "Claude Code lets a 20-year-old from Chiloé with no programming
  experience build software that his own dad can use."
- **Our assessment**: This is the strongest single evidence point in the Opus 4.7
  hackathon for the domain-expert-as-developer accessibility claim. Torralbo
  extends the pattern documented in the Opus 4.6 note (where "non-professional
  developers" were still professionals in other fields — a lawyer, a cardiologist)
  to someone with no professional background whatsoever. His competitive advantage
  was access to domain expertise (his father) and the ability to conduct structured
  interviews that extracted that expertise into computable form. The "his own dad
  can use" framing shows that the target user was the domain expert himself, not
  a tech-savvy user — a meaningful accessibility bar.

### Claim 8: The Opus 4.7 hackathon reproduces the accessibility pattern from Opus 4.6 — domain experts winning over developers — while extending it to industrial, vocational, and educational domains not covered in April 2026

- **Evidence**: Winner profiles: Keskin (physician), Chapellier (electronics
  repair technician), Vásquez-Henríquez (CS instructor), Torralbo (no programming
  experience, 20 years old). New domains in Opus 4.7 not present in Opus 4.6:
  medical education, electronics repair, home repair diagnostics, factory
  maintenance, interactive play. Opus 4.6 covered: civic tech (permit processing),
  visual IDE for education, clinical AI, road infrastructure, music.
- **Confidence**: emerging (two-hackathon comparison; consistent structural outcome
  across different model versions, different winning cohorts, and different
  competition timing)
- **Quote**: (no direct quote; pattern observation across both hackathons)
- **Our assessment**: The reproducibility of the accessibility pattern across Opus
  4.6 (April 2026) and Opus 4.7 (June 2026) — two separate competitions, two months
  apart, with entirely different winners — is stronger evidence for the pattern's
  generality than any single hackathon. The domain expansion is also meaningful:
  Opus 4.7's winners come from vocational (electronics repair, carpentry, factory
  maintenance) and educational domains, showing the pattern extends beyond the
  civic/healthcare/creative domains that Opus 4.6 covered. If the guide's current
  examples of domain-expert accessibility draw entirely from the 4.6 cohort, they
  should be updated with the 4.7 cohort to demonstrate breadth across both model
  versions and domain types.

### Claim 9: Running five to six agents in parallel per domain during development, with benchmarking at every step, is Wrench Board's documented development methodology for a complex multi-agent diagnostics system

- **Evidence**: Named project (Wrench Board), named winner (Alexis Chapellier).
  "Multi-agent mode execution with five to six agents running in parallel during
  debugging" described as the technical approach. Benchmarking at every step also
  described.
- **Confidence**: anecdotal (single practitioner report; specific numbers — "5-6
  agents" — suggest deliberate methodology rather than vague description)
- **Quote**: (no direct Chapellier quote on the parallel agent methodology)
- **Our assessment**: "5-6 agents in parallel during debugging" is a specific
  development practice, not just an architecture pattern. It implies that for a
  complex diagnostics domain (electronics repair), Chapellier ran multiple agents
  with different diagnostic approaches simultaneously and compared results to
  benchmark accuracy, rather than iterating sequentially on a single agent. This
  is a practitioner application of the generator-verifier and orchestrator-subagent
  patterns from the multi-agent coordination patterns note — using parallel agent
  runs as a form of ensemble diagnosis. It also suggests that the orchestration
  overhead of spinning up 5-6 agents simultaneously was manageable within the
  hackathon week, which is a practical signal about Managed Agents' multi-agent
  coordination overhead.

### Claim 10: Spending two full days on design and technical specifications before writing any code enabled Maieutic's complex CS-education IDE to be completed within the hackathon week

- **Evidence**: Named project (Maieutic), named winner (Paula Vásquez-Henríquez).
  "Dedicated two days to design and technical specs before writing code" described
  as the approach. Maieutic includes a locked editor, disabled autocomplete,
  redirected reasoning questions, Intent-Diff Review, and a live instructor
  dashboard — a system complex enough that upfront design was material.
- **Confidence**: anecdotal (single practitioner's reported experience; causal
  attribution to the two-day spec phase is the winner's own assessment)
- **Quote**: "Those two days of spec felt slow at the time...but they were what
  let the rest of the week move fast."
- **Our assessment**: The Vásquez-Henríquez quote is the sharpest articulation
  of spec-first development's tempo effect in the corpus. The Opus 4.6 hackathon
  covered spec-driven development via McBee's 39,000-line Elisa project (Claim 3
  in that note), but McBee is a software engineer — his spec discipline comes from
  professional experience. Vásquez-Henríquez is a CS instructor, not a software
  engineer; her two-day spec was domain-led (what should a CS education tool do?
  how should it structure feedback?) rather than architecture-led. The pattern
  generalizes: spec-first development is effective when the domain expert leads
  the specification phase, even when they are not the primary coder.

### Claim 11: ARIA's builders spent their entire second day planning with a GitHub Project board before writing code, and Claude Code wrote approximately 80% of raw code lines while humans made domain logic and design decisions

- **Evidence**: Named project (ARIA), named team (Benguezzou and Hnaien). Specific
  planning tool (GitHub Project board). Specific code-contribution estimate (Claude
  Code ~80% of raw lines; humans handled domain logic and design decisions). One
  piece of advice from the builders was: "Ask Claude to find if there's anything
  wrong with what you've already built before building the next thing."
- **Confidence**: anecdotal (single team's report; the 80% estimate is their
  own self-assessment)
- **Quote**: "Ask Claude to find if there's anything wrong with what you've
  already built before building the next thing."
- **Our assessment**: The ARIA builders' explicit division of labor (Claude Code:
  raw implementation; humans: domain logic and design decisions) is the clearest
  statement in the Opus 4.7 hackathon of how the human-AI collaboration model
  actually worked. It is consistent with the McBee quote from Opus 4.6 ("I know
  systems architecture...Claude Code helped me turn all that knowledge into a
  shippable product") but now attributed to an AI/ML engineer team, not just an
  experienced software engineer. The "find what's wrong with what you've already
  built" advice is a concrete application of the generator-verifier pattern as
  a coding practice: build incrementally, run a verification pass before extending,
  rather than building and verifying only at the end.

### Claim 12: Virtual Puppet Theater demonstrates Opus 4.7's spatial reasoning applied to real-time 3D performance — webcam input to animated 3D puppet at 60 fps, with voice-driven scene transformation and prop spawning

- **Evidence**: Named project (Virtual Puppet Theater), named winner (Rene
  Hangstrup Møller, full-stack developer). Technical stack: Bun, Vite, TypeScript,
  MediaPipe hand tracking (WASM), Three.js for 3D rendering at 60 fps, WebSocket
  server connecting to Opus 4.7, ElevenLabs voice output. Opus 4.7's spatial
  reasoning handled visual output through screenshot-based feedback loops. Voice
  prompts can transform scenery and spawn 3D props.
- **Confidence**: anecdotal (single developer's project; technical stack details
  are specific and credible)
- **Quote**: "Plan time to create the demo video...it takes way longer than you
  think."
- **Our assessment**: Virtual Puppet Theater is the most technically complex
  real-time system in the Opus 4.7 hackathon. The Three.js 60-fps target (real-time
  3D rendering) combined with WebSocket-based Claude communication and MediaPipe
  WASM hand tracking represents a multi-layer performance-constrained architecture.
  The use of screenshot-based feedback loops for Opus 4.7's spatial reasoning
  (where the model sees 3D scene output as a screenshot and responds) is the
  same pattern Wrench Board used for schematic reasoning — suggesting screenshot-
  based feedback loops are an emerging multi-domain pattern for visual-reasoning
  applications in the Opus 4.7 generation. The Møller quote, while practical advice,
  is notable as the one piece of meta-advice about hackathon product presentation.

## Concrete Artifacts

### Winner Summary Table — Opus 4.7 Hackathon (June 2026)

```
Built with Opus 4.7 Claude Code Hackathon — Winner Summary
(Anthropic, June 2026; hackathon week)

Prize                     | Builder(s)                  | Background                        | Project           | Domain
--------------------------|----------------------------|-----------------------------------|-------------------|---------------------------
1st Place                 | Bedirhan Keskin             | Physician (Istanbul)               | Medkit            | Medical education / simulation
2nd Place                 | Alexis Chapellier           | Electronics repair tech (France)   | Wrench Board      | Electronics diagnostics
3rd Place                 | Paula Vásquez-Henríquez    | CS instructor (Chile, UDD)         | Maieutic          | CS education / metacognition
Most Creative Use of      | Rene Hangstrup Møller       | Full-stack developer               | Virtual Puppet    | Interactive real-time play
Opus 4.7                  |                             |                                   | Theater           |
Keep Thinking Prize       | Benjamin Torralbo           | No programming experience (age 20) | MaestrIA          | Home repair diagnostics
Best Use of Claude         | Idriss Benguezzou +         | Industrial AI/ML engineer +        | ARIA              | Factory machine maintenance
Managed Agents            | Adam Hnaien                 | Self-taught Claude Code user       |                   |
```

### MaestrIA Domain Knowledge Injection — Configuration Contents

```
MaestrIA context engineering configuration (JSON-injected, no system prompt modification)
Source: Anthropic hackathon post, June 2026

Knowledge categories:
  - 17 diagnostic rules
  - 7 native woods (Chilean lumber vocabulary and properties)
  - 16 trade dialect terms
  - 19 benchmark prices
  - 9 common craft mistakes

Knowledge source: interviews with Benjamin Torralbo's father (master carpenter)
Injection method: structured JSON configuration
Effect: eval score vs. human master's judgment: 74% → 81%
```

### Medkit Architecture Description

```
Medkit (medical education simulation)
Builder: Bedirhan Keskin (physician)
Development: 4 separate Claude Code sessions via Claude Managed Agents; "talk, don't type"

Architecture:
  - Simulated patient interface (gamified clinic)
  - Curriculum coverage: diagnosis, history-taking, lab ordering,
    imaging review, treatment prescription
  - Agentic grader: evaluates encounter against published clinical guidelines

Post-hackathon uptake:
  - 3 medical faculties in Istanbul planning pilots
  - 1 pharma company in Istanbul planning pilot

Source: Anthropic hackathon post, June 2026
```

### Wrench Board Architecture Description

```
Wrench Board (electronics repair diagnostics)
Builder: Alexis Chapellier (independent electronics repair technician)

Architecture:
  - Input: user-uploaded schematics + boardviews + symptom description
  - Agent actions: creates unified electrical graph, identifies exact
    probe points, processes measurements, iterates diagnosis
  - Visual reasoning: Opus 4.7 schematic/boardview spatial understanding
    via screenshot-based feedback loops
  - Development methodology: 5-6 agents running in parallel per domain,
    benchmarking at every step

Source: Anthropic hackathon post, June 2026
```

### ARIA Architecture and Development Approach

```
ARIA (Adaptive Runtime Intelligence — factory machine maintenance)
Builders: Idriss Benguezzou + Adam Hnaien

Architecture:
  - 5 agents continuously monitoring factory machines
  - Agent functions: failure detection + imminent breakdown prediction +
    custom diagnostics + repair plans
  - Platform: Claude Managed Agents (sandboxed Python env, session
    persistence, MCP dispatching)

Development:
  - Day 2: entirely spent planning via GitHub Project board
  - Code split: ~80% raw lines by Claude Code; domain logic + design by humans
  - Self-reported infrastructure equivalent: "5 weeks" without Managed Agents

Key quote: "Without Claude Managed Agents, we'd have spent the week building
infrastructure...instead, we spent that week building the product."
Key advice: "Ask Claude to find if there's anything wrong with what you've
already built before building the next thing."

Source: Anthropic hackathon post, June 2026
```

### Maieutic IDE Feature Set and Intent-Diff Review

```
Maieutic (spec-first CS education IDE)
Builder: Paula Vásquez-Henríquez (CS instructor, Universidad del Desarrollo, Chile)

IDE features:
  - Locked editor: disabled until spec is sufficiently detailed
  - Disabled autocomplete: prevents AI-assisted coding without spec grounding
  - Redirected reasoning questions: agent guides students to reason, not
    just receive answers
  - Intent-Diff Review: Claude compares final code against prior specification,
    classifies divergences as:
      drift   — student moved away from spec without realizing
      revision — deliberate spec change
      bug      — code doesn't implement spec as intended

Instructor tools:
  - Live dashboard with per-student cognitive summaries
  - Cohort-wide misunderstanding identification

Development timeline: 2 days design/spec → code phase
Key quote: "Those two days of spec felt slow at the time...but they were
what let the rest of the week move fast."

Source: Anthropic hackathon post, June 2026
```

### Virtual Puppet Theater Technical Stack

```
Virtual Puppet Theater
Builder: Rene Hangstrup Møller (full-stack developer)

Technical stack:
  - Runtime: Bun
  - Bundler: Vite
  - Language: TypeScript
  - Hand tracking: MediaPipe (WASM)
  - 3D rendering: Three.js (60 fps target)
  - AI connection: WebSocket server to Opus 4.7
  - Voice output: ElevenLabs
  - Visual reasoning: Opus 4.7 spatial understanding via screenshot-based
    feedback loops

Interactions:
  - Webcam video → animated puppet mirroring user movement
  - Voice prompts → scene transformation + 3D prop spawning
  - AI-driven companion puppet → provides responsive dialogue

Source: Anthropic hackathon post, June 2026
```

## Cross-References

- **Corroborates**: `blog-anthropic-opus46-hackathon-winners.md` (Claim 7:
  "Four of five main hackathon winners were non-professional developers") — the
  same accessibility pattern appears in Opus 4.7. Keskin (physician), Chapellier
  (electronics repair tech), Vásquez-Henríquez (CS instructor), and Torralbo (no
  programming experience) all fit the non-developer winner pattern documented in
  the Opus 4.6 note. Claim 9 in the Opus 4.6 note ("domain experts translate
  professional knowledge into shippable products") is directly replicated here
  across new domains. The two-hackathon comparison elevates the pattern from a
  single-event finding to a reproducible structural result.

- **Corroborates**: `blog-anthropic-claude-managed-agents.md` (Claim 1: "building
  agents meant spending development cycles on secure infrastructure...") — ARIA's
  quote ("Without Claude Managed Agents, we'd have spent the week building
  infrastructure...instead, we spent that week building the product") is the
  most direct practitioner confirmation of that claim from a hackathon context.
  Also corroborates Claim 8 (weeks instead of months) in the form of a hackathon
  week vs. an implied 5-week infrastructure build. Medkit's multi-session
  development with session persistence corroborates Claim 3 ("long-running
  sessions that operate autonomously for hours, with progress persisting through
  disconnections").

- **Corroborates**: `blog-anthropic-multi-agent-coordination-patterns.md`
  (Claim 7: orchestrator-subagent recommended as the default) — Wrench Board's
  5-6 parallel debugging agents is consistent with the orchestrator-subagent or
  agent teams pattern. ARIA's five monitoring agents is another concurrent multi-
  agent deployment. Both are hackathon-week evidence that parallel agent topologies
  are accessible to practitioners (not just architectural abstractions).

- **Corroborates**: `blog-anthropic-opus47-best-practices.md` — Wrench Board's
  explicit reliance on Opus 4.7's visual schematic reasoning is a practitioner
  validation of the visual reasoning capability described there. The
  screenshot-based feedback loop for visual output is consistent with Opus 4.7's
  documented improved visual understanding.

- **Extends**: `blog-anthropic-opus46-hackathon-winners.md` — Adds six new
  domains (medical education, electronics repair, CS metacognition, interactive
  play, home repair, factory maintenance) and documents three capabilities that
  were absent in the Opus 4.6 cohort: (1) Opus 4.7 visual reasoning for technical
  schematics (Wrench Board), (2) Claude Managed Agents as the primary
  infrastructure layer (ARIA, Medkit), (3) quantified JSON context injection
  (MaestrIA 74%→81%). The Opus 4.7 hackathon should be read as a sequel that
  confirms the Opus 4.6 accessibility pattern while providing evidence for new
  capability categories.

- **Extends**: `blog-anthropic-claude-managed-agents.md` — ARIA is the first
  industrial IoT case study in the corpus for Managed Agents (the launch post
  covered enterprise software, meeting prep, legal Q&A). Factory machine
  predictive maintenance with five concurrent monitoring agents extends the
  Managed Agents evidence base into operational technology domains where uptime
  requirements and domain vocabulary are categorically different from SaaS
  enterprise software.

- **Novel**:
  - **Quantified JSON context injection with no system prompt change (MaestrIA)**:
    No prior corpus source documents a context engineering approach where domain
    knowledge injection is entirely in configuration (not prompts), attributed
    to a specific percentage improvement (74%→81%) against a human expert's judgment.
    This is the most actionable context engineering data point in the corpus.
  - **Intent-Diff Review taxonomy (Maieutic)**: Classifying spec-to-code divergence
    as drift, revision, or bug is a three-way taxonomy not documented elsewhere in
    the corpus. It generalizes beyond CS education to any workflow where spec-to-
    implementation fidelity matters.
  - **Agentic grading against published clinical guidelines (Medkit)**: Using an
    agent as an evaluator against a published professional standard (clinical
    guidelines) for complex multi-step domain interactions. No prior corpus note
    documents this evaluation architecture.
  - **Screenshot-based feedback loops for visual reasoning as a cross-project
    pattern (Wrench Board + Virtual Puppet Theater)**: Two separate projects in
    the same hackathon independently used screenshot-based feedback loops to enable
    Opus 4.7 spatial/visual reasoning. This convergence suggests a reusable
    pattern, not a project-specific trick.
  - **Voice-first development modality for non-developer builders (Medkit)**:
    "Talk, don't type" as the primary development modality for a domain expert
    builder has not been documented as a named pattern in the corpus. It removes
    the keyboard-and-IDE interface barrier for domain experts whose primary
    fluency is verbal.
  - **Industrial IoT domain for multi-agent systems (ARIA)**: Five concurrent
    monitoring agents for factory machine predictive maintenance extends the
    multi-agent pattern corpus into operational technology — outside the
    enterprise software and civic tech domains that dominate existing notes.
  - **Zero-programming-experience winner sourcing domain knowledge from family
    interviews (MaestrIA)**: Benjamin Torralbo's approach — interview a family
    member expert, encode as JSON — documents a knowledge elicitation workflow
    accessible to anyone regardless of technical background.
  - **Two-hackathon reproducibility as evidence of pattern generality**: Comparing
    Opus 4.6 (April 2026) and Opus 4.7 (June 2026) hackathon winner profiles shows
    the accessibility pattern persisting across model versions, competition timing,
    and winner cohorts. No prior corpus note explicitly compares two hackathon
    cohorts to establish reproducibility.

## Guide Impact

- **Chapter 04 (Context Engineering) — Domain knowledge as JSON configuration**:
  MaestrIA's 74%→81% improvement from structured JSON injection (no system prompt
  change) should be added as the anchor case for the "domain knowledge as context"
  pattern. Ch04 currently discusses context engineering in general terms; MaestrIA
  provides a concrete, measurable example of the form: interview domain expert,
  enumerate decision rules and vocabulary, inject as JSON config, measure improvement
  vs. baseline. The specific contents (17 rules, 7 vocabulary terms, 16 dialect
  terms, 19 prices, 9 mistake types) show what a complete domain knowledge encoding
  looks like in practice.

- **Chapter 02 (Harness Engineering) — Managed Agents as infrastructure accelerant**:
  ARIA provides the clearest practitioner case for adding a "when to use Managed
  Agents instead of building your own infrastructure" decision criterion in Ch02.
  The five-weeks-vs-one-week comparison is now supported by both the Managed Agents
  launch post (enterprise software testimonials) and a hackathon project (industrial
  IoT). The ARIA quote should appear alongside the Sentry/Atlassian testimonials
  as the primary evidence for the infrastructure-vs-product tradeoff.

- **Chapter 02 (Harness Engineering) — Screenshot-based feedback loops for
  visual reasoning**: Two Opus 4.7 hackathon projects independently converged on
  screenshot-based feedback loops for visual/spatial reasoning. Ch02 should document
  this as a reusable pattern for incorporating Opus 4.7's visual understanding into
  agentic workflows: provide visual context as screenshots, request spatial analysis,
  update the visual output, repeat. The pattern is applicable to any domain where
  the output is visual (schematics, 3D scenes, dashboards, medical images).

- **Chapter 02 (Harness Engineering) — Parallel agent debugging methodology**:
  Wrench Board's 5-6 parallel agents during development, benchmarked at every step,
  is a concrete development-time application of multi-agent patterns from Ch02's
  content. Currently Ch02 covers multi-agent patterns as deployment architectures;
  the Wrench Board approach suggests parallel agents are also useful as a development
  and validation methodology (run multiple diagnostic approaches simultaneously,
  compare, select best). This is a different use case than production architecture.

- **Chapter 05 (Team Adoption) — Voice-first development for domain experts**:
  Keskin's "talk, don't type" development modality should be documented in Ch05's
  domain-expert adoption path as an alternative to keyboard-and-IDE interaction.
  For domain experts in clinical, legal, or vocational settings where verbal
  communication is primary, voice-first development removes the biggest interface
  barrier. Combined with Managed Agents session persistence (no state loss between
  sessions), it enables sustained project development without traditional IDE use.

- **Chapter 05 (Team Adoption) — Reproducibility of domain-expert accessibility
  across model versions**: Ch05 currently cites the Opus 4.6 hackathon as evidence
  for domain-expert adoption. Adding the Opus 4.7 hackathon results makes the
  accessibility case stronger: it is not a single event but a reproducible pattern
  across two competitions, two months apart, with different winners in different
  domains. The case for targeting domain experts (not just developers) in adoption
  programs is now backed by two independent structured competitions.

- **Chapter 03 (Verification and Quality) — Agentic grading against published
  standards**: Medkit's clinical-guidelines grader should be added to Ch03 as a
  pattern for evaluating complex domain outputs. The design challenge is making the
  grader's criteria explicit enough to avoid the "early victory problem" (from the
  multi-agent coordination patterns note, Claim 2) while capturing the nuance of
  clinical judgment. Ch03 should note this as an open problem: structured graders
  against formal standards (clinical guidelines, legal rules, building codes) are
  a high-value application but require careful criteria design.

- **Chapter 02 or Chapter 04 — Intent-Diff Review as a general verification
  pattern**: Maieutic's Intent-Diff Review (spec vs. code, three-way divergence
  classification) is a verification architecture applicable beyond CS education.
  Any workflow that starts with a specification (requirements, acceptance criteria,
  design doc) and produces an implementation can apply an intent-diff check as a
  quality gate. Ch02's harness engineering content should reference this as a
  lightweight alternative to full generator-verifier architectures when the spec
  already exists as a formal artifact.

## Extraction Notes

- Source fetched via WebFetch, which converts HTML to markdown via AI processing.
  The quotes extracted here appear in the WebFetch response as attributed winner
  quotes. Per MINER.md §2a, the Assayer should verify verbatim accuracy of all
  quoted passages against the live source URL. If WebFetch introduced any
  paraphrasing in attributed quotes, the quote should be updated to match the
  source exactly.
- The hackathon competition size (number of participants, total prize pool) is not
  stated in the WebFetch content for the Opus 4.7 post. The Opus 4.6 post stated
  "500 participants, $100,000 prize pool." This source note does not assume the same
  parameters apply to Opus 4.7; the Assayer should check the live URL for competition
  scale data.
- Rene Hangstrup Møller (Virtual Puppet Theater) is described as a "full stack
  developer" — unlike most other Opus 4.7 winners, he is a professional developer.
  The Opus 4.6 pattern (four of five non-professional developers) may not hold
  exactly in Opus 4.7; the Assayer should check winner demographics from the live
  source.
- No claims were found to directly contradict existing source notes. The Opus 4.6
  and 4.7 hackathon notes address different winner cohorts and different model
  capabilities — they are additive, not competing. The Managed Agents claims here
  corroborate (not contradict) the launch post. No contradiction issue is required.
- Confidence is set to `emerging` (consistent with the Opus 4.6 note) because:
  (1) winner claims are self-reported in a competition context; (2) competition
  design selects for best-in-show, not typical outcomes; (3) specific metrics
  (74%→81% eval improvement) are not independently verified. The reproducibility
  observation (consistent pattern across two hackathons) is higher confidence than
  individual claims.
