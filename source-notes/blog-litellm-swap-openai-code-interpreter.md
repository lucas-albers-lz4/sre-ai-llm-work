---
source_url: https://docs.litellm.ai/blog/swap_openai_code_interpreter
source_type: blog-post
title: "Swap OpenAI Code Interpreter for E2B/OpenSandbox"
author: "Krrish Dholakia (CEO, LiteLLM)"
date_published: 2026-06-23
date_extracted: 2026-08-01
last_checked: 2026-08-01
status: current
confidence_overall: emerging
issue: "#712"
---

# Swap OpenAI Code Interpreter for E2B/OpenSandbox

> A LiteLLM vendor blog post (by CEO Krrish Dholakia) documenting a gateway-level
> pattern for intercepting OpenAI's vendor-hosted `code_interpreter` tool call and
> re-executing the generated code in an operator-controlled sandbox (E2B managed,
> or OpenSandbox self-hosted Docker for no-egress perimeters), while keeping the
> client request and the `code_interpreter_call` response shape unchanged. The
> operational takeaways are data-perimeter control over model-generated code
> execution, execution billing moved off OpenAI onto operator compute, and
> deny-by-default egress on the self-hosted backend.

## Source Context

- **Type**: blog-post (vendor engineering blog hosted under `docs.litellm.ai/blog`),
  tagged `code interpreter`, `sandbox`, `e2b`, `opensandbox`, `agents`. Published
  June 23, 2026.
- **Author credibility**: Krrish Dholakia is CEO of LiteLLM (BerriAI), the
  maintainer of the gateway the post documents. Claims about how the LiteLLM
  feature works (config keys, interception flow, availability version) are
  authoritative first-party product documentation and verifiable in the
  open-source codebase. Claims about *benefits* (data residency guarantees,
  cost shift, isolation) are vendor assertions without metrics or independent
  corroboration.
- **Scope**: Covers (1) the interception loop (register sandbox tool → intercept
  `code_interpreter` tool call → create sandbox → execute → feed result back →
  teardown on completion), (2) two sandbox backends (E2B managed, OpenSandbox
  self-hosted Docker) and their deployment tradeoff, (3) SDK configuration for
  both Responses API and Chat Completions, (4) proxy (`config.yaml`) configuration
  with no client-side change, (5) OpenSandbox egress controls (`allow_internet_access`,
  `network_policy`), (6) the "why route through your own sandbox" benefits.
  Does NOT cover: any measurements, latency/throughput impact, failure modes,
  sandbox escape scenarios, or comparison of the two backends beyond one sentence.
  The page is thin — one short post with four config/code blocks.

## Extracted Claims

### Claim 1: OpenAI's native `code_interpreter` tool runs the model's Python inside an OpenAI-hosted container that is opaque, billed by OpenAI, and the code (often customer data) leaves the caller's perimeter
- **Evidence**: Opening statement of the post; this is the stated motivation for
  the whole feature.
- **Confidence**: settled
- **Quote**: "The OpenAI Responses and Chat Completions APIs let you declare a `code_interpreter` tool and the model runs Python inside an OpenAI-hosted container. That container is opaque, billed by OpenAI, and the code (often customer data) leaves your perimeter."
- **Our assessment**: An accurate description of the vendor-hosted executor problem
  this feature is built to solve: the executor is a black box on OpenAI's
  infrastructure, billed per call, and any code (which often embeds customer data)
  is uploaded out of the operator's control. This is the security/trust premise of
  the entire interception pattern.

### Claim 2: LiteLLM intercepts the `code_interpreter` tool call and re-executes it in a sandbox the operator controls, leaving the client request unchanged
- **Evidence**: Opening statement, continued.
- **Confidence**: settled
- **Quote**: "LiteLLM now let's you intercept that tool call and runs it in a sandbox you control. The client request is unchanged."
- **Our assessment**: The core value proposition: transparent interception. The
  source text contains the typo "let's you" (for "lets you"), reproduced verbatim
  here. Client-transparency is what makes this drop-in — no client-side change
  is required, which is a repeated theme across the post.

### Claim 3: The swap loop runs: when the model emits a `code_interpreter` tool call, LiteLLM creates a sandbox (E2B or OpenSandbox), executes the generated code, feeds the result back into the loop, and tears the sandbox down on completion, keeping the response shape compatible with OpenAI's native `code_interpreter_call`
- **Evidence**: "How the swap works" section.
- **Confidence**: settled
- **Quote**: "When the model emits a `code_interpreter` tool call, LiteLLM creates a sandbox (E2B or OpenSandbox), executes the generated code, feeds the result back into the loop, and tears the sandbox down on completion. The response shape stays compatible with OpenAI's native `code_interpreter_call`."
- **Our assessment**: The full lifecycle is register → intercept → create sandbox →
  execute → feed result back → teardown. Two properties matter operationally:
  the sandbox is torn down on completion (resource cleanup), and the
  `code_interpreter_call` response shape is preserved so the client sees no
  difference from the native flow.

### Claim 4: Two sandbox backends are supported — E2B for a managed sandbox, and OpenSandbox for self-hosted Docker-backed execution when the code or data cannot leave the operator's network
- **Evidence**: "How the swap works" section; the OpenSandbox `sandbox_tools`
  swap example in the proxy section.
- **Confidence**: settled
- **Quote**: "Two backends are supported today: E2B for a managed sandbox, and OpenSandbox for self-hosted Docker-backed execution when the code or data cannot leave your network."
- **Our assessment**: The managed-vs-self-hosted split is the central deployment
  tradeoff. E2B hands sandbox infrastructure to a third party; OpenSandbox keeps
  execution fully inside the operator's perimeter at the cost of running a
  Docker-backed sandbox fleet. The self-hosted path is the one that satisfies
  strict data-residency / air-gapped requirements.

### Claim 5: On the Chat Completions path the native `code_interpreter` tool is rewritten before it reaches OpenAI into a `litellm_code_execution` function tool, and each sandbox result is appended as a `role: tool` message until the model returns a final answer
- **Evidence**: Explicit mechanism description under the SDK section; the Chat
  Completions example passes `max_agentic_loops=4`.
- **Confidence**: settled
- **Quote**: "The native `code_interpreter` tool is rewritten before it reaches OpenAI; on the chat path it becomes a `litellm_code_execution` function tool and LiteLLM appends each sandbox result as a `role: tool` message until the model returns a final answer."
- **Our assessment**: The concrete mechanism: the model never receives the native
  tool — LiteLLM substitutes a function tool and drives the agentic loop itself,
  appending each execution result as a tool message and looping until a final
  answer, bounded by `max_agentic_loops`. The gateway becomes the agentic-loop
  driver rather than a pass-through.

### Claim 6: The interception feature is available starting `LiteLLM v1.91.0.dev1` — a dev/pre-release build
- **Evidence**: Explicit availability statement near the top of the post.
- **Confidence**: settled
- **Quote**: "Available starting `LiteLLM v1.91.0.dev1`."
- **Our assessment**: A pre-release availability gate. Operators adopting this
  pattern must run a dev (or later stable) build of the gateway, which matters for
  change-management policies that prohibit pre-release dependencies. (The sibling
  Bedrock-invoke incident note dates the v1.91.0 stable ship at July 4, so the
  feature lands in the v1.91.0 line.)

### Claim 7: In proxy (gateway) deployments the swap is enabled entirely in config via `sandbox_tools` entries, a `code_interpreter_interception` callback, and `code_interpreter_interception_params` — with no client-side change, so the OpenAI SDK keeps working unchanged
- **Evidence**: Proxy section with full `config.yaml`; explicit statements that
  there is no client-side change and the OpenAI SDK works unchanged.
- **Confidence**: settled
- **Quote**: "Same swap behind the AI gateway, with no client-side change."
- **Quote**: "The OpenAI SDK keeps working unchanged. Point it at the proxy, declare `code_interpreter`, and the gateway handles the rest."
- **Our assessment**: The proxy form is the operationally relevant one for the
  guide: any existing OpenAI-compatible client declares `code_interpreter` exactly
  as before and the gateway transparently reroutes execution. Enabling is
  config-only (`sandbox_tools` + a callback), no client rollout needed.

### Claim 8: OpenSandbox runs sandboxes locally with egress denied by default; network access requires explicitly flipping `allow_internet_access=True` or passing an explicit `network_policy`
- **Evidence**: Explicit statement in the proxy/OpenSandbox section.
- **Confidence**: settled
- **Quote**: "OpenSandbox runs sandboxes locally with egress denied by default; flip `allow_internet_access=True` or pass an explicit `network_policy` when the code needs the network."
- **Our assessment**: The strongest security control in the source: deny-by-default
  egress from the code-execution sandbox. Model-generated code gets network access
  only when the operator explicitly allows it. This is a directly citable Ch06
  default-deny pattern for sandboxed model-code execution.

### Claim 9: The pattern keeps the OpenAI client contract while owning the execution layer — generated code and uploaded data stay inside the operator's sandbox, and execution billing stops going to OpenAI
- **Evidence**: "Why route it through your own sandbox" section.
- **Confidence**: emerging (mechanism is settled vendor documentation; the
  cost/data-residency benefits are asserted without any measurements)
- **Quote**: "You keep the OpenAI client contract while owning the execution layer. The generated code and any uploaded data stay inside the sandbox you operate, billing for execution stops going to OpenAI, and the same setup works for Responses and Chat Completions across any model the gateway routes to."
- **Our assessment**: Data residency and cost control are the two headline benefits.
  "Billing stops going to OpenAI" shifts execution compute to the operator's own
  infrastructure — a real operational change, but the post gives no numbers on
  OpenAI's per-call interpreter billing versus self-hosted execution cost, so the
  economic claim is unquantified.

### Claim 10: The same setup works for both the Responses API and the Chat Completions API, across any model the gateway routes to
- **Evidence**: Two SDK code examples (Responses + Chat Completions) in the SDK
  section; the "same setup works for Responses and Chat Completions" statement.
- **Confidence**: emerging
- **Quote**: "the same setup works for Responses and Chat Completions across any model the gateway routes to"
- **Our assessment**: Because interception happens at the gateway, the sandboxing
  applies to any model that emits a `code_interpreter`-style tool call, not just
  OpenAI models. Gateway-level interception makes sandboxed execution
  provider-agnostic — a notable design property for a multi-model gateway.

### Claim 11: Streaming, forced `tool_choice`, and concurrent requests are isolated per request and cleaned up on completion
- **Evidence**: Closing paragraph of the "Why route it through your own sandbox"
  section.
- **Confidence**: emerging (vendor claim; no test evidence or demonstration in the
  source)
- **Quote**: "Streaming, forced `tool_choice`, and concurrent requests are isolated per request and cleaned up on completion."
- **Our assessment**: Addresses the three operational concerns any sandboxed-execution
  feature must handle — streaming response behavior, forced tool selection, and
  concurrent-request sandbox isolation with cleanup. Plausible as a design
  requirement, but asserted without demonstration; treat as a requirement list
  rather than a measured guarantee.

## Concrete Artifacts

All artifacts below are extracted verbatim from the source page's code blocks
(blank lines and indentation reconstructed from the rendered syntax-highlighted
blocks; no words added or removed).

### SDK — Responses API setup (verbatim from "SDK" tab)

```python
import os, litellm
from litellm.sandbox.sandbox_tools import register_sandbox_tools
from litellm.integrations.code_interpreter_interception.handler import (
    CodeInterpreterInterceptionLogger,
)

os.environ["E2B_API_KEY"] = "e2b_..."
os.environ["OPENAI_API_KEY"] = "sk-..."

register_sandbox_tools([
    {
        "sandbox_tool_name": "my-e2b",
        "litellm_params": {
            "sandbox_provider": "e2b",
            "api_key": "os.environ/E2B_API_KEY",
        },
    }
])

litellm.callbacks = [
    CodeInterpreterInterceptionLogger(sandbox_tool_name="my-e2b")
]

response = await litellm.aresponses(
    model="openai/gpt-5",
    tools=[{"type": "code_interpreter", "container": {"type": "auto"}}],
    input="Product of first 6 primes. Just the number.",
)
print(response.output_text)
```

Source: https://docs.litellm.ai/blog/swap_openai_code_interpreter — "SDK / Responses API" tab.

### SDK — Chat Completions setup (verbatim from "SDK" tab)

```python
import os, litellm
from litellm.sandbox.sandbox_tools import register_sandbox_tools
from litellm.integrations.code_interpreter_interception.handler import (
    CodeInterpreterInterceptionLogger,
)

os.environ["E2B_API_KEY"] = "e2b_..."
os.environ["OPENAI_API_KEY"] = "sk-..."

register_sandbox_tools([
    {
        "sandbox_tool_name": "my-e2b",
        "litellm_params": {
            "sandbox_provider": "e2b",
            "api_key": "os.environ/E2B_API_KEY",
        },
    }
])

litellm.callbacks = [
    CodeInterpreterInterceptionLogger(sandbox_tool_name="my-e2b")
]

response = await litellm.acompletion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Product of first 6 primes. Just the number."}],
    tools=[{"type": "code_interpreter", "container": {"type": "auto"}}],
    max_agentic_loops=4,
)
print(response.choices[0].message.content)
```

Source: https://docs.litellm.ai/blog/swap_openai_code_interpreter — "SDK / Chat Completions" tab. Note the `max_agentic_loops=4` bound on the tool loop and the `"api_key": "os.environ/E2B_API_KEY"` reference-style value (LiteLLM resolves the `os.environ/...` prefix).

### Proxy `config.yaml` with E2B backend (verbatim from "Proxy" section)

```yaml
model_list:
  - model_name: gpt-5
    litellm_params:
      model: openai/gpt-5
      api_key: os.environ/OPENAI_API_KEY

sandbox_tools:
  - sandbox_tool_name: my-e2b
    litellm_params:
      sandbox_provider: e2b
      api_key: os.environ/E2B_API_KEY

litellm_settings:
  callbacks: ["code_interpreter_interception"]
  code_interpreter_interception_params:
    sandbox_tool_name: my-e2b
```

Source: https://docs.litellm.ai/blog/swap_openai_code_interpreter — "Proxy / config.yaml".

### OpenAI SDK client, unchanged (verbatim from "Proxy" section)

```python
from openai import OpenAI

client = OpenAI(api_key="sk-1234", base_url="http://localhost:4000/v1")

response = client.responses.create(
    model="gpt-5",
    tools=[{"type": "code_interpreter", "container": {"type": "auto"}}],
    input="Product of first 6 primes. Just the number.",
)
print(response.output_text)
```

Source: https://docs.litellm.ai/blog/swap_openai_code_interpreter — "Proxy" section. This is the client-side proof of "no client-side change": the client points at the proxy and declares `code_interpreter` exactly as it would against OpenAI.

### OpenSandbox self-hosted backend swap (verbatim from "Proxy" section)

```yaml
sandbox_tools:
  - sandbox_tool_name: my-opensandbox
    litellm_params:
      sandbox_provider: opensandbox
      api_base: os.environ/OPEN_SANDBOX_API_BASE
      api_key: os.environ/OPEN_SANDBOX_API_KEY
```

Source: https://docs.litellm.ai/blog/swap_openai_code_interpreter — "Proxy" section, "To run fully on-prem, swap the `sandbox_tools` entry to OpenSandbox".

## Cross-References

- **Corroborates**:
  - `docs-google-sre-prodcast-04-09-ai-agents.md` **Claim 3** (default guardrail:
    deny agents any world-mutating action; writes run in a sandbox, anything that
    breaks the sandbox needs an additional check). This source is a production
    instantiation of that principle at the gateway layer: model-generated code
    execution is confined to a sandbox the operator controls, and on the
    OpenSandbox backend egress is denied by default (Claim 8 here). The Prodcast
    states the principle; this source shows a concrete product implementing it.
  - `blog-litellm-lap-internal-agent-30-percent.md` — Both sources independently
    pick **E2B sandboxes** as the isolated execution environment for model-generated
    code (this source's Concrete Artifacts; the LAP note's brain/sandbox split
    architecture diagram). The LAP note uses E2B as an agent-runtime sandbox
    (per-session `git/gh/pytest` execution); this source uses E2B as a
    gateway-intercepted code-execution sandbox. Convergent vendor practice on the
    execution-sandbox pattern.

- **Contradicts**: None. Verified against all existing source notes and
  `CONTRADICTIONS.md` (no open `C-NNN` entries). No existing note makes a claim
  about gateway tool-call interception or sandboxed code execution that this
  source would oppose. No contradiction issue filed.

- **Extends**:
  - `blog-litellm-lap-internal-agent-30-percent.md` — Extends the E2B-sandbox
    execution pattern from a bespoke agent runtime (LAP brain/sandbox split) into
    a configurable, client-transparent gateway feature that intercepts a *vendor*
    tool call. It also extends the data-perimeter theme from that note (credentials
    pinned to bound hosts) to execution: model-generated code and uploaded data
    stay inside the operator's sandbox rather than a vendor-hosted container.
  - `blog-litellm-gpt-5-3-codex-day-0.md` — Both notes concern OpenAI models
    routed through the LiteLLM gateway on the Responses API (`/v1/responses`,
    `client.responses.create`). The day-0 note documents routing an OpenAI
    agentic-coding model and preserving its `phase` output-item metadata; this
    source documents gateway-level tool-call interception/rewriting on the same
    endpoint surface. The two cover different layers (metadata passthrough vs.
    tool-execution routing) of the same gateway Responses-API path.
  - `blog-litellm-save-claude-code-costs.md` **Claim 3** (proxy-side `cache_control`
    injection, "no client-side edit") and **Claim 4** (MCP Tool Search — the gateway
    rewrites the tool surface transparently) — the recurring "gateway rewrites the
    request/tool surface transparently, client unchanged" pattern. This source
    applies the same transparency principle one level deeper: not just rewriting
    tool schemas but routing tool *execution*.

- **Novel**: First source note in the corpus covering:
  - **Gateway-level interception of a vendor-hosted code-execution tool** — rerouting
    OpenAI's `code_interpreter` tool call to operator-controlled sandboxes, client
    request and response shape unchanged.
  - **The `litellm_code_execution` tool substitution + `role: tool` result-feedback
    agentic loop** — the gateway rewriting the native tool before it reaches the
    model and driving the loop to a final answer, bounded by `max_agentic_loops`.
  - **The E2B (managed) vs. OpenSandbox (self-hosted Docker) backend tradeoff** for
    execution sandboxes, including the data-residency rationale for self-hosting.
  - **OpenSandbox's deny-egress-by-default control** (`allow_internet_access`,
    `network_policy`) as a data-perimeter mechanism for model-generated code.
  - **Moving code-execution billing off the model vendor** onto operator compute.

## Guide Impact

- **Chapter 06 (Security and Trust)**: Add the **gateway-level code-execution
  interception pattern** as a data-perimeter control. Model-generated code (which
  often embeds customer data) must not execute on opaque vendor-hosted containers;
  intercept the code-execution tool call at the gateway and run it in a sandbox
  the operator controls. For no-egress/air-gapped perimeters, use a self-hosted
  sandbox backend with **egress denied by default** (OpenSandbox), enabling network
  access only via explicit `allow_internet_access=True` or an explicit
  `network_policy` (Claim 8). Cite this as the practical counterpart to the
  Google Prodcast's "writes run in a sandbox" guardrail principle.

- **Chapter 05 (LLM Ops Reliability)**: Add the **tool-call interception loop** as
  a gateway ops pattern: the gateway runs the agentic loop (rewrite the native tool
  into a function tool → execute in a sandbox → append the result as a `role: tool`
  message → loop until a final answer, bounded by `max_agentic_loops`). Note that
  this moves execution compute off the model vendor's per-call billing onto operator
  infrastructure, and that the same setup spans Responses + Chat Completions and any
  model the gateway routes to (Claims 9-10). Flag the **availability gate** (dev
  build `v1.91.0.dev1`+) for change-management policy (Claim 6).

- **Chapter 03 (Runbooks and Agents)**: Add the **sandbox lifecycle requirements**
  for any sandboxed code-execution loop: tear the sandbox down on completion, and
  isolate streaming / forced `tool_choice` / concurrent requests per request with
  cleanup (Claims 3, 11). These are the operational invariants an agentic
  tool-execution loop must hold.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page (no paywall, no
  truncation; the page is a single short post with four config/code blocks). No
  sub-pages followed — the only outbound reference is "Full reference is in the
  sandbox docs," which is a pointer, not substantive content.
- All quoted passages were copied character-for-character from the rendered page
  text and verified against the fetched HTML. Note the source contains the typo
  "let's you intercept" (for "lets you intercept") in the opening — reproduced
  verbatim (Claim 2).
- `confidence_overall` set to `emerging`: the configuration, mechanism, and
  availability claims (Claims 1-8) are settled first-party product documentation
  and verifiable in the open-source LiteLLM codebase; the benefit claims (billing
  shift, per-request isolation, provider-agnostic coverage — Claims 9-11) are
  asserted without metrics or independent corroboration, and the post is a single
  vendor doc page with no practitioner outcome data.
- **Candidate dismissal** (from `miner-related-notes.md`; each cited or dismissed):
  - `docs-langfuse-mcp-server.md` — Langfuse docs MCP server; unrelated to
    execution sandboxing. Dismissed.
  - `blog-litellm-save-claude-code-costs.md` — Cited (Extends, Claims 3/4):
    gateway-transparent request/tool-surface rewriting.
  - `docs-google-sre-reliable-product-launches.md` — launch coordination; unrelated.
    Dismissed.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — Cited (Corroborates, Claim 3):
    writes run in a sandbox.
  - `docs-google-sre-prodcast-04-05-furino-slos.md` — SLOs; unrelated. Dismissed.
  - `docs-langfuse-security-and-guardrails.md` — application-layer input/output
    scanner guardrails (content filtering), a related but different mechanism than
    execution sandboxing. Dismissed.
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — retail/gaming SRE;
    unrelated. Dismissed.
  - `blog-litellm-april-townhall-updates.md` — CI/CD supply-chain isolation;
    different security topic. Dismissed.
  - `failure-litellm-bedrock-invoke-prompt-cache.md` — gateway translation breaking
    a provider prompt cache; a different gateway-translation failure class, not
    sandboxing. Dismissed.
  - `blog-incidentio-ai-sre-incident-run.md` — incident-response AI agent; unrelated.
    Dismissed.
- Triage-flagged nearest litellm notes dismissed as non-overlapping (verified by
  reading frontmatter/scope): `failure-litellm-wildcard-model-access-desync.md`
  (gateway auth desync), `blog-litellm-fastapi-middleware-performance.md` (proxy
  middleware latency), `blog-litellm-redis-circuit-breaker.md` (Redis resilience),
  `failure-litellm-supply-chain-incident-march-2026.md` (PyPI supply-chain
  incident) — none cover tool-call interception or sandboxed code execution.
- `blog-litellm-gpt-5-3-codex-day-0.md` was triage-flagged as matching "code
  interpreter," but I verified the source page and note contain no `code_interpreter`
  or tool content at all — it is a Day-0 model-support note about the Responses-API
  `phase` metadata. Cited only for the shared LiteLLM Responses-API endpoint
  surface (see Extends), with no overlap on sandboxing/interception.
- No contradiction issue filed: verified against `CONTRADICTIONS.md` (no open
  `C-NNN` entries), open `contradiction`-labeled issues (none), and all corpus
  notes. No opposing claims found.
