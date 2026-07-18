---
source_url: https://docs.litellm.ai/blog/fastapi-middleware-performance
source_type: blog-post
title: "Your Middleware Could Be a Bottleneck"
author: "Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM), Ryan Crabbe (Performance Engineer, LiteLLM)"
date_published: 2026-02-07
date_extracted: 2026-07-18
last_checked: 2026-07-18
status: current
confidence_overall: emerging
issue: "#324"
---

# Your Middleware Could Be a Bottleneck

> A practitioner optimization report from LiteLLM documenting how Starlette's
> `BaseHTTPMiddleware` allocates 7 intermediate objects/tasks per request (even
> for a no-op passthrough), and how replacing a single `BaseHTTPMiddleware`
> subclass with a pure ASGI middleware yielded +74% throughput and -38% median
> latency on their proxy server — with a reproducible benchmark script. The
> pattern generalizes to any FastAPI-based LLM gateway or proxy.

## Source Context

- **Type**: blog-post (vendor engineering performance post), tagged `performance`,
  `fastapi`, `middleware`.
- **Author credibility**: High — co-authored by LiteLLM's CEO (Krrish Dholakia),
  CTO (Ishaan Jaffer), and Performance Engineer (Ryan Crabbe). The post includes
  a fully reproducible benchmark script, before/after code with line-level
  implementation detail, and the overhead breakdown is a structural property
  of Starlette's own codebase (verifiable independently).
- **Scope**: Covers (1) the 7-object overhead breakdown of Starlette's
  `BaseHTTPMiddleware`, (2) a before/after benchmark isolating middleware
  overhead (Apache Bench, 50K requests, 1K concurrent, 1 worker), (3) the
  pure-ASGI middleware replacement pattern, (4) the specific
  `PrometheusAuthMiddleware` before/after code, (5) the static-analysis check
  introduced to prevent regression. Does NOT cover: other optimization
  components within the ~30% overall reduction, general FastAPI performance
  beyond middleware, or alternative middleware libraries.

## Extracted Claims

### Claim 1: Starlette's `BaseHTTPMiddleware` creates 7 intermediate objects and tasks per request, even for a pure no-op passthrough
- **Evidence**: The article enumerates all 7 steps: Request Wrapping (`_CachedRequest`),
  Sync Event (`anyio.Event()`), Memory Stream (`create_memory_object_stream()`),
  Task Group (`create_task_group()`), Background Task (`task_group.start_soon(coro)`),
  Nested Task Group (`receive_or_disconnect()`), Response Wrapping (`_StreamingResponse`).
  This is a structural property of the Starlette library, not a LiteLLM-specific claim.
- **Confidence**: settled (verifiable against Starlette source code)
- **Quote**: "On every request, even a pure passthrough (meaning nothing happens),
  BaseHTTPMiddleware creates 7 intermediate objects and tasks"
- **Our assessment**: This is the core analytical contribution of the post — a concrete,
  itemized breakdown of what `BaseHTTPMiddleware` does per request. Anyone can verify
  by inspecting Starlette's `middleware/base.py`. The 7-object figure is not a
  measurement artifact; it is a structural count of allocations and tasks. This is
  the highest-value extract for the guide.

### Claim 2: Pure ASGI middleware costs only 2 steps per request (scope check + direct call) and avoids all allocation overhead
- **Evidence**: The side-by-side comparison shows the pure ASGI path: scope type check
  (`scope["type"] != "http"`) followed by direct delegation (`await self.app(scope, receive, send)`).
- **Confidence**: settled (trivially verifiable property of the ASGI protocol)
- **Quote**: "Compare that to a pure ASGI middleware, which we can have just check the
  request path and continue along. 2 steps per request: 1 Scope Check — scope[\"type\"] != \"http\";
  2 Direct Call — await self.app(scope, receive, send)"
- **Our assessment**: The contrast is clean and the ASGI pattern is straightforward.
  The key insight is that for middleware that does nothing on most requests (Claim 4),
  the 2-step path essentially eliminates overhead: no objects, no task groups, no
  streams. This is the actionable replacement pattern.

### Claim 3: Replacing one `BaseHTTPMiddleware` with a pure ASGI middleware yielded +74% throughput and -38% median latency
- **Evidence**: Benchmark results from Apache Bench (50,000 requests, 1,000 concurrent,
  1 uvicorn worker). Before (1 ASGI + 1 BaseHTTPMiddleware): 3,596–4,161 RPS, 21ms P50.
  After (2x pure ASGI): 6,504–6,631 RPS, 13ms P50. Full per-run table published.
- **Confidence**: settled (reproducible benchmark with published script)
- **Quote**: "+74% Throughput (RPS)"
- **Quote**: "-38% Median Latency (P50)"
- **Quote**: "50,000 requests · 1,000 concurrent · 1 worker"
- **Our assessment**: These are the headline numbers. The methodology is sound — the
  endpoint (`GET /health` → `PlainTextResponse("ok")`) does zero work to isolate
  middleware overhead, and the single-worker design means the benchmark measures
  per-event-loop cost, not horizontal scalability. The improvements are large but
  are specifically for *middleware overhead* on a no-op path; real endpoints with
  substantive work would see smaller relative gains. The benchmark is fully
  reproducible (see Concrete Artifacts), which is a significant strength.

### Claim 4: The `PrometheusAuthMiddleware` does nothing on ~99.9% of requests — it only authenticates the `/metrics` endpoint
- **Evidence**: The post states that the middleware authenticates requests to `/metrics`,
  is off by default (requires a config flag), and even when enabled, the vast majority
  of proxy requests are not to `/metrics`.
- **Confidence**: settled (stated architectural fact about LiteLLM's own proxy)
- **Quote**: "For a middleware that for us, does nothing on 99.9% of requests, paying
  this cost doesn't make sense."
- **Our assessment**: This is the context that makes the optimization meaningful — if
  the middleware did substantive work on most requests, the overhead would be
  amortized. The pattern is: a middleware that acts on a tiny fraction of traffic
  but wraps every request in `BaseHTTPMiddleware` overhead is a performance
  anti-pattern. This is generalizable to any FastAPI service with a narrow-purpose
  middleware.

### Claim 5: The replacement pure ASGI middleware costs "one dict lookup, one string check, and one function call" on the common path, with zero allocations
- **Evidence**: The final code block shows the early-return pattern: check `scope["type"]`
  and path, `await self.app()` immediately if not `/metrics`. The post explicitly states
  the cost.
- **Confidence**: settled (the code is published and the cost statement is consistent
  with the code)
- **Quote**: "For the 99.9% of requests that aren't hitting /metrics, the middleware is
  now one dict lookup, one string check, and one function call. No objects allocated,
  no tasks spawned."
- **Our assessment**: The early-return pattern is the technique: short-circuit before
  doing any work, and stay in the ASGI protocol (scope/receive/send) rather than
  promoting to Starlette's Request/Response layer unless necessary. This is the
  concrete pattern to recommend in the guide.

### Claim 6: LiteLLM added a static analysis check to prevent re-introducing `BaseHTTPMiddleware` subclasses for simple use cases
- **Evidence**: Stated in the article's closing section as an ongoing measure.
- **Confidence**: emerging (stated intent without published linter rule or code reference)
- **Quote**: "We're now putting in a static analysis check to prevent this from happening
  again with any newly introduced middlewares. If we find the use case is necessary then
  that's okay and we'll reevalute but for everything LiteLLM needs to do at the moment
  it's not."
- **Our assessment**: A good process addition — static analysis enforcement makes this
  one-time optimization durable against future regressions. The "if we find the use case
  is necessary" caveat is important: `BaseHTTPMiddleware` is not universally bad, it
  provides request/response-level abstractions that are useful for middleware that needs
  to inspect or modify request/response bodies. The post's position is that simple
  middleware (check path, delegate) should use ASGI; complex middleware may still need
  `BaseHTTPMiddleware`. The Assayer should note the typo in the source ("reevalute").

### Claim 7: This middleware change was part of a broader optimization effort yielding ~30% reduction in proxy overhead over two weeks
- **Evidence**: Stated in the article's final paragraph.
- **Confidence**: anecdotal (aggregate across all optimizations, not attributed to the
  middleware change alone)
- **Quote**: "Across all optimizations combined, we've measured about a 30% reduction
  in proxy overhead over the past two weeks."
- **Our assessment**: The 30% figure is the aggregate of all optimizations, not just
  this middleware change — the middleware change's standalone contribution is the
  +74% / -38% numbers in Claim 3. The 30% is useful context (the middleware change
  was a meaningful component of a larger effort) but should not be cited as attributable
  to the middleware change alone.

## Concrete Artifacts

All artifacts below are extracted from the source page. Code is reproduced from the
rendered page; formatting is normalized to valid syntax without altering tokens.

### Proxy config flag to enable the middleware (verbatim YAML)

```yaml
litellm_settings:
    require_auth_for_metrics_endpoint: true
```

### Before: original `PrometheusAuthMiddleware` (BaseHTTPMiddleware subclass) — verbatim from the page

```python
class PrometheusAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if self._is_prometheus_metrics_endpoint(request):
            if self._should_run_auth_on_metrics_endpoint() is True:
                try:
                    await user_api_key_auth(request=request, api_key=...)
                except Exception as e:
                    return JSONResponse(status_code=401, content=...)
        response = await call_next(request)
        return response

    @staticmethod
    def _is_prometheus_metrics_endpoint(request: Request):
        if "/metrics" in request.url.path:
            return True
        return False
```

### After: replacement pure ASGI middleware — verbatim from the page

```python
class PrometheusAuthMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or "/metrics" not in scope.get("path", ""):
            await self.app(scope, receive, send)
            return
        if litellm.require_auth_for_metrics_endpoint is True:
            request = Request(scope, receive)
            api_key = request.headers.get("Authorization") or ""
            try:
                await user_api_key_auth(request=request, api_key=api_key)
            except Exception as e:
                # send 401 directly via ASGI protocol
                ...
                return
        await self.app(scope, receive, send)
```

### Benchmark script (`benchmark_middleware.py`) — verbatim from the post

```python
import argparse
import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

class NoOpBaseHTTPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        return await call_next(request)

class NoOpPureASGIMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.app(scope, receive, send)

def create_app(middleware_type: str | None = None, layers: int = 2) -> FastAPI:
    app = FastAPI()
    @app.get("/health")
    async def health():
        return PlainTextResponse("ok")
    if middleware_type == "mixed":
        app.add_middleware(NoOpBaseHTTPMiddleware)
        app.add_middleware(NoOpPureASGIMiddleware)
    elif middleware_type == "asgi":
        for _ in range(layers):
            app.add_middleware(NoOpPureASGIMiddleware)
    return app

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--middleware", choices=["asgi", "mixed"], default=None)
    parser.add_argument("--layers", type=int, default=2)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    app = create_app(middleware_type=args.middleware, layers=args.layers)
    uvicorn.run(app, host="0.0.0.0", port=args.port, workers=1, log_level="warning")
```

### Benchmark results (per-run table — verbatim from the post)

```
50,000 requests · 1,000 concurrent · 1 worker

Before (1 ASGI + 1 BaseHTTP)
Config                 Run    RPS      P50 (ms)
Before (1 ASGI+BaseHTTP)  1    3,596    21
Before (1 ASGI+BaseHTTP)  2    3,599    21
Before (1 ASGI+BaseHTTP)  3    4,161    21

After (2x Pure ASGI)
Config                 Run    RPS      P50 (ms)
After (2x Pure ASGI)      1    6,504    13
After (2x Pure ASGI)      2    6,631    13
After (2x Pure ASGI)      3    6,595    13

Improvements:
+74% Throughput (RPS)
-38% Median Latency (P50)
```

### 7-object overhead pipeline (reconstructed from the post's flow diagram)

The post renders this as a vertically-stacked pipeline graphic. The text labels
for each step, in order from 1 to 7, are:

```
1  Request Wrapping       _CachedRequest
2  Sync Event             anyio.Event()
3  Memory Stream          create_memory_object_stream()
4  Task Group             create_task_group()
5  Background Task        task_group.start_soon(coro)
6  Nested Task Group      receive_or_disconnect()
7  Response Wrapping      _StreamingResponse
```

### Benchmark methodology description (verbatim)

> "A minimal FastAPI app serves GET /health → PlainTextResponse(\"ok\"). The endpoint
> does zero work to isolate the middleware overhead: any difference between configs
> is purely the cost of the middleware plumbing itself."

> "Apache Bench (ab) fires requests at the server with 1,000 concurrent connections
> and a single uvicorn worker. One worker means one event loop, so the benchmark
> directly measures how each middleware design handles concurrent load on a single
> thread."

## Cross-References

- **Corroborates**: None directly. No existing source note covers FastAPI middleware
  overhead, the `BaseHTTPMiddleware` → pure ASGI migration pattern, or a generic
  proxy-middleware optimization benchmark. The LiteLLM April townhall note
  (`blog-litellm-april-townhall-updates.md`, Claim 9) mentions "Investigate latency
  overhead for long-running Claude Code requests" as a reliability investment —
  conceptually adjacent (both are about LiteLLM proxy latency), but that claim is
  about *long-running agent requests* measured from the outside, while this post is
  about *per-request middleware overhead* measured at the proxy internals level.
  Different mechanism, compatible direction.

- **Contradicts**: None. No existing source note asserts that `BaseHTTPMiddleware`
  is optimal or that its overhead is negligible. No contradiction issue filed.

- **Extends**:
  - `blog-litellm-april-townhall-updates.md` — that note's reliability/investment
    claim (10k+ RPS uptime target, latency overhead investigation) is grounded, in
    part, by the concrete optimization patterns in this post. LiteLLM's proxy
    middleware was one concrete source of latency they systematically measured and
    reduced. Together the two notes bracket LiteLLM's performance work: one shows
    the targets and roadmap, the other shows the executed measurement-and-fix cycle
    for one specific subsystem.
  - `failure-litellm-wildcard-model-access-desync.md` — that incident report
    documents a failure in LiteLLM's *access control* layer at the proxy level.
    This post documents a performance optimization in LiteLLm's *middleware* layer
    at the proxy level. Both are about the LiteLLM proxy internals, but different
    subsystems (auth logic vs. middleware plumbing). The guide should treat them as
    complementary: the proxy has multiple concern-layers (auth, routing, middleware)
    each with its own failure and optimization patterns.

- **Novel**: First source note in the corpus to introduce:
  - The `BaseHTTPMiddleware` 7-object overhead breakdown as a concrete, actionable
    performance anti-pattern for FastAPI-based LLM gateways.
  - The pure-ASGI middleware replacement pattern (class with `__init__(self, app)`
    and `__call__(self, scope, receive, send)`) with before/after code diff.
  - A reproducible middleware-overhead benchmarking methodology (Apache Bench,
    50K/1K/1-worker, zero-work endpoint, per-run tables).
  - The early-return pattern for narrow-purpose middleware that acts on a tiny
    fraction of traffic: check scope path → `await self.app()` if not a match.
  - Static analysis enforcement as a process guard against middleware base-class
    misuse in proxy/LLM-infra projects.

## Guide Impact

- **Chapter 02 (Architecture & Infrastructure — LLM proxy/gateway optimization)**:
  Add the `BaseHTTPMiddleware` → pure ASGI migration pattern as a concrete,
  evidence-backed optimization for any FastAPI-based LLM gateway or proxy. Specific
  additions:
  - The 7-object overhead breakdown (Claim 1) as a diagnostic checklist: if a
    middleware is a narrow passthrough for most requests, profile it with this
    framework.
  - The early-return ASGI pattern (Claims 2, 5) as the replacement template: check
    scope type and path, short-circuit via `await self.app()`, only promote to
    Starlette Request/Response objects when actual work is needed.
  - The "99.9% waste" heuristic (Claim 4): when a middleware acts on <1% of traffic,
    wrapping it in `BaseHTTPMiddleware` is likely a performance bug. Estimate the
    fraction of traffic a middleware acts on; if the fraction is tiny, the overhead
    is not amortized.
  - The static-analysis enforcement pattern (Claim 6) as a process guard for
    proxy/infra teams that own FastAPI services: lint against
    `BaseHTTPMiddleware` subclass patterns that can be replaced with pure ASGI.

- **Chapter 05 (LLM Ops Reliability — capacity and throughput)**:
  - Add the benchmark methodology (50K requests, 1K concurrent, 1 worker, zero-work
    endpoint) as a reusable template for isolating middleware overhead in LLM
    proxy capacity testing. The "one worker to measure per-event-loop cost" design
    is a specific methodological choice worth documenting.
  - Add the observed improvement magnitudes as reference ranges (+74% throughput,
    -38% median latency) for similar middleware-optimization efforts — with the
    caveat (from Our assessment, Claim 3) that real endpoints with substantive work
    will see smaller relative gains.
  - Reference the ~30% overall proxy overhead reduction (Claim 7) as context: this
    middleware change was one component of a broader optimization program, not a
    silver bullet.

## Extraction Notes

- Source read in full. Docusaurus blog post at
  `https://docs.litellm.ai/blog/fastapi-middleware-performance`, published
  February 7, 2026, by Krrish Dholakia (CEO), Ishaan Jaffer (CTO), and Ryan Crabbe
  (Performance Engineer). The page was fetched via direct HTTP and HTML-to-text
  extraction; all quoted passages were copied character-for-character from the
  rendered page text. The `quote` block in Claim 2 required escaping the double
  quotes around `"type"` to render valid markdown.
- The page is self-contained (a single blog post with no substantive sub-pages to
  follow). The two external links — Starlette Middleware documentation and Apache
  Bench documentation — are standard references, not substantive sub-pages per
  MINER.md §1. The sidebar links to related posts ("Incident Report: Invalid model
  cost map on main", "Improve release stability with 24 hour load tests",
  "Achieving Sub-Millisecond Proxy Overhead") were not followed; they are adjacent
  but not required for this extraction, and "Achieving Sub-Millisecond Proxy Overhead"
  may warrant its own source-note issue.
- `confidence_overall` set to `emerging` to match the sibling LiteLLM blog notes:
  the structural claims about BaseHTTPMiddleware internals (Claim 1) and the
  replacement pattern (Claim 2) are effectively settled properties of Starlette,
  but the performance impact figures (Claims 3, 7) are single-vendor, single-scenario
  measurements. The static-analysis claim (Claim 6) is an intent statement without
  published artifact. This mixes settled-structural and anecdotal-measurement claims
  under one note; `emerging` reflects the note as a whole.
- The 4th run in the "Before" table shows 4,161 RPS vs 3,596/3,599 for runs 1-2.
  This variance (run-to-run spread of ~16%) is not commented on in the source.
  Worth noting for the Assayer: the improvement is still large (+56% even against
  the best Before run), but the After runs are also tighter (6,504–6,631, spread
  ~2%), suggesting something changed between runs (possibly CPU turbo or background
  load). Not a contradiction — just noise typical of single-machine benchmarks.
- No contradiction issue filed: verified against all 31 existing source notes; the
  terms "FastAPI", "BaseHTTPMiddleware", "ASGI", "Starlette" match zero notes.
  The conceptually adjacent LiteLLM April townhall latency claim covers a different
  mechanism (long-running Claude Code reqests vs. per-request middleware overhead).
