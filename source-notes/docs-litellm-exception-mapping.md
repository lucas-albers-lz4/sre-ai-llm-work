---
source_url: https://docs.litellm.ai/docs/exception_mapping
source_type: docs
title: "Exception Mapping | liteLLM (provider-error → exception-class → HTTP-status taxonomy)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; front-matter last_updated 2026-10-12)
date_extracted: 2026-10-13
last_checked: 2026-10-13
status: current
confidence_overall: emerging
issue: "#1692"
---

# Exception Mapping (LiteLLM Docs — `/docs/exception_mapping`)

> The authoritative provider-error → exception-class → HTTP-status contract for
> the LiteLLM gateway: one table maps 400/401/402/403/404/408/422/429/500/503/≥500
> to `openai`-subclassed classes, every returned exception carries three extra
> attributes (`status_code`, `message`, **`llm_provider`**), retryability is
> delegated to the status-only helper `litellm._should_retry(e.status_code)`, and
> the fail-open default collapses any **unmapped** provider error into
> `litellm.APIConnectionError` — the single most consequential operational hazard
> on the page, because an unknown provider failure is then indistinguishable from
> a transport failure to any alert keyed on connection errors.

## Source Context

- **Type**: docs — official LiteLLM / BerriAI vendor documentation, a living
  Docusaurus page at `/docs/exception_mapping`, nav position
  Python SDK → Configuration → Exception Mapping (the page's own sidebar lists
  it directly after "Completion Token Usage & Cost"). Front matter carries
  `last_updated: "2026-10-12"`, `canonical_url:
  https://docs.litellm.ai/docs/exception_mapping`, and a two-entry `related:`
  list (`/docs/completion/token_usage`, `/docs/mcp`). It also links out to the
  proxy-side [Error Reference](/docs/proxy/error_reference) "for the JSON error
  payload, the response headers, and how to tell a gateway error from a provider
  error" — that page is **not** part of this extraction (see Extraction Notes).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation —
  authoritative for the *documented* mapping, class hierarchy, and extra
  attributes the gateway guarantees. Not evidence of measured behavior: the page
  carries no version pin, no changelog entry, no error-rate data, and no failure
  writeup. It is also undated beyond `last_updated`.
- **Scope**: The status-code → exception table, the three universal extra
  attributes, the retry helper, the 402 router-cooldown rule, the Azure
  content-filter forensics path, and the provider × exception coverage matrix.
  Does **not** cover the proxy JSON error envelope / response headers (deferred
  to the linked Error Reference), fallback routing configuration, or any
  measured behavior of the classes.
- **Extraction method note**: quoted character-for-character from the page's raw
  markdown endpoint (`https://docs.litellm.ai/docs/exception_mapping.md`, HTTP
  200), which preserves the tables and code blocks exactly; the rendered HTML
  was read first for orientation.

## Extracted Claims

### Claim 1: The page publishes the gateway's provider-error → exception-class → HTTP-status contract as a single table, and asserts the classes are drop-in for existing OpenAI error handling
- **Evidence**: The intro sentence, then a 22-row table keyed on "Status Code / Error Type / Inherits from / Description", then the compatibility sentence immediately below it.
- **Confidence**: settled (explicit first-party contract statement about the vendor's own mapping)
- **Quote**: "LiteLLM maps exceptions across all providers to their OpenAI counterparts."
- **Quote**: "All our exceptions inherit from OpenAI's exception types, so any error-handling you have for that, should work out of the box with LiteLLM."
- **Our assessment**: This is the load-bearing claim of the page and the reason it belongs in the corpus: it converts "catch whatever the provider throws" into a *named, finite* contract. The qualifier matters — "inherit from OpenAI's exception types" is a compatibility promise about `except` clauses, not a promise that the *classification* is semantically correct for the underlying provider failure. Claim 3 is where that distinction bites.

### Claim 2: Every returned exception carries three additional attributes beyond the OpenAI base — `status_code`, `message`, and `llm_provider` — and this holds even for OpenAI and Azure, where the original exception object is passed through with `llm_provider` added
- **Evidence**: The three-bullet list immediately below the table, then the closing "Note" that carves out the OpenAI/Azure pass-through.
- **Confidence**: settled (explicit; the pass-through carve-out is stated precisely)
- **Quote**: "For all cases, the exception returned inherits from the original OpenAI Exception but contains 3 additional attributes:"
- **Quote**: "status_code - the http status code of the exception"
- **Quote**: "message - the error message"
- **Quote**: "llm_provider - the provider raising the exception"
- **Quote**: "**Note** For OpenAI and Azure we return the original exception (since they're of the OpenAI Error type). But we add the 'llm_provider' attribute to them."
- **Our assessment**: `llm_provider` is the quietly important field. It is the vendor-attribution signal that survives a cross-provider fallback path — the error path carries "which provider actually raised this," independent of the requested `model` string. That is the exact handle the guide's "Silent model fallback breaks attribution" section needs on the *error* axis, mirroring the response-`model` handle it already teaches (`guide/05-llm-ops-reliability.md:972`, citing `blog-litellm-claude-fable-5-day-0` Claim 6). Note the page documents the attribute's *presence* on every class but not its *values* (e.g. whether it is the `custom_llm_provider` slug or a display name), and the OpenAI/Azure carve-out means the added attribute is a mutation of a third-party exception object rather than a LiteLLM wrapper type — a detail an `isinstance`-based handler should know.

### Claim 3: The fail-open default is `litellm.APIConnectionError` — any **unmapped** provider error is returned as a connection error, and any unmapped ≥500 as `InternalServerError`
- **Evidence**: The description cell of the 500 `APIConnectionError` row, the "Base case" sentence above the coverage matrix, and the ≥500 `InternalServerError` row description.
- **Confidence**: settled (explicit, stated three ways on the page)
- **Quote**: "If any unmapped error is returned, we return this error" (the 500 `APIConnectionError` row description)
- **Quote**: "Base case we return APIConnectionError"
- **Quote**: "If any unmapped 500-status code error is returned, this error is raised" (the ≥500 `InternalServerError` row description)
- **Our assessment**: This is the sharpest operational caveat on the page and we buy it as a real alerting hazard. A novel provider failure mode that LiteLLM has no mapping for is silently reclassified as a *connection* error — the class an SRE is most likely to page on as "network/transport is broken." So a paging rule keyed on `APIConnectionError` (or on `status_code == 500`) will mis-attribute an unmapped provider-side rejection to infrastructure. It is also a one-way loss of information: once collapsed to `APIConnectionError`, the original provider error text survives only in `message`, and the correct-ness of any dashboards that split by exception class is only as good as this mapping's coverage (Claim 9's matrix is the coverage caveat). The guide should treat "unknown provider error" as its own watch item rather than trusting the connection-error bucket.

### Claim 4: Two 400 subclasses exist specifically to *drive fallback behavior* rather than to describe the error — `ContextWindowExceededError` (context-window fallbacks) and `ContentPolicyViolationError` (content-policy fallbacks)
- **Evidence**: The two table rows carry the mechanism in their descriptions, and the closing page note explains the granularity rationale for the context-window type.
- **Confidence**: settled (explicit "enables ... fallbacks" in the vendor's own description)
- **Quote**: "Special error type for context window exceeded error messages - enables context window fallbacks"
- **Quote**: "Special error type for content policy violation error messages - enables content policy fallbacks"
- **Quote**: "The `ContextWindowExceededError` is a sub-class of `InvalidRequestError`. It was introduced to provide more granularity for exception-handling scenarios."
- **Our assessment**: This is the mechanism sitting underneath the guide's fallback doctrine: the "context window fallback" path fires because the gateway classifies the failure as this specific type, not because of string matching on the provider message. That is exactly the "map provider error codes onto classes rather than string-matching error text" question the triage asked. It also means a provider whose context-window failure is *not* mapped to this type (alt: surfaces as a plain `BadRequestError`) will not trigger the fallback — the coverage matrix (Claim 9) is where an operator checks that. The remaining 400 types are descriptive, not behavioral: `UnsupportedParamsError` (unsupported params passed), `ImageFetchError` (image fetch/processing), and the deprecated `InvalidRequestError` ("Deprecated error, use BadRequestError instead").

### Claim 5: A provider 402 (`PaymentRequiredError`) is a routing event, not just a billing event — the router cools that deployment down when the model group has another deployment
- **Evidence**: The 402 table row, which states the router action in the description itself.
- **Confidence**: settled (explicit)
- **Quote**: "Raised when the provider answers 402, for example an account that is out of credits. The router cools that deployment down when its model group has another deployment"
- **Our assessment**: Material for Ch05's capacity/fallback material: spend exhaustion on one deployment is handled like a health failure — the router removes it from rotation while a sibling deployment exists. Three operational readings worth carrying: (1) a 402 can silently shrink the effective model group, so capacity math that assumes all deployments are live will be wrong during a credits outage; (2) the cooldown is *conditional* on "its model group has another deployment" — with a single-deployment group there is nothing to cool down to, so the 402 surfaces to the caller rather than being absorbed; (3) it is a router behavior documented on an error-mapping page, which is why an SRE scanning only the router docs would miss that 402 triggers cooldown. The page does not state the cooldown duration or how the deployment is re-admitted.

### Claim 6: Retryability is delegated to a **status-code-only** helper, `litellm._should_retry(e.status_code)` — the documented retry decision does not consult the exception class or the error body
- **Evidence**: The closing line of the "Usage - Should you retry exception?" snippet.
- **Confidence**: settled that this is the documented usage; the helper is private (leading underscore), and the page states no retry policy behind it.
- **Quote**: `should_retry = litellm._should_retry(e.status_code)`
- **Our assessment**: Two parts. First, this is the retryable-vs-terminal decision surface the triage asked for: retry policy is *derivable from status code* per the vendor's own example, rather than guessed. Second, the API is a **private** symbol (underscore-prefixed) documented as public guidance — the same "documented but not a stable contract" pattern the corpus records elsewhere; the page states no policy, no TTL, no backoff, and no list of which statuses it treats as retryable. The status-only signature is also the premise disputed by open contradiction **#1548** (see Claim 7 and Cross-References): a `budget_exceeded` 429 and a genuine rate-limit 429 are indistinguishable to a helper that reads only `status_code`.

### Claim 7: 429 maps unconditionally to `RateLimitError`, and `BudgetExceededError` is filed under status "N/A" — so this page does not encode the body-level 429 discrimination that the LiteLLM A2A budget docs require
- **Evidence**: The 429 row of the exception table; the `BudgetExceededError` row (status "N/A", inherits `Exception`); and the absence of any `type`/body-discriminant field anywhere on the page.
- **Confidence**: settled that the page states the mapping; the conflict consequence is graded as relevant to an *open* contradiction, not asserted as resolved.
- **Quote**: "| 429 | RateLimitError | openai.RateLimitError |" (the 429 table row)
- **Quote**: "| N/A | BudgetExceededError | Exception | Raised for proxy, when budget is exceeded |" (the `BudgetExceededError` row)
- **Our assessment**: This is the page's interface with open contradiction **#1548** (HTTP 429 retryability: promptfoo treats 429 as unconditionally transient-retryable, vs LiteLLM A2A's `budget_exceeded` 429 which "cannot be distinguished by status code alone"). This page is a *third* data point and it lines up with the promptfoo/status-only side: it maps 429 → `RateLimitError` and offers `_should_retry(e.status_code)` (Claim 6), which cannot see the `"type": "budget_exceeded"` body discriminant that `docs-litellm-a2a-iteration-budgets.md` Claim 5 documents. So LiteLLM's own error-taxonomy reference does not surface the discrimination its A2A budget page requires — exactly the status-code-only premise #1548 disputes. Per MINER §4a we do **not** file a new contradiction (one is already open and covers this) and we do **not** pick a verdict; the note records the page's statement and links the conflict. Note also the return-type asymmetry: `BudgetExceededError` inherits from bare `Exception`, not from an OpenAI type, so it is the one class a generic `except openai.APIError` handler will *miss*.

### Claim 8: Azure OpenAI content-policy forensics are reachable only through `provider_specific_fields["innererror"]["content_filter_result"]`, with per-category `filtered`/`severity` and the sample `code: "ResponsibleAIPolicyViolation"`
- **Evidence**: The "Accessing Provider-Specific Error Details" section's prose, its worked `except ContentPolicyViolationError` snippet, and the sample JSON error structure.
- **Confidence**: settled (documented access path plus a full sample payload)
- **Quote**: "LiteLLM exceptions include a `provider_specific_fields` attribute that contains additional error information specific to each provider."
- **Quote**: "When Azure OpenAI returns content policy violations, you can access the detailed content filtering results through the `innererror` field:"
- **Our assessment**: This is the corpus's first concrete *content-policy forensics* surface: after a `ContentPolicyViolationError` fires (Claim 4's fallback trigger), the reason — and the per-category severity — lives in a provider-specific nested field, not in the top-level exception. Categories documented in the sample: `hate`, `jailbreak`, `self_harm`, `sexual`, `violence`, each with `filtered` and (for most) `severity`, plus the outer `code: "ResponsibleAIPolicyViolation"`. For an SRE building policy-violation alerting or an eval harness classifying block reasons, this is the documented path — and the fact that it is Azure-specific while the 400 `ContentPolicyViolationError` is provider-generic is itself the caveat: a content-policy 400 from a *non-Azure* provider will not carry this `innererror` structure, and the page documents no generic equivalent.

### Claim 9: A provider × exception coverage matrix exists, and the page's own caveat is that empty cells mean "lack of association" — the exact per-provider capability set is not asserted
- **Evidence**: The "Custom mapping list" matrix (rows: `openai`, `anthropic`, `bedrock`, `azure`, `vertex_ai`, `gemini`, `cohere`, `ollama`, `vllm`, and ~15 more; columns: the 11 exception families), plus the two bullet notes beneath it and the "Base case" sentence above it.
- **Confidence**: settled for the caveat's wording; the matrix is a coverage table, not evidence.
- **Quote**: "Base case - we return `litellm.APIConnectionError` exception (inherits from openai's APIConnectionError exception)."
- **Quote**: "- \"✓\" indicates that the specified `custom_llm_provider` can raise the corresponding exception."
- **Quote**: "- Empty cells indicate the lack of association or that the provider does not raise that particular exception type as indicated by the function."
- **Our assessment**: The genuine operational value is the *caveat*, not the cells: a fallback or alerting rule that assumes `anthropic` raises the same exception set as `bedrock` (or as `openai`) is **not supported by this table**. The page gives no way to distinguish "this provider never raises this type" from "we simply haven't recorded it," and `APIConnectionError` remains the documented fallback for every gap (Claim 3). The guide should therefore not derive provider-parity claims cell-by-cell from this matrix; use it to know *the fallback bucket is the default* for under-documented providers, and to reject parity assumptions.

### Claim 10: The page's streaming example recommends catching the specific OpenAI type first and a generic `except Exception` as the fallback — the only acknowledgment that streaming errors surface like synchronous ones
- **Evidence**: The "Usage - Catching Streaming Exceptions" snippet, which wraps a `stream=True` call and a `for chunk in response` iteration and closes with a broad `except Exception`.
- **Confidence**: settled (the snippet is explicit); the page states no prose rationale.
- **Quote**: `except openai.APITimeoutError as e:`
- **Quote**: `except Exception as e:`
- **Quote**: `print(f"Did not raise error \`openai.APITimeoutError\`. Instead raised error type: {type(e)}, Error: {e}")`
- **Our assessment**: Two readings. The useful one: errors on a streamed call are raised *inside the iteration* and are catchable with the same class hierarchy as non-streaming, so exception-based handling is portable across `stream=True`. The cautionary one: the example's generic `except Exception` is the same swallow-everything shape the corpus already flags in LiteLLM's own streaming sample (`docs-litellm-completion-stream.md` Claim 14), and here the page offers it without a comment on what gets swallowed — including `BudgetExceededError` (Claim 7), which inherits bare `Exception` and would be caught by that final clause.

### Claim 11: The page contradicts itself on `ContextWindowExceededError`'s parent — the table says it inherits `litellm.BadRequestError`, while the page's own closing note calls it a sub-class of `InvalidRequestError`
- **Evidence**: The 400 `ContextWindowExceededError` table row vs. the final paragraph of the "Custom mapping list" section; the `InvalidRequestError` row is simultaneously documented as a *deprecated* alias of `openai.BadRequestError`.
- **Confidence**: settled (both strings are on the page, verbatim, and are mutually inconsistent about the immediate parent)
- **Quote** (table row): "| 400         | ContextWindowExceededError| litellm.BadRequestError | Special error type for context window exceeded error messages - enables context window fallbacks |"
- **Quote** (closing note): "The `ContextWindowExceededError` is a sub-class of `InvalidRequestError`. It was introduced to provide more granularity for exception-handling scenarios."
- **Quote** (table row): "| 400 | InvalidRequestError | openai.BadRequestError | Deprecated error, use BadRequestError instead |"
- **Our assessment**: Recorded as an internal documentation tension, **not** filed as a contradiction issue (per MINER §4a — a page-level parent-chain discrepancy with no divergent guide advice). The practical question it raises is the one a fallback handler depends on: if `ContextWindowExceededError` subclasses `litellm.BadRequestError` (table), then `except litellm.BadRequestError` catches it; if it subclasses the *deprecated* `InvalidRequestError`, then code written against the recommended `BadRequestError` may or may not. Either way the page itself says not to use `InvalidRequestError` ("Deprecated error, use BadRequestError instead") while the closing note hangs the fallback class off it. Flagged for the maintainers; the safe operator position is to catch `ContextWindowExceededError` by name.

## Concrete Artifacts

All artifacts verbatim from `https://docs.litellm.ai/docs/exception_mapping.md` (the page's own raw markdown endpoint, which preserves the tables).

**The exception table, verbatim** (the page's central artifact; rendered as one block):

```
| Status Code | Error Type               | Inherits from | Description |
|-------------|--------------------------|---------------|-------------|
| 400         | BadRequestError          | openai.BadRequestError |
| 400 | UnsupportedParamsError | litellm.BadRequestError | Raised when unsupported params are passed |
| 400         | ContextWindowExceededError| litellm.BadRequestError | Special error type for context window exceeded error messages - enables context window fallbacks |
| 400         | ContentPolicyViolationError| litellm.BadRequestError | Special error type for content policy violation error messages - enables content policy fallbacks |
| 400         | ImageFetchError | litellm.BadRequestError | Raised when there are errors fetching or processing images |
| 400 | InvalidRequestError | openai.BadRequestError | Deprecated error, use BadRequestError instead |
| 401         | AuthenticationError      | openai.AuthenticationError |
| 402         | PaymentRequiredError     | litellm.BadRequestError | Raised when the provider answers 402, for example an account that is out of credits. The router cools that deployment down when its model group has another deployment |
| 403         | PermissionDeniedError    | openai.PermissionDeniedError |
| 404         | NotFoundError            | openai.NotFoundError | raise when invalid models passed, example gpt-8 |
| 408 | Timeout | openai.APITimeoutError | Raised when a timeout occurs |
| 422         | UnprocessableEntityError | openai.UnprocessableEntityError |
| 429         | RateLimitError           | openai.RateLimitError |
| 500         | APIConnectionError       | openai.APIConnectionError | If any unmapped error is returned, we return this error |
| 500         | APIError | openai.APIError | Generic 500-status code error |
| 503 | ServiceUnavailableError | openai.APIStatusError | If provider returns a service unavailable error, this error is raised |
| >=500       | InternalServerError      | openai.InternalServerError | If any unmapped 500-status code error is returned, this error is raised |
| N/A         | APIResponseValidationError | openai.APIResponseValidationError | If Rules are used, and request/response fails a rule, this error is raised |
| N/A | BudgetExceededError | Exception | Raised for proxy, when budget is exceeded |
| N/A | JSONSchemaValidationError | litellm.APIResponseValidationError | Raised when response does not match expected json schema - used if `response_schema` param passed in with `enforce_validation=True` |
| N/A | MockException | Exception | Internal exception, raised by mock_completion class. Do not use directly |
| N/A | OpenAIError | openai.OpenAIError | Deprecated internal exception, inherits from openai.OpenAIError. |
```

**The retry helper, verbatim** (Claim 6) — a private, status-code-only decision:

```python
except openai.APITimeoutError as e:
    should_retry = litellm._should_retry(e.status_code)
    print(f"should_retry: {should_retry}")
```

**The streaming catch pattern, verbatim** (Claim 10) — specific type first, bare `Exception` last:

```python
    for chunk in response:
        print(chunk)
except openai.APITimeoutError as e:
    print("Passed: Raised correct exception. Got openai.APITimeoutError\nGood Job", e)
    print(type(e))
    pass
except Exception as e:
    print(f"Did not raise error `openai.APITimeoutError`. Instead raised error type: {type(e)}, Error: {e}")
```

**The Azure content-filter error structure, verbatim** (Claim 8) — the documented sample JSON returned by the proxy:

```json
{
  "error": {
    "message": "litellm.ContentPolicyViolationError: AzureException - The response was filtered due to the prompt triggering Azure OpenAI's content management policy...",
    "type": null,
    "param": null,
    "code": "400",
    "provider_specific_fields": {
      "innererror": {
        "code": "ResponsibleAIPolicyViolation",
        "content_filter_result": {
          "hate": { "filtered": true, "severity": "high" },
          "jailbreak": { "filtered": false, "detected": false },
          "self_harm": { "filtered": false, "severity": "safe" },
          "sexual": { "filtered": false, "severity": "safe" },
          "violence": { "filtered": true, "severity": "medium" }
        }
      }
    }
  }
}
```

**The provider × exception coverage matrix, verbatim** (Claim 9 — rows and columns trimmed to the header + a representative subset; the full table ships ~23 provider rows in the source):

```
| custom_llm_provider | Timeout | ContextWindowExceededError | BadRequestError | NotFoundError | ContentPolicyViolationError | AuthenticationError | APIError | RateLimitError | ServiceUnavailableError | PermissionDeniedError | UnprocessableEntityError |
| openai              | ✓       | ✓                          | ✓               |               | ✓                           | ✓                   |          |                |                         |                       |                           |
| anthropic           | ✓       | ✓                          | ✓               | ✓             |                             | ✓                   |          |                | ✓                       | ✓                     |                           |
| bedrock             | ✓       | ✓                          | ✓               | ✓             |                             | ✓                   |          | ✓              | ✓                       | ✓                     |                           |
| vertex_ai           | ✓       |                            | ✓               |               |                             |                     | ✓        |                |                         |                       | ✓                         |
| azure               | ✓       | ✓                          | ✓               | ✓             | ✓                           | ✓                   |          |                | ✓                       |                       |                           |
| vllm                |         |                            |                  |               |                             | ✓                   | ✓        |                |                         |                       |                           |
```

## Cross-References

**Candidates from `miner-related-notes.md`** (read before writing Cross-References per MINER §4; every listed path cited or dismissed):

- `source-notes/docs-litellm-completion-input-params.md` — **cited** (Corroborates, Extends; Claims 4 and 13 verified). **Claim 4** (`context_window_fallback_dict` "fires only on a context-window error, where `fallbacks` fires on any call failure") is the *configuration* half of this page's Claim 4 — this page supplies the exception type (`ContextWindowExceededError`) that gives that trigger its granularity. **Claim 13** ("SDK-level `fallbacks` has no time budget, no loop and no cooldown — each entry is tried exactly once in order, total failure raises the last error suffixed `All fallback attempts failed`") is what an operator's fallback *chain* does once a class of this page triggers it.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **cited** (Contradicts via open issue **#1548**; Claim 5 verified). Its **Claim 5** documents a 429 carrying `"type": "budget_exceeded"` that "cannot be distinguished by status code alone," which is precisely what this page's 429 → `RateLimitError` row (Claim 7) and `_should_retry(e.status_code)` (Claim 6) cannot encode. See the primary Contradicts entry below.
- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch JSONL rate limiting, per-record TPM reservations, and the pre-forward 429. Shares the status-code vocabulary only; it documents no exception classes and no error taxonomy.
- `source-notes/docs-litellm-completion-web-search.md` — **dismissed**: provider web-search support matrix; no error-class content.
- `source-notes/docs-litellm-bedrock-invoke.md` — **dismissed**: `/invoke` passthrough routing and SigV4→bearer auth swap; no exception taxonomy.
- `source-notes/docs-litellm-audio-transcription.md` — **dismissed**: per-request `fallbacks[]` on a non-chat endpoint plus `model_info: mode` registration. It documents a fallback *path* but not the exception contract that triggers it (this page's subject); adjacency only.
- `source-notes/blog-litellm-auto-router-v2.md` — **dismissed**: complexity/semantic/adaptive routing tiers and the per-request decision log. It is the corpus's reference for *routing decisions*, not for the exception classes that feed the router's cooldown (this page's Claim 5); no claim overlap.
- `source-notes/docs-litellm-mock-requests.md` — **dismissed**: `mock_response` stubbing and null `usage`; the `MockException` row here is a one-line footnote, not a shared subject.
- `source-notes/docs-litellm-completion-web-fetch.md` — **dismissed**: Anthropic `web_fetch_20250910` tool parameters; no error classes.
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**: agent spectrum, read/write guardrails, pre-on-caller; not about gateway error taxonomy.

**Additional cross-references found by searching `source-notes/` directly** (all verified per MINER §4b; non-claim sections cited by section name):

- `source-notes/docs-litellm-completion-stream.md` — **cited** (Corroborates; Claims 1 and 8 verified). **Claim 1** is the corpus's other appearance of the exact class-and-retry pattern this page's ≥500 row documents: LiteLLM "raise[s] a `litellm.InternalServerError`, to allow retry logic to happen" for a looping stream — i.e. the unmapped-500 type here (Claim 3) is deliberately reused as a **retryable** signal elsewhere, which tempers reading `InternalServerError` as purely terminal. **Claim 8** (the abort fires mid-iteration after partial output is delivered, so a client-side classifier cannot distinguish it from a provider 500) is the concrete hazard of a blanket status/class retry rule.
- `source-notes/failure-litellm-model-cost-map-silent-fallback.md` — **cited by section name** (Extends/Corroborates; its headings are Symptoms/Lessons, not `### Claim N`, so cited per §4b rule 4). **Lesson 2** ("Silent fallback to stale local data is worse than failing loudly — a logged warning lets operators connect symptoms to causes") and **Lesson 3** (out-of-band failures need their own probes) are the general principle this page's fail-open default (Claim 3) instantiates for the *error* path: an unmapped provider error is fixed into a known bucket with no signal that a mapping is missing. Its **External-dependency catalog** artifact is the template for cataloging the per-provider coverage gaps this page's Claim 9 caveat exposes.
- `source-notes/docs-litellm-cost-map-and-response-cost.md` — **cited as adjacent** (records a pointer, no claim overlap). Its front matter lists `/docs/exception_mapping` in its `related:` array, confirming the two pages are the vendor's paired SDK references (cost/token and errors). It records no exception-taxonomy content — this note fills that gap rather than extending it.
- `source-notes/failure-litellm-vllm-embeddings-encoding-format.md` — **cited** (Corroborates; Claim 3 verified). Its **Claim 3** (a parameter change completely failed vLLM embeddings "for ~3 hours while OpenAI and other providers ... were unaffected") is the corpus's canonical example of the *provider-scoped* failure this page's `llm_provider` attribute (Claim 2) and coverage matrix (Claim 9) are meant to make attributable — and the source the guide's Ch02 provider-breakdown rule already cites.
- **No prior `docs-litellm-exception-mapping.md`** exists (checked `source-notes/`); no open/closed issue duplicates it (triage verified; `gh` search confirms #1692 is the only `exception_mapping` issue).

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-completion-stream.md` **Claim 1, Claim 8** — `litellm.InternalServerError` as the retryable-500 type (Claim 3 here) and the mid-stream abort whose class is indistinguishable from an upstream 500.
  - `source-notes/docs-litellm-completion-input-params.md` **Claim 4, Claim 13** — the fallback configuration whose triggers are the `ContextWindowExceededError` / fallback classes on this page.
  - `source-notes/failure-litellm-vllm-embeddings-encoding-format.md` **Claim 3** — a real provider-scoped failure, the case `llm_provider` attribution and the coverage matrix exist to expose.
  - `source-notes/failure-litellm-model-cost-map-silent-fallback.md` **Lesson 2, Lesson 3** (by section) — the general "silent classification erodes observability" principle applied here to the error path.
- **Contradicts**:
  - **Open contradiction #1548** (already filed; not re-filed here per MINER §4a). #1548 pitches promptfoo's "429 is unconditionally transient-retryable" against
    `source-notes/docs-litellm-a2a-iteration-budgets.md` **Claim 5** (a LiteLLM 429 with `"type": "budget_exceeded"` that must be discriminated by body, not status). **This page is a LiteLLM-side data point for the status-only position**: Claim 7 maps 429 unconditionally to `RateLimitError`, `BudgetExceededError` is filed under status "N/A" with no 429 link, and Claim 6's `_should_retry(e.status_code)` reads only the status code. The page therefore does not encode the body-level discrimination its own A2A budget page requires. No verdict is picked here; the conflict stays with #1548 for human resolution.
  - No claim-level opposition with any existing *source note* beyond the above: the other LiteLLM notes document fallbacks, cost maps, transport, or streaming without asserting a contradictory exception contract.
- **Extends**:
  - `guide/05-llm-ops-reliability.md` §"Silent model fallback breaks attribution" — currently rule-only on the response-`model` field; this page adds the **error-axis** attribution handle (`llm_provider` on every exception, Claim 2).
  - `failure-litellm-model-cost-map-silent-fallback.md` **Lesson 5** (the dependency-inventory template) — Claim 9's per-provider coverage caveat is a new row-family for that catalog (which exception families each provider can raise, and that `APIConnectionError` is the documented fallback for the gaps).
- **Novel**: The corpus's first **exception taxonomy** source — the status→class table itself, the universal `status_code`/`message`/`llm_provider` attribute set, `litellm._should_retry` as the status-only retry contract, the 402→router-cooldown rule, the Azure `innererror` content-filter path, and the provider × exception coverage matrix with its "lack of association" caveat. No prior note covers any exception class.

## Guide Impact

- **Chapter 05 (§"Silent model fallback breaks attribution", `guide/05-llm-ops-reliability.md:972`)**: Add the **error-path** counterpart to the existing response-`model` rule. The section already teaches "Surface the `model` field from the response metadata ... do not infer it from the request." This source documents the same discipline for failures: every LiteLLM exception carries `llm_provider` ("the provider raising the exception"), so failure attribution should be read from the exception attribute, not inferred from the requested model or provider. Concrete recommendation: tag error metrics/logs with `llm_provider` and `status_code` alongside the request's model, so a cross-provider fallback that fails on the *second* provider is attributed to the provider that actually raised it.
- **Chapter 05 (§"Cost, capacity, and fallback patterns")**: Add the two fallback-trigger classes and the 402 routing rule as the mechanism behind the chapter's fallback guidance: (1) `ContextWindowExceededError` and `ContentPolicyViolationError` are distinct types *created to enable* the corresponding fallback paths (Claim 4) — so the recommended approach is to configure fallbacks against **classes**, not string-matched provider messages, and to verify on the coverage matrix (Claim 9) that the relevant provider can raise the class; (2) a 402 `PaymentRequiredError` causes the **router to cool the deployment down** when the model group has another deployment (Claim 5) — spend exhaustion is a capacity/routing event, and capacity math must not assume all deployments stay in rotation during a credits outage.
- **Chapter 05 (Retry policy) and open contradiction #1548**: Record that LiteLLM documents retryability as a **status-code-only** decision (`litellm._should_retry(e.status_code)`, Claim 6) and maps 429 unconditionally to `RateLimitError` (Claim 7), and that this is the premise open contradiction **#1548** disputes for `budget_exceeded` 429s. Do not present "429 is transient" as settled until #1548 resolves; a body-discriminant check (`error.type`) is the operator-side hedge.
- **Chapter 02 (§"Break error rates down by provider and operation", `guide/02-observability.md:214`)**: Add the **alerting hazard** this page introduces (Claim 3): an **unmapped** provider error degrades to `litellm.APIConnectionError`, so a paging rule keyed on connection errors (or on `status_code == 500`) will mis-attribute novel provider failures to transport. Recommendation: monitor the *rate of `APIConnectionError` with `llm_provider` set to a real provider* as its own signal (a spike there can mean missing exception mappings, not a network outage), and use `llm_provider` as the provider-breakdown dimension this section already prescribes.
- **Chapter 02 (Alerting on LLM quality/guardrail signals)**: Add the Azure content-filter forensics path (Claim 8) as the documented way to classify *why* a request was blocked — `provider_specific_fields["innererror"]["content_filter_result"]` with per-category `filtered`/`severity` — noting it is Azure-specific and has no documented generic equivalent across providers.

## Extraction Notes

- Source read in full via WebFetch (rendered markdown) for orientation, then **re-fetched from the page's own raw markdown endpoint** (`https://docs.litellm.ai/docs/exception_mapping.md`, HTTP 200) for byte-exact quoting; every `Quote` field and the Concrete Artifacts tables/snippets are transcribed from that `.md` endpoint. The rendered HTML renderer collapses the tables' column padding, so the `.md` endpoint is the source of record for the table text.
- **No sub-pages were followed**, though MINER §1 allows up to 5 and the page's most substantive outbound link is the proxy-side [Error Reference](/docs/proxy/error_reference) ("the JSON error payload, the response headers, and how to tell a gateway error from a provider error"). It was **not** followed because (a) the triage asked specifically for *this page's* exception taxonomy, and the Error Reference is a distinct surface (proxy JSON envelope / headers) that the triage did not request, and (b) it is a natural separate Miner target. That page is a real coverage gap this note leaves open; the JSON-envelope half of the error contract is not captured here.
- The page is a living vendor doc: front matter `last_updated: "2026-10-12"` (one day before `date_extracted`). `date_published` is unknown; `date_extracted` and `last_checked` are both `2026-10-13`.
- **Contradiction decision (no new issue filed, per MINER §4a)**: The material conflict this page participates in — status-only 429 handling vs. the A2A `budget_exceeded` 429 — is **already covered by open contradiction #1548**, so re-filing would violate §4a's "check open `contradiction`-labeled issues before filing." It is cross-referenced under `**Contradicts:**` and no verdict is picked. The one *internal* page inconsistency found (`ContextWindowExceededError`'s parent, Claim 11) is a parent-chain documentation discrepancy that does not yield divergent guide advice, so it is recorded as a claim + an open question for maintainers, not filed.
- **Cross-reference verification (MINER §4b)**: `miner-related-notes.md` was read before writing Cross-References; all ten candidate paths are cited or dismissed above. Every cited `Claim N` was re-read in its source note and confirmed to say what it is cited for; `failure-litellm-model-cost-map-silent-fallback.md` is cited by **section name** (its headings are not `### Claim N`), per §4b rule 4. No claim number was invented, and no quote from another note was reconstructed.
- `confidence_overall` is **`emerging`**, matching the sibling LiteLLM docs notes: this is a first-party *capability contract* (concrete status→class table, a named attribute set, a named helper) but with no measured behavior, no version pin, no failure writeup, and one internal parent-chain inconsistency (Claim 11). Individual mapping statements (Claims 1–5, 8) are `settled` as statements about documented product behavior; the fail-open hazard (Claim 3) and the 429 conflict (Claim 7) are graded for their operational consequence, cross-checked against existing corpus and open contradiction #1548 rather than asserted as resolved.
