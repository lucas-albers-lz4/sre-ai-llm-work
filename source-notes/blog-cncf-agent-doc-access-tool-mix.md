---
source_url: https://www.cncf.io/blog/2026/07/21/why-your-agent-needs-access-to-your-documentation
source_type: blog-post
title: "Why your agent needs access to your documentation"
author: "Finn Bauer (kapa.ai; CNCF Member Post)"
date_published: 2026-07-21
date_extracted: 2026-10-14
last_checked: 2026-10-14
status: current
confidence_overall: anecdotal
issue: "#1720"
---

# Why your agent needs access to your documentation

> A vendor-authored, first-party usage report from kapa.ai: an in-product chat
> agent with ~30 native platform tools plus one `search_knowledge_base` tool
> over documentation was analyzed across its last 1,192 conversations, and the
> single docs tool turned out to be the most-used tool — rivaling all native
> tools combined. The report names three roles the docs tool played (fallback
> at 32.1%, context at ~7%, and an unexpected "planning" role where docs teach
> the agent which native tool to call) and argues documentation is "part of how
> the agent reasons," not just a last-resort lookup.

## Source Context

- **Type**: blog-post (CNCF Member Post — vendor-authored; kapa.ai sells
  documentation-based AI assistant tooling, the exact product category the post
  advocates).
- **Author credibility**: Finn Bauer, kapa.ai, writing about an agent the
  company shipped inside its own product. First-hand *descriptive* authority on
  what their agent did (they own the conversation logs), but direct commercial
  interest in the conclusion (docs-retrieval tooling is kapa.ai's product). No
  disclosure line and no product pitch in the body, but the recommendation is
  category-aligned with the author's employer.
- **Scope**: Covers one measured result (tool-usage share across 1,192
  conversations of one in-product agent), a three-role usage taxonomy
  (fallback / context / planning) with shares for two of the roles, and a
  design argument for documentation access in agents. Does **NOT** cover: any
  code, config, architecture, tool schema, sampling methodology, denominator,
  attribution method, failure trace, or cost/latency figure. The 1,192-
  conversation window's representativeness is unstated.
- **Freshness**: Published 2026-07-21, after the Dec-2025 corpus cutoff; not
  covered by any existing note (Prospector duplicate check).

## Extracted Claims

### Claim 1: An in-product agent was given ~30 native platform tools plus one `search_knowledge_base` tool covering documentation, code examples, support FAQs, and API reference
- **Evidence**: The author's description of the agent they shipped; the
  native-tool count is given as approximate, the docs tool as a single tool
  spanning four content surfaces.
- **Confidence**: settled (descriptive of their own shipped agent)
- **Quote**: "The agent has around 30 native tools to interact with our platform, such as search_conversations and display_chart. It also has a single search_knowledge_base tool that can read documentation, code examples, support FAQs, and API reference."
- **Our assessment**: The tool inventory is the setup for the whole result and
  is the clearest artifact in the post: one retrieval tool fronting four doc
  surfaces, alongside ~30 purpose-built action tools. Note the asymmetry the
  author does not emphasize — the ~30 native tools are individually specialized,
  while the one docs tool is a broad free-form retrieval interface. That is
  exactly the shape Ch03's "structured tool contracts over free-form interfaces"
  rule would push against, so this source is a useful stress test of that rule
  (see Guide Impact).

### Claim 2: Contrary to the team's expectation that native tools would dominate, `search_knowledge_base` was the single most-used tool, almost as much as all the native tools combined
- **Evidence**: First-party aggregate usage telemetry over the agent's last
  1,192 conversations. No per-tool counts, no denominator, no sampling method,
  no definition of "used."
- **Confidence**: anecdotal (self-reported, single-vendor, unpublished
  methodology; the Prospector graded it `anecdotal` and this note concurs)
- **Quote**: "We expected the native tools to do most of the work. But when we looked at the last 1,192 conversations, search_knowledge_base was the most used tool, almost as much as all the native tools combined."
- **Our assessment**: This is the headline datapoint and the reason the source
  is in the corpus. It is genuinely surprising — the opposite of the "fewer,
  purpose-built tools" intuition — and it would be high-value corroboration for
  retrieval investment *if* it were audited. It is not: the window, the
  attribution logic, and whether "conversations" means sessions or turns are all
  unstated. Treat the direction as a hypothesis worth testing on your own agent,
  not as a benchmark. The vendor's commercial interest in this exact result is
  the reason to grade it `anecdotal` rather than `emerging`.

### Claim 3: The largest role for the docs tool was fallback — 32.1% of conversations used it for questions no native tool could answer, and without it the agent "would have had to refuse or guess"
- **Evidence**: Stated share over the 1,192 conversations, plus example
  questions (Slack integration setup, widget CORS errors, crawl frequency) that
  are product questions outside the native tools' schema.
- **Confidence**: anecdotal (single number, no methodology disclosed)
- **Quote**: "The main use case for knowledge base search was acting as a failover when users asked questions that no native tool could answer. That accounted for 32.1% of conversations."
- **Quote**: "Without search_knowledge_base, the agent would have had to refuse or guess."
- **Examples as quoted in the source**: "How do I set up the Slack integration?" / "Why am I getting CORS errors on the widget?" / "How often do website crawls ingest?"
- **Our assessment**: The mechanism is credible and matches the corpus's
  recurring "coverage gaps at the tool boundary" theme: a fixed native-tool
  schema cannot enumerate every product question, so a retrieval fallback
  absorbs the long tail. The 32.1% figure should be read as "reported, not
  verified." The useful, transferable part is the *shape* of the fallback —
  exception-handling by retrieval rather than by refusal — not the number.

### Claim 4: The second role, ~7% of conversations, was context addition — native tools report account state while docs supply its meaning, and neither alone sufficed
- **Evidence**: A stated ~7% share plus a worked example: `list_integrations`
  reported the user's current MCP configuration; the docs supplied the
  comparison to alternative integration types, which lives only in the docs.
- **Confidence**: anecdotal (single number, worked example is one anecdote)
- **Quote**: "The next pattern was conversations where the agent used both kinds of tools, around 7% of the total."
- **Quote**: "The native tools answer what is true about a user's account right now. search_knowledge_base answers what it means."
- **Quote**: "Neither tool could have answered on its own. The native tool knew the state; the knowledge-base tool knew the product."
- **Our assessment**: The state-vs-meaning division of labor is the most
  defensible of the three roles and the easiest to design for: it is a clean
  complementarity claim, not a competition, and it gives a concrete reason to
  keep *both* a structured data tool and a retrieval tool rather than choosing
  one. Buy the mechanism; keep the 7% as reported.

### Claim 5: The unexpected third role is planning — the docs tool was called not to answer the user but so the agent could "figure out what to do," teaching it which native tool to call
- **Evidence**: A worked example: a request for "negative sentiment"
  conversations, for which no sentiment field or filter exists anywhere in the
  product; the agent read the docs, learned negative signal surfaces as
  downvotes and feedback comments, then called the correct native tool with the
  correct filters.
- **Confidence**: anecdotal (one detailed worked example; no share given for
  this role — the Prospector noted the post reports shares only for roles 1 and
  2)
- **Quote**: "In some conversations, search_knowledge_base was not called to answer the user. It was called so the agent could figure out what to do."
- **Quote**: "Instead, the agent searched the documentation, found that negative signals are captured as downvotes and feedback comments, and then called the right native tool with the right filters. The docs were not the answer; they were the briefing the agent needed before it could act. The knowledge-base tool was doing planning work."
- **Our assessment**: This is the novel and highest-value claim in the source,
  and the part the Prospector specifically flagged for extraction. It reframes
  documentation retrieval from an *answer source* to a *routing/planning input*:
  the docs teach the agent the product's vocabulary, which is what lets it
  translate an underspecified user request into the right structured tool call.
  This is mechanistically the missing link between a user's language and a
  tool's schema — a function that, in the corpus, is otherwise attributed to
  good tool naming/descriptions (ACI). It deserves a design rule candidate:
  when user language and tool schema mismatch, the retrieval tool is how the
  agent bridges them. The caveat is that it rests on a single worked example in
  a vendor post; grade `anecdotal`, recommend a second independent source before
  hardening into guide advice (as the Prospector explicitly warned).

### Claim 6: Docs do a "third job" — teaching the agent what the product can actually do — alongside answering and contextualizing
- **Evidence**: The author's own synthesis of the planning pattern above; a
  named three-job taxonomy.
- **Confidence**: anecdotal
- **Quote**: "We have started thinking of this as a third job the knowledge-base tool does, alongside answering and contextualizing: it teaches the agent what the product can actually do, so the agent can pick the right native tool."
- **Our assessment**: The taxonomy (answer / contextualize / teach-the-agent)
  is a compact, reusable framing and the post's clearest contribution to Ch03's
  agent-tooling design material. The third job is the non-obvious one; the
  first two are what most engineers already assume. Treat the taxonomy as
  vocabulary for design review — "does your agent have a way to learn its own
  tool surface?" — not as a measured distribution (only roles 1 and 2 have
  reported shares).

### Claim 7: The fallback load was driven by an expectation mismatch — users treated an analytics agent as a catch-all product agent, and the docs tool is what let it meet that expectation
- **Evidence**: The author's interpretation of the fallback conversations; the
  example questions are product-support shaped, not analytics shaped.
- **Confidence**: anecdotal
- **Quote**: "We had built an analytics agent, but users treated it as a catch-all product agent, and the documentation tool was what let it meet that expectation."
- **Our assessment**: A useful product-design observation with an ops parallel:
  users route to the interface they have, not the interface you scoped. For the
  guide, this is a caution against sizing a tool set to the *intended* task
  distribution; the real distribution is set by user behavior and is often
  broader. It also flags a measurement hazard the source does not address — if
  users treat the agent as a catch-all, then "most-used tool" partly measures
  mis-scoped user expectations, not agent design quality.

### Claim 8: The post's thesis is that documentation is "part of how the agent reasons," not merely a fallback; the author's closing framing is that the docs tool is what makes the ~30 native tools useful
- **Evidence**: The author's concluding thesis statement, supported only by the
  single-agent, single-vendor telemetry above. No comparison condition (an
  agent without the docs tool) is reported.
- **Confidence**: anecdotal (this is the vendor thesis; explicitly flagged by
  the Prospector as not to be hardened)
- **Quote**: "We shipped 30 native tools and one tool that reads documentation. The tool that reads documentation is what makes the other 30 useful."
- **Quote**: "the documentation is not just a fallback, it is part of how the agent reasons."
- **Our assessment**: This is the strongest *claim* and the weakest *evidence*
  in the post. The mechanism is plausible and partially supported by the
  planning example (Claim 5), but the causal framing ("makes the other 30
  useful") is asserted, not demonstrated — there is no counterfactual run and
  no independent replication. Do not let this harden into a guide
  recommendation on this source alone, per the Prospector's instruction. It is
  the right hypothesis to carry forward and test.

### Claim 9: The CNCF-specific relevance claim — across the CNCF landscape, documentation is a primary interface and tends to be "large, fast-moving, and spread across many surfaces," making docs-vs-tools a practical agent design decision
- **Evidence**: Author's ecosystem observation naming Kubernetes, Prometheus,
  Envoy, Argo, and OpenTelemetry as projects with large, dispersed docs. Not
  measured; a framing claim for the audience.
- **Confidence**: anecdotal (ecosystem framing, no data)
- **Quote**: "Across the CNCF landscape, from Kubernetes and Prometheus to Envoy, Argo, and OpenTelemetry, documentation is one of the primary interfaces between a project and its users, and it tends to be large, fast-moving, and spread across many surfaces."
- **Our assessment**: This is the reason the post is in *this* corpus rather
  than a generic SaaS blog. The "large, fast-moving, and spread across many
  surfaces" characterization is also the strongest link to the corpus's
  documentation-freshness concerns (stale runbooks / stale docs) — a retrieval
  tool pointed at fast-moving docs inherits a freshness problem the source does
  not discuss. Flag that gap for the Smith.

### Claim 10: The design question the post poses — how much the agent should read docs versus call purpose-built tools — is a practical decision, and the answer here is not "fewer native tools" but "the retrieval tool is what makes the others usable"
- **Evidence**: The author's framing of the design tradeoff and their
  conclusion. No alternative configuration is tested.
- **Confidence**: anecdotal
- **Quote**: "the question of how much the agent should read the docs versus call purpose-built tools becomes a practical design decision"
- **Our assessment**: This is the claim with direct guide leverage (see Guide
  Impact). It is a *qualification* of the tool-count/structured-contract
  intuition, not a refutation: structured contracts remain right for action
  tools, while a free-form retrieval tool may legitimately be the highest-
  traffic tool because it does routing and context work the structured tools
  cannot. Carry it as an emerging design rule with the anecdotal evidence grade
  attached, and do not read it as "add more free-form tools."

## Concrete Artifacts

The source contains no code, config, schema, or diagram. The only concrete
artifacts are usage numbers and the example questions/requests. Quoted verbatim
from the CNCF page (2026-07-21); emphasis markers present in the raw page were
reduced to their rendered text.

### Reported tool-usage shares (verbatim)

```
- Most-used tool: search_knowledge_base ("almost as much as all the
  native tools combined") — over 1,192 conversations
- Fallback role: 32.1% of conversations
- Context-addition role: around 7% of the total
- Planning role: no share given
```

### Agent tool inventory (verbatim)

```
"The agent has around 30 native tools to interact with our platform, such as
search_conversations and display_chart. It also has a single
search_knowledge_base tool that can read documentation, code examples, support
FAQs, and API reference."
```

### Fallback example questions (verbatim, as bulleted in the source)

```
- "How do I set up the Slack integration?"
- "Why am I getting CORS errors on the widget?"
- "How often do website crawls ingest?"
```

### The planning worked example (verbatim)

```
"The clearest example: a user asked the agent to find conversations with
negative sentiment. There is no sentiment filter and no sentiment field
anywhere in the product. An agent with only native tools would either refuse
or guess at a tool that does not exist."
```

### The context-addition worked example (verbatim)

```
"list_integrations answered the first half by reporting the current
configuration. To answer the second half, the agent had to read the docs,
because the comparison between integration types lives there."
```

## Cross-References

- **Corroborates**:
  - [docs-langfuse-mcp-server.md](docs-langfuse-mcp-server.md) **Claim 1**
    ("Langfuse exposes its documentation to AI agents through a dedicated,
    public MCP server") and its "docs-as-a-tool" framing: an observability
    vendor packages its docs behind an agent-facing retrieval surface so agents
    self-serve. That note documents *how* docs are exposed (MCP endpoint,
    transport, no auth); this source supplies a usage datapoint for *why* docs
    access belongs in the tool set. Different vendors, same pattern: docs as a
    first-class agent interface, not a human-only artifact. Also **Claim 6** of
    that note (the same search exposed as both an MCP tool `searchLangfuseDocs`
    and a plain REST endpoint) is a concrete instance of a broad documentation
    retrieval tool of the kind this source says carries the traffic.
  - [blog-pagerduty-sre-agent-triage.md](blog-pagerduty-sre-agent-triage.md)
    **Claim 4** ("SRE Agent connects to observability, code, and documentation
    via connectors (MCP-based), establishing the data fabric for triage") —
    documentation is wired in as a first-class connector alongside
    observability and code, independent of this source and in an SRE-agent
    context. Supports this source's Claim 8 thesis that docs access is part of
    the fabric, not an afterthought.
  - [blog-incidentio-ai-sre-incident-run.md](blog-incidentio-ai-sre-incident-run.md)
    **Claim 10** (incident-response friction is "too many tools, too much
    context switching") — the paper's concern is *human* tool fragmentation,
    while this source is about the agent's *tool mix*; both point at the same
    underlying cost of a fragmented tool surface. Cited as thematic
    corroboration only, not as the same claim.

- **Contradicts**: None filed. Two tensions were examined against MINER.md §4a
  and both are conditioning variables, not opposing claims:
  - [blog-pagerduty-production-ai-agent-gaps.md](blog-pagerduty-production-ai-agent-gaps.md)
    **Claim 13** ("basic RAG... starts falling short" for agent *shared memory*,
    because it lacks temporal/invalidation awareness). That note's scope is
    inter-agent shared memory where facts get invalidated; this source's scope
    is single-agent lookup over a product's own docs. Different problem, so not
    a contradiction — but the staleness concern is transferable and this source
    does not address it (see Guide Impact).
  - [blog-pagerduty-sre-agent-architecture.md](blog-pagerduty-sre-agent-architecture.md)
    **Claim 3** (instruction overload — "an inverse relationship between
    instruction volume and output quality"). This source reports a large
    (~30) native tool set plus a retrieval tool being *usable*, which sits
    awkwardly beside the instruction-overload finding. It is a valid
    conditioning variable rather than a contradiction: the PagerDuty finding is
    about a monolithic agent's instructions competing for attention, while this
    source's thesis is precisely that the retrieval tool *reduces* selection
    burden by teaching the agent the mapping. No contradiction issue filed;
    note the tension as an open design question.

- **Extends**:
  - [blog-anthropic-building-effective-agents.md](blog-anthropic-building-effective-agents.md)
    — **Claim 7** ("The basic building block of agentic systems is an LLM
    enhanced with augmentations such as retrieval, tools, and memory") and
    **Claim 16** (ACI tool design determines agent success). This source is an
    empirical (if unaudited) datapoint underneath both: it shows retrieval
    carrying disproportionate traffic against a large tool set, and it
    supplies the "planning" mechanism — docs helping the agent select the
    correct tool when user language does not match the tool schema — which is a
    lower-level companion to ACI's naming/description discipline. **Claim 9**
    (routing classifies input and directs it to a specialized followup) is the
    pattern this source's planning role instantiates using the docs as the
    classifier.
  - [blog-anthropic-agent-skills.md](blog-anthropic-agent-skills.md) —
    adjacent on equipping agents with on-demand external knowledge, but a
    different mechanism: skills package procedural knowledge on a filesystem
    with progressive disclosure (its Claim 4), whereas this source's docs tool
    is a retrieval interface. The shared insight is that agent-facing knowledge
    should live *outside* the context window until needed; the two notes
    describe two packaging mechanisms for that idea. Extends rather than
    duplicates.
  - [blog-cncf-4-body-problem-sre-context.md](blog-cncf-4-body-problem-sre-context.md)
    — same CNCF Member Post venue and same "context before agents" thesis
    family (its Claim 1: "AI's biggest challenge in operations isn't model
    capability. It's context."). That note argues for a unified knowledge-graph
    substrate from an architecture standpoint with no measurement; this source
    reports a *measured* (self-reported) retrieval-usage share for one narrow
    doc-retrieval tool. Extends the thesis with a datapoint — and, importantly,
    the datapoint is a plain retrieval tool, not the knowledge graph that note
    prescribes, which is a mild scope tension worth noting to the Smith.

- **Novel** (to our corpus):
  - The **measured tool-mix observation**: one documentation retrieval tool as
    the most-used tool against ~30 native tools, over 1,192 conversations —
    no corpus note reports a tool-usage distribution.
  - The **three-role taxonomy for a documentation retrieval tool** (fallback /
    context / planning), with reported shares for the first two.
  - The **"planning" use pattern** specifically — docs as a *tool-selection
    map* / routing input rather than an answer source — is the corpus's first
    articulation of documentation retrieval as part of the agent's reasoning
    loop rather than its knowledge base.
  - The **expectation-mismatch mechanism** (users route to the interface they
    have; the agent's real task distribution is broader than its designed one).

## Guide Impact

- **Chapter 03 (Runbooks and Agents), "Structured tool contracts over
  free-form interfaces" (line 159)**: Add a qualifier. The current rule
  ("Define agent-facing tool and service contracts as structured, typed
  schemas") is right for *action* tools, but this source is evidence that a
  free-form *retrieval* tool over documentation can be the highest-traffic tool
  in the set, because it does work the structured tools cannot: absorbing
  out-of-schema questions (Claim 3) and mapping user language onto the right
  tool (Claim 5). Recommend the section state: structured contracts remain the
  rule for action tools; a documentation-retrieval tool is a legitimate and
  often load-bearing *reasoning* tool, not an interface smell. Grade the
  supporting evidence `anecdotal` (single-vendor, self-reported) and cite this
  note as the source — do not state it as settled.
- **Chapter 03, agent tool-set design**: Add the three-role taxonomy (Claims
  3–6) as a design-review checklist — for your agent's docs/retrieval tool, ask
  whether it is covering (a) out-of-schema questions, (b) state-meaning
  context, and (c) tool selection when user vocabulary and schema diverge. The
  planning role (Claim 5) is the one most often missed. Flag it as emerging: a
  single worked example in a vendor post.
- **Chapter 03, "If your agent uses retrieval, test retrieval quality"
  (line 434)**: This source supplies a *why* the current text asserts but does
  not evidence: retrieval may be the single most-used tool, so retrieval
  quality is not a peripheral concern. Recommend strengthening the line to say
  retrieval is likely load-bearing and should be evaluated and instrumented
  accordingly — with the evidence caveat attached.
- **Chapter 02 (Observability)**: The chapter already requires instrumenting
  retrieval as a distinct operation. Add the corollary this source demonstrates:
  **per-tool usage telemetry** (which tools are actually called, and how often)
  is itself an eval input — the kapa.ai team found their design assumption
  wrong only by measuring tool-usage shares (Claim 2). Recommend a short note
  that tool-usage distribution is worth capturing and reviewing, since it can
  contradict the intended design.
- **Cross-cutting caution (do not adopt as settled)**: The vendor thesis
  (Claim 8) and the 32.1% / ~7% figures are unaudited, first-party, and
  category-aligned with the author's employer (kapa.ai sells docs-assistant
  tooling). The Prospector's instruction stands: treat as a hypothesis and
  require a second, independent source before hardening into guide guidance.
  Also flag the unaddressed freshness gap (Claim 9): a retrieval tool pointed
  at "large, fast-moving, and spread across many surfaces" CNCF docs inherits a
  staleness problem this source never mentions (cf.
  blog-cncf-4-body-problem-sre-context Claim 7 on stale runbooks).

## Extraction Notes

- Source read in full via WebFetch of the single article URL; no sub-pages
  followed (the post is self-contained, has no substantive outbound links used
  as evidence, and is short). All quotes are contiguous verbatim fragments from
  the fetched rendered page; markdown emphasis markers present in the raw page
  (e.g. around "32.1%") were reduced to plain text, and no two non-adjacent
  sentences were spliced (MINER.md §2a).
- **Evidence quality drives the grade**: no code, config, schema, architecture,
  diagram, failure trace, cost/latency figure, or methodology exists in the
  source. The measurement is first-party, unaudited, single-vendor, and
  category-aligned with the author's employer. `confidence_overall` set to
  `anecdotal` accordingly (the Prospector graded it medium-to-high novelty but
  explicitly said the mechanism is a hypothesis, not a benchmark). Individual
  claims are graded `settled` only where they are descriptive of the agent the
  author shipped (Claim 1).
- **Triaged type**: issue carries `triaged:text` (+ `mining-queued`,
  `priority:high`); text-source extraction rubric applied, with extra weight on
  the Prospector's requested tool-selection mechanism (Claim 5) and honest
  evidence grading.
- **miner-related-notes.md candidates disposition** (10 listed, all processed
  per MINER.md §4):
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — **Dismissed**. Retail/
    gaming SLO granularity; no tool-mix or documentation-retrieval content.
  - `docs-promptfoo-enterprise-audit-logging.md` — **Dismissed**. Audit-log
    event taxonomy; no agent tool-selection or docs-retrieval claim.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — **Dismissed**.
    Declarative vs. imperative config workflows; no relevance.
  - `docs-google-sre-reliable-product-launches.md` — **Dismissed**. Launch
    coordination process; no relevance.
  - `docs-litellm-anthropic-advisor-tool.md` — **Dismissed**. Within-request
    advisor model composition and token accounting; no docs-retrieval content.
  - `docs-promptfoo-evaluate-openai-agents-python.md` — **Dismissed**. Tracing
    bridge for evaluating OpenAI Agents; no relevance to tool mix.
  - `docs-litellm-batches-api.md` — **Dismissed**. Batch rate-limiting
    accounting; no relevance.
  - `docs-langfuse-mcp-server.md` — **Cited** (Corroborates, Claims 1 and 6).
    The closest genuine match: docs exposed as an agent-facing retrieval tool.
  - `docs-google-sre-eliminating-toil.md` — **Dismissed**. Toil taxonomy; no
    agent-tool content.
  - `docs-google-sre-on-call.md` — **Dismissed**. Pager load and alert hygiene;
    no agent-tool content.
- Additional cross-references were searched directly in `source-notes/`
  (`pagerduty|incidentio|anthropic|retrieval|tool_choice|knowledge base`) and
  verified per MINER.md §4b by re-reading each cited note's `### Claim:`
  headings: blog-pagerduty-sre-agent-triage (Claim 4), blog-pagerduty-
  production-ai-agent-gaps (Claim 13), blog-pagerduty-sre-agent-architecture
  (Claim 3), blog-incidentio-ai-sre-incident-run (Claim 10), blog-anthropic-
  building-effective-agents (Claims 7, 9, 16), blog-anthropic-agent-skills
  (Claim 4), blog-cncf-4-body-problem-sre-context (Claims 1, 7). All cited
  claim numbers were re-checked against the notes.
- **No contradiction issue filed**: the two tensions (RAG-vs-retrieval scope;
  instruction-overload vs. a large usable tool set) are conditioning variables,
  not opposing claims that would lead to different guide advice, so they fail
  the MINER.md §4a bar and are recorded in Cross-References instead. No open
  `contradiction`-labeled issues or `C-NNN` entries were implicated.
