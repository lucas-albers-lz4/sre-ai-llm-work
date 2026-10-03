---
source_url: https://docs.litellm.ai/docs/completion/prompt_compression
source_type: docs
title: "Prompt Compression (compress()) — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs)
date_extracted: 2026-10-03
last_checked: 2026-10-03
status: current
confidence_overall: emerging
issue: "#1557"
---

# Prompt Compression (compress())

> LiteLLM's in-process `litellm.compress()` shrinks long conversations by keeping high-relevance/recent context, replacing low-relevance content with stubs in a `cache`, and returning a `litellm_content_retrieve` tool so the model can recover compressed content on demand. It also offers a server-side callback loop (`compression_interception`) that makes retrieval transparent for `/v1/messages`.

## Source Context

- **Type**: docs (LiteLLM Python SDK / proxy feature reference, beta)
- **Author credibility**: Official LiteLLM documentation (BerriAI). Documents an API they ship.
- **Scope**: Documents `litellm.compress()` parameters, return shape, behavior notes, retrieval handling, server-side callback loop, and vendor-run performance benchmarks (SWE-bench Lite, Claude Opus, n=5). Does not exhaustively document failure modes (cache retention, retrieval miss, round-trip costs).
- **Caveats**: Feature is marked "Beta — APIs and behavior may change before general availability."

## Extracted Claims

### Claim 1: `litellm.compress()` is a beta, relevance-based compression API that returns compressed messages plus a retrieval path
- **Evidence**: Page opens with beta admonition; function takes messages/model/call_type and compression params; returns dict with messages, tokens, compression_ratio, cache, and tools.
- **Confidence**: settled
- **Quote**: "This feature is in beta. APIs and behavior may change before general availability." and "Use `litellm.compress()` to shrink long conversation history before calling `completion()`. The function keeps high-relevance and recent context, replaces low-relevance content with lightweight stubs, and returns a retrieval tool so the model can request full content only when needed."
- **Our assessment**: Clear contract: compression produces stubs + cache + retrieval tool (lossless on-demand). Beta status means behavior may change.

### Claim 2: The return shape is explicit and observable at the call site
- **Evidence**: "What It Returns" enumerates keys.
- **Confidence**: settled
- **Quote**: "- `messages`: compressed conversation messages\n- `original_tokens`: token count before compression\n- `compressed_tokens`: token count after compression\n- `compression_ratio`: fraction of tokens removed\n- `cache`: key-value mapping of stub key -> original full content\n- `tools`: retrieval tool definition (`litellm_content_retrieve`) for on-demand restoration"
- **Our assessment**: The return includes token accounting and the retrieval tool definition; caller can measure effect directly.

### Claim 3: Parameters define trigger, target, scoring, and call type/schema
- **Evidence**: Parameters list.
- **Confidence**: settled
- **Quote**: "- `messages` (`List[dict]`, required): input conversation messages\n- `model` (`str`, required): model name used for token counting\n- `call_type` (`CallTypes`, default `CallTypes.completion`): the LiteLLM call type whose message schema these messages follow. Supported values: `CallTypes.completion` / `CallTypes.acompletion` (OpenAI chat-completions shape) and `CallTypes.anthropic_messages` (Anthropic Messages shape)\n- `compression_trigger` (`int`, default `200000`): compress only if input token count exceeds this\n- `compression_target` (`Optional[int]`, default `70% of compression_trigger`): desired post-compression token budget\n- `embedding_model` (`Optional[str]`): if set, combines BM25 + embedding relevance scoring\n- `embedding_model_params` (`Optional[dict]`): additional kwargs passed to `litellm.embedding()`\n- `compression_cache` (`Optional[DualCache]`): optional cache used by embedding scoring"
- **Our assessment**: Defaults are fixed numbers (200000 trigger, 70% target) independent of model context window by default.

### Claim 4: Behavior notes give concrete preservation and truncation guarantees
- **Evidence**: "Behavior Notes" bullets.
- **Confidence**: settled
- **Quote**: "- Messages below `compression_trigger` are passed through unchanged.\n- System messages, the last user message, and the last assistant message are always preserved.\n- If a relevant message does not fully fit the remaining budget, `compress()` may keep a truncated version of it.\n- Compressed-out content is never lost; it is stored in `cache` and addressable by `litellm_content_retrieve`."
- **Our assessment**: Explicit four-part contract. Note: protection stated for system + last two turns only; no documented guarantee about preserving `tool_use`/`tool_result` pairs or `cache_control`-marked messages.
### Claim 5: Retrieval is handled by `litellm_content_retrieve` tool; caller must resolve from cache
- **Evidence**: Example shows looking up requested key in `compressed["cache"]` and returning as tool output.
- **Confidence**: settled
- **Quote**: "If the model calls `litellm_content_retrieve`, look up the requested key in `compressed[\"cache\"]` and return that value as tool output." and code example with `args = json.loads(tool_call.function.arguments); full_content = compressed["cache"][args["key"]]`
- **Our assessment**: When used in-process (not via callback), the application must own the retrieval loop.

### Claim 6: Server-side callback loop (`compression_interception`) for `/v1/messages` automates retrieval
- **Evidence**: Config YAML and five-step flow.
- **Confidence**: settled
- **Quote**: "With this enabled, LiteLLM runs the following server-side flow:\n1. Compresses inbound messages before the first provider call.\n2. Injects the `litellm_content_retrieve` tool.\n3. Detects retrieval `tool_use` blocks in the model response.\n4. Resolves retrieval keys from the compression cache.\n5. Reruns the model via agentic loop and returns the final answer."
- **Our assessment**: Moves retrieval loop into gateway for Anthropic Messages (`/v1/messages`) path. No documented behavior for cache miss, extra round-trip cost, or whether reruns themselves get compressed.

### Claim 7: SWE-bench Lite benchmark (Claude Opus, 5 problems, trigger=10k) shows large token/cost savings with tradeoff in hunk overlap
- **Evidence**: Metrics table and definitions.
- **Confidence**: anecdotal (n=5, single model, single trigger)
- **Quote**: "Benchmarked on [SWE-bench Lite](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Lite_bm25_27K) (real GitHub issues with ~27k tokens of BM25-retrieved repo context per problem)." and table: "Hunk overlap | 0.582 | 0.361 | -0.221", "Avg prompt tokens | 30,828 | 6,890 | -77.7%", "Avg cost/problem | $0.488 | $0.136 | **-72.0%**"; file overlap unchanged at 1.000, exact file match 100%, content similarity similar.
- **Our assessment**: Directionally strong savings; quality impact appears modest in file targeting but hunk overlap drops. Small sample precludes generalization.

### Claim 8: Benchmark metrics defined and eval commands provided for reproducibility
- **Evidence**: "Metrics explained" table and eval commands.
- **Confidence**: settled
- **Quote**: "File overlap | Fraction of gold-patch files present in the generated patch\nExact file match | Whether the generated patch touches exactly the same set of files\nHunk overlap | Fraction of gold hunk line ranges covered by generated hunks\nContent similarity | Jaccard similarity of changed lines (added/removed) between gold and generated patches" and commands: `python tests/eval_swe_bench.py --model claude-opus-5 --problems 5` etc.
- **Our assessment**: Vendor provides concrete eval hooks; still small-sample caveat holds.

## Concrete Artifacts

### Quickstart example (in-process)
```python
import litellm
from litellm.types.utils import CallTypes

messages = [
    {"role": "system", "content": "You are a coding assistant."},
    {"role": "user", "content": "# auth.py\n" + "def authenticate():\n    pass\n" * 2000},
    {"role": "user", "content": "# utils.py\n" + "def helper():\n    pass\n" * 2000},
    {"role": "user", "content": "Fix the bug in auth.py"},
]

compressed = litellm.compress(
    messages=messages,
    model="gpt-5.6-terra",
    call_type=CallTypes.completion,
    compression_trigger=1000,
    compression_target=500,
)

response = litellm.completion(
    model="gpt-5.6-terra",
    messages=compressed["messages"],
    tools=compressed["tools"],
)
```
*(Attribution: LiteLLM docs, "Quickstart" — copied verbatim structure.)*

### Retrieval handling
```python
import json

tool_call = response.choices[0].message.tool_calls[0]
args = json.loads(tool_call.function.arguments)
full_content = compressed["cache"][args["key"]]
```
*(Attribution: LiteLLM docs, "Handling Retrieval Tool Calls".)*

### Server-side callback config (`/v1/messages`)
```yaml
litellm_settings:
  callbacks: ["compression_interception"]
  compression_interception_params:
    enabled: true
    compression_trigger: 10000
    compression_target: 7000
```
*(Attribution: LiteLLM docs, "Server-side Callback Loop".)*

### SWE-bench eval commands
```bash
# 5-problem quick check
python tests/eval_swe_bench.py --model claude-opus-5 --problems 5

# Custom trigger/target
python tests/eval_swe_bench.py --model gpt-5.6-terra --problems 20 \
    --compression-trigger 15000 --compression-target 10000

# With embedding scoring
python tests/eval_swe_bench.py --model gpt-5.6-terra --problems 10 \
    --embedding-model text-embedding-3-small
```
*(Attribution: LiteLLM docs, "Running the SWE-bench eval".)*

## Cross-References

- **Corroborates**:
  - `source-notes/docs-litellm-completion-message-trimming.md` (Claim 7, 8, 9, 10, 11) — documents `compress()` contract, return shape, defaults, callback loop, and SWE-bench results; this note extracts from the dedicated `prompt_compression` page.
  - `source-notes/blog-litellm-headroom-integration.md` (Claim 5) — external sidecar compression with `retrieve_headroom` tool; same recoverability pattern (stubs + cache + retrieval). Complementary (proxy guardrail) vs in-process/callback here.

- **Extends**:
  - `source-notes/blog-litellm-save-claude-code-costs.md` (Claim 9) — frames compression as trimming dynamic middle (Headroom) vs prefix caching; this note adds concrete API (`compress()`), token accounting, and eval metrics.
  - `source-notes/blog-litellm-may-townhall-updates.md` — mentions Prompt Compression (beta) shipped; this note is the reference-level extraction of that feature.

- **Contradicts**: None filed. No direct opposition found in corpus; differences are mechanistic (in-process/callback vs external sidecar) or completeness gaps (preservation rules not fully specified).

- **Novel**: Dedicated extraction of the `prompt_compression` docs page (#1557) with full parameter list, return dict, retrieval handling, `compression_interception` callback loop, and verbatim benchmark numbers/metrics definitions.

## Guide Impact

- **Chapter 05 (LLM Ops & Reliability)**: Add section on gateway-side prompt compression with `litellm.compress()` and `compression_interception`. Must cover: trigger/target semantics (fixed defaults), always-kept guarantees (system + last user + last assistant) with caveats (tool pairings not guaranteed), lossless-on-demand via `litellm_content_retrieve` + cache, and operational dependencies (cache retention for retrieval). Note beta status and that correctness depends on cache availability.
- **Chapter 05 (Cost/Context Control)**: Cite SWE-bench Lite numbers (n=5, Claude Opus, trigger=10k): −77.7% tokens, −72.0% cost, file overlap preserved (1.000/100%), hunk overlap drops 0.582→0.361. Treat as anecdotal evidence; call out sample size and methodology.
- **Chapter 03 (Runbooks & Agents)**: For agentic flows using `/v1/messages`, document `compression_interception` callback loop (5 steps). For direct SDK use, document required retrieval loop (tool result injection). Include failure exposure: what if retrieval key missing? (page doesn't specify — flag as open operational question).

## Extraction Notes

- Followed the page fully (Quickstart, returns, params, behavior, retrieval, server-side loop, performance, eval commands).
- Cross-referenced existing notes: `docs-litellm-completion-message-trimming.md` already covers parts of `prompt_compression` (Claims 7-11 in that note); this is a dedicated extraction of the page itself with full artifacts.
- Confidence overall marked `emerging` due to beta status and n=5 benchmark.
- No contradiction filed; mechanistic differences (Headroom sidecar vs native) are complementary.
