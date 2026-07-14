---
source_url: https://www.promptfoo.dev/blog/ai-regulation-2025/
source_type: blog-post
title: "How AI Regulation Changed in 2025"
author: "Michael D'Angelo (Promptfoo Co-founder & CTO)"
date_published: 2025-12-15
date_extracted: 2026-07-14
last_checked: 2026-07-14
status: current
confidence_overall: emerging
issue: "#201"
---

# How AI Regulation Changed in 2025

> A well-sourced 2025 survey of AI regulatory change — federal (OMB M-26-04, EO
> 14319), state (Colorado SB24-205, California AB 2013/SB 53/SB 942, Texas HB
> 149, NYC LL144), and international (EU AI Act, China filing/labeling) — that
> argues the engineering implication is that agentic, tool-using systems break
> text-in/text-out compliance assumptions and force testing of the *action path*,
> not just model output.

## Source Context

- **Type**: blog-post (vendor practitioner analysis/survey, Promptfoo)
- **Author credibility**: Michael D'Angelo, Co-founder & CTO of Promptfoo (the
  article banner notes Promptfoo is now part of OpenAI). The regulatory claims
  are anchored to primary documents with specific citations — OMB M-26-04
  (Dec 2025), EO 14319 (July 2025), EO 14179/14110, named state bills
  (SB24-205, AB 2013, SB 53, SB 942, HB 149, NYC LL144), the EU AI Act
  (Regulation 2024/1689), and China's CAC interim measures and GB 45438-2025.
  The article is a synthesis of public legal/regulatory text, not original
  research, and closes with a product pitch for Promptfoo's red-teaming/eval
  tooling. Treat the regulatory *facts* (dates, citations) as high-credibility
  and the engineering *implications* (what regulators "will" demand) as the
  author's interpretation.
- **Scope**: What changed in US federal/state and international AI regulation in
  2025 and the 2026 compliance timeline; the "Technical Context" section on how
  agentic systems change the testing/eval surface. Does NOT cover: how to
  implement specific guardrails, detection pipelines, or incident-response
  runbooks (it links out to NCSC and OWASP for those). The body is a factual
  regulatory survey; only the final section is a sales pitch.
- **Note on Prospector triage**: The triage comment stated "Promptfoo is not yet
  represented in source-notes/." That is incorrect — `blog-promptfoo-ai-
  orchestrated-cyberattacks.md` (#203) already covers a Promptfoo source by the
  *same author*. This note cross-references it directly (see below). The two
  Promptfoo posts are complementary: #203 is the offensive/threat-model angle;
  this one is the regulatory/compliance demand-side angle for the same testing
  thesis.

## Extracted Claims

### Claim 1: AI regulation reaches product through a stack — executive order → OMB memo → procurement language → contract requirement → request for evidence
- **Evidence**: The article's organizing thesis. "This is why 2025 mattered: the
  stack filled in. Executive orders issued years ago became OMB memos, which
  became procurement language, which became contract requirements, which became
  requests for evidence that vendors need to produce." Concrete symptom cited:
  "Enterprise security questionnaires added AI sections... RFPs began requiring
  documentation that didn't exist six months ago."
- **Confidence**: settled
- **Quote**: "Executive orders issued years ago became OMB memos, which became procurement language, which became contract requirements, which became requests for evidence that vendors need to produce."
- **Our assessment**: A useful mental model for the guide — compliance arrives as
  a *procurement* force, not a direct statute, so the practical trigger for most
  builders is a security questionnaire or RFP. This reframes "AI compliance" as an
  SRE/ops concern (produce artifacts on demand), which is the article's core
  bridge to engineering.

### Claim 2: OMB M-26-04 (issued December 2025) requires federal agencies buying LLMs to obtain model cards, evaluation artifacts, and acceptable use policies by March 2026
- **Evidence**: Specific memo and deadline. "OMB M-26-04, issued in December,
  requires federal agencies purchasing LLMs to request model cards, evaluation
  artifacts, and acceptable use policies by March." Later: "Agencies must update
  their procurement policies by March 11, 2026."
- **Confidence**: settled
- **Quote**: "requires federal agencies purchasing LLMs to request model cards, evaluation artifacts, and acceptable use policies by March."
- **Our assessment**: This is the single most concrete compliance forcing function
  in the piece. The artifact list (model cards, evaluation artifacts, AUPs) is
  exactly what an eval/observability pipeline produces — the link to Ch05/Ch02 is
  direct. The March 11, 2026 date is specific and verifiable.

### Claim 3: EO 14319 (July 2025) established two "Unbiased AI Principles" for federal LLMs — truth-seeking and ideological neutrality
- **Evidence**: "Executive Order 14319 added requirements specific to large
  language models, establishing two 'Unbiased AI Principles'." The two are
  defined: "Truth-seeking: LLMs should provide accurate responses to factual
  queries and acknowledge uncertainty when appropriate" and "Ideological
  neutrality: LLMs should not encode partisan viewpoints into outputs unless
  specifically prompted."
- **Confidence**: settled
- **Quote**: "Truth-seeking: LLMs should provide accurate responses to factual queries and acknowledge uncertainty when appropriate."
- **Our assessment**: These principles are the *content* of the behavior federal
  buyers will demand evidence for. Note the federal framing treats accuracy and
  non-discrimination as potentially in tension (see Claim 11) — a genuinely
  novel, contested axis the guide's Ch06 should capture, not flatten.

### Claim 4: The December OMB memo specifies four artifacts vendors must supply — system/data cards, evaluation artifacts, acceptable use policy, and a feedback mechanism
- **Evidence**: The article's artifact table, with descriptions: "Model/system/
  data cards — Documentation of training, capabilities, limitations";
  "Evaluation artifacts — Results from testing"; "Acceptable use policy — What the
  system should and shouldn't do"; "Feedback mechanism — How users report
  problematic outputs."
- **Confidence**: settled
- **Quote**: "Evaluation artifacts Results from testing"
- **Our assessment**: This is the concrete deliverable清单. For builders, the
  mapping is: eval artifacts = your red-team/regression suite output; system card
  = your model/prompt/tool/retrieval inventory; feedback mechanism = a "report
  output" button + triage workflow. This is the artifact backbone the guide's
  Ch05/Ch06 can adopt verbatim.

### Claim 5: For application builders, the required evaluation artifacts are red-team results for tool misuse, prompt injection, and data leakage
- **Evidence**: "Evaluation artifacts: red-team results for tool misuse, prompt
  injection, and data leakage." Set alongside "System card: which model(s) you
  use, your prompts/policies, tools, retrieval sources, and human review points"
  and "Acceptable use policy: what your UI allows, what it blocks, and what your
  system won't do."
- **Confidence**: emerging
- **Quote**: "Evaluation artifacts: red-team results for tool misuse, prompt injection, and data leakage"
- **Our assessment**: This is the most guide-actionable sentence in the source:
  it names the *exact* red-team categories a compliance-grade eval suite must
  cover. It directly dovetails with `blog-pagerduty-production-ai-agent-gaps.md`
  Claim 5 (prompt injection susceptibility 80-90%) and `blog-promptfoo-ai-
  orchestrated-cyberattacks.md` Claim 12 (promptfoo red-team configs for
  exfiltration/leak/prompt-injection). The compliance world is now mandating what
  the security notes already recommend.

### Claim 6: State laws add specific, dated obligations — Colorado SB24-205 (June 30, 2026), California AB 2013 training-data transparency (Jan 1, 2026), California SB 942 (Aug 2, 2026), Texas HB 149 (Jan 1, 2026), NYC LL144 (in effect)
- **Evidence**: A state-law table with compliance dates. Colorado SB24-205:
  "Deployer obligations: impact assessments, algorithmic discrimination
  prevention, consumer notices, appeals — June 30, 2026 (originally Feb 1)."
  California AB 2013: "Training data transparency (includes fine-tuning) — January
  1, 2026." Texas HB 149: "Prohibited practices, government AI disclosure —
  January 1, 2026." NYC Local Law 144: "Bias audits, candidate notice for hiring
  AI — In effect."
- **Confidence**: settled
- **Quote**: "Colorado SB24-205 (delayed by SB25B-004) Deployer obligations: impact assessments, algorithmic discrimination prevention, consumer notices, appeals June 30, 2026 (originally Feb 1)"
- **Our assessment**: The dates are specific and the corpus has no other source
  covering the *state* compliance calendar. High value for Ch06 as a concrete
  "what's due when" reference. The recurring theme — impact assessments, bias
  audits, consumer notices, appeal pathways — maps to the audit-trail/logging
  requirements this article repeatedly stresses.

### Claim 7: The EU AI Act began phasing in 2025 (prohibited practices Feb 2025, GPAI obligations Aug 2025) with high-risk system requirements scheduled for August 2026, but a November 2025 "Digital Omnibus" proposal may delay high-risk obligations 16 months to December 2027
- **Evidence**: "August 2026: High-risk AI system requirements were scheduled to
  apply" and "the Commission proposed a Digital Omnibus package in November 2025
  that would delay high-risk obligations by 16 months, to December 2027. The
  proposal still requires Parliament and Council approval."
- **Confidence**: emerging
- **Quote**: "the Commission proposed a Digital Omnibus package in November 2025 that would delay high-risk obligations by 16 months, to December 2027."
- **Our assessment**: Accurately captures a moving target — the timeline is
  explicitly unsettled (needs Parliament/Council approval). Good illustration for
  the guide that the regulatory landscape is not static; builders should architect
  for adaptability rather than optimize for one regime (echoes Claim 14).

### Claim 8: China governs AI via administrative filing and content labeling — 611 generative-AI services and 306 apps had filed as of November 2025, and GB 45438-2025 mandates visible labels, provenance metadata, and a six-month log-retention requirement in specific cases
- **Evidence**: "As of November 2025, 611 generative AI services and 306 apps had
  completed this process, and apps must now publicly disclose which filed model
  they use, including the filing number." On labeling: "AI-generated content must
  include visible labels, metadata identifying the source and provider, and
  platforms must verify labels before distribution. Tampering is prohibited. The
  rules include a six-month log retention requirement in specific cases (for
  example, when explicit labeling is suppressed at a user's request)."
- **Confidence**: settled
- **Quote**: "AI-generated content must include visible labels, metadata identifying the source and provider, and platforms must verify labels before distribution. Tampering is prohibited. The rules include a six-month log retention requirement in specific cases (for example, when explicit labeling is suppressed at a user's request)."
- **Our assessment**: The six-month log-retention requirement is the most
  engineering-relevant detail for an SRE audience — it's a concrete, auditable
  retention obligation that maps onto logging/observability infrastructure
  (Ch02). The "provenance metadata" requirement also aligns with the article's
  recurring audit-trail theme.

### Claim 9: The center of gravity in 2025 shifted from single-prompt completion to agentic systems that plan, call tools, maintain state, and take external actions — simultaneously across US and Chinese labs
- **Evidence**: "The center of gravity shifted in 2025: from single-prompt
  completion to agentic systems that plan over many steps, call tools, maintain
  state across long interactions, and take actions in external environments."
  Substantiated by the "lab/model" release table (OpenAI, Anthropic, Google,
  Meta, DeepSeek, Qwen) all shipping tool-calling / long-horizon / agent-first
  models.
- **Confidence**: settled
- **Quote**: "from single-prompt completion to agentic systems that plan over many steps, call tools, maintain state across long interactions, and take actions in external environments."
- **Our assessment**: This is the pivot from "regulation survey" to "engineering
  thesis," and it is the most novel angle for this corpus. It is a settled
  industry observation (all frontier vendors shipped tool-use in 2025) and sets up
  Claims 10-12. Corroborates `blog-litellm-agents-are-the-new-llms.md` Claim 5
  (primitive shifts from model call to agent session) and `blog-honeycomb-
  instrumenting-ai-agents-opentelemetry.md` Claim 5 (tool calls are where most
  agentic failures live).

### Claim 10: Regulations written for text-in/text-out systems don't map to systems that choose tools, interpret output, recover from errors, and mutate external state
- **Evidence**: "The compliance implication: regulations written for text-in-text-
  out systems don't map cleanly to systems that choose tools, interpret tool
  output, recover from errors, and mutate external state. Evaluating whether a
  model hallucinates is different from evaluating whether an agent selects the
  right tool, handles its errors appropriately, and takes actions aligned with
  user intent."
- **Confidence**: emerging
- **Quote**: "regulations written for text-in-text-out systems don't map cleanly to systems that choose tools, interpret tool output, recover from errors, and mutate external state."
- **Our assessment**: This is the article's sharpest engineering claim and the
  best one-liner for the guide's Ch06: the compliance/eval surface shifts from
  *output quality* to *action quality*. It directly motivates why tool selection,
  error handling, and rollback must be tested (Claim 12). Emerging rather than
  settled because it is the author's synthesis, not a quoted regulatory text.

### Claim 11: Impact assessments and audits must cover the deployed stack — prompts, tool inventory, tool permissions, retrieval, memory, and logging — not just the base model
- **Evidence**: "Impact assessments and audits need to cover the deployed stack:
  prompts, tool inventory, tool permissions, retrieval, memory, and logging, not
  just base models."
- **Confidence**: emerging
- **Quote**: "Impact assessments and audits need to cover the deployed stack: prompts, tool inventory, tool permissions, retrieval, memory, and logging, not just base models."
- **Our assessment**: This is the operational checklist the guide can lift
  directly into Ch06/Ch05. Every item (tool inventory, tool permissions, retrieval,
  memory, logging) is an observability/eval concern the Datadog and Honeycomb
  notes already treat as first-class (see Cross-References). The claim turns
  abstract "compliance" into a concrete inventory/audit scope.

### Claim 12: Testing must cover deployed systems — test retrieval quality if you retrieve, tool selection and error handling if you use tools, behavior at varying context lengths if you maintain state, and adversarial (not just cooperative) conditions if you read untrusted input
- **Evidence**: "If your application uses retrieval, test retrieval quality. If it
  uses tools, test tool selection and error handling. If it maintains context
  across turns, test behavior at different context lengths. If it reads untrusted
  input, test adversarial conditions, not just cooperative ones."
- **Confidence**: emerging
- **Quote**: "If your application uses retrieval, test retrieval quality. If it uses tools, test tool selection and error handling. If it maintains context across turns, test behavior at different context lengths. If it reads untrusted input, test adversarial conditions, not just cooperative ones."
- **Our assessment**: This is the actionable test-design guidance and it is
  excellent. It maps one-to-one onto the failure modes in `blog-pagerduty-
  production-ai-agent-gaps.md` (context fatigue Claim 3, compounding errors Claim
  4, prompt injection Claim 5) and `blog-honeycomb-instrumenting-ai-agents-
  opentelemetry.md` Claim 5 (tool calls are where failures live). The "adversarial,
  not cooperative" instruction is the key evaluand for red-teaming (cf. the
  cyberattacks note's CI-gated adversarial testing).

### Claim 13: If an AI can take actions (refunds, emails, record edits, code execution), compliance applies to the action path, not just the text output — so agentic systems need rollback-behavior testing
- **Evidence**: "If your AI can take actions, regulators will evaluate the
  actions. If your system can issue refunds, send emails, modify records, or
  execute code, compliance requirements apply to the action path, not just the text
  output. This is why agentic systems need testing that covers tool selection,
  error handling, and rollback behavior."
- **Confidence**: emerging
- **Quote**: "If your system can issue refunds, send emails, modify records, or execute code, compliance requirements apply to the action path, not just the text output. This is why agentic systems need testing that covers tool selection, error handling, and rollback behavior."
- **Our assessment**: The "rollback behavior" requirement is the novel,
  testable contribution here — it extends the agent-reliability discussion (which
  usually stops at error handling) to *reversibility*. Strong material for Ch03
  (Runbooks and Agents) on scoping agent permissions and mandating rollback/undo
  paths. Emerging because it is interpretive, but well-reasoned.

### Claim 14: The regulatory landscape is unsettled (federal-state conflict unresolved, preemption litigation not started, international requirements diverging), so compliance infrastructure should adapt to multiple regimes rather than optimize for one
- **Evidence**: "The regulatory landscape is unsettled. The federal-state conflict
  isn't resolved. Preemption litigation hasn't started. International requirements
  continue to diverge. Building compliance infrastructure that adapts to different
  requirements is more practical than optimizing for any single regime."
- **Confidence**: emerging
- **Quote**: "Building compliance infrastructure that adapts to different requirements is more practical than optimizing for any single regime."
- **Our assessment**: Sound architectural advice that mirrors the guide's general
  "design for change" posture. It is a meta-claim about how to build compliance
  tooling; aligns with the "don't over-fit to one SLO/regime" instinct elsewhere
  in the corpus.

### Claim 15: If you only do one thing before 2026, make your AI system's behavior measurable, repeatable, and explainable to someone outside your team
- **Evidence**: Closing directive: "If you only do one thing before 2026: make
  your AI system's behavior measurable, repeatable, and explainable to someone
  outside your team."
- **Confidence**: emerging
- **Quote**: "If you only do one thing before 2026: make your AI system's behavior measurable, repeatable, and explainable to someone outside your team."
- **Our assessment**: This is the article's thesis in one sentence and the cleanest
  bridge to the corpus's recurring themes — observability (Ch02), evaluation
  (Ch05), and trust/auditability (Ch06). "Explainable to someone outside your
  team" is precisely the model-card/evaluation-artifact requirement from Claims
  2-4.

## Concrete Artifacts

### OMB M-26-04 required artifact set (verbatim table from the article)

```
Artifact            | Description
--------------------|-------------------------------------------------------------
Model/system/data   | Documentation of training, capabilities, limitations
  cards             |
Evaluation artifacts| Results from testing
Acceptable use      | What the system should and shouldn't do
  policy            |
Feedback mechanism  | How users report problematic outputs
```
*Source: promptfoo blog, "July: LLM Procurement Requirements" section — the four artifacts federal agencies must request under the December OMB memo implementing EO 14319.*

### What application builders must prepare (verbatim list from the article)

```
System card        : which model(s) you use, your prompts/policies, tools,
                     retrieval sources, and human review points
Evaluation artifacts: red-team results for tool misuse, prompt injection,
                     and data leakage
Acceptable use policy: what your UI allows, what it blocks, and what your
                     system won't do
Feedback mechanism : a "report output" button plus an internal triage workflow
```
*Source: promptfoo blog, "July: LLM Procurement Requirements" → "For application builders, this means preparing:"*

### 2026 compliance timeline (verbatim table from the article)

```
Date        | Event
------------|-------------------------------------------------------------
Jan 1       | California AB 2013 (training data transparency) effective
Jan 1       | Texas HB 149 effective
~Jan 10     | DOJ AI Litigation Task Force established
~Mar 11     | Commerce evaluation of state laws due
~Mar 11     | FTC policy statement on preemption due
Mar 11      | Agencies update LLM procurement policies (M-26-04)
May 19      | TAKE IT DOWN Act (S. 146): platforms must remove nonconsensual
            |   intimate images within 48 hours of valid request
~Jun 11     | FCC proceeding on federal disclosure standard begins
Jun 30      | Colorado SB24-205 compliance
Aug 2       | California SB 942 effective
Aug 2026    | EU AI Act high-risk requirements scheduled (may slip to
            |   Dec 2027 per Digital Omnibus proposal)
```
*Source: promptfoo blog, "2026 Timeline" section.*

### Lab/model release → compliance-implication mapping (verbatim table excerpt)

```
Lab / Model              | 2025 Releases                       | Compliance Implication
-------------------------|-------------------------------------|---------------------------------------------
OpenAI (GPT-5.2, gpt-oss)| Tool calling, long-horizon reasoning,| Open weights mean your org becomes the
                         | open weights                         | "provider"; tool use expands test surface
                         |                                     | from output quality to action quality
Anthropic (Claude 4, 4.5)| Extended thinking interleaved with  | Agent workflows and "computer use"
                         | tools                                | interactions require testing tool selection,
                         |                                     | error handling, and action sequences
Google (Gemini 3 +       | Agent-first IDE, multi-surface       | Systems spanning editor/terminal/browser
 Antigravity)            | operation                            | are exactly what procurement questionnaires
                         |                                     | struggle to describe
```
*Source: promptfoo blog, "Technical Context" → lab/model table (excerpt; rows for Meta, DeepSeek, Qwen omitted for length). The "compliance implication" column is the article's own phrasing.*

### China content-labeling requirement (verbatim, from the article)

```
AI-generated content must include visible labels, metadata identifying the
source and provider, and platforms must verify labels before distribution.
Tampering is prohibited. The rules include a six-month log retention
requirement in specific cases (for example, when explicit labeling is
suppressed at a user's request).
```
*Source: promptfoo blog, "China" section — labeling requirements (GB 45438-2025) effective September 2025.*

## Cross-References

- **Corroborates**:
  - `blog-promptfoo-ai-orchestrated-cyberattacks.md` (#203, *same author and
    publisher*) — this article's Claims 5, 10, 12-13 (test tool misuse / prompt
    injection / data leakage; test the action path incl. rollback) are the
    *demand-side* counterpart to that note's Claim 11 ("Continuous adversarial
    testing is now table stakes... run red-team exercises quarterly") and Claim 12
    (promptfoo red-team configs produce a CI/CD security scorecard). This note
    supplies the external forcing function (M-26-04, EO 14319, state laws) that
    makes the cyberattacks note's recommended CI-gated red-teaming *contractually
    required*, not optional. Both notes also converge on the same artifact pitch
    (exportable results, regression tests, audit trails).
  - `blog-pagerduty-production-ai-agent-gaps.md` — Claim 12 (metrics framework
    tracking tool error rates, safety violations, human escalation) and Claim 10
    (automated eval pipelines + golden datasets + LLM-as-a-judge + CI gates) and
    Claim 15 (deterministic tests inadequate for NL systems) corroborate this
    article's Claims 4, 11-12 (eval artifacts, audit the deployed stack, test
    tool selection/error handling). Its Claim 5 (prompt injection susceptibility
    80-90%) is exactly the "prompt injection" eval category this article's Claim 5
    mandates. Together they argue CI-gated, artifact-producing evaluation is both
    a reliability and a compliance requirement.
  - `docs-datadog-llm-observability.md` — Claim 1 (an LLM-app request is "a single
    trace you can monitor, troubleshoot, and evaluate") and Claim 4 (span kinds
    include `Tool`) and Claim 2 (trace shapes include "dynamic agent") are the
    observability substrate this article's "logging must be in the impact
    assessment" (Claim 11) and six-month log-retention requirement (Claim 8)
    depend on. Corroborates that audit trails are a first-class engineering
    artifact.
  - `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` — Claim 5 ("Tool
    calls are where most agentic failures live") directly corroborates this
    article's central Claim 10/12 thesis that the test surface shifts to tool
    selection and error handling. Claim 1 ("The LLM is rarely the root cause of
    agent failures") and Claim 11 (attach evaluation results as span events)
    support the "audit what you tested" angle.
  - `blog-litellm-agents-are-the-new-llms.md` — Claim 5 (the primitive shifts
    "from the model call to the agent session") and Claim 6 (gateway shifts "from
    routing model calls to routing agent work") align with this article's Claim 9
    (agentic shift) and Claim 11 (govern the deployed stack of tools/retrieval/
    memory). The compliance scope effectively becomes "govern the agent session,"
    which is what the control-plane pattern argues for.

- **Contradicts**: None identified. This is a regulatory *survey*; the technical
  notes are engineering *guidance*. No claim here opposes an existing note's
  claim on the same topic in a way that would change guide advice. One nuance
  worth flagging for the Smith: this article frames prompt-injection/tool-misuse
  testing as a *compliance* obligation, whereas `blog-pagerduty-production-ai-
  agent-gaps.md` Claim 14 frames guardrails as defense-in-depth to *block* prompt
  injection — these are complementary (test AND block), not contradictory. No
  contradiction issue is required (CONTRADICTIONS.md has no entries and there are
  no open `contradiction`-labeled issues).

- **Extends**:
  - Extends `blog-promptfoo-ai-orchestrated-cyberattacks.md` by adding the
    *regulatory demand-side* rationale (M-26-04, EO 14319, state laws) for why
    that note's recommended CI-gated red-teaming artifact pipeline is becoming
    mandatory rather than advisory.
  - Extends `blog-pagerduty-production-ai-agent-gaps.md`'s evaluation/metrics
    material by adding the compliance/audit-trail requirement that elevates those
    pipelines from "reliability nice-to-have" to "contractually required
    evidence."

- **Novel**: This is the **first source in the corpus covering AI
  *regulation/compliance* as an engineering forcing function**. New to the corpus:
  - Specific, dated regulatory citations as a compliance calendar: OMB M-26-04
    (March 11, 2026 procurement deadline), EO 14319 "Unbiased AI Principles"
    (truth-seeking, ideological neutrality), Colorado SB24-205 (June 30, 2026),
    California AB 2013 (Jan 1, 2026) / SB 53 / SB 942 (Aug 2, 2026), Texas HB 149
    (Jan 1, 2026), NYC LL144 (in effect), EU AI Act high-risk (Aug 2026, possibly
    Dec 2027), China GB 45438-2025 labeling + six-month log retention.
  - The "documentation is now structural" framing and the four-artifact taxonomy
    (model/system/data cards, evaluation artifacts, AUP, feedback mechanism).
  - The explicit thesis (Claim 10) that text-in/text-out regulations don't map to
    tool-choosing, state-mutating agents, and the resulting requirement to test
    the *action path* including **rollback behavior** (Claim 13) — rollback is not
    covered by any other note.
  - The federal-vs-state tension on whether accuracy and non-discrimination
    conflict (a genuinely novel axis for Ch06).

## Guide Impact

- **Chapter 06 (Security and Trust)**: Primary destination. Add:
  - A "compliance as a forcing function" section built on Claims 1-2, 4-6, 11:
    security questionnaires/RFPs now demand model cards, evaluation artifacts, and
    AUPs; impact assessments must cover the *deployed stack* (prompts, tool
    inventory, tool permissions, retrieval, memory, logging).
  - The dated state/federal/international compliance calendar (Claim 6-8, Concrete
    Artifacts → 2026 Timeline) as a reference the guide currently lacks entirely.
  - The "test the action path, including rollback" requirement (Claims 10, 13) as
    a concrete agent-trust control — extends the existing agent-permissions
    guidance with a reversibility mandate.
  - The federal-vs-state accuracy/non-discrimination tension (Claim 3 / analysis)
    as a non-obvious trust-axis the chapter should name rather than flatten.

- **Chapter 05 (LLM Ops Reliability)**: Use Claims 4-5, 11-12 to argue that
  evaluation pipelines (already recommended via the PagerDuty note's Claim 10/12)
  are now *contractually required evidence*: red-team results for tool misuse,
  prompt injection, and data leakage are the "evaluation artifacts" M-26-04 asks
  agencies to collect. Connect the eval suite output to the compliance artifact
  taxonomy (system card, eval artifacts, AUP, feedback mechanism).

- **Chapter 02 (Observability)**: Use Claims 8 and 11 to add a compliance angle to
  logging: China's six-month log-retention requirement and the article's
  "logging must be in the impact assessment" claim make audit-trail completeness a
  measurable, regulated property — not just an ops nicety. Reinforces the
  Datadog/Honeycomb "trace everything, including tool spans" material with an
  external mandate.

- **Chapter 03 (Runbooks and Agents)**: Adopt the rollback-behavior testing
  requirement (Claim 13) and the "test tool selection and error handling,
  adversarial not cooperative" guidance (Claim 12) as concrete agent-design
  controls — scoping permissions, mandating undo/reversal paths, and red-teaming
  the action sequence rather than the output.

## Extraction Notes

- Source is a single long-form blog post (published 2025-12-15 by Michael D'Angelo,
  Promptfoo Co-founder & CTO; ~article reads as a substantive survey). Read in
  full via downloaded HTML (70 KB) converted to text; all quotes in this note were
  verified character-for-character against the raw HTML before writing.
- The article is vendor (Promptfoo) content and closes with a product pitch
  ("We built Promptfoo for exactly this..."). I extracted the substantive
  regulatory and technical-context claims and reproduced the tables verbatim as
  Concrete Artifacts, but treated the product-positioning framing as lower
  authority than the cited primary documents (OMB memos, EO text, named bills, EU
  Regulation 2024/1689, China CAC/GB standards).
- The Prospector triage comment incorrectly stated "Promptfoo is not yet
  represented in source-notes/." It is — `blog-promptfoo-ai-orchestrated-
  cyberattacks.md` (#203) is by the same author. I corrected this in the Source
  Context note and built the Cross-References on that existing note rather than
  treating Promptfoo as novel.
- I did NOT deep-follow the "Further Reading" primary documents (OMB M-26-04 PDF,
  EO text, individual state bill pages, EU AI Act full text, CAC filings). The
  blog post is self-contained for all Prospector key questions (compliance
  deadlines, documentation requirements, the agentic testing-surface thesis). The
  underlying legal texts are the primary sources the blog summarizes; mining them
  separately could tighten Claims 2-3/6-8 but is not required for this note.
- No part of the source was paywalled; publicly accessible. Date concern:
  published 2025-12-15, fast-moving regulatory content (preemption litigation, EU
  Digital Omnibus delays) may shift — I marked the forward-looking timeline claims
  as `emerging` and flagged the unsettled status explicitly in Claims 7 and 14.
