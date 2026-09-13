---
source_url: https://docs.litellm.ai/docs/observability/supabase_integration
source_type: docs
title: "Supabase — liteLLM Documentation"
author: "LiteLLM (community-maintained docs page)"
date_published: unknown (living vendor docs; current as of 2026-09-13)
date_extracted: 2026-09-13
last_checked: 2026-09-13
status: current
confidence_overall: emerging
issue: "#1285"
---

# Supabase — liteLLM Documentation

> A thin, community-maintained vendor tutorial documenting LiteLLM's Supabase
> integration: a self-hosted Postgres `request_logs` table that both
> `success_callback` and `failure_callback` write to, pairing `total_cost`,
> `response_time`, `status`/`error`, and `end_user` in one per-request row.
> Its durable value is the fixed table schema and the narrow callback surface
> (`success_callback` / `failure_callback` / `modify_integration` / per-request
> `user=` attribution) — not any operational reliability property, none of which
> the page demonstrates.

## Source Context

- **Type**: docs (vendor integration page, LiteLLM × Supabase)
- **Author credibility**: Low-to-medium. The page carries LiteLLM's standard
  community-maintained disclaimer:
  > "This is community maintained, Please make an issue if you run into a bug"
  Config snippets are therefore "the documented wiring," not "the wiring that
  has survived production." Supabase itself contributes nothing to the page —
  it is used purely as a self-hosted Postgres sink; the interesting content is
  the request-log table shape, not the vendor.
- **Scope**: Covers the `request_logs` DDL, the two-line success/failure callback
  wiring, env vars (`SUPABASE_URL` / `SUPABASE_KEY`), a complete good-and-bad-call
  example, per-request end-user attribution via the `user=` kwarg, and table-name
  override via `litellm.modify_integration`. Does **NOT** cover: proxy
  `config.yaml` (this is SDK-level wiring), buffering/retry/drop semantics when
  the sink is unreachable or slow, log-loss behavior, write-volume or retention
  guidance, index design, redaction/RLS guidance for the raw payload columns, or
  metrics/SLO guidance. The page has zero failure-mode discussion.
- **Extraction note**: Extracted from the **canonical** URL
  (`/docs/observability/supabase_integration`) per the triage reconciliation
  precedent set on #1284. The submitted alias (`/observability/supabase_integration`)
  serves a superseded legacy build — older DDL (no `status` column, no
  `litellm_call_id`), `gpt-3.5-turbo` example, and the deprecated
  `litellm.identify({"end_user": ...})` call instead of the `user=` kwarg. The
  legacy content is noted where it differs but nothing in this note's Quotes or
  Artifacts relies on it.

## Extracted Claims

### Claim 1: LiteLLM's Supabase integration is a dual-outcome request ledger — both `success_callback` and `failure_callback` write to the same `request_logs` table, so successful and failed requests land in one sink
- **Evidence**: The intro and "Use Callbacks" section show exactly two enabled
  callbacks with no routing between them: `litellm.success_callback=["supabase"]`
  and `litellm.failure_callback=["supabase"]`. The completed example makes one
  good and one bad call to exercise both paths.
- **Confidence**: settled (factual description of the documented config surface)
- **Quote**: "In this case, we want to log requests to Supabase in both scenarios - when it succeeds and fails."
- **Our assessment**: This is the pattern worth distinguishing from the LiteLLM
  callbacks *overview* surface, which typically routes success payloads to
  analytics backends and failure payloads to error trackers. Routing both
  outcomes to one table is what makes a self-built error-rate and latency SLI
  queryable from a single ledger (the `error`, `response_time`, and `status`
  columns all sit on the same row). The page makes neither that observation nor
  any reliability claim — it simply wires both sinks to one table.

### Claim 2: The `request_logs` schema is fixed and pairs per-request cost, latency, and outcome in one row — `model`, `messages`, `response`, `end_user`, `status`, `error`, `response_time`, `total_cost`, `additional_details`, and a `litellm_call_id text unique` dedup key — and the only overridable part of the integration is the table name, not the column names
- **Evidence**: The "Create a supabase table" section gives the full Postgres DDL
  (Artifact 1), and the constraint that accompanies it.
- **Confidence**: settled (the DDL and the "don't change the column names" note
  are explicit)
- **Quote**: "Note: You can change the table name. Just don't change the column names."
- **Our assessment**: The column set is the concrete shape of the per-request LLM
  telemetry the Prospector flagged as the mechanism behind Ch05's "silent model
  fallback breaks attribution" concern: `total_cost` and `response_time` sit on
  the same row as `end_user`, `status`, and `error`, so spend and latency can be
  attributed to a tenant and an outcome from one record. Operational caveats we
  add (the page does not): the `messages json` / `response json` / `error json`
  columns store **full raw payloads at rest** in self-hosted Postgres with no
  redaction, retention, RLS, or access-control guidance on this page — adopting
  it as written puts prompt/response content and error payloads in the database
  (see Cross-References to the guardrail-logging-secret-exposure and Honeycomb
  notes). A duplicate `success_callback` follow-up row would double-write the
  same request, so operators should treat the callback set as the ledger's
  write path. The schema's one dedup affordance is `litellm_call_id text unique`
  (Artifact 1): *if* the callback populates that column, a double-write surfaces
  as an insert conflict rather than silent duplication. The page never says when
  or whether it is populated, and the column is nullable (in Postgres a unique
  index permits multiple NULLs), so we treat it as a latent dedup guard that the
  operator must verify, not a documented guarantee.

### Claim 3: End-user attribution is manual request metadata — the caller passes `user` to `litellm.completion` on each call; nothing upstream derives it
- **Evidence**: The "Additional Controls → Identify end-user" section.
- **Confidence**: settled (documented API surface)
- **Quote**: "Pass `user` to `litellm.completion` to map your llm call to an end-user"
- **Our assessment**: This is the manual-context boundary the corpus already
  documents for observability: the gateway records what it is told, and the
  caller must supply end-user identity per request. The legacy
  `/observability/` build shows the earlier spelling — `litellm.identify({"end_user": "krrish@berri.ai"})` —
  confirming the mechanism is a request-metadata annotation, not a column the
  gateway derives. Anything upstream that drops the `user` field silently breaks
  per-tenant cost reporting, so the guide should recommend making end-user
  attribution a required client contract rather than a best-effort kwarg.

### Claim 4: The page is explicitly community-maintained, thin on operational depth, and demonstrates no reliability behavior — it cannot support claims about what happens to telemetry when the sink fails
- **Evidence**: The community-maintained tip banner, and the absence of any
  failure-mode, buffering, log-loss, or retention discussion anywhere on the page.
- **Confidence**: settled (the disclaimer is explicit; the absence is verifiable)
- **Quote**: "This is community maintained, Please make an issue if you run into a bug"
- **Our assessment**: Bounds every claim above as "the documented wiring," not
  "wiring validated in production." This page must not be cited for any
  reliability property of callback logging (backpressure, write-path latency
  impact, delivery guarantees when Supabase is down or slow) — it asserts none.
  It is a reference for the API surface (callback registration + per-request
  attribution + table-name override) and the ledger schema, and nothing more.
  On grading: Claims 1–4 are all `settled` because they describe a fixed, published
  API surface and a fixed DDL that we verified character-for-character — there is
  nothing inferential in them to grade `emerging`. The frontmatter's
  `confidence_overall: emerging` is the *other* axis: every claim here is settled
  **at the documented-surface level**, while the integration's behaviour in
  production is `emerging` because a community-maintained page carrying no
  production evidence is the only support for it. Both grades are correct; they
  answer different questions.

## Concrete Artifacts

### Artifact 1: `request_logs` DDL (from "Create a supabase table", verbatim per rendered page)
```sql
create table
  public.request_logs (
    id bigint generated by default as identity,
    created_at timestamp with time zone null default now(),
    model text null default ''::text,
    messages json null default '{}'::json,
    response json null default '{}'::json,
    end_user text null default ''::text,
    status text null default ''::text,
    error json null default '{}'::json,
    response_time real null default '0'::real,
    total_cost real null,
    additional_details json null default '{}'::json,
    litellm_call_id text unique,
    primary key (id)
  ) tablespace pg_default;
```
Note: the legacy `/observability/` build of this page omits the `status` column
and (in the rendered page) the `litellm_call_id text unique` line, and instead
adds `constraint request_logs_pkey primary key (id)`. The current canonical
schema is the one above.

### Artifact 2: Callback enablement (from "Use Callbacks", verbatim)
```python
litellm.success_callback=["supabase"]
litellm.failure_callback=["supabase"]
```
Advertised as "Use just 2 lines of code, to instantly see costs and log your
responses **across all providers** with Supabase:".

### Artifact 3: Complete example (from "Complete code", verbatim per rendered page — incomplete as pasted: `import os` and `import litellm` are absent at the source, so this will not run as-is)
```python
from litellm import completion

## set env variables
### SUPABASE
os.environ["SUPABASE_URL"] = "your-supabase-url"
os.environ["SUPABASE_KEY"] = "your-supabase-key"

## LLM API KEY
os.environ["OPENAI_API_KEY"] = ""

# set callbacks
litellm.success_callback=["supabase"]
litellm.failure_callback=["supabase"]

# openai call
response = completion(
  model="gpt-5.6-luna",
  messages=[{"role": "user", "content": "Hi 👋 - i'm openai"}],
  user="ishaan22" # identify users
)

# bad call, expect this call to fail and get logged
response = completion(
  model="chatgpt-test",
  messages=[{"role": "user", "content": "Hi 👋 - i'm a bad call to test error logging"}]
)
```

### Artifact 4: End-user attribution (from "Additional Controls → Identify end-user", verbatim per rendered page)
```python
response = completion(
  model="gpt-5.6-luna",
  messages=[{"role": "user", "content": "Hi 👋 - i'm openai"}],
  user="ishaan22" # identify users
)
```

### Artifact 5: Table-name override (from "Additional Controls → Different Table name", verbatim)
```python
litellm.modify_integration("supabase",{"table_name": "litellm_logs"})
```

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed):

- `source-notes/docs-litellm-helicone-integration.md` — **cited** (Corroborates
  below).
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**: agent
  capability spectrum and pre-on-caller pattern; no logging-sink content.
- `source-notes/blog-litellm-auto-router-v2.md` — **dismissed**: router/scoring
  config; unrelated to request-logging callbacks.
- `source-notes/docs-langfuse-security-and-guardrails.md` — **dismissed**: guardrail
  architecture and tracing latency; no request-log-schema overlap beyond the shared
  PII-in-payload concern better served by the Honeycomb note.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: MCP server topic,
  unrelated.
- `source-notes/docs-google-sre-data-processing-pipelines.md` — **dismissed**: pipeline
  freshness/correctness SLOs; unrelated.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil taxonomy,
  unrelated.
- `source-notes/docs-promptfoo-deterministic-metrics.md` — **dismissed**: assertion/
  metric boundaries, unrelated.
- `source-notes/docs-datadog-llm-observability.md` — **cited** (Corroborates below).
- `source-notes/blog-litellm-save-claude-code-costs.md` — **dismissed**: budget
  windows and prompt-caching cost controls; different cost surface (spend caps on
  virtual keys vs. a request-log spend ledger).

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-datadog-llm-observability.md` **Claim 11** (auto-instrumentation
    "works for calls to supported frameworks and libraries"; custom application
    context is manual). The `user="ishaan22"` kwarg and `litellm.identify`-era
    variant (this note Claim 3) are concrete instances of that boundary at the LiteLLM
    SDK level: the callback logs the request, but end-user identity is hand-set per
    request and nothing derives it.
  - `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` **Claim 4**
    ("Auto-instrumentation can't infer your conversation boundaries or your agent identity")
    and **Claim 8** (prompt/response capture accelerates root-cause investigation but
    requires PII handling). This note's Claim 3 is LiteLLM's SDK-level spelling of the
    same manual-context rule, and Claim 2/`Artifact 1` (raw `messages`/`response` JSON
    at rest with no redaction guidance) is precisely the PII-exposure surface Claim 8
    warns about.
  - `source-notes/docs-litellm-helicone-integration.md` **Claim 1** (callback mode is
    the out-of-path, provider-agnostic placement). Supabase is a third instance of the
    `success_callback` out-of-path pattern (alongside Helicone), and **Claim 4** there
    (community-maintained → no production-validation warranty) is the same disclaimer
    this page carries.
- **Advancing / complementary** (not a contradiction):
  - `source-notes/docs-litellm-helicone-integration.md` **Claim 3** documents the
    stacked-authority hazard of *in-path* vendor headers re-implementing
    routing/retry/fallback controls. This page's plain Postgres sink has none of that —
    the two integrations sit on opposite ends of the placement spectrum established
    there. Same observation, different pole; no contradiction.
- **Extends**:
  - `source-notes/failure-litellm-guardrail-logging-secret-exposure.md` (Extracted
    Lessons → Lesson 1: observability/logging integrations are data-exposure surfaces
    requiring the same sanitization as any other output path). The Supabase DDL stores
    raw request/response/error payloads, so this page is a concrete example of a
    logging sink that *must* be treated as an exposure surface and given sanitization,
    access control, and retention — none of which this page advises.
  - `source-notes/failure-litellm-model-cost-map-silent-fallback.md` (Extracted
    Lessons → Lesson 3: out-of-band functions like cost calculation fail invisibly to
    request metrics). This page supplies the complementary *positive* artifact — a
    self-hosted per-request `total_cost` column operators can query directly instead of
    relying on cost-map lookups that silently degrade. The interplay is our synthesis;
    the page itself never discusses cost-map failures.
  - `source-notes/failure-litellm-prisma-reconnect-event-loop-blocking.md` **Claim 1**
    (a synchronous `subprocess.Popen.wait()` hidden behind an async library method
    blocks the whole asyncio event loop, defeating `asyncio.wait_for()`) and **Claim 6**
    (the blockage manifests only under partial failure — an unresponsive database, not a
    hard-down one). This is the reliability counterweight to this note's Claim 4: the
    Supabase page documents a request-log sink and asserts *nothing* about sink failure,
    while the Prisma incident is the corpus's LiteLLM-stack-native evidence that a
    degraded (not stopped) Postgres dependency freezes the proxy's event loop, takes
    `/health/liveliness` down with it, and gets the pod SIGKILLed — "converting a
    transient DB outage into a full proxy restart." Read together, adopting the
    self-hosted `request_logs` ledger adds a Postgres write path to a gateway whose own
    Postgres layer has already produced a full-outage incident; the page cannot supply
    that risk analysis, and this note does not pretend it does. (Not a contradiction —
    the Prisma note says nothing about telemetry sinks, and Claim 4's bounding stands
    unchanged; this is purely the missing pointer to the peer that *does* cover the
    ground.)
  - `source-notes/blog-litellm-redis-circuit-breaker.md` **Claim 2** (the slow-Redis
    case is the dangerous one: "the one that takes down gateways — is a slow Redis")
    and **Claim 3**
    ("A slow Redis becomes a database outage becomes a full gateway outage."). The
    second, vendor-authored instance of the same pattern as the Prisma incident — an
    out-of-path dependency that *degrades* rather than fails is what takes the gateway
    down — which is exactly the failure shape this page's new ledger sink would need
    analysed before adoption.
- **Novel** (first appearances in the corpus):
  - The **self-hosted dual-outcome request ledger**: both `success_callback` and
    `failure_callback` writing to one queryable SQL table that pairs `total_cost` and
    `response_time` with `status`/`error` and `end_user` per request — the concrete
    per-request row behind "silent model fallback breaks attribution" in Ch05.
  - LiteLLM's **callback surface** at the SDK level — `success_callback`,
    `failure_callback`, `litellm.modify_integration`, and per-request `user=`
    attribution — which the triage confirmed appears nowhere else in `source-notes/`.

## Guide Impact

- **Chapter 02 (Observability)**: Add the `request_logs` schema (Artifact 1) as a
  concrete reference shape for a **self-hosted per-request LLM ledger** — the column
  set (`model`, `messages`, `response`, `end_user`, `status`, `error`, `response_time`,
  `total_cost`, `additional_details`, `litellm_call_id`) is the pairing of
  cost/latency/outcome/tenant in one row that vendor callbacks often split across
  endpoints, and `litellm_call_id text unique` is the candidate dedup key for it.
  Pair the shape with the sink-risk citation, since the schema alone reads as free:
  `failure-litellm-prisma-reconnect-event-loop-blocking.md` (Claim 1, Claim 6) is the
  corpus evidence that a degrading Postgres dependency in this same stack is what
  freezes the proxy event loop. Also add Claim 3
  (`user=` kwarg) as another concrete instance of the already-stated "auto-instrumentation
  covers the framework layer; application context is manual" rule (alongside Datadog
  Claim 11 and Honeycomb Claim 4): end-user identity is request metadata the caller
  must supply, not a gateway-derived column.
- **Chapter 05 (LLM Ops Reliability — spend/attribution)**: Recommend the
  self-hosted ledger as the mechanism for making cost *and* error-rate *and* latency
  attributable per request and per `end_user` — the concrete replacement for
  environment-specific vendor dashboards, and the queryable surface that mitigates the
  silent cost-attribution failures in `failure-litellm-model-cost-map-silent-fallback.md`.
  The recommendation must carry the sink-degradation caveat with a citation, because
  this page cannot supply it: source the write-path risk to
  `failure-litellm-prisma-reconnect-event-loop-blocking.md` (Claim 1 — a blocking
  library call inside the async path froze the loop for 30–120 s and the kubelet killed
  the pod, "converting a transient DB outage into a full proxy restart"; Claim 6 — it
  only manifests under partial failure, i.e. an *unresponsive* DB), with
  `blog-litellm-redis-circuit-breaker.md` (Claim 2, Claim 3) as the adjacent second
  instance of degradation-not-outage dependency failure. Recommend the ledger and that
  note's partial-failure validation together, so a reader is not told to add a Postgres
  write path without being pointed at the evidence that this stack's Postgres layer can
  take the gateway down. Do **not** cite this source for any callback write-path
  reliability property (backpressure, delivery guarantees, sink-failure behavior) — the
  page asserts none (Claim 4).
- **Chapter 06 (Security and Trust)**: Add the raw-payload-at-rest caveat: adopting
  this documented schema as-is stores full `messages`/`response`/`error` JSON in
  Postgres with no page-provided redaction, retention, or RLS guidance — pair the
  ledger with sanitization and least-privilege access per
  `failure-litellm-guardrail-logging-secret-exposure.md` Lesson 1.

## Extraction Notes

- **Canonicalization**: The triaged URL (`https://docs.litellm.ai/observability/supabase_integration`)
  serves a **superseded legacy build** (older DDL without `status`/`litellm_call_id`,
  `gpt-3.5-turbo` example, `litellm.identify({"end_user": ...})`). The current page is
  the canonical `/docs/observability/supabase_integration` (title "Supabase", includes
  the community-maintained banner). Extraction and all Quotes/Artifacts use the
  canonical page, following the #1284 Helicone reconciliation precedent; the legacy
  spelling of `identify` is noted in Claim 3 and Artifact 1. Same crawl
  canonicalization hazard the #1284 note flagged — worth normalizing
  `registry/site-crawl-state.json` crawl keys to `/docs/`.
- **Verification of verbatim content**: both page variants were fetched as raw
  Markdown from `BerriAI/litellm-docs` (`docs/observability/supabase_integration.md`
  and `src/pages/observability/supabase_integration.md`) and cross-checked against the
  rendered pages at both URLs. The canonical page's code blocks render the Docusaurus
  variable `{{openai_small}}` (raw source) as `gpt-5.6-luna` (rendered); Artifact 3/4
  present the rendered form, which is what an operator sees at the URL.
- **Triage bounding honored**: `priority:low`, ~3 KB page. The note records the two
  non-obvious constraints the Prospector asked to verify — (a) only the table name is
  overridable, column names are fixed; (b) raw payloads at rest with no redaction
  guidance — plus the ledger pattern and the end-user attribution hook. It does not
  over-read the page into failure-mode, buffering, SLO, or retention claims that are
  absent (Claim 4 explicitly bounds this).
- **Cross-references verified per MINER.md §4b**: Datadog Claim 11 (auto/manual
  instrumentation boundary), Honeycomb Claims 4 and 8, and Helicone Claims 1, 3, and 4
  were re-read in their notes and match the citations above. Failure-note citations use
  section names (Extracted Lessons), not claim numbers. The two reliability notes added
  on rework were re-read and their numbered claims confirmed before citing:
  `failure-litellm-prisma-reconnect-event-loop-blocking.md` Claim 1 (blocking sync call
  in the async path) and Claim 6 (partial-failure-only manifestation), and
  `blog-litellm-redis-circuit-breaker.md` Claim 2 (slow Redis worse than down Redis) and
  Claim 3 (slow Redis → DB outage → gateway outage). Quoted fragments were copied
  verbatim from those notes.
- **Confidence reconciliation**: four `settled` claims against
  `confidence_overall: emerging` is intentional and not lazy grading. The claims are
  `settled` because they assert the *documented surface* (callback names, DDL, kwarg,
  disclaimer) which was re-fetched and checked character-for-character; the overall
  grade is `emerging` because the source carries no production evidence for the
  integration's runtime behaviour. Settled-at-the-documented-surface / emerging-at-the-
  production-behaviour level. See Claim 4's assessment for the same statement in place.
- **Artifact 3 fidelity**: the source's "Complete code" block genuinely omits
  `import os` and `import litellm` while using both; the artifact is reproduced verbatim
  with the defect disclosed in its label rather than silently repaired, consistent with
  the `{{openai_small}}` disclosure above.
- **No contradiction issue filed**: no existing source note is opposed by any claim
  here. The legacy-vs-canonical schema difference (one variant has `status` and
  `litellm_call_id`, the other does not) is a superseded-docs alias hazard within a
  single page, not a source-versus-source disagreement — handled as a
  canonicalization note, consistent with the #1284 precedent. The Helicone in-path
  header surface and this page's out-of-path Postgres sink occupy opposite ends of the
  placement spectrum already documented in the Helicone note; they agree rather than
  conflict. Likewise the newly cited
  `failure-litellm-prisma-reconnect-event-loop-blocking.md` does not contradict this
  page — that note is about the proxy's Prisma metadata store, not telemetry sinks, and
  this page makes no sink-reliability claim for it to oppose. It is additive: the peer
  that covers the write-path risk this page is silent on. No contradiction issue filed
  on rework either.
