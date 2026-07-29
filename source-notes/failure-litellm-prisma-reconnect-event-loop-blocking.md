---
source_url: https://docs.litellm.ai/blog/prisma-reconnect-blocking-incident
source_type: failure-report
platform: blog
title: "Incident Report: Prisma DB Reconnect Blocks the Event Loop and Kills Liveliness"
author: "Yuneng Jiang (Senior SWE, LiteLLM)"
date_published: 2026-04-29
date_extracted: 2026-07-29
last_checked: 2026-07-29
status: current
confidence_overall: settled
issue: "#645"
---

# Failure Report: LiteLLM Prisma Reconnect Blocks the Event Loop During DB Outages

> A synchronous `subprocess.Popen.wait()` hidden inside `prisma-client-py`'s async `Engine.aclose()` blocked the asyncio event loop for 30–120 seconds during Prisma reconnect on an unresponsive database. Because `asyncio.wait_for()` can only cancel at `await` points and there is no `await` inside `subprocess.wait()`, the safety timeout could not fire. `/health/liveliness` froze, Kubernetes liveness probes timed out, and the kubelet SIGKILLed the pod — converting a transient DB outage into a full proxy restart.

## Source Context

- **Platform**: Vendor engineering incident blog published on `docs.litellm.ai/blog`, authored by LiteLLM's Senior SWE Yuneng Jiang.
- **Author credibility**: High — vendor-authored incident report with clear root cause, code-level diffs, PR reference (#26225), verification metrics, and remediation guidance. LiteLLM is a widely-used open-source LLM gateway/proxy.
- **Scope**: A specific, fully root-caused and remediated production incident affecting Prisma-based Postgres reconnect under partial-failure (unresponsive, not hard-down) conditions. The failure pattern generalizes to a class: async library methods that wrap synchronous subprocess `wait()` calls, defeating asyncio timeout mechanisms.

## What Was Attempted

- **Goal**: Gracefully reconnect LiteLLM proxy's Prisma client to Postgres after a DB outage, with a safety timeout via `asyncio.wait_for()` so the event loop doesn't freeze.
- **Tool/approach**: LiteLLM proxy's Prisma reconnect path in `litellm/proxy/db/prisma_client.py` (`recreate_prisma_client`) and a now-removed direct-reconnect branch in `litellm/proxy/utils.py`. The intended flow: health watchdog detects DB query failures → `await self.db.disconnect()` → construct fresh `Prisma()` → `await new_client.connect()` → swap reference. The `/health/liveliness` route was intentionally DB-agnostic and expected to stay green.
- **Setup**: LiteLLM proxy deployed on Kubernetes with a single long-lived Prisma client for its Postgres metadata store (keys, teams, spend logs). Postgres behind a network boundary that can experience transient outages.

## What Went Wrong

- **Symptoms**: When upstream Postgres became unreachable, the Prisma reconnect path called `await self.db.disconnect()`, which froze the entire asyncio event loop for 30–120 seconds. `/health/liveliness` could not respond during the freeze. Kubernetes liveness probes timed out and the kubelet SIGKILLed the pod — "the proxy looked dead even though the underlying issue was a *transient* DB outage that the reconnect logic was supposed to ride through."
- **Severity**: High — pods killed and restarted instead of degrading gracefully and reconnecting once the DB came back.
- **Reproducibility**: Deterministic during DB outages where the engine's TCP close operations hang against an unresponsive database. Reproduced internally with `docker pause` on Postgres.

### Symptom A: `subprocess.Popen.wait()` in `prisma-client-py`'s `Engine.aclose()` blocked the asyncio event loop

- **Evidence**: Blog post's Root Cause section describes the exact code path. `prisma-client-py`'s `Engine.aclose()` is `async` from Python's perspective, but the implementation calls `self.process.wait()` — a synchronous, blocking call with no `await` point.
- **Quote**: "prisma-client-py's engine cleanup is internally synchronous. The library's Engine.aclose() looks async from Python's perspective, but the implementation that finally shuts down the Rust query-engine subprocess calls: self.process.send_signal(signal.SIGTERM); self.process.wait()  # <-- BLOCKING. Does not yield to the loop."
- **Confidence**: settled.

### Symptom B: `asyncio.wait_for()` safety timeout could not fire because there was no `await` point inside `subprocess.wait()`

- **Evidence**: The blog explicitly diagnoses why the existing `asyncio.wait_for()` wrapper was ineffective. Since `wait_for` can only cancel at `await` points, and `subprocess.wait()` is purely synchronous, the timeout never interrupted the freeze — the cancellation coroutine itself couldn't run.
- **Quote**: "The reconnect path was wrapped in asyncio.wait_for() as a 'safety timeout', but wait_for can only cancel at await points. There is no await inside subprocess.wait(), so the timeout could not fire. The loop simply did not run any coroutines — including the cancellation coroutine — until wait() returned on its own."
- **Confidence**: settled.

### Symptom C: `/health/liveliness` shared the event loop with the proxy's request handling, so a freeze anywhere in the loop killed it too

- **Evidence**: The blog's Lessons Learned section explicitly names this as a design vulnerability. The liveness route was intentionally cheap (no DB access) but it shared the asyncio loop with every other coroutine.
- **Quote**: "/health/liveliness was intentionally minimal so that it would survive a DB outage, but it shares the asyncio loop with every other request, so any synchronous blocking call elsewhere in the loop drags it down regardless of how cheap the route itself is."
- **Confidence**: settled.

## Root Cause (if identified)

- **Author's diagnosis**: `prisma-client-py`'s `Engine.aclose()` is `async` in name only — the underlying implementation calls `self.process.wait()` synchronously, blocking the event loop. When Postgres is unhealthy, the Rust query-engine subprocess's outbound TCP `close()` calls hang against the unresponsive database, and `wait()` blocks for 30–120 seconds. The existing `asyncio.wait_for()` wrapper was ineffective because it can only cancel at `await` points, and `subprocess.wait()` contains none.
- **Our assessment**: Correct and thorough analysis. The root cause is a *signature-reality mismatch*: the async method signature implies non-blocking behavior, but the implementation is synchronous. This is a particularly insidious failure pattern because the blocking call is invisible under healthy conditions (engine exits in milliseconds) and only manifests under partial failure (unresponsive, not hard-down) — the exact condition you'd most expect reconnect logic to handle gracefully.
- **Category**: genuine-bug (in `prisma-client-py`'s async API contract), but more broadly a **design failure pattern** where third-party library async APIs wrap synchronous subprocess calls without documentation or mitigation.

### Root-cause detail A: The blocking path only manifests under partial-failure (unresponsive DB, not hard-down)

- **Evidence**: The blog explicitly distinguishes between healthy and unhealthy conditions. Under healthy conditions the engine exits in milliseconds and the blocking call is invisible.
- **Quote**: "When the database is healthy the engine exits within milliseconds and the blocking call is invisible. When the database is unhealthy, the engine's own outbound TCP close() calls hang waiting for FIN/ACK from the unresponsive Postgres host, and wait() blocks the whole event loop for the duration."
- **Confidence**: settled.

### Root-cause detail B: Two code paths (recreate_prisma_client and the direct-reconnect branch in utils.py) had the same bug — only one was fixed initially

- **Evidence**: The blog describes two reconnect call sites and states that both now converge through the single `recreate_prisma_client` flow, with the "formerly-separate 'direct reconnect' branch in litellm/proxy/utils.py" also going through the same kill-then-recreate flow.
- **Quote**: "Both reconnect call sites — recreate_prisma_client and the formerly-separate 'direct reconnect' branch in litellm/proxy/utils.py — now go through recreate_prisma_client. The two engine-alive and engine-dead paths converge on the same kill-then-recreate flow, which removes a class of 'what if the engine died between checks' bugs."
- **Confidence**: settled.

## Recovery Path

- **What they switched to**: PR #26225 replaced `await self.db.disconnect()` with direct PID-based subprocess signaling: look up engine PID → `os.kill(pid, SIGTERM)` → `await asyncio.sleep(0.5)` (a real `await` that keeps the loop running) → `os.kill(pid, SIGKILL)` if still alive → construct and connect fresh Prisma client → swap reference.
- **Workaround**: As a stopgap, increase liveness probe timeout beyond worst-case `engine.wait()` duration (e.g., 180s) to reduce pod kills — but this does not fix the underlying event-loop freeze.
- **Unresolved**: None stated; status is Resolved with PR #26225 merged on April 29, 2026.

### Fix detail A: The fix uses process-level signals instead of library-level cleanup, which provides a deterministic, async-friendly shutdown

- **Evidence**: The blog's Lessons Learned #4 explicitly recommends this approach for wedged subprocesses. The code diff shows the exact implementation: SIGTERM → await sleep → SIGKILL.
- **Quote**: "Prefer process-level signals to library-level cleanup for unrecoverable subprocesses. When the engine has wedged on socket close, there is no graceful path that does not involve waiting on it. SIGTERM + bounded asyncio.sleep + SIGKILL gives a deterministic, async-friendly shutdown."
- **Confidence**: settled.

### Fix detail B: One test encoding the old "preserve engine on successful disconnect" invariant was removed as part of the fix

- **Evidence**: The blog states that `test_lightweight_reconnect_skips_kill_on_successful_disconnect` was removed because it "encoded the old 'preserve the engine on successful disconnect' invariant that was itself part of the bug."
- **Quote**: "One previously-passing test, test_lightweight_reconnect_skips_kill_on_successful_disconnect, encoded the old 'preserve the engine on successful disconnect' invariant that was itself part of the bug (prisma-client-py's aclose() kills the engine regardless) and was removed."
- **Confidence**: settled.

### Fix detail C: 40 unit tests across two test files were updated for the new code path

- **Evidence**: The blog explicitly states the count and file locations.
- **Quote**: "40 unit tests across tests/test_litellm/proxy/db/test_prisma_self_heal.py and tests/litellm/proxy/test_prisma_engine_watchdog.py were updated to reflect the new code path."
- **Confidence**: settled.

## Concrete Artifacts

**Incident metadata (verbatim from source):**
```
Date: April 2026
Duration: Multiple incidents across customer deployments before fix landed
Severity: High — surfaced as full proxy outages in Kubernetes
Status: Resolved
Note: This fix is available starting from the release that contains PR #26225
(merged April 29, 2026).
```

**Pre-fix code path (verbatim from source — Root Cause section):**
```python
self.process.send_signal(signal.SIGTERM)
self.process.wait()       # <-- BLOCKING. Does not yield to the loop.
```

**The fix diff from PR #26225 (verbatim from source, simplified):**
```python
- # Old: blocks event loop for as long as the engine takes to shut down
- await self.db.disconnect()
+ # New: signal the engine subprocess directly, yield via real await,
+ # then SIGKILL if it has not exited.
+ pid = self._get_engine_pid()
+ if pid is not None:
+     try:
+         os.kill(pid, signal.SIGTERM)
+     except ProcessLookupError:
+         pass
+ await asyncio.sleep(0.5)
+ if pid is not None:
+     try:
+         os.kill(pid, signal.SIGKILL)
+     except ProcessLookupError:
+         pass
```

**Verification metrics (verbatim from source):**

| Condition | max `/health/liveliness` latency | 2xx |
|-----------|----------------------------------|-----|
| Pre-fix, prod-like slow close (5s injected) | 10006 ms (probe timeout) | 99.7% |
| With this fix, same slow close injected | 52.7 ms | 100% |
| With this fix, natural run (no injection) | 78.8 ms | 100% |

**The four lessons learned (verbatim from source):**

> 1. **Don't trust async def for shutdown paths in third-party libraries.** An async signature only commits the library to a coroutine-shaped API; it does not commit to actually yielding. When the cost of *not* yielding is "the pod gets killed", verify behavior under partial failure (network partition, paused DB) — not just under "DB is healthy" or "DB is hard-down".
>
> 2. **asyncio.wait_for() is not a safety net for sync work.** It can only cancel at await points, so wrapping a blocking call in wait_for does not give you a timeout — it just hides the bug until something else (Kubernetes, a load balancer, a customer) does notice.
>
> 3. **Health checks belong on the same event loop as the work they describe.** /health/liveliness was intentionally minimal so that it would survive a DB outage, but it shares the asyncio loop with every other request, so any synchronous blocking call elsewhere in the loop drags it down regardless of how cheap the route itself is.
>
> 4. **Prefer process-level signals to library-level cleanup for unrecoverable subprocesses.** When the engine has wedged on socket close, there is no graceful path that does not involve waiting on it. SIGTERM + bounded asyncio.sleep + SIGKILL gives a deterministic, async-friendly shutdown.

**Operator guidance (verbatim from source):**
> If you saw any of the following symptoms on LiteLLM versions before this fix, the bug above is the most likely cause:
> - Kubernetes pods restarting repeatedly during transient Postgres incidents (RDS failovers, network partitions, brief CPU starvation on the DB).
> - /health/liveliness returning 200 most of the time but timing out for tens of seconds during DB issues.
> - Pods recovering on their own (re-roll, re-mount) instead of via in-proxy reconnect, and litellm logs showing nothing between "reconnect started" and the next pod startup.

## Extracted Claims

### Claim 1: A synchronous `subprocess.Popen.wait()` hidden inside an async library method can block the entire asyncio event loop, defeating any timeout mechanism that relies on `await` points
- **Evidence**: `prisma-client-py`'s `Engine.aclose()` looks `async` but internally calls `self.process.wait()` — a blocking call with no `await` point. During a DB outage, the engine's TCP close hangs, and `wait()` stalls for 30–120 seconds. `asyncio.wait_for()` could not cancel because "there is no await inside subprocess.wait()."
- **Confidence**: settled
- **Quote**: "The library's Engine.aclose() looks async from Python's perspective, but the implementation that finally shuts down the Rust query-engine subprocess calls: self.process.send_signal(signal.SIGTERM); self.process.wait()  # <-- BLOCKING. Does not yield to the loop."
- **Our assessment**: This is a meticulously documented incident with a clearly identified root cause, code-level evidence, and a verified fix. The failure pattern — sync subprocess `wait()` hiding behind an async API — is reproducible and generalizes beyond Prisma. The claim is settled for the documented mechanism.

### Claim 2: `asyncio.wait_for()` is not a safety net for synchronous blocking calls — it can only cancel at `await` points
- **Evidence**: The reconnect path was wrapped in `asyncio.wait_for()` as a safety timeout, but the timeout could not fire because there is no `await` inside `subprocess.wait()`. The cancellation coroutine itself could not run during the freeze.
- **Confidence**: settled
- **Quote**: "asyncio.wait_for() is not a safety net for sync work. It can only cancel at await points, so wrapping a blocking call in wait_for does not give you a timeout."
- **Our assessment**: This is a fundamental property of Python's asyncio that the incident demonstrates concretely. The claim is well-established in Python asyncio documentation, but this incident provides a vivid real-world example of the consequences — a production outage in a Kubernetes-deployed LLM gateway.

### Claim 3: Health-check endpoints that share the asyncio loop with the rest of the application are vulnerable to any synchronous blocking call anywhere in the loop
- **Evidence**: `/health/liveliness` was intentionally minimal (no DB access) yet froze during the Prisma reconnect because it shared the event loop with the proxy's request handling. No coroutine could run while `subprocess.wait()` blocked.
- **Confidence**: settled
- **Quote**: "/health/liveliness was intentionally minimal so that it would survive a DB outage, but it shares the asyncio loop with every other request, so any synchronous blocking call elsewhere in the loop drags it down regardless of how cheap the route itself is."
- **Our assessment**: This is an important architectural lesson for async Python services. The typical mitigation — making liveness checks cheap and DB-independent — is insufficient if the entire event loop can be frozen. This argues for either (a) running health checks on a separate event loop or in a separate process, or (b) ensuring no synchronous blocking call can ever occur in the service's request path. The incident demonstrates that (b) is extremely hard to guarantee when third-party async libraries are involved.

### Claim 4: Process-level signals (SIGTERM + bounded sleep + SIGKILL) provide a deterministic, async-friendly shutdown for wedged subprocesses
- **Evidence**: PR #26225 replaced `await self.db.disconnect()` with direct PID-based signaling: `os.kill(pid, SIGTERM)` → `await asyncio.sleep(0.5)` → `os.kill(pid, SIGKILL)` if still alive. The `await asyncio.sleep(0.5)` is a real `await` point that keeps the event loop running, allowing health checks to respond.
- **Confidence**: settled
- **Quote**: "Prefer process-level signals to library-level cleanup for unrecoverable subprocesses. When the engine has wedged on socket close, there is no graceful path that does not involve waiting on it. SIGTERM + bounded asyncio.sleep + SIGKILL gives a deterministic, async-friendly shutdown."
- **Our assessment**: The approach is correct and generalizable. The key insight is that an `await asyncio.sleep()` call is interleaved between the two kill signals to provide a real yield point, keeping the event loop responsive. The pattern is applicable to any async Python service that manages subprocesses and needs a responsive teardown path.

### Claim 5: Pre-fix verif metrics show 10006ms max latency with 99.7% 2xx; post-fix shows 52.7ms max with 100% 2xx — a ~190x improvement
- **Evidence**: The blog provides a verification table with three experimental conditions (pre-fix, post-fix with slow close injected, post-fix natural run). The metrics were collected against a local proxy + Postgres in Docker using `docker pause` to simulate an unresponsive database.
- **Confidence**: settled
- **Quote**: "Pre-fix, prod-like slow close (5s injected): 10006 ms (probe timeout) / 99.7% / With this fix, same slow close injected: 52.7 ms / 100%"
- **Our assessment**: The methodology (Docker pause on Postgres to simulate unresponsive DB) is sound, and the reproducibility of the 52.7ms result under the same failure condition confirms the fix's effectiveness. The ~190x latency improvement is dramatic and credible for the pattern described (replacing a synchronous subprocess `wait()` with async-friendly signal-based teardown).

### Claim 6: The bug manifests only under partial-failure conditions (unresponsive DB where TCP close hangs), not under healthy or hard-down DB — making it invisible to standard testing
- **Evidence**: The blog explicitly describes the three-state condition: "When the database is healthy the engine exits within milliseconds and the blocking call is invisible." The blocking only occurs "when the database is unhealthy" in the specific sense of being unresponsive (TCP close hangs waiting for FIN/ACK).
- **Confidence**: settled
- **Quote**: "When the database is unhealthy, the engine's own outbound TCP close() calls hang waiting for FIN/ACK from the unresponsive Postgres host, and wait() blocks the whole event loop for the duration."
- **Our assessment**: This is the most insidious aspect of the failure pattern. Standard testing with a hard-down DB (container stopped, network disconnected) would not reproduce it — the engine would exit quickly. Only partial-failure testing (Docker pause, iptables drop, network partition) reveals it. This underscores the triage assessment's point about verifying async library shutdown paths under realistic partial-failure conditions.

### Claim 7: Two distinct reconnect code paths existed with the same bug — a convergent fix eliminated the redundancy and a class of edge-case bugs
- **Evidence**: The blog states that before the fix, there was both `recreate_prisma_client` and a separate "direct reconnect" branch in `litellm/proxy/utils.py`. The fix unified both paths through `recreate_prisma_client`.
- **Confidence**: settled
- **Quote**: "Both reconnect call sites — recreate_prisma_client and the formerly-separate 'direct reconnect' branch in litellm/proxy/utils.py — now go through recreate_prisma_client. The two engine-alive and engine-dead paths converge on the same kill-then-recreate flow, which removes a class of 'what if the engine died between checks' bugs."
- **Our assessment**: This is a common maintenance anti-pattern in production code: multiple call sites implementing the same logical operation diverging over time. The fix correctly converges them, reducing future maintenance burden and eliminating a class of edge cases.

### Claim 8: A previously-passing unit test encoded the bug's invariant and had to be removed as part of the fix
- **Evidence**: The blog explicitly names the removed test and explains why the invariant it encoded was itself part of the bug.
- **Quote**: "One previously-passing test, test_lightweight_reconnect_skips_kill_on_successful_disconnect, encoded the old 'preserve the engine on successful disconnect' invariant that was itself part of the bug (prisma-client-py's aclose() kills the engine regardless) and was removed."
- **Confidence**: settled
- **Our assessment**: This is a valuable meta-lesson: a test can pass for the wrong reason by encoding a faulty invariant. The test assumed `disconnect()` was a clean operation that preserved the engine, but in reality `prisma-client-py`'s `aclose()` always kills the engine. The "preserve engine on successful disconnect" invariant was based on a misunderstanding of the library's behavior. This reinforces the importance of testing invariants derived from actual library semantics rather than expected behavior.

## Cross-References

- **Corroborates failures in**:
  - `failure-litellm-httpx-cache-eviction.md` — Same vendor (LiteLLM), same theme of async-related production failures in the proxy's infrastructure layer (httpx client lifecycle vs Prisma subprocess lifecycle). Both incidents involve an async cleanup path with unintended consequences that cause request failures. The httpx incident shares the pattern of "assumed cleanup behavior turns out to be destructive under conditions the test suite doesn't exercise."
  - `blog-litellm-april-townhall-updates.md` Claim 7 — Documents Prisma migration failure classes (schema migration not applied, marked-applied-but-incomplete, non-root-image). This is a *different* Prisma concern (schema migration vs runtime reconnect blocking) but they collectively establish that Prisma's integration with LiteLLM has multiple failure surfaces. This note extends that picture with a runtime blocking failure orthogonal to the migration failures.
  - `blog-litellm-fastapi-middleware-performance.md` — Discusses per-event-loop cost as a performance characteristic (the benchmark intentionally uses one worker/one loop to measure overhead). The subject article demonstrates the downside of that same architecture: if everything shares one event loop, a single blocking call freezes everything. The performance note does not contradict — it shows the performance *benefit* of the single-loop design, while this note shows the reliability *cost*.

- **Contradicts**: None. No existing source note claims that `asyncio.wait_for()` is an effective timeout for synchronous subprocess `wait()` calls, or that third-party async library methods can be trusted to yield without verification.

- **Extends / thematically adjacent**:
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` — Discusses the principle of "predict failure, plan accordingly." This incident is a concrete case study: the engineers predicted the DB could fail (hence the reconnect logic and `asyncio.wait_for()`), but did not predict that the *reconnect path itself* could fail by freezing the event loop. The incident extends the principle by showing that failure-prediction must include the recovery path, not just the primary service path.
  - `failure-litellm-wildcard-model-access-desync.md` — Another LiteLLM failure note where an update path (config reload) had a subtle state-management bug. Both share the pattern of "the recovery/update path contains its own failure mode, distinct from the primary path's failure mode."

- **Novel**: This is the first source note covering:
  1. **Sync subprocess `wait()` hiding behind an async library API** — the specific mechanism where an `async def` method wraps a synchronous `subprocess.Popen.wait()`, defeating asyncio-based timeout mechanisms.
  2. **The `asyncio.wait_for()` cancellation-limitation exploited at production scale** — the fundamental property that `wait_for` can only cancel at `await` points, demonstrated by a production outage with concrete latency metrics.
  3. **Process-level signal-based subprocess teardown with interleaved `await` point** — the specific fix pattern (SIGTERM → `await asyncio.sleep(0.5)` → SIGKILL) that keeps the event loop responsive during subprocess cleanup.
  4. **Partial-failure-only manifestation** — the bug only appears when the DB is unresponsive (TCP close hangs) but not hard-down, making it invisible to standard healthy/stopped testing.
  5. **Test encoding bug invariant** — the concrete case of a unit test that encoded a faulty assumption about library behavior and had to be removed as part of the fix.

## Guide Impact

- **Chapter 04 (L4 proxy reliability) or Chapter 05 (LLM Ops Reliability — async event loop management)**: Add a design anti-pattern: "Third-party async library methods wrapping synchronous subprocess `wait()` calls — the `async def` signature does not guarantee yielding, and `asyncio.wait_for()` provides no safety timeout because it can only cancel at `await` points." Include the LiteLLM Prisma reconnect incident as a case study with the specific root cause, the fix pattern (SIGTERM + bounded sleep + SIGKILL), and the verification methodology (Docker pause to simulate unreachable DB, pre/post latency metrics).

- **Chapter 02 (Observability — liveness/readiness probe design)**: Add guidance on the distinction between liveness and readiness during DB outages, and explicitly warn that liveness probes sharing the event loop with request handling are vulnerable to any synchronous blocking call anywhere in the service. Recommend either (a) dedicated health-check workers/processes or (b) mandatory verification that no blocking call exists in the async request path.

- **Chapter 03 (Incident Response — postmortem drafting, lessons learned)**: Use this incident's four lessons as a template for postmortem findings in async Python services. The "Don't trust async def for shutdown paths" and "asyncio.wait_for() is not a safety net for sync work" lessons are directly reusable as runbook guidance.

- **Chapter 05 (LLM Ops Reliability — database connection resilience)**: Add the partial-failure testing methodology (Docker pause, network partition simulation) as a recommended validation step for async DB client reconnect paths. Standard testing against healthy or hard-down databases is insufficient — the bug only manifests under unresponsive (TCP hang) conditions.

## Extraction Notes

- Source read in full via direct HTTP fetch from the rendered blog page (Docusaurus HTML, ~8 KB of extractable text). Complete article content extracted — no paywall, no truncation.
- The page is a single self-contained incident report with code-level diffs, verification tables, and operator guidance. No sub-pages were linked beyond the PR reference (GitHub PR #26225) which was not fetched as it is a code diff, not a narrative source.
- No contradiction issue filed: verified against all existing source notes and CONTRADICTIONS.md (empty). The event-loop blocking failure pattern from async subprocess `wait()` is genuinely novel in this corpus. The closest thematic adjacency (blog-litellm-fastapi-middleware-performance.md discussing per-event-loop cost) covers a different concern and does not contradict.
- The cross-reference candidates from `miner-related-notes.md` that are not cited above are dismissed because they do not address asyncio event-loop blocking, Prisma subprocess lifecycle, or the specific failure mechanism documented here:
  - `docs-langfuse-security-and-guardrails.md` — Security/guardrail patterns, unrelated.
  - `docs-langfuse-mcp-server.md` — MCP server reference, unrelated.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — AI agent spectrum, unrelated.
  - `docs-google-sre-reliable-product-launches.md` — Launch coordination engineering, unrelated.
  - `docs-google-sre-prodcast-04-05-furino-slos.md` — SLO fundamentals, unrelated.
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` — Already cited under Extends / thematically adjacent for the "predict failure" principle.
  - `blog-incidentio-ai-sre-incident-run.md` — AI SRE incident investigation, unrelated.
  - `blog-litellm-may-townhall-updates.md` — Security hardening, release versioning, unrelated.
  - `blog-litellm-observatory.md` — Release-validation load tests, unrelated.
  - `blog-pagerduty-sre-agent-triage.md` — SRE Agent triage, unrelated.
  - `blog-pagerduty-production-ai-agent-gaps.md` — AI agent production gaps, unrelated.
  - `blog-litellm-april-townhall-updates.md` — Already cited (Prisma migration failures — distinct concern).
