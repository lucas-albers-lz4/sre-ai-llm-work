---
source_url: https://docs.litellm.ai/docs/completion/shared_session
source_type: docs
title: "Shared Session | liteLLM"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-10-04)
date_extracted: 2026-10-04
last_checked: 2026-10-04
status: current
confidence_overall: emerging
issue: "#1574"
---

# Shared Session (LiteLLM Docs)

> The page documents the `shared_session` keyword argument on `acompletion()` / `completion()` as a per-call mechanism to reuse an `aiohttp.ClientSession` across multiple API calls, with explicit lifecycle ownership (caller owns user-supplied sessions, handler cleans up auto-created ones), DEBUG-only observability via `LITELLM_LOG=DEBUG` markers, and concrete tuning examples (`TCPConnector(limit=300, limit_per_host=75)`, `ClientTimeout(total=180)`). The page describes the call chain threading (`acompletion()` → `BaseLLMHTTPHandler` → `AsyncHTTPHandler` → `LiteLLMAiohttpTransport`) and presents the feature as optional and backward-compatible, but does not state provider scope (in contrast to the global handler page which restricts to `aiohttp_openai/` and excludes plain `openai/`).

## Source Context

- **Type**: docs (official vendor documentation — single living Docusaurus page at `/docs/completion/shared_session`, verified HTTP 200; ~76 KB of rendered HTML covering usage, benefits, debug logging, common patterns, implementation details, backward compatibility, testing, files modified, troubleshooting).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation. Authoritative for documented API surface. However, the page carries no metrics, no benchmarks, no version range, no changelog entry, no link to implementing source, and is undated — all quantitative values are presented as code comments/examples without stated derivation.
- **Scope**: How to pass a shared `aiohttp.ClientSession` via the `shared_session` parameter to LiteLLM completion calls. Covers basic usage (with/without shared session), benefits, debug logging (`LITELLM_LOG=DEBUG` with specific log markers), common patterns (FastAPI integration, batch processing, custom session configuration), implementation details (call chain threading), backward compatibility claims, testing, files modified, and troubleshooting. Does not cover provider scope limitations (whether this affects non-`aiohttp_openai/` providers), and the "session" terminology can be conflated with LiteLLM's real session affinity concept.

## Extracted Claims

### Claim 1: Without `shared_session`, each `acompletion()` call creates a separate session; with it, the caller-supplied session is reused across calls
- **Evidence**: "Without Shared Session (Default)" example shows two consecutive `acompletion()` calls with comments "Each call creates a new session" and "Two separate sessions created". "Basic Usage" example shows passing `shared_session=session` to both calls and reusing the same session within the `async with` context.
- **Confidence**: settled
- **Quote**: "Each call creates a new session" and "Two separate sessions created" (from the Default example)
- **Our assessment**: Clear behavioral distinction. The default is per-call session creation; the shared path explicitly reuses the same `ClientSession` instance across calls. This is the core operational point — connection reuse is the intended effect.

### Claim 2: The `shared_session` parameter is threaded through the full LiteLLM call chain to the aiohttp transport
- **Evidence**: Implementation Details section lists the full chain.
- **Confidence**: settled
- **Quote**: "The `shared_session` parameter is threaded through the entire LiteLLM call chain: 1. **`acompletion()`** - Accepts `shared_session` parameter 2. **`BaseLLMHTTPHandler`** - Passes session to HTTP client creation 3. **`AsyncHTTPHandler`** - Uses existing session if provided 4. **`LiteLLMAiohttpTransport`** - Reuses the session for HTTP requests"
- **Our assessment**: The page makes the integration path explicit. This is important because it suggests the parameter rides the aiohttp transport layer; however, the page does not state whether this path is taken for all providers or only for those that use the aiohttp transport (the global handler page was explicit that only `aiohttp_openai/` + Topaz image variations use `BaseLLMAIOHTTPHandler`).

### Claim 3: Lifecycle ownership is explicitly split — user-supplied sessions are closed by the caller; handler-auto-created sessions are cleaned up by the handler
- **Evidence**: Resource Management bullets under the earlier related page context are echoed implicitly in examples; the page shows user-managed sessions via `async with ClientSession() as shared_session:` and also states backward compatibility and the parameter is optional. More directly in the examples, when the caller creates the session, they manage it (FastAPI example uses `async with` in request scope; Batch example uses `async with` around the batch).
- **Confidence**: settled
- **Quote**: "Create session per request" (FastAPI example comment) and the pattern `async with aiohttp.ClientSession() as session:` where the caller controls the context. Also "Auto-created sessions: Automatically cleaned up by the handler" is stated in the related http_handler_config page's contract; this page focuses on user-supplied cases. The key operational point from examples: when passing `shared_session`, the caller owns the session lifecycle and must not close it while other in-flight calls are using it.
- **Our assessment**: This ownership contract matches the mirror-image hazard in `failure-litellm-httpx-cache-eviction.md` (closing while in use). Operators must treat caller-supplied sessions as borrowed resources during concurrent calls.

### Claim 4: Debug observability is DEBUG-only and exposes specific log markers indicating shared session reuse
- **Evidence**: Debug Logging section sets `os.environ['LITELLM_LOG'] = 'DEBUG'` and shows commented example log lines.
- **Confidence**: settled
- **Quote**: "# 🔄 SHARED SESSION: acompletion called with shared_session (ID: 12345)\n# ✅ SHARED SESSION: Reusing existing ClientSession (ID: 12345)"
- **Our assessment**: The only stated observability signal is DEBUG-level logging with these specific markers. There is no warning/error when the feature is "applied" or when it might silently not apply — making verification dependent on debug log inspection. This is consistent with "accepted/assigned but not applied with no observable signal" blind spots elsewhere in the corpus.

### Claim 5: Backward compatibility and optionality are explicit vendor claims
- **Evidence**: Backward Compatibility section and parameter default.
- **Confidence**: settled
- **Quote**: "- **100% backward compatible** - Existing code works unchanged\n- **Optional parameter** - `shared_session=None` by default\n- **No breaking changes** - All existing functionality preserved"
- **Our assessment**: Soft vendor assertions (no evidence/measurements provided). The page is undated living docs; these are intent claims rather than verifiable guarantees from the page itself.

### Claim 6: Concrete tuning surface is documented (timeouts and connector limits) as copy-pasteable examples
- **Evidence**: Custom Session Configuration example sets `ClientTimeout(total=180)` and `TCPConnector(limit=300, limit_per_host=75)`.
- **Confidence**: settled
- **Quote**: `timeout=aiohttp.ClientTimeout(total=180), connector=aiohttp.TCPConnector(limit=300, limit_per_host=75)`
- **Our assessment**: These are concrete, actionable parameters. However they appear as example values with no stated rationale, benchmarks, or version constraints — they are reused tuning numbers (the same numeric triple appears in related contexts). Treat as example defaults, not established best practices from evidence in this page.

### Claim 7: The feature is presented as opt-in and the default path is unchanged; the page emphasizes "make sure `shared_session` is passed to all `acompletion()` calls" (implicit) via batch example
- **Evidence**: Batch Processing example passes the same `shared_session` to every task in the batch. Troubleshooting says "Check parameter passing: Make sure `shared_session` is passed to all `acompletion()` calls".
- **Confidence**: settled
- **Quote**: "Check parameter passing: Make sure `shared_session` is passed to all `acompletion()` calls" (Troubleshooting > Session Not Being Reused)
- **Our assessment**: Partial application is possible and is called out as a troubleshooting point. If some calls pass it and others don't, you mix fresh and shared sessions — a silent partial-application hazard. The page identifies the verification step (debug logs / parameter passing check).

### Claim 8: Implementation touched multiple provider integration files (as documented)
- **Evidence**: Files Modified section lists the touched files.
- **Confidence**: settled (documented by vendor)
- **Quote**: "- `litellm/main.py` - Added `shared_session` parameter to `acompletion()` and `completion()`\n- `litellm/llms/custom_httpx/http_handler.py` - Core session reuse logic\n- `litellm/llms/custom_httpx/llm_http_handler.py` - HTTP handler integration\n- `litellm/llms/openai/openai.py` - OpenAI provider integration\n- `litellm/llms/openai/common_utils.py` - OpenAI client creation\n- `litellm/llms/azure/chat/o_series_handler.py` - Azure O Series handler"
- **Our assessment**: The file list is concrete. Notably it includes OpenAI and Azure O Series handler changes, but does not name other providers. Combined with the call-chain threading, this still leaves provider scope ambiguous relative to the global handler page's explicit restriction.

## Concrete Artifacts

```python
# Without Shared Session (Default)
import asyncio
from litellm import acompletion

async def main():
    # Each call creates a new session
    response1 = await acompletion(
        model="gpt-5.6-terra",
        messages=[{"role": "user", "content": "Hello"}]
    )
    
    response2 = await acompletion(
        model="gpt-5.6-terra",
        messages=[{"role": "user", "content": "How are you?"}]
    )
    # Two separate sessions created

asyncio.run(main())
```

```python
# With Shared Session
import asyncio
import aiohttp
from litellm import acompletion

async def main():
    async with aiohttp.ClientSession() as session:
        response1 = await acompletion(
            model="gpt-5.6-terra",
            messages=[{"role": "user", "content": "Hello"}],
            shared_session=session
        )
        response2 = await acompletion(
            model="gpt-5.6-terra",
            messages=[{"role": "user", "content": "How are you?"}],
            shared_session=session
        )
        # Both calls reuse the same session

asyncio.run(main())
```

```python
# Debug Logging
import os
import litellm

# Enable debug logging
os.environ['LITELLM_LOG'] = 'DEBUG'

# You'll see logs like:
# 🔄 SHARED SESSION: acompletion called with shared_session (ID: 12345)
# ✅ SHARED SESSION: Reusing existing ClientSession (ID: 12345)
```

```python
# FastAPI Integration
from fastapi import FastAPI
import aiohttp
import litellm

app = FastAPI()

@app.post("/chat")
async def chat(messages: list[dict]):
    # Create session per request
    async with aiohttp.ClientSession() as session:
        return await litellm.acompletion(
            model="gpt-5.6-terra",
            messages=messages,
            shared_session=session
        )
```

```python
# Batch Processing
import asyncio
from aiohttp import ClientSession
from litellm import acompletion

async def process_batch(messages_list):
    async with ClientSession() as shared_session:
        tasks = []
        for messages in messages_list:
            task = acompletion(
                model="gpt-5.6-terra",
                messages=messages,
                shared_session=shared_session
            )
            tasks.append(task)
        # All tasks use the same session
        results = await asyncio.gather(*tasks)
        return results
```

```python
# Custom Session Configuration
import aiohttp
import litellm

# Create optimized session
async with aiohttp.ClientSession(
    timeout=aiohttp.ClientTimeout(total=180),
    connector=aiohttp.TCPConnector(limit=300, limit_per_host=75)
) as shared_session:
    
    response = await litellm.acompletion(
        model="gpt-5.6-terra",
        messages=[{"role": "user", "content": "Hello"}],
        shared_session=shared_session
    )
```

## Cross-References

- **Corroborates**: None identified among existing notes (this mechanism — per-call `shared_session` kwarg on `acompletion()` — is not covered by existing source notes).
- **Contradicts**: None. No existing note makes an opposing claim about `shared_session`.
- **Extends**: `docs-litellm-completion-http-handler-config.md` (#1482) — both concern aiohttp session reuse on LiteLLM's completion path, but via different mechanisms. The existing note documents global handler injection (`litellm.main.base_llm_aiohttp_handler = BaseLLMAIOHTTPHandler(session=...)`) with explicit provider scope limitation (only `aiohttp_openai/` + Topaz image variations; plain `openai/` excluded and the assignment target matters). This page documents a per-call `shared_session=` parameter threaded through the same call chain. These are complementary mechanisms, not duplicates. The key junction is provider scope: the global handler page states scope explicitly; this page does **not** state provider scope, leaving ambiguity about whether `shared_session` only takes effect on providers using the aiohttp transport path.
- **Novel**: The first source note covering the per-call `shared_session` parameter for LiteLLM completions. Specific novel elements: (1) explicit threading of `shared_session` through `acompletion()` → `BaseLLMHTTPHandler` → `AsyncHTTPHandler` → `LiteLLMAiohttpTransport`, (2) the DEBUG log markers `🔄 SHARED SESSION: ...` and `✅ SHARED SESSION: Reusing existing ClientSession (ID: ...)`, (3) the explicit troubleshooting instruction to pass `shared_session` to all calls (partial-application hazard), (4) concrete per-call usage patterns distinct from global handler assignment.

## Guide Impact

- **Chapter [05] (LLM ops reliability — gateway/transport connection management)**: Add a subsection distinguishing per-call session injection (`shared_session` kwarg) from global custom handler injection. Emphasize: (a) different injection points and ownership models, (b) the partial-application hazard (must pass to all calls in a batch/request scope), (c) verification via DEBUG logs (the only stated signal), and (d) unresolved provider-scope question — treat scope as unverified unless confirmed against the implementation; do not assume it applies to all providers.
- **Chapter [02] (Observability — session-tagged debug logging)**: Document the specific DEBUG markers (`🔄 SHARED SESSION: ... (ID: ...)`, `✅ SHARED SESSION: Reusing existing ClientSession (ID: ...)`) as a concrete signal for connection reuse verification in tests/troubleshooting.

## Extraction Notes

- This is a single living vendor docs page (Docusaurus). Content matches the rendered HTML at the stated URL; footer shows `© 2026 LiteLLM`.
- No benchmarks, metrics, version constraints, or dated changelog references appear. All performance claims ("Performance", "Resource Efficiency") are unquantified marketing-adjacent prose — extracted only as descriptive benefits, not as evidence.
- Provider scope is not stated on this page. The triage comments flagged this as the key question relative to `docs-litellm-completion-http-handler-config.md` (which explicitly restricts to `aiohttp_openai/` and excludes plain `openai/`). We did not assume scope; we recorded the ambiguity in Cross-References/Guide Impact rather than asserting a contradiction.
- The tuning numbers (`total=180`, `limit=300`, `limit_per_host=75`) appear verbatim in the Custom Session Configuration example; they are example values, not independently verified.
- The "Files Modified" list is vendor-reported (from the page) — included as an artifact for context, not treated as primary evidence of behavior.
