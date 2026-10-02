---
source_url: https://docs.litellm.ai/docs/completion/message_trimming
source_type: docs
title: "Trimming Input Messages — LiteLLM Documentation (with sibling page Prompt Compression / compress())"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; page frontmatter last_updated 2026-10-01)
date_extracted: 2026-10-02
last_checked: 2026-10-02
status: current
confidence_overall: emerging
issue: "#1510"
---

# Trimming Input Messages (LiteLLM Docs)

> LiteLLM's *Prompts & Context* section documents two client-side, in-process
> helpers that shrink a request's message array before `completion()` is
> called — `trim_messages()` and `compress()`. This note's primary finding is
> a **documented-gap asymmetry**: `compress()` ships an explicit four-bullet
> preservation contract (system message, last user turn, and last assistant
> turn always kept; content never lost but retrievable) plus token accounting
> in its return value, while `trim_messages()` — the helper whose entire job
> is to *drop* input — documents **none** of that: no drop order, no
> system-prompt protection, no `tool_use`/`tool_result` pairing rule, no
> single-oversized-message behavior, no return accounting, and no observable
> surface. `trim_messages()` is real, callable, and defaults to trimming to
> "about 75%" of a limit whose base the page never states. Per the
> Prospector's guidance, the unstated behavior is recorded as open questions,
> not asserted as defects.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway). The
  primary page is a sub-page of "Guides > Prompts & Context"; the sibling page
  is the same section, immediately adjacent (they are each other's
  `related:` front-matter entry and each other's "Previous"/"Next" nav link).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *surface* (function names, parameter names, defaults,
  and — for `compress()` — the one published benchmark). Not authoritative for
  *behavior*: the trimming page documents capability only, with no measured
  enforcement, no failure writeup, no production experience report, and no
  statement of the trim algorithm.
- **Scope — primary page** (`/docs/completion/message_trimming`): the
  `trim_messages()` helper, two usage snippets, and a four-parameter list.
  Front-matter `last_updated: 2026-10-01`; front-matter `related:` lists only
  `/docs/completion/prompt_compression` and `/docs/completion/prompt_caching`.
  Does **not** cover drop semantics, error modes, mutation semantics, or the
  relationship to gateway-side mechanisms.
- **Scope — followed sub-page** (`/docs/completion/prompt_compression`,
  read per MINER.md §1 "follow up to 5 linked pages that seem substantive";
  it is linked from the primary page's front-matter `related:`, its
  "Related pages" footer, and the section nav). Covers `litellm.compress()`:
  beta banner, quickstart, return-dict contract, eight parameters, a
  "Behavior Notes" preservation contract, retrieval-tool handling, a
  server-side callback mode for `/v1/messages`, and one SWE-bench Lite
  benchmark with methodology. Also does **not** cover `tool_use` /
  `tool_result` pairing or `cache_control` interaction.
- **Not read** (out of MINER.md §1 budget of 5 followed pages, and not needed
  for any claim here): `/docs/completion/prompt_caching`,
  `/docs/completion/prefix`, `/docs/completion/predict_outputs`,
  `/docs/completion/prompt_formatting`. Two of these (`prefix`,
  `prompt_caching`) are recorded as **open questions** rather than answers —
  see Extraction Notes.

## Extracted Claims

### Claim 1: `trim_messages()` is a client-side, in-process, pre-call helper whose entire documented contract is a single inequality — the page states no return type, no error mode, and no guarantee beyond it
- **Evidence**: The page's one-line summary plus two usage snippets. Both
  snippets pass the helper's return value straight back into `completion()`'s
  `messages` argument, so the helper's output substitutes for the caller's own
  message list — but the page has no "Returns" section and never states a
  return type or value.
- **Confidence**: settled (for the documented contract); the *behavior* is
  anecdotal-by-absence and is not extractable from this source.
- **Quote**: "Use litellm.trim_messages() to ensure messages does not exceed a model's token limit or specified `max_tokens`"
- **Our assessment**: The single useful thing an operator can take from this
  page is the *shape* of the guarantee: this is a pre-call, caller-side
  transform, not a gateway feature and not a provider feature. That layer
  distinction matters and is real — it means (a) nothing server-side observes
  that the trim happened, and (b) the caller owns whatever the trimmed array
  broke. Both consequences follow from the placement of the call, not from any
  documented statement about the helper, so they are safe; everything about
  *which* messages survive is not. Note the prose says `litellm.trim_messages()`
  while both snippets import `from litellm.utils import trim_messages` — the
  documented import path is `litellm.utils`, and the top-level `litellm.`
  form shown in the prose is never demonstrated.

### Claim 2: `model` is documented as optional *only* because `max_tokens` can substitute for it — yet both documented examples pass `model`, so the substitute path has no example and the page does not state what happens when neither is supplied
- **Evidence**: The parameter bullet for `model`, read against the two usage
  snippets. Snippet 1 calls `trim_messages(messages, model)`; snippet 2 calls
  `trim_messages(messages, model, max_tokens=10)`. Both pass `model`.
- **Confidence**: settled (the bullets are explicit; the absence of a
  neither-supplied behavior statement is verified against the complete page
  source — the page is 12 lines of prose plus two code blocks).
- **Quote**: "`model`:[Optional] This is the LiteLLM model being used. This parameter is optional, as you can alternatively specify the `max_tokens` parameter."
- **Our assessment**: This is the sharpest contract gap on the page. The page
  promises an either/or and then demonstrates only one arm of it, twice. An
  operator reading the parameter list could reasonably write
  `trim_messages(messages)` or `trim_messages(messages, max_tokens=N)` and
  get an `IndexError`/`TypeError` from a positional-argument mismatch or a
  `None`-window lookup — but the page documents neither the signature nor a
  failure mode, so we cannot and do not assert which. Recorded as an open
  question (OQ-1, below).

### Claim 3: `trim_ratio` defaults to `0.75`, and the sentence explaining it is truncated mid-thought and never states what the 75% is a fraction of
- **Evidence**: The `trim_ratio` bullet, verbatim, has no terminating period
  and ends at "about 75%". It introduces the ratio ("the target ratio of
  tokens to use following trimming") but names neither the denominator (the
  model's window vs the supplied `max_tokens`) nor the purpose of the
  remainder.
- **Confidence**: settled for the default and the truncation; the base of the
  ratio is **not** extractable from this source.
- **Quote**: "`trim_ratio`:[Optional] This represents the target ratio of tokens to use following trimming. It's default value is 0.75, which implies that messages will be trimmed to utilise about 75%"
- **Our assessment**: Two findings in one bullet. (1) The default is real and
  worth citing: the helper deliberately targets 75% of its budget rather than
  trimming to the edge, which implies a 25% headroom reserve — but the page
  never says that reserve is for the *completion*, so do not attribute intent.
  (2) The sentence is genuinely unfinished: there is no period, and the
  fraction-of-what is unstated, so "75% of the context window" and "75% of
  `max_tokens`" are both consistent with the text. The "It's default value"
  typo ("Its") is reproduced verbatim above and is cosmetic, but it does
  signal that this bullet has not had an editorial pass — which is the kind of
  page where an operator should treat the *unstated* parts as unknown rather
  than as defaults.

### Claim 4: The page documents no drop semantics at all — verified absences: which messages are dropped, from which end, whether the system prompt is protected, whether `tool_use`/`tool_result` pairing survives, what happens when one message alone exceeds the limit, whether the input list is mutated in place, and how much was removed
- **Evidence**: Complete absence, checked against the page's full raw source
  (`https://docs.litellm.ai/docs/completion/message_trimming.md` — front
  matter, one bolded summary line, `## Usage`, `## Usage - set max_tokens`,
  `## Parameters`, four bullets, `## Related pages`). There is no "Behavior"
  section, no "Notes" section, and no error section. Every unanswered question
  below is a verified absence, not an unfound section.
- **Confidence**: settled (that the documentation is silent). This claim is
  about the *documentation*, not about the implementation.
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The substantive ops content of this page. An
  undocumented lossy transform on the message array is a real operational
  hazard class in this corpus, and `trim_messages()` is the sharpest instance
  of it: the helper's only job is to remove input, and it documents none of
  the four properties an operator needs to trust it. Ranked by how much they
  would change a guide recommendation: (1) **which end** — a front-trim on a
  long tool loop silently deletes the task framing; (2) **system-prompt
  protection** — if unprotected, the system turn is the cheapest thing to drop
  and the request keeps a 200; (3) **`tool_use`/`tool_result` pairing** — the
  corpus's `docs-litellm-claude-code-context-management.md` **Claim 4**
  documents that LiteLLM's *other* context mechanism treats structural
  preservation as a headline guarantee, so the absence here is a real
  difference in assurance, not a stylistic one; (4) **oversized single
  message** — if one message exceeds the whole budget, no amount of dropping
  solves it and the helper's only two outcomes are fail or truncate that
  message. None of the four can be resolved from this source. See OQ-2/OQ-3.

### Claim 5: `max_tokens` on `trim_messages()` is an *input-payload* cap — the page's own second example passes `max_tokens=10` to the trim helper and passes no `max_tokens` at all to `completion()`, so the parameter name collides with OpenAI's output-token `max_tokens` and the page never disambiguates them
- **Evidence**: Snippet 2 verbatim below. The helper receives
  `max_tokens=10`; the `completion()` call that consumes its output declares
  only `model` and `messages`. The parameter bullet defines the helper's
  `max_tokens` as a bound on the *messages*, and snippet 2's inline comment
  restates it as a bound on `messages`.
- **Confidence**: settled (explicit code + explicit bullet + explicit inline
  comment, all on one page).
- **Quote**: "`max_tokens`:[Optional] This is an int, manually set upper limit on messages"
- **Our assessment**: The single most actionable naming hazard on the page, and
  the one an operator is most likely to hit: every LiteLLM/OpenAI reader has
  `max_tokens` loaded as *max output tokens*, and on this page it silently
  means *max input tokens* instead. Read the two snippets together with that
  prior and the natural misreading is *I set a 10-token completion budget* —
  when the actual effect is *I capped the entire conversation at 10 tokens.*
  Note also that the example value `10` is not a realistic conversation size
  for any current model, so it cannot have been used to exercise the helper
  against a real payload; treat it as an API-shape illustration, not a working
  configuration. Two correct usages follow and neither is stated: (a) budget
  the input yourself and pass it as the helper's `max_tokens` while setting the
  completion's own output budget separately, or (b) omit it and let `model`
  supply the window. The guide should name the collision explicitly.
### Claim 6: The two pages in this section are documented to very different completeness standards for the same job — `compress()` carries a Beta status banner and a "Behavior Notes" contract; `trim_messages()` carries no status marker at all and links to only two related pages
- **Evidence**: The sibling page's front-matter `summary` is the beta warning
  and its body opens with a `Beta` admonition. The trimming page's
  front-matter `summary` is the one-line function description, and its
  `related:` list has two entries (`prompt_compression`, `prompt_caching`)
  against the sibling's two entries (`predict_outputs`, `message_trimming`).
  The section hub `/docs/guides/prompts_context` likewise reproduces the beta
  warning for `compress()` next to a bare description for `trim_messages()`.
- **Confidence**: settled (both front matters and both rendered pages read
  directly).
- **Quote** (from `/docs/completion/prompt_compression`): "This feature is in beta. APIs and behavior may change before general availability."
- **Our assessment**: Read as an adoption signal rather than a defect: the
  absence of a beta marker on `trim_messages()` reads as "stable," which is
  exactly the wrong inference for a helper whose algorithm is undocumented.
  An operator applying the corpus's usual vendor-doc rule ("beta means treat
  the contract as provisional") would correctly deprioritize `compress()` and
  then over-trust `trim_messages()`. Practical guidance that follows from the
  two pages taken together: prefer `compress()` for the compression job
  precisely because its guarantees are written down, and treat
  `trim_messages()` as usable only where the caller can independently verify
  the trimmed array (e.g. a short, structurally uniform conversation with no
  tool use) — not in a tool-calling loop, where Claims 4's unanswered
  structural questions bite.

### Claim 7: `litellm.compress()` is a beta, relevance-based compressor with an explicit four-bullet contract — pass-through below the trigger, system + last user + last assistant turns always preserved, partial truncation allowed, and no content ever lost
- **Evidence**: The sibling page's "Behavior Notes" section, quoted verbatim
  below, plus its beta admonition and its description of the relevance model.
- **Confidence**: settled (explicit vendor contract, four separate guarantees).
- **Quote** (from `/docs/completion/prompt_compression`): "Messages below `compression_trigger` are passed through unchanged." / "System messages, the last user message, and the last assistant message are always preserved." / "If a relevant message does not fully fit the remaining budget, `compress()` may keep a truncated version of it." / "Compressed-out content is never lost; it is stored in `cache` and addressable by `litellm_content_retrieve`."
- **Our assessment**: This is the contract `trim_messages()` lacks, and it is
  worth stating as a pair: both helpers shrink the input array before the same
  `completion()` call, and both are documented in the same docs section, but
  only one of them states (a) what is protected, (b) that partial keeps are
  possible, and (c) that the removed content is recoverable. The
  losslessness guarantee is the substantive one — it converts compression
from *context you paid for and threw away* into *context the model can ask
back for*, which is the mechanism `blog-litellm-headroom-integration.md`
  **Claim 5** documents for Headroom's `retrieve_headroom` tool. Two limits
  the page does not lift: "always preserved" is stated for system and the
  last two turns but **not** for `tool_use`/`tool_result` pairing, so a
  relevance-scored compressor still has no documented pairing guarantee; and
  the page does not say whether `cache_control`-marked messages are exempt
  (OQ-4).

### Claim 8: `compress()` returns its own token accounting and a retrieval-tool definition — making the reduction measurable at the call site, which `trim_messages()` has no documented equivalent of
- **Evidence**: The "What It Returns" section enumerates six keys of the
  returned dict, of which three are counters and one is a tool definition.
- **Confidence**: settled (explicit return contract).
- **Quote** (from `/docs/completion/prompt_compression`): "`original_tokens`: token count before compression" / "`compressed_tokens`: token count after compression" / "`compression_ratio`: fraction of tokens removed" / "`tools`: retrieval tool definition (`litellm_content_retrieve`) for on-demand restoration"
- **Our assessment**: Across the four context-reduction surfaces this corpus
  now covers, only two expose an observable: this return dict, and Headroom's
  `x-litellm-applied-guardrails` header
  (`blog-litellm-headroom-integration.md` **Claim 6**). The gateway
  `context_management` polyfill has a third — the response
  `context_management.applied_edits` object
  (`docs-litellm-claude-code-context-management.md` **Claim 11**).
  `trim_messages()` has **no** documented observable: no return accounting, no
  header, no response field. So the cheapest-to-reach helper is also the only
  one of the four whose effect is invisible to both the caller and the
  gateway. That is the note's cross-cutting Ch05 finding, and it is why the
  three surfaces should not be presented to readers as interchangeable
  options.

### Claim 9: `compress()`'s defaults are anchored to a fixed `compression_trigger` of `200000`, not to the model's context window — and `trim_messages()`'s `trim_ratio` base is unstated — so neither helper documents a window-aware default budget
- **Evidence**: The `compression_trigger` and `compression_target` parameter
  bullets from the sibling page. `compression_target`'s default is expressed as
  a percentage *of the trigger*, not of the window and not of the model's
  context size.
- **Confidence**: settled for the documented defaults; the
  window-mismatch implication is this note's reading (flagged in Our
  assessment).
- **Quote** (from `/docs/completion/prompt_compression`): "`compression_trigger` (`int`, default `200000`): compress only if input token count exceeds this" / "`compression_target` (`Optional[int]`, default `70% of compression_trigger`): desired post-compression token budget"
- **Our assessment**: Both helper families size themselves against a
  hard-coded or caller-supplied number rather than against
  `model`'s context window. A default `compression_trigger` of 200,000 is
  inert on a 128k-window model and very late on a 1M-window model, and the
  page never says the default is window-aware — the operator must set it. This
  is the opposite failure mode from the gateway side: LiteLLM's polyfill at
  least enforces a documented floor and default in *input tokens*
  (`docs-litellm-claude-code-context-management.md` **Claim 8**: 50,000-token
  floor, 150,000 default) and the gateway's `context_window_fallback_dict`
  fires reactively on a provider context error
  (`docs-litellm-completion-input-params.md` **Claim 4**). Neither in-process
  helper has any error-triggered path at all — they are prophylactic only, so
  if a caller mis-sizes the budget, nothing downstream catches it.

### Claim 10: `compress()` has a documented server-side mode on `/v1/messages` that closes the retrieval loop agentically — a third deployment shape beyond the in-process call and the proxy guardrail
- **Evidence**: The sibling page's "Server-side Callback Loop" section: a
  `litellm_settings` YAML block plus a numbered five-step flow.
- **Confidence**: settled (explicit config and an enumerated flow).
- **Quote** (from `/docs/completion/prompt_compression`): "1. Compresses inbound messages before the first provider call." / "5. Reruns the model via agentic loop and returns the final answer."
- **Our assessment**: This is what makes `compress()` operationally
  interesting rather than merely documented: without the callback, a caller
  using `compress()` has to write the `tool_use` → cache lookup → tool-result
  → re-call loop themselves (the page's "Handling Retrieval Tool Calls"
  section shows exactly that hand-rolled code). The callback moves that loop
  into the gateway. So the deployment-shape taxonomy for context reduction is
  at least: in-process call (caller owns the loop), gateway callback (gateway
  owns the loop, caller configures YAML), or external proxy guardrail
  (Headroom, `blog-litellm-headroom-integration.md` **Claim 1**) — and the
  choice determines who sees the tool call and who owns the failure. The page
  states the happy path only: no behavior is documented for a retrieval key
  that misses the cache, for the extra round-trip's cost, or for whether the
  rerun is itself compressed.

### Claim 11: The only published benchmark for either helper is n=5 on SWE-bench Lite at `trigger=10k`, and it reports a real tool-loop quality tradeoff alongside 77.7% token and 72.0% cost reduction — directionally consistent with Headroom's marketed range but on a sample far too small to validate a general claim
- **Evidence**: The sibling page's "Performance" section: dataset link, the
  section header stating the configuration, the metrics table, and the
  vendor's own "Key takeaways". Metric definitions are given in a second
  table and reproducible commands are provided.
- **Confidence**: anecdotal for the numbers (n=5, one model, one trigger
  value, no variance or confidence interval); settled for the fact that the
  benchmark exists and for the metric definitions.
- **Quote** (from `/docs/completion/prompt_compression`): "Benchmarked on [SWE-bench Lite](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Lite_bm25_27K) (real GitHub issues with ~27k tokens of BM25-retrieved repo context per problem)." / "### Claude Opus: 5 problems, trigger=10k" / "Hunk overlap | 0.582 | 0.361 | -0.221" / "Avg prompt tokens | 30,828 | 6,890 | -77.7%" / "Avg cost/problem | $0.488 | $0.136 | **-72.0%**"
- **Our assessment**: Two things, and the second is the reason to keep the
  confidence at anecdotal despite the page looking rigorous. (1) The
  cost/token numbers are credible-shaped and land inside Headroom's marketed
  60–95% band — but note this is `compress()`'s BM25-stub-and-restore
  mechanism, not Headroom's, and it does not validate Headroom's claim, which
  `blog-litellm-headroom-integration.md` **Claim 4** records as having no
  disclosed methodology. The methodological bar differs sharply between two
  pages from the same vendor on adjacent topics. (2) The tradeoff the table
  quietly records is the one an ops reader needs: the *locator* metrics are
  unchanged (`File overlap` 1.000 → 1.000, `Exact file match` 100% → 100%,
  `Content similarity` 0.367 → 0.373) but the *span* metric drops — hunk
  overlap 0.582 → 0.361, i.e. -0.221 absolute and about -38% relative. The
  vendor characterizes that as "drops modestly"; the guide should say plainly
  that compression preserved *which* file the model edited but degraded *how
  much surrounding context* it edited it with, and that -38% relative is not a
  small number. Add n=5, one model, one trigger, and no baseline variance, and
  this is a directional data point, not a number to plan against.

## Concrete Artifacts

Verbatim from `https://docs.litellm.ai/docs/completion/message_trimming`
(fetched from the page's own raw markdown endpoint
`…/message_trimming.md`, which carries front matter the rendered page does
not). Note the trailing whitespace, the inline comments, and the absence of a
`max_tokens` argument on either `completion()` call — all as in the source.

```python
from litellm import completion
from litellm.utils import trim_messages

response = completion(
    model=model, 
    messages=trim_messages(messages, model) # trim_messages ensures tokens(messages) < max_tokens(model)
) 
```

```python
from litellm import completion
from litellm.utils import trim_messages

response = completion(
    model=model, 
    messages=trim_messages(messages, model, max_tokens=10), # trim_messages ensures tokens(messages) < max_tokens
) 
```

The complete `## Parameters` section, verbatim (the `trim_ratio` bullet's
unterminated sentence and the "It's" typo are the source's own):

```markdown
The function uses the following parameters:

- `messages`:[Required] This should be a list of input messages 

- `model`:[Optional] This is the LiteLLM model being used. This parameter is optional, as you can alternatively specify the `max_tokens` parameter.

- `max_tokens`:[Optional] This is an int, manually set upper limit on messages

- `trim_ratio`:[Optional] This represents the target ratio of tokens to use following trimming. It's default value is 0.75, which implies that messages will be trimmed to utilise about 75%
```

Full front matter of the primary page, verbatim — the `related:` list is the
route to the sub-page mined below:

```yaml
title: "Trimming Input Messages"
url: "/docs/completion/message_trimming"
canonical_url: "https://docs.litellm.ai/docs/completion/message_trimming"
type: "docs"
last_updated: "2026-10-01"
summary: "Use litellm.trim_messages() to ensure messages does not exceed a model's token limit or specified `max_tokens`"
related:
  - "/docs/completion/prompt_compression"
  - "/docs/completion/prompt_caching"
```

From the followed sub-page `https://docs.litellm.ai/docs/completion/prompt_compression`
— the `compress()` return contract and the "Behavior Notes" preservation
contract, verbatim:

```markdown
`compress()` returns a dictionary with:

- `messages`: compressed conversation messages
- `original_tokens`: token count before compression
- `compressed_tokens`: token count after compression
- `compression_ratio`: fraction of tokens removed
- `cache`: key-value mapping of stub key -> original full content
- `tools`: retrieval tool definition (`litellm_content_retrieve`) for on-demand restoration
```

```markdown
## Behavior Notes

- Messages below `compression_trigger` are passed through unchanged.
- System messages, the last user message, and the last assistant message are always preserved.
- If a relevant message does not fully fit the remaining budget, `compress()` may keep a truncated version of it.
- Compressed-out content is never lost; it is stored in `cache` and addressable by `litellm_content_retrieve`.
```

From the same sub-page — the server-side callback configuration, verbatim:

```yaml
litellm_settings:
  callbacks: ["compression_interception"]
  compression_interception_params:
    enabled: true
    compression_trigger: 10000
    compression_target: 7000
```

The five-step flow that config enables, verbatim as an ordered list:

```markdown
1. Compresses inbound messages before the first provider call.
2. Injects the `litellm_content_retrieve` tool.
3. Detects retrieval `tool_use` blocks in the model response.
4. Resolves retrieval keys from the compression cache.
5. Reruns the model via agentic loop and returns the final answer.
```

From the same sub-page — the full published benchmark table, verbatim, with
the vendor's "Key takeaways" bullets:

```markdown
### Claude Opus: 5 problems, trigger=10k

| Metric | Baseline | Compressed | Delta |
|---|---|---|---|
| File overlap | 1.000 | 1.000 | +0.000 |
| Exact file match | 100% | 100% | +0.0% |
| Hunk overlap | 0.582 | 0.361 | -0.221 |
| Content similarity | 0.367 | 0.373 | +0.006 |
| Avg prompt tokens | 30,828 | 6,890 | -77.7% |
| Avg cost/problem | $0.488 | $0.136 | **-72.0%** |

**Key takeaways:**

- **File-level targeting is fully preserved** — the model edits the same files with or without compression.
- **Content similarity matches baseline** — the actual lines changed are comparable.
- **Hunk overlap drops modestly** (-0.221). The model targets the right files but may edit slightly different line ranges with less surrounding context.
- **72% cost savings** with 78% token reduction.
```

And the hand-rolled retrieval loop the callback mode replaces, verbatim from
the same sub-page's "Handling Retrieval Tool Calls" section:

```python
import json

tool_call = response.choices[0].message.tool_calls[0]
args = json.loads(tool_call.function.arguments)
full_content = compressed["cache"][args["key"]]
```

## Cross-References

**Candidates from `miner-related-notes.md`** (every listed path cited or
dismissed; lexical retrieval returned generic LiteLLM parameter-surface
matches rather than context-management hits, which is why the most relevant
notes below were found by searching `source-notes/` directly):

- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch JSONL
  submission accounting and `batch_enqueued_token_limit`. Its `max_tokens`
  hit is an *output-token reservation per record*, a different meaning of the
  same parameter name (see this note's Claim 5); nothing about input-message
  trimming.
- `source-notes/docs-litellm-bedrock-invoke.md` — **dismissed**: Bedrock
  native Invoke passthrough routing and bearer-token auth swap. No
  context-budget content.
- `source-notes/docs-litellm-completion-input-params.md` — **cited**
  (Extends; primary reference note for the reactive alternative — see below).
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **cited** (Extends,
  and as a contrast on observability — see below).
- `source-notes/docs-litellm-audio-transcription.md` — **dismissed**:
  non-chat endpoint routing and fallback validation. Unrelated.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **dismissed**:
  within-request advisor composition and its token accounting. Shares only the
  word "messages"; no context-reduction content.
- `source-notes/docs-litellm-a2a-agent-card.md` — **dismissed**: served-card
  field matrix and skill routing. Unrelated.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **cited** (Extends — the
  declared-vs-measured cost distinction, see below).
- `source-notes/docs-litellm-completion-function-call.md` — **dismissed**:
  capability-predicate lookups and `tool_choice` discarding. Note the overlap
  in *theme* (silent parameter loss) is captured through
  `docs-litellm-messages-to-responses-mapping.md` **Claim 1** instead, which
  is the sharper instance.
- `source-notes/blog-litellm-auto-router-v2.md` — **dismissed**: routing
  strategies and debuggability. Unrelated.

**Additional cross-references found by searching `source-notes/`:**

- `source-notes/docs-litellm-claude-code-context-management.md` — **cited**
  (Corroborates, Extends — the primary contrast note).
- `source-notes/docs-litellm-token-usage-helpers.md` — **cited**
  (Corroborates, Extends).
- `source-notes/docs-litellm-anthropic-count-tokens.md` — **cited**
  (Corroborates, Extends).
- `source-notes/blog-litellm-headroom-integration.md` — **cited**
  (Corroborates, Extends).
- `source-notes/blog-litellm-save-claude-code-costs.md` — **cited**
  (Corroborates, Extends).
- `source-notes/docs-litellm-messages-to-responses-mapping.md` — **cited**
  (Corroborates).

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-token-usage-helpers.md` **Claim 2** —
    "`token_counter` counts tokens locally using the model's tokenizer,
    falling back to tiktoken when no model-specific tokenizer is available."
    This answers part of the Prospector's question about which counter a trim
    decision uses: the trimming page never says, but every token-counting
    primitive LiteLLM documents for in-process use resolves to that local
    counter. So a `trim_messages()` budget is enforced against a local
    estimate, and inherits the divergence that note's assessment calls out
    ("the estimate can diverge from provider-reported totals").
  - `source-notes/docs-litellm-anthropic-count-tokens.md` **Claim 7** —
    provider routing for token counting is not total and falls back to local
    tiktoken counting. Same consequence, reached from the endpoint side:
    whichever counting path a trim decision uses, an unknown-model or
    unsupported-provider configuration is counted locally, so the trim fires
    early or late relative to the model's own native count.
  - `source-notes/docs-litellm-claude-code-context-management.md` **Claim 12**
    — polyfill threshold checks count with `litellm.token_counter`, tiktoken
    `cl100k_base` fallback for unknown models. The corpus now has three
    independently-mined confirmations that LiteLLM's *context-control
    decisions* are made on a local count. Worth generalizing in Ch05: this is
    a gateway-wide property, not a per-feature quirk.
  - `source-notes/blog-litellm-headroom-integration.md` **Claim 5** — Headroom
    exposes a retrieval tool so the model can recover the full original
    context. Corroborated by this note's Claim 7: `compress()`'s
    `litellm_content_retrieve` tool is the same recoverability pattern in the
    same docs section, implemented as an in-process call rather than a proxy
    guardrail.
  - `source-notes/blog-litellm-save-claude-code-costs.md` **Claim 9** — "Prompt
    cache trims the static prefix; Headroom trims the dynamic middle." This
    note's Claim 8 sharpens that framing from two mechanisms to four, and
    identifies a fourth category neither prior note had: a **silent** client-
    side transform with no observable at all.
  - `source-notes/docs-litellm-messages-to-responses-mapping.md` **Claim 1** —
    parameters dropped "silently", caller gets a 200 with no error and no
    telemetry. The corpus's established "silent degradation" theme; this note
    supplies an instance where the loss is of *content* rather than of a
    *constraint*, which is strictly worse, and adds that the loss is not even
    reported in the return value.

- **Contradicts**:
  - **None. No contradiction issue filed**, per MINER.md §4a. Checked
    CONTRADICTIONS.md and the open issue list before deciding. The candidates
    examined and why each is a *conditioning variable* rather than a
    contradiction — MINER.md §4a explicitly excludes these:
    (a) `blog-litellm-headroom-integration.md` **Claim 8** (Headroom never
    compresses `cache_control`-marked messages) vs `compress()`, whose
    Behavior Notes list no such exemption — different mechanisms, and
    `compress()` makes no claim either way, so there is no opposition;
    (b) `blog-litellm-headroom-integration.md` **Claim 4** (60–95% reduction,
    no methodology) vs this note's Claim 11 (77.7% measured with disclosed
    methodology) — different mechanisms, and the measured figure falls *inside*
    the marketed band rather than opposing it;
    (c) `docs-litellm-completion-input-params.md` **Claim 4**
    (`context_window_fallback_dict` fires reactively) vs these helpers' purely
    prophylactic posture — reactive vs proactive is a timing difference, and
    the two compose rather than conflict;
    (d) this note's Claims 4 and 7 (`trim_messages()` documents no
    preservation contract, `compress()` documents one) are two pages of one
    vendor documenting two helpers — an *assurance gap between two
    mechanisms*, not two claims that cannot both be true. Recorded here and in
    the note as a documented gap and an open question.

- **Extends**:
  - `source-notes/docs-litellm-claude-code-context-management.md` (#1445) —
    the primary contrast note, and the one the triage named. Extends it on
    three axes. (1) **Layer**: that note's **Claim 1** establishes
    routing-dependent in-gateway polyfill semantics; this note adds the
    *client-side* layer beneath it, where the caller — not the gateway —
    decides what the provider ever sees, so no `applied_edits` telemetry can
    exist. (2) **Structural assurance**: that note's **Claim 4** documents
    `clear_tool_uses_20250919` preserving message-array structure with a hard
    floor on the most recent `tool_result`; this note shows LiteLLM's *other*
    context mechanism (`compress()`) documenting a preservation contract too,
    and its cheapest one documenting none — so the corpus now has a three-way
    comparison, not a single endorsed mechanism. (3) **Budget trigger**: that
    note's **Claim 8** documents a 50,000-token floor and 150,000 default in
    input tokens at the proxy; this note's Claim 9 shows neither in-process
    helper has a window-aware default. The two notes together answer the
    triage's framing question — for a *contract operators can rely on*,
    #1445's `context_management` is the documented surface; `trim_messages()`
    is not, and this note says so explicitly rather than by omission.
  - `source-notes/docs-litellm-completion-input-params.md` **Claim 4** —
    `context_window_fallback_dict` "fires only on a context-window error,
    where `fallbacks` fires on any call failure." This note adds the third and
    opposite posture in the corpus: two helpers that never see an error because
    they act *before* the request. The guide can now state the full choice —
    proactive in-process trim (no error path, no telemetry), proactive
    in-process compression (no error path, but measurable return value), or
    reactive gateway fallback (error-triggered, `fallbacks` semantics).
  - `source-notes/blog-litellm-save-claude-code-costs.md` **Claim 3** — the
    proxy auto-injects `cache_control` at "the system message (or the
    second-to-last user turn)" to make Claude's prompt cache work without
    client-side edits. This note raises the interaction the triage flagged:
    `trim_messages()` rewrites the caller's own array *before* the request, so
    it can change the byte sequence of exactly those marked positions, and
    `compress()` rewrites message content into stubs with no documented
    `cache_control` exemption. Per the triage's instruction this is recorded
    as **OQ-4**, not asserted — but it is now a specific, named question
    rather than a vague one, and it is the question most worth an independent
    test.
  - `source-notes/docs-litellm-a2a-cost-tracking.md` **Claim 3** — the flat
    per-query cost is "a gateway-declared synthetic charge" with "no documented
    linkage to the agent's measured token usage." This note supplies the
    opposite case on the same axis: `compress()`'s `original_tokens` /
    `compressed_tokens` / `compression_ratio` are measured by the same local
    counter, so the reduction is measurable *at the call site* but still
    locally estimated rather than reconciled against provider billing. Useful
    for Ch05's cost section: there are three positions on this axis —
    declared-synthetic, locally-measured, and provider-reconciled — and the
    corpus now has a note for each.
  - `source-notes/docs-litellm-a2a-iteration-budgets.md` — cited as a
    contrast rather than corroboration. That note's per-session caps are
    *enforcing* and *observable*: over-cap requests receive HTTP 429 with a
    `budget_exceeded` type. These two helpers are *budgeting* but not
    enforcing: `trim_messages()` degrades the payload and says nothing, and
    neither helper refuses a request. The triage's note about the 429
    status-class collision applies usefully here in reverse — the reliable
    pattern across this corpus is that a budget that cannot be *observed* is a
    budget nobody can alert on.
  - `source-notes/blog-litellm-headroom-integration.md` **Claim 4** — extends
    the evidence-quality asymmetry this note's Claim 11 exposes: two
    same-vendor compression pages on adjacent topics, one disclosing metric
    definitions, dataset, and reproduction commands at n=5, the other
    disclosing nothing across a 35-point range. A Ch02/Ch05 reader can
    therefore weight the two claims very differently even though both are
    "vendor-stated."

- **Novel**: First corpus coverage of LiteLLM's **`trim_messages()`** helper
  and, with the followed sub-page, of **`litellm.compress()`** — zero prior
  notes mention either function (`grep -rl` for `compress()`,
  `litellm.compress`, `prompt_compression`, `message_trimming`,
  `trim_messages` across `source-notes/` returns only
  `registry/site-crawl-state.json`, which is crawl bookkeeping, not a note).
  Specifically new to the corpus: the `trim_ratio: 0.75` default; the
  `max_tokens` input-vs-output naming collision on the trim helper; the
  verified absence of drop semantics, structural guarantees, return
  accounting, and observability on the trimming page; the `compress()`
  six-key return contract and its `litellm_content_retrieve` restore path; the
  `compression_trigger`/`compression_target` default pair and its
  window-independence; the `compression_interception` server-side callback
  loop on `/v1/messages`; and the SWE-bench Lite benchmark table, including
  the hunk-overlap degradation the corpus has not previously recorded.

## Guide Impact

Verified before writing: `grep -niE "trim|compress|context window|context_window"
guide/05-llm-ops-reliability.md` returns **zero** matches. Ch05 currently has
no context-budget or context-window-overflow control content at all, and
nothing in `guide/` recommends any of these four mechanisms. So this is
net-new chapter material rather than a correction, and the triage's Ch03
suggestion is not warranted — none of this source's content is agent-loop
process design, it is per-request payload sizing.

- **Chapter 05 (llm-ops-reliability) — add a "context-budget control
  surfaces" subsection** covering the four mechanisms the corpus now covers
  and the three axes that distinguish them: *where it runs* (in-process client
  vs gateway polyfill vs proxy guardrail), *what is observable* (none /
  return-dict counters / `applied_edits` / guardrail header), and *when it
  acts* (prophylactic vs reactive-on-error). The single sentence the
  subsection should lead with, sourced to Claims 1, 4, and 8: **the easiest
  helper to reach (`trim_messages()`, one import) is the only one of the four
  with no documented way to tell that it acted.**
- **Chapter 05 — add the `max_tokens` naming-collision warning** (Claim 5).
  Concretely: on `trim_messages()`, `max_tokens` bounds the *input messages*
  (*manually set upper limit on messages*), not the completion; the page's
  own example passes it only to the trim helper and leaves `completion()`
  without one. An operator carrying the OpenAI meaning of `max_tokens` will
  misread this by a factor of the entire conversation, and no LiteLLM page in
  the corpus disambiguates the two senses. This is the one finding in this
  note that changes what a reader should *write*, so it deserves a callout, not
  a footnote.
- **Chapter 05 — add the "budgets you cannot observe are budgets you cannot
  alert on" rule** (Claims 8 and 9), cross-referencing
  `docs-litellm-claude-code-context-management.md` **Claim 11**
  (`applied_edits`) and `blog-litellm-headroom-integration.md` **Claim 6**
  (`x-litellm-applied-guardrails`). Extend the existing 429 status-class
  lesson from `docs-litellm-a2a-iteration-budgets.md`: that note covers a cap
  that reports through a status code an operator must disambiguate; these
  cover caps that report through nothing at all.
- **Chapter 05 — qualify the compression-cost claim.** The corpus currently
  cites Headroom's 60–95% reduction as a directional signal only
  (`blog-litellm-headroom-integration.md` **Claim 4**). This note supplies the
  first same-vendor figure with disclosed methodology (Claim 11), and the
  guide should cite it *with* the n=5 caveat and *with* the hunk-overlap
  finding: token/cost reduction was 77.7% / 72.0%, and tool-span fidelity fell
  about 38% relative. Frame the tradeoff as "compression preserved which file
  the model edited and degraded how much context it edited it with" — the
  vendor's own "drops modestly" framing should not be the guide's framing.
- **Chapter 05 — prefer `compress()` over `trim_messages()` for the same job,
  and say why in terms of the documented contract, not the algorithm**
  (Claims 6, 7). The vendor gives no reason to believe `trim_messages()` is
  implemented worse; the claim is narrower and defensible: `compress()`
  documents what it protects and makes its reduction measurable, and
  `trim_messages()` documents neither. If the Smith wants a sharper line, the
  honest framing is that `trim_messages()` is undocumented *enough* that it
  should not be the recommended default in a tool-calling loop — the triage's
  own phrasing, and the reason Claims 2–5 are worth a note at all on a page
  this thin.
- **No `guide/` edit is proposed by this note.** Per repo rules this is Smith
  work; the impact above is advisory input only.

## Extraction Notes

- **Followed sub-page, disclosed.** The primary page is thin — a bolded
  summary line, two code blocks, and four parameter bullets (front matter
  `last_updated: 2026-10-01`). MINER.md §1 directs following substantive
  linked pages, and the primary page's own front-matter `related:` points at
  `/docs/completion/prompt_compression`, which is also its "Previous" nav
  link and is in the same docs section. Claims 7–11 and the second half of
  Concrete Artifacts are extracted from that sub-page and **every quote from
  it is attributed inline** to `https://docs.litellm.ai/docs/completion/prompt_compression`
  in its Evidence field. `source_url` in the front matter remains the primary
  page (the issue's source). Claims 1–6 are from the primary page only.
- **Verbatim sourcing method.** Both pages were read from their raw markdown
  endpoints (`…/message_trimming.md`, `…/prompt_compression.md`), which
  expose the Docusaurus front matter and preserve exact line breaks and
  punctuation. This was done deliberately: the *rendered* HTML fetch collapses
  newlines inside code blocks, which would have made any code-block quote
  inexact. All fenced blocks in Concrete Artifacts are byte-exact from those
  endpoints, including trailing whitespace, the "It's default value" typo,
  and the unterminated `trim_ratio` sentence.
- **Absences were verified, not inferred.** Claims 3, 4 and 6 rest on what the
  complete page does *not* contain. Both raw files were read end to end; the
  trimming page is 12 lines of prose plus two code blocks with no Behavior,
  Notes, Returns, or error section of any kind. Per the triage's explicit
  instruction, none of this is written as a defect claim about the
  implementation — only as a statement about the documentation.
- **No contradiction filed.** See the Contradicts block above for the four
  candidates examined and why each is a conditioning variable under MINER.md
  §4a rather than a contradiction. This was a deliberate outcome, not an
  oversight; the triage's assessment that "nothing here contradicts the
  current guide" held up.
- **Open questions this source cannot answer** (recorded rather than guessed,
  per the triage's guidance):
  - **OQ-1** — behavior of `trim_messages()` when *neither* `model` nor
    `max_tokens` is supplied (Claim 2).
  - **OQ-2** — drop order and system-prompt protection (Claim 4). Untestable
    from docs; needs a read of the implementation or a black-box experiment.
  - **OQ-3** — `tool_use` / `tool_result` pairing on a trim, and behavior when
    one message alone exceeds the limit (Claim 4).
  - **OQ-4** — the prompt-cache interaction the triage raised (Claims 7, 8):
    does `compress()` or `trim_messages()` respect `cache_control` markers, and
    do they invalidate the cached prefix that
    `blog-litellm-save-claude-code-costs.md` **Claim 3** makes the proxy inject
    at the system message or second-to-last user turn? `compress()`'s Behavior
    Notes list no `cache_control` exemption, which is suggestive but is not a
    statement. Unresolved here by design.
  - **OQ-5** — whether `compress()`'s stated preservation contract
    ("System messages, the last user message, and the last assistant message
    are always preserved") extends to `tool_use`/`tool_result` pairing. The
    page does not say, so the same hazard that OQ-3 raises for `trim_messages()`
    is not excluded for `compress()` — it is simply also undocumented there
    (Claim 7).
- **Pages deliberately not mined.** `/docs/completion/prompt_caching`,
  `/docs/completion/prefix`, `/docs/completion/predict_outputs`, and
  `/docs/completion/prompt_formatting` were read only as far as needed to
  confirm the section structure and are not extracted here — each is a
  separate source with its own `source_url` and belongs in its own note.
  `/docs/completion/prefix` was read in full during navigation and does
  document a `prefix: true` assistant-prefill flag (Deepseek, Mistral,
  Anthropic); noted here only so the next Miner knows it is unmapped, not
  because it bears on any claim in this note.
- **Confidence rationale for `emerging`.** The documented surfaces (function
  names, parameter names, defaults, the `compress()` return contract and
  Behavior Notes, the config YAML) are `settled` at the individual-claim level.
  The note is `emerging` overall because: no claim here has independent
  validation or an operational experience report attached; the one published
  benchmark is n=5 on a single model at a single trigger value (Claim 11); and
  the headline findings about `trim_messages()` are claims about *missing*
  documentation, which cannot be confirmed by a second reader without
  re-reading the same page. Consistent with how other single-page LiteLLM docs
  notes in the corpus are graded.
