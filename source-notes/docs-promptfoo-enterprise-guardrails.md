---
source_url: https://www.promptfoo.dev/docs/enterprise/guardrails
source_type: docs
title: "Promptfoo Enterprise: Adaptive Guardrails — The Runtime Enforcement Contract, the Parallel-Execution Cost Asymmetry, and the Stale-Policy Failure Modes"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-07
date_extracted: 2026-10-07
last_checked: 2026-10-07
status: current
confidence_overall: emerging
issue: "#1611"
---

# Promptfoo Enterprise: Adaptive Guardrails

> The vendor's runtime *enforcement* contract for promptfoo's eval-platform
> guardrails — `POST /api/v1/guardrails/{targetId}/evaluate` with four
> placements and a five-value aggregate `action` the caller must gate on
> explicitly ("do not let either fall through by accident" for `warn`/`error`),
> plus the operational tradeoffs hiding inside it: concurrent execution buys
> zero latency for benign traffic while adversarial prompts still pay full LLM
> cost, regex fast filters short-circuit before the LLM policy stage, and
> policies are cache-stale by default until forced regeneration — with
> first-party documentation of *no* failure-semantics knobs and *no*
> measurement anywhere on the page.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo Enterprise
  "Enterprise > Guardrails" / Adaptive Guardrails page). Page header carries
  the gating notice "This feature requires Promptfoo Enterprise." Page footer:
  "Last updated on **Oct 7, 2026** by **mldangelo-oai**".
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of its own Enterprise runtime product, so
  authoritative *as a specification* — endpoint path, env-var names, enum
  members, example thresholds, stage caps, and batch sizes below are the
  vendor's own contract and are string-checkable by anyone with an Enterprise
  tenant. It is not measurement: the page publishes no latency, false-positive,
  block-rate, volume, or cost figure anywhere, and nothing here is verifiable
  against the open-source repository (the product is Enterprise-gated). The
  prose efficacy claims ("close the loop", "living defense layer") are
  marketing-adjacent framing, not evidence.
- **Scope**: Covers what Adaptive Guardrails are, the red-team→policy→production
  feedback loop, manual vs automated policy management, creation/generation/
  testing UI, the integrate snippet (endpoint, auth, placements, aggregate
  action, response fields), the parallel-execution placement tradeoff,
  analytics surfaces, tool-call policies, four Technical Specifications tables
  (input-example limits, LLM prompt limits, scaling behavior, policy
  constraints), three troubleshooting playbooks, and an eleven-question FAQ.
  Does **not** cover the eval-time `guardrails` assertion (separate page, own
  note), failure semantics of the evaluate endpoint when the guardrail service
  itself is unreachable or erroring, auth/permission model beyond a Bearer
  token and one regeneration-permission mention, retention of
  `guardrailResults`, any measured efficacy or latency, or the third-party
  guardrail integrations it only names.
- **Relationship to sibling pages**: the page itself draws the plane line —
  a note callout separates this runtime enforcement product from the
  eval-side `guardrails` assertion the corpus already covers, and the linked
  guardrail testing guide's feature table does the same ("Enterprise Adaptive
  Guardrails | How do I enforce Promptfoo-hosted policies at runtime?"). This
  is promptfoo's *second* guardrail surface in the corpus and its first
  runtime one.

## Extracted Claims

### Claim 1: The runtime enforcement contract is a caller-integrated HTTP endpoint — `POST {baseUrl}/api/v1/guardrails/{targetId}/evaluate` carrying a `placement` enum, Bearer auth via `PROMPTFOO_API_KEY`, and required `PROMPTFOO_TARGET_ID`, with four placements defaulting to `INPUT` + `OUTPUT`
- **Evidence**: The "Integrate the Guardrail" section's worked `fetch` example
  (endpoint path, env vars, `identityContext` body field — reproduced in
  Concrete Artifacts) and the FAQ's placement answer. The page's own note callout
  states the plane.
- **Confidence**: settled (documented contract; endpoint, enum members, and env
  var names are string-checkable)
- **Quote**: "No. Adaptive guardrails support four placement types: `INPUT`,
  `OUTPUT`, `TOOL_CALL_INPUT`, and `TOOL_CALL_OUTPUT`. By default, guardrails
  are applied to both `INPUT` and `OUTPUT`. You can configure tool call
  placements for additional coverage."
- **Quote**: "This page describes Promptfoo Enterprise's runtime enforcement
  product. To test a target's provider-reported safety decision in an eval, see
  the `guardrails` assertion and guardrail testing guide."
- **Our assessment**: The most important structural fact on the page, in the
  vendor's own voice: promptfoo ships *two* guardrail artifacts, and this is
  the one that actually blocks production traffic. The corpus's existing
  promptfoo guardrail note (`docs-promptfoo-guardrails-assertions.md` Claim 1)
  establishes the eval-side assertion "does not run a guardrail"; this page is
  the runner, with the integrating client as the enforcement point. Note the
  deployment consequence: unlike a gateway-attached guardrail (LiteLLM's model),
  this endpoint's placement in the request path, its timeout behavior, and its
  failure handling are all the *caller's* code — the vendor supplies the
  decision endpoint and an example gate, nothing more (Claim 13).

### Claim 2: The gate contract is a five-value aggregate `action` — `allow`, `log`, `warn`, `block`, `error` — and the vendor explicitly warns that `warn` and `error` need caller-defined handling or they fall through, a documented fail-open trap at the integration layer
- **Evidence**: The sentence immediately following the integrate snippet.
- **Confidence**: settled (explicit vendor guidance with a named failure mode)
- **Quote**: "Gate the model call on the aggregate `action`: `allow`, `log`,
  `warn`, `block`, or `error`. Choose an explicit policy for `warn` and `error`;
  do not let either fall through by accident."
- **Our assessment**: The load-bearing operational claim for Ch05/Ch06. The
  vendor ships a *five*-value verdict space but only `block` is self-evidently
  terminal — `warn` (scored below the block dial) and `error` (evaluation
  failed) both default to "you decide," and a caller that only writes
  `if (action === 'block')` silently fails open on exactly the states where the
  guardrail was uncertain or broken. This is the runtime, caller-side sibling of
  the eval-side fail-open family the corpus already tracks
  (`docs-promptfoo-guardrails-assertions.md` Claim 3: missing signal passes with
  score 1) — different layer, same "gate reports green while not enforcing"
  shape. The example snippet models the *conservative* choice (gates on
  `block` **or** `error`), which is the pattern to publish. Note also that
  `log` and `allow` are behaviorally identical at the gate (both proceed); the
  value of `log` is audit, not routing.

### Claim 3: The response is an audit-grade object, not a boolean — aggregate `action` plus `severity`, `guardrailResults`, `latencyMs`, optional `sanitizedContent`, with vendor guidance to retain per-guardrail results instead of collapsing them
- **Evidence**: The same integrate paragraph, which enumerates the response
  fields and the retention instruction.
- **Confidence**: settled (documented response shape)
- **Quote**: "The endpoint evaluates every active guardrail attached to the
  target ID and also returns `severity`, `guardrailResults`, and `latencyMs`.
  A transforming policy can return `sanitizedContent`. Keep the per-guardrail
  results for audit and debugging instead of reducing the response to a
  boolean."
- **Our assessment**: Two things worth carrying. First, `latencyMs` per
  evaluation is the only latency number this product documents anywhere, and it
  is per-request telemetry the caller must persist itself — there is no
  documented aggregation, dashboard, or export for it (the Guardrails >
  Dashboard tracks targets, not guardrail latency). Second, the explicit
  "instead of reducing the response to a boolean" instruction is the vendor
  agreeing with the corpus's observability rule: `guardrailResults` is what a
  post-incident review reads to answer "which guardrail fired and why," and the
  sibling audit-logging note (`docs-promptfoo-enterprise-audit-logging.md`
  Claim 2) establishes that control-plane audit logging does **not** cover
  data-plane request events — so `guardrailResults` retention is the caller's
  job or it does not exist. `sanitizedContent` also makes this endpoint a
  *transforming* control (a block that rewrites), the same dual role LiteLLM's
  generic guardrail API gives `GUARDRAIL_INTERVENED`
  (`docs-litellm-generic-guardrail-api.md` Claim 3).

### Claim 4: Placement of the guardrail relative to the model call is an explicit latency-vs-cost tradeoff — concurrent execution gives benign traffic "zero added latency" but still incurs the LLM call for adversarial prompts that are ultimately blocked
- **Evidence**: The "Parallel Execution" section, both paragraphs.
- **Confidence**: settled (documented tradeoff; no measured magnitudes given)
- **Quote**: "But if you want to minimize your Time to First Token (TTFT), you
  could run the query to your model, as well as the guardrail at the same time."
- **Quote**: "This approach prioritizes UX by ensuring non-malicious queries
  see zero added latency. However, it incurs the cost of the LLM call even for
  adversarial prompts that are ultimately blocked."
- **Our assessment**: The cost/latency asymmetry the Prospector flagged, and
  the cleanest statement of it in any corpus source: the concurrent pattern
  optimizes *latency* only, and the party who attacks you pays the bill with
  *your* provider budget — the guardrail saves spend only when it runs before
  the model (the sequential pattern, which taxes every benign request's TTFT
  instead). Neither mode dominates; the choice is which resource (user
  latency vs adversarial-token spend) the traffic profile makes scarcer, and
  the guide should present it as a two-axis dial rather than "run guardrails
  concurrently." The page gives no numbers for either axis (no TTFT delta, no
  blocked-prompt token share), so this stays a qualitative tradeoff. The
  sibling Langfuse note's Claim 3 ("Some LLM security checks need to be
  awaited before the model can be called, others block the response to the
  user") frames the same choice as traceable latency — this page supplies the
  other half: what the concurrent choice costs.

### Claim 5: Enforcement runs as two ordered planes — regex fast filters first, short-circuiting "without calling the LLM," then LLM-based policy evaluation — each with its own false-positive and latency profile
- **Evidence**: The FAQ ordering answer, plus the "Generate Guardrail" section's
  fast-filter guidance.
- **Confidence**: settled (documented evaluation order)
- **Quote**: "Fast filters (regex rules) run first as a pre-filter. If a fast
  filter triggers, the request is handled immediately without calling the LLM.
  If no fast filter matches, the request proceeds to LLM-based policy
  evaluation."
- **Quote**: "Fast filters is a great place to start, since this will be the
  first filter that is run on your prompts. Here you can set regular expressions
  that will check for sensitive text such as credit card numbers, addresses, and
  SSNs."
- **Our assessment**: A second enforcement plane with independent failure
  modes, invisible in the aggregate `action`: a regex fast filter that
  over-matches blocks (or warns) with *zero* LLM involvement, so its
  false-positives cannot be explained by policy severity tuning, and its
  latency contribution is regex-only — while everything reaching the LLM stage
  pays model latency on every request that got past the filters. Operationally
  this matters for the "High false positive rate" playbook: step 1 is "review
  automated policies," but fast filters are configured separately (the page
  recommends them as the starting point), so a PII-regex false positive would
  not be found in the policies list at all. The ordering also means fast
  filters are the cheapest place to put deterministic detections (card numbers,
  SSNs) — a mini version of the corpus's regex-before-LLM cost rule.

### Claim 6: The adaptive loop is structurally bounded to known-vulnerability similarity — the guardrail "can only block patterns similar to known vulnerabilities," and entirely new attack types require new red-team testing to be detected
- **Evidence**: The FAQ new-attack answer and troubleshooting item 1.
- **Confidence**: settled (documented capability boundary, stated twice)
- **Quote**: "It blocks patterns similar to discovered vulnerabilities.
  Entirely new attack types require additional red team testing to be detected.
  This is why the feedback loop between testing and guardrail generation is
  important."
- **Quote**: "Guardrails can only block patterns similar to known vulnerabilities."
- **Our assessment**: The honest limit of a findings-derived guardrail, stated
  by the vendor in its own troubleshooting path. It converts "adaptive" from a
  promise into a coverage claim: the guardrail's effective rule set is a
  function of the red-team corpus you have run, so a target that has never been
  scanned for an attack class has no automated defense against that class
  (manual policies and fast filters are the only ex-ante coverage). For the
  guide this is the counterweight to the feedback-loop framing — schedule
  red-team cycles as *coverage expansion* for the runtime control, not just as
  eval hygiene, and never present the guardrail as signatureless protection.
  It also corroborates the corpus's recurring "defense lags the newest
  technique" theme (cf. `blog-promptfoo-owasp-red-teaming.md` Claim 4's
  recurring-schedule rationale).

### Claim 7: Policies are cache-stale by default and silently consolidated — cached guardrails are returned unless regeneration is forced, and semantically overlapping policies are LLM-merged during generation, so a specific rule can be folded into a broader one and stop firing
- **Evidence**: The "Policies not updating after new red team tests"
  troubleshooting playbook (items 1 and 4), the "Guardrail not blocking expected
  patterns" item 4, the Policies constraint table ("Policy consolidation |
  LLM-enforced deduplication | Redundant policies are merged automatically"),
  and the FAQ on deleted automated policies.
- **Confidence**: settled (documented default behavior and troubleshooting)
- **Quote**: "Cached guardrails are returned by default — you must explicitly
  regenerate to incorporate new findings."
- **Quote**: "During generation, semantically overlapping policies are merged.
  Review your policies to ensure the relevant rule wasn't folded into a broader
  one."
- **Quote**: "The deleted policies will not reappear until you explicitly
  regenerate."
- **Our assessment**: Two distinct staleness modes the guide should carry as
  operational rules. (1) *Cache staleness*: after a new red-team scan, the
  guardrail does not update itself — "regeneration is triggered manually"
  (Claim 10) and the default read path serves the cached object, so the
  detection→enforcement loop has an unbounded, operator-controlled lag. A
  missing block after a scan is a *staleness* check first, a policy problem
  second (the playbook's item ordering says exactly this). (2)
  *Consolidation loss*: deduplication is LLM-enforced and runs during
  generation, so the act of refreshing the guardrail can also *weaken* it — a
  narrow rule merged into a broader one is a documented cause of newly
  missing blocks, and the fix ("review your policies") is manual diffing with
  no documented change log or before/after export. The deletion answer adds a
  third wrinkle: deleting an automated policy is not durable across the next
  regeneration (it reappears), while manual policies are (Claim 10) — so the
  durable way to carve out an exception is a manual policy, not a deletion.

### Claim 8: Runtime validation sends zero examples — policy text only, "keeping latency low" — while generation and testing stages run under published caps (>20 examples switches to map-reduce at batch size 25), a deliberate latency-vs-context tradeoff at the enforcement plane
- **Evidence**: The LLM Prompt Limits table (Runtime validation row), Input
  Example Limits table, and Scaling Behavior table — all reproduced verbatim in
  Concrete Artifacts.
- **Confidence**: settled (documented stage caps; the "keeps latency low"
  rationale is the vendor's own stated intent, not a measurement)
- **Quote**: "Only policy text is sent — no raw examples, keeping latency low"
- **Our assessment**: The one place the page explains a latency decision: the
  online path (runtime validation of a request against the policy) is
  deliberately context-free — 0 examples, policy text only — while all the
  example-heavy context (500 per vulnerability for policy generation, 5 in the
  generation prompt, 3 known-violation few-shots in the system prompt) is paid
  offline at generation time. That split is the correct shape for an
  enforcement control and worth stating in the guide: *put the context in the
  policy authoring pipeline, not in the request path.* The downside is
  inherited from authoring: with no examples at validation time, the runtime
  judge's pattern-matching rests entirely on how well the offline pipeline
  condensed the corpus — and the offline pipeline itself has caps (500/300/50/
  20/10 examples by stage) plus the >20-example map-reduce threshold where
  "policies are consolidated," i.e. the same consolidation that can drop rules
  (Claim 7) sits directly downstream of the largest caps.

### Claim 9: Tool-call placements are manual-only — `TOOL_CALL_INPUT` / `TOOL_CALL_OUTPUT` policies "aren't automatically generated from your red team scans" — even though the stated use case (PII filters stopping argument exfiltration to third-party APIs) is exactly what automated coverage would want
- **Evidence**: The "Tool Calls" advanced-configuration section.
- **Confidence**: settled (documented capability gap and manual workflow)
- **Quote**: "Tool call guardrails aren't automatically generated from your red
  team scans, but they can manually be added to your list of policies."
- **Quote**: "Tool call guardrails allow you to validate structured arguments
  before they reach external functions. For example, applying a PII filter to
  `TOOL_CALL_INPUT` prevents sensitive user data from being exfiltrated to
  3rd-party APIs or logged in external systems."
- **Our assessment**: The feedback loop that makes the guardrail "adaptive"
  covers input/output text only; the tool-call surface — the one the page itself
  motivates with third-party exfiltration and argument validation — is
  hand-written policy forever (until/unless the vendor extends generation).
  That is the same coverage-vs-interception gap the corpus recorded for LiteLLM
  (`docs-litellm-generic-guardrail-api.md` Claim 5: universal interception,
  three-endpoint tool enforcement), from the opposite direction: there, tool
  enforcement existed but was endpoint-scoped; here, tool enforcement exists
  across a placement enum but is scan-unreachable. The mechanism itself is
  genuinely useful and pairs with the guide's function-calling authorization
  section: validating structured arguments *before* they reach external
  functions is the runtime counterpart to `bfla`/`bola` probes, and the default
  integration advice ("we suggest just setting up input and output calls, and
  integrating tool call input/output calls later") means most first
  deployments have no tool-call coverage at all.

### Claim 10: The policy lifecycle is two-tiered — automated policies are generated from red-team failures and replaced on regeneration, manual policies are never removed, and there is no required regeneration schedule (recommended: after each red-team cycle)
- **Evidence**: The Policy Management bullets, the FAQ regeneration-cadence
  answer, and the Policies constraint table row "Manual policies on
  regeneration | Preserved".
- **Confidence**: settled (documented lifecycle semantics)
- **Quote**: "Manual Policies: Added by you, never removed during regeneration."
- **Quote**: "Regenerate after each red team testing cycle that discovers new
  vulnerabilities. There is no required schedule — regeneration is triggered
  manually when you're ready to incorporate new findings. Manual policies are
  always preserved during regeneration."
- **Our assessment**: The lifecycle is the design center of the product and
  also where its operational burden lands: automated rules track the scan
  corpus, manual business logic persists, and *the human decides when the two
  are reconciled* — with no schedule, no "new findings pending" indicator
  documented, and no diff on regeneration. The safety property (manual policies
  never silently deleted) is good; the hazard is the mirror image of Claim 7:
  manual policies also never age out, so stale hand-written rules accumulate
  alongside evolving automated ones with no documented review artifact. The
  cadence guidance ("after each red team testing cycle") plus the recurring
  red-team discipline in `blog-promptfoo-owasp-red-teaming.md` Claim 4
  compose into a concrete loop: scheduled scans → manual regeneration →
  policy review — with the middle step currently undocumented-automatable.

### Claim 11: Severity is a 0.0–1.0 score mapped to per-action threshold dials — the worked example blocks nothing at severity 0.30 until the `block` dial is lowered to 0.7 — so tuning is threshold adjustment against observed prompts, not policy rewriting
- **Evidence**: The "Testing the Guardrail" section's worked example and the
  "High false positive rate" playbook item 3 ("Adjust your action thresholds").
- **Confidence**: settled (documented scoring scale and tuning mechanism; the
  0.30 / 0.7 values are example settings, not defaults)
- **Quote**: "As you can see, this prompt gets a severity of only 0.30 (on a
  0.0-1.0 scale). This means that some level of hate speech is being detected,
  but it isn't enough for blocking the prompt or returning a warning."
- **Quote**: "Try setting the block dial down to 0.7 and see if there are things
  that now get blocked that weren't earlier. The best way to find the right
  setting is to experiment with different prompts on the Test Guardrail menu."
- **Our assessment**: The action taxonomy (Claim 2) is driven by score
  thresholds, which makes the guardrail's strictness a continuous knob with a
  discrete readout — a detection at 0.30 produces `log`/`allow`-class behavior
  until the dial moves. The vendor's tuning method is explicitly
  prompt-experimentation on a test page: no documented precision/recall curve,
  no suggested operating point, no per-policy threshold (dials are per
  guardrail). For the guide, this is the false-positive/false-negative tradeoff
  made literal and *unmeasured* — every deployment re-derives its operating
  point by hand, which is also why the analytics advice matters: "reviewing
  some requests in each range (e.g., block, warn, log) to ensure that they all
  are labeled as expected" is the only documented calibration loop, and it is
  manual sampling. Pairs with Claim 2: `warn` is a *tunable* state, which is
  precisely why its fall-through behavior needs an explicit caller policy.

### Claim 12: Adaptive guardrails sit alongside four third-party guardrail types chosen at creation — OpenAI Moderation, Microsoft Presidio, Azure AI Content Safety, and AWS Bedrock Guardrails — but the page documents no adapter behavior, config, or semantics for any of them
- **Evidence**: The FAQ third-party answer and the "Generate Guardrail" menu
  description ("choose between adaptive guardrails, along with third-party
  guardrails that do not adapt to your red team scans").
- **Confidence**: settled (the enumeration is explicit; everything beyond the
  names is undocumented on this page)
- **Quote**: "Yes. In addition to adaptive guardrails, Promptfoo supports OpenAI
  Moderation, Microsoft Presidio, Azure AI Content Safety, and AWS Bedrock
  Guardrails. You can select the guardrail type during creation."
- **Our assessment**: The multi-vendor guardrail picture the Prospector wanted,
  at name-level only: promptfoo positions itself as the *orchestrator* plane
  where a target picks one of four provider guardrails or the adaptive one —
  useful for the guide's vendor matrix (each of these four is also a
  first-class integration elsewhere in the corpus: Bedrock Guardrails in the
  LiteLLM notes, Presidio in `docs-litellm-apply-guardrail-endpoint.md` Claim 7,
  Azure/OpenAI in the assertion note's provider matrix), but the page documents
  how none of them map onto the five-value `action` enum, how their detections
  surface in `guardrailResults`, or whether the third-party ones also score
  severity. Treat as a capability list; the interop semantics are unknown rather
  than absent.

### Claim 13: The page documents no failure semantics for the evaluate call itself and no measurement of any kind — no unreachable/error knobs, no timeout behavior, no status codes; the only failure handling shown is in the caller's example code (throw on non-2xx, gate on `block` || `error`)
- **Evidence**: Full-page scan of the fetched page (2026-10-07): zero HTTP
  status codes, zero mentions of timeout/retry/unreachable/fail-open/fail-closed
  for the evaluate endpoint, zero latency/FP-rate/volume/cost figures; the
  integrate snippet's `if (!response.ok) { throw ... }` and
  `if (result.action === 'block' || result.action === 'error')` are the entire
  documented failure handling, and both live in caller-owned code.
- **Confidence**: emerging (the absence is verified against this page; the
  linked API reference could not be fetched — see Extraction Notes — so a
  fuller schema may exist elsewhere)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The Prospector's caveat made explicit, and it is the
  sharpest cross-vendor contrast in this note. Ch05's guardrail-availability
  claim rests on LiteLLM's two-knob spectrum (`docs-litellm-generic-guardrail-api.md`
  Claims 8-10, both defaults fail-closed, critical-level bypass log) and
  `docs-litellm-apply-guardrail-endpoint.md` Claim 11 already recorded the same
  documented gap on LiteLLM's direct-call route; promptfoo's evaluate endpoint
  is the *second* instance of the genre — a security control on a request path whose
  outage behavior its own docs do not specify. Here the gap is structurally
  worse than at a gateway: because the caller writes the gate (Claims 1-2),
  fail-open vs fail-closed on guardrail-service failure is decided implicitly
  by whatever each integrating service does on `!response.ok` — the shipped
  example throws (fail-closed), but nothing says production code does. No
  alertable bypass signal (compare LiteLLM's critical-level log line), no
  error-rate SLO hook, no `latencyMs`-based timeout policy. Not a
  contradiction — an undocumented surface we would name, for the guide, as
  operator-defined by omission: the failure policy exists only in whatever the
  integrating services happen to do.

## Concrete Artifacts

All artifacts verbatim from the fetched page
(https://www.promptfoo.dev/docs/enterprise/guardrails). Code-block line breaks
restored from the page's token-line structure with no wording changes; table
cells copied character-for-character; troubleshooting list numbers and bold
lead-ins rendered as plain list text (markup only, no wording changes).

### The integrate snippet (verbatim from "Integrate the Guardrail")

```javascript
const baseUrl = process.env.PROMPTFOO_API_BASE_URL ?? 'http://localhost:3200';
const targetId = process.env.PROMPTFOO_TARGET_ID;

if (!targetId) {
  throw new Error('PROMPTFOO_TARGET_ID is required');
}

const response = await fetch(`${baseUrl}/api/v1/guardrails/${targetId}/evaluate`, {
  method: 'POST',
  headers: {
    Authorization: `Bearer ${process.env.PROMPTFOO_API_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    placement: 'INPUT', // this can also be OUTPUT, TOOL_CALL_INPUT, and TOOL_CALL_OUTPUT
    messages: [{ role: 'user', content: 'Your user message here' }],
    identityContext: { sub: 'user-123', metadata: { role: 'admin' } }, // optional
  }),
});

if (!response.ok) {
  throw new Error(`Guardrail evaluation failed (${response.status}): ${await response.text()}`);
}

const result = await response.json();

if (result.action === 'block' || result.action === 'error') {
  // Do not send the input to the model.
}
```

### Input Example Limits (verbatim from "Technical Specifications")

| Stage | Limit | Notes |
| --- | --- | --- |
| Policy generation (max examples per vulnerability) | 500 | Raw input fed into the policy generation pipeline |
| Guardrail content generation (jailbreak examples) | 300 | Used to build guardrail context during creation |
| Testing a policy against examples | 50 | Max examples used when validating a policy's effectiveness |
| Issue attack examples (returned for display) | 20 | Shown in the UI for review |
| Guardrail test examples | 10 | Available in the test guardrail interface |

### LLM Prompt Limits (verbatim from "Technical Specifications")

| Context | Examples | Notes |
| --- | --- | --- |
| Policy generation prompt | 5 | Sampled from vulnerability examples to guide policy creation |
| Judgement phase prompt | 5 | Used to evaluate candidate policies |
| Known violations in guardrail system prompt | 3 | Included as few-shot examples for pattern matching |
| Runtime validation | 0 | Only policy text is sent — no raw examples, keeping latency low |

### Scaling Behavior (verbatim from "Technical Specifications")

| Metric | Value | Notes |
| --- | --- | --- |
| Scaled pipeline threshold | >20 examples | Automatically switches to map-reduce processing |
| Batch size (map-reduce) | 25 | Examples are processed in batches, then policies are consolidated |

### Policies (verbatim from "Technical Specifications")

| Constraint | Behavior | Notes |
| --- | --- | --- |
| Policies per guardrail | Unlimited | No schema cap on the number of policies |
| Policy consolidation | LLM-enforced deduplication | Redundant policies are merged automatically |
| Manual policies on regeneration | Preserved | Only automated policies are replaced when regenerating |

### Troubleshooting: "Guardrail not blocking expected patterns" (verbatim)

```
If legitimate jailbreak attempts are passing through:

1. Verify the pattern was discovered during red team testing. Guardrails can only block patterns similar to known vulnerabilities.
2. Add a manual example. If the pattern is new, you can add examples directly through the API — manual examples override automated extraction from red team results.
3. Regenerate the guardrail after running additional red team tests to incorporate new findings.
4. Check if the policy was consolidated. During generation, semantically overlapping policies are merged. Review your policies to ensure the relevant rule wasn't folded into a broader one.
```

### Troubleshooting: "Policies not updating after new red team tests" (verbatim)

```
If new vulnerabilities aren't reflected in your guardrail:

1. Trigger regeneration with force. Cached guardrails are returned by default — you must explicitly regenerate to incorporate new findings.
2. Verify vulnerabilities are associated with the correct target. Policies are generated from vulnerabilities linked to the guardrail's target ID, so confirm your red team results are tied to the right target.
3. Check permissions. Regeneration requires guardrail creation permissions. Verify your account has the appropriate access.
```

## Cross-References

**Candidates from `miner-related-notes.md`** (read before writing this section;
every listed path is cited or dismissed by name):

- `source-notes/docs-promptfoo-enterprise-findings-reports.md` — **cited**
  (Extends — see below).
- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch
  TPM/RPM rate-limit accounting for `POST /v1/batches`; no guardrail content
  of any kind.
- `source-notes/blog-promptfoo-owasp-red-teaming.md` — **cited** (Corroborates,
  Claim 6/Claim 10 pairing — see below).
- `source-notes/docs-promptfoo-enterprise-audit-logging.md` — **cited**
  (Extends — see below).
- `source-notes/blog-pagerduty-sre-agent-triage.md` — **dismissed**:
  AI-incident triage via an SRE Agent; no runtime guardrail contract.
- `source-notes/docs-promptfoo-pi-scorer.md` — **dismissed**: third-party
  scoring-model grader; no guardrail surface.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: Langfuse docs
  MCP server; unrelated vendor surface.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  characterization and measurement; unrelated.
- `source-notes/docs-google-sre-reliable-product-launches.md` — **dismissed**:
  launch-coordination discipline; unrelated.
- `source-notes/docs-google-sre-team-lifecycles.md` — **dismissed**: SRE team
  org/lifecycles; unrelated.

Additional cross-references found by searching `source-notes/` (the Prospector's
overlap list): `docs-promptfoo-guardrails-assertions.md`,
`docs-litellm-generic-guardrail-api.md`, `docs-litellm-apply-guardrail-endpoint.md`,
`docs-langfuse-security-and-guardrails.md` — all cited below.

**Primary cross-references (verified per MINER §4b — cited claims re-read in
the source notes before writing):**

- **Corroborates**:
  - `source-notes/docs-promptfoo-guardrails-assertions.md` **Claim 3**
    (the eval-side gate fails open when the response omits `guardrails`, so
    `guardrails` passes with score 1) — this page supplies the *runtime*
    member of the same silent-bypass family: a caller that handles only
    `block` falls through on `warn` and `error`, which the vendor explicitly
    warns against (Claim 2 here). Two planes, two leak paths, one shape:
    a gate that reports success while not enforcing. (Verified: claim heading
    and quote re-read.)
  - `source-notes/docs-litellm-generic-guardrail-api.md` **Claim 3** (the
    three-verdict response includes `GUARDRAIL_INTERVENED`, which rewrites
    the request) — corroborates the transforming-control semantics of this
    page's optional `sanitizedContent` (Claim 3 here): both vendors' guardrail
    contracts can block *and* rewrite, not merely deny. (Verified: claim
    heading and quote re-read.)
  - `source-notes/blog-promptfoo-owasp-red-teaming.md` **Claim 4**
    ("Pre-deployment red teaming must be integrated into CI/CD pipelines and run
    on a recurring schedule because LLM application changes have nondeterministic
    consequences") — that note states the *requirement* for recurring scans;
    this page is where the recurring scan pays a second dividend: each cycle
    also feeds the runtime guardrail's regeneration (Claims 6, 10 here), so the
    CI cadence is both an eval practice and a defense-coverage practice.
    (Verified: claim heading and quote re-read.)
- **Contradicts**: **None identified, and no contradiction issue filed.**
  Verified against `CONTRADICTIONS.md` (format-only file; no `C-NNN` entries)
  and the open `contradiction`-labeled issues (#1150, #1307, #1322, #1338,
  #1352, #1408, #1461, #1462, #1486, #1514, #1517, #1534, #1548, #1550, #1562,
  #1565, #1591, #1593, #1597) — none touch promptfoo runtime guardrail
  enforcement. The two candidate surfaces were checked rather than assumed:
  (a) Ch05's "guardrail in the request path is an availability dependency"
  (via `docs-litellm-generic-guardrail-api.md` Claims 8-10, both knobs default
  fail-closed) versus this page's caller-owned gate with no documented failure
  semantics (Claim 13) — that is a *documentation-depth* difference between
  vendors at different layers (gateway-attached vs caller-integrated), not two
  opposing claims about one fact; this page asserts nothing about what happens
  when the evaluate endpoint fails. (b) The eval-plane vs runtime-plane split
  is explicitly declared by the page itself (Claim 1), a conditioning
  distinction, not a conflict. No verdict picked here per MINER §4a.
- **Extends**:
  - `source-notes/docs-promptfoo-guardrails-assertions.md` — the corpus's
    promptfoo guardrail coverage moves from verdict-reading to *enforcement*:
    that note's Claims 1-2 ("It does not run a guardrail or inspect the text" /
    "A pass means Promptfoo did not receive `flagged: true`; it does not prove
    that a guardrail ran") describe the test-side reader, and this page is the
    runner that produces the production decision the assertion would grade if
    wired up. The two must be read as a pair in the guide (Claim 1 here) — the
    page's own note callout does exactly that.
  - `source-notes/docs-litellm-generic-guardrail-api.md` **Claims 8-10**
    (two-knob fail-open/fail-closed spectrum, both defaults closed;
    critical-level bypass log; classify-before-flipping guidance) — the
    contrast is the extension: this page is the second vendor's request-path
    guardrail contract with *no* analog to any of those three (Claim 13), and
    the pair tells the guide what to demand from any guardrail vendor's docs —
    failure knobs, an alertable bypass signal, and an outage-error budget —
    before attaching one to a request path. (Verified: claim headings and
    quotes re-read.)
  - `source-notes/docs-litellm-apply-guardrail-endpoint.md` **Claim 11**
    (the direct-call path documents no failure-semantics knobs, no HTTP status
    codes, no measured performance) — identical documented gap on a third
    guardrail invocation surface; this page's caller-throws-on-`!ok` example is
    the same "the consumer must define failure behavior" shape. Also extends
    its **Claim 7** (five guardrail types enumerated on the LiteLLM direct-call
    page) with this page's four third-party alternatives (Claim 12 here) —
    two vendors' menus of swappable guardrail backends. (Verified: claim
    headings and quotes re-read.)
  - `source-notes/docs-langfuse-security-and-guardrails.md` **Claim 3**
    ("Some LLM security checks need to be awaited before the model can be
    called, others block the response to the user") — that note makes guardrail
    latency a *traceable* dimension; this page's Parallel Execution section
    (Claim 4) supplies the missing cost half of the same decision (concurrent =
    zero benign latency but full LLM spend on blocked adversarial prompts) and,
    per **Claim 9** of that note (per-scanner scores logged, pipeline fails on
    any rejection), the per-guardrail `guardrailResults` / `severity` retention
    instruction (Claim 3 here) is the vendor-level analogue of per-scanner
    score logging. (Verified: claim headings and quotes re-read.)
  - `source-notes/docs-promptfoo-enterprise-audit-logging.md` **Claim 2**
    ("Audit Logging captures operations in the promptfoo control plane and
    administrative actions. Evaluation runs, prompt testing, and other data
    plane operations are tracked separately") — this page is one of the things
    "tracked separately" points at: per-request guardrail evaluations with
    `severity`, `guardrailResults`, and `latencyMs` (Claim 3) are data-plane
    telemetry whose retention, retrieval, and audit story that note's taxonomy
    explicitly does not cover. The control-plane audit log therefore cannot
    answer "which guardrail fired on this request" — only this endpoint's
    caller-held response objects can. (Verified: claim heading and both quotes
    re-read.)
  - `source-notes/docs-promptfoo-enterprise-findings-reports.md` **Claim 5**
    (Colang v1/v2 exports convert red-team findings into NVIDIA NeMo Guardrails
    guardrails — "a findings-to-runtime-defense loop that is net-new to this
    corpus") — this page is promptfoo's *native* findings-to-runtime-defense
    loop (red-team failures → generated policies → blocking rules, Claims 6,
    10), the same loop that note exported off-platform. Read together they show
    the loop in both forms: hosted (here) and portable (there), with this
    page adding the operational cost that note's export path defers — cache
    staleness, consolidation, and manual regeneration (Claim 7). (Verified:
    claim heading and quote re-read.)
- **Novel**: First corpus coverage of a **runtime enforcement API from an eval
  platform vendor**, and net-new regardless of vendor:
  1. **The four-placement / five-action gate contract** (Claims 1-2) — the
     placement enum with INPUT+OUTPUT default, the `allow|log|warn|block|error`
     aggregate, and the vendor's own fail-through warning as a citable
     fail-open trap.
  2. **The parallel-execution cost asymmetry** (Claim 4) — "zero added
     latency" for benign traffic *purchased with* full LLM cost on blocked
     adversarial prompts; no other corpus source states the guardrail
     latency/cost tradeoff this cleanly.
  3. **Two-plane filter ordering** (Claim 5) — regex fast filters
     short-circuiting "without calling the LLM" ahead of LLM policy
     evaluation, a second enforcement plane with its own false-positive class
     invisible to policy-severity tuning.
  4. **Cache-by-default staleness + LLM policy consolidation as documented
     causes of missed blocks** (Claims 7-8) — including the >20-example
     map-reduce threshold and the 0-example runtime-validation row, the
     corpus's first look inside a guardrail's authoring-vs-online context
     budget.
  5. **Tool-call placement as a manual-only surface** (Claim 9) — the
     coverage gap opposite LiteLLM's endpoint carve-out (its Claim 5).
  6. **The documented-absence finding** (Claim 13) — a request-path security
     endpoint with no documented failure semantics, second instance of the gap
     genre after `docs-litellm-apply-guardrail-endpoint.md` Claim 11.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — "A guardrail in the request path is an
  availability dependency" (`guide/05-llm-ops-reliability.md:1307`)**: Add the
  second vendor's contract as the *contrast case* the section currently lacks.
  Today the section rests entirely on LiteLLM's two-knob spectrum with
  fail-closed defaults and a critical-level bypass log. New material: (a) a
  caller-integrated guardrail endpoint has **no** vendor-side failure knobs —
  failure behavior is operator-defined by omission, with the shipped example's
  `throw`-on-`!response.ok` as the only documented failure path (Claim 13) —
  so the guide's rule should generalize from LiteLLM's knobs to *what every
  guardrail dependency needs* (failure policy, bypass signal, error budget),
  naming both vendors; (b) add the parallel-execution cost asymmetry to the
  section's tradeoff vocabulary: the concurrent pattern converts guardrail
  latency into adversarial-prompt LLM spend (Claim 4), so "guardrail placement"
  is a three-way choice (pre-model / concurrent / post-response) trading user
  latency against provider cost against blocked-output exposure; (c) route the
  aggregate-`action` handling rule (Claim 2) through the chapter's
  config-change three-property test — an integrating service that adds a
  `warn`/`error` branch (or removes one) silently changes gate behavior.
- **Chapter 06 (Security and Trust) — "A guardrail gate reads a signal — it
  does not run a guardrail" (`guide/06-security-and-trust.md:387`)**: Extend
  the section into a two-plane statement of promptfoo's guardrail stack: the
  eval-side verdict reader (existing, cited to
  `docs-promptfoo-guardrails-assertions`) and the runtime enforcement endpoint
  this note covers (Claim 1's page callout is the vendor's own sentence for
  it). New checklist items beside the existing rule: handle `warn`/`error`
  explicitly in the gate (Claim 2), keep `guardrailResults`/`severity`/
  `latencyMs` rather than collapsing to a boolean (Claim 3), know that fast
  filters decide before any LLM stage (Claim 5), and never present the
  adaptive loop as signatureless — "can only block patterns similar to known
  vulnerabilities" (Claim 6).
- **Chapter 06 — "Red-teaming as a CI gate" (`guide/06-security-and-trust.md:120`)**:
  Add the runtime dividend of the recurring-scan discipline: each red-team
  cycle is also the coverage-expansion mechanism for the production guardrail,
  but only if someone forces regeneration — cached guardrails are returned by
  default, consolidation can fold a specific rule into a broader one, and the
  cadence is explicitly manual (Claims 7, 10). Concretely: make
  "regenerate + diff policies" a tracked step in the post-scan runbook, not an
  implied side effect of scanning.
- **Chapter 06 — "Function-calling authorization" (`guide/06-security-and-trust.md:265`)**:
  Add `TOOL_CALL_INPUT` PII/argument filtering (Claim 9) as a second concrete
  runtime mechanism beside the LiteLLM `tools`/`tool_calls` gateway guardrail
  already cited there, with two honesty caveats from this page: tool-call
  policies are **not** auto-generated from scans (manual forever), and the
  vendor's own onboarding advice defers tool placements to "later," so a
  first integration has no tool-call coverage.

## Extraction Notes

- Source read in full via HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/enterprise/guardrails, HTTP 200, no
  paywall). Every `Quote` was verified character-for-character against the raw
  HTML text extraction before writing; code-block line breaks in the integrate
  snippet were restored from the page's token-line structure (no wording
  changes), and the four Technical Specifications tables were reconstructed
  from the page's own `<table>` cells. Quote locations for re-verification:
  Claim 2/3 quotes are the paragraph immediately after the integrate snippet
  under "Integrate the Guardrail"; Claim 4 quotes are the two "Parallel
  Execution" paragraphs; Claim 5 quotes are the FAQ answer "How are fast
  filters and policies evaluated?" and the "Generate Guardrail" fast-filter
  paragraph; Claim 6 quotes are the FAQ "How does the guardrail handle new
  attack types?" and troubleshooting item 1; Claim 7 quotes are the two
  troubleshooting playbooks and the FAQ "Can I disable specific automated
  policies?"; Claim 8's quote is the LLM Prompt Limits table's Runtime
  validation row; Claim 11 quotes are the two "Testing the Guardrail"
  paragraphs.
- **Linked pages followed (MINER §1, budget of 5)**: (1)
  `https://www.promptfoo.dev/docs/guides/testing-guardrails/` — fetched and
  read; it is eval-side testing material whose feature-comparison table
  explicitly separates "Enterprise Adaptive Guardrails | How do I enforce
  Promptfoo-hosted policies at runtime?" from the `guardrails`/`not-guardrails`
  assertions, independently confirming the plane split recorded in Claim 1; it
  is otherwise adjacent to the existing assertions note and was not
  re-extracted. (2) The integrate paragraph's linked API reference
  (`https://www.promptfoo.dev/docs/api-reference/#tag/guardrails`, "full
  request and response schema") — **could not be read**: the page is
  client-rendered Swagger with no statically fetchable spec (probed
  `/openapi.yml`, `/openapi.json`, `/swagger.json`, `/docs/openapi.yml`,
  `/spec/openapi.yaml`, `/docs/api-reference/guardrails` — all 404; no spec URL
  referenced in the shipped JS). Contract claims in Claims 1-3 therefore rest
  on this page's own prose and code sample, which state the endpoint, enum
  members, response fields, and auth env vars explicitly; the full schema is
  recorded as unknown rather than absent. The prose-linked `guardrails`
  assertion page and `GET /guardrails` export endpoint are already covered by
  `docs-promptfoo-guardrails-assertions.md` / this note's FAQ extraction and
  were not re-fetched.
- **Enterprise gating**: first-party spec behind "This feature requires
  Promptfoo Enterprise" — nothing checkable against the OSS repo, and per the
  Prospector's caveat no performance claim was extracted as evidence (there
  are none on the page: zero latency, FP-rate, volume, or cost figures). The
  0.30/0.7 severity values are worked example settings, not defaults, and are
  labeled as such in Claim 11.
- **Contradiction scan (MINER §4a)**: none filed; see Cross-References →
  Contradicts for the two candidate surfaces checked (LiteLLM availability
  semantics; eval-vs-runtime plane split) and why neither qualifies.
- **Cross-ref verification (§4b)**: every cited claim was re-read in its source
  note before writing: `docs-promptfoo-guardrails-assertions.md` Claim 3;
  `docs-litellm-generic-guardrail-api.md` Claims 3, 8-10;
  `docs-litellm-apply-guardrail-endpoint.md` Claims 7, 11;
  `docs-langfuse-security-and-guardrails.md` Claims 3, 9;
  `docs-promptfoo-enterprise-audit-logging.md` Claim 2 (heading + both
  quotes); `docs-promptfoo-enterprise-findings-reports.md` Claim 5 (heading +
  quote); `blog-promptfoo-owasp-red-teaming.md` Claim 4 (heading + quote).
  No claim numbers invented.
- `confidence_overall` is `emerging`, matching the sibling promptfoo
  Enterprise/config notes (#1303 assertions, #1589 audit-logging): the
  contract claims (endpoint, enums, caps, lifecycle, ordering) are
  settled-as-documented and string-checkable, but this is vendor documentation
  behind an Enterprise gate with zero measurement, no independent validation,
  an unfetchable API schema (Claim 13's absence is scoped to this page), and
  several operational conclusions in `Our assessment` (calibration loop,
  consolidation loss, tool-surface gap) that are the Miner's synthesis from
  the documented surface.
- `date_published` uses the page's "Last updated on Oct 7, 2026" date
  (undated page otherwise).
