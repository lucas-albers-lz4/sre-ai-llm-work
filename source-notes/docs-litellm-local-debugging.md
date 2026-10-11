---
source_url: https://docs.litellm.ai/docs/debugging/local_debugging
source_type: docs
title: "Local Debugging | liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; page's own `last_updated` field is 2026-10-09)
date_extracted: 2026-10-10
last_checked: 2026-10-10
status: current
confidence_overall: settled
issue: "#1662"
---

# Local Debugging (LiteLLM SDK Docs)

> The vendor's own Python-SDK debugging page, and the corpus's first
> first-party admission that a one-line debug toggle — `litellm._turn_on_debug()`
> — **logs API keys**, with the doc's only guard being an up-front
> "do not use in production" warning and no gate, redaction, or
> destination control. It documents three SDK debug handles and nothing
> server-side: the verbose toggle, `litellm.json_logs = True` (raw POST only),
> and the sanctioned per-call `logger_fn=` callback that receives a
> `model_call_dict`. It is a credential-exposure footgun on the SDK path that
> sits beside — and must not be conflated with — the proxy/gateway debug
> surface documented elsewhere.

## Source Context

- **Type**: docs (single-page LiteLLM SDK reference at
  `/docs/debugging/local_debugging`; raw markdown fetched from
  `https://docs.litellm.ai/docs/debugging/local_debugging.md`, HTTP 200,
  ~2.8 KB). The page's own front matter carries `last_updated: "2026-10-09"`,
  which is the closest thing to a publication date this living doc has.
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for *what the SDK documents doing*. This page is the vendor
  describing its own debug interface — no metrics, no test output, no incident
  detail, no changelog.
- **Scope**: Pure Python-SDK usage. Covers exactly three handles —
  `litellm._turn_on_debug()`, `litellm.json_logs = True`, and
  `completion(..., logger_fn=<callable>)` — plus the API-key-exposure warning
  and code samples. Does **not** cover: any CLI flag, any `config.yaml` /
  proxy setting, any server-side debug control, log destinations, redaction, or
  env-gating. The page renders/behaves at the SDK level; the gateway-side debug
  surface (`--detailed_debug`, `LITELLM_LOG=DEBUG`, `litellm_request_debug`,
  `request_correlation_in_logs`) is a different page and is out of scope here.

## Extracted Claims

### Claim 1: The vendor documents that `litellm._turn_on_debug()` logs API keys and states outright that it must not be used in production
- **Evidence**: The page's opening paragraph, which introduces both debug
  methods and then adds an explicit warning before any code. It is the only
  security statement on the page.
- **Confidence**: settled (explicit, unqualified first-party statement that the
  flag emits API keys)
- **Quote**: "There's 2 ways to do local debugging - `litellm._turn_on_debug()` and by passing in a custom function `completion(...logger_fn=<your_local_function>)`. Warning: Make sure to not use `_turn_on_debug()` in production. It logs API keys, which might end up in log files."
- **Our assessment**: This is the load-bearing claim and it is a *vendor
  admission*, not a community warning: the maintainers of the SDK say their own
  one-line debug switch writes live credential material into log storage.
  Two things make it guide-relevant rather than trivia. (1) It is a
  **credential-exposure surface on the SDK path**, which is the same failure
  *class* as the guardrail-logging incident
  (`failure-litellm-guardrail-logging-secret-exposure.md`) but reached through
  a *different* mechanism — operator intent rather than a sanitization bug in an
  observability integration. (2) The warning is a **caution, not a control**:
  the page offers no env gate, no non-prod-only guard, no redaction option, no
  way to constrain where the output goes. The operator's only protection is to
  remember not to set the flag in production — which is exactly the kind of
  memory-dependent safety control the guide's security chapters argue against.

### Claim 2: The page does not specify *which* key material is logged or to *which* destinations, so the exposure's blast radius is unstated
- **Evidence**: The warning sentence names "API keys" generically and says they
  "might end up in log files"; no paragraph, table, or code comment narrows
  which keys, in what encoding, or to which sinks (stdout, a logging handler,
  a file, a callback).
- **Confidence**: settled as an *absence* in the documentation (directly
  re-checkable — the page is short and the warning is the only security text)
- **Quote**: (no direct quote beyond Claim 1's warning; the absence itself is the finding)
- **Our assessment**: The honest read is that the vendor documents a broad,
  unbounded hazard with a broad remedy ("don't"). For an SRE writing a runbook
  this matters: the page cannot be used to reason about scope ("only the
  primary key is leaked" vs "all environment keys"), so the safe operating
  assumption is worst-case: any credentials visible to the process may be
  emitted wherever the process's logs are routed. We record this as a
  documented-absence claim, not as a claim about runtime behavior — per MINER
  §2a we do not invent a mechanism the page does not state.

### Claim 3: `_turn_on_debug()` is a one-line, process-global verbose toggle that prints "everything litellm is doing"
- **Evidence**: The "Set Verbose" section's prose and its code sample, whose
  only line that matters is the toggle; the code comment frames the change as a
  single line.
- **Confidence**: settled (explicit vendor statement of what the toggle does and
  how it is enabled)
- **Quote**: "This is good for getting print statements for everything litellm is doing." / `litellm._turn_on_debug() # 👈 this is the 1-line change you need to make`
- **Our assessment**: The "1-line change" framing is the operational point: a
  credential-leaking mode is one line away in any process, and the sample shows
  it enabled *before* `os.environ["OPENAI_API_KEY"]` / `COHERE_API_KEY` are set
  and before the `completion(...)` calls. The output is described as "print
  statements for everything litellm is doing" — i.e. unscoped verbose chatter,
  which is consistent with (but does not prove) the API keys landing in the
  same stream. We document the toggle as process-global by construction (it is
  set on the `litellm` module, not per-call), matching the module-global shape
  of other LiteLLM debug knobs in the corpus.

### Claim 4: `litellm.json_logs = True` is documented narrowly — it serializes only the raw outbound POST request as JSON, not the full debug surface
- **Evidence**: The "JSON Logs" section, a two-sentence prose block plus a
  "See Code" link. The scope sentence is explicit and self-limiting.
- **Confidence**: settled (explicit vendor scope statement)
- **Quote**: "If you need to store the logs as JSON, just set the `litellm.json_logs = True`." / "We currently just log the raw POST request from litellm as a JSON"
- **Our assessment**: Record the narrowness, and do **not** overstate it. The
  vendor's "currently just" is a self-described provisional scope: JSON logging
  here covers the outgoing request payload, not responses, not internal
  decisions, and not the verbose stream. Two consequences for the guide. (1)
  Anything the raw POST contains — including, on a misconfigured or debug
  request, credential material in headers or fields — is what gets serialized;
  the page does not claim `json_logs` redacts. (2) An operator who wants
  structured logs for *everything* is not served by this flag alone, so
  `json_logs` must not be described in the guide as "LiteLLM's structured
  logging mode" without the raw-POST-only qualifier.

### Claim 5: `logger_fn=<callable>` is the documented, sanctioned per-call inspection affordance — a callback that receives a `model_call_dict` and can *see or modify* the model call input/output
- **Evidence**: The "Logger Function" section, which states the use case
  (diagnosing a failing call and seeing "the exact params being set"), names the
  dict contract, and gives a complete runnable example.
- **Confidence**: settled (explicit vendor statement of the callback contract and
  the see/modify capability)
- **Quote**: "But sometimes all you care about is seeing exactly what's getting sent to your api call and what's being returned - e.g. if the api call is failing, why is that happening? what are the exact params being set?" / "In that case, LiteLLM allows you to pass in a custom logging function to see / modify the model call Input/Outputs." / "**Note**: We expect you to accept a dict object."
- **Our assessment**: This is the page's constructive half and the cleanest
  thing on it. It is the *counterpart* to the naive toggle: instead of turning
  on a credential-leaking verbose mode, the operator passes a scoped callback
  and inspects exactly what crossed the wire for that one call — the same
  "diff the outbound payload" reflex the corpus reaches for elsewhere
  (`docs-litellm-json-mode-structured-outputs.md` Claim 5). Two caveats we
  carry. (1) The vendor's wording says the callback can **"see / modify"** the
  call input/output — if `model_call_dict` is the structure actually sent, a
  callback is not read-only instrumentation but a request-mutation hook, and the
  page gives no warning about that capability. We record the vendor's wording
  and flag the mutation reading as *possible but not demonstrated* here; the
  page has no example that mutates. (2) `logger_fn` is **per-call**, unlike the
  process-global toggle, so it is the placement with the smallest blast radius —
  which is precisely why the guide should prefer it.

### Claim 6: All three debug handles are SDK-level; the page documents no proxy/CLI debug control, and the SDK-vs-proxy split matters for where a warning applies
- **Evidence**: The whole page is Python (`import litellm`, `completion(...)`),
  and its only non-code affordance is a Discord link; there is no CLI flag,
  `config.yaml` key, environment variable, or server deploy option anywhere.
- **Confidence**: settled as a scoping statement about the page (directly
  re-checkable — the page is ~2.8 KB and fully read)
- **Quote**: (no direct quote; the page's own scope is the finding — all three handles are Python SDK)
- **Our assessment**: Recorded to guard against a conflation the Prospector
  flagged: this page is the **SDK** debug surface, and a guide sentence of the
  form "enable LiteLLM debug logging in production" would be ambiguous/wrong if
  it merged `_turn_on_debug()` (SDK import toggle) with the proxy controls
  (`--detailed_debug`, `LITELLM_LOG=DEBUG`, etc.) that live on a different page.
  The credential-leak warning in Claim 1 is *scoped to the SDK toggle* and this
  page says nothing about whether a proxy debug mode has the same property; we
  do not transfer the claim across surfaces.

### Claim 7: The page documents `_turn_on_debug()` while other current corpus notes document `litellm.set_verbose = True` as the SDK debug toggle — the page states neither that they are equivalent nor which is current
- **Evidence**: This page names `_turn_on_debug()` (intro and "Set Verbose").
  `docs-litellm-message-sanitization.md` (Claim 8) and
  `docs-litellm-json-mode-structured-outputs.md` (Claim 5) both record
  `litellm.set_verbose = True` as the SDK debug affordance on other LiteLLM
  pages. This page never mentions `set_verbose`, and the other pages never
  mention `_turn_on_debug()`.
- **Confidence**: settled as a *documentation* observation (both names are
  directly quoted from their pages); whether the two are aliases, one is
  deprecated, or they compose is **not stated anywhere we read** — recorded as
  an open question
- **Quote**: `litellm._turn_on_debug() # 👈 this is the 1-line change you need to make`
- **Our assessment**: Do **not** assert the two are equivalent. The safe,
  checkable guide statement is that LiteLLM's own docs use two different names
  for what appears to be "turn on verbose logs" (`_turn_on_debug` here,
  `set_verbose` elsewhere) and never reconcile them — so an operator grepping
  for the toggle should search both. This is the same lightweight doc-to-doc
  inconsistency the corpus already records across LiteLLM pages (naming/prose-vs-
  code mismatches in `docs-litellm-completion-input-params.md` Claim 2 and
  `docs-litellm-message-sanitization.md` Claim 9). Not a contradiction: neither
  page makes a claim about the other, so per MINER §4a we do not file one.

## Concrete Artifacts

### The warning and the three handles (verbatim from page)

Intro paragraph (the credential warning):

> There's 2 ways to do local debugging - `litellm._turn_on_debug()` and by
> passing in a custom function `completion(...logger_fn=<your_local_function>)`.
> Warning: Make sure to not use `_turn_on_debug()` in production. It logs API
> keys, which might end up in log files.

"Set Verbose" sample (verbatim, page's comment preserved):

```python
import litellm
from litellm import completion

litellm._turn_on_debug() # 👈 this is the 1-line change you need to make

## set ENV variables
os.environ["OPENAI_API_KEY"] = "openai key"
os.environ["COHERE_API_KEY"] = "cohere key"

messages = [{ "content": "Hello, how are you?","role": "user"}]

# openai call
response = completion(model="gpt-5.6-luna", messages=messages)

# cohere call
response = completion("command-nightly", messages)
```

"Logger Function" section — contract and complete example (verbatim):

```python
def my_custom_logging_fn(model_call_dict):
    print(f"model call details: {model_call_dict}")
```

```python
from litellm import completion

def my_custom_logging_fn(model_call_dict):
    print(f"model call details: {model_call_dict}")

## set ENV variables
os.environ["OPENAI_API_KEY"] = "openai key"
os.environ["COHERE_API_KEY"] = "cohere key"

messages = [{ "content": "Hello, how are you?","role": "user"}]

# openai call
response = completion(model="gpt-5.6-luna", messages=messages, logger_fn=my_custom_logging_fn)

# cohere call
response = completion("command-nightly", messages, logger_fn=my_custom_logging_fn)
```

### What is *not* on the page (Miner inventory)

No shell command, no CLI flag, no `config.yaml`/proxy setting, no environment
variable for the toggle, no log-destination or redaction option, no statement of
*which* API keys are logged, and no test output or incident reference. The page's
only non-code elements are the warning, the three section bodies, and a Discord
invite ("Still Seeing Issues?").

## Cross-References

**Candidates from `miner-related-notes.md`** (each listed path cited or
dismissed, per MINER §4):

- `source-notes/docs-litellm-completion-input-params.md` — **Cited (Extends)**.
  Its Extraction Notes ("Duplicate-history note") record that `logger_fn` and
  `verbose` were checked against the current revision of the `/completion/input`
  page and found **absent** there (the current InputParams surface lists only
  `api_base`, `api_version`, `num_retries`, `context_window_fallback_dict`,
  `fallbacks`, `metadata`, the two cost overrides, and the prompt-template
  block). This page is the documented **home** of the `logger_fn` pattern those
  notes found missing — the two together close the loop: `logger_fn` is a
  real, documented completion kwarg, but it is documented on the debugging page,
  not on the input-params reference.
- `source-notes/docs-litellm-batches-api.md` — **Dismissed**: batch input-file
  rate limiting and per-record token accounting; no debug/logging surface.
- `source-notes/docs-litellm-completion-web-search.md` — **Dismissed**: provider
  web-search support matrix; unrelated.
- `source-notes/docs-litellm-bedrock-invoke.md` — **Dismissed**: native Bedrock
  Invoke passthrough route; unrelated to SDK debug toggles.
- `source-notes/docs-litellm-audio-transcription.md` — **Dismissed**:
  `/audio/transcriptions` endpoint and its support matrix; unrelated.
- `source-notes/docs-litellm-completion-web-fetch.md` — **Dismissed**: Anthropic
  web-fetch tool surface; unrelated.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Dismissed**: A2A
  per-session cost controls; unrelated.
- `source-notes/docs-langfuse-mcp-server.md` — **Dismissed**: Langfuse docs MCP
  server; different product, no claim overlap.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **Dismissed**:
  advisor tool via the gateway; unrelated.
- `source-notes/blog-litellm-auto-router-v2.md` — **Dismissed**: routing
  strategy blog; unrelated.

**Additional cross-references found by searching `source-notes/` and `guide/`:**

- **Corroborates**:
  - `source-notes/docs-litellm-message-sanitization.md` — **Claim 8**: "The
    only documented signal that any of this happened is three
    `verbose_logger.debug` lines behind `litellm.set_verbose = True` — nothing
    appears in the response and no metric is named." That claim establishes
    `litellm.set_verbose = True` as the SDK debug toggle elsewhere in the
    corpus and reinforces the theme that LiteLLM's debug output is a logging
    surface an operator has to reason about (here, one that the vendor says
    carries API keys). Also the naming-discrepancy anchor for Claim 7.
  - `source-notes/docs-litellm-json-mode-structured-outputs.md` — **Claim 5**:
    that page's SDK example sets `litellm.set_verbose = True # see the raw
    request made by litellm` as its "only introspection affordance" for
    checking the outbound payload. Same debug-toggle vocabulary and same
    verify-what-crossed-the-wire purpose as this page's `logger_fn` (Claim 5) —
    but note this page documents `_turn_on_debug()` and never `set_verbose`
    (Claim 7).
  - `source-notes/failure-litellm-guardrail-logging-secret-exposure.md` —
    **Corroborates the *theme*, not the mechanism**: that incident report is the
    corpus's canonical "logging/telemetry path is a credential-exposure
    surface" case (its Root Cause and Lesson 1). This page is the same *class*
    of hazard on a different path — an operator-intent SDK debug toggle rather
    than a sanitization bug in the guardrail logging integration. Both say the
    same thing: LiteLLM's logging surface must be treated as sensitive. No
    conflict; the notes are complementary (bug-triggered vs toggle-triggered
    exposure).

- **Contradicts**: None filed, and no self-contradiction on the page. The only
  candidate tension is the **naming relationship** in Claim 7
  (`_turn_on_debug()` here vs `set_verbose` in
  `docs-litellm-message-sanitization.md` Claim 8 and
  `docs-litellm-json-mode-structured-outputs.md` Claim 5). This is a
  documentation inconsistency across *different* pages that make no claim about
  each other — not two claims in opposition on the same point — so per MINER
  §4a it is recorded as an open question, not filed. Checked before deciding:
  open `contradiction`-labeled issues and `CONTRADICTIONS.md` cover no
  debug-toggle surface.

- **Extends**:
  - `source-notes/docs-litellm-completion-input-params.md` — see candidate note
    above; this page supplies the `logger_fn` documentation that note recorded
    as absent from the input-params page.
  - `source-notes/docs-litellm-message-sanitization.md` — the debug/observability
    half. That note documents the *mutations* whose only signal is a debug log;
    this note documents the *debug surface itself* (and its credential hazard).
    Read together they cover both ends of "the gateway does something and the
    only way to see it is debug output" — and both note that the debug output is
    itself something the vendor warns about.

- **Novel**:
  - **First source note in the corpus on LiteLLM's SDK-level local-debugging
    page** (the Prospector confirmed no note covers `_turn_on_debug`,
    `json_logs`, `logger_fn`, `proxy/debugging`, or `troubleshoot/`).
  - **First first-party statement that a debug toggle leaks API keys**
    (Claim 1) — distinct from the guardrail-logging incident, which was a bug,
    not a documented behavior.
  - **The `logger_fn` per-call wire-inspection pattern** (Claim 5) as the
    vendor-sanctioned alternative to the leaky global toggle.
  - **The SDK-vs-proxy debug-surface split** (Claim 6) — recorded so the guide
    does not conflate an import-level toggle with a server deploy flag.

## Guide Impact

- **Chapter 06 (Security and Trust), §"Gateway credential routing: declare,
  don't infer" and the surrounding secret-in-logs material**: add one rule
  sourced here. LiteLLM's own SDK docs state that `_turn_on_debug()` "logs API
  keys, which might end up in log files" and warn against production use, with
  no enforcement mechanism — a vendor-confirmed credential-exposure surface
  reached by operator intent. Recommend the guide name it as the SDK-path
  sibling of the guardrail-logging incident
  (`failure-litellm-guardrail-logging-secret-exposure.md`) and of the
  "Upstream URLs and secrets showing up in logs" symptom quoted from
  `blog-litellm-july-stability-update` Claim 2 (`guide/06-security-and-trust.md`
  ~L618). Cite Claim 1.
- **Chapter 02 (Observability), §"The observability model for LLM
  applications"**: add the SDK-side debug affordances as the concrete handles
  for "what actually crossed the wire" — `logger_fn=<callable>` for per-call,
  scoped inspection of the `model_call_dict` (preferred), `json_logs = True`
  for the raw outbound POST only, and `_turn_on_debug()` for full verbose
  output that must not be used in production. Record the caveat that
  `logger_fn`'s documented wording is "see / modify", so it is a potential
  request-mutation hook, not read-only. Cite Claims 3, 4, 5.
- **Chapter 05 (LLM Ops Reliability)**, incident-response / runbook context:
  where the guide advises toggling verbose logging to debug a gateway failure,
  add the guard that the LiteLLM SDK's most obvious verbose toggle is the one
  the vendor documents as leaking API keys, and that the sanctioned alternative
  is the per-call `logger_fn` callback. This converts a common reflex
  ("turn on debug") into a credential-safety decision. Cite Claims 1 and 5.
- **Do not** carry the page as proxy/gateway guidance. Its scope is the Python
  SDK (Claim 6); a guide statement that merges `_turn_on_debug()` with the proxy
  debug flags (`--detailed_debug`, `LITELLM_LOG=DEBUG`) would misattribute the
  warning to a surface this page does not cover.

## Extraction Notes

- Full read of the page via rendered HTML and via the site's raw markdown
  (`.../local_debugging.md`, HTTP 200, ~2.8 KB). Both agree. The page is short
  and fully covered: intro (with warning), Set Verbose, JSON Logs, Logger
  Function (+ Complete Example), Still Seeing Issues. No sub-page was followed:
  the only substantive link is a "See Code" pointer and a GitHub feedback
  issue — neither defines new behavior, and the sibling proxy-debugging page is
  explicitly out of scope for this note per the Prospector's scope note.
- **This is a thin, `priority:low` source and the note reflects that.** Per the
  Prospector's instruction to extract narrowly rather than inflate, the claims
  are limited to what the page actually states: the credential-leak warning, the
  three handles, the SDK-vs-proxy scoping, and one documented-but-unreconciled
  naming inconsistency. There is no shell command, metric, timestamp, YAML
  config, or incident detail to extract, and none is invented. The page was
  judged substantive enough to warrant a note (real prose + runnable samples),
  not low-value enough to skip.
- **Provenance**: auto-filed from the already-registered `litellm-docs`
  site-crawl seed, so no new registry entry is warranted and
  `registry/sources.json` / `registry/claims-index.json` are left untouched (per
  the repo's hard rules they are rebuilt after merge).
- **Related-notes candidates** (`miner-related-notes.md`, 10 candidates) were
  each checked against the claim they suggest: **cited** —
  `docs-litellm-completion-input-params.md` (Extends); **dismissed** — all nine
  others, retrieved on shared LiteLLM vocabulary and touching none of
  `_turn_on_debug`, `json_logs`, `logger_fn`, or SDK debug output. Additional
  cross-refs were found by searching `source-notes/` and `guide/`
  (`docs-litellm-message-sanitization.md` Claim 8,
  `docs-litellm-json-mode-structured-outputs.md` Claim 5,
  `failure-litellm-guardrail-logging-secret-exposure.md`). Per MINER §4b, each
  cited `Claim N` was re-read in its note and the number confirmed against the
  claim's content; the `docs-litellm-completion-input-params.md` reference is
  cited by section name ("Extraction Notes → Duplicate-history note") because
  the material is not a numbered claim there.
- **No contradiction issue filed**: the only tension (Claim 7's
  `_turn_on_debug` vs `set_verbose`) is a cross-page naming inconsistency, not
  opposing claims, and is recorded as an open question per MINER §4a.
- **Unresolved open questions** (flagged, not filled in): (a) which key
  material and which log destinations `_turn_on_debug()` actually touches, and
  whether a proxy debug mode shares the property; (b) whether `logger_fn`'s
  "see / modify" wording means the callback can mutate the outbound request (the
  page's example only prints); (c) the current-vs-deprecated relationship
  between `_turn_on_debug()` and `set_verbose`. These need code/release checks
  or a vendor statement; the page does not provide them.
