---
source_url: https://docs.litellm.ai/blog/litellm-rust-launch
source_type: blog-post
title: "Migrating LiteLLM to Rust — Building the Fastest and Litest AI Gateway"
author: "Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-06-22
date_extracted: 2026-07-26
last_checked: 2026-07-26
status: current
confidence_overall: emerging
issue: "#552"
---

# Migrating LiteLLM to Rust — Building the Fastest and Litest AI Gateway

> A detailed engineering deep-dive from LiteLLM's CTO on the architecture and
> staged migration strategy for moving the AI gateway's hot path from Python to
> Rust. Describes the "describe, don't execute" PyO3 bridge pattern where the Rust
> core transforms data without performing any I/O, the 3-beat-per-route migration
> cadence, the V5a→V5b server evolution, and the sidecar architecture for customer
> Python plugins. Includes reproducible benchmarks and prior-art references. This is
> the primary source document whose findings the June townhall post (June 26, 2026)
> summarized at a higher level.

## Source Context

- **Type**: blog-post (vendor engineering deep-dive), tagged `rust`, `ai-gateway`,
  `performance`, `benchmarks`, `reliability`, `engineering`.
- **Author credibility**: High — Ishaan Jaffer is CTO of LiteLLM, the company
  behind the open-source LLM gateway/proxy. This post describes their own
  architecture decisions, benchmarks, and migration strategy with significant
  engineering detail (architectural diagrams, a published benchmark harness,
  per-route rationale). Credibility is high for *what LiteLLM is doing* in its Rust
  migration — the architecture design, the staged rollout plan, and the reproducible
  benchmarks are all verifiable artifacts. The post is the primary engineering
  document that the June 26 townhall post subsequently summarized.
- **Scope**: Covers (1) the "describe, don't execute" architecture principle for the
  Rust core (pure data transformation, no I/O), (2) the PyO3 bridge architecture
  with flag-gated per-provider rollout, (3) the 3-beat-per-route migration cadence
  (prove one provider → roll out all providers → fold route into Rust core), (4) the
  four-stage architecture evolution (pure Python → PyO3 → FastAPI thin shell → pure
  Rust axum), (5) the V5a→V5b server evolution, (6) the sidecar architecture for
  customer Python plugins, (7) reproducible benchmark methodology with harness
  checked into the repo, (8) per-route ordering rationale, (9) two prior-art
  references (Datadog Java→Rust, GitGuardian Rust migration). Does NOT cover:
  other LiteLLM security/stability/reliability work, customer case studies, or
  other product roadmap items.

## Extracted Claims

### Claim 1: The Rust core follows a "describe, don't execute" principle — it never opens sockets, reads secrets, or writes to databases; it only transforms data
- **Evidence**: Explicitly stated in the "How the migration works" section with the
  naming "describe, don't execute" appearing in the Stage 1 architecture diagram.
  The data-transformation-only scope is enumerated: request→provider transform,
  provider response→client response transform, stream chunk transform, token
  counting, error normalization.
- **Confidence**: settled (stated as a design constraint for the Rust core, not a
  future aspiration — the constraint is what enables the staged migration)
- **Quote**: "The core idea is a clean split. We build one Rust core that only
  transforms data: it turns your request into a provider request, turns the provider
  response back, transforms stream chunks, counts tokens, and normalizes errors. It
  never opens a socket, reads a secret, or writes to your database. The host process
  does all of that. That separation is what lets us put Rust into production without
  rewriting the server, because Python keeps doing the I/O while Rust takes over the
  translation."
- **Our assessment**: This is the foundational architectural pattern in the source
  — the principle that a hot-path component can be extracted to another language as
  long as it has zero I/O responsibility. The Rust core becomes a pure function
  (request → transformed request) that the host process calls. This is a
  generalizable pattern for incremental language migration in any gateway or proxy
  where transformations are compute-bound and I/O is the host's job. High signal for
  the guide.

### Claim 2: The PyO3 bridge lets Python do all I/O while Rust does transforms, with flag-gated per-provider rollout and a parity check gate
- **Evidence**: The Stage 1 architecture diagram and its description show the
  flow: client → FastAPI proxy (Python, unchanged) → litellm Python SDK (does all
  I/O) → flag-gated PyO3 bridge → either the Rust core
  (transform_request/transform_response) or the existing Python transforms. A parity
  check enforces identical output before any provider is switched to Rust.
- **Confidence**: settled (architecture is described with a published diagram and
  the parity-check enforcement mechanism is explicit)
- **Quote**: "The Rust core returns a prepared request; the Python SDK still
  performs every byte of I/O."
- **Our assessment**: The flag-gated PyO3 bridge with per-provider parity checking
  is the key incremental-deployment mechanism. It lets LiteLLM ship Rust code to
  production risk-free — if the Rust path produces different output for any provider,
  the flag falls back to the existing Python path. This is a concrete pattern for
  "ship the new implementation behind a feature flag with automatic fallback" that
  generalizes beyond Rust migrations.

### Claim 3: Each route follows a 3-beat cadence: prove one provider, then roll out to all providers, then fold the route into the Rust core
- **Evidence**: Stated explicitly in the "One route at a time, proven in production"
  section with a visual flow diagram showing the repeating cadence: Prove one
  provider → Roll out all providers → Fold route into the Rust core.
- **Confidence**: settled (stated as the migration process the team is executing)
- **Quote**: "The repeating cadence inside Stage 1: 1. Prove one provider, 2. Roll
  out all providers, 3. Fold route into the Rust core."
- **Quote**: "We never flip a whole endpoint at once. For each route we prove one
  provider first, roll it out to every provider on that route, and only then start
  the next route."
- **Our assessment**: A named, transferable pattern for any infrastructure migration
  that spans multiple routes/providers. The key insight is the smallest-risk-first
  ordering: the first provider on a new route is the simplest/smallest (e.g., Mistral
  OCR for the OCR route), proving the mechanism before expanding. This pattern can
  guide operators doing any multi-provider or multi-endpoint migration.

### Claim 4: The migration progresses through four stages from pure Python to pure Rust, each shipped to production before the next begins
- **Evidence**: The four-stage progression is presented with a visual diagram and
  labels: Stage 0 (pure Python SDK + FastAPI proxy, 0% Rust), Stage 1 (Python drives
  Rust transforms via PyO3, transforms + router in Rust), Stage 2 (FastAPI shell
  with entire forwarding path in Rust), Stage 3 (pure Rust axum server with Python
  in sidecar, 100% Rust on hot path).
- **Confidence**: emerging (the earlier stages are in progress; the later stages
  have target dates through Dec 2026)
- **Quote**: "Four stages, each shipped to production before the next begins."
- **Our assessment**: The staged architecture is a textbook incremental-migration
  pattern. Each stage is independently deployable and reduces risk surface before
  the next stage. Stage 1 (PyO3 bridge) is the critical intermediate step — it lets
  Rust transforms run inside the Python process without any server architecture
  change. This is the most generalizable pattern for the guide: when migrating a
  hot path, first extract the pure-transformation logic into the new language behind
  a bridge, then evolve the server architecture to remove the bridge.

### Claim 5: The server evolution follows V5a (FastAPI thin shell, Rust engine) → V5b (pure Rust axum, Python plugins in optional sidecar), removing Python from forwarding before removing PyO3
- **Evidence**: Described in the "Onto a Rust server" section with two architectural
  diagrams. V5a: FastAPI shell terminates HTTP, runs auth/rate-limit/callbacks only;
  entire forwarding path is one PyO3 call into Rust engine. V5b: Rust
  (axum/hyper) runs full server with no PyO3 on hot path; Python plugins in
  optional PyO3 sidecar.
- **Confidence**: emerging (V5a is planned for Dec 2026 target; V5b is the end state)
- **Quote**: "V5a removes Python from forwarding while keeping the shell; V5b
  removes PyO3 from the hot path."
- **Quote**: "Your custom Python plugins (auth, guardrails, callbacks, SSO) keep
  working in an optional sidecar, so nothing breaks."
- **Our assessment**: The two-step server evolution is architecturally nuanced:
  V5a extracts the *business logic* (forwarding) while keeping the *runtime shell*
  in Python, so the server operation (HTTP termination, auth, rate-limit) remains
  unchanged. V5b then replaces the runtime shell while maintaining plugin
  compatibility through a sidecar. This decouples two concerns — business-logic
  extraction vs. runtime migration — allowing independent verification of each.

### Claim 6: The routes move in order of increasing risk — OCR first (no streaming, tiny schema), then /v1/messages (adds streaming), then /chat/completions (largest surface), then router, then full server
- **Evidence**: The "Why this order" section states the rationale for each choice
  and which risk each step retires. The "One route at a time" section enumerates
  the route order with provider-level detail (Mistral OCR first, then /messages,
  then /chat/completions, then major providers by traffic: Azure, Bedrock, Vertex).
- **Confidence**: settled (the route order and its rationale are explicit design
  decisions, not forward-looking predictions)
- **Quote**: "The OCR route retires integration risk on the smallest surface.
  /v1/messages retires streaming risk before the largest parameter set.
  /chat/completions is taken on only after streaming is proven."
- **Quote**: "Every step ships to real users before the next begins, with the parity
  check as the gate."
- **Our assessment**: The order reveals a risk-retirement strategy: retire the
  easiest risk (integration/schema) first, then the next (streaming), then the
  hardest (full parameter surface). Each step's output is proven in production
  before the next step's input is built. This is a replicable sequencing principle
  for any phased migration of a multi-endpoint system.

### Claim 7: The benchmark harness is checked into the repo under benchmark/ with a summarized CSV, making the overhead measurement fully reproducible
- **Evidence**: Stated in the benchmark section and the FAQ. The harness includes "a
  mock upstream, a thin Rust forwarding gateway (axum), the same forwarding path
  running through LiteLLM today (litellm.acompletion over uvicorn), and a load
  client that times each request in microseconds."
- **Confidence**: settled (the harness is published and reproducible by design)
- **Quote**: "The overhead harness (mock, gateway, load client) is checked in next
  to this post under benchmark/, and the summarized numbers are in
  rust_proxy_benchmark_results.csv, so you can reproduce the sub-1ms result. This
  measures the gateway forwarding path (request transform, forwarding, response
  handling), not a full production workload."
- **Our assessment**: Publishing the benchmark harness alongside the blog post is
  unusually transparent for a vendor performance claim. The methodology is clear
  (same upstream/payload for both runtimes, only Python vs Rust varies). The caveat
  that this measures only the "gateway forwarding path" not "a full production
  workload" is honest scoping. This reproducibility standard is a pattern worth
  citing in the guide's discussion of vendor claims evaluation.

### Claim 8: The Rust gateway is deployed with a full non-breaking guarantee — same config.yaml, same database, same client API, same providers
- **Evidence**: Stated in multiple places: the "What you get" section, the "What
  stays the same" section, and the FAQ. Emphasized as "not a v2 and not a rewrite."
- **Confidence**: settled (stated as a design constraint enforced by the staged
  migration approach — the architecture is built so the host process remains
  unchanged during each route migration)
- **Quote**: "This is not a v2 and not a rewrite. There is no new major version to
  migrate to and nothing for you to change. The runtime under the hot path gets
  faster and lighter while your config stays exactly where it is."
- **Quote**: "Nothing you depend on changes. The migration is invisible from the
  outside: Your Python SDK keeps the exact same interface; the same calls now run
  on Rust bindings underneath. Your config.yaml is unchanged. Your database and
  schema are unchanged. Your client API and request/response shapes are unchanged.
  Your providers, routing, and keys are unchanged. You get lower memory and lower
  overhead, and you do nothing to get it."
- **Our assessment**: The non-breaking guarantee is not just a marketing claim — it
  is enforced architecturally by the clean split (Claim 1) and the PyO3 bridge
  (Claim 2). Because the Rust core only transforms data and the Python host still
  owns all I/O and the API surface, the external contract does not change. This
  architectural constraint — "you can't break what you don't touch" — is a
  replicable principle for any hot-path replacement.

### Claim 9: The post cites Datadog's Java→Rust static analyzer migration and GitGuardian's Rust platform migration as prior-art industry references
- **Evidence**: The "References" section at the bottom of the post lists these two
  external sources alongside LiteLLM's own documentation links.
- **Confidence**: settled (cited references; they are external sources that the
  reader can verify independently)
- **Quote**: "How Datadog migrated their static analyzer from Java to Rust" and
  "How GitGuardian migrated the heart of their platform to Rust"
- **Our assessment**: These references situate LiteLLM's Rust migration within a
  recognizable industry pattern (production infrastructure migration from a managed
  runtime to Rust for performance and memory efficiency). They are not LiteLLM's own
  claims but show the migration strategy is influenced by prior successful Rust
  migrations in other infrastructure domains.

### Claim 10: The Rust migration removes GIL concerns for the hot path — request transforms, streaming, and routing run outside the GIL in the end state
- **Evidence**: The FAQ section explicitly addresses the GIL question. The post
  states the gateway is mostly I/O-bound and scales with multiple workers today, but
  the Rust migration renders the question moot for the hot path.
- **Confidence**: emerging (the GIL removal is realized incrementally as each
  route moves to Rust; the full effect depends on reaching Stage 3)
- **Quote**: "The Rust migration removes the question for the hot path: request
  transforms, streaming, and routing run in the Rust core and router, outside the
  GIL, with no first-party Python on the forwarding path in the end state."
- **Our assessment**: A secondary but non-trivial architectural benefit of the
  migration. The GIL is a well-known Python limitation for CPU-bound work, and
  while the gateway is described as mostly I/O-bound, moving the
  compute-intensive operations (transform, parsing, token counting) to Rust
  eliminates a future scalability constraint. The post's honest assessment
  ("the gateway is mostly I/O" → "multiple workers scale today") prevents this
  from being a misleading GIL-fear argument.

## Concrete Artifacts

### Benchmark comparison table (verbatim from the source)

```
| Metric               | Rust gateway | LiteLLM (Python) |
|----------------------|--------------|-------------------|
| Per-request overhead | ~0.05ms      | ~7.5ms            |
| Throughput under load| 6,782 req/s  | 453 req/s         |
| Peak memory under load| 31.7MB      | 358.9MB           |
```

Attribution: https://docs.litellm.ai/blog/litellm-rust-launch, "How fast is the LiteLLM gateway?" section.

### Migration timeline (verbatim from the source)

```
| Target          | What moves to Rust                                                  |
|-----------------|----------------------------------------------------------------------|
| Aug 15, 2026    | litellm.ocr() for Mistral, then all of litellm.ocr(), then the /ocr |
|                 | route                                                                |
| Sep 1, 2026     | Same pattern for /messages, then /chat/completions                   |
| Sep 15, 2026    | The router: load balancing, fallbacks, retries, cooldowns            |
| Dec 1, 2026     | The full server: FastAPI thin shell, then pure Rust (axum)           |
```

Attribution: https://docs.litellm.ai/blog/litellm-rust-launch, "Timeline" section.

### Four-stage migration architecture (verbatim from the source)

```
Stage 0 · Today        | Pure Python SDK + FastAPI proxy | 100% Python | 0% Rust on hot path
Stage 1 · Core in Rust | Python drives Rust transforms    | V0 to V3    | transforms + router
                       | via PyO3                         |             |
Stage 2 · Thin shell   | FastAPI shell, hot path all Rust | V4 to V5a   | ~entire forwarding path
Stage 3 · Pure Rust    | axum server, Python in sidecar   | V5b         | 100%
```

Attribution: https://docs.litellm.ai/blog/litellm-rust-launch, "How the migration works" section (reconstructed from the stage-progression diagram).

### The 3-beat-per-route cadence (verbatim from the source)

```
The repeating cadence inside Stage 1
1. Prove one provider
2. Roll out all providers
3. Fold route into the Rust core
```

Attribution: https://docs.litellm.ai/blog/litellm-rust-launch, "One route at a time, proven in production" section.

### Route ordering rationale (verbatim from the source)

```
- OCR first. Start with Mistral OCR, the smallest surface: no streaming, tiny
  schema, few params.
- /v1/messages next. This adds streaming: SSE parsing, chunk emission, usage
  accounting, token cost.
- /chat/completions after that. The largest surface, taken on only once streaming
  is proven: tools, function calling, multimodal, and the full optional-param
  matrix.
- Major providers. Azure, then Bedrock, then Vertex, by traffic volume.
  Auth-coupled providers get signed headers from the host (boto3 / google-auth
  first, native Rust later). Long-tail providers keep running on Python.
```

Attribution: https://docs.litellm.ai/blog/litellm-rust-launch, "One route at a time, proven in production" section.

### Server evolution: V5a → V5b (architecture descriptions from the source)

```
Stage 2 / V5a — FastAPI as a thin shell:
- FastAPI shell (Python): auth, rate limit, callbacks only — terminates HTTP,
  no forwarding logic
- Rust engine (one PyO3 call): router + core + HTTP + stream + cost — entire
  forwarding hot path

Stage 3 / V5b — Pure Rust server:
- Rust server (axum / hyper): auth, rate limit, router, core, streaming, cost,
  spend — no PyO3 on hot path
- PyO3 sidecar: customer Python plugins, guardrails
- Redis: routing state
- Postgres: spend + config
```

Attribution: https://docs.litellm.ai/blog/litellm-rust-launch, "Onto a Rust server" section.

### Benchmark methodology and harness description (verbatim from the source)

> "We built a small harness: a mock upstream, a thin Rust forwarding gateway (axum),
> the same forwarding path running through LiteLLM today (litellm.acompletion over
> uvicorn), and a load client that times each request in microseconds."

> "The overhead harness (mock, gateway, load client) is checked in next to this post
> under benchmark/, and the summarized numbers are in
> rust_proxy_benchmark_results.csv, so you can reproduce the sub-1ms result."

Attribution: https://docs.litellm.ai/blog/litellm-rust-launch, "How fast is the LiteLLM gateway?" section.

### References section from the source (verbatim)

> - How Datadog migrated their static analyzer from Java to Rust
> - How GitGuardian migrated the heart of their platform to Rust
> - LiteLLM AI Gateway, full feature overview
> - Load balancing and routing across 100+ LLM providers

Attribution: https://docs.litellm.ai/blog/litellm-rust-launch, "References" section.

## Cross-References

- **Corroborates**:
  - `docs-google-sre-prodcast-01-05-client-transparent-migrations.md` **Claim 1**
    (client transparency is NOT byte-for-byte matching but source and target behaving
    identically for all user-observable aspects of existing traffic) — LiteLLM's
    Rust migration uses the same principle: "same config.yaml, same database, same
    client API, same providers" with parity-check gates enforcing output equivalence
    before each route promotion. LiteLLM's approach is a concrete implementation of
    the client-transparency thesis where the observable interface (API contract) is
    preserved while the implementation (Python→Rust) changes underneath.

- **Contradicts**: None. The triage guidance correctly identifies the relationship:
  this post is the primary engineering deep-dive that the June townhall note
  (`blog-litellm-june-townhall-updates.md`) summarized at a higher level. The
  benchmark numbers align within expected rounding (~0.05ms vs 0.05ms, 6,782 vs
  6,782 req/s, 31.7MB vs 32MB). No contradiction issue filed.

- **Extends**:
  - `blog-litellm-june-townhall-updates.md` — that note summarized the Rust
    benchmarks and staged rollout at a bullet-list level (Claims 3, 4, 12). This
    post provides the architectural design rationale that the townhall only alluded
    to: the "describe, don't execute" principle (Claim 1), the PyO3 bridge with
    flag-gated per-provider parity checking (Claim 2), the 3-beat-per-route cadence
    (Claim 3), the V5a→V5b server evolution (Claim 5), the route ordering rationale
    (Claim 6), and the reproducible benchmark methodology (Claim 7). The two notes
    together form a primary-source + summary pair: this post is what the townhall
    condensed.
  - `blog-litellm-april-townhall-updates.md` **Claim 9** (10k+ RPS uptime /
    latency overhead investigation as a reliability investment) — the Rust migration
    architecture in this note is the concrete engineering response that April's
    aspirational target set in motion. This note shows *how* LiteLLm is achieving
    the performance gains — not just the benchmarks but the architecture that
    produces them.
  - `blog-litellm-fastapi-middleware-performance.md` — that note (Feb 2026)
    documented a ~74% throughput improvement from replacing `BaseHTTPMiddleware`
    with pure ASGI in the Python proxy. This Rust launch post documents the next
    architectural step: moving the entire forwarding path out of Python into Rust.
    Together they form a trajectory: Python-level optimization (Feb) → Rust core
    (Jun) → pure Rust server (Dec target).
  - `blog-litellm-agents-are-the-new-llms.md` **Claim 9** (LiteLLM Agent Platform
    is "a Rust-based AI Gateway and Agent Control Plane") — this post provides the
    architecture and migration strategy behind the "Rust-based AI Gateway" claim,
    moving it from a stated architecture choice to a detailed implementation plan
    with benchmarks.

- **Novel**: First source note to introduce:
  - The "describe, don't execute" / "no I/O" Rust core principle as an architectural
    pattern for incremental language migration in an LLM gateway.
  - The PyO3 bridge architecture with flag-gated per-provider parity checking as a
    deployment mechanism for swapping Python transforms with Rust transforms.
  - The 3-beat-per-route migration cadence (prove one provider → roll out all
    providers → fold route into Rust core).
  - The V5a→V5b two-step server evolution (FastAPI thin shell → pure Rust axum with
    Python sidecar).
  - The per-route risk-ordering rationale (OCR first → /v1/messages →
    /chat/completions → router → full server) with specific risk retirement at each
    step.
  - The sidecar architecture for keeping customer Python plugins operational during
    a language migration of the hot path.
  - A reproducible benchmark harness for gateway overhead measurement published
    alongside the vendor's performance claims.
  - Prior-art references from Datadog and GitGuardian for Rust migration patterns
    in production infrastructure.

## Guide Impact

- **Chapter 02 (LLM Gateway Architecture)**: Add the "describe, don't execute"
  architectural pattern (Claim 1) as a foundational design principle for LLM
  gateway hot-path components. The key insight is that a hot-path transformation
  component should be a pure function (no I/O) so it can be migrated to a
  higher-performance language without touching the server process. Add the PyO3
  bridge with flag-gated parity checking (Claim 2) as a concrete deployment pattern
  for swapping gateway transforms — ship the new implementation behind a feature
  flag with automatic fallback when output doesn't match. Add the sidecar
  architecture (Claim 5) as a pattern for maintaining plugin compatibility during
  a hot-path language migration.

- **Chapter 04 (Production Deployments)**: Add the 3-beat-per-route migration
  cadence (Claim 3) and the per-route risk-ordering strategy (Claim 6) as replicable
  patterns for multi-endpoint infrastructure migrations. The principle — retire one
  risk dimension at a time, prove each in production before the next begins — is
  generalizable beyond Rust migrations to any provider-addition or endpoint-migration
  scenario. Add the four-stage architecture progression (Claim 4) as a deployment
  evolution template: extract pure logic → bridge into new language → thin shell →
  full rewrite with plugin sidecar.

- **Chapter 06 (Performance / Reliability Engineering)**: Add the reproducible
  benchmark methodology (Claim 7) as a standard for evaluating vendor gateway
  performance claims — a published harness with mock upstream, same-payload testing
  across runtimes, and honest scoping ("gateway forwarding path, not full production
  workload"). Add the non-breaking guarantee architecture (Claim 8) as a template
  for how to make a significant runtime change invisible to consumers: because the
  Rust core only transforms data and leaves the I/O surface unchanged, the external
  contract doesn't change.

- **Chapter 05 (LLM Ops Reliability / Capacity)**: Add the GIL-removal benefit
  (Claim 10) as a secondary consideration for gateway performance — the Rust
  migration eliminates GIL contention for CPU-bound transform operations on the hot
  path, even though the gateway is primarily I/O-bound. Add the memory improvement
  trajectory (359MB→32MB→65MB target) as a reference range for gateway memory
  profiling in capacity planning.

## Extraction Notes

- Source read in full. Docusaurus blog post at
  `https://docs.litellm.ai/blog/litellm-rust-launch`, published June 22, 2026, by
  Ishaan Jaffer (CTO, LiteLLM). Page was fetched via direct HTTP (curl) with
  HTML-to-text extraction; all quoted passages were copied character-for-character
  from the rendered page text.
- The page is self-contained. The two prior-art references (Datadog, GitGuardian)
  are external links cited for context — they were identified in the extraction but
  not followed as sub-pages per MINER.md §1 since they are external sources, not
  LiteLLM's own content. The LiteLLM feature overview and routing docs links are
  LiteLLM product documentation but not substantive sub-pages requiring extraction.
- `confidence_overall` set to `emerging` consistent with other LiteLLM vendor blog
  notes. Most architectural claims (Claims 1–3, 6, 8) are settled — they describe
  design decisions already in effect. The migration timeline and server evolution
  targets (Claims 4, 5) are forward-looking with target dates through Dec 2026,
  which pulls the overall confidence down. The benchmark data (Claim 7 concrete
  numbers, Claim 10 GIL analysis) is individually settled, but the overall
  migration is still in progress.
- The triage comments identified this post as the primary source that the June 26
  townhall post summarized (published 4 days earlier, June 22). The extraction
  focused on the architectural design rationale absent from the townhall note and
  treated the benchmark numbers and timeline as already captured in
  `blog-litellm-june-townhall-updates.md`.
- All miner-related-notes.md candidates were evaluated: 10 candidates, of which 3
  were cited (docs-google-sre-prodcast-01-05 for client-transparency corroboration,
  blog-litellm-june-townhall-updates and blog-litellm-april-townhall-updates for
  extends) and 7 were dismissed as unrelated (docs-google-sre-prodcast-04-09,
  docs-langfuse-mcp-server, docs-google-sre-reliable-product-launches,
  docs-langfuse-security-and-guardrails, docs-google-sre-prodcast-04-05-furino-slos,
  docs-datadog-llm-observability, docs-google-sre-prodcast-03-07-retail-gaming,
  docs-google-sre-handling-overload). See miner-related-notes.md for candidate
  details — this file was read but not committed.
- No contradiction issue filed: verified against all existing source notes. The
  overlapping LiteLLM notes (June townhall, April townhall, FastAPI middleware,
  agents-as-new-LLMs) are all compatible — the June townhall is a higher-level
  summary of this post, the April townhall motivated the performance work, the
  FastAPI middleware note is a prior optimization phase, and the agents-as-new-LLMs
  note references the Rust gateway at a strategic level. The client-transparency
  prodcast note corroborates the non-breaking guarantee approach but does not
  contradict.
