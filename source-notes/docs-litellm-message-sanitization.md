---
source_url: https://docs.litellm.ai/docs/completion/message_sanitization
source_type: docs
title: "Message Sanitization for Tool Calling for anthropic models | liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-09-29)
date_extracted: 2026-09-29
last_checked: 2026-09-29
status: current
confidence_overall: settled
issue: "#1509"
---

# Message Sanitization for Tool Calling (LiteLLM Docs)

> The documented shape of the gateway rewriting the **caller's own message
> history** — not parameters, *content* — in flight before provider
> conversion: three mutations (inject a fabricated tool result, **delete** a
> tool result, overwrite empty content) that change what the model sees, are
> announced by nothing but debug logs, are gated on a **global-only** flag
> whose most intuitive per-request use breaks the call with a 400, and are
> applied on the Anthropic path only — so one `modify_params: true` makes the
> *same* message array produce provider-dependent semantics. This is the
> `messages` analogue of the `drop_params` knob and the substrate for
> guide/05-llm-ops-reliability.md's "Parameter migration hazards" and
> "Provider parity in the shared forwarding path" rules.

## Source Context

- **Type**: docs
- **Author credibility**: First-party LiteLLM gateway reference. Authoritative
  for *what the software documents doing*; it is a capability description, not
  a report of observed production behavior. There are no metrics, no incident
  reports, no customer evidence, and no methodology behind the performance
  figures. The page is undated. Current as of 2026-09-29.
- **Scope**: Covers `modify_params`-gated sanitization of OpenAI-format message
  arrays on the Anthropic transformation path: three cases, configuration
  placements, provider support, implementation pointers, logging, and an FAQ.
  Does **not** cover: message trimming (token budgets — separate page, issue
  #1510), parameter dropping (`drop_params`, issue #1480), the actual
  Anthropic protocol rules being satisfied, or any measured impact.
- **Independent verification performed by the Miner**: the page's claims were
  checked against the shipped implementation in `litellm` **v1.103.0** (latest
  release at extraction time, published 2026-09-28) via
  `litellm/litellm_core_utils/prompt_templates/factory.py` and a repo-wide code
  search. Results are in "Implementation Verification" below. The page itself
  cites no version, so doc/code skew is possible and is flagged per claim.

## Extracted Claims

### Claim 1: `modify_params=True` is the *only* switch, and it gates three named mutations of the outbound message array that run before provider-specific conversion
- **Evidence**: The Overview section enumerates the three cases; the "How It
  Works" section states the ordering ("runs **before** messages are converted
  to provider-specific formats") and names the three helper functions; the
  "Enable Globally" section lists exactly three placements (SDK module global,
  proxy `litellm_settings`, env var) plus a "No Per-Request Override" section.
- **Confidence**: settled (explicit vendor statement, repeated in four
  independent sections, and structurally confirmed by the shipped code — see
  Implementation Verification)
- **Quote**: "When `litellm.modify_params = True` is enabled, LiteLLM automatically sanitizes messages to fix three common issues:" / "The message sanitization process runs **before** messages are converted to provider-specific formats"
- **Our assessment**: Buy it. The three placements are a *global* blast radius
  by construction — there is no per-deployment and no per-request form, so this
  is a fleet-wide or process-wide switch on conversation content, not a
  per-model knob. That is the opposite shape from `drop_params`
  (`docs-litellm-drop-params.md` Claim 3, four documented placements including a
  per-request kwarg) and from `additional_drop_params` (Claim 4, "settable
  per-request or per-deployment"). Worth stating plainly in the guide: the
  remediation "just set the flag for this one call" that works for `drop_params`
  does not exist here.

### Claim 2: Case A **injects a fabricated tool result** into the model's context, and the vendor states the model cannot tell it apart from a real one
- **Evidence**: Case A section with a runnable example that comments in the
  message that will be added; the FAQ entry "What happens to the dummy tool
  results?" states the model-visible consequence. The injected `role`/`tool_call_id`
  pair mirrors a genuine tool result exactly.
- **Confidence**: settled (explicit vendor statement of both the injection and
  the indistinguishability; the placeholder string and its format are given
  verbatim)
- **Quote**: `content: "[System: Tool execution skipped/interrupted by user. No result provided for tool 'web_search'.]"` / "Dummy tool results are sent to the LLM provider along with other messages. The model sees them as regular tool results with informative error messages."
- **Our assessment**: This is the highest-consequence claim on the page and the
  one the guide is missing. A client bug, a user interrupt, or a network drop
  that loses a tool result does not surface as an error — it becomes a
  successful turn whose tool output is a LiteLLM-authored string. Downstream
  there is no discriminator: an eval harness, a transcript replay, or an
  incident reconstruction cannot distinguish "the tool ran and said this" from
  "the tool never ran". The page's own "When this happens" list (user
  interrupts, client loses results, conversation flow changes, tools optional
  in multi-turn) is a list of *normal* agent-loop events, not edge cases.
  Note the vendor is candid that this is a fabrication, not a repair — the
  "Best Practices" section's remedy is "provide actual tool results", which is
  caller-side work the gateway cannot do.

### Claim 3: Case B **deletes** an orphaned tool result outright — silent, unrecoverable loss of whatever the tool actually returned
- **Evidence**: Case B section; the FAQ and Troubleshooting sections describe
  only how to *prevent* the condition, never that the content is gone.
- **Confidence**: settled (explicit vendor statement of the removal; no
  compensating claim anywhere on the page that the content is preserved,
  summarized, or reported)
- **Quote**: "**Problem:** A tool message references a `tool_call_id` that doesn't exist in any previous assistant message." / "LiteLLM automatically removes these orphaned tool result messages."
- **Our assessment**: Asymmetric with Case A and worth naming as such. Case A
  fabricates; Case B **destroys evidence**. For an SRE reconstructing an
  incident, a tool result that the gateway classified as orphaned and dropped
  is evidence that no longer exists anywhere — not in the provider's logs, not
  in the client's array (the FAQ states the caller's list is unchanged), and
  not in the response. The page's troubleshooting entry for the *symptom*
  ("Unexpected Dummy Tool Results") only covers Case A; there is no
  troubleshooting entry for "my tool result disappeared". Note also the
  trigger is narrow and structural: a `tool_call_id` with no match in the
  *preceding assistant message* — so any client that reorders, merges, or
  compacts tool messages (message trimming, history summarization, resuming a
  session from a checkpoint) can trigger silent deletion of real tool output.

### Claim 4: Case C overwrites empty or whitespace-only content with a fixed system-bracketed string — including in list-of-blocks content
- **Evidence**: Case C section with a two-message example (`content: ""` and
  `content: "   "`) and the replacement shown for both.
- **Confidence**: settled for the string form (explicit vendor statement with
  the exact replacement); the *gating* of this case is contradicted by the
  shipped code — see Claim 6
- **Quote**: "LiteLLM replaces empty content with a system placeholder message." / `{"role": "user", "content": "[System: Empty message content sanitised to satisfy protocol]"}`
- **Our assessment**: The string is a fixed constant, so an empty turn is
  replaced by text that reads as a system notice but is delivered in a
  `user`/`assistant` role slot — the model receives a fabricated user turn
  saying the content was sanitized. For an eval or a transcript diff, that is
  indistinguishable from a user who typed that. Cheap to state, and it is the
  only one of the three cases that the vendor's own code shows running
  *unconditionally* on the Anthropic path (Claim 6) — so an operator who
  believes they have sanitization off may still have empty turns rewritten.

### Claim 5: The per-request override is a trap: `litellm.completion()` has no `modify_params` argument, and passing one forwards an unknown body field that Anthropic rejects with a 400
- **Evidence**: An entire "No Per-Request Override" section under Configuration,
  naming the exact rejection. Independently confirmed by the Miner: the
  `completion()` signature in `litellm/main.py` v1.103.0 contains no
  `modify_params` parameter and terminates its explicit parameters in
  `**kwargs`.
- **Confidence**: settled (explicit vendor statement of the failure, *plus*
  direct verification of the signature in the shipped code — the strongest
  single claim on the page)
- **Quote**: "Sanitization reads only the global `litellm.modify_params` flag, set by any of the options above. `litellm.completion()` has no `modify_params` argument, so passing `modify_params=True` on a call does not enable sanitization and is forwarded to the provider as an extra body field, which Anthropic rejects with `400 invalid_request_error: modify_params: Extra inputs are not permitted`"
- **Our assessment**: This is the claim the guide should quote, because it
  converts a would-be silent failure into a *loud* one — and the mechanism is
  already documented in the corpus. `docs-litellm-completion-input-params.md`
  Claim 3 states that any parameter LiteLLM does not classify as an OpenAI
  param "is assumed provider specific and passes it in as a kwarg in the
  request body". `modify_params` is exactly such a non-OpenAI param, so the
  intuitive per-request enable is guaranteed to be forwarded verbatim and
  rejected upstream. The operational shape is the one
  `docs-litellm-drop-params.md` Claim 1 documents in its other polarity: a
  config that *looks* like it enables a compatibility feature instead produces
  a hard 400 on every call that carries it. Practical consequence for a
  migration: a team adding `modify_params=True` to individual call sites
  converts a working Anthropic route into a 400-ing one, and the only working
  form is a process- or proxy-wide flag.

### Claim 6: The page states all three cases toggle together under `modify_params` with no selective disable — but the shipped code applies Case C unconditionally on the Anthropic path and adds a fourth, undocumented case
- **Evidence**: Page side — the FAQ answer plus the absence of any per-case
  switch anywhere on the page. Code side — verified in v1.103.0: (a)
  `anthropic_messages_pt()` calls `_sanitize_empty_text_content()` on every
  message *outside* the `modify_params` gate, with an in-code comment
  explaining that empty text blocks "will always 400 otherwise"; (b)
  `sanitize_messages_for_tool_calling()` contains a "Case D" that
  deduplicates tool results sharing a `tool_call_id`, which the page never
  mentions. Repo-wide code search confirms `sanitize_messages_for_tool_calling`
  is referenced only from `factory.py` and two test files.
- **Confidence**: settled for the *discrepancy* (both sides directly quoted
  below; the doc side is a single FAQ sentence, the code side is a shipped
  release). The page is undated, so it is possible the docs describe a
  different version than v1.103.0 — flagged, not resolved
- **Quote**: "Currently, all three cases are handled together when `modify_params=True`. To disable sanitization entirely, set `modify_params=False`."
- **Our assessment**: This is the finding, and it is why `confidence_overall`
  is `settled` despite the page being a bare vendor doc: the page's central
  control-flow claim is checkable, and it does not match the release. Two
  practical consequences. (1) `modify_params=False` does **not** restore
  pass-through of empty content on the Anthropic path — the rewrite is
  unconditional there and the code says so in a comment. An operator auditing
  "what does the gateway change about my messages when sanitization is off"
  will get the wrong answer from the docs. (2) There is a fourth mutation
  (duplicate `tool_result` collapse) that the vendor ships, that the docs do
  not describe, and that — unlike the other three — logs at **warning** level,
  not debug. Filed as contradiction **#1514**; the verdict is not ours to pick.

### Claim 7: The sanitization logic is described as provider-agnostic but applied only in the Anthropic transformation pipeline — so identical messages get provider-dependent treatment
- **Evidence**: "Supported Providers" section, a one-item ✅ list, plus a
  "Note" that disclaims the generality. Verified by the Miner in v1.103.0:
  `prompt_factory()` dispatches to `anthropic_messages_pt()` only on the
  `custom_llm_provider == "anthropic"` branch, and a repo-wide search finds
  no other caller of the sanitizer.
- **Confidence**: settled (explicit vendor statement, and the code search
  confirms the scope is exactly as stated — for the `anthropic/` provider route)
- **Quote**: "**Note:** While the sanitization logic is provider-agnostic, it is currently only applied in the Anthropic message transformation pipeline. Support for additional providers may be added in future releases."
- **Our assessment**: The vendor's note is narrower than the operational
  consequence. The scoping is not "Anthropic the *model*" but "Anthropic the
  *transport*": the same Claude model reached as `anthropic/claude-*` is
  sanitized, and the same Claude model reached as `bedrock/...` or
  `vertex_ai/...` does not go through this function at all. In a deployment
  with a `fallbacks:` list or a multi-provider route, a single
  `modify_params: true` therefore changes what the model sees on the primary
  route and not on the fallback route — the failover target sees a different
  conversation than the primary did, from the same client request. This is
  `docs-litellm-messages-to-responses-mapping.md` Claim 4's topology problem
  (a chained gateway silently loses `prompt_cache_key` because "the downstream
  proxy's real provider is unknown") applied to message *content* instead of
  cache affinity: behavior that depends on which provider happened to be
  selected.

### Claim 8: The only documented signal that any of this happened is three `verbose_logger.debug` lines behind `litellm.set_verbose = True` — nothing appears in the response and no metric is named
- **Evidence**: The "Logging" section, which is a code block of three comment
  lines rather than a description; the "Monitor Sanitization Events" best
  practice repeats the same SDK-only incantation. No section of the page
  mentions a response field, header, callback, or counter.
- **Confidence**: settled (the page is short and fully read; the omission is
  checkable by re-reading it, and the code confirms all three cases log
  through `verbose_logger.debug` or lower)
- **Quote**: `litellm.set_verbose = True  # Enable debug logging` / `"_add_missing_tool_results: Found 1 orphaned tool calls. Adding dummy tool results."` / `"_sanitize_empty_text_content: Replaced empty text content in user message"`
- **Our assessment**: Same shape as `docs-litellm-drop-params.md` Claim 9
  (the `drop_params` page documents no signal at all) and
  `docs-litellm-completion-input-params.md` Claim 6 (silent `stop`
  truncation, "no warning emitted") — but worse on one axis. A dropped
  *parameter* narrows the request; a fabricated *tool result* puts
  model-visible text into the transcript that the caller never wrote, and the
  default-log-level operator cannot see it. Two caveats the guide should carry
  rather than overstate: (a) the page documents `litellm.set_verbose` only as an
  **SDK** flag and never gives a proxy-config equivalent, so on a gateway
  deployment the documented detection path is unclear; (b) the Case D
  deduplication in Claim 6 *does* log at warning level, so "everything here is
  debug-only" is true of the three documented cases and not of the
  implementation. The honest rule: the only documented detection is a debug
  log, and the vendor documents no proxy-side way to turn it on.

### Claim 9: The page's own quoted log string for Case B does not match the shipped code — the docs show the offending `tool_call_id`, the code redacts it
- **Evidence**: The "Logging" code block on the page versus the
  `verbose_logger.debug` call inside `_is_orphaned_tool_result()` in v1.103.0.
- **Confidence**: settled (a directly re-checkable string comparison between
  the page and the release; both sides quoted below)
- **Quote**: `"_is_orphaned_tool_result: Found orphaned tool result with tool_call_id=call_123"`
- **Our assessment**: Small, but it is the canary for how to read every other
  log string on the page: the page's log examples are illustrative, not
  transcribed. Treat the three documented log lines as *shapes to grep for*,
  not exact strings to alert on — and prefer alert patterns that key on the
  function-name prefix (which is stable across both versions) over patterns
  that key on the id interpolation. Worth flagging to the Assayer: it means
  quotes from this page's code blocks should not be treated as transcripts.

### Claim 10: Sanitization does not mutate the caller's list — it returns a new one — so a caller inspecting its own messages after the call sees the originals intact
- **Evidence**: First FAQ entry, stated as a yes/no question with a negative
  answer. The code confirms it: `_sanitize_empty_text_content` and the
  Case B/C paths build a new `sanitized_messages` list, and the
  content-rewrite branch does an explicit `dict(message)` copy before
  mutating.
- **Confidence**: settled (explicit vendor statement, plus code structure)
- **Quote**: "No, sanitization creates a new list of messages. Your original messages remain unchanged."
- **Our assessment**: This is a *reassurance* the page offers and it deserves
  scrutiny, because it is true and irrelevant to the operator's actual
  question. The caller's array is unchanged; the **provider's** is not. A
  debugging workflow that diffs what the client sent against what the client
  still holds will show no diff, because the divergence happened on the wire.
  Combined with Claim 8 (no response-side signal), there is no documented
  artifact anywhere in the request/response cycle that reflects the mutation.

### Claim 11: The performance claim is an unevidenced vendor assertion — O(n) in the number of messages, "typically < 1ms" — with no measurement, workload, or hardware stated
- **Evidence**: A "Performance Impact" troubleshooting entry, three bullets,
  no methodology.
- **Confidence**: anecdotal (an assertion, not a measurement — recorded
  because an operator may encounter the claim and needs to know its weight)
- **Quote**: "Runs in O(n) time where n = number of messages" / "Typically adds < 1ms to request processing time"
- **Our assessment**: Do not carry this as evidence. The code is consistent
  with the complexity class (a single forward pass with a set of collected
  ids), but neither the complexity class nor the constant is load-bearing for
  any guide recommendation, and "typically" has no referent. Recorded so the
  Smith can see the claim was made and correctly discounted rather than missed.
  One adjacent, more useful implementation detail the page does give and the
  code confirms: the work is skipped entirely unless the flag is set — the
  sanitizer returns its input unchanged when `modify_params` is false (Case C
  aside; see Claim 6).

### Claim 12: `modify_params` and `drop_params` are explicitly separate features that compose, and the page draws the dividing line as "messages" vs "parameters"
- **Evidence**: A dedicated FAQ entry, "Is this related to `drop_params`?",
  with a two-item contrast and a composability statement. Cross-checked
  against the `drop_params` page, which never mentions `modify_params`.
- **Confidence**: settled (explicit vendor statement, one-directional by
  omission — the `drop_params` page does not cross-reference back)
- **Quote**: "No, they're separate features:" / "`modify_params` - Modifies/fixes message content and structure" / "`drop_params` - Removes unsupported API parameters" / "Both can be enabled simultaneously."
- **Our assessment**: Useful as a taxonomy anchor, with one caution: the
  "both can be enabled simultaneously" framing understates the coupling,
  because `drop_params` has a per-request kwarg (Claim 3 of the `drop_params`
  note) and `modify_params` has none (Claim 5 here). Operators migrating the
  two knobs together will discover the placement asymmetry only at the point
  where a per-request override is needed. The page's "Related Features" list
  also links message trimming, which is a third, distinct transform — token
  budget, not protocol validity — and is covered separately (issue #1510).

### Claim 13: Sanitization is applied to both streaming and non-streaming requests
- **Evidence**: FAQ entry "Does this work with streaming?". The code is
  consistent: the sanitizer operates on the message array before the
  transport split, so it cannot differ by stream mode.
- **Confidence**: settled (explicit vendor statement; structurally
  unsurprising)
- **Quote**: "Yes, message sanitization works with both streaming and non-streaming requests."
- **Our assessment**: Included because it closes off a plausible alternative
  explanation ("the gateway must skip sanitization to preserve stream
  semantics"). It does not: the transform is upstream of any streaming
  concern, which is also why a fabricated tool result is inserted identically on
  both paths. Low guide value on its own; useful as a bound on Claims 2 and 3.

## Concrete Artifacts

### The three mutations, as the page documents them

Page source: https://docs.litellm.ai/docs/completion/message_sanitization,
"Case A", "Case B", "Case C". The comment lines are the page's own — they show
what LiteLLM adds or removes.

```
# Case A — orphaned tool call: LiteLLM ADDS this message
# {
#     "role": "tool",
#     "tool_call_id": "call_abc123",
#     "content": "[System: Tool execution skipped/interrupted by user. No result provided for tool 'web_search'.]"
# }

# Case B — orphaned tool result: LiteLLM REMOVES the message entirely
{
    "role": "tool",
    "tool_call_id": "call_nonexistent",  # This tool_call_id doesn't exist!
    "content": "Some result"
}

# Case C — empty content: LiteLLM REPLACES content, in place, per message
{"role": "user", "content": "[System: Empty message content sanitised to satisfy protocol]"}
{"role": "assistant", "content": "[System: Empty message content sanitised to satisfy protocol]"}
```

### The three global enablement forms (page, "Enable Globally")

```
# SDK
import litellm
litellm.modify_params = True

# PROXY (config.yaml)
litellm_settings:
  modify_params: true

# Environment
export LITELLM_MODIFY_PARAMS=True
```

There is deliberately no fourth form. The page's "No Per-Request Override"
section is the documentation of that absence.

### The documented failure from trying anyway (page, verbatim)

```
400 invalid_request_error: modify_params: Extra inputs are not permitted
```

### The documented log lines (page, "Logging") — illustrative, see Claim 9

```
import litellm
litellm.set_verbose = True  # Enable debug logging
# You'll see logs like:
# "_add_missing_tool_results: Found 1 orphaned tool calls. Adding dummy tool results."
# "_is_orphaned_tool_result: Found orphaned tool result with tool_call_id=call_123"
# "_sanitize_empty_text_content: Replaced empty text content in user message"
```

### Troubleshooting entry with no counterpart for Case B (page)

```
### Unexpected Dummy Tool Results

**Issue:** Dummy tool results appear when you expect actual results

**Cause:** Tool result messages are missing or have incorrect `tool_call_id`
```

There is no "my tool result disappeared" entry, and no statement anywhere that
the deleted content is recoverable.

### Implementation Verification (Miner, not the page)

Source: `litellm/litellm_core_utils/prompt_templates/factory.py` at tag
**v1.103.0** (latest release, published 2026-09-28; retrieved 2026-09-29), plus
a repo-wide code search for `sanitize_messages_for_tool_calling`, which returns
exactly three files: `factory.py` and two test files. Nothing in the rest of
LiteLLM calls the sanitizer. The page is undated, so this is a point-in-time
check, not a version claim about what any given release shipped.

**The gate is a single early return, and the whole function is opt-in:**

```python
def sanitize_messages_for_tool_calling(
    messages: list[AllMessageValues],
) -> list[AllMessageValues]:
    ...
    if not litellm.modify_params:
        return messages
```

**Case A — the fabricated tool result, as implemented:**

```python
            dummy_tool_result: ChatCompletionToolMessage = {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": f"[System: Tool execution skipped/interrupted by user. No result provided for tool '{tool_name}'.]",
            }
            result_messages.append(dummy_tool_result)
```

The `role`/`tool_call_id` pair is structurally identical to a real tool
result; only the `content` string distinguishes it. The tool name falls back to
the literal `unknown_tool` when the call carries no parseable function name.

**Case B — the log line that does not match the page (Claim 9):**

```python
        verbose_logger.debug("_is_orphaned_tool_result: Found orphaned tool result with redacted tool_call_id")
```

The page prints `with tool_call_id=call_123`; the release prints
`with redacted tool_call_id`. The id is not in the log at all.

**Case C is applied outside the gate — the Claim 6 discrepancy.** In
`anthropic_messages_pt()`, immediately after the gated call and before the
Anthropic-specific rewriting:

```python
    # Sanitize messages for tool calling issues when modify_params=True
    messages = sanitize_messages_for_tool_calling(messages)

    # Anthropic rejects empty text content blocks with:
    #   "messages: text content blocks must be non-empty"
    # OpenAI/other providers silently tolerate `{"role": "user", "content": ""}`,
    # so callers (and upstream agent frameworks like pydantic-ai) routinely
    # send empty user/assistant turns. We always rewrite these to a placeholder
    # for Anthropic-shaped requests, independent of `litellm.modify_params`,
    # because there is no way to "pass through" an empty text block — the
    # request will always 400 otherwise. The richer tool-call sanitization
    # (Cases A/B/D in `sanitize_messages_for_tool_calling`) remains gated on
    # `modify_params` because it actually mutates conversation structure.
    messages = [_sanitize_empty_text_content(m) for m in messages]
```

Two things the page does not say and the code says explicitly: the
author's own reason for the asymmetry ("it actually mutates conversation
structure" — an intentional severity ranking of the three mutations), and the
`"messages: text content blocks must be non-empty"` rejection that motivates
it. The placeholder constant is module-level:

```python
_EMPTY_TEXT_PLACEHOLDER: Final = "[System: Empty message content sanitised to satisfy protocol]"
```

**The undocumented Case D — deduplication of tool results.** Present in
v1.103.0, absent from the page. It runs after the main loop, is *not* gated
separately (it inherits the function's `modify_params` gate), resets its
id-tracking at each non-tool message so reused ids across turns are not
collapsed, and keeps the **last** occurrence:

```python
    # Case D: Deduplicate tool results with the same tool_call_id.
    # Anthropic requires exactly one tool_result per tool_use. Session history
    # (e.g. from conversation resume) can contain duplicate tool_result messages
    # ...
    # NOTE: This intentionally keeps the *last* occurrence ...
    for idx, msg in enumerate(sanitized_messages):
        ...
            if tcid in seen_in_block:
                duplicates_to_remove.add(seen_in_block[tcid])
                verbose_logger.warning(
                    "sanitize_messages_for_tool_calling: dropping duplicate "
                    "tool_result with tool_call_id=%s. This may indicate "
                    "duplicate tool messages in conversation history.",
                    tcid,
                )
```

`verbose_logger.warning` — the only one of the four cases that is not
debug-only, and the only one the operator is told nothing about.

**Provider routing, confirming Claim 7.** In `prompt_factory()`:

```python
    elif custom_llm_provider == "anthropic":
        if litellm.AnthropicTextConfig._is_anthropic_text_model(model):
            return anthropic_pt(messages=messages)
        return anthropic_messages_pt(messages=messages, model=model, llm_provider=custom_llm_provider)
    elif custom_llm_provider == "anthropic_xml":
        return anthropic_messages_pt_xml(messages=messages)
```

The sanitized path is the `anthropic` provider branch only. `anthropic_xml`
routes to a different function, and Bedrock/Vertex/Gemini/OpenAI branches never
reach it.

**`completion()` has no `modify_params` parameter — Claim 5, verified.** The
`def completion(` signature in `litellm/main.py` (v1.103.0) runs for 128 lines
and contains no `modify_params` parameter; the explicit parameters terminate in
`**kwargs`, which is where a per-request `modify_params=True` lands and is
subsequently forwarded to the provider as a body field.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-litellm-completion-input-params.md` — **Claim 3** is the
    mechanism behind Claim 5: "LiteLLM assumes any non-openai param is
    provider specific and passes it in as a kwarg in the request body". That is
    exactly why `modify_params=True` on a call is forwarded and 400'd.
  - `source-notes/docs-litellm-completion-input-params.md` — **Claim 6**
    corroborates the failure *shape*: a request-mutating gateway behavior
    ("LiteLLM will automatically truncate the list to the first 4 elements")
    that is silent, with a single module-global escape hatch. Same family as
    Case A/B/C; different knob.
  - `source-notes/docs-litellm-drop-params.md` — **Claim 1** corroborates the
    loud branch: `drop_params` is what turns a raise into a silent drop. This
    page is the same design philosophy applied to message *contents*, and it is
    the knob family `docs-litellm-drop-params.md` explicitly separates (Claim 12
    quotes the page's own dividing line).
  - `source-notes/docs-litellm-messages-to-responses-mapping.md` — **Claim 1**
    corroborates the observability gap: "`stop_sequences` and `top_k` are
    silently dropped — a caller setting them gets a 200 with no error and no
    telemetry that the constraint was ignored". Same "gateway mutates the
    outbound request, caller cannot tell" pattern, different surface.
  - `source-notes/docs-litellm-messages-to-responses-mapping.md` — **Claim 4**
    corroborates the topology hazard: behavior that changes with which provider
    the gateway resolved, because "the downstream proxy's real provider is
    unknown". Claim 7 is the message-content version.
  - `source-notes/docs-litellm-anthropic-advisor-tool.md` — **Claim 9** is the
    closest sibling: on the *same* Anthropic pipeline the gateway rewrites
    conversation history (strips `advisor_tool_result` / `server_tool_use`
    blocks) to keep the provider happy. Two features, one underlying behavior:
    the gateway edits history in flight.

- **Contradicts**:
  - **The page contradicts its own implementation on Case C and omits Case D.**
    Side A (page): "Currently, all three cases are handled together when
    `modify_params=True`. To disable sanitization entirely, set
    `modify_params=False`." Side B (v1.103.0
    `litellm/litellm_core_utils/prompt_templates/factory.py`,
    `anthropic_messages_pt()`): `_sanitize_empty_text_content` is applied to
    every message **outside** the `modify_params` gate, with an in-code comment
    stating the rewrite is "independent of `litellm.modify_params`"; and a
    fourth case (duplicate `tool_result` deduplication) exists in
    `sanitize_messages_for_tool_calling()` that the page never describes.
    Filed as a contradiction issue: **#1514**. **No verdict is taken here.**
  - `source-notes/docs-litellm-drop-params.md` **Claim 3** vs this page's
    Claim 1, read as a *tension* rather than a conflict: the `drop_params`
    family has four documented placements including a per-request kwarg; the
    `modify_params` family has three global placements and the page
    explicitly forecloses the per-request one. Recorded because a guide
    sentence of the form "set the flag for this call" is correct for one and
    actively harmful for the other. Not filed as a contradiction — the pages
    make no claim about each other.

- **Extends**:
  - `source-notes/docs-litellm-drop-params.md` — the `modify_params` family.
    This note covers the *messages* gate; the `drop_params` note covers the
    *parameters* gate. Together they are the two halves of "what does the
    gateway change about my request", and the split is the page's own (Claim
    12).
  - `source-notes/docs-litellm-completion-input-params.md` — the message-shape
    and parameter-gate boundaries for `/chat/completions`; this note is the
    behavior-modification layer above it.
  - `source-notes/docs-litellm-anthropic-advisor-tool.md` — the same
    Anthropic-only transform pipeline; useful together when reasoning about
    what a Claude request looks like on the wire.

- **Novel**:
  - **Fabricated tool results as a first-class, documented gateway behavior**
    (Claim 2). Nothing in the corpus describes a gateway authoring
    model-visible tool output on the caller's behalf. The failure-report notes
    cover silent *omission* (`failure-litellm-model-cost-map-silent-fallback.md`)
    and silent *downgrade*, not silent *authoring*.
  - **Silent deletion of real tool output** (Claim 3) — a gateway destroying
    evidence with no replacement, no log at default levels, and no
    troubleshooting entry.
  - **A global-only flag whose per-request use is a hard 400** (Claim 5). The
    corpus has the mirror case (a per-deployment `drop_params` that silently
    narrows); the "the natural fix breaks the call" shape is new.
  - **Provider-*transport*-scoped content mutation** (Claim 7) — the same
    Claude model sanitized on one route and not on another.
  - **A documented vendor doc/code discrepancy in scope and in a quoted log
    string** (Claims 6, 9), with an undocumented fourth case at warning level.

- **Related, deliberately not merged**: message trimming (token budget) is a
  separate page and a separate issue (#1510); it is a *budget* transform, not
  a *protocol-validity* transform, and folding it in here would blur exactly
  the distinction the guide needs.

## Guide Impact

- **Chapter 05, §"Parameter migration hazards" (~L327-341)**: the section's
  rule is "audit existing request parameters against the model's supported set
  before routing production traffic. Parameters valid on earlier models may be
  silently ignored or explicitly rejected." This source is the *content*
  analogue the section does not cover, and it changes the remediation advice,
  not just the evidence. Add: when `modify_params` is on, the gateway itself
  may inject, delete, or overwrite items in `messages` — a request can be
  mutated by the proxy rather than by the model, and the three mutations are
  gated on a **global-only** flag. The guide's existing per-request remediation
  pattern (implicit in `drop_params`) does not transfer: `completion()` has no
  `modify_params` argument, and passing one is forwarded to Anthropic and
  rejected with `400 invalid_request_error: modify_params: Extra inputs are not
  permitted`. Cite Claim 5.
- **Chapter 05, §"Provider parity in the shared forwarding path" (~L343)**: a
  clean, vendor-documented instance of the section's thesis. One
  `modify_params: true` produces provider-dependent message content for the
  same input, because the transform is applied only on the `anthropic/`
  provider route. Add the sharper form the vendor does not state: the scoping
  is by *transport*, not by model, so `anthropic/claude-*` and
  `bedrock/...claude-*` routes to the same model get different treatment — which
  makes any `fallbacks:` list a place where failover changes conversation
  content. Cite Claims 1 and 7.
- **Chapter 05, §"A green eval is not evidence until you can name what it
  measured" (~L567)** and **§"Agent-loop cost caps fail open and expire"
  (~L1147)**: add the tool-result integrity precondition. An agent-loop eval
  over a client that intermittently drops tool results is measuring
  LiteLLM's placeholder string, not the tool, when `modify_params` is on, and
  nothing in the response distinguishes the two. Same for the transcript
  evidence used in incident reconstruction. Cite Claims 2, 3, and 10.
- **Chapter 02, §"The observability model for LLM applications"**: add a named
  gap. The only documented signal that the outbound conversation was rewritten
  is a `verbose_logger.debug` line behind `litellm.set_verbose = True`, and the
  page documents that flag only in SDK form with no proxy-config equivalent —
  so a gateway operator has no documented way to turn detection on. The
  caller's own message list is unchanged by design, so client-side diffing
  shows nothing. State it as a bounded claim: the three *documented* cases are
  debug-only (the undocumented fourth logs at warning). Cite Claims 8, 9, and
  10, and pair with `docs-litellm-drop-params.md` Claim 9, which establishes
  the corpus-wide pattern that gateway-side request mutation emits no
  caller-visible signal.
- **Chapter 06, §security/trust**: light touch, one line. A fabricated tool
  result is model-visible text the caller did not author, delivered in a
  `role: "tool"` slot structurally identical to a real result. The content
  string is a fixed, clearly-bracketed constant, so this is **not** an
  injection surface — frame it as provenance loss (you cannot tell from a
  transcript which tool outputs are real), not as prompt injection. Cite
  Claims 2 and 3.
- **Do not** carry the `< 1ms` / O(n) performance assertion into the guide. It
  is an unevidenced vendor claim (Claim 11) and the note is the only place it
  should live.

## Extraction Notes

- Full read of the page, including Overview, Why Message Sanitization?, Quick
  Start (both SDK and PROXY tabs), all three Sanitization Cases, Configuration
  (both subsections), Supported Providers, Implementation Details, four
  Best Practices, Related Features, three Troubleshooting entries, six FAQ
  entries, and See Also. No linked sub-page was followed: the four
  "Related Features" links are all separately-registered pages already covered
  or queued (`drop_params` → #1480, message trimming → #1510, function calling
  and reasoning content are outside this issue's scope), and following them
  would re-mine material this corpus already owns.
- **Implementation verification was performed by the Miner and is not part of
  the source.** Claims 6 and 9, and the verification items behind Claims 1, 5,
  7, 8, 10, and 13, were checked against `litellm` **v1.103.0** (latest release,
  published 2026-09-28), retrieved 2026-09-29. The page is **undated** and
  cites no version, so a doc/code skew is possible and the Miner's read is a
  point-in-time check rather than a claim about what every release shipped.
  Both sides of each discrepancy are quoted so a human resolver can judge
  without re-running the check. Repo-wide code search for
  `sanitize_messages_for_tool_calling` returns exactly three files
  (`factory.py` and two test files), which is the basis for the provider-scope
  verification in Claim 7.
- **A contradiction issue was filed** for the Case C gating and the Case D
  omission (docs FAQ vs v1.103.0 `anthropic_messages_pt()` /
  `sanitize_messages_for_tool_calling()`). Filed as **#1514**, with a
  recommended verdict of `unresolved` on the grounds that a version boundary
  needs establishing before a winner is picked. No verdict is taken here, per
  MINER.md §4a; a human (or Smith + human) assigns the `C-NNN` entry in
  CONTRADICTIONS.md.
  The pre-existing open contradiction issues (e.g. #1462, #1461 on the advisor
  tool; #1338 on A2A budget storage) were checked first — none covers
  `modify_params` or message sanitization.
- **Related-notes candidates** (`miner-related-notes.md`, 10 candidates) were
  each read against the claim they suggest. **Cited in Cross-References**:
  `docs-litellm-completion-input-params.md` (Claim 3 → Claim 5 mechanism;
  Claim 6 → failure shape), `docs-litellm-messages-to-responses-mapping.md`
  (Claim 1 → observability gap; Claim 4 → topology hazard),
  `docs-litellm-anthropic-advisor-tool.md` (Claim 9 → same-pipeline history
  rewrite), `docs-litellm-drop-params.md` (Claims 1, 3, 9). **Dismissed as
  lexical matches with no bearing on this page**:
  `docs-litellm-batches-api.md`, `docs-litellm-bedrock-invoke.md`,
  `docs-litellm-a2a-iteration-budgets.md`, `docs-litellm-audio-transcription.md`,
  `docs-litellm-a2a-agent-card.md`, `docs-litellm-a2a-cost-tracking.md`,
  `blog-litellm-auto-router-v2.md` — all retrieved on shared LiteLLM vocabulary
  ("silently", "tool", "config", "budget"); none mentions `modify_params`,
  message sanitization, or outbound content mutation. Per MINER.md §4b, every
  `Claim N` cited above was re-read in the cited note and the number confirmed
  against the claim's content, not approximated.
- **Provenance**: the page was auto-filed from the already-registered
  `litellm-docs` site-crawl seed, so no new registry entry is warranted and
  `registry/sources.json` is left untouched. There is no `source-notes/
  docs-litellm-message-sanitization.md` in the corpus, and no note, guide line,
  or open issue anywhere in the repo mentions `modify_params`,
  `sanitize_messages_for_tool_calling`, or either placeholder string
  (re-verified this session) — this is genuinely uncovered content.
- **Prose/code mismatch is a pattern here, not a one-off.** The page's quoted
  log line does not match the release (Claim 9), and the page's control-flow
  claim does not match the release (Claim 6).
  `docs-litellm-completion-input-params.md` Claim 5 (the page's prose default of
  600 seconds against a signature defaulting to `None`) found the same
  prose-vs-code disagreement on a different LiteLLM page, and
  `docs-litellm-anthropic-advisor-tool.md` Claim 12 found a page contradicting
  *itself* on a model ID. The Smith may want a standing note that LiteLLM
  documentation strings and code blocks in this corpus should be treated as
  illustrative, not transcribed.
- **Thinness**: the page is short in prose but dense in specifics — two exact
  placeholder strings, a named source file and function, three named helper
  functions, six log strings, one exact 400 message, and a three-item
  configuration table. Thirteen claims were extractable from the page alone;
  no claim required padding.
