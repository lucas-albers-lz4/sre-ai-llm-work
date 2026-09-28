---
source_url: https://docs.litellm.ai/docs/completion/http_handler_config
source_type: docs
title: "Custom HTTP Handler | liteLLM"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-09-28)
date_extracted: 2026-09-28
last_checked: 2026-09-28
status: current
confidence_overall: emerging
issue: "#1482"
---

# Custom HTTP Handler (LiteLLM Docs)

> The page's whole extractable value is its **Scope** admonition: injecting a
> custom `aiohttp.ClientSession` into LiteLLM's chat completions requires
> assigning the replacement to `litellm.main.base_llm_aiohttp_handler`, because
> assigning to `litellm.base_llm_aiohttp_handler` "creates a new attribute on
> the `litellm` package that nothing reads, and the custom session is silently
> ignored" — and even the *correct* assignment changes nothing outside the
> non-default `aiohttp_openai/` provider (plain `openai/` and every other
> provider go through httpx clients and "are not affected by this handler"). A
> "looks configured, does nothing" failure with **zero** error, warning, or
> log, on a knob whose own overview advertises fleet-wide-sounding uses
> (connection pooling, corporate proxy, performance, request monitoring). Plus
> a second import-time binding trap (`litellm.images.main` captures its own
> reference at import, so the Topaz image-variation path the page names as
> in-scope is *not* changed by the assignment), a two-branch session-lifecycle
> ownership contract, and three mutually inconsistent timeout/pool profiles —
> none of them backed by any benchmark.

## Source Context

- **Type**: docs (official vendor documentation — single living Docusaurus page
  at `/docs/completion/http_handler_config`, verified HTTP 200 this session and
  matching `source_url`; ~73 KB of rendered HTML, of which the extractable
  body is ~90 lines). Nav position per the page's own breadcrumb:
  Supported Endpoints → `/chat/completions` → Custom HTTP Handler. Siblings in
  the same nav branch: `usage` (Previous) and `/completions` (Next) — the
  site-crawl seed filed the sibling `drop_params` page separately as #1480
  (already mined as `docs-litellm-drop-params.md`), so it was not re-extracted
  here.
- **Author credibility**: LiteLLM (BerriAI) first-party product
  documentation. Authoritative for the *documented* surface of a shipped
  feature — the exact assignment target, the provider scope, the constructor
  signature, the lifecycle contract, and copy-pasteable config. It is **not**
  evidence of measured behavior: the page carries no metrics, no benchmark, no
  version range, no changelog entry, no link to the implementing source, and
  no failure report. It is also undated. Every quantitative value on the page
  (timeouts, pool limits, DNS cache TTL) is presented as a code comment with
  no stated derivation — see Claim 7.
- **Scope**: How to inject a custom `aiohttp.ClientSession` (or `transport`, or
  `connector`) into LiteLLM's chat-completion path: the assignment target, the
  provider scope limit, three worked patterns (FastAPI `lifespan`, corporate
  proxy/SSL, high-throughput), the constructor options, the resource-management
  contract, and dev/production config tips. Does **not** cover: the transport
  layer LiteLLM uses for non-`aiohttp_openai/` providers (httpx, covered
  elsewhere in the corpus and *not* configurable through this page), the
  `aiohttp_benchmarks` page rejected in #1380, any in-gateway observability
  surface, or any request-level configuration (this is SDK/process-level Python
  code, not `config.yaml` — a significant scope limit the page never states,
  see Extraction Notes).

## Extracted Claims

### Claim 1: `BaseLLMAIOHTTPHandler` is consulted only by the `aiohttp_openai/` provider (chat completions) and by Topaz image variations — every other provider, *explicitly including plain `openai/`*, goes through the httpx-based clients and is unaffected
- **Evidence**: The "Scope" admonition immediately below the Overview, which
  names both in-scope paths and then names the excluded class. It is the
  first-sentence scope statement on the page, not a footnote.
- **Confidence**: settled (explicit, unambiguous vendor scope statement about
  their own code)
- **Quote**: "`BaseLLMAIOHTTPHandler` is only used by the `aiohttp_openai/`
  provider (chat completions) and by Topaz image variations. Requests to other
  providers, including plain `openai/`, go through the httpx based clients and
  are not affected by this handler."
- **Our assessment**: This is the highest-value claim on the page, and it is
  the *sharp* edge of the title. A reader who lands on "Custom HTTP Handler"
  under `/chat/completions` with no other context will reasonably read the
  feature as gateway-wide; the scope statement says the opposite, and singles
  out plain `openai/` — the single most common LiteLLM route — as excluded.
  The failure mode is asymmetric and undetectable: an operator who tunes this
  handler and serves `openai/` models has changed *nothing*, with no error, no
  warning, and no log, because the calls were never going to consult the
  handler in the first place. Combined with Claim 4 (the examples also switch
  the model prefix to `aiohttp_openai/`), the page's actual contract is
  "opt-in transport *and* opt-in route prefix" — two changes, one of which the
  Overview never mentions.

### Claim 2: The assignment target is module-scoped, and the plausible-looking wrong target is a **silent** no-op — `litellm.base_llm_aiohttp_handler` "creates a new attribute on the `litellm` package that nothing reads, and the custom session is silently ignored"
- **Evidence**: Second and third sentences of the same "Scope" admonition. The
  code is correct in every one of the page's five snippets, so the trap exists
  only for a reader who writes the assignment from memory or from the class
  name rather than copying the snippet.
- **Confidence**: settled (explicitly stated failure mode, with the mechanism
  named)
- **Quote**: "The instance that `litellm.completion` calls lives in the
  `litellm.main` module, so the replacement must be assigned to
  `litellm.main.base_llm_aiohttp_handler`. Setting
  `litellm.base_llm_aiohttp_handler` creates a new attribute on the `litellm`
  package that nothing reads, and the custom session is silently ignored."
- **Our assessment**: We buy this, and it is the single most reusable
  operational pattern on the page. The mechanism is Python's ordinary attribute
  assignment: `import litellm` exposes the *package*, and the handler instance
  `litellm.completion` actually dereferences is a module-global in
  `litellm.main`. Assigning to the package name creates a brand-new attribute,
  binds it successfully, and nobody reads it — so there is no `AttributeError`,
  no `DeprecationWarning`, no log line, and no behavioral difference to observe
  in a smoke test that watches only success/failure. The verification rule this
  implies is the guide-useful one: **read back the exact attribute the call
  path dereferences** (`litellm.main.base_llm_aiohttp_handler is my_handler`),
  not the one whose name looks like the feature. This is a module-boundary
  instance of the class the corpus already tracks in config ("acknowledged but
  not applied") — see Cross-References.

### Claim 3: A second, unavoidable static-binding trap: `litellm.images.main` binds its own reference to the handler **at import time**, so the Topaz image-variation path is not changed by the assignment — one of the two paths the page names as in-scope
- **Evidence**: Fourth sentence of the "Scope" admonition, immediately after
  the two assignment-target sentences. It is the only statement on the page
  about the image-variation path.
- **Confidence**: settled (explicit)
- **Quote**: "`litellm.images.main` binds its own reference to the handler at
  import time, so the Topaz image variation path is not changed by this
  assignment."
- **Our assessment**: The page states this as a fact without saying what an
  operator should do about it, and the fact is more interesting than it looks:
  the *same* sentence that names Topaz image variations as in-scope also
  documents that the documented mechanism cannot change that path. So
  "Topaz image variations" is in scope for the handler in principle, but the
  only documented injection mechanism is inert for it — a `from
  litellm.images.main import base_llm_aiohttp_handler` style override (or a
  post-import rebind of *that* module's global) would be required, and the page
  does not document it. The guide-relevant generalization is the import-time
  capture pattern: **a module-level `from x import y` binding is a snapshot,
  and post-import reassignment of `x.y` will not reach it.** That is a
  distinct failure mode from Claim 2 — in Claim 2 the wrong target is
  writable-but-unread; here the correct target is readable but already
  snapshotted elsewhere. Recorded as an internal tension of the page rather
  than a contradiction (see Extraction Notes).

### Claim 4: Turning the custom session on is a **routing** change as well as a config change — every worked example switches the model prefix to `aiohttp_openai/<model>`, while the "Default (No Changes Required)" example keeps the unprefixed `gpt-5.6-luna` and is annotated "Works exactly as before"
- **Evidence**: Side-by-side reading of the two Basic Usage snippets. The
  "Custom Session" snippet's final line carries the inline comment "#
  `aiohttp_openai/` completions now use your session"; the default snippet
  carries "# Works exactly as before" and calls `gpt-5.6-luna` with no
  provider prefix.
- **Confidence**: settled (the two snippets are unambiguous; the default
  example is *silent* about the interaction, which is the point)
- **Quote**: "# `aiohttp_openai/` completions now use your session" / "# Works
  exactly as before"
- **Our assessment**: The real contract is two opt-ins, and the page only ever
  presents the first. Injecting the handler (Claim 2) plus re-prefixing the
  model (here) are both required, and the *second* one is a per-request string
  change in calling code or in a `config.yaml` `model_name` mapping — i.e. it
  is far more invasive and far more likely to be half-done than the module
  assignment. This is a genuine operational hazard: a fleet can be correctly
  assigned *and* still serve 100% of its traffic through `openai/`, in which
  case the tuning is pure dead configuration. Worth noting the asymmetry
  against the default path: the page presents the unprefixed default as
  unchanged, which is true, but "unchanged" here means "not routed through the
  thing you just configured."

### Claim 5: Session-lifecycle ownership is an explicit two-branch contract — user-supplied sessions are closed by the caller, handler-auto-created sessions are cleaned up by the handler, and the page asserts full backward compatibility
- **Evidence**: The "Resource Management" section, three bullets. The
  caller-close rule is the load-bearing one and is reinforced by the FastAPI
  `lifespan` example's `# Shutdown` / `await session.close()`.
- **Confidence**: settled (explicit contract statement)
- **Quote**: "- **User sessions**: You manage the lifecycle (call `await
  session.close()`)"
- **Quote**: "- **Auto-created sessions**: Automatically cleaned up by the
  handler"
- **Quote**: "- **100% backward compatible**: Existing code works unchanged"
- **Our assessment**: This is the ownership half of a pair with
  `failure-litellm-httpx-cache-eviction.md`, and the two errors are mirror
  images: that report is a resource closed **while still in use** by a
  third party that assumed sole ownership; this is a resource the operator
  **owns** and must close, where the failure is the opposite — never closed
  (leak) or closed at the wrong moment. The backward-compatibility bullet is
  worth flagging as a soft claim: it is a vendor assertion with no test or
  measurement on the page, and it is the kind of statement that a future
  refactor invalidates silently. There is a further lifecycle hazard the page
  does not mention: the FastAPI example closes the session on shutdown but
  never unbinds the handler, so after the lifespan exits the module-global
  `base_llm_aiohttp_handler` still holds a reference to a **closed** session —
  a post-shutdown request would fail against it rather than falling back to a
  default handler.

### Claim 6: The constructor exposes three orthogonal injection points (`client_session`, `transport`, `connector`) and the page's three worked patterns each pick a different one — a session for pooling, a session with an SSL connector plus `trust_env` for proxying, and a session with a tuned connector for throughput
- **Evidence**: The "Constructor Options" block plus the three Common Patterns
  snippets, all reproduced verbatim under Concrete Artifacts.
- **Confidence**: settled (documented signature and three runnable
  instantiations)
- **Quote**: "`client_session=None,    # Custom aiohttp.ClientSession`"
- **Quote**: "`transport=None,         # Advanced transport control`"
- **Quote**: "`connector=None,         # Custom aiohttp.BaseConnector`"
- **Our assessment**: A real API, not a stub: the three parameters are not
  redundant, because `transport` takes precedence over `connector` in aiohttp's
  own `TCPConnector(transport=...)` construction, and the page does not state
  that precedence or what happens if more than one is supplied. Only
  `client_session` is demonstrated across all three patterns, so `transport` is
  documented-but-unexercised. The `trust_env=True` half of the proxy pattern
  is worth isolating: it is the *only* documented mechanism on the page for
  picking up environment proxy settings, and it is a plain `aiohttp`
  `ClientSession` parameter being passed through, not a LiteLLM feature. The
  `load_cert_chain('cert.pem', 'key.pem')` mTLS pattern is likewise stock
  `ssl` — the operational value here is knowing *where* the knob lives (the
  connector you construct), not that LiteLLM invented it.

### Claim 7: The page publishes **three mutually inconsistent** timeout/pool profiles with no stated derivation — dev (`total=60`, `limit=50`), the main "Custom Session" example (`total=180`, `limit=300`, `limit_per_host=75`), and the "Production" tip (`total=300`, `limit=1000`, `limit_per_host=200`, `keepalive_timeout=60`) — and backs none of them with a measurement
- **Evidence**: The "Custom Session" Basic Usage snippet, the "Configuration
  Tips → Development" snippet, and the "Configuration Tips → Production"
  snippet, all verbatim under Concrete Artifacts. The main example's numbers
  match neither tip.
- **Confidence**: settled (the inconsistency is directly observable in the
  page's own text; the *absence* of any benchmark is also directly observable)
- **Quote**: `timeout=aiohttp.ClientTimeout(total=180)` /
  `timeout=aiohttp.ClientTimeout(total=60)` /
  `timeout=aiohttp.ClientTimeout(total=300)`
- **Our assessment**: We do **not** buy these as tuning guidance. They are
  unsourced constants, and the page offers no way to tell whether a value is
  a recommendation, an example, or a leftover: the *main* example is captioned
  "# Create optimized session" with a 180s/300/75 shape that appears in
  neither the dev nor the production tip. A reader choosing "production"
  values by pattern-matching on the headline example rather than the
  "Configuration Tips" table picks a third, undocumented profile. The
  relevant comparison is the corpus's rejected #1380
  (`/docs/aiohttp_benchmarks`), which *did* publish methodology and numbers for
  an aiohttp/httpx transport comparison and was rejected for staleness — this
  page, which ships no methodology at all, is the surviving surface, and it
  supplies no measured basis for any of these values. Treat the numbers as
  shape examples (timeout + connector size are the right two dials to expose),
  not as a sizing recommendation; the guide should not cite any specific value
  as evidence-backed.

### Claim 8: The "High Performance" and "Production" profiles are not the same recipe — `ttl_dns_cache=600` and `enable_cleanup_closed=True` appear **only** in the former, making the "Production" tip a strict subset rather than a restatement
- **Evidence**: Character-level diff of the two "production" snippets, both
  reproduced verbatim below. `High Performance` carries six connector
  parameters; `Production` carries four.
- **Confidence**: settled (directly observable)
- **Quote**: "`ttl_dns_cache=600,      # DNS cache`"
- **Quote**: "`enable_cleanup_closed=True`"
- **Our assessment**: Worth extracting as a standalone delta because it is the
  kind of thing a reader will get wrong by assuming the two sections agree.
  DNS caching (`ttl_dns_cache=600`) is the practically significant omission: it
  is the dial that removes per-connection DNS resolution for a gateway that
  fans out to a small number of provider hosts, and the page's *canonical*
  production recipe drops it. `enable_cleanup_closed=True` is the
  long-lived-connection hygiene flag (reaps connections aborted by the peer),
  which is precisely the setting you want when `keepalive_timeout` is on and
  load is bursty. That the higher-profile "High Performance" block has *more*
  connector tuning than the block labeled "Production" is itself the evidence
  that neither is a reviewed, canonical config.

### Claim 9: "Request monitoring" is advertised as a first-class use case in the Overview, but the page ships no monitoring example, no hook, no event, and no instrumentation surface — the injected session is the only place to put one
- **Evidence**: The Overview's four-bullet use-case list names "Request
  monitoring"; the page's four remaining sections (Constructor Options,
  Resource Management, Configuration Tips, and the preceding patterns) contain
  no monitoring code or any statement about what a custom session can observe.
- **Confidence**: settled (an absence, directly verifiable on the page)
- **Quote**: "- Request monitoring"
- **Our assessment**: The mechanism is real and obvious to an engineer — you
  own the `ClientSession`, so you can wrap the connector, install a
  `TraceConfig`, or subclass — but the page offers no example, no documented
  hook, and no statement about whether LiteLLM's own callbacks/spend logging
  still fire on top of a user-supplied session. That last gap is the
  operational question: an operator instrumenting at the transport layer by
  swapping in their own session is modifying the very object LiteLLM's
  telemetry may depend on, and the page neither warns nor confirms. Recorded
  as a thin spot, not a defect; the guide should not imply the page
  documents an observability surface.

### Claim 10: The page documents **no verification step** — no read-back recipe, no assertion, no log, metric, or health field that would tell an operator the assignment landed
- **Evidence**: Absence across all nine sections. The only signal the page
  offers for the whole feature is the Resource Management bullet "100%
  backward compatible: Existing code works unchanged", which is a
  compatibility claim, not an observability one.
- **Confidence**: settled (an absence, directly verifiable on the page)
- **Quote**: (no direct quote; see Our assessment)
- **Our assessment**: This is the claim that turns Claims 2–4 into an
  operational problem rather than a documentation nit. The page describes a
  configuration whose failure mode is indistinguishable from success and then
  provides no way to distinguish them. The concrete remedy is short and the
  guide should carry it: after assignment, assert identity on the attribute
  the call path reads — `assert litellm.main.base_llm_aiohttp_handler is
  handler` — and separately assert that the traffic being served actually
  routes through `aiohttp_openai/` (e.g. by a one-off request with a sentinel
  proxy/mocked endpoint, or by checking the model prefix in config). This is
  the same "no documented signal for a drop" gap the corpus already recorded
  for `drop_params` (see Cross-References), and the same "reload success ≠
  reachability" rule Ch05 already states for a different LiteLLM config path.

## Concrete Artifacts

All artifacts verbatim from the fetched page
(`https://docs.litellm.ai/docs/completion/http_handler_config`), extracted from
the rendered HTML.

**The "Scope" admonition, in full, verbatim** (this is the page's entire
non-boilerplate prose; attribution: the info admonition titled "Scope",
directly under the Overview):

```
Scope

BaseLLMAIOHTTPHandler is only used by the aiohttp_openai/ provider (chat
completions) and by Topaz image variations. Requests to other providers,
including plain openai/, go through the httpx based clients and are not affected
by this handler.

The instance that litellm.completion calls lives in the litellm.main module, so
the replacement must be assigned to litellm.main.base_llm_aiohttp_handler.
Setting litellm.base_llm_aiohttp_handler creates a new attribute on the litellm
package that nothing reads, and the custom session is silently ignored.
litellm.images.main binds its own reference to the handler at import time, so
the Topaz image variation path is not changed by this assignment.
```

*Attribution: "Custom HTTP Handler" → Overview → Scope admonition. Wording and
punctuation are character-for-character; the line wrapping and the split
between the two `<p>` elements in the admonition body are ours for
readability (the source renders them as one info admonition labelled "Scope").*

**Overview use-case list (verbatim)**

```
You can inject custom aiohttp.ClientSession instances into LiteLLM for:

-   Custom connection pooling and timeouts
-   Corporate proxy and SSL configurations
-   Performance optimization
-   Request monitoring
```

**Default (No Changes Required) (verbatim)**

```python
import litellm

# Works exactly as before
response = await litellm.acompletion(
    model="gpt-5.6-luna",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**Custom Session (verbatim)** — note `total=180` / `limit=300` /
`limit_per_host=75` here vs. `total=300` / `limit=1000` in "Production"
(Claim 7).

```python
import aiohttp
import litellm
import litellm.main
from litellm.llms.custom_httpx.aiohttp_handler import BaseLLMAIOHTTPHandler

# Create optimized session
session = aiohttp.ClientSession(
    timeout=aiohttp.ClientTimeout(total=180),
    connector=aiohttp.TCPConnector(limit=300, limit_per_host=75)
)

# Replace the handler that litellm.completion uses
litellm.main.base_llm_aiohttp_handler = BaseLLMAIOHTTPHandler(client_session=session)

# aiohttp_openai/ completions now use your session
response = await litellm.acompletion(model="aiohttp_openai/gpt-5.6-luna", messages=[...])
```

**FastAPI Integration (verbatim)** — the `lifespan` pattern; note the handler
is never unbound after `await session.close()` (Claim 5).

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
import aiohttp
import litellm
import litellm.main
from litellm.llms.custom_httpx.aiohttp_handler import BaseLLMAIOHTTPHandler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=180),
        connector=aiohttp.TCPConnector(limit=300)
    )
    litellm.main.base_llm_aiohttp_handler = BaseLLMAIOHTTPHandler(
        client_session=session
    )
    yield
    # Shutdown
    await session.close()

app = FastAPI(lifespan=lifespan)

@app.post("/chat")
async def chat(messages: list[dict]):
    return await litellm.acompletion(model="aiohttp_openai/gpt-5.6-luna", messages=messages)
```

**Corporate Proxy (verbatim)**

```python
import ssl

# Custom SSL context
ssl_context = ssl.create_default_context()
ssl_context.load_cert_chain('cert.pem', 'key.pem')

# Proxy session
session = aiohttp.ClientSession(
    connector=aiohttp.TCPConnector(ssl=ssl_context),
    trust_env=True  # Use environment proxy settings
)

litellm.main.base_llm_aiohttp_handler = BaseLLMAIOHTTPHandler(client_session=session)
```

**High Performance (verbatim)** — the only snippet carrying `ttl_dns_cache`
and `enable_cleanup_closed` (Claim 8).

```python
# Optimized for high throughput
session = aiohttp.ClientSession(
    timeout=aiohttp.ClientTimeout(total=300),
    connector=aiohttp.TCPConnector(
        limit=1000,             # High connection limit
        limit_per_host=200,     # Per host limit
        ttl_dns_cache=600,      # DNS cache
        keepalive_timeout=60,   # Keep connections alive
        enable_cleanup_closed=True
    )
)

litellm.main.base_llm_aiohttp_handler = BaseLLMAIOHTTPHandler(client_session=session)
```

**Constructor Options (verbatim)** — reproduced with the page's own comment
column:

```
BaseLLMAIOHTTPHandler(
    client_session=None,    # Custom aiohttp.ClientSession
    transport=None,         # Advanced transport control
    connector=None,         # Custom aiohttp.BaseConnector
)
```

**Resource Management (verbatim)**

```
-   **User sessions**: You manage the lifecycle (call `await session.close()`)
-   **Auto-created sessions**: Automatically cleaned up by the handler
-   **100% backward compatible**: Existing code works unchanged
```

**Configuration Tips — Development (verbatim)**

```python
session = aiohttp.ClientSession(
    timeout=aiohttp.ClientTimeout(total=60),
    connector=aiohttp.TCPConnector(limit=50)
)
```

**Configuration Tips — Production (verbatim)**

```python
session = aiohttp.ClientSession(
    timeout=aiohttp.ClientTimeout(total=300),
    connector=aiohttp.TCPConnector(
        limit=1000,
        limit_per_host=200,
        keepalive_timeout=60
    )
)
```

**Profile comparison (our tabulation of the four snippets above, not a
source table — the page publishes no comparison table):**

| Where on page | timeout total | limit | limit_per_host | ttl_dns_cache | keepalive_timeout | enable_cleanup_closed |
|---|---|---|---|---|---|---|
| Basic Usage → Custom Session | 180 | 300 | 75 | — | — | — |
| Common Patterns → FastAPI | 180 | 300 | — | — | — | — |
| Common Patterns → High Performance | 300 | 1000 | 200 | 600 | 60 | True |
| Config Tips → Development | 60 | 50 | — | — | — | — |
| Config Tips → Production | 300 | 1000 | 200 | — | 60 | — |

## Cross-References

**Candidates from `miner-related-notes.md`** (every listed path is cited or
dismissed; the lexical retrieval is dominated by the shared `litellm`/agent
vocabulary and returns no transport-layer matches):

- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch TPM/RPM
  accounting and enqueued-token reservations; rate-limit arithmetic, no
  transport or session-lifecycle content. The lexical pull is the
  `silently ignored` phrasing in its Claim 5, which is a *shared pattern*, not
  shared subject matter.
- `source-notes/docs-litellm-bedrock-invoke.md` — **dismissed**: Bedrock
  native Invoke passthrough routing and SigV4→bearer auth swap; the one
  adjacency is "passthrough path," which this page does not cover.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **dismissed**:
  per-session `max_iterations` / `max_budget_per_session` cost caps and
  trace-id enforcement; "session" here means an agent conversation session
  keyed on `x-litellm-trace-id`, not an HTTP client session. Term collision
  only.
- `source-notes/docs-litellm-bedrock-converse.md` — **dismissed**: Bedrock
  native Converse passthrough and its support matrix; no transport
  configuration.
- `source-notes/docs-litellm-audio-transcription.md` — **dismissed**:
  `mode: audio_transcription` routing and fallback configuration; no
  connection-pool or session content.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **dismissed**: the
  lexical pull is the word "keepalives" (SSE pings); this page has no
  streaming content. Advisor sub-inference composition and usage-splitting are
  unrelated.
- `source-notes/blog-litellm-auto-router-v2.md` — **cited (Extends)**: the
  nearest substantive candidate. See the primary list below — the `aiohttp_openai/`
  model prefix is a routing decision, and that note is the corpus's reference
  for routing-flavor selection; the difference is that here the route choice
  silently determines whether a transport config applies at all.
- `source-notes/docs-litellm-a2a-agent-card.md` — **dismissed**: served
  agent-card field matrix and skill-scoping drops; no transport content.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **dismissed**: per-agent
  flat vs token-based chargeback; no transport content.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: docs-as-MCP for
  coding agents on the `streamableHttp` transport; a different vendor and a
  different (documentation-serving) transport, no overlap in subject.

**Primary cross-references** (found by searching `source-notes/` and `guide/`
myself; every `Claim N` verified by re-reading the cited note, per MINER §4b):

- **Corroborates**:
  - `source-notes/docs-litellm-drop-params.md` **Claim 9** — "The page
    documents **no observable signal for a drop** — no log line, metric,
    response field, or header is stated for either branch, so the only
    difference a caller or monitor can detect between "param honored" and
    "param silently stripped" is the absence of the raise." This note's
    Claim 10 is the same gap in a different subsystem: a gateway knob whose
    silent branch is indistinguishable from its working branch. Two LiteLLM
    config surfaces, one shared blind spot.
  - `source-notes/docs-litellm-claude-code-context-management.md` **Claim 5** —
    "`compact_20260112` requires `context_management_summary_model` to be set
    in `general_settings`. Without it, the edit is acknowledged but no
    compaction is performed." Same failure class as this note's Claim 2, one
    layer over: there the config is *acknowledged* (an `applied_edits` entry
    appears) and does nothing; here the config is *assigned* (a real package
    attribute is created) and does nothing. Both are the "looks applied, is a
    no-op" shape, and the mitigation in both cases is an explicit read-back
    assertion on the specific field that gates the behavior.
  - `source-notes/docs-litellm-claude-code-context-management.md` **Claim 9** —
    four knobs ("`pause_after_compaction`, `clear_at_least`, `exclude_tools`,
    `clear_tool_inputs`") are "Accepted in request but ignored by polyfill
    (v0)". Corroborates the guide-relevant generalization this note supports:
    in LiteLLM, *accepted* is not *applied*, and a v0/early feature can accept
    a configuration surface it does not honor.
- **Contradicts**: **None found; no contradiction issue filed.** Reasoning in
  Extraction Notes. The one near-miss — the #1380 triage's rejected finding
  that "aiohttp is now the default transport with opt-out via
  `DISABLE_AIOHTTP_TRANSPORT`" — is about a *different* mechanism (the global
  default transport for LiteLLM's httpx-style handlers, as of 2026-05) and
  that page was **rejected**, so it is not in the corpus;
  `docs-litellm-benchmarks.md` explicitly records that the in-corpus
  benchmarks page "contains zero `aiohttp` mentions". No in-corpus source
  note claims otherwise.
- **Extends / thematically adjacent**:
  - `source-notes/failure-litellm-httpx-cache-eviction.md` — the mirror-image
    lifecycle failure, and the pairing the Prospector asked for. That note's
    Claim 2 records the mixed-ownership problem: "The cached values are a mix
    of: Redis/async Redis clients — owned exclusively by the cache, safe to
    close on eviction; httpx-backed SDK clients (OpenAI, Anthropic, etc.) —
    shared references, still in use by router/model instances." The error
    there is closing a resource *still in use*; the error here (Claim 5) is
    failing to close a resource *you own*. Together they are the two ends of
    HTTP-client lifecycle ownership in the same gateway, and a guide section
    on LLM client lifecycle should carry both. The transport also differs
    (httpx vs aiohttp), which is itself worth stating: the corpus now has one
    note per transport.
  - `source-notes/docs-litellm-gateway-auth-reference.md` **Claim 1** — "The
    MCP **ASGI** routes … bypass the standard FastAPI auth dependency"; the
    page's own assessment of that claim notes the operator consequence is that
    a credential form is "silently ignored on `/mcp` but honored on
    `/mcp-rest`". Structurally identical to this note's Claim 1: a setting
    honored on one dispatch path and inert on a sibling path, with no error.
    A guide rule covering one should cover the other — "a knob is only
    fleet-wide if every path that can serve traffic reads it."
  - `source-notes/docs-litellm-benchmarks.md` **Claim 11** — "The fastest way
    to benchmark proxy overhead is using network_mock mode. This intercepts
    outbound requests at the httpx transport layer and returns canned
    responses, no need for setting up a mock provider." Establishes the
    **inbound** (gateway → caller) transport layer in the corpus; this page is
    the **outbound** (gateway → provider) one. Useful pairing for the guide
    because the outbound connection pool is where per-provider fan-out cost
    lands, and because it shows the httpx-vs-aiohttp split is a *layer*
    distinction, not a single transport.
  - `source-notes/blog-litellm-fastapi-middleware-performance.md`
    **Claim 1** — "On every request, even a pure passthrough (meaning nothing
    happens), BaseHTTPMiddleware creates 7 intermediate objects and tasks."
    That note's lever is inbound middleware allocation; this page's is the
    outbound socket pool. Both are per-request cost knobs in the same Python
    process, and the FastAPI `lifespan` pattern here is the lifecycle half of
    the same optimization program.
  - `source-notes/blog-litellm-sub-millisecond-proxy-overhead.md`
    **Claim 7** — "This separation allows each component to focus on what it
    does best: Python acts as the control plane, while the sidecar handles the
    hot path." That claim's heading enumerates the sidecar's hot-path
    responsibilities as request forwarding, connection reuse/pooling,
    timeouts/limits, and high-frequency metric aggregation. That split is
    about the *inbound* hot path. This page configures the *outbound* pool
    that the Python control plane uses to reach providers — a surface the
    sidecar architecture does not move, and therefore one that stays
    operator-tuned in Python.
- **Novel** (grep-verified across `source-notes/` and `guide/`: zero prior
  matches for `aiohttp`, `BaseLLMAIOHTTPHandler`, `base_llm_aiohttp`,
  `TCPConnector`, `ClientSession`, `client_session`, or "connection pool" in
  any gateway-transport context — the only hits for "connection pool" are
  Redis-pool leaks in `failure-litellm-httpx-cache-eviction.md` and a
  hypothetical in `docs-google-sre-address-cascading-failures.md`):
  1. **The `litellm.main.` vs `litellm.` assignment trap** — the first
     documented, module-scoped, silently-ignored configuration target in the
     corpus with the mechanism named by the vendor.
  2. **The import-time binding capture** (`litellm.images.main`) — a
     post-import config that cannot reach a module that already imported the
     symbol. First in-corpus instance of that specific mechanism.
  3. **The whole outbound connection-pool surface** — `aiohttp_openai/` as a
     distinct opt-in provider route, `TCPConnector` sizing, `ttl_dns_cache`,
     `keepalive_timeout`, `enable_cleanup_closed`, `trust_env` +
     `TCPConnector(ssl=...)` for corporate proxy/mTLS. The guide has no
     connection-pool-sizing guidance for LLM gateways at all.
  4. **The provider-scope asymmetry for a *transport* config** — the corpus has
     per-*endpoint* and per-*route-family* asymmetries (batches, Bedrock
     passthrough, MCP vs A2A) but not per-*transport-provider* ones.
  5. **The caller-owns-the-session contract** — a two-branch lifecycle rule
     (user sessions closed by caller, handler-created sessions closed by
     handler) that is the inverse of the eviction incident's failure.

## Guide Impact

- **Chapter 05 (§"Config changes need their own three-property test", §"Reload
  success ≠ model reachability")**: Add a named worked example for
  *invisible-success* config. The guide already states "A successful reload
  log line is not evidence the model is reachable"; this source is the same
  failure in a different config surface and adds the sharper point that
  **there is no log line at all** — `litellm.base_llm_aiohttp_handler = ...`
  raises nothing, warns nothing, and logs nothing. The three-property test's
  auto-stop property is unimplementable for a change you cannot observe, so
  the guide should add the precondition: *before* canarying a config change,
  name the read-back assertion that proves it took effect, and reject any
  change for which none exists. Concretely for this surface: assert
  `litellm.main.base_llm_aiohttp_handler` identity (the module path, not the
  package attribute — Claim 2).
- **Chapter 05 (§"Provider parity in the shared forwarding path")**: This
  source is the mirror image of the section's existing case, and the pairing
  is worth stating explicitly. The existing vLLM case is a *stricter sibling*
  rejecting a parameter the shared path forwards — the fix is filter-to-omit
  at the shared boundary. This source is a setting that applies to a strict
  *subset* of the fleet and is inert on the rest, including plain `openai/` —
  the fix is not a code change but a route-prefix change plus a read-back
  check. Proposed addition to that section's existing "test the non-default
  provider" rule: **audit the blast radius of every transport-level knob —
  enumerate the routes it is reachable from, and treat "affects only the
  non-default provider" as a deployment-blocking fact to verify, not a
  footnote.** Note the double opt-in (assign the handler *and* prefix the
  model `aiohttp_openai/`, Claims 2 + 4): a fleet can be correctly assigned
  and still route 100% of traffic past the config.
- **Chapter 05 (§"Cost, capacity, and fallback patterns")**: The page is the
  corpus's only source on outbound connection-pool sizing for an LLM gateway.
  Recommend adding a short subsection stating the *shape* of the knob set
  (`ClientTimeout(total=…)` + `TCPConnector(limit, limit_per_host,
  ttl_dns_cache, keepalive_timeout, enable_cleanup_closed)`) as the two dials
  worth exposing, **explicitly flagging that the specific values on this page
  are unsourced** (Claim 7) and must be derived per deployment — measured
  against the gateway's own concurrency and provider fan-out, not copied from
  a docs snippet. Do not let the Smith cite `limit=1000` /
  `limit_per_host=200` as evidence-backed: three inconsistent profiles ship on
  one page and none has a benchmark behind it (contrast the *rejected* #1380,
  which at least published methodology). Also add the lifecycle rule from
  Claim 5 alongside the existing eviction material: a session you supply is
  yours to close (`await session.close()` at shutdown), and — the mirror of
  the eviction incident — do not let a third party close one you still hold.
- **Chapter 02 (Observability)**: The page advertises "Request monitoring" as
  an Overview use case and documents no monitoring example, hook, or
  instrumentation surface (Claim 9). Do **not** cite it as an observability
  source. The honest, narrower use is as a *transport-layer instrumentation
  point*: owning the `ClientSession` is the one documented way to observe
  outbound provider traffic in-process, which is why an operator reaching for
  it needs to know that swapping the session also changes the object
  LiteLLM's own callbacks and spend logging may depend on — a question this
  page leaves unanswered. If Ch02's request-monitoring section is extended,
  record that unanswered dependency as an open question rather than a
  capability.
- **Chapter 06 (Security and Trust)**: Minor but worth a line in the corporate-proxy
  pattern — `trust_env=True` plus a client certificate chain via
  `TCPConnector(ssl=ssl_context)` is the documented egress path for
  enterprise TLS interception, and it is plain `ssl`/`aiohttp` config being
  passed through, not a LiteLLM security control. The relevant security note
  is the lifecycle one: an unclosed or prematurely-closed session is an
  availability dependency, in the same family as Ch06's
  "a guardrail in the request path is an availability dependency."

## Extraction Notes

- Source read in full. Fetched twice this session — once via WebFetch as
  markdown and once as raw HTML (`curl`, 73,345 bytes) — because the markdown
  renderer collapsed the code blocks' newlines. The note's code blocks and every
  `Quote` field are transcribed from the raw HTML `<pre><code>` spans and
  paragraph text, character-for-character. No quote is spliced across
  non-adjacent sentences; the one multi-sentence quote (the Scope admonition,
  under Concrete Artifacts) is a contiguous run of the source's own paragraph,
  and the paragraph break is the source's own. The `.md` route
  (`/docs/completion/http_handler_config.md`) returns 404 and the page is not
  present at the usual `docs/my-website/docs/completion/` path on
  `BerriAI/litellm@main`, so the rendered page is the source of record.
- **No linked sub-pages were followed** (MINER §1 allows up to 5). The page's
  only outbound links are its own nav siblings (`usage`, `/completions`), the
  Enterprise footer (marketing, per the Prospector), and a link to the
  LiteLLM Enterprise page. None is substantive relative to this page, which is
  self-contained. The nearest *related* page by subject,
  `/docs/aiohttp_benchmarks`, was deliberately **not** followed: it is the
  subject of the **rejected** issue #1380 (rejected 2026-09-19 on staleness —
  it benchmarks v1.71.1 from May 2025 and its `USE_AIOHTTP_TRANSPORT` lever has
  since been inverted to `DISABLE_AIOHTTP_TRANSPORT`). Reading a rejected
  source for corroboration would reintroduce exactly the stale guidance that
  got it rejected. Its rejection reasoning is used only as a contrast in
  Claim 7, and is cited as a rejected issue, never as evidence.
- **Contradiction decision (no issue filed, per MINER §4a "when NOT to
  file").** Two candidates were examined and both resolve to scope, not
  opposition:
  1. *#1380's rejected finding vs. this page.* The #1380 triage concluded
     that aiohttp is now LiteLLM's **default transport** (opt-out via
     `DISABLE_AIOHTTP_TRANSPORT`), which on its face reads as opposed to this
     page's "only `aiohttp_openai/` uses aiohttp; plain `openai/` goes through
     httpx." They are different layers: #1380 concerns the transport that
     LiteLLM's httpx-shaped clients use globally, this page concerns a
     per-provider handler (`BaseLLMAIOHTTPHandler`) reachable from a model
     prefix. Both can be true simultaneously. Decisive: #1380 is
     `rejected`/closed and therefore not a corpus source, so there is no
     claim in the corpus to contradict, and the in-corpus benchmarks note
     (`docs-litellm-benchmarks.md`, Extraction Notes) states outright that
     the `/docs/benchmarks` page "contains zero `aiohttp` mentions". `CONTRADICTIONS.md`
     has no entries and the nine open `contradiction`-labeled issues (#1150,
     #1307, #1322, #1338, #1352, #1408, #1461, #1462, #1486) cover routing
     flavors, g-eval judges, A2A budget storage, batch paths, agent cards,
     missing-trace semantics, `thinking.summary`, advisor-tool pairings, and
     promptfoo rubric portability — none touches transport, session lifecycle,
     or handler injection.
  2. *The page against itself (Claim 3).* The Scope admonition names "Topaz
     image variations" as in-scope for the handler and, two sentences later,
     states that the assignment does not change that path. That is a real
     internal tension and a genuinely useful one — but it is a gap in the
     *documentation of a mechanism*, not two opposing claims about how the
     mechanism behaves. The page asserts one thing (the assignment does not
     reach the image path) and merely lists Topaz in an earlier scope
     sentence. Per §4a's "one side is so weakly supported it doesn't rise to
     a real claim," this is handled as Claim 3 + a Guide Impact note, not a
     verdict. The Smith should treat "how do you actually inject a handler
     into `litellm.images.main`?" as an open question for the maintainers.
  No contradiction issue was filed.
- **Cross-reference verification (MINER §4b)**: `miner-related-notes.md` was
  read before writing Cross-References; all ten candidate paths are cited or
  dismissed above. Every `Claim N` cited was re-read in its source note before
  being written here, and the two quoted passages from other notes
  (`docs-litellm-claude-code-context-management.md` Claim 5; the
  `docs-litellm-gateway-auth-reference.md` Claim 1 / Our-assessment phrasing;
  `docs-litellm-drop-params.md` Claim 9) were copied from those files, not
  reconstructed. Claim numbers were counted in document order per §4b where
  the notes do not number explicitly. Non-claim material is cited by section
  or note name, not by a claim number. Additional cross-references beyond the
  candidate list came from my own `source-notes/` and `guide/` searches for
  `aiohttp`, `BaseLLMAIOHTTPHandler`, `TCPConnector`, `ClientSession`,
  connection-pool, and silent-no-op phrasings.
- `confidence_overall` is **`emerging`**, matching the sibling LiteLLM docs
  notes (`docs-litellm-drop-params.md`, `docs-litellm-gateway-auth-reference.md`):
  this is vendor capability documentation with a concrete, non-obvious
  failure mode and copy-pasteable config, but no measured behavior, no
  independent validation, no version range, and no production experience
  report. The scope/assignment claims (1–3) are `settled` as statements about
  *documented product behavior* — the same framing the gateway-auth note used
  for its analogous "the two surfaces differ" observation — while the numeric
  configuration values (7–8) are explicitly **not** graded as evidence, since
  the page derives none of them.
- **Scope limit worth flagging to the Smith**: this feature is configured from
  **Python process code** (module assignment, or a `lifespan` hook), not from
  `config.yaml`. The page never says so. An operator reading the guide's
  gateway-configuration sections could reasonably assume this is a `config.yaml`
  knob; it is not, which materially changes how it can be rolled out (a code
  change / restart, not a reload) and therefore how it interacts with the
  config-change canary machinery in Ch05.
