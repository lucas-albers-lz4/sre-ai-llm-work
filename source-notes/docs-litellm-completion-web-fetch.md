---
source_url: https://docs.litellm.ai/docs/completion/web_fetch
source_type: docs
title: "Web Fetch — LiteLLM Documentation (Anthropic web_fetch_20250910 via the gateway)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; page is not in the published `docs/docs/` tree at fetch time — very new)
date_extracted: 2026-10-06
last_checked: 2026-10-06
status: current
confidence_overall: emerging
issue: "#1608"
---

# Web Fetch (LiteLLM Docs)

> LiteLLM proxies Anthropic's **provider-native server tool** `web_fetch_20250910`
> through its `/chat/completions` path — Anthropic-only (`anthropic/`), with five
> optional per-request parameters (`max_uses`, `allowed_domains`, `blocked_domains`,
> `citations.enabled`, `max_content_tokens`). The page is a request-construction
> reference: it documents the tool spec and copy-paste wiring, and it is
> operationally thin — no rate limits, timeouts, error/retry semantics, response
> or citation schema, pricing, or any gateway-level routing/spend/fallback
> guidance. The two extractable ops-relevant findings are (1) the JS-rendering
> caveat, a silent partial-content failure mode, and (2) documented per-request
> caps whose enforcement location the page never states.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, a focused
  topic page under "Guides > Tool Calling", located between "Web Search
  Interception" and "Computer Use"). `web_search` (#1609) and `vision` (#1607)
  are separately-filed sibling pages.
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *surface* the gateway exposes (the tool `type`/`name`,
  the documented parameters and their per-field meaning, the supported-provider
  and supported-model lists, the SDK/proxy call shapes). It is **capability
  documentation only**: no measured latency, no cost figures, no failure writeup,
  no production experience. Per the Prospector's bounding rule, every claim below
  stays at "the gateway documents this," never "this holds in production."
- **Scope**: Covers Web Fetch vs Web Search, provider and model support, SDK and
  proxy quick starts, four usage examples, a multi-tool example, and the tool
  spec. Does **not** cover the response object schema, citation payload shape,
  rate limits, timeouts, error/retry behavior, cost, caching, or any gateway
  policy (routing, spend, fallback) on this path — the page's only output
  handling is `print(response)`.
- **Sub-pages**: none linked from the page. The page was verified (search + the
  published `docs/docs/` source tree on `BerriAI/litellm`) to have no separate
  referenced pages to follow.

## Extracted Claims

### Claim 1: The web fetch tool is a provider-native Anthropic server tool exposed through LiteLLM's completion path — Anthropic-only, `web_fetch_20250910`, appended to the `tools` array the same way over the SDK and the proxy
- **Evidence**: The "Supported Providers:" block lists exactly "Anthropic API
  (`anthropic/`)"; the "Supported Tool Types:" block lists exactly
  `web_fetch_20250910`. Both the SDK quick start and the proxy quick start pass
  an identical tool object (`{"type": "web_fetch_20250910", "name": "web_fetch",
  "max_uses": 5}`) in `tools=`, and both call through the chat-completions shape
  (`completion(...)` / `client.chat.completions.create(...)`).
- **Confidence**: settled (explicitly stated on the page)
- **Quote**: "Anthropic API (anthropic/)"
- **Our assessment**: This is *not* "LiteLLM supports web fetch across
  providers" — the single-provider surface is explicit and must stay explicit in
  the guide. The identical wire shape in both examples is the only evidence the
  page gives that the tool dict is forwarded rather than rewritten; it shows the
  object entering the proxy, not what the proxy emits upstream. The proxying
  surface is the same shape the corpus already records for other Anthropic
  server tools (`docs-litellm-anthropic-advisor-tool.md`).

### Claim 2: The full parameter surface of `web_fetch_20250910` is five optional fields — `max_uses`, `allowed_domains`, `blocked_domains`, `citations.enabled`, `max_content_tokens` — with the documented default example capping content at 100000 tokens
- **Evidence**: The "Spec" section's code block (see Concrete Artifacts). Every
  parameter is commented "Optional". `max_content_tokens` is shown with the value
  `100000`.
- **Confidence**: settled (verbatim spec block)
- **Quote**: "The web fetch tool supports the following parameters:"
- **Our assessment**: Nothing on the page states which fields are mandatory vs
  optional beyond the "Optional" comments on each of the five; `type`/`name` are
  the only un-commented fields and read as required (they are the tool identity).
  The spec gives a shape, not semantics-tables: no behavior for overlapping
  `allowed_domains`/`blocked_domains`, no cap granularity of `max_uses` beyond
  "per request", no unit for `max_content_tokens` beyond tokens.

### Claim 3: `allowed_domains` / `blocked_domains` are the only domain-scoping (egress-allowlisting) controls the page documents, and they are **request-scoped, client-supplied** values inside the `tools` array — not a gateway config
- **Evidence**: The spec comments "Only fetch from these domains" and "Never
  fetch from these domains"; the two fields only ever appear inside the
  per-request `tools` object. There is no example of configuring them in
  `config.yaml`'s `litellm_params` (the proxy wiring block carries only
  `model`/`api_key`).
- **Confidence**: settled for the surface (fields exist and are request-scoped
  in every example); "the only egress control" is a negative claim about this
  page.
- **Quote**: "// Optional: Only fetch from these domains"
- **Our assessment**: Because the fields travel with the caller's request, they
  are a *caller-controlled* boundary, not an operator policy. A fetched page that
  the caller allowed into context is still untrusted content. This is the
  request-path counterpart of — not a replacement for — an author-side,
  machine-checkable frontmatter allowlist like Ch06's Langfuse skill example.

### Claim 4: `max_uses` (limit of fetches per request) and `max_content_tokens` (maximum content length) cap per-request token burn and fetch count, and the page documents these as **per-request** controls; whether they are *provider-enforced upstream of the gateway* is our inference, not something the page states
- **Evidence**: The spec comments "Limit the number of fetches per request" and
  "Maximum content length in tokens"; the tool description calls the feature
  "web content retrieval tool with usage limits, domain filtering, and citation
  support". The tool is Anthropic-server-side (`anthropic/` only), which is the
  basis for the upstream-enforcement inference.
- **Confidence**: emerging (the per-request scoping is documented; enforcement
  location is inferred)
- **Quote**: "// Optional: Limit the number of fetches per request"
- **Our assessment**: The Prospector's question was whether the docs support
  "enforced upstream of the gateway; does not depend on LiteLLM's own
  accounting" — they do **not** state it. The page names no error type, no 429
  behavior, and no gateway-side accounting role for these caps. Record the
  per-request reading as documented and the "independent of gateway accounting"
  reading as inference only. The contrast with the session-scoped caps in
  `docs-litellm-a2a-iteration-budgets.md` holds at the *scope* level (per-request
  vs per-session), which is documented on both pages; the enforcement-location
  asymmetry is not.

### Claim 5: The web fetch tool "currently does not support websites dynamically rendered via JavaScript" — a silent partial-content failure mode for any runbook that fetches SPA pages
- **Evidence**: The note block immediately under the "Supported Models" list.
- **Confidence**: settled (vendor caveat, verbatim)
- **Quote**: "The web fetch tool currently does not support websites dynamically rendered via JavaScript."
- **Our assessment**: Failure-class: the page says the tool "does not support"
  JS-rendered pages, and documents no error or fallback for them. A runbook
  fetching a client-side-rendered page gets static-shell content (or worse,
  nothing) with no documented signal. For Ch05 this is a concrete reason to test
  web-fetch against the actual target DOM, not the URL.

### Claim 6: The page documents no rate limits, timeouts, error/retry semantics, response schema, citation payload shape, or pricing for the web fetch path — the absence of operational documentation is itself a finding, and the page offers no gateway-level rate-limit/spend/fallback controls for this path
- **Evidence**: Full read of the page. The proxy section's only output line is
  `print(response)`; the Spec section is the last substantive content; nothing
  anywhere mentions retries, timeouts, spend, routing, or fallback. `citations`
  appears only as the `{"enabled": true}` toggle.
- **Confidence**: settled (negative evidence from a complete read)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The Prospector's warning in the triage — the guide must
  not infer gateway-level rate/spend/fallback controls from this page — is
  confirmed. This is a request-path dependency whose failure modes (Anthropic
  side) are undocumented, matching Ch05's existing "undocumented failure modes
  are a finding" pattern. Record the blank as evidence, don't fill it from the
  Anthropic upstream docs.

### Claim 7: The page is internally inconsistent — the supported-model table lists `claude-opus-4-6` / `claude-sonnet-4-6` etc., but every code example on the page uses `anthropic/claude-sonnet-5`, which is not in that table
- **Evidence**: "Supported Models" lists `claude-opus-4-6`, `claude-sonnet-4-6`,
  `claude-opus-4-5`, `claude-sonnet-4-5`, `claude-haiku-4-5`,
  `claude-opus-4-1-20250805`, `claude-opus-4-20250514`,
  `claude-sonnet-4-20250514`, `claude-3-7-sonnet-20250219`,
  `claude-3-5-sonnet-latest` (deprecated), `claude-3-5-haiku-latest`; every code
  sample (SDK quick start, proxy quick start, and all four usage examples plus
  the multi-tool example) uses `model="anthropic/claude-sonnet-5"`.
- **Confidence**: settled (observable on the page)
- **Quote**: "Web fetch is available on the following Anthropic API models:"
- **Our assessment**: Recorded, not resolved — the Prospector instructed the
  Miner to record this rather than pick a winner. Either the table is stale
  (examples reflect current reality) or the examples use a model the tool is not
  listed as supporting. Both readings produce the same guide advice (verify
  model support against the current table before relying on the tool), so no
  contradiction issue was filed (§4a "when NOT to file": no opposing claims that
  would change guide advice).

### Claim 8: Web Fetch and Web Search are distinct capabilities — fetch retrieves full content from caller-supplied URLs, search discovers URLs from a query — so web fetch cannot discover or find content, only retrieve
- **Evidence**: The "Web Fetch vs Web Search" section's comparison table and the
  two example prompts: "Fetch the content from https://example.com/pricing and
  summarize it" (fetch) vs "What are the latest AI developments this week?"
  (search).
- **Confidence**: settled
- **Quote**: "Web Fetch retrieves the full content from specific web pages that you provide URLs for, while Web Search performs internet searches to find relevant information based on your queries."
- **Our assessment**: The two tools are complementary (retrieve-what-you-know vs
  discover-what-you-don't). A runbook that needs both must wire both tools; the
  current page does not discuss combining `web_fetch` with `web_search` (its
  multi-tool example uses a text editor instead). Guide text should not present
  web fetch as a search capability.

### Claim 9: Web fetch composes with other tools by simple array addition — the page's multi-tool example pairs `web_fetch_20250910` with a `text_editor_20250124` tool in the same `tools` array
- **Evidence**: "Advanced Usage with Multiple Tools" section; the `tools` array
  contains both tool objects and the message asks the model to fetch arXiv
  papers, analyze them, and write a report file.
- **Confidence**: settled
- **Quote**: "You can combine web fetch with other tools like computer use or text editor:"
- **Our assessment**: Composition is presented as pure array concatenation with
  no interaction semantics documented — no ordering, no result-binding between
  fetch output and later tools, no token accounting for the fetched content that
  then re-enters context as tool output. This is the mechanical baseline the
  guide can rely on; the interplay cost is undocumented.

### Claim 10: The page ships no content-trust or prompt-injection discussion — fetched web content enters the model context as tool output with no documented sanitization, warn-on-fetch, or trust tier — leaving the web-fetch path as the indirect-prompt-injection surface the corpus documents elsewhere
- **Evidence**: Absence across the full page: no security, injection, sanitization,
  or trust section; the only domain-related controls are the two spec fields.
- **Confidence**: emerging (negative claim from this page; the risk class itself
  is corroborated externally)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: `docs-litellm-message-sanitization.md` documents LiteLLM's
  Anthropic tool-message sanitization pipeline and its injection of fabricated
  tool results; nothing on this page ties web fetch to that pipeline or to any
  warning/trust mechanism. Operators should treat fetched page content as the
  untrusted input the Ch06 boundary rules cover, and scope `allowed_domains` as
  a *defense-in-depth* input, not a guarantee.

## Concrete Artifacts

Tool spec (verbatim from the page's "Web Fetch Tool (`web_fetch_20250910`)"
section; the page renders this as a single line):

```
{  "type": "web_fetch_20250910",  "name": "web_fetch",  // Optional: Limit the number of fetches per request  "max_uses": 10,  // Optional: Only fetch from these domains  "allowed_domains": ["example.com", "docs.example.com"],  // Optional: Never fetch from these domains  "blocked_domains": ["private.example.com"],  // Optional: Enable citations for fetched content  "citations": {    "enabled": true  },  // Optional: Maximum content length in tokens  "max_content_tokens": 100000}
```

Proxy wiring — "Define web fetch models on config.yaml" (verbatim), plus the
"Run proxy server" line `litellm --config config.yaml`:

```yaml
model_list:
  - model_name: claude-sonnet-5 # Anthropic claude-sonnet-5
    litellm_params:
      model: anthropic/claude-sonnet-5
      api_key: os.environ/ANTHROPIC_API_KEY
```

Proxy test via the OpenAI SDK (verbatim from "Test it using the OpenAI Python SDK"):

```python
client = OpenAI(
    api_key="sk-<your-litellm-api-key>", # your litellm proxy api key
    base_url="http://0.0.0.0:4000")
response = client.chat.completions.create(
    model="claude-sonnet-5",
    messages=[
        {
            "role": "user",
            "content": "Please fetch and analyze the content from https://news.ycombinator.com and tell me about the top stories"
        }
    ],
    tools=[
        {
            "type": "web_fetch_20250910",
            "name": "web_fetch",
            "max_uses": 5,
        }
    ])
print(response)
```

Supported models (verbatim list): `claude-opus-4-6` (Claude Opus 4.6),
`claude-sonnet-4-6` (Claude Sonnet 4.6), `claude-opus-4-5` (Claude Opus 4.5),
`claude-sonnet-4-5` (Claude Sonnet 4.5), `claude-haiku-4-5` (Claude Haiku 4.5),
`claude-opus-4-1-20250805` (Claude Opus 4.1), `claude-opus-4-20250514`
(Claude Opus 4), `claude-sonnet-4-20250514` (Claude Sonnet 4),
`claude-3-7-sonnet-20250219` (Claude Sonnet 3.7),
`claude-3-5-sonnet-latest` (Claude Sonnet 3.5 v2 - deprecated),
`claude-3-5-haiku-latest` (Claude Haiku 3.5).

Multi-tool example (second tool object, verbatim):
`"text_editor_20250124"` with `"name": "str_replace_editor"`, combined with
`web_fetch_20250910` / `"name": "web_fetch"` / `"max_uses": 5`.

## Cross-References

- **Corroborates**: `blog-promptfoo-indirect-prompt-injection-web-agents.md`
  Claim 1 (web-browsing agents are vulnerable to indirect prompt injection
  because fetched page content enters the agent's context) — Claim 10 above is
  the request-path instance of that risk on LiteLLM's web fetch tool; same
  note's Claim 11 (the "lethal trifecta" of private data access + untrusted
  content + external communication) bounds the scenario where an agent fetches
  an attacker-chosen page and has private data to lose.
- **Contradicts**: none. The model-table vs code-example mismatch (Claim 7) is
  a within-page inconsistency recorded but **not** filed as a contradiction:
  both readings yield the same guide advice (§4a "when NOT to file"). No
  existing source note opposes any claim here.
- **Extends**:
  - `docs-litellm-anthropic-advisor-tool.md` — the prior precedent for LiteLLM
    exposing an Anthropic server-side tool through the gateway (Claims 1, 15);
    its Claim 8 documents a *named* failure encoding for `max_uses`
    (`AdvisorMaxIterationsError`) on the advisor tool, which is exactly what
    Claim 4/6 flag as missing for `web_fetch_20250910` (no error semantics
    documented).
  - `docs-litellm-a2a-iteration-budgets.md` Claim 1 — the session-scoped
    `max_iterations` / `max_budget_per_session` controls that Claim 4 contrasts
    against at the scope level (per-session gateway-tracked vs per-request
    tool-level).
  - `docs-litellm-completion-function-call.md` — its Extraction Notes section
    explicitly lists `/docs/completion/web_fetch` as a separately-registered
    sibling page it deliberately did not follow; this note is that page
    arriving with its own depth.
  - `docs-litellm-messages-to-responses-mapping.md` Claim 7 — on the
    `/v1/messages`→Responses path tools are **type-remapped, not passed
    through**; `web_fetch_20250910` is only never mentioned there, so the shape
    on that path is unresolved — this note adds the chat-completions-path shape
    without contradicting that claim.
- **Novel**: The `web_fetch_20250910` tool surface itself (tool type, the
  documented five-parameter spec, `allowed_domains`/`blocked_domains`
  request-path egress controls, the JS-rendering caveat, and the missing
  operational documentation — rate limits, error semantics, citation payload —
  as a recorded absence). Also the model-table vs code-example inconsistency
  (Claim 7).

## Guide Impact

- **Chapter 06 (security & trust)**: `guide/06-security-and-trust.md`'
  "Skills ship a tool allowlist at authoring time" recommends author-side,
  machine-checkable allowlists (`WebFetch(domain:langfuse.com)`). Add the
  gateway-tool counterpart as a distinct, weaker layer: on LiteLLM's web fetch
  path, `allowed_domains`/`blocked_domains` are **request-scoped, caller
  supplied** — an input to scoping, not an operator boundary. The rule text
  should say domain-scoping on a passthrough web tool constrains *where* the
  tool fetches, not *that it is trusted*, and that fetched content from even
  allowed domains is untrusted (Claim 3, Claim 10). Cite this source.
- **Chapter 05 (LLM ops reliability)**: in the "Agent-loop cost caps fail open
  and expire" section, add the contrast that provider-native per-request caps
  (`max_uses`, `max_content_tokens`) are documented only at per-request scope
  and their enforcement location is undocumented (Claim 4), and the missing
  failure-mode documentation (rate limits, timeouts, error semantics, citation
  schema) is itself a finding for any runbook depending on web fetch (Claim 6).
  Add the JS-rendering caveat as a concrete silent-partial-content failure
  class (Claim 5) — verify against the actual target DOM rather than the URL.
  Do **not** infer gateway-level rate/spend/fallback controls from this page.
- **Chapter 03 (runbooks and agents)**: any runbook modeling an agent
  iteration budget around web fetch should treat `max_uses` as per-request
  (resets semantics unknown from this source) and fetch-vs-search as distinct
  capabilities (Claim 8); a research agent needs both tools, and fetched content
  re-entering context carries no documented token accounting (Claim 9).

## Extraction Notes

- Full read of the page per MINER §1, including the comparison table,
  supported-provider/tool-type blocks, both quick starts, all four usage
  examples, the multi-tool example, and the spec. No linked sub-pages exist on
  the page; I additionally searched the published `docs/docs/` source tree on
  `BerriAI/litellm` for a `web_fetch` page to check the spec block
  character-for-character and found none (the page post-dates the published
  tree), so the spec artifact above is quoted from the live rendered page and
  is confirmed to be a single line there.
- `miner-related-notes.md` candidates (10) were each cited or dismissed:
  cited — `docs-litellm-a2a-iteration-budgets.md` (Extends, Claim 4), `docs-litellm-anthropic-advisor-tool.md` (Extends, Claims 1/8/15). Dismissed as
  out-of-scope for this page: `docs-litellm-batches-api.md` (batch input-file
  rate limiting; different endpoint and accounting contract),
  `docs-litellm-completion-input-params.md` (OpenAI completion supported-params
  gate; governs `completion()` parameters, not server-tool fields),
  `docs-litellm-bedrock-invoke.md` (Bedrock native Invoke passthrough auth),
  `docs-litellm-audio-transcription.md` (non-chat endpoint support matrix),
  `docs-litellm-mock-requests.md` (mock responses), `docs-google-sre-eliminating-toil.md`
  (toil taxonomy, no agent interplay), `blog-litellm-auto-router-v2.md` (routing
  strategies), `docs-litellm-a2a-agent-card.md` (A2A agent-card field matrix).
- Per MINER §4b, every cross-referenced claim number was re-read in the cited
  note before writing; no quote from another note is reproduced here, so no
  cross-note quote risk.
- No contradiction issue filed. Claim 7's mismatch is internal to the page and,
  per the Prospector's explicit instruction, is recorded rather than resolved;
  per §4a the two readings do not produce different guide advice. Claim 4's
  enclosure (upstream enforcement) is an inference clearly labelled as such, in
  direct answer to the Prospector's "docs support that reading or is it our
  inference."
- Following the Prospector's bounding rule, I did not fetch the upstream
  Anthropic docs to fill in the response schema, rate limits, or error
  behavior; the missing-evidence finding (Claim 6) is intentional.