---
source_url: https://simonwillison.net/2026/May/19/5-minute-llms/
source_type: blog-post
title: "The last six months in LLMs in five minutes"
author: Simon Willison
date_published: 2026-05-19
date_extracted: 2026-05-27
last_checked: 2026-05-27
status: current
confidence_overall: emerging
issue: "#953"
---

# The Last Six Months in LLMs in Five Minutes

> Simon Willison's PyCon US 2026 lightning-talk retrospective names November 2025 as
> a defined inflection point for coding agents, traces the causal chain from RLVR
> training → "often-work to mostly-work" quality leap → OpenClaw/Claws explosion →
> Mac Mini as personal-agent hardware, and closes with open-weights laptop models
> beginning to saturate his pelican-bicycle SVG benchmark.

## Source Context

- **Type**: blog-post (annotated lightning-talk slides from PyCon US 2026; published
  2026-05-19; structured as a narrative retrospective covering November 2025 through
  May 2026, with embedded model comparisons, screenshots of pelican SVG outputs, and
  a named cultural observation about "Claws")
- **Author credibility**: Simon Willison is the creator of Django, creator of the
  `llm` CLI, and one of the most widely-cited independent practitioners in LLM
  tooling. He has no vendor affiliation, dogfoods coding agents daily, and writes
  with disciplined analytical precision. He has been consistently applying the same
  pelican-on-a-bicycle SVG benchmark across models for at least six months, making
  it a durable cross-model comparison lens. This post synthesizes first-hand
  observation across the November 2025–May 2026 window and is therefore unusually
  high-signal as a retrospective: the author has lived through every event he
  narrates.
- **Scope**: Covers the November 2025 model leadership churn; the RLVR mechanism
  behind the coding agent quality leap; Willison's pelican benchmark as a cross-model
  evaluation heuristic; the December–January "LLM psychosis" experimentation wave;
  the February 2026 OpenClaw emergence and the "Claws" category; the April 2026
  open-weights capability leap (Gemma 4, GLM-5.1, Qwen3.6). Does NOT cover: specific
  harness engineering patterns, CI integration, cost optimization, team adoption
  strategies, or safety/security topics. The post is a cultural and capability
  narrative, not a how-to guide.

## Extracted Claims

### Claim 1: November 2025 was a named inflection point for coding agents, specifically when they crossed from "often-work to mostly-work" quality — a daily-driver threshold

- **Evidence**: Willison's direct retrospective assessment. He uses this framing to
  anchor his entire talk; the inflection point is not speculative but his named
  characterization of a change he experienced in his own work.
- **Confidence**: emerging (high-signal practitioner retrospective; not empirically
  measured, but the "often-work to mostly-work" framing is precise and specific; the
  qualifier "emerging" reflects that this is one practitioner's synthesis, not a survey)
- **Quote**: "Coding agents went from often-work to mostly-work, crossing a quality
  barrier where you could use them as a daily-driver."
- **Our assessment**: "Often-work to mostly-work" is the most precise one-sentence
  characterization of the coding agent quality threshold in the current corpus. It
  specifies not just that agents improved but the exact nature of the improvement:
  from a tool that required frequent intervention to a tool that was reliable enough
  for continuous professional use. The "daily-driver" language is important — it
  implies that the improvement was qualitative (changed the tool's place in a
  practitioner's workflow), not merely incremental.

### Claim 2: RLVR (Reinforcement Learning from Verifiable Rewards) was the specific training mechanism that both OpenAI and Anthropic used through 2025 to achieve the November inflection in coding agent quality

- **Evidence**: Willison attributes the November quality leap directly to RLVR,
  naming both Anthropic and OpenAI as having deployed this training approach. This is
  consistent with published information about both labs' training strategies.
- **Confidence**: emerging (Willison's practitioner attribution of a named mechanism;
  RLVR as a concept is well-established; the attribution to both labs throughout 2025
  is his synthesis, not an official statement from either lab)
- **Quote**: "OpenAI and Anthropic had spent most of 2025 running Reinforcement
  Learning from Verifiable Rewards to increase the quality of code written by their
  models."
- **Our assessment**: This is the most explicit causal chain for the November 2025
  quality leap in the corpus: RLVR training (mechanism) → improved code quality
  (result) → often-work to mostly-work threshold (practitioner experience). The
  verifiable reward function for code — tests pass or fail — is the same structural
  advantage Karpathy identified (see `blog-simonwillison-voice-mode-weaker.md` Claim
  3). This source confirms that both labs deployed the mechanism in parallel and
  that it visibly converged in November 2025.

### Claim 3: In November 2025, the "best" model changed hands five times among Anthropic, OpenAI, and Google, with Claude Sonnet 4.5 → GPT-5.1 → Gemini 3 → GPT-5.1 Codex Max → Claude Opus 4.5

- **Evidence**: Willison's specific timeline with model names and release dates. This
  is a factual claim about a sequence of model releases with specific dates.
- **Confidence**: emerging (Willison's practitioner assessment of which model held
  "best" status at each point; the metric is his own pelican-benchmark assessment,
  not an objective benchmark; the dates and model names are factual)
- **Quote**: (no direct quote for the 5-times count; the article section heading is
  "The 'best' model changed hands 5 times between Anthropic, OpenAI and Google";
  the model sequence appears as a structured timeline with dates in the slide)
- **Our assessment**: The specific five-change timeline in a single month is the
  clearest evidence in the corpus of how compressed model competition was at the
  November 2025 frontier. For practitioners trying to select models, a month where
  "best" changed five times meant that any evaluation older than a week was obsolete.
  This was not normal competitive cadence; it was a specific convergence of model
  releases that happened to cluster around the RLVR training completion deadline for
  multiple labs.

### Claim 4: Willison's "pelican riding a bicycle" SVG test is a useful cross-model evaluation heuristic because it is hard to fake and no lab would specifically train for it

- **Evidence**: Willison's explicit rationale, given as the reason he uses this test
  consistently. He applies it across every model he evaluates; the corpus contains
  multiple notes documenting his pelican results across different models.
- **Confidence**: anecdotal (practitioner rationale; the "zero chance of training for
  this" claim is a reasonable inference about vendor training priorities, not a
  confirmed fact)
- **Quote**: "Because pelicans are hard to draw, bicycles are hard to draw, pelicans
  can't ride bicycles... and there's zero chance any AI lab would train a model for
  such a ridiculous task."
  (Note: the ellipsis may represent a WebFetch join of adjacent sentences rather than
  a single continuous passage; treat as approximate verbatim)
- **Our assessment**: The anti-Goodhart logic is sound: the benchmark is resistant to
  overfitting precisely because it is too specific and obscure to be worth a lab's
  training effort. However, Claim 11 in this note (Qwen3.6 laptop model outperforming
  Claude Opus 4.7 on this task) indicates that the benchmark is beginning to saturate
  — even laptop-runnable models can now pass it, which was not true in November 2025.
  The benchmark's usefulness as a frontier differentiator has a finite lifespan.

### Claim 5: Gemini 3.1 Pro (February 2026) drew the best pelican of the November cohort, including a fish in its basket — improving on all November models

- **Evidence**: Willison's direct observation in the "February 2026" section. He had
  established Gemini 3 as drawing "the best pelican out of this lot" in November, then
  Gemini 3.1 Pro raised the bar further.
- **Confidence**: anecdotal (single practitioner test; Willison has applied this test
  consistently across months, which gives it some longitudinal validity)
- **Quote**: "Gemini 3.1 Pro came out, and drew me a really good pelican riding a
  bicycle. Look at this! It's even got a fish in its basket."
- **Our assessment**: The improvement visible between Gemini 3 (November) and Gemini
  3.1 Pro (February) on a creative spatial reasoning task suggests the quality
  progression continued past the November inflection point. The "fish in its basket"
  detail indicates spontaneous narrative elaboration beyond the literal prompt — a
  qualitative improvement in creative interpretation.

### Claim 6: The December 2025–January 2026 holiday break produced a wave of developer over-experimentation ("LLM psychosis") — including projects nobody needed

- **Evidence**: Willison's self-report and broader cultural observation, with his own
  "micro-javascript" as a concrete example of a project with questionable utility.
- **Confidence**: anecdotal (self-report plus cultural observation; "LLM psychosis"
  is his own framing)
- **Quote**: "Over the holiday period, from December to January, a whole lot of us
  took advantage of the break to have a poke at these new models and coding agents
  and see what they could do. They could do a lot! Some of us got a little bit
  over-excited."
- **Our assessment**: This is the practitioner-level documentation of the
  "capability-driven over-enthusiasm" cycle: a quality threshold is crossed, people
  have free time, they build things they find interesting rather than useful. The
  micro-javascript project (a vibe-coded Python implementation of JavaScript in
  Pyodide, built because it was technically interesting, not because the world
  needed another JavaScript runtime) is the canonical example. This pattern is useful
  context for organizations trying to direct AI-adoption energy productively: the
  first wave of experimentation after a quality breakthrough tends toward technically
  interesting but practically marginal projects.

### Claim 7: "Claws" emerged as a generic category term for personal AI assistants, based on OpenClaw, NanoClaw, ZeroClaw, and similar products

- **Evidence**: Willison's direct observation of the emergence of a generic term from
  specific product names. He notes this as a new naming convention that crystallized
  around the February 2026 OpenClaw explosion.
- **Confidence**: emerging (practitioner observation of cultural/linguistic emergence;
  Willison is well-positioned to observe this in the ecosystem he tracks closely)
- **Quote**: "OpenClaw is a 'personal AI assistant', and we actually got a generic
  term for these, based on NanoClaw and ZeroClaw and suchlike... they're called Claws."
  (Note: the ellipsis likely represents WebFetch rendering of bold/formatting from
  the source; "Claws" was bolded in the original)
- **Our assessment**: The emergence of "Claws" as a category term signals that the
  personal AI assistant pattern reached a critical mass of distinct implementations in
  early 2026. Category naming marks the point where a pattern has enough instances to
  need a shared vocabulary — it is a market/cultural signal rather than a technical
  one. For the guide: this is the naming for an architectural pattern (autonomous
  agent running as a personal assistant on local hardware) that practitioners should
  treat as an established category when writing about agent use cases.

### Claim 8: Mac Minis sold out in Silicon Valley in early 2026 as practitioners purchased them specifically to host personal AI assistants (Claws)

- **Evidence**: Willison's direct market observation, corroborated by Drew Breunig's
  "digital pets / aquarium" metaphor. Willison frames this as a direct consequence of
  good coding agents enabling the Claw category.
- **Confidence**: anecdotal (market observation without sales data; high-signal author
  with direct ecosystem visibility)
- **Quote**: "Mac Minis started to sell out around Silicon Valley, because people were
  buying them to run their Claws."
- **Our assessment**: The Mac Mini sellout is concrete evidence that the Claws
  phenomenon had immediate hardware-market impact. The Mac Mini is the specific
  hardware because it is low-cost, always-on, quiet, and capable of running
  frontier-class local models — the "right" form factor for a personal AI assistant
  that needs to run continuously. This is the practitioner-level evidence that the
  Claws category was not theoretical; it was generating real purchasing behavior.

### Claim 9: Drew Breunig coined the "digital pets / aquarium" metaphor: Claws are the new digital pets, and Mac Minis are their aquariums

- **Evidence**: Willison attributes this metaphor to Drew Breunig (a practitioner
  Willison knows personally), presented as a joke that nonetheless captures the
  cultural phenomenon accurately.
- **Confidence**: anecdotal (attributed metaphor; not a technical claim; but the
  metaphor accurately captures the caretaking/hosting relationship between Claw owners
  and their Mac Mini hardware)
- **Quote**: "Drew Breunig joked to me that this is because they're the new digital
  pets, and a Mac Mini is the perfect aquarium for your Claw."
- **Our assessment**: The "digital pets / aquarium" framing is the most vivid cultural
  characterization of the Claws phenomenon in the corpus. It encodes several
  structural observations simultaneously: Claws require dedicated hardware (you
  maintain the aquarium), they are personalised and attached to their owner (digital
  pets, not generic tools), and they need ongoing care/feeding (model updates,
  configuration). For the guide: this metaphor is worth using when explaining the
  Claw/personal agent category to readers — it immediately conveys the relationship
  between the agent and its hosting hardware.

### Claim 10: OpenClaw originated as "Warelay" (first commit end of November 2025), went through multiple name changes, and became a widely-used open-source personal AI assistant project by February 2026 — less than three months after its first commit

- **Evidence**: Willison's narrative of the OpenClaw origin story, positioned as the
  concrete instantiation of what good coding agents enabled. The rapid trajectory from
  first commit to widespread adoption is documented with the timeline.
- **Confidence**: emerging (Willison's external observation about an open-source
  project's history; the name sequence and timeline are factual claims that are
  independently verifiable from the project's git history)
- **Quote**: (no direct quote for the full origin story; the WebFetch gave summaries
  of this section)
- **Our assessment**: The Warelay → OpenClaw trajectory is the clearest evidence that
  good coding agents were a prerequisite for the Claws category: the project started
  within weeks of the November 2025 inflection point, and exploded in February 2026.
  The short timeline (3 months from first commit to category-defining project) is a
  causal argument: coding agent quality enabling personal agent development. This is
  the concrete example of the RLVR → coding agents → autonomous agents causal chain.

### Claim 11: By April 2026, the Gemma 4 series was the most capable open-weight model lineup from a US company, while GLM-5.1 (754B parameters, 1.51TB) was a massive Chinese lab open-weight model that required substantial hardware

- **Evidence**: Willison's April 2026 section covers multiple major open-weight
  releases. Gemma 4 and GLM-5.1 are presented as the headline open-weights developments.
- **Confidence**: emerging (Willison's practitioner assessment at time of publication;
  "most capable US open-weight" is a qualitative claim subject to benchmark
  disagreement)
- **Quote** (GLM-5.1 size): "754B parameter, 1.51TB" (verified against
  `blog-simonwillison-glm51.md` Claim 1: "Chinese AI lab Z.ai's latest model is a
  giant 754B parameter 1.51TB (on Hugging Face) MIT-licensed monster")
- **Our assessment**: The April 2026 open-weights releases represent a step-change in
  what was available to practitioners who could afford or access the hardware. Gemma 4
  as the best US open-weights option and GLM-5.1 as the largest available open model
  together define the frontier of the non-proprietary model ecosystem in April 2026.
  The hardware caveat for GLM-5.1 is important: a 1.51TB model is not practically
  runnable by individual practitioners without specific infrastructure.

### Claim 12: Qwen3.6-35B-A3B (20.9GB, laptop-runnable) outperformed Claude Opus 4.7 on the pelican SVG benchmark in April 2026, signaling that the benchmark has saturated as a frontier differentiator

- **Evidence**: Willison's direct comparison: a 20.9GB model running locally beat a
  frontier proprietary model on his benchmark task. He explicitly notes this exceeds
  the benchmark's utility.
- **Confidence**: anecdotal (single practitioner test on one benchmark task; but the
  result is striking and specific)
- **Quote**: "20.9GB file that runs on my laptop" (about Qwen3.6-35B-A3B)
- **Our assessment**: A 20.9GB model outperforming a frontier proprietary model on a
  creative spatial-reasoning task is strong evidence for how rapidly open-weight
  models had improved by April 2026. The guide implication: the quality gap between
  frontier proprietary and capable laptop-runnable models was closing much faster
  than most practitioners assumed. The benchmark saturation is also meaningful — the
  pelican test stopped differentiating between "frontier" and "very good" in April
  2026. Practitioners building model-selection heuristics need tasks harder than this
  to distinguish frontier from near-frontier quality.

### Claim 13: Two themes dominate the six-month retrospective: coding agents matured significantly; laptop-available open-weight models wildly outperformed expectations despite remaining weaker than frontier models

- **Evidence**: Willison's explicit synthesis at the end of the talk, stated as his
  two main findings from the period.
- **Confidence**: emerging (practitioner retrospective synthesis; coherent with the
  specific claims documented throughout the post)
- **Quote**: "the laptop-available models, while a lot weaker than the frontier, have
  started wildly outperforming expectations"
- **Our assessment**: The explicit acknowledgment that laptop models are "a lot weaker
  than the frontier" while still "wildly outperforming expectations" is the nuanced
  framing practitioners need: not "open-weights have caught up with frontier" (they
  haven't) but "open-weights have crossed a quality threshold that nobody expected
  them to reach so quickly." This distinction matters for guide advice: teams should
  evaluate open-weight models seriously for tasks where absolute frontier capability
  is not required, but should not expect parity for the hardest tasks.

## Concrete Artifacts

### Model Leadership Timeline: November 2025

```
Simon Willison, PyCon US 2026 lightning talk / simonwillison.net/2026/May/19/5-minute-llms/

"The 'best' model changed hands 5 times between Anthropic, OpenAI and Google"

Sequence (by pelican-bicycle benchmark assessment):
  Claude Sonnet 4.5     — 29th September (held position entering November)
  GPT-5.1               — November 13
  Gemini 3              — November 18
  GPT-5.1 Codex Max     — November 19
  Claude Opus 4.5       — November 24

Note from Willison: "Gemini 3 drew the best pelican out of this lot,
but pelicans aren't everything."
```

### Open-Weights Capability Timeline: April 2026

```
Simon Willison, PyCon US 2026 lightning talk / simonwillison.net/2026/May/19/5-minute-llms/

Key releases (April 2026):
  Gemma 4        — April 2   — "most capable open weight models from a US company"
                               (Willison's characterisation)
  GLM-5.1        — April 7   — 754B parameters, 1.51TB (Z.ai / Chinese lab GLM)
                               MIT-licensed, requires substantial hardware
  Qwen3.6-35B-A3B              20.9GB, runs on a laptop
                               Willison: outperformed Claude Opus 4.7 at pelican test

Also released in this period: Gemini 3.5 Flash, DeepSeek V4 (see separate notes)
```

### The Claws Emergence Timeline

```
Simon Willison, PyCon US 2026 lightning talk / simonwillison.net/2026/May/19/5-minute-llms/

CODING AGENT QUALITY LEAP (Nov 2025)
  Mechanism: RLVR training completing at both OpenAI and Anthropic
  Result: "Coding agents went from often-work to mostly-work"

OPENCLAWS ORIGIN
  End of November 2025  — First commit to "Warelay" project
  [Name sequence: Warelay → CLAWDIS → CLAWDBOT → Clawdbot → Moltbot → OpenClaw]
  February 2026         — "OpenClaw" name / exploded in popularity

CATEGORY NAMING
  Generic term "Claws" crystallised around OpenClaw, NanoClaw, ZeroClaw
  Hardware: Mac Mini (low-cost, always-on, capable of local frontier models)
  Cultural framing (Drew Breunig): "the new digital pets;
    a Mac Mini is the perfect aquarium for your Claw"
```

### The Pelican Benchmark Evolution

```
Simon Willison, PyCon US 2026 lightning talk / simonwillison.net/2026/May/19/5-minute-llms/

Willison's rationale: "pelicans are hard to draw, bicycles are hard to draw,
  pelicans can't ride bicycles... and there's zero chance any AI lab would
  train a model for such a ridiculous task"
  [Note: ellipsis may represent WebFetch join of adjacent sentences]

Progression:
  November 2025   — Gemini 3 drew "the best pelican out of this lot"
  February 2026   — Gemini 3.1 Pro: "a really good pelican riding a bicycle
                    [with] a fish in its basket" — new quality bar
  April 2026      — Qwen3.6-35B-A3B (20.9GB, laptop) outperforms Claude Opus 4.7
                    → benchmark saturation: no longer reliably distinguishes
                       frontier from near-frontier capability
```

## Cross-References

- **Corroborates**:
  - `blog-simonwillison-voice-mode-weaker.md` Claim 3 ("Code tasks receive
    disproportionate AI model investment because they have explicit, verifiable reward
    functions that enable RL training"): The current source shows the practical result
    of the mechanism Karpathy described in that note. RLVR running throughout 2025 at
    both Anthropic and OpenAI is exactly the "verifiable reward function enables RL
    training at scale" story playing out — and Claim 1 here documents the practitioner-
    visible result: the "often-work to mostly-work" threshold crossing in November 2025.
    Together the two notes give the structural reason (voice-mode note) and the outcome
    (this note).
  - `blog-simonwillison-glm51.md` Claim 1 ("GLM-5.1 is a 754B parameter MIT-licensed
    open-weights model from Z.ai, accessible via OpenRouter"): Claim 11 here corroborates
    the factual metadata about GLM-5.1 (754B, 1.51TB) and places it in the broader April
    2026 open-weights quality wave context that the GLM-5.1 note does not provide.
  - `blog-thebatch-hermes-openclaw-tml-cybersecurity.md` Claim 1 ("Hermes Agent
    overtook OpenClaw on OpenRouter despite complaints about token inefficiency"): That
    note documents OpenClaw's later dominance and Hermes's overtaking of it (May 2026).
    The current source documents OpenClaw's origin (first commit November 2025, explosion
    February 2026) and its cultural context. Together the two notes trace the full
    OpenClaw trajectory: origin → dominance → being overtaken.

- **Extends**:
  - `blog-simonwillison-vibe-coding-agentic-engineering.md`: That note (May 6, 2026)
    documents Willison reflecting on the convergence of vibe coding and responsible
    agentic engineering and the normalization-of-deviance risk. The current source
    provides the chronological foundation for that reflection: the December–January "LLM
    psychosis" period documented here (Claim 6) is the same wave of over-excited
    experimentation that the vibe-coding note diagnoses as a professional risk. The
    micro-javascript project (nobody needed it) is the concrete example of what
    Willison was already recognizing as a problem in the later note.
  - `blog-simonwillison-glm51.md`: That note covers GLM-5.1 in depth (single-model
    hands-on test, SVG generation quality). The current source adds narrative context:
    GLM-5.1 as one of a cluster of major April 2026 open-weights releases that together
    constitute a step-change in what non-proprietary models could do.
  - `blog-simonwillison-deepseek-v4.md`: DeepSeek V4 is a contemporaneous April 2026
    release not covered in the current source. That note's detailed treatment of pricing
    and efficiency complements the current source's narrative-level treatment of the
    April open-weights wave.

- **Contradicts**: None identified. No claim in this source materially opposes a
  claim in any existing corpus note in a way that would lead to different guide advice.
  The RLVR mechanism (Claim 2) is consistent with the Karpathy/Willison voice-mode
  note. The November 2025 inflection is consistent with the French-Owen coding agents
  February note (which documents post-inflection quality as its starting assumption).
  The open-weights quality trajectory is consistent with GLM-5.1 and DeepSeek notes.

- **Novel**:
  - **"November 2025 inflection point" as a named historical marker**: No other corpus
    note explicitly names November 2025 as a defined inflection point for coding agents
    or explains the RLVR training completion as its mechanism. Individual model-release
    notes exist for each November model, but none synthesize the month as a named
    threshold. The "often-work to mostly-work" language is the first precise one-sentence
    characterisation of the quality transition in the corpus.
  - **"Claws" as an established category term for personal AI assistants**: No prior
    corpus note documents the emergence of "Claws" as a generic category, its derivation
    from OpenClaw/NanoClaw/ZeroClaw, or its cultural context (Mac Mini as aquarium, Breunig
    metaphor). The Hermes/OpenClaw note covers OpenClaw as a specific product; the current
    source documents it as a category.
  - **Mac Mini sellout as concrete cultural evidence of personal AI assistant adoption**:
    The specific hardware-market signal (Mac Minis selling out in Silicon Valley) is not
    documented elsewhere in the corpus. It provides concrete evidence that the Claws
    category drove real purchasing behavior, not just practitioner interest.
  - **OpenClaw origin story (Warelay → name sequence → February explosion)**: The
    detailed origin and trajectory of OpenClaw — first commit November 2025, multiple
    name changes, February explosion — is not captured in any existing note. The Hermes/
    OpenClaw note covers it only at the point of OpenRouter dominance.
  - **Pelican benchmark saturation**: The narrative of the pelican benchmark progressing
    from frontier differentiator (November 2025) through Gemini 3.1 improvement (February)
    to full saturation by a laptop model (April 2026, Qwen3.6) is unique to this source.
    No other note documents the benchmark's lifecycle.
  - **"LLM psychosis" framing for the December–January experimentation wave**: The
    cultural framing of the holiday experimentation period as producing "over-excited"
    projects of questionable utility is unique to this note. The micro-javascript example
    is the concrete artifact.

## Guide Impact

- **Chapter 02 (Coding Agents — The Quality Threshold)**: Claims 1 and 2 provide the
  most precise language in the corpus for the November 2025 quality transition:
  "often-work to mostly-work" via RLVR. The guide currently lacks a named inflection
  point with an explained mechanism. Add a section anchored by Willison's characterisation:
  "RLVR training throughout 2025 at both Anthropic and OpenAI enabled coding agents to
  cross a quality threshold in November 2025" — pair with `blog-simonwillison-voice-mode-weaker.md`
  Claim 3 for the structural explanation and this source for the practitioner-visible result.

- **Chapter 03 (Agentic Workflows — Personal AI Assistants / "Claws")**: Claims 6, 7, 8,
  9, and 10 together describe a concrete architectural and cultural pattern: personal AI
  assistants running on dedicated local hardware. The guide should introduce "Claws" as a
  named category (alongside orchestrated agents and cloud agents), document the Mac Mini as
  representative hardware, and use the Breunig "digital pets / aquarium" metaphor to make the
  concept vivid. The OpenClaw origin story (Claim 10) should anchor a timeline of when this
  category emerged and why (good coding agents were the prerequisite).

- **Chapter 03 (Agentic Workflows — Model Landscape)**: Claim 3 (5 model changes in November)
  should appear in any section on model selection as evidence of how volatile frontier
  leadership was during the November 2025 inflection. Teams building model-selection processes
  should account for multi-week leadership churn, not just annual cycles.

- **Chapter 04 (Open-Weight Models)**: Claims 11, 12, and 13 together establish the state of
  open-weights as of April 2026: Gemma 4 (best US open-weight), GLM-5.1 (largest overall,
  hardware-intensive), Qwen3.6 (laptop-runnable, beating frontier models on creative coding).
  The conclusion "wildly outperforming expectations despite remaining weaker than frontier"
  should anchor the guide's framing of open-weight model utility: good enough for many tasks,
  not yet at frontier for the hardest ones.

- **Chapter 02 (Evaluating Models — Benchmark Design)**: Claim 4 (pelican benchmark anti-
  Goodhart rationale) and Claim 12 (benchmark saturation) together make a guide-ready point
  about evaluation heuristics: even carefully designed anti-benchmark-specific tests saturate
  as models improve. Teams should design evaluation tasks that are both practical and resistant
  to saturation — and should plan to update evaluations periodically rather than assuming any
  static benchmark remains informative. The pelican benchmark lifecycle is a concrete case study
  for this pattern.

- **Chapter 01 (Adoption Patterns — Experimentation Cycles)**: Claim 6 (LLM psychosis,
  over-excited holiday projects) is a useful cultural framing for the guide's adoption
  chapter. The pattern — quality threshold → free time → wave of marginally useful experimentation
  — is predictable and should be planned for. Organizations doing structured AI adoption should
  channel this energy toward evaluation and production-useful experiments, not discourage it.

## Extraction Notes

- **Source is annotated lightning-talk slides, not a long-form essay**: The source is
  structured as a PyCon talk retrospective with section headings and slide-level content.
  Individual sections are brief; the value is the synthesis and the specific named claims
  (inflection point, often-work to mostly-work, Claws, pelican saturation) rather than
  extended analysis.
- **WebFetch produced paraphrases for several sections**: The WebFetch tool returned summaries
  rather than fully verbatim content for some sections (notably the April 2026 section,
  the OpenClaw origin details, and the concluding synthesis). All Quote fields are marked
  "no direct quote" where verbatim text could not be confirmed. The GLM-5.1 metadata (754B,
  1.51TB) was verified against `blog-simonwillison-glm51.md` Claim 1. The pelican-benchmark
  quotes were obtained verbatim from multiple consistent WebFetch extractions.
- **Ellipsis in some quotes**: Two quotes contain ellipsis ("...") which may represent
  the WebFetch tool joining adjacent sentences rather than a single continuous passage in
  the source. Both are flagged in the respective Quote fields.
- **No contradictions filed**: Claims were checked against the full relevant corpus section.
  No claim in this source materially opposes an existing note in a way requiring a
  contradiction issue.
- **Cross-references verified**: For all cited source notes, claim numbers were verified
  by re-reading the relevant sections: `blog-simonwillison-voice-mode-weaker.md` Claim 3
  (line 79: "Code tasks receive disproportionate AI model investment..."), `blog-simonwillison-glm51.md`
  Claim 1 (line 24), `blog-thebatch-hermes-openclaw-tml-cybersecurity.md` Claim 1 (line 46).
  All confirmed before writing.
- **Source URL note**: The issue URL included `#atom-everything` (Atom feed fragment);
  the canonical page URL without the fragment is used as `source_url`.
