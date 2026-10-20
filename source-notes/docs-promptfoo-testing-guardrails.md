---
source_url: https://www.promptfoo.dev/docs/guides/testing-guardrails
source_type: docs
title: "Promptfoo Guide: Testing and Validating Guardrails"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-19
date_extracted: 2026-10-20
last_checked: 2026-10-20
status: current
confidence_overall: emerging
issue: "#1800"
---

# Promptfoo Guide: Testing and Validating Guardrails

> A practical guide for testing guardrails as part of CI and evals, emphasizing the distinction between detect-only signals and enforced blocks, integrated-vs-standalone testing, mixed-dataset gating, and fail-closed normalization across vendor adapters.

## Source Context

- **Type**: docs (vendor how-to guide, not a reference page)
- **Author credibility**: Promptfoo, first-party LLM eval/red-team vendor. The guide is operational documentation with concrete provider normalization examples and explicit failure-mode warnings; it publishes no measured efficacy metrics, so its framing is prescriptive rather than evidence-backed.
- **Scope**: Covers guardrail eval design patterns: choosing the right safety check, integrated app testing vs direct service testing, HTTP/provider transforms, per-provider normalization (Azure Content Safety/Prompt Shields, Bedrock ApplyGuardrail, NeMo), the `guardrails`/`not-guardrails` assertions with `purpose: redteam`, and production gate metrics. Links to the `guardrails` assertion reference page; does not duplicate the full assertion matrix in depth. Post-dates the previously captured assertion note (#1303) and carries updated adapter guidance.

## Extracted Claims

### Claim 1: Guardrail outcomes are not binary in effect — a reported match may reject, replace, mask, or only annotate; a signal does not prove enforcement
- **Evidence**: Opening sentence and "Choose the right safety check" section contrasting `guardrails` assertion (reads normalized `guardrails.flagged` on the target response) with `moderation` assertion (runs an independent grader) and emphasizing detect-only vs enforced blocks.
- **Confidence**: settled (operational design principle documented across promptfoo guardrail material)
- **Quote**: "A reported match does not always mean the request was blocked."
- **Our assessment**: This is the central SRE framing: treat the normalized `guardrails` object as a verdict signal from the target, not proof that the system actually prevented the unsafe output from propagating. It reinforces the precondition for gating: any CI gate must know whether `flagged: true` means an enforced block in the production path (see Claim 5).

### Claim 2: Test the integrated application at least once — a standalone classifier can pass while the app drops streaming intervention, skips fallback, or fails to forward the final decision
- **Evidence**: "Testing Application with Integrated Guardrails" lead and rationale.
- **Confidence**: settled (operational best practice; cannot be inferred from provider normalization alone)
- **Quote**: "A standalone classifier can pass while the application drops its streaming intervention, skips a fallback path, or fails to forward the final decision."
- **Our assessment**: A two-level testing discipline (integrated + direct) is operationally necessary for wiring failures. This is distinct from tuning thresholds (which direct testing does well) and is the specific "wiring/observability failure class" flagged in triage.

### Claim 3: Mixed datasets require paired assertions — adversarial cases use `not-guardrails`, benign cases use `guardrails`; do not rely on a single `defaultTest` in mixed suites
- **Evidence**: "Choose the right safety check" and "Guardrails Assertion" example; note about not using `defaultTest` in mixed suites appears in the referenced assertion behavior.
- **Confidence**: settled (documented assertion discipline)
- **Quote**: "Promptfoo adds default assertions to the `not-guardrails` attack cases too." (referenced; the page shows explicit per-case `assert` for attack/benign)
- **Our assessment**: A one-sided gate measures nothing. The guide's explicit pairing prevents applying a benign expectation to attack cases.

### Claim 4: HTTP status alone does not indicate a guardrail fired — in-band signals are common (AWS ApplyGuardrail HTTP 200; Azure output filters may return HTTP 200 with `finish_reason: content_filter`; Anthropic may return HTTP 200 with `stop_reason: refusal`; Mistral blocks with HTTP 403 and are not normalized by promptfoo today)
- **Evidence**: "How guardrail responses arrive" callouts and "Things to think about" signal mapping notes, plus the transform examples showing parsing from body/metadata.
- **Confidence**: emerging/settled per vendor (vendor-documented behavior; coverage varies)
- **Quote**: "AWS `ApplyGuardrail` returns HTTP 200 with an action, Azure can return a successful completion with `finish_reason: content_filter`, and Anthropic can return a successful message with `stop_reason: refusal`. Return expected interventions as a scorable `output` plus `guardrails`."
- **Our assessment**: Counters the naive "non-200 means blocked" monitoring heuristic. For CI gating, the decision must be parsed from the normalized `guardrails` (or transformed body), not HTTP status.

### Claim 5: Guardrail execution failures/timeouts/partial/skipped/filter errors must be surfaced as errors/indeterminate, not mapped to `flagged: false` (fail-closed)
- **Evidence**: "Guardrails Assertion" verification checklist ("Guardrail timeouts and filter failures should not appear as clean passes"), "Testing Azure Content Filter" ("Do not label the result `flagged: false` when the Content Safety request fails"), and the fail-closed guidance in the transform/normalization section.
- **Confidence**: settled (explicit vendor guidance)
- **Quote**: "Guardrail execution failures should surface as errors and be tracked as indeterminate, not mapped to `flagged: false`."
- **Our assessment**: This directly addresses the central fail-open hazard. For release gates, indeterminate is a failure class (not a pass), so CI must count indeterminate rate (Claim 9).

### Claim 6: `flagged` means the target reported a policy trigger, not that enforcement occurred — the redteam `purpose` override requires that `flagged: true` proves an actual block
- **Evidence**: "Comparing Guardrail Performance" section describing `guardrails-eval` plugin + `purpose: redteam` assertion and the override semantics; warning about detect-only hiding bypass.
- **Confidence**: settled (documented override behavior)
- **Quote**: "`guardrails-eval` is a collection of vulnerability plugins, not a provider integration or assertion. ... The companion `purpose: redteam` assertion changes final aggregation: a `flagged: true` response force-passes the whole test, overriding the vulnerability grader and every other assertion. Only enable it when `flagged: true` proves the request was actually blocked — a detect-only signal that still returns unsafe output would hide the bypass."
- **Our assessment**: Critical for red-team CI: the override is safe only when the target’s `flagged: true` corresponds to enforced blocking. With detect-only classifiers, enabling `purpose: redteam` can produce `success: true`/exit 0 while an unsafe response is still delivered.

### Claim 7: Provider-native specifics matter for correct normalization — Azure AI Content Safety uses ordinal severities (0/2/4/6, not probabilities); Prompt Shields uses `userPromptAnalysis.attackDetected` and `documentsAnalysis[].attackDetected`; Bedrock ApplyGuardrail returns HTTP 200 for both clean and intervened (map `action === 'GUARDRAIL_INTERVENED'` to `flagged: true`); NeMo requires explicit rail status normalization (do not infer block from refusal text); Model Armor `NO_MATCH_FOUND`/skipped states are detect-only caveats
- **Evidence**: Dedicated subsections with concrete field names, API notes, and code snippets/transform guidance.
- **Confidence**: emerging/settled (vendor-specific details current as of 2026-10-19)
- **Quote**: "Azure AI Content Safety’s Analyze Text API returns ordinal severity levels, not 0–1 probabilities. The default four-level scale is `0`, `2`, `4`, and `6`;" and "Azure uses `content_filter_error` for an indeterminate filter result."; "Prompt Shields returns prompt and document attack decisions. The current response fields are `userPromptAnalysis.attackDetected` and `documentsAnalysis[].attackDetected`."; "ApplyGuardrail returns HTTP 200 for both clean and intervened content. A detection-only assessment is not the same as an intervention, so choose whether your benchmark measures policy matches, enforced blocks, or both."; "Do not infer a block only from generic refusal text."
- **Our assessment**: These concrete mapping details fill gaps not present in the high-level assertion note, especially for Azure ordinal severities and the explicit “detection-only ≠ intervention” distinction for Bedrock/Model Armor-style behavior.

### Claim 8: Missing guardrail metadata is a fail-open case — a green test with no `guardrails` object proves nothing about enforcement
- **Evidence**: "Guardrails Assertion" verification step.
- **Confidence**: settled (explicit caution)
- **Quote**: "Missing guardrail metadata currently behaves like `flagged: false`. Inspect at least one real result before using the assertion as a CI gate; a green test with no `guardrails` object proves nothing about enforcement."
- **Our assessment**: Reinforces Claim 3’s spirit from the assertion note but framed as a pre-gate inspection checklist item. Matches the corpus’s existing finding about silent fail-open when the signal is absent.

### Claim 9: Gate design should track four production metrics — attack block rate, false-positive rate, indeterminate rate (timeouts/partial/skipped/filter errors), and latency/cost of integrated vs standalone guarding
- **Evidence**: "Things to think about" numbered list.
- **Confidence**: emerging (operational recommendation, not empirically justified by the page)
- **Quote**: "Track at least four outcomes: 1. **Attack block rate**: attacks with `flagged: true` divided by attacks attempted. 2. **False-positive rate**: benign cases incorrectly flagged divided by benign cases. 3. **Indeterminate rate**: guardrail timeouts, partial executions, skipped filters, and filter errors. 4. **Latency and cost**: compare integrated and standalone guardrail overhead."
- **Our assessment**: Explicitly elevates indeterminate rate to a first-class metric (ties to Claim 5). Treating indeterminate as non-pass is the CI implication.

### Claim 10: Fail closed in transforms — throw on unknown/missing critical fields and do not default unknown decisions to `flagged: false`
- **Evidence**: HTTP transform examples show throwing on missing decision/attackDetected, and the Azure Content Safety example says "Do not label the result `flagged: false` when the Content Safety request fails."
- **Confidence**: settled (defensive programming guidance)
- **Quote**: "A provider `error` skips assertions. ... Return expected interventions as a scorable `output` plus `guardrails`." and "Do not label the result `flagged: false` when the Content Safety request fails."
- **Our assessment**: Normalization layer is where fail-closed must be enforced; assertion itself cannot recover when the signal is collapsed into `flagged: false`.

## Cross-References

- **Corroborates**: `source-notes/docs-promptfoo-guardrails-assertions.md` — same `GuardrailResponse` shape, missing-metadata fail-open, `not-guardrails` inverse, and `purpose: redteam` override semantics. This guide operationalizes those with provider mappings and integrated-vs-standalone testing.
- **Extends**: `source-notes/docs-promptfoo-guardrails-assertions.md` — adds vendor intervention-signal matrix details (ordinal severities, Prompt Shields field names, ApplyGuardrail HTTP 200, detect-only vs enforced, indeterminate-as-failure), two-level testing discipline, and four production metrics including indeterminate rate. Also links to HTTP provider guardrails support.
- **Extends**: `source-notes/docs-promptfoo-enterprise-guardrails.md` — runtime enforcement contract at Enterprise layer; this guide is the eval/testing discipline for that contract (what to assert and how to normalize across vendors).
- **Complementary**: `source-notes/docs-litellm-generic-guardrail-api.md` — focuses on guardrail-in-request-path availability/fail-open behavior in a gateway; complementary to eval/testing perspective here.
- **Novel**: The explicit "indeterminate rate" as a required gate metric, concrete Azure Content Safety ordinal severity guidance (0/2/4/6, not probabilities), explicit "detection-only ≠ intervention" for Bedrock/Model Armor style cases, and the operational instruction to test the integrated application (wiring/streaming/fallback) as a required practice rather than optional.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: Add guardrail gate criteria requiring (a) integrated+standalone tests, (b) mixed datasets with paired `guardrails`/`not-guardrails`, (c) fail-closed normalization (never collapse errors/timeouts to `flagged: false`), (d) track indeterminate rate as a first-class SLO/metric, (e) explicit precondition check before enabling `purpose: redteam` override.
- **Chapter 06 (Security and Trust)**: Capture vendor signal mapping table (HTTP status is not a signal; AWS HTTP 200 with action, Azure content_filter vs HTTP 400, Anthropic stop_reason, Mistral 403, detect-only cases). Document redteam override hazard (hide bypass when detect-only) and missing-metadata fail-open inspection requirement.
- **Chapter 02 (Observability)**: Add guardrail-signal export/inspection checklist (`--no-cache`, export `.response.guardrails` per case, check for missing object, track indeterminate/latency/cost).

## Extraction Notes

- Page is vendor documentation updated 2026-10-19; first-party, current. Content matches triage key questions precisely (vendor signal matrix, indeterminate-as-failure, two-level testing). Cites relation to assertion reference without re-extracting full matrix.
- Extraction focused on operational gate-design claims (not product marketing). Provider-specific details captured verbatim where safety-critical (ordinal severities, field names, caveats). Did not extract all code blocks as artifacts beyond noting normalization patterns; the transform examples are illustrative.
- Cross-refs target existing corpus notes; no contradiction found. Overlaps assertion note but extends with implementation details.
