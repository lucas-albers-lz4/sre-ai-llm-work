---
source_url: https://docs.litellm.ai/blog/two-week-stability-update
source_type: blog-post
title: "July stability update: hardening MCP auth and cutting pass-through memory"
author: "Ishaan Jaffer (CTO, LiteLLM), Tin Lo (AI Engineer), Mateo Wang (AI Engineer), Yassin Kortam (Senior SWE)"
date_published: 2026-07-11
date_extracted: 2026-09-08
last_checked: 2026-09-08
status: current
confidence_overall: settled
issue: "#1241"
---

# July stability update: hardening MCP auth and cutting pass-through memory

> A two-week vendor stability report from LiteLLM covering two major engineering
> fixes (MCP Gateway credential resolver refactor and pass-through memory
> streaming), a breakdown of 134 merged bug fixes by area, and a forward-looking
> goal of 95% end-to-end test coverage — with concrete PR numbers, failure-mode
> enumerations, and a deliberate memory-vs-inspectability trade-off for proxy
> pass-through routes.

## Source Context

- **Type**: blog-post (vendor engineering stability report), tagged
  `stability`, `mcp`, `performance`, `product`.
- **Author credibility**: High for *what LiteLLM is doing in its own
  reliability pipeline* — authored by the CTO (Ishaan Jaffer) and three AI
  engineers at LiteLLM, reporting completed work (134 merged fix PRs) with
  concrete evidence (PR numbers, before/after descriptions, failure-mode
  enumerations). This is the July installment of the recurring vendor
  reliability cadence that started with the April townhall and continued through
  May and June.
- **Scope**: Covers (1) MCP Gateway credential resolver redesign —
  inferring auth vs declaring auth, fail-closed typed match, the specific bug
  class this kills, (2) pass-through memory fix — streaming non-JSON
  downloads to bound memory while intentionally buffering JSON for
  inspectability, (3) by-area fix counts (134 total), (4) forward goal of
  95% e2e test coverage. Does NOT cover: Rust migration, release versioning,
  product roadmap, or CI/CD changes — those are covered by other townhall posts.

## Extracted Claims

### Claim 1: The MCP Gateway previously inferred the auth method from whichever credential fields were set, with no single resolver and no error on ambiguity — ambiguity resolved to "attach a credential anyway" instead of "stop"
- **Evidence**: Described under "Before: infer the auth method from whatever
  credentials are set" with a named bug class.
- **Confidence**: settled
- **Quote**: "there was no single place that decided which credential to attach,
  and no error when the decision was ambiguous. Inferring from set fields meant
  two code paths could read the same server and disagree. The precedence order
  meant adding a field could silently change which credential won. And the silent
  fallback meant an unhandled case still sent something upstream instead of
  refusing. Ambiguity resolved to 'attach a credential anyway' instead of
  'stop'."
- **Our assessment**: A clear articulation of the "infer from fields" anti-
  pattern in gateway auth design. The four failure modes (two paths disagree,
  precedence shift, silent fallback, no refusal) are specific and
  transferable. This is a real architectural pattern worth capturing for any
  LLM gateway implementing multi-credential MCP routing.

### Claim 2: The inferred-auth approach caused five specific classes of bugs — tokens to wrong upstream, duplicate/stale Authorization headers, MCP requests skipping team/route/key checks, stale/cross-user cached OAuth tokens, and upstream URLs/secrets leaking into logs
- **Evidence**: Enumerated list under the "Before" section with five
  named failure types.
- **Confidence**: settled
- **Quote**: "Tokens sent to the wrong upstream server. Duplicate or stale
  `Authorization` headers slipping through. MCP requests skipping the normal
  team, route, and key checks. Cached OAuth tokens going stale or crossing
  between users. Upstream URLs and secrets showing up in logs."
- **Our assessment**: Five concrete, distinct failure modes. The "cross-user
  OAuth tokens" and "upstream URLs/secrets in logs" items are the most
  security-relevant — they describe credential misrouting and credential
  leakage, two failure classes already in the corpus from other LiteLLM notes.
  This enumeration is the evidence base for the architectural fix that follows.

### Claim 3: The fix replaces inference with an explicit user-declared auth method in a typed credential-resolver class, with exhaustive match so adding a mode without handling it fails the type checker, and unhandled cases raise instead of silently attaching no auth
- **Evidence**: Described under "After: the user declares the auth method, and
  it fails closed" with design constraints.
- **Confidence**: settled
- **Quote**: "Each mode has its own fully typed config, so there is no guessing
  from which fields are set and no precedence order. The match is exhaustive,
  so adding a mode without handling it fails the type checker, and an unhandled
  case raises instead of quietly attaching no auth."
- **Our assessment**: A textbook fail-closed typed-dispatch pattern. The three
  guarantees — (1) no guessing from fields, (2) exhaustive match catches new
  modes at type-check time, (3) unhandled case raises — are transferable
  design principles for any gateway implementing credential resolution across
  multiple auth methods. This is the key extractable pattern from this source.

### Claim 4: Large non-JSON pass-through downloads (batch-result files, binary/octet-stream) were previously buffered whole in memory before being forwarded; the fix streams responses chunk-by-chunk so memory stays flat regardless of file size
- **Evidence**: Described under "Performance: pass-through memory" with PR
  number.
- **Confidence**: settled
- **Quote**: "Large non-JSON pass-through downloads (batch-result files, binary
  and octet-stream downloads) were buffered whole in memory before being sent
  on. We changed this to stream the response chunk by chunk, so memory stays
  flat regardless of file size (#32386)."
- **Our assessment**: A concrete memory fix with a specific PR number. The
  before/after is clear: whole-buffer → chunked-stream for non-JSON. The
  scope is explicitly named: provider pass-through routes (`/vertex_ai/*`,
  `/bedrock/*`, `/openai/*`, `/anthropic/*`) and custom pass-through
  endpoints. High credibility.

### Claim 5: JSON responses still buffer by design so spend logging and guardrails can inspect the body — a deliberate memory-vs-inspectability trade-off
- **Evidence**: Explicitly stated in the same section as the streaming fix.
- **Confidence**: settled
- **Quote**: "JSON responses still buffer by design, so spend logging and
  guardrails can inspect the body."
- **Our assessment**: The deliberate trade-off is the extractable pattern here.
  A gateway proxy that streams everything loses the ability to inspect the body
  for spend logging and guardrails; a gateway that buffers everything pays the
  memory cost. LiteLLM's choice — stream binary/octet-stream (no inspection
  needed), buffer JSON (inspection required) — is a practical boundary. This
  is reusable guidance for proxy/gateway pass-through route design.

### Claim 6: Prometheus skips budget-metric DB lookups entirely when gauges are no-ops (nothing is scraping them)
- **Evidence**: Listed under "Two more fixes in the same spirit."
- **Confidence**: settled
- **Quote**: "Prometheus skips budget-metric DB lookups entirely when the gauges
  are no-ops (nothing is scraping them)."
- **Our assessment**: A simple, transferable optimization pattern — avoid paying
  for work nobody needs. The principle is generic: if a monitoring metric has
  no consumers, don't compute it. The concrete instantiation (Prometheus
  budget-metric DB lookups when gauges are no-ops) is a specific example of
  lazy evaluation for observability overhead.

### Claim 7: The complexity router builds its semantic route index once under concurrent cold-start, instead of rebuilding it per request
- **Evidence**: Listed under "Two more fixes in the same spirit."
- **Confidence**: settled
- **Quote**: "The complexity router builds its semantic route index once under
  concurrent cold-start, instead of rebuilding it per request."
- **Our assessment**: A standard compute-once-cache-many optimization. The
  specific detail ("once under concurrent cold-start") suggests the index is
  built lazily on first request and then shared — a well-known pattern. The
  transferable lesson is that route-resolution lookups that are invariant
  across requests should not be recomputed.

### Claim 8: 134 bug fixes shipped in two weeks, with the largest area being MCP Gateway (50 fixes), followed by LLM Providers (27), Proxy Core/Reliability (23), UI/Dashboard (20), Logging/Observability (9), and Guardrails (5)
- **Evidence**: Published by-area breakdown table with counts.
- **Confidence**: settled
- **Quote**: "All 134 fixes, by area: MCP Gateway — 50, LLM Providers (AI Eng)
  — 27, Proxy Core / Reliability — 23, UI / Dashboard — 20, Logging /
  Observability — 9, Guardrails — 5, Total — 134."
- **Our assessment**: Concrete, enumerated retrospective data. The
  concentration of fixes in MCP Gateway (37% of all fixes) is the strongest
  signal — it shows where the active failure surface is in this gateway. The
  note "One reported ticket often turns into several fix PRs" explains why the
  PR count exceeds the ticket count. The LLM provider fixes break down further:
  10 new-model capability drops, 6 wrong-cost, 6 wrong-routing, 5 broken
  response/streaming. High credibility as self-reported vendor metrics.

### Claim 9: Most of the 134 bugs were caught late — in staging or from user reports — and the next goal is 95% end-to-end test coverage, citing Meta's fix-fast approach
- **Evidence**: Stated under "Next goal: 95% end-to-end test coverage."
- **Confidence**: emerging
- **Quote**: "Most of these 134 bugs were caught late, in staging or from a user
  report. We want to catch them before they merge. We believe by investing in
  improving our e2e testing coverage we can significantly reduce the number of
  reported regressions from users on an upgrade."
- **Our assessment**: The admission that bugs were caught late (staging/user
  reports rather than tests) is honest and informative. The 95% e2e coverage
  target is forward-looking. The Meta reference ("fix-fast" approach) provides
  external grounding for the strategy. The June townhall note already captured
  the zero-regression commitment (Aug 29 target); this July note shows the
  testing-infrastructure follow-through. Confidence is emerging because the 95%
  target is aspirational, not delivered.

## Concrete Artifacts

**By-area fix breakdown (verbatim from source):**
```
| Area                    | Fixes |
|-------------------------|-------|
| MCP Gateway             | 50    |
| LLM Providers (AI Eng)  | 27    |
| Proxy Core / Reliability| 23    |
| UI / Dashboard          | 20    |
| Logging / Observability | 9     |
| Guardrails              | 5     |
| Total                   | 134   |
```

Attribution: https://docs.litellm.ai/blog/two-week-stability-update, "By the
numbers" section.

**LLM provider fix breakdown (verbatim from source):**
```
| Type of bug                          | Count |
|--------------------------------------|-------|
| New model capabilities getting dropped| 10    |
| Wrong cost or billing                 | 6     |
| Routing or fallback picking wrong model| 6    |
| Broken response or streaming output   | 5     |
| Total                                | 27    |
```

Attribution: https://docs.litellm.ai/blog/two-week-stability-update, "AI Eng:
LLM providers (27 fixes)" section.

**Key PRs from the MCP credential resolver work (verbatim from source):**
```
#32815 credential class merge (the single typed resolver)
#32652 stale token invalidation
#32715 semantic filter fail-closed
```

Attribution: https://docs.litellm.ai/blog/two-week-stability-update, Appendix
→ MCP Gateway → Credential resolver.

**Pass-through memory fix PR (verbatim from source):**
```
#32386 stream non-SSE pass-through responses instead of buffering in memory
```

Attribution: https://docs.litellm.ai/blog/two-week-stability-update, Appendix
→ Performance.

## Cross-References

- **Corroborates**:
  - `blog-litellm-june-townhall-updates.md` **Claim 5** (MCP auth unified
    from 5 separate code paths to a single unified path) — the June note
    reports the unification as delivered; this July note is the deeper technical
    follow-through: it names the specific anti-pattern (inference from fields),
    the five bug classes it caused, and the architectural fix (typed credential
    resolver with exhaustive match + fail-closed). The June claim describes the
    "what"; this July source describes the "how" and "why." They are consistent
    and complementary.
  - `blog-litellm-june-townhall-updates.md` **Claim 8** (zero-regression
    commitment with Aug 29 target) — this July note's admission that "most of
    these 134 bugs were caught late, in staging or from a user report" is the
    diagnostic that explains *why* the zero-regression commitment exists: the
    current test coverage is insufficient to catch regressions pre-merge. The
    95% e2e coverage goal is the infrastructure response.
  - `blog-litellm-may-townhall-updates.md` **Claim 2** (89 vulnerabilities
    patched in 4 weeks) — the July note's 134-fix count in 2 weeks is a higher
    velocity, consistent with the escalating fix cadence across the May→June→July
    window. Different scope (vulnerability patches vs. all bug fixes) but same
    operational pattern of public fix-count reporting.

- **Extends**:
  - `failure-litellm-mcp-stdio-command-injection.md` — that note covers
    CVE-2026-30623 (command injection via MCP stdio `command` field) with an
    allowlist-based fix. This July note covers a different MCP auth failure
    class: credential resolution ambiguity (wrong token, stale OAuth, secrets in
    logs). Both are MCP gateway security hardening, but they address orthogonal
    vulnerability surfaces — input validation (CVE) vs. credential routing
    (this note). The July note's typed credential resolver is architecturally
    complementary to the stdio allowlist: one hardens what commands the gateway
    runs, the other hardens which credentials the gateway attaches.
  - `failure-litellm-guardrail-logging-secret-exposure.md` — that note covers
    upstream URLs and secrets appearing in logs via the guardrail logging path.
    This July note names "upstream URLs and secrets showing up in logs" as one
    of the five bug classes caused by the inferred-auth approach. The July
    source is the *design fix* for the credential-resolution path that caused
    the symptom documented in the guardrail-logging note. The guardrail-logging
    note covers the observability-side fix (sanitization before emission); this
    July note covers the auth-side fix (typed resolver so wrong credentials
    are never attached in the first place). Complementary, not redundant.
  - `blog-litellm-june-townhall-updates.md` — extends the June townhall's
    stability report with the next monthly installment. The June note covers
    Rust benchmarks, zero-regression commitment, and root-cause fixes; this
    July note covers MCP auth hardening, pass-through memory, and the testing
    follow-through. Same vendor cadence genre, different engineering focus.

- **Novel**: Introduces the following patterns to the corpus for the first time:
  1. **Fail-closed typed credential resolver for MCP gateway auth** — the
     "infer from fields" → "declare with typed config + exhaustive match"
     pattern, with the five specific bug classes it prevents. This is a
     transferable security pattern for any LLM gateway implementing multi-
     credential MCP routing.
  2. **Streaming pass-through vs. buffer-for-inspectability trade-off** — the
     deliberate design decision to stream non-JSON pass-through responses
     (flat memory) while buffering JSON responses (for spend logging and
     guardrails). This is reusable guidance for proxy/gateway pass-through
     route design.
  3. **134-fix breakdown by area** — the first July installment of the public
     fix-count cadence, showing MCP Gateway as the dominant failure surface
     (37% of fixes) and LLM provider bugs broken down by type.
  4. **95% e2e test coverage target** — the testing-infrastructure follow-
     through on the June zero-regression commitment, with Meta's fix-fast
     approach as the stated inspiration.

## Guide Impact

- **Chapter 06 (Security and Trust) — MCP Credential Resolution Pattern**:
  Add the "infer from fields" anti-pattern and the "declared typed config +
  exhaustive match + fail-closed" fix as a concrete security design pattern
  for LLM gateways implementing MCP multi-credential routing. Cite the five
  bug classes (wrong-upstream tokens, stale Authorization headers, skipped
  team/route/key checks, cross-user OAuth cache, secrets in logs) as the
  evidence base for why inference-from-fields is unsafe. Reference this source
  note's Claims 1–3.

- **Chapter 05 (LLM Ops Reliability) — Pass-Through Memory Management**:
  Add the streaming-vs-buffering trade-off for proxy pass-through routes:
  stream non-JSON (binary/octet-stream) to bound memory; buffer JSON for
  spend logging and guardrails. This is a concrete implementation of the
  "don't pay for work nobody needs" principle (Prometheus no-op gauge skip,
  complexity router one-time index build). Reference this source note's
  Claims 4–7 and the PR (#32386).

- **Chapter 05 (LLM Ops Reliability) — Vendor Reliability Cadence**: Add
  this July stability update as the next data point in the recurring vendor
  reliability report series (April → May → June → July). The 134-fix count
  and by-area breakdown provide a reliability-signal for LLM gateway operators
  evaluating vendor stability. Note the MCP Gateway concentration (37% of
  fixes) as an indicator of active failure-surface investment.

- **Chapter 05 (LLM Ops Reliability) — Testing Coverage as a Reliability
  Investment**: Add the 95% e2e coverage target and the admission that most
  bugs are caught late (staging/user reports) as a pattern: public reliability
  commitments require testing infrastructure to deliver, and the gap between
  the commitment and the current coverage is the work to be done.

## Extraction Notes

- Source read in full. Docusaurus blog post, published July 11, 2026, by Ishaan
  Jaffer (CTO) and three AI engineers at LiteLLM. Page was fetched via webfetch
  (markdown format) and all quoted passages were copied character-for-character
  from the rendered page text.
- The page is self-contained. The Appendix lists PR numbers for MCP gateway,
  AI Eng, and Performance sections — these were followed as evidence for the
  claims but are external links, not content to extract.
- The `miner-related-notes.md` candidates file was read before writing
  Cross-References. None of the 10 listed candidates (Google SRE docs, Langfuse
  docs, LiteLLM cost-cutting post) are relevant to this source's claims — the
  candidates matched on broad lexical overlap but not on the specific MCP auth
  or pass-through memory patterns. Cross-references were built from the
  Prospector's overlap list instead.
- `confidence_overall` set to `settled`: the two major fixes (credential
  resolver, pass-through streaming) report completed work with PR numbers; the
  134-fix breakdown is a retrospective count; the only forward-looking item is
  the 95% e2e coverage target (which is appropriately noted as emerging within
  Claim 9). The overall rating reflects that the source's core claims are
  retrospective evidence, not aspirational targets.
- No contradiction issue filed: verified against all existing source notes. The
  overlapping notes (April/May/June townhall, MCP stdio command injection,
  guardrail logging secret exposure) are all compatible with this source's
  claims. The MCP credential resolver is a distinct fix from the stdio allowlist
  (orthogonal vulnerability surfaces). The pass-through memory fix complements
  rather than contradicts the guardrail logging fix (auth-side vs. observability-
  side).
