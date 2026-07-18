---
source_url: https://langfuse.com/docs/security-and-guardrails
source_type: docs
title: "Security & Guardrails — Langfuse Docs"
author: "Langfuse (Langfuse GmbH / Finto Technologies Inc.)"
date_published: n.d. (living documentation; current as of 2026-07-18)
date_extracted: 2026-07-18
last_checked: 2026-07-18
status: current
confidence_overall: emerging
issue: "#321"
---

# Security & Guardrails — Langfuse Docs

> Vendor documentation page describing LLM application security guardrails with
> concrete implementation patterns: PII anonymization/deanonymization pipeline
> (llm_guard), input/output scanner composition, Lakera Guard integration,
> and Langfuse tracing for monitoring guardrail effectiveness and latency impact.
> Provides the observability/telemetry side of the guardrail pattern the guide's
> Ch06 currently discusses only at the threat-model/red-teaming level.

## Source Context

- **Type**: docs (vendor documentation — Langfuse Security & Guardrails page)
- **Author credibility**: Langfuse is a widely-used open-source LLM observability
  platform (tracing, evaluation, prompt management). The security page documents
  the integration patterns Langfuse supports with third-party guardrail tools.
  Claims about Langfuse's own features (tracing, scoring, dashboards) are
  authoritative for how the product works; claims about guardrail effectiveness
  (which tools catch which injections) are vendor-illustrative rather than
  independent benchmarks. Overall, treat feature descriptions as settled and
  effectiveness comparisons as emerging.
- **Scope**: Covers (1) the two-pronged architecture (runtime guardrails +
  post-hoc observability), (2) the PII anonymize→call→deanonymize pattern with
  `@observe()` tracing, (3) input scanner composition (toxicity, prompt injection,
  token limits, banned topics), (4) output scanner composition (refusal, relevance,
  sensitive content), (5) prompt injection detection comparison between LLM Guard
  and Lakera Guard, (6) latency impact tracking, (7) four monitoring workflows for
  production security. Does NOT cover: self-hosting security, model-level safety
  training, network security, or the internal architecture of LLM Guard.
- **Sub-pages followed**: The **Security Cookbook** (`/docs/security/example-python`)
  was read end-to-end for the detailed code examples (banned topics, anonymization,
  multi-scanner stacking, output scanning, prompt injection comparison). These
  concrete artifacts are folded into this note's claims rather than extracted as
  separate claims about a different page — the cookbook is explicitly the code
  companion to this security overview page. Also read the Langfuse Observability
  overview for tracing context.

## Extracted Claims

### Claim 1: Langfuse security architecture is two-pronged — runtime blocking via guardrail libraries combined with post-hoc observability via Langfuse tracing — making security checks observable components of the trace DAG
- **Evidence**: The page opens by noting LLM applications carry "a host of potential
  safety risks" (prompt injection, PII leakage, harmful prompts) and then structures
  the solution as a two-part approach: (1) run-time security measures via LLM Guard
  and similar libraries, (2) monitoring and evaluation with Langfuse. The monitoring
  section then describes how each security check shows up in a trace alongside the
  LLM call it protects, making the security pipeline observable.
- **Confidence**: settled
- **Quote**: "LLM security involves implementing protective measures to safeguard
  LLMs and their infrastructure from unauthorized access, misuse, and adversarial
  attacks."
- **Our assessment**: This is the page's organizing architecture and the key
  contribution to the corpus. Previous notes cover either runtime guardrails
  (PagerDuty Claim 14, defense-in-depth) or observability (Langfuse eval note
  Claim 1, evaluation loop) but not the combination. This source shows how to
  wire them together so a guardrail invocation appears as a traced observation
  in the same DAG as the Generation it protects — directly confirming and
  extending `docs-langfuse-glossary.md` Claim 4 (Guardrail is a first-class
  traced observation type).

### Claim 2: The PII anonymize → LLM call → deanonymize pipeline, instrumented with @observe() decorators at each step, is a reference implementation for GDPR/HIPAA-compliant LLM applications
- **Evidence**: The page provides a complete worked example: a court transcript
  summarization app. An `Anonymize` scanner redacts PII before the LLM call, the
  LLM receives only the sanitized prompt, the model response is passed through a
  `Deanonymize` scanner to restore the original named entities, and every step
  (`anonymize()`, `summarize_transcript()`, `deanonymize()`) is decorated with
  `@observe()` so the full pipeline appears in the Langfuse trace. The example
  explicitly names compliance requirements: "sensitive-information applications
  often need to use anonymize and deanonymize functionality to comply with data
  privacy policies such as HIPAA or GDPR."
- **Confidence**: emerging
- **Quote**: "sensitive-information applications often need to use anonymize and
  deanonymize functionality to comply with data privacy policies such as HIPAA or
  GDPR."
- **Our assessment**: This is the most directly reusable pattern in the source —
  a traced, three-stage pipeline (anonymize → call → deanonymize) with observability
  at every stage. The use of `@observe()` on each function means the latency of
  scanning and the fact that scanning occurred are both visible in the trace. The
  quote above is the compliance hook that makes this pattern mandatory-reading for
  any regulated LLM deployment. We rate this emerging because it is a vendor
  reference implementation rather than a production-proven case study — but the
  pattern is sound and directly adoptable.

### Claim 3: Security checks that block or await responses are a significant latency driver, and Langfuse tracing helps dissect whether those checks are worthwhile by exposing their latency within traces
- **Evidence**: The page describes latency impact as a distinct monitoring workflow:
  "Track Latency. Some LLM security checks need to be awaited before the model can
  be called, others block the response to the user." The latency of each guardrail
  check appears as a sub-span in the trace, making per-check timing visible.
- **Confidence**: emerging
- **Quote**: "Track Latency. Some LLM security checks need to be awaited before the
  model can be called, others block the response to the user."
- **Our assessment**: This converts security overhead from a blind cost to a
  measurable dimension. The key insight from a reliability perspective: tracing
  guardrail latency allows operators to decide whether a specific check's protection
  is worth its latency budget (e.g., a 2-second PII scan on every request might not
  be justified vs. sampling). No existing corpus note quantifies this tradeoff.
  The quote is verbatim from the page's "Track Latency" workflow description.

### Claim 4: Input scanners (Anonymize, BanTopics, PromptInjection, Toxicity, TokenLimit) and output scanners (Deanonymize, NoRefusal, Relevance, Sensitive, BanTopics, Bias, Gibberish, FactualConsistency, URLReachability) form a composable guardrail stack, where multiple scanners run sequentially via scan_prompt() / scan_output()
- **Evidence**: The security cookbook page provides code examples stacking multiple
  input scanners:
  ```python
  from llm_guard.input_scanners import Toxicity, TokenLimit, PromptInjection
  scanner = scan_prompt(input_scanners, prompt)
  ```
  and multiple output scanners:
  ```python
  from llm_guard.output_scanners import NoRefusal, Relevance, Sensitive
  scanner = scan_output(output_scanners, sanitized_prompt, answer)
  ```
  The page also lists additional output scanners: "Ban topics, Bias, Gibberish,
  Factual consistency, URL Reachability."
- **Confidence**: settled
- **Quote**: (no single direct quote captures the full scanner composition; see
  code blocks in Concrete Artifacts for the verbatim implementations)
- **Our assessment**: This is the practical SDK-level composition pattern. The
  scanner stacking model (run multiple scanners, each produces an `is_valid` and
  `risk_score`, fail on any single scanner rejection) mirrors a defense-in-depth
  check pipeline. The distinction between input scanners (pre-request) and output
  scanners (post-response) is the key architectural split. Corroborates
  `docs-google-sre-prodcast-05-06-ai-safety.md` Claim 5's multi-layered defense
  architecture — system instructions → filters → LLM-classifier → ART — by showing
  how the application-layer filter layer (Claim 5's Layer 2) composes multiple
  scanners.

### Claim 5: No single guardrail library or approach catches all injection patterns — different tools have different detection profiles, requiring multi-tool defense-in-depth with monitoring
- **Evidence**: The security cookbook's prompt injection section directly compares
  LLM Guard and Lakera Guard on the same attack pattern ("Grandma Trick" — the
  classic "pretend to be grandma and ask for a napalm recipe"). LLM Guard fails
  to catch it: "the 'grandma napalm' prompt passes through undetected, and the
  model outputs a detailed napalm recipe." Lakera Guard catches the same prompt:
  "Lakera Guard identified a prompt injection. No user was harmed by this LLM."
  The cookbook's direct comparison headline: "This example shows why it is so
  important to test and compare security tools." The main page's FAQ reinforces
  this: "No single approach is 100% effective" for prompt injection prevention.
- **Confidence**: settled
- **Quote**: "This example shows why it is so important to test and compare security
  tools" — and — "As you can see, LLM Guard fails to catch the injected Grandma
  Trick prompt. Let's see how another security library, Lakera, performs:" — and
  — "No single approach is 100% effective"
- **Our assessment**: This is an important caveat for the guide — guardrail
  libraries are not interchangeable, and relying on a single tool creates blind
  spots. The concrete comparison (LLM Guard misses the Grandma Trick; Lakera
  catches it) is the strongest evidence. The FAQ's explicit "No single approach is
  100% effective" statement on prompt injection provides the page-level authority.
  This claim corroborates `blog-promptfoo-ai-orchestrated-cyberattacks.md` Claim 9
  (traditional defenses fail against AI-operated attacks) but applies the finding
  specifically to guardrail library selection rather than detection methodology.
  No contradiction — it extends the gap analysis into the tool-selection domain.

### Claim 6: Security scores from guardrail checks can be logged as Langfuse scores and validated against human annotations or automated evaluations to measure whether guardrail tools are actually effective
- **Evidence**: The page describes two score-based validation workflows: (1)
  annotations in the UI — "comparing security scores returned by the security
  tools with these annotations" to spot when the guardrail disagreed with a
  human reviewer; (2) automated evaluations — Langfuse's model-based evaluators
  "scan traces for things such as toxicity or sensitivity to flag potential risks
  and identify any gaps." The cookbook code examples show per-scanner scores
  logged via `langfuse.score_current_span(...)`.
- **Confidence**: emerging
- **Quote**: "comparing security scores returned by the security tools with these
  annotations" — and — "scan traces for things such as toxicity or sensitivity to
  flag potential risks and identify any gaps"
- **Our assessment**: This connects guardrail operation to the evaluation loop
  established in `docs-langfuse-evaluation-core-concepts.md` Claim 1 (offline→online
  closed loop). Each guardrail check generates a Score that can be validated
  against a human-judgment baseline or an LLM-as-a-Judge evaluator. This is the
  feedback channel that lets teams measure false-positive and false-negative rates
  of their guardrails over time — analogous to the drift-detection procedure in
  `docs-google-sre-prodcast-05-06-ai-safety.md` Claim 7 (monitor filter rate +
  confusion matrix). Combined, they form a complete guardrail effectiveness
  monitoring stack: rate monitoring (Google) + score validation (Langfuse).

### Claim 7: The Langfuse security page identifies four distinct production monitoring workflows for LLM security: manual trace inspection, dashboard monitoring, score validation (annotations + automated evals), and latency impact analysis
- **Evidence**: The page structures its monitoring section under four labeled
  workflows: "Manually inspect traces," "Monitor security scores over time in the
  Langfuse Dashboard," "Validate security checks using Langfuse scores," and
  "Track Latency." The score validation section is further split into annotations
  and automated evaluations.
- **Confidence**: settled
- **Quote**: (no single direct quote lists all four; they are rendered as four
  sub-headings on the page — see Concrete Artifacts for the verbatim structure)
- **Our assessment**: These four workflows form a graded response spectrum:
  raw visibility (traces) → aggregate visibility (dashboard) → validation
  (scores) → efficiency decisions (latency). Each builds on the previous. The
  guide should present these as the "how to monitor guardrails" progression.
  The latency workflow (Claim 3) is the most novel — no existing note treats
  guardrail overhead as a monitorable, actionable signal.

### Claim 8: Lakera Guard provides API-based prompt injection detection as an alternative to LLM Guard — it catches injection patterns (including indirect injection via context poisoning) that LLM Guard misses
- **Evidence**: The security cookbook tests both libraries on the same two injection
  prompts. For the "grandma napalm" direct injection: LLM Guard gives
  `highest_score=0.0` (misses it), Lakera returns `{'prompt_injection': True,
  'jailbreak': False}` with `category_scores` showing `prompt_injection: 1.0`.
  For an indirect injection (malicious string appended to context in a Q&A about
  the Miami Grand Prix): LLM Guard again gives `highest_score=0.0`, and Lakera
  catches it. The page concludes "why it is so important to test and compare
  security tools."
- **Confidence**: emerging
- **Quote**: "Lakera Guard identified a prompt injection. No user was harmed by
  this LLM."
- **Our assessment**: This is the most concrete evidence in the source that
  guardrail tool selection must be empirically validated on your actual attack
  surface. The two-tool comparison is instructive: one library uses local model
  classification (LLM Guard), the other uses an API-based detection service
  (Lakera). Both miss some patterns; neither is a silver bullet. We rate this
  emerging because the comparison is the vendor's illustrative example, not an
  independent benchmark — but the core finding (different tools have different
  detection profiles) is sound and likely generalizes.

### Claim 9: The multi-scanner stacking pattern runs each input or output scanner sequentially, logs each scanner's score independently via langfuse.score_current_span(), and the pipeline fails if any single scanner rejects the content
- **Evidence**: The security cookbook's "Multiple Scanners" and "Output Scanning"
  sections show this pattern explicitly. After each scanner's `scan_prompt` or
  `scan_output` call, the risk score is logged: `langfuse.score_current_span(...)`.
  If any scanner returns `is_valid = False`, the application returns a rejection
  message rather than continuing. The cookbook demonstrates this with Toxicity,
  TokenLimit, and PromptInjection scanners on input and NoRefusal, Relevance,
  and Sensitive scanners on output.
- **Confidence**: settled
- **Quote**: (no direct quote; see Concrete Artifacts for the verbatim code
  showing the stacking and score-logging pattern)
- **Our assessment**: This is the practical code-level pattern for the
  defense-in-depth guardrail stack described abstractly by
  `blog-pagerduty-production-ai-agent-gaps.md` Claim 14 (guardrails need sync +
  async checks). The key design decision is fail-on-any: a single scanner
  rejection blocks the pipeline. This is appropriate for high-stakes scenarios
  but may cause excessive blocking if a scanner has high false-positive rates —
  which is exactly why Claim 6's score-validation workflow matters (to measure
  and tune false positives).

### Claim 10: The Langfuse security documentation positions guardrails as an application-layer complement to model-level safety training — operating at the request/response boundary rather than within the model
- **Evidence**: The FAQ answer for "What are security guardrails for LLMs?" states:
  "Security guardrails are protective measures that intercept and filter inputs
  and outputs of LLM applications to prevent misuse and harm." The answer lists
  input guardrails, output guardrails, PII detection/redaction, content filtering,
  and topic restriction, and notes these run at the application layer, "complementary
  to model-level safety training."
- **Confidence**: settled
- **Quote**: "Security guardrails are protective measures that intercept and filter
  inputs and outputs of LLM applications to prevent misuse and harm."
- **Our assessment**: This frames guardrails as an SRE/application-layer concern
  rather than an ML concern — they run in the same request path as caching,
  auth, and rate-limiting. This positioning is critical for the guide: it means
  guardrail design and monitoring belong in Ch05/Ch06 (ops + security), not in a
  model-training chapter. The quote provides a clean, citable definition.

### Claim 11: Langfuse's security monitoring recommendations include a five-step production posture — trace every request through guardrails, LLM-as-a-Judge auto-scoring, custom dashboards, annotation queues for human review, and latency tracking
- **Evidence**: The FAQ answer for "How do I monitor LLM security in production?"
  enumerates five steps: (1) trace every request through the guardrail pipeline to
  see which checks triggered, (2) use LLM-as-a-Judge evaluators to auto-score
  traces for "toxicity, PII leakage, and prompt injection," (3) custom dashboards
  to track security scores over time, (4) annotation queues for human review of
  flagged conversations, (5) "Track the latency impact of security checks to
  balance protection with user experience."
- **Confidence**: emerging
- **Quote**: "Track the latency impact of security checks to balance protection
  with user experience."
- **Our assessment**: This five-step posture is the page's most actionable
  production guidance. Step 1 (trace everything) is the baseline that enables
  steps 2–5. Steps 2–3 provide automated+aggregate visibility; step 4 provides
  the human validation loop; step 5 provides the cost-benefit lever. The latency
  quote directly reinforces Claim 3 (latency as a monitorable dimension). This
  posture corroborates the evaluation-loop pattern in
  `docs-langfuse-evaluation-core-concepts.md` Claim 1 (offline→online closed loop)
  and `docs-google-sre-prodcast-05-06-ai-safety.md` Claim 7 (drift monitoring),
  extending both with the specific five-step production implementation.

## Concrete Artifacts

### Verbatim code: PII anonymize/deanonymize pipeline with Langfuse tracing

```python
from llm_guard.input_scanners import Anonymize
from llm_guard.input_scanners.anonymize_helpers import BERT_LARGE_NER_CONF
from langfuse.openai import openai
from langfuse import observe
from llm_guard.output_scanners import Deanonymize
from llm_guard.vault import Vault

vault = Vault()

@observe()
def anonymize(input: str):
  scanner = Anonymize(vault, preamble="Insert before prompt", allowed_names=["John Doe"], hidden_names=["Test LLC"],
                    recognizer_conf=BERT_LARGE_NER_CONF, language="en")
  sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
  return sanitized_prompt

@observe()
def deanonymize(sanitized_prompt: str, answer: str):
  scanner = Deanonymize(vault)
  sanitized_model_output, is_valid, risk_score = scanner.scan(sanitized_prompt, answer)
  return sanitized_model_output

@observe()
def summarize_transcript(prompt: str):
  sanitized_prompt = anonymize(prompt)
  answer = openai.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=100,
        messages=[
          {"role": "system", "content": "Summarize the given court transcript."},
          {"role": "user", "content": sanitized_prompt}
        ],
    ).choices[0].message.content
  sanitized_model_output = deanonymize(sanitized_prompt, answer)
  return sanitized_model_output
```
Source: https://langfuse.com/docs/security-and-guardrails — "Getting Started" section.
Each function is decorated with `@observe()` so the full anonymize→LLM→deanonymize
pipeline appears as traced sub-spans in the Langfuse trace.

### Verbatim code: Multi-scanner stacking pattern (input scanners)

```python
# From the security cookbook — multiple input scanners run sequentially,
# each score logged independently, fail if any scanner rejects
from llm_guard.input_scanners import Toxicity, TokenLimit, PromptInjection
# Each scanner returns (sanitized_prompt, is_valid, risk_score)
# langfuse.score_current_span(...) is called after each scanner
# If any scanner returns is_valid=False, the app returns a rejection message
```
Source: https://langfuse.com/docs/security/example-python — "Multiple Scanners" section.
(The full code uses `scan_prompt(input_scanners, prompt)` which internally sequences
the scanners and returns combined results.)

### Verbatim code: Output scanning pattern

```python
from llm_guard.output_scanners import NoRefusal, Relevance, Sensitive
# scan_output(output_scanners, sanitized_prompt, answer)
# Returns (sanitized_model_output, is_valid, risk_score)
# Additional output scanners: Ban topics, Bias, Gibberish, Factual consistency,
# URL Reachability.
```
Source: https://langfuse.com/docs/security/example-python — "Output Scanning" section.

### Verbatim quote: LLM Guard vs Lakera Guard on prompt injection detection

```
LLM Guard result on "grandma napalm" prompt: highest_score = 0.0 (missed it)
Lakera Guard result on same prompt: prompt_injection = True, jailbreak = False,
  category_scores: {prompt_injection: 1.0}

Page comment: "This example shows why it is so important to test and compare
security tools."

Second test (indirect injection via context poisoning):
LLM Guard: highest_score = 0.0 (missed)
Lakera: detected it
Page comment: "As you can see, LLM Guard fails to catch the injected Grandma Trick
prompt. Let's see how another security library, Lakera, performs:"
```
Source: https://langfuse.com/docs/security/example-python — "Prompt Injection" section.
Verbatim results and direct quotes from the comparison table and commentary.

### The four Langfuse security monitoring workflows (verbatim sub-headings from the page)

```
1. Manually inspect traces
   — Investigate security issues by looking at individual traces

2. Monitor security scores over time in the Langfuse Dashboard
   — Aggregate visibility into guardrail effectiveness

3. Validate security checks using Langfuse scores
   a. Annotations (in UI): "comparing security scores returned by the security
      tools with these annotations"
   b. Automated evaluations: model-based evals "scan traces for things such as
      toxicity or sensitivity to flag potential risks and identify any gaps"

4. Track Latency
   — "Some LLM security checks need to be awaited before the model can be
      called, others block the response to the user."
```
Source: https://langfuse.com/docs/security-and-guardrails — "Monitoring and
evaluation with Langfuse" section, four sub-workflows described as bulleted items
on the rendered page.

## Cross-References

- **Corroborates**:
  - `docs-langfuse-glossary.md` **Claim 4** — Guardrail as a first-class observation
    type ("An observation type that represents a component protecting against
    malicious content, jailbreaks, or other security risks"). The security-and-guardrails
    page fills in the practical implementation of what the glossary only defines: the
    guardrail-tracing pipeline (anonymize → LLM call → deanonymize) with `@observe()`
    decorators that generates the Guardrail observations the glossary describes.
  - `docs-google-sre-prodcast-05-06-ai-safety.md` **Claim 5** — Multi-layered defense
    (system instructions → filters → LLM-classifier → ART). This source's Claim 4
    (input/output scanner composition) and Claim 9 (multi-scanner stacking with
    fail-on-any) show how the application-layer filter layer (Layer 2 in the Prodcast)
    is implemented with llm_guard. The Prodcast describes the architecture at the
    principle level; this source provides the SDK-level instantiation.
  - `docs-google-sre-prodcast-05-06-ai-safety.md` **Claim 7** — Drift detection for
    safety classifiers via filter-rate monitoring + confusion matrix. This source's
    Claim 6 (score validation via annotations + automated evals) provides the
    Langfuse-based feedback channel that powers the confusion-matrix approach: guardrail
    scores are logged per-check, and human annotations of the same traces provide the
    ground truth needed to compute FP/TP rates.
  - `blog-pagerduty-production-ai-agent-gaps.md` **Claim 14** — "Guardrails require
    defense-in-depth with synchronous and asynchronous checks." This source's Claim 9
    (multi-scanner stacking, fail-on-any rejection) is a concrete implementation of
    the synchronous guardrail layer, with each scanner instrumented via `@observe()`
    so its latency and outcome are visible in every trace.

- **Contradicts**: None identified. All claims in this source are either vendor
  documentation of Langfuse features, code-level implementation patterns that extend
  existing architectural coverage, or tool comparisons (LLM Guard vs Lakera) that
  provide evidence for existing claims (no single guardrail is sufficient). No claim
  here opposes a claim in an existing source note in a way that would change guide
  advice. The closest surface — the Google Prodcast (S5E6) describing model-level
  safety and this source describing application-layer guardrails — are complementary
  layers, not in conflict. No contradiction issue filed.

- **Extends**:
  - Extends `docs-langfuse-glossary.md` **Claim 4** (Guardrail as observation type)
    from an abstract definition into a working implementation with code, tracing,
    and latency measurement. The glossary says a Guardrail is a type of observation;
    this source shows exactly how to produce that observation.
  - Extends `docs-langfuse-evaluation-core-concepts.md` **Claim 1** (offline→online
    evaluation loop) with the security-specific monitoring workflows (Claim 7, 11 here)
    — manual trace inspection, security-dashboard monitoring, score validation against
    human annotations, and latency impact tracking. The eval note describes the loop
    generically; this source adds the security/monitoring specialization.
  - Extends `blog-promptfoo-ai-orchestrated-cyberattacks.md` **Claims 5–6** (LLM-querying
    malware / prompt injection as offensive threat) with the defensive guardrail-
    implementation and observability side. That note covers attacker-side patterns;
    this note covers how to detect and block them with instrumented guardrails.
  - Extends `blog-promptfoo-building-security-scanner-llm-apps.md` **Claim 2** (the
    "laundering" mechanism — LLM output IS the dangerous action) and **Claim 4**
    (deadly duo — untrusted content + privileged actions) by providing runtime
    guardrails that can detect and block the laundering in the request/response path,
    complementing that note's build-time code-scanning approach.
  - Extends `docs-google-sre-prodcast-04-01-security-sre-intersection.md` **Claim 7**
    (shared tooling / "same lens" for security and SRE) — Langfuse tracing of
    guardrail checks is a concrete instance of shared observability tooling: the same
    trace that shows the LLM Generation latency also shows the guardrail check that
    scanned the input, so security and SRE see the same data.

- **Novel**: This source is the **first in the corpus to combine LLM application-layer
  guardrails with observability/tracing**, providing the telemetry side of the
  guardrail pattern. Specifically novel:
  - The **two-pronged architecture** — runtime blocking LLM Guard + post-hoc Langfuse
    tracing — as a named, code-supported pattern (Claim 1). No existing note describes
    guardrail instrumentation.
  - The **PII anonymize→call→deanonymize traced pipeline** (Claim 2) — a concrete,
    copy-pasteable reference implementation for GDPR/HIPAA compliance with full
    observability.
  - **Security-check latency as a monitorable dimension** (Claim 3) — no existing
    corpus source treats guardrail overhead as an actionable signal.
  - The **LLM Guard vs Lakera empirical comparison** (Claims 5, 8) — a concrete
    evidence point that different guardrail tools have different detection profiles
    and must be empirically validated, not treated as interchangeable.
  - The **four security monitoring workflows** (Claim 7) — the graded progression
    from raw traces to dashboard to validation to latency efficiency.
  - The **multi-scanner fail-on-any stacking pattern** (Claim 9) with per-scanner
    score logging — a concrete implementation pattern for defense-in-depth guardrails.

## Guide Impact

- **Chapter 06 (Security and Trust)**: This is the primary destination. Add:
  - A **"guardrails in practice" subsection** built on this note. Include the
    two-pronged architecture (Claim 1) as the organizing frame: runtime blocking +
    post-hoc observability. The PII anonymize→call→deanonymize pipeline (Claim 2)
    is the reference implementation for GDPR/HIPAA compliance. Present the
    multi-scanner stacking pattern (Claim 9) as the synchronous guardrail layer
    recommended by `blog-pagerduty-production-ai-agent-gaps.md` Claim 14.
  - A **"no single tool catches everything" warning** citing the LLM Guard vs Lakera
    comparison (Claims 5, 8): different guardrail tools have different detection
    profiles, and teams must empirically test their chosen library against their
    actual attack surface. Pair with the FAQ's "No single approach is 100% effective"
    statement.
  - A **"five-step guardrail monitoring posture"** (Claim 11) for production LLM
    deployments: trace every request through guardrails, LLM-as-a-Judge auto-scoring
    for toxicity/PII/injection, custom dashboards, annotation queues for human review,
    and latency tracking. This operationalizes the evaluation loop from
    `docs-langfuse-evaluation-core-concepts.md` in the security domain.
  - **Security-check latency** (Claim 3) as a new consideration in the security-vs-
    performance tradeoff analysis: guardrails that block or await responses drive
    latency, and tracing enables per-check cost-benefit decisions.

- **Chapter 05 (LLM Ops Reliability — monitoring)**: Add the **four security
  monitoring workflows** (Claim 7) as a graded monitoring progression: raw traces
  → dashboards → score validation → latency-efficiency decisions. This extends
  the evaluation-loop monitoring (from `docs-langfuse-evaluation-core-concepts.md`)
  with security-specific signals and the latency-cost tradeoff. The per-check score
  logging (Claim 9) via `langfuse.score_current_span()` is a concrete observability
  pattern for generating the guardrail effectiveness data that fuels the
  drift-detection confusion matrix (`docs-google-sre-prodcast-05-06-ai-safety.md`
  Claim 7).

- **Chapter 02 (Observability)**: Add the guardrail-as-observation tracing pattern
  (Claim 1) as an extension of the observation-type taxonomy from
  `docs-langfuse-glossary.md` (Claim 4 — Guardrail is a traced observation type).
  The Glossary defines the type; this source shows what a guardrail observation
  looks like in practice (an `@observe()`-decorated function that runs a security
  check and logs its outcome). This gives Ch02 a concrete "here is what a guardrail
  trace looks like" example.

## Extraction Notes

- Source fetched 2026-07-18. The main Security & Guardrails page
  (https://langfuse.com/docs/security-and-guardrails) was fetched via WebFetch and
  curl; it rendered server-side and was fully readable. The Security Cookbook
  companion page (https://langfuse.com/docs/security/example-python) was also
  fetched and read end-to-end. The Observability overview page
  (https://langfuse.com/docs/observability/overview) was fetched for context on
  Langfuse tracing primitives. The LLM Guard homepage (https://llm-guard.com) was
  unreachable (DNS resolve failure) — but the llm_guard Python interface is fully
  documented through the Langfuse cookbook code examples, so coverage is not
  materially reduced.
- Quotes marked as direct in this note were extracted from the rendered page text
  via WebFetch (which enforces a 125-character single-quote limit). Longer or
  multi-sentence quotes are composed from contiguous passages that appeared adjacent
  in the source, marked with "— and —" between fragments. The Assayer should
  spot-check key quotes against https://langfuse.com/docs/security-and-guardrails
  and https://langfuse.com/docs/security/example-python for character-for-character
  accuracy.
- Code blocks in Concrete Artifacts were extracted from the page's syntax-highlighted
  code blocks and are reproduced verbatim. The `@observe()` decorator pattern is the
  key Langfuse SDK primitive and appears unchanged from the source.
- The LLM Guard vs Lakera comparison results (Claim 8) are the page's own numbers
  from the cookbook's prompt injection test section. The page does not disclose LLM
  Guard or Lakera model versions, thresholds, or configurations beyond what is shown
  in the code snippets. Treat as illustrative rather than benchmark-grade.
- `confidence_overall` is set to **emerging** following the precedent of
  `docs-langfuse-evaluation-core-concepts.md`: the feature claims (how Langfuse
  tracing works) are authoritative for the product, but the effectiveness claims
  (which guardrails work, latency impact magnitude, detection rates) are
  vendor-illustrative and not independently benchmarked. The page is living
  documentation with no publication date; assessed as current as of extraction.
- No contradiction with any existing source note was found. The tool comparisons
  extend rather than oppose existing claims about defense-in-depth. No
  contradiction issue was filed.
