---
source_url: https://docs.litellm.ai/blog/sub-millisecond-proxy-overhead
source_type: blog-post
title: "Achieving Sub-Millisecond Proxy Overhead"
author: "Alexsander Hamir (Performance Engineer, LiteLLM), Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-02-02
date_extracted: 2026-08-01
last_checked: 2026-08-01
status: current
confidence_overall: emerging
issue: "#711"
---

# Achieving Sub-Millisecond Proxy Overhead

> LiteLLM's first articulation (Feb 2, 2026) of its Q1 performance
> architecture: an *optional sidecar* that owns the hot path (request
> forwarding, connection reuse/pooling, timeout/limit enforcement,
> high-frequency metric aggregation) while Python stays the control plane
> (validation/normalization, model & provider selection, callbacks). Also
> defines the proxy-overhead metric, its A/B measurement methodology
> (same workload, identical QPS, all processes on one machine), and the
> dated QPS baseline (failed at ~1,000 QPS under the TensorZero benchmark
> → now 1,000 QPS no failures, scaling to 5,000 QPS on a single 4-CPU/
> 8-GB instance). The sidecar is explicitly an optimization, not a
> requirement, as of the publication date.

## Source Context

- **Type**: blog-post (vendor architecture/performance-engineering post),
  tagged `performance`, `architecture`. Published on LiteLLM's docs-site blog.
- **Author credibility**: High — co-authored by LiteLLM's Performance Engineer
  (Alexsander Hamir), CEO (Krrish Dholakia), and CTO (Ishaan Jaffer). The post
  describes their own Q1 performance target, their own measurement approach, and
  their own architecture decision. Credibility is high for *what LiteLLM is doing
  and targeting*; the performance baselines are vendor-reported and not published
  with a reproducible harness in this post (contrast: the Rust-launch post, which
  checked a benchmark harness into the repo, and the middleware post, which
  published a benchmark script).
- **Scope**: Covers (1) the definition of "proxy overhead," (2) the measurement
  methodology (A/B latency delta at identical QPS on one machine), (3) the dated
  QPS baseline and its history, (4) the optional sidecar architecture and the
  control-plane/hot-path responsibility split, (5) the optionality/rollout
  principle, (6) the forward-looking hardware goal (1-CPU/2-GB instance). Does
  NOT cover: any actual measured sub-millisecond number (no overhead value is
  reported — the post states the target and the QPS baselines), implementation
  details of the sidecar, or code/config artifacts. The post is prose plus one
  architecture diagram.

## Extracted Claims

### Claim 1: LiteLLM's Q1 2026 performance target is sub-millisecond proxy overhead on a single 4-CPU/8-GB-RAM instance
- **Evidence**: Direct statement of the target in the Introduction, framed as
  the Q1 goal the architecture direction serves.
- **Confidence**: settled (stated target, dated to Q1 2026)
- **Quote**: "Our Q1 performance target is to aggressively move toward sub-millisecond proxy overhead on a single instance with 4 CPUs and 8 GB of RAM, and to continue pushing that boundary over time."
- **Our assessment**: A concrete, dated performance target. Note that the post
  sets the target but reports *no measured sub-millisecond number* — it gives
  QPS baselines and the target, not a measured latency delta. The guide should
  treat "sub-millisecond" as an announced goal, not a demonstrated result, as of
  the publication date.

### Claim 2: "Proxy overhead" is defined as the latency LiteLLM itself introduces, independent of the upstream provider
- **Evidence**: One-sentence definition opening the Introduction.
- **Confidence**: settled (definitional statement)
- **Quote**: "Proxy overhead refers to the latency introduced by LiteLLM itself, independent of the upstream provider."
- **Our assessment**: A clean operational definition — this is the metric being
  optimized. It separates the gateway's contribution from provider latency, which
  is the prerequisite for the A/B methodology in Claim 3. Useful for the guide's
  capacity/latency vocabulary: "proxy overhead" should always be defined this way.

### Claim 3: Proxy overhead is measured by running the same workload directly against the provider and through LiteLLM at identical QPS, with the load generator, LiteLLM, and a mock LLM endpoint all on the same machine so the latency delta excludes network noise
- **Evidence**: The methodology description in the Introduction gives the exact
  setup: identical QPS (example 1,000), latency delta comparison, all three
  components on the same machine.
- **Confidence**: settled (described methodology; the approach is sound and the
  noise-elimination rationale is explicit)
- **Quote**: "To measure it, we run the same workload directly against the provider and through LiteLLM at identical QPS (for example, 1,000 QPS) and compare the latency delta. To reduce noise, the load generator, LiteLLM, and a mock LLM endpoint all run on the same machine, ensuring the difference reflects proxy overhead rather than network latency."
- **Our assessment**: A reusable, sound proxy-overhead measurement pattern. Two
  design choices are worth generalizing: (1) same workload + identical QPS makes
  the delta attributable to the proxy, and (2) a mock LLM endpoint on the same
  machine removes network latency as a confound. This pairs well with the existing
  "Metrics without a unit are noise" material in Ch05 — a proxy-overhead figure is
  only meaningful with its measurement setup stated. Caveat: the post describes
  the methodology but does not publish the harness or a measured result (unlike
  the Rust-launch post), so the *method* is settled but the *numbers* in this post
  are not independently reproducible from it.

### Claim 4: Under the benchmark originally conducted by TensorZero, LiteLLM previously failed at around 1,000 QPS
- **Evidence**: One-sentence historical statement in the "Where We're Coming From"
  section, attributing the benchmark to TensorZero.
- **Confidence**: settled (stated historical fact by the vendor about their own
  system)
- **Quote**: "Under the same benchmark originally conducted by TensorZero, LiteLLM previously failed at around 1,000 QPS."
- **Our assessment**: This anchors the improvement narrative. The failure mode is
  unspecified ("failed at around 1,000 QPS" — timeouts, errors, or latency SLOs
  are not stated). The reference to the TensorZero benchmark is external context;
  the post does not link or describe it. Treat as a vendor-stated historical
  baseline, not an independently measured one.

### Claim 5: LiteLLM can now be stress-tested at 1,000 QPS with no failures and scales to 5,000 QPS without failures on a single 4-CPU/8-GB-RAM instance
- **Evidence**: The current-baseline statement in "Where We're Coming From,"
  directly contrasting with Claim 4.
- **Confidence**: settled (vendor-stated current capability; not independently
  reproduced in this post)
- **Quote**: "Today, LiteLLM can be stress-tested at 1,000 QPS with no failures and can scale up to 5,000 QPS without failures on a 4-CPU, 8-GB RAM single instance setup."
- **Our assessment**: The dated QPS baseline this post is anchored on — roughly a
  5x improvement over the ~1,000 QPS failure baseline. It is a single-vendor,
  single-scenario measurement with no published harness in this post, so the guide
  should cite it as a *dated vendor-measured baseline* with the hardware and
  same-machine setup attached, not as an absolute capacity ceiling. Consistent with
  the 10k+ RPS uptime target the April townhall later set (this 5k baseline predates
  that target — same direction, no conflict).

### Claim 6: Per-request work becomes expensive inside the Python process at higher request rates, so LiteLLM chose an optional sidecar architecture rather than rewriting the system or adding complex deployment requirements
- **Evidence**: The Design Choice section states the tradeoff and the decision
  explicitly.
- **Confidence**: settled (stated design decision)
- **Quote**: "At higher request rates, however, certain classes of work become expensive when executed inside the Python process on every request. Rather than rewriting LiteLLM or introducing complex deployment requirements, we adopt an optional sidecar architecture."
- **Our assessment**: The core architectural rationale: per-request Python work
  does not amortize at high QPS, and the chosen remedy is extraction (sidecar), not
  rewrite. This is the same motivation family as the middleware micro-optimization
  post (per-request overhead) and the later Rust migration. It is the generalizable
  gateway-architecture pattern: when the hot path dominates, carve it out rather
  than rewrite the whole system.

### Claim 7: The architecture splits responsibilities — Python is the control plane (request validation/normalization, model & provider selection, callbacks/integrations) while the sidecar owns the hot path (request forwarding, connection reuse/pooling, timeouts/limits, high-frequency metric aggregation)
- **Evidence**: The two enumerated ownership lists in the Design Choice section,
  closed by the explicit split statement.
- **Confidence**: settled (stated architecture with the specific division of
  responsibilities)
- **Quote**: "This separation allows each component to focus on what it does best: Python acts as the control plane, while the sidecar handles the hot path."
- **Our assessment**: The guide-worthy claim — a named control-plane/hot-path
  split with specific responsibilities on each side. The division is concrete:
  Python keeps the low-QPS, logic-heavy work (validation, selection, callbacks);
  the sidecar owns the per-request hot path (forwarding, pooling, timeouts,
  high-frequency metrics). This Feb 2026 post is the *first articulation* of the
  split that the June 2026 Rust-launch post later executed (see Cross-References).
  Note the sidecar's role in this post is the hot-path accelerator, whereas in the
  Rust end-state the sidecar hosts Python plugins — the same term, different
  component across the architecture's evolution (see Extraction Notes).

### Claim 8: The sidecar is intentionally optional so it can ship incrementally and be validated under real-world workloads before becoming a hard dependency — it is bundled, auto-started, requires no additional infrastructure, and can be disabled entirely
- **Evidence**: The entire "Why the Sidecar Is Optional" section states the
  rollout principle and the self-hosting guarantee.
- **Confidence**: emerging (stated design intent / dated rollout status, explicitly
  "as of today")
- **Quote**: "This allows us to ship it incrementally, validate it under real-world workloads, and avoid making it a hard dependency before it is fully battle-tested across all LiteLLM features."
- **Quote**: "Just as importantly, this ensures that self-hosting LiteLLM remains simple. The sidecar is bundled and started automatically, requires no additional infrastructure, and can be disabled entirely. From a user's perspective, LiteLLM continues to behave like a single service."
- **Our assessment**: A rollout principle for shipping performance hot-paths
  without breaking deployability: bundle + auto-start + disableable keeps the
  product a single service while the new component is proven incrementally. This is
  the same incremental-shipping family as the Rust post's flag-gated parity rollout.
  Marked `emerging` because it is a dated status ("as of today" / "not a hard
  dependency before it is fully battle-tested"), not a settled architectural law —
  it could change as the sidecar matures.

### Claim 9: As of the publication date, the sidecar is an optimization, not a requirement
- **Evidence**: Direct one-sentence status statement closing the "Why the Sidecar
  Is Optional" section.
- **Confidence**: emerging (explicitly date-sensitive)
- **Quote**: "As of today, the sidecar is an optimization, not a requirement."
- **Our assessment**: This is the operative takeaway for guide advice: at the time
  of writing, operators do not need the sidecar; it is additive. The Prospector's
  triage correctly flagged this as an emerging claim — a "not a requirement" status
  is exactly the kind of statement that flips as an architecture matures. The guide
  should present the sidecar as an available optimization pattern, not a mandatory
  dependency, citing this dated status.

### Claim 10: LiteLLM targets the same sub-millisecond performance on modest hardware such as a 1-CPU/2-GB-RAM instance
- **Evidence**: The conclusion restates the hardware goal as part of keeping
  deployment/self-hosting simple.
- **Confidence**: emerging (forward-looking goal, not yet demonstrated)
- **Quote**: "we establish a foundation for making LiteLLM permanently fast over time—even on modest hardware such as a 1-CPU, 2-GB RAM instance, while keeping deployment and self-hosting simple"
- **Our assessment**: A forward-looking capacity-planning signal: the architecture
  is intended to keep the gateway cheap to deploy (1-CPU/2-GB) rather than
  requiring big instances. Relevant as a *goal* for gateway operators evaluating
  deployment cost, not as a demonstrated capability on that hardware class.

### Claim 11: LiteLLM frames sub-millisecond overhead as requiring architectural change rather than a single optimization, and as a long-term investment to make the gateway "permanently fast"
- **Evidence**: The conclusion states the framing; the Design Choice section calls
  it a long-term investment.
- **Confidence**: emerging (strategic framing / forward-looking commitment)
- **Quote**: "Sub-millisecond proxy overhead is not achieved through a single optimization, but through architectural changes."
- **Quote**: "This architectural change is how we intend to make LiteLLM permanently fast. While it supports our near-term performance targets, it is a long-term investment."
- **Our assessment**: The strategic framing that ties the sidecar architecture to
  the Q1 target. It signals that the performance program is architectural (matching
  the trajectory that led to the Rust migration four months later), not a series of
  micro-optimizations. Useful context for the guide so readers do not expect a
  single-tweak silver bullet.

## Concrete Artifacts

The post is prose-only (no code, config, or benchmark tables). The one concrete
artifact is the control-plane/hot-path responsibility split, reproduced verbatim
from the Design Choice section (the source renders this as an architecture
diagram with these text lists):

```
Python continues to own:
- Request validation and normalization
- Model and provider selection
- Callbacks and integrations

The sidecar owns performance-critical execution, such as:
- Efficient request forwarding
- Connection reuse and pooling
- Enforcing timeouts and limits
- Aggregating high-frequency metrics

This separation allows each component to focus on what it does best:
Python acts as the control plane, while the sidecar handles the hot path.
```

Attribution: https://docs.litellm.ai/blog/sub-millisecond-proxy-overhead,
"Design Choice" section.

No other concrete artifacts (metrics tables, code examples, error messages) appear
in the source.

## Cross-References

- **Corroborates**:
  - `blog-litellm-fastapi-middleware-performance.md` **Claim 7** — that sibling
    post (Feb 7, 2026, same authors) reports "about a 30% reduction in proxy
    overhead over the past two weeks" across its middleware optimizations. This
    post uses the same "proxy overhead" definition (Claim 2) as the thing being
    reduced. Same metric, same goal, different mechanisms.
  - `blog-litellm-april-townhall-updates.md` **Claim 9** — April's reliability
    investment target ("Increase uptime for 10k+ RPS scenarios. Investigate
    latency overhead for long-running Claude Code requests") is a *later* target
    set on top of this post's Feb baseline (1,000 QPS no failures, up to 5,000
    QPS). The 10k+ target is in the same direction as the 5k baseline, not a
    contradiction. The Ch05 guide section "Latency overhead of long-running agent
    requests" already cites the April claim; this post provides the proxy-overhead
    measurement and architectural context beneath it.

- **Contradicts**: None. No contradiction issue filed. Verified against the
  existing notes: no source note asserts that proxy overhead is negligible, that
  Python-per-request work is fine at high QPS, or that a sidecar is unnecessary.
  One evolution worth flagging for the Smith (not a filed contradiction — see
  Extraction Notes): this Feb post puts the *hot path in the sidecar* ("Python
  acts as the control plane, while the sidecar handles the hot path"), while the
  Rust-launch end-state (V5b) puts the hot path in the Rust main server with
  *Python plugins in the optional sidecar*. Same term "sidecar," different
  component, at different phases of an explicitly evolving architecture — the two
  claims are time-separated, so they do not oppose each other at the same snapshot.

- **Extends**:
  - `blog-litellm-rust-launch.md` (issue #552) — **Claim 5** (V5a→V5b server
    evolution; in the V5b end-state, customer Python plugins — auth, guardrails,
    callbacks, SSO — keep working in an optional PyO3 sidecar). This note is the
    *origin* of that
    sidecar direction: it is the first articulation (Feb 2, 2026) of the
    control-plane/hot-path split as a Q1 performance target; the Rust post (June
    22, 2026) documents the later execution of the same architecture direction.
    Together the two notes let the guide trace the sidecar pattern from framing to
    implementation. This note adds the *rationale* and the *dated baseline*; the
    Rust note adds the migration mechanics and measured per-request overhead
    (~0.05ms Rust vs ~7.5ms Python).
  - `blog-litellm-fastapi-middleware-performance.md` (issue #324) — the sibling
    performance post (Feb 7, 2026). Its Extraction Notes explicitly flagged this
    post as warranting its own source-note issue. The middleware post is
    per-request micro-optimization *inside* the Python process; this post is the
    architectural direction (extract the hot path to a sidecar). Complementary,
    same overall proxy-overhead reduction program.
  - `blog-litellm-observatory.md` (issue #551) — published the same week (Feb 6,
    2026) by the same Performance Engineer + CEO + CTO, it describes long-running
    release-validation load testing (3-hour tests, <1% failure threshold). Both
    are performance-measurement/validation approaches for the same proxy; this
    post's same-machine A/B latency-delta method measures *overhead*, the
    Observatory measures *sustained reliability under load*. Different measurement
    targets, same vendor program.
  - `blog-litellm-april-townhall-updates.md` (issue #198) — **Claim 9** (10k+
    RPS uptime target, latency-overhead investigation) is the reliability-target
    context that this post's performance work feeds; this post shows the
    architectural response (sidecar split + dated QPS baseline) beneath those
    targets.

- **Novel**: First source note in the corpus to introduce:
  - The control-plane/hot-path split as a named design pattern for LLM gateways
    with the *specific responsibility division* (Python: validation/normalization,
    model & provider selection, callbacks; sidecar: forwarding, connection
    reuse/pooling, timeout/limit enforcement, high-frequency metric aggregation).
    The Rust note's sidecar is the later, narrower execution (Python-plugin host in
    the end-state); this note is the origin framing of the hot-path/control-plane
    split itself.
  - The proxy-overhead measurement methodology as a reusable technique: same
    workload direct vs. through the proxy at identical QPS, load generator + proxy
    + mock LLM on the same machine, latency delta = overhead.
  - The dated TensorZero-baseline contrast (failed at ~1,000 QPS → 1,000 QPS no
    failures → 5,000 QPS) as a documented gateway-capacity improvement trajectory.
  - The "optional sidecar" rollout principle for shipping perf hot-paths
    incrementally (bundled, auto-started, disableable, self-hosting stays one
    service) without breaking deployability.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — Cost, capacity, and fallback patterns /
  Evaluation and measurement methodology**:
  - Add the proxy-overhead measurement methodology (Claim 3) under the existing
    "Evaluation and measurement methodology" section, alongside "Metrics without a
    unit are noise": a proxy-overhead figure is only meaningful with its setup
    stated — same workload at identical QPS against a mock upstream, all processes
    on one machine, latency delta = overhead. This is a reusable baseline technique
    for any LLM gateway capacity test.
  - Add the optional sidecar / control-plane-hot-path split (Claims 6, 7) as a
    gateway capacity/architecture pattern in the capacity section: when per-request
    Python work becomes expensive at high QPS, extract the hot path (forwarding,
    pooling, timeouts, high-frequency metrics) to a sidecar while Python keeps
    validation/normalization, selection, and callbacks. This is the architectural
    response to the already-cited 10k+ RPS uptime target and the "latency overhead
    of long-running agent requests" rule (both currently cite the April townhall
    note only).
  - Add the dated QPS baseline (Claim 4, Claim 5) as a *reference range* for
    gateway capacity planning: failed ~1,000 QPS (TensorZero benchmark) → 1,000
    QPS no failures → 5,000 QPS on a single 4-CPU/8-GB instance (Feb 2026), with
    sub-millisecond overhead as a target, not a measured result. Present it as
    dated vendor-measured data with the hardware and same-machine setup attached,
    not as an absolute ceiling. Note the 10k+ RPS April target is the later,
    higher bar.
  - Add the forward-looking hardware goal (Claim 10) as emerging context for
    gateway deployment-cost planning (sub-millisecond overhead targeted on a
    1-CPU/2-GB instance) — a goal, not a demonstrated capability.

- **Chapter 00 (Principles)**:
  - Add the "optional sidecar" rollout principle (Claims 8, 9) as a general
    pattern: ship performance hot-paths incrementally by bundling + auto-starting +
    making the new component disableable, so self-hosting stays a single service
    and the component is proven under real workloads before it becomes a hard
    dependency. This complements the Rust note's flag-gated parity rollout under
    the same "prove before you commit" principle already in Ch00.

## Extraction Notes

- Source read in full. Docusaurus blog post at
  `https://docs.litellm.ai/blog/sub-millisecond-proxy-overhead`, published
  February 2, 2026, by Alexsander Hamir (Performance Engineer), Krrish Dholakia
  (CEO), and Ishaan Jaffer (CTO). The page was fetched via direct HTTP (curl) with
  HTML-to-text extraction; all quoted passages were copied character-for-character
  from the rendered page text (verified against the extracted text, including the
  em dash in the Claim 10 quote).
- The post is self-contained prose with one architecture diagram; no code/config
  snippets, benchmark tables, or error messages appear. The sidebar links to
  adjacent LiteLLM posts (e.g., "Benchmarking the LiteLLM Rust AI Gateway") were
  not followed — they are adjacent posts, not sub-pages requiring extraction, and
  the Rust post is already a separate source note (issue #552).
- `confidence_overall` set to `emerging`, matching the sibling LiteLLM blog notes.
  The definitional and design-decision claims (Claims 2, 4, 6, 7) are settled as
  statements about LiteLLM's own system, and the methodology (Claim 3) is sound,
  but the post reports **no measured sub-millisecond overhead number** and its QPS
  baselines (Claims 4, 5) are vendor-reported without a published harness in this
  post (unlike the Rust and middleware posts). The optionality status (Claims 8,
  9) and forward-looking goals (Claims 10, 11) are explicitly date-sensitive. This
  mix under one note lands at `emerging`.
- Sidecar-meaning evolution, flagged for the Smith (not filed as a contradiction
  issue): this Feb post describes the sidecar as the component that *handles the
  hot path* while Python is the control plane; the June Rust post's end-state
  (V5b) places the hot path in a pure-Rust main server with *Python plugins* in
  the optional sidecar. The term "sidecar" is applied to different components at
  different phases of an architecture the Feb post itself calls evolving ("we will
  continue sharing benchmarks and updates as the architecture evolves"). These are
  time-separated claims, not opposing claims at the same snapshot, so no
  contradiction issue was filed; the guide should present the sidecar pattern as
  evolving from "hot-path accelerator" (Feb framing) to "Python-plugin host in a
  Rust end-state" (June implementation) rather than as a single fixed design.
- All miner-related-notes.md candidates were evaluated (10 candidates): 1 cited
  (blog-litellm-april-townhall-updates) and 9 dismissed as unrelated:
  blog-litellm-save-claude-code-costs (cost-cutting features, not proxy
  architecture), docs-langfuse-mcp-server (unrelated vendor), docs-google-sre-
  prodcast-04-09-ai-agents (agent spectrum/guardrails), docs-langfuse-security-
  and-guardrails (security scanners), docs-google-sre-reliable-product-launches
  (launch process), docs-google-sre-prodcast-04-05-furino-slos (SLOs), docs-google
  -sre-prodcast-03-07-retail-gaming (retail/gaming SRE), blog-litellm-may-townhall
  -updates (security/versioning townhall), failure-litellm-bedrock-invoke-prompt-
  cache (cache-invalidation incident — different mechanism from hot-path
  overhead). See miner-related-notes.md for candidate details — this file was read
  but not committed. In addition, the Prospector's triage comments named three
  overlapping notes that are not in the lexical candidates list
  (blog-litellm-fastapi-middleware-performance, blog-litellm-rust-launch,
  blog-litellm-observatory); all three were read in full and cited above.
- No contradiction issue filed: no existing source note opposes any claim in this
  post, and the two nearby candidate contradictions (sidecar-role evolution vs.
  Rust note; 5k baseline vs. April 10k+ target) are time-separated or directional
  differences, not conflicting claims at the same snapshot. Open contradiction
  issues and CONTRADICTIONS.md contain no entries on LiteLLM proxy overhead or the
  sidecar architecture.
