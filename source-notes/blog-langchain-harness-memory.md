---
source_url: https://www.langchain.com/blog/your-harness-your-memory
source_type: blog-post
title: "Your harness, your memory"
author: Harrison Chase (LangChain CEO)
date_published: 2026-04-11
date_extracted: 2026-05-24
last_checked: 2026-05-24
status: current
confidence_overall: emerging
issue: "#134"
---

# Your harness, your memory

> Harrison Chase (LangChain CEO) argues that agent harnesses are structurally
> permanent — not because models won't improve, but because any LLM-plus-tools
> system requires surrounding infrastructure by definition — and that memory
> ownership is the primary mechanism by which closed harnesses create irreversible
> vendor lock-in.

## Source Context

- **Type**: blog-post (LangChain blog, April 11, 2026 — two days after the
  Deep Agents Deploy announcement targeting the same audience)
- **Author credibility**: Harrison Chase is co-founder and CEO of LangChain, the
  dominant Python agent orchestration framework. He has direct commercial interest
  in arguing that harnesses are permanent and that open-source alternatives to
  closed managed agents matter. Claims about harness necessity and memory ownership
  are credible as architectural reasoning, but treat competitive characterizations
  of specific vendors (Claude Agent SDK, Codex, OpenAI Responses API) as vendor
  positioning rather than neutral technical assessments. The post cites Sarah
  Wooders ("memory isn't a plugin (it's the harness)") and the Claude Code 512k LOC
  source leak as external supporting evidence.
- **Scope**: Covers (1) why harnesses are permanent infrastructure, (2) how
  harnesses control memory through context management, (3) three tiers of memory
  lock-in severity from stateful APIs to fully closed harnesses, (4) the proprietary
  value of accumulated agent memory, and (5) LangChain's Deep Agents as the open
  alternative. Does NOT cover technical benchmarks, performance data, API specifics,
  or implementation details. This is an architectural argument post, not an
  engineering how-to.

## Extracted Claims

### Claim 1: Agent harnesses are the dominant way to build agents today, and they will not disappear as models improve

- **Evidence**: Architectural argument supported by industry examples (Claude Code,
  Deep Agents, Pi, OpenClaw, OpenCode, Codex, Letta Code all named as examples of
  harnesses). The post cites the evolution of agent infrastructure from RAG chains
  (2022) → LangGraph flows → agent harnesses as evidence that scaffolding type
  evolves but scaffolding itself persists.
- **Confidence**: emerging (reasoned argument with illustrative examples; no controlled
  study; author has commercial interest in the conclusion)
- **Quote**: "Agent harnesses are becoming the dominant way to build agents, and they
  are not going anywhere."
- **Our assessment**: The persistence argument rests on the definitional claim (Claim 2)
  rather than empirical evidence. The historical evolution supports the argument that
  scaffolding *type* changes, but the claim that harnesses specifically (vs. some other
  abstraction) are permanent is architectural reasoning, not demonstrated fact. The
  enumeration of harness examples from multiple vendors (including competitors) is the
  strongest form of evidence — it is not just LangChain saying this; the whole ecosystem
  has converged on this pattern.

### Claim 2: An agent is by definition an LLM interacting with tools and other data sources; there will always be a surrounding system to facilitate that interaction

- **Evidence**: Definitional argument from the author. No empirical evidence — this is
  a logical claim about what the word "agent" means.
- **Confidence**: settled (the definitional claim is structurally valid given the
  accepted definition of an LLM agent; the inference is direct)
- **Quote**: "An agent, by definition, is an LLM interacting with tools and other sources
  of data. There will always be a system around the LLM to facilitate that type of
  interaction."
- **Our assessment**: This is the strongest argument in the post because it does not
  depend on current model capability. Even a vastly more capable model still needs
  something to route its tool calls, manage its context, and connect it to external
  state. The counterargument — that models could internalize this infrastructure as
  learned behavior — is not addressed, but the definitional point holds: even if the
  harness is very thin, it still exists. This directly refutes the "models will absorb
  harnesses" community sentiment that the Prospector flagged.

### Claim 3: Claude Code's leaked source code containing 512k lines of code is evidence that even best-in-class model builders invest heavily in harness infrastructure

- **Evidence**: The Claude Code source code was leaked via Anthropic's npm package
  (documented in `failure-alex000kim-claudecode-source-leak.md`). Harrison Chase cites
  this figure as a concrete data point showing that harness complexity is real, not
  hypothetical.
- **Confidence**: settled (the 512k LOC figure is corroborated by the alex000kim
  failure report and HN discussion, both of which documented the leak independently)
- **Quote**: "When Claude Code's source code was leaked, there was 512k lines of code.
  That code is the harness."
- **Our assessment**: This is the sharpest rhetorical move in the post — Anthropic itself,
  the company most invested in model capability, built a 512k LOC harness. The implicit
  argument: if models were absorbing harnesses, Anthropic would not be building one. The
  512k LOC figure is independently corroborated by `failure-alex000kim-claudecode-source-leak.md`
  (which documented the source leak and analyzed the architecture). Harrison Chase's use
  of this figure to argue for harness permanence is the same data point used differently:
  the failure report analyzed what the code reveals about implementation; this post uses
  the code's existence to argue about industry direction.

### Claim 4: Managing context — and therefore memory — is a core capability and responsibility of the agent harness

- **Evidence**: Author's architectural reasoning, backed by a citation to Sarah Wooders'
  blog post titled "memory isn't a plugin (it's the harness)." The specific harness
  memory functions listed include: how AGENTS.md/CLAUDE.md is loaded into context, skill
  metadata display, whether the agent can modify its own system instructions, what survives
  compaction, and filesystem exposure.
- **Confidence**: emerging (compelling architectural argument with expert corroboration;
  the specific enumeration is plausible and granular, which increases confidence)
- **Quote**: "Managing context, and therefore memory, is a core capability and
  responsibility of the agent harness."
- **Our assessment**: The equation "context management = memory management" is the
  conceptual core of the post and of the memory-ownership argument that follows. The
  specific enumeration of harness memory functions is notable: (1) how AGENTS.md/CLAUDE.md
  loads into context, (2) skill metadata shown to agents, (3) whether agents can modify
  system instructions, (4) what survives compaction, (5) filesystem exposure. This is
  a concrete operational definition of what "memory" means at the harness level — not
  a vector database, but these five context-management decisions. This framing gives
  practitioners a checklist: if your harness handles these five functions, it owns memory.
  Compare with `blog-langchain-deep-agents-deploy.md` Claim 5: "An agent harness is
  intimately tied to memory."

### Claim 5: Context management ultimately constitutes the foundation for agent memory

- **Evidence**: Author's framing that memory is downstream of context management. The
  full chain: harness manages context → context is memory → whoever controls the harness
  controls the memory.
- **Confidence**: emerging (architectural reasoning; the specific chain of reasoning is
  sound, though "foundation" implies stronger claims than can be empirically verified)
- **Quote**: "ultimately, how the harness manages context and state in general is the
  foundation for agent memory."
- **Our assessment**: This claim establishes the lock-in argument's logical foundation.
  If memory = context management, and the harness controls context management, then
  harness lock-in is memory lock-in by identity — not just by consequence. This is
  a stronger claim than "memory is hard to migrate" (which is pragmatic lock-in); it is
  "you cannot separate the memory from the harness that manages it" (which is
  architectural lock-in). The strength of this claim is what makes the three lock-in
  tiers (Claims 6-8) consequential rather than hypothetical.

### Claim 6: Using a stateful API (OpenAI Responses API or Anthropic server-side compaction) is "mildly bad" — state is stored on the vendor's server

- **Evidence**: Author's categorization of lock-in severity. Named examples: OpenAI
  Responses API and Anthropic server-side compaction.
- **Confidence**: emerging (architectural characterization; "mildly bad" is a value
  judgment, but the structural claim about where state is stored is accurate for both
  named products)
- **Quote**: "Mildly bad: If you use a stateful API (like OpenAI's Responses API, or
  Anthropic's server side compaction), you are storing state on their server."
- **Our assessment**: The "mildly bad" label distinguishes this from the more severe
  scenarios below, but "storing state on their server" has real consequences: migration
  requires extracting that state, which may not be possible in a usable format. For
  Anthropic server-side compaction specifically: the compaction summary that the model
  uses to resume sessions is stored in Anthropic's infrastructure. For OpenAI Responses
  API: conversation state is managed server-side. In both cases, the user cannot inspect
  or extract the stored state in a format usable by a different provider's harness.
  The severity label is the author's framing; practitioners should evaluate based on
  how much state they expect to accumulate.

### Claim 7: Closed harnesses (such as Claude Agent SDK / Claude Code) are "bad" — they interact with memory in ways unknown to the user

- **Evidence**: Author's categorization. Named examples: Claude Agent SDK (described as
  using Claude Code under the hood, which is not open source).
- **Confidence**: anecdotal (vendor competitive positioning; the "unknown" characterization
  is the author's characterization of a closed-source product; it cannot be independently
  verified by definition)
- **Quote**: "Bad: If you use a closed harness (like Claude Agent SDK, which uses Claude
  Code under the hood, which is not open source), this harness interacts with memory in
  a way that is unknown to you."
- **Our assessment**: The "unknown" framing is the strongest version of the lock-in
  argument and the least verifiable. By contrast, the open-source harnesses (LangGraph)
  interact with memory in ways that *can* be inspected. The 512k LOC source leak
  (Claim 3) is relevant here — the Claude Code source was previously unknown; its
  exposure allowed the alex000kim analysis. Harrison Chase's claim is structurally
  accurate for any closed-source product: you cannot audit what you cannot read.
  Whether "unknown" is "bad" depends on how much practitioners value auditability.

### Claim 8: The worst scenario is a fully closed harness with long-term memory entirely behind an API — the user has no access to or control over their accumulated agent knowledge

- **Evidence**: Author's categorization; no specific named product given in the "worst"
  category, but the framing refers to fully managed platforms where memory is a
  platform-managed resource.
- **Confidence**: anecdotal (vendor competitive framing; the described scenario is
  architecturally real but the severity label is the author's)
- **Quote**: "But worst is something else - when the whole harness, including long term
  memory is behind an API."
- **Our assessment**: The Dreaming feature in Claude Managed Agents
  (`blog-anthropic-managed-agents-dreaming-outcomes.md`, Claim 1) is the clearest
  current example of this scenario: a scheduled, asynchronous, cross-session process
  that extracts patterns and curates memories inside the Anthropic platform, with the
  accumulated output constituting a proprietary dataset about the user's agents. Teams
  that use Dreaming are building institutional knowledge inside Anthropic's infrastructure.
  Harrison Chase does not name Dreaming specifically (it was announced April 11 — the
  same day as this post), but the description fits. The counter-argument: for teams
  without the engineering capacity to build their own long-term memory layer, a managed
  platform is preferable to no memory at all.

### Claim 9: Codex (OpenAI) generates encrypted compaction summaries that are not usable outside the OpenAI ecosystem

- **Evidence**: Direct technical characterization from the author. No independent
  technical documentation cited.
- **Confidence**: anecdotal (specific technical claim from a competitive post; the
  mechanism described is plausible but has not been independently verified by this
  extraction)
- **Quote**: "even though Codex is an open source, it generates an encrypted compaction
  summary (that is not usable outside of the OpenAI ecosystem)."
- **Our assessment**: If accurate, this is the clearest concrete example of the
  "mildly bad" stateful API scenario applied to a harness that is nominally open source.
  An open-source harness that generates encrypted state not readable by third parties
  creates lock-in at the data layer even when there is none at the code layer. This is
  a pattern worth tracking: open-source licensing does not guarantee data portability.
  The encrypted summary format is the mechanism that makes "open source" and "locked in"
  compatible. This claim should be verified against Codex documentation before being
  cited as settled.

### Claim 10: Without accumulated agent memory, agents are easily replicable by anyone with access to the same tools

- **Evidence**: Author's argument about the competitive value of memory.
- **Confidence**: emerging (a logical inference; the claim is that memory is the
  differentiation factor, which is plausible but not demonstrated empirically)
- **Quote**: "Without memory, your agents are easily replicable by anyone who has access
  to the same tools."
- **Our assessment**: This is the flip side of the lock-in argument: memory is both
  what creates lock-in AND what creates the competitive moat that makes lock-in
  tolerable. The claim is an argument for why practitioners should care about memory
  ownership — the memory is where the differentiated value accumulates. The implication:
  in a world where model capability is commoditized, the organization that retains
  ownership of accumulated agent memory has a durable advantage over one that stores
  it in a vendor's platform. This complements the Dreaming argument from a different
  direction: Dreaming creates valuable accumulated knowledge; memory ownership means
  retaining that knowledge when switching platforms.

### Claim 11: Accumulated agent memory constitutes a proprietary dataset of user interactions and preferences that creates competitive advantage

- **Evidence**: Author's argument about the strategic value of memory.
- **Confidence**: emerging (reasonable inference; no empirical data on the magnitude
  of advantage or how quickly it materializes)
- **Quote**: "With memory, you build up a proprietary dataset - a dataset of user
  interactions and preferences."
- **Our assessment**: This positions accumulated agent memory as equivalent to training
  data — a proprietary dataset that becomes more valuable over time and harder to
  replicate from scratch. The analogy is to recommendation systems: a cold-start
  recommendation system (no history) and a mature one (years of interaction data) may
  use the same algorithm but produce dramatically different results. If agent memory
  follows the same curve, early adopters who accumulate memory in their own infrastructure
  build a compounding advantage over those who do not. The counter-argument: agent
  memory in 2026 is early enough that few teams have accumulated significant datasets,
  so the switching cost concern is prospective rather than immediate.

### Claim 12: In order to own your memory, you need to use an open harness

- **Evidence**: Author's conclusion. Supported by the logical chain: memory = context
  management (Claim 5) → closed harness = unknown context management (Claims 6-8) →
  open harness = auditable context management → auditable = owned.
- **Confidence**: anecdotal (vendor conclusion; structurally valid as an argument, but
  "open" is not uniformly defined, and deep integration with LangSmith can create
  deployment-layer lock-in even for "open" harnesses)
- **Quote**: "In order to own your memory, you need to be using an Open Harness."
- **Our assessment**: The conclusion is the product recommendation, but the argument is
  structurally sound: a harness whose source code you can audit and deploy anywhere
  gives you ownership of the context management decisions that constitute memory ownership.
  The caveat from `blog-langchain-deep-agents-deploy.md` applies: Deep Agents Deploy is
  open-source at the harness layer but has a LangSmith dependency at the deployment layer.
  "Open harness" and "fully portable" are not the same. Teams should evaluate lock-in
  at each layer: model, harness code, deployment infrastructure, and stored state.

## Concrete Artifacts

### Harness Memory Control Functions (from the post)

```
# Key harness responsibilities in memory/context management
# Source: "Your harness, your memory", Harrison Chase, LangChain, April 11, 2026

Questions only the harness can answer:
  1. How is the AGENTS.md or CLAUDE.md file loaded into context?
  2. How is skill metadata shown to the agents?
  3. Can the agent modify its own system instructions?
  4. What survives compaction?
  5. What is the filesystem the agent is exposed to?
```

### Memory Lock-in Severity Tiers (from the post)

```
# Three-tier classification of memory lock-in severity
# Source: "Your harness, your memory", Harrison Chase, LangChain, April 11, 2026

Tier 1 — Mildly bad (stateful APIs):
  Examples: OpenAI Responses API, Anthropic server-side compaction
  Mechanism: State stored on vendor's server
  Risk: Migration requires extracting vendor-held state

Tier 2 — Bad (closed harnesses):
  Examples: Claude Agent SDK (uses Claude Code under the hood, not open source)
  Mechanism: Harness interacts with memory in ways unknown to the user
  Risk: Cannot audit, verify, or migrate context management behavior

Tier 3 — Worst (fully closed harness + long-term memory behind API):
  Examples: Fully managed platforms where memory accumulates inside vendor infrastructure
  Mechanism: Entire harness + long-term memory = opaque API
  Risk: Institutional knowledge locked entirely inside vendor platform;
        starting fresh required on any migration

Special case: nominally open source + encrypted state
  Example: Codex (open source harness)
  Mechanism: "generates an encrypted compaction summary (that is not usable outside
             of the OpenAI ecosystem)"
  Risk: Open-source code + proprietary state format = code portability without
        data portability
```

### Agent Harness Evolution Timeline (from the post)

```
# Historical evolution of agent scaffolding (per Harrison Chase)
# Source: "Your harness, your memory", Harrison Chase, LangChain, April 11, 2026

~2022: Simple RAG chains (ChatGPT era)
         Tool: LangChain chains
         Pattern: retrieval + generation

~2023: Complex flows
         Tool: LangGraph
         Pattern: conditional routing, branching workflows

~2024-2026: Agent harnesses (current dominant pattern)
         Examples: Claude Code, Deep Agents, Pi, OpenClaw, OpenCode, Codex, Letta Code
         Pattern: full harness managing context, tools, memory, sandboxing

Authorial thesis: Each era replaced the specific scaffolding type,
not scaffolding itself. "What has happened (and will continue to happen)
is that a lot of the scaffolding needed in 2023 is no longer needed.
But this has been replaced by other types of scaffolding."
```

## Cross-References

- **Corroborates**:
  - `blog-langchain-deep-agents-deploy.md` (Claim 5): that note's memory lock-in claim
    ("An agent harness is intimately tied to memory. A key role of the harness is to
    manage context (memory is just context). As more and more parts of the harness become
    closed, locked behind an API — so does your memory.") is the exact same argument as
    Claims 4-5 here, from an earlier LangChain post. The present post extends and deepens
    that earlier claim with the three-tier lock-in taxonomy (Claims 6-8). The two notes
    together present LangChain's full memory ownership argument across two posts.
  - `failure-alex000kim-claudecode-source-leak.md`: The 512k LOC figure cited in Claim 3
    is independently documented in that failure report. Harrison Chase cites the leak as
    evidence for harness permanence; alex000kim analyzed the code to extract specific
    engineering lessons. Both sources use the same data point to different ends. The
    failure report provides the technical substance; this post provides the architectural
    implication.
  - `blog-anthropic-claude-managed-agents.md`: The Managed Agents platform features
    described there (managed sandboxing, memory, multi-agent coordination) are the
    concrete instantiation of Claim 8 here (fully closed harness + long-term memory
    behind API). The two notes give both sides: Anthropic describing the platform's
    capabilities, LangChain describing why those capabilities create lock-in.
  - `blog-anthropic-harnessing-claude-intelligence.md` (Claim 15): "What can I stop
    doing?" / harness components become dead weight as models improve — this post's
    Claim 1 (harnesses persist) addresses the same structural question from the opposite
    angle: Chase argues the type of scaffolding changes but scaffolding itself doesn't
    go away. Both are first-party acknowledgments that harnesses evolve; they frame the
    evolution differently (what to remove vs. why you can't remove it all).

- **Contradicts**: None filed. The "models absorb harnesses" sentiment the Prospector
  flagged as contradicted by this post appears to be a general community belief rather
  than a specific claim in an existing source note. No existing source note in the corpus
  directly argues that models will absorb their own harnesses, so no contradiction issue
  is warranted.

- **Extends**:
  - `blog-anthropic-managed-agents-dreaming-outcomes.md` (Claim 1): Dreaming — the
    scheduled cross-session pattern-extraction process that accumulates institutional
    knowledge inside Anthropic's platform — is the clearest current example of Claim 8
    here (worst case: fully closed harness + long-term memory behind API). The Dreaming
    announcement (April 11, same day as this post) was presumably not yet known to Chase
    when writing. Together: this post provides the architectural argument for why Dreaming
    creates lock-in; the dreaming note describes what is being locked in.
  - `blog-thebatch-nemotron-agent-infra.md` (Claim 8/9): That note documents the
    OpenAI/AWS stateful agent deal's architectural distinction (stateful = AWS, stateless
    = Azure) without evaluating what that means for memory ownership. This post provides
    the evaluative frame: stateful APIs are "mildly bad" for memory portability because
    state accumulates on the vendor's server.
  - `blog-langchain-deep-agents-deploy.md`: This post provides the architectural
    argument (why memory ownership matters) that motivates the product announced in that
    post (how Deep Agents Deploy preserves memory ownership). The two posts are the
    argument and the solution from the same author within two days of each other.

- **Novel**:
  - **Three-tier lock-in taxonomy** (stateful API → closed harness → fully managed
    platform + memory): No existing source note in the corpus classifies memory lock-in
    into severity tiers with named examples at each level. This taxonomy is new and
    actionable for practitioners evaluating harness options.
  - **Encrypted state as a lock-in mechanism independent of code openness**: The Codex
    example — open-source code with encrypted compaction summaries unusable outside
    OpenAI's ecosystem — introduces a new failure mode: "open source" does not imply
    "data portable." No existing corpus source identifies this specific pattern.
  - **Harness evolution argument** (scaffolding type changes, scaffolding itself persists):
    The historical framing (RAG chains → LangGraph flows → agent harnesses) as evidence
    that each era replaces the scaffolding type rather than eliminating scaffolding is a
    new argument structure in the corpus. Previous corpus sources either assume harnesses
    are permanent (without arguing it) or describe specific harness features.
  - **The five harness memory control questions**: The enumeration of "How is AGENTS.md
    loaded? How is skill metadata shown? Can the agent modify system instructions? What
    survives compaction? What is the exposed filesystem?" as the operational definition
    of "what harness memory control means" is a concrete checklist not available elsewhere.
    This is more actionable than the generic claim "harnesses control memory."
  - **The proprietary dataset framing of agent memory**: Positioning accumulated agent
    memory as a proprietary training dataset (comparable to recommendation system history)
    that creates compounding competitive advantage is a new framing in the corpus.

## Guide Impact

- **Chapter 02 (Agent Harness Architecture & Design)**: Add Harrison Chase's definitional
  argument (Claim 2) as the concise answer to "why won't better models eliminate harnesses?"
  — "There will always be a system around the LLM to facilitate that type of interaction."
  The 512k LOC Claim 3 should be cited as the concrete evidence that harness complexity
  is real even for the best model builders.

- **Chapter 02 (Harness Architecture — Five Memory Control Functions)**: Add the five
  harness memory control questions (Concrete Artifacts section) as the operational
  checklist for evaluating harness memory ownership. When comparing harness options,
  practitioners should verify that they can answer all five questions for their chosen
  harness. A harness that cannot answer any of these publicly is exercising Tier 2
  lock-in (Claim 7).

- **Chapter 04 (Memory & Context Management)**: The "context management = memory
  management" equation (Claims 4-5) should anchor any section on agent memory. The
  current corpus treats context and memory as related but separate concerns; this post
  argues they are identical from the harness's perspective. This reframing has
  implications for how practitioners think about memory architecture: it is not a
  separate system you add to a harness, it is an emergent property of how the harness
  manages context.

- **Chapter 05 (Vendor Lock-in & Architectural Portability)**: The three-tier lock-in
  taxonomy (Claims 6-8 + Concrete Artifacts table) should be the organizing framework
  for the chapter on lock-in. Practitioners can self-locate their current situation in
  one of the three tiers and assess migration difficulty accordingly. Add the Codex
  encrypted-state finding as a worked example of how open-source licensing does not
  guarantee data portability.

- **Chapter 05 (Lock-in & Portability — Dreaming as Tier 3 Example)**: The Dreaming
  feature from `blog-anthropic-managed-agents-dreaming-outcomes.md` should be cited
  as the concrete current example of Tier 3 lock-in (fully managed platform with
  long-term memory as API). The Harvey ~6x completion rate improvement from Dreaming
  shows that this lock-in is not hypothetical — real value accumulates inside managed
  platforms, which raises the switching cost over time.

## Extraction Notes

- The blog post redirects from blog.langchain.com/your-harness-your-memory to
  www.langchain.com/blog/your-harness-your-memory. Both URLs resolve to the same content.
- Harrison Chase published this post on April 11, 2026 — the same day the Dreaming
  feature was announced in Claude Managed Agents. Whether this timing was coordinated
  is unclear, but the two posts address the same question (what happens to memory in
  a managed harness) from opposite sides.
- The Sarah Wooders reference ("memory isn't a plugin (it's the harness)") is cited
  but the blog URL was not separately fetched for this extraction. The Wooders post
  may contain additional claims relevant to Ch04.
- All verbatim quotes above have been verified against multiple WebFetch passes of
  the source URL. The post does not contain code examples, configuration snippets,
  or quantitative benchmarks — it is a pure architectural argument post.
- The Prospector noted overlap with `blog-thebatch-nemotron-agent-infra.md`, but
  the overlap is tangential — the Nemotron note documents a news digest that includes
  the OpenAI/AWS stateful deal; this post provides the architectural argument for why
  that deal's stateful API design creates lock-in. The connection is at the level of
  the stateful API concept, not the specific content of either note.
- Confidence set to `emerging`: the architectural arguments are well-structured and
  the specific quotes are verified, but no benchmarks or empirical data support the
  claims about memory ownership severity. Harrison Chase has a direct commercial
  interest in the conclusion that closed harnesses are bad, which limits the
  independence of the evidence.
