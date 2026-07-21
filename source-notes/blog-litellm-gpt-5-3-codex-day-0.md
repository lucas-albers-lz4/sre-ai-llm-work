---
source_url: https://docs.litellm.ai/blog/gpt_5_3_codex
source_type: blog-post
title: "Day 0 Support: GPT-5.3-Codex"
author: "Sameer Kankute (SWE, LLM Translation), Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-02-24
date_extracted: 2026-07-21
last_checked: 2026-07-21
status: current
confidence_overall: emerging
issue: "#399"
---

# Day 0 Support: GPT-5.3-Codex

> A LiteLLM vendor announcement documenting how to run OpenAI's GPT-5.3-Codex
> through the LiteLLM gateway via the `/v1/responses` endpoint. The operationally
> novel detail is the `phase` metadata field on assistant output items
> (null / "commentary" / "final_answer") that must be persisted verbatim across
> multi-turn conversations — a new OpenAI Responses API metadata pattern that
> LiteLLM proxies through unchanged.

## Source Context

- **Type**: blog-post (vendor "Day 0 support" product announcement on
  `docs.litellm.ai/blog`), tagged `openai`, `gpt-5.3-codex`, `codex`,
  `day 0 support`.
- **Author credibility**: High for *how LiteLLM itself routes and configures
  the model* — authored by a LiteLLM SWE (Sameer Kankute) and the company's
  CEO (Krrish Dholakia) and CTO (Ishaan Jaffer), i.e. the maintainers of the
  gateway. The config and phase-handling detail is first-party documentation.
- **Scope**: Covers (1) Day-0 availability through a unified OpenAI-compatible
  interface via the Responses API, (2) the `phase` parameter semantics
  (null / "commentary" / "final_answer"), (3) verbatim persistence rules for
  multi-turn conversation history, (4) a Docker image with version pin
  `v1.81.12-stable.gpt-5.3`, and (5) a Python example showing the phase-persistence
  pattern. Does NOT cover: production metrics, latency/throughput measurements,
  failure analysis, any practitioner outcome, or non-Responses-API endpoints
  (the post exclusively documents `/v1/responses`). It is a thin launch/how-to
  post structurally following the same LiteLLM "Day 0 Support" template as the
  other Day-0 notes but notably thinner — the only operational detail beyond
  the standard config boilerplate is the `phase` parameter handling.

## Extracted Claims

### Claim 1: LiteLLM supports GPT-5.3-Codex on Day 0, including passthrough of the `phase` metadata on Responses API output items
- **Evidence**: Opening statement of the post; the Python example then shows
  how the proxy returns and persists `phase` on assistant output items.
- **Confidence**: settled (the vendor documenting its own supported routing;
  the Python example is concrete and testable).
- **Quote**: "LiteLLM now supports GPT-5.3-Codex on Day 0, including support
  for the new assistant `phase` metadata on Responses API output items."
- **Our assessment**: Standard Day-0 enablement claim. The second clause
  ("including support for...") is the value-add: LiteLLM is not just routing
  the model but also preserving a new OpenAI API metadata field that would
  otherwise be stripped by a generic proxy. Credible and concrete.

### Claim 2: GPT-5.3-Codex uses the `/v1/responses` endpoint (OpenAI Responses API), not `/v1/chat/completions`
- **Evidence**: The Docker run example and the curl example both target
  `http://0.0.0.0:4000/v1/responses`. The Python example uses
  `client.responses.create()`. No alternative endpoint is shown.
- **Confidence**: settled (the vendor's only documented access path; the
  OpenAI client call `client.responses.create()` is the Responses API SDK call).
- **Quote**: (no direct single quote; the endpoint appears in the curl command
  as `"http://0.0.0.0:4000/v1/responses"` and in the Python code as
  `client.responses.create(model="gpt-5.3-codex", ...)`)
- **Our assessment**: This distinguishes Codex models from standard chat models
  in the LiteLLM routing surface. The Gemini Day-0 notes document `/v1/responses`
  as one of four endpoints; this post documents `/v1/responses` as the *only*
  endpoint for this model. Operators adding Codex models to an existing proxy
  config may need to verify their client code targets the Responses API path
  rather than the chat completions path.

### Claim 3: The `phase` field on assistant output items distinguishes preamble/commentary turns from final closeout responses, with supported values `null`, `"commentary"`, and `"final_answer"`
- **Evidence**: Explicitly stated in the post's explanation of the `phase` field
  and its values.
- **Confidence**: settled (documented spec of the OpenAI Responses API metadata
  that LiteLLM proxies through).
- **Quote**: "`phase` appears on assistant output items and helps distinguish
  preamble/commentary turns from final closeout responses."
- **Our assessment**: This is the key novel element in the post. The `phase`
  field is a new OpenAI API metadata pattern that lets consumers distinguish
  model preamble/commentary from the actual final answer — relevant for UI
  rendering (hide commentary), telemetry routing, and evaluation pipelines
  that should only score final answers. The three-value enum (null, "commentary",
  "final_answer") is the concrete API surface a gateway operator must handle.
  Entirely new to the corpus — no existing note discusses phase metadata.

### Claim 4: Assistant output items with `phase` metadata must be persisted verbatim and sent back on the next turn; `phase` must not be added to user messages
- **Evidence**: The Python example code and the "Notes" block state the rules
  explicitly. The code shows user messages appended without `phase` and
  assistant output items appended verbatim (including `phase`).
- **Confidence**: settled (concrete code example from the vendor; the rule is
  enforced by the pattern of the example).
- **Quote**: (no direct quote for the rule as a sentence; the rule is
  operationalized in the code comments:
  `# User message: no phase field` and
  `# Persist assistant output items verbatim, including phase`)
- **Our assessment**: Straightforward but easy to get wrong. If a gateway
  operator or agent framework reconstructs conversation history by stripping
  metadata fields from output items, the `phase` metadata would be lost.
  The rule is: echo what the model returns unchanged, and never add `phase`
  to user-generated messages.

### Claim 5: Dropping `phase` metadata during history reconstruction degrades output quality on long-running tasks
- **Evidence**: "Notes" section at the end of the post warns of this consequence.
- **Confidence**: emerging (stated as a warning by the vendor; the mechanism —
  the model may lose ability to distinguish its own prior commentary from
  final answers — is plausible but not demonstrated with metrics).
- **Quote**: "If `phase` metadata is dropped during history reconstruction,
  output quality can degrade on long-running tasks."
- **Our assessment**: The practical consequence of Claim 4. For long-running
  agentic tasks where the conversation history spans many turns, stripping
  `phase` metadata from earlier assistant turns could make the model lose
  context of what was preamble vs. final closeout. This is a new failure mode
  to document: metadata-stripping proxies or history-reconstruction logic that
  silently drops unknown fields may harm output quality for Codex models
  without any error or warning.

### Claim 6: The recommended Docker image for GPT-5.3-Codex support is `ghcr.io/berriai/litellm:v1.81.12-stable.gpt-5.3`, a stable build — unlike other Day-0 models that ship on dev or release-candidate tags
- **Evidence**: The Docker pull and run commands specify this exact image tag.
- **Confidence**: settled (first-party deploy instruction; the tag is concrete
  and referenced in both pull and run commands).
- **Quote**: "`ghcr.io/berriai/litellm:v1.81.12-stable.gpt-5.3`"
- **Our assessment**: Notable because it differs from the sibling Day-0 notes.
  Opus 4.7 shipped on Stable (`v1.83.3-stable`), Opus 4.8 on a Nightly Dev
  (`v1.88.0-dev.1`), Fable 5 on Release Candidate (`v1.89.0-rc.2`), and
  Gemini 3.5 Flash on a Dev nightly (`v1.87.0-dev.1`). This GPT-5.3-Codex
  post ships on a stable build (`v1.81.12-stable.gpt-5.3`). The stable tag
  means operators can adopt the model without running pre-release software.
  (Note: the Docker run command contains an apparent copy-paste issue — the
  env var name says `ANTHROPIC_API_KEY` when the value is `$OPENAI_API_KEY`,
  suggesting the example template was adapted from an Anthropic-model post.)

### Claim 7: The Python pattern for persisting `phase` uses the OpenAI Responses API client with a global items list, manually appending user messages (no phase) and verbatim output items (including phase)
- **Evidence**: The complete Python example in the post shows `items = []`
  persisting per conversation, a `_item_get` helper for safe attribute access,
  and a `run_turn` function that appends user content as a structured message
  dict (with no `phase`) and then appends each `resp.output` item verbatim
  (preserving `phase`).
- **Confidence**: settled (concrete, runnable code from the vendor).
- **Quote**: (see Concrete Artifacts → Python example for the verbatim code block)
- **Our assessment**: The pattern is the operational template any gateway
  operator or agent framework consuming Codex models needs to follow. The
  key detail is that the OpenAI Responses API returns output items as objects
  with a `phase` attribute, and the code must append them unchanged rather
  than extracting and re-serializing selected fields. The `_item_get` helper
  handles the case where output items may be either dicts or objects (common
  in the Responses API which can return different item types). The optional
  `latest_phase` scan (reversed output, looking for the last non-None phase
  on `output_item.done` type items) is shown as a UI/telemetry routing hook.

## Concrete Artifacts

All artifacts below are extracted verbatim from the source page. Config keys,
model IDs, and parameter names in code spans are rendered as literal text from
the page. No words were added or removed.

### Proxy `config.yaml` (verbatim)

```yaml
model_list:
  - model_name: gpt-5.3-codex
    litellm_params:
      model: openai/gpt-5.3-codex
```

### Docker pull, run, and curl commands (verbatim)

```bash
docker pull ghcr.io/berriai/litellm:v1.81.12-stable.gpt-5.3

docker run -d \
  -p 4000:4000 \
  -e ANTHROPIC_API_KEY=$OPENAI_API_KEY \
  -v $(pwd)/config.yaml:/app/config.yaml \
  ghcr.io/berriai/litellm:v1.81.12-stable.gpt-5.3 \
  --config /app/config.yaml

curl -X POST "http://0.0.0.0:4000/v1/responses" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_KEY" \
  -d '{
    "model": "gpt-5.3-codex",
    "input": "Write a Python script that checks if a number is prime."
  }'
```

Note: The `-e ANTHROPIC_API_KEY=$OPENAI_API_KEY` flag appears to be a
copy-paste artifact — the env var name says `ANTHROPIC_API_KEY` while the
value references `$OPENAI_API_KEY`, suggesting the example was adapted from
an Anthropic-model Day-0 post.

### Python example — persisting `phase` with OpenAI client (verbatim)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://0.0.0.0:4000/v1",  # LiteLLM Proxy
    api_key="your-litellm-api-key",
)

items = []  # Persist this per conversation/thread

def _item_get(item, key, default=None):
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)

def run_turn(user_text: str):
    global items
    # User message: no phase field
    items.append(
        {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": user_text}],
        }
    )
    resp = client.responses.create(
        model="gpt-5.3-codex",
        input=items,
    )
    # Persist assistant output items verbatim, including phase
    for out_item in (resp.output or []):
        items.append(out_item)
    # Optional: inspect latest phase for UI/telemetry routing
    latest_phase = None
    for out_item in reversed(resp.output or []):
        if _item_get(out_item, "type") == "output_item.done" and _item_get(out_item, "phase") is not None:
            latest_phase = _item_get(out_item, "phase")
            break
    return resp, latest_phase
```

### Phase persistence guidance (verbatim)

> "Preserve full assistant output history for best multi-turn behavior."
>
> "If `phase` metadata is dropped during history reconstruction, output quality
> can degrade on long-running tasks."

## Cross-References

- **Corroborates**:
  - `blog-litellm-gemini-3-5-flash-day-0.md` (Claim 8 — `/v1/responses` endpoint)
    and `blog-litellm-gemini-3-flash-day-0.md` (Claim 5 — four-endpoint support
    including `/v1/responses`). Both notes document that LiteLLM supports the
    OpenAI Responses API endpoint for their respective models. This GPT-5.3-Codex
    post is a third instance confirming that LiteLLM routes through `/v1/responses`,
    but is the *only* one where `/v1/responses` is the exclusive access path.
  - `blog-litellm-claude-fable-5-day-0.md` (Claim 1) — Same Day-0 support template
    pattern: a unified API interface, version-pinned image, per-model `config.yaml`.
    This post is another instance of that pattern, now applied to an OpenAI Codex
    model, confirming the template's provider-agnostic stability.
  - `blog-litellm-april-townhall-updates.md` (Claim 6 — the 4-tier release-tag
    taxonomy) — This post's `v1.81.12-stable.gpt-5.3` tag is a **Stable** build
    under that taxonomy, consistent with Opus 4.7's Stable ship. This contrasts
    with Opus 4.8 (Nightly Dev), Fable 5 (Release Candidate), and Gemini 3.5
    Flash (Nightly Dev), continuing the observation that Day-0 tag maturity
    varies by model.

- **Contradicts**: None. No contradiction issue filed. Verified against all
  existing source notes and `CONTRADICTIONS.md` (no open `C-NNN` entries).
  No existing note makes a claim about the `phase` parameter or about Codex
  model response metadata that this note would oppose.

- **Extends**:
  - `blog-litellm-gemini-3-5-flash-day-0.md` and `blog-litellm-gemini-3-flash-day-0.md`
    — Both notes document that LiteLLM routes through `/v1/responses` for Gemini
    models, but only as an endpoint listing (one of four). This GPT-5.3-Codex note
    is the first to detail a *Responses-API-specific feature* (`phase` metadata),
    extending the endpoint-surface documentation from "which endpoints exist" to
    "what per-endpoint metadata patterns the operator must handle." This note
    adds the phase-persistence requirement to the corpus's understanding of the
    Responses API surface.
  - `blog-litellm-claude-fable-5-day-0.md` (Claim 10 — the cost-map reload
    enablement path) — Like the Claude Day-0 notes, this post's standard config
    and Docker deploy would rely on the `POST /reload/model_cost_map` path for
    operators using the default remote cost map. The wildcard-desync incident's
    lesson ("reload success ≠ end-to-end health") applies: operators following
    this post's instructions should validate the model is actually reachable
    via an end-to-end request, not just that the image is pulled and running.

- **Novel**: First source note in the corpus to capture:
  - **The `phase` parameter** (null / "commentary" / "final_answer") on
    Responses API output items — a new OpenAI API metadata pattern that
    distinguishes model preamble/commentary from final answers. Entirely
    new to the corpus.
  - **Phase-persistence rules** — the requirement to persist assistant output
    items verbatim (including `phase`) and never add `phase` to user messages.
  - **Phase-drop quality degradation** — the warning that dropping `phase`
    metadata during history reconstruction degrades output quality on
    long-running tasks. A new failure mode for metadata-stripping proxies.
  - **Exclusive `/v1/responses` endpoint routing** — the first note where a
    model documented in the corpus uses the Responses API *exclusively*
    (rather than as one of several supported endpoints).
  - **GPT-5.3-Codex model** — a new OpenAI model family (code generation /
    agentic coding) not previously covered in the corpus.
  - **The `client.responses.create()` pattern** — SDK usage of the Responses
    API directly, as opposed to `client.chat.completions.create()` used in all
    prior LiteLLM Day-0 notes.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability / API surface evolution) / Responses API
  metadata handling**: Add that the OpenAI Responses API introduces metadata
  fields (specifically `phase`) on output items that must be preserved verbatim
  across multi-turn conversations. Gateway operators and agent frameworks that
  reconstruct conversation history by stripping unknown fields will silently
  degrade output quality for Codex models. Document the three rules:
  (1) persist assistant output items including `phase` exactly as returned,
  (2) send them back on the next turn unchanged, (3) never add `phase` to
  user messages. This source provides the concrete Python pattern for safe
  persistence (see Concrete Artifacts).
- **Chapter 05 / endpoint routing catalog**: Add that GPT Codex models route
  exclusively through `/v1/responses`, not `/v1/chat/completions`. Operators
  adding Codex support to an existing proxy must target the Responses API
  endpoint. This expands the endpoint routing documentation, which currently
  covers `/v1/chat/completions` and `/v1/messages` (Claude models) and the
  four-endpoint Gemini surface.
- **Chapter 05 / phase metadata for telemetry and evaluation**: The `phase`
  field's distinction between `"commentary"` (preamble/thinking-aloud) and
  `"final_answer"` (the actual response) is directly useful for evaluation
  pipelines that should only score final answers, and for telemetry routing
  that treats commentary differently from answers. Recommend capturing this
  as a generic metadata-routing pattern in the gateway design material.
- **Chapter 05 / model enablement**: Add that this model ships on a **Stable**
  image (`v1.81.12-stable.gpt-5.3`), unlike several other Day-0 models that
  required dev or RC builds. This means operators can adopt Codex without
  running pre-release software — a lower-risk enablement path worth flagging
  for teams with policies against pre-release dependencies.

## Extraction Notes

- Source read in full. Docusaurus blog post at
  `https://docs.litellm.ai/blog/gpt_5_3_codex`, published February 24, 2026.
  Page fetched via `WebFetch` (HTML-to-text extraction) with two passes to
  capture verbatim passages. All quoted passages were copied character-for-character
  from the rendered page text.
- The page is self-contained (a single announcement with config, Docker, curl,
  and Python examples). No outbound links to substantive related pages were
  found in the announcement body. Nothing paywalled or truncated.
- The post is notably thin — even for a LiteLLM Day-0 post — as the Prospector's
  triage comment noted. The only operational detail beyond the standard
  setup boilerplate is the `phase` metadata handling. The config.yaml has a
  single entry (no multi-backend setup), and the Docker run command contains
  what appears to be a copy-paste artifact (`-e ANTHROPIC_API_KEY=$OPENAI_API_KEY`).
  The Python example is the most substantive section.
- `confidence_overall` set to `emerging`: the first-party config and phase-handling
  detail is effectively settled how-to, but the post as a whole is a thin Day-0
  announcement whose primary value is one new concept (the `phase` parameter).
  The quality-degradation warning (Claim 5) is stated without supporting metrics
  or demonstration. This matches the `emerging` rating on sibling LiteLLM Day-0
  notes.
- No contradiction issue filed: verified against all existing source notes and
  open contradiction-labeled issues on the repo. No note makes an opposing claim
  about the `phase` parameter or Codex model metadata — the concept is entirely
  new to the corpus.
- Novelty per triage: low. The "Day 0 support" template is well-documented
  (six instances in the corpus across different providers). The mineable,
  non-obvious content is the `phase`-parameter pattern — captured above.
  The copy-paste artifact (`ANTHROPIC_API_KEY`) in the Docker command is noted
  for the Assayer's awareness but does not affect the extraction.
- The page renders the byline as "Feb 24, 2026"; recorded as
  `date_published: 2026-02-24`. The author byline reads "Sameer Kankute (SWE @
  LiteLLM, LLM Translation), Krrish Dholakia (CEO), and Ishaan Jaffer (CTO)".
  The author list matches the Gemini Day-0 posts (Sameer Kankute first author)
  rather than the Claude posts (Mateo Wang first author).
