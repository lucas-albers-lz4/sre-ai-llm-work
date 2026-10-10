---
source_url: https://www.promptfoo.dev/docs/guides/chatbase-redteam
source_type: docs
title: "Promptfoo Docs — Red Teaming a Chatbase Chatbot (Third-Party HTTP Target)"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-10
date_extracted: 2026-10-10
last_checked: 2026-10-10
status: current
confidence_overall: emerging
issue: "#1654"
---

# Promptfoo Docs — Red Teaming a Chatbase Chatbot (Third-Party HTTP Target)

> A vendor recipe for red-teaming a hosted third-party chatbot (Chatbase) that
> you do **not** own, over its generic HTTP API. Its transferable payload is the
> black-box HTTP-target red-team pattern: a two-layer parsing contract
> (`transformRequest` → OpenAI-style messages in, `transformResponse: 'json.text'`
> out) plus per-test session-identity plumbing (`conversationId` bound to
> `context.uuid` via `transformVars`) that makes stateful multi-turn attack
> strategies (`goat`, `crescendo`, `mischievous-user`) work against an opaque
> endpoint.

## Source Context

- **Type**: docs (vendor recipe guide — Promptfoo "Red Teaming a Chatbase
  Chatbot", auto-discovered from the registered `promptfoo-docs` site-crawl
  seed). Single guide page under Red teaming → Guides.
- **Author credibility**: Promptfoo, the LLM eval / red-team vendor (now part of
  OpenAI per the site banner). First-party documentation of the product's own
  `redteam` CLI and HTTP-target config surface — authoritative for the documented
  syntax and mechanism, but vendor-positioned: no metrics, no execution results,
  and no independent validation. Page footer shows "Last updated on **Oct 10,
  2026** by **mldangelo-oai**".
- **Scope**: Covers (1) single-turn vs multi-turn test framing and why
  multi-turn systems are the harder target; (2) prerequisites (Node.js
  `>=22.22.0`, promptfoo CLI, Chatbase API credentials); (3) the `http` provider
  target config that adapts Chatbase's non-OpenAI API — `transformRequest`,
  `transformResponse`, and the `conversationId` body field; (4) `defaultTest`
  `transformVars` binding `conversationId` to `context.uuid`; (5) the three
  stateful multi-turn strategies; (6) the `redteam generate` / `eval` / `view`
  workflow; (7) a generic two-branch troubleshooting note. Does NOT cover:
  defenses/guardrails, findings triage or report export, measured
  pass-rates/latency/cost, or any target beyond Chatbase's API shape (the
  `gpt-5-mini` model string is a placeholder in the vendor's example body).

## Extracted Claims

### Claim 1: Promptfoo manages multi-turn state through a `conversationId` that links messages, and the page frames multi-turn systems as introducing security challenges that single-turn systems do not have
- **Evidence**: The "Multi-turn vs Single-turn Testing" section states the state
  mechanism and then draws the security distinction: multi-turn context enables
  better UX but lets attackers manipulate conversation context across messages
  (building false premises or extracting sensitive information).
- **Confidence**: settled (documented mechanism + vendor framing)
- **Quote**: "In Promptfoo, this state is managed through a `conversationId` that links messages together. While this enables a better user experience, it introduces security challenges."
- **Our assessment**: This is the page's thesis and the reason a distinct target
  class is needed: against a single-turn system the attacker has no history to
  manipulate, so the interesting attack surface (building false premises across
  turns) simply does not exist. The fabricated-premise / slow-extraction threat
  is the same multi-turn manipulation risk the OWASP red-teaming note lists as a
  first-class agent risk category (see Cross-References). We buy the framing; the
  page does not, however, measure how much real risk the state adds.

### Claim 2: Single-turn systems are "inherently more secure" because attackers cannot manipulate conversation history — but that security is paid for in usability
- **Evidence**: The "Single-turn Systems" subsection makes the causal claim
  (no retained context ⇒ no history to manipulate) and immediately states the
  tradeoff (users must supply complete context with every message).
- **Confidence**: emerging (architectural argument, no evidence or measurements)
- **Quote**: "This makes single-turn systems inherently more secure since attackers can't manipulate conversation history. However, this security comes at the cost of usability - users must provide complete context with every message, making interactions cumbersome."
- **Our assessment**: Directionally correct as a threat-model statement — state is
  what enables cross-turn manipulation — and it pairs neatly with the "lethal
  trifecta" framing elsewhere in the corpus (private data + untrusted content +
  external comms). It is a design-tradeoff assertion, not a measured result; the
  guide should carry it as the *why* behind multi-turn red-teaming, not as a
  quantified security claim. The word "inherently" overstates it: a single-turn
  system can still leak via a single well-crafted prompt; what state removal
  eliminates is the *multi-turn* attack class specifically.

### Claim 3: A hosted third-party chatbot is red-teamed as a generic `http` target, and the state key must be threaded into the request body as `conversationId: '{{conversationId}}'`
- **Evidence**: The target config uses `id: 'http'` pointing at Chatbase's
  `/api/v1/chat`, with `conversationId` placed inside the `body` map alongside
  messages, chatbot ID, and generation params, so the target's own API receives
  the session id (Promptfoo is not the state owner — the endpoint is).
- **Confidence**: settled (documented config)
- **Quote**: (config block; see Concrete Artifacts → Chatbase target config) "'conversationId': '{{conversationId}}',"
- **Our assessment**: The important structural point: for a black-box target,
  state continuity is the *endpoint's* responsibility, so the harness must inject
  a stable per-conversation identifier into every turn. This is architecturally
  different from a model you host, where the provider adapter holds the message
  history. The guide's red-team material should state that red-teaming a
  third-party chatbot requires knowing the target's own state key (here
  `conversationId`), because the harness cannot supply history out of band.

### Claim 4: Per-test conversation identity is manufactured with `transformVars: '{ ...vars, conversationId: context.uuid }'` under `defaultTest.options`, generating a unique conversation id for each test
- **Evidence**: The `defaultTest.options.transformVars` line in the config, and
  the configuration note that spells out the consequence: "The `context.uuid`
  generates a unique conversation ID for each test, enabling Chatbase to track
  conversation state across multiple messages."
- **Confidence**: settled (documented behavior + explicit explanation)
- **Quote**: "The `context.uuid` generates a unique conversation ID for each test, enabling Chatbase to track conversation state across multiple messages."
- **Our assessment**: This is the page's most reusable nugget and the one the
  Prospector flagged: it is a concrete application of the input-side
  `transformVars` transform (which merges returned keys into `vars` and can
  override existing keys — see `docs-promptfoo-configuration-guide.md` Claim 4).
  By spreading the existing `vars` and adding `conversationId: context.uuid`, the
  recipe gives every test a fresh, isolated conversation thread at the target.
  The failure mode this avoids is cross-test state bleed: without a unique id, a
  stateful external endpoint would carry one test's history into the next.
  Note the `context.uuid` value is per-test, so each red-team *test* is one
  conversation — multi-turn strategies then run their turns within that single
  conversation.

### Claim 5: A non-OpenAI HTTP target needs a two-layer parsing contract — `transformRequest` formats the outbound request as OpenAI-compatible messages, and `transformResponse` extracts the response text from the JSON body
- **Evidence**: The configuration note is explicit: `transformRequest` "Formats
  the request as OpenAI-compatible messages" and `transformResponse` "Extracts
  the response text from the JSON body." The config's concrete values are
  `transformRequest: '[{ role: "user", content: prompt }]'` and
  `transformResponse: 'json.text'`.
- **Confidence**: settled (documented config + explanation)
- **Quote**: "Configure both the `transformRequest` and `transformResponse` for your chatbot:" followed by "`transformRequest`: Formats the request as OpenAI-compatible messages" and "`transformResponse`: Extracts the response text from the JSON body"
- **Our assessment**: This is the adapter contract that lets Promptfoo's
  OpenAI-shaped machinery (prompts, strategies, graders) drive a foreign API. The
  split matters operationally: the *request* side must translate Promptfoo's chat
  messages into the target's wire shape, and the *response* side must pull a
  single string out of the target's JSON envelope (`json.text` here) before any
  assertion or grader sees it. This is the same class of provider-stage transform
  the corpus already documents — `transformResponse` is the provider-stage output
  transform in the three-stage pipeline (`docs-promptfoo-configuration-guide.md`
  Claim 1), and the sibling HTTP-provider escape hatch `transformToolsFormat`
  handles the analogous tool-shape translation
  (`docs-promptfoo-configuration-tools.md` Claim 9). What is new here is applying
  it to *red-team* a third-party endpoint rather than to evaluate a
  self-configured app.

### Claim 6: The stateful multi-turn attack strategies are declared as `goat`, `crescendo`, and `mischievous-user`, each with `stateful: true`
- **Evidence**: The "Strategy Configuration" section lists exactly three
  strategies, each carrying a `config.stateful: true` flag.
- **Confidence**: settled (documented config)
- **Quote**: (config block; see Concrete Artifacts → Stateful strategy config) "- id: 'goat'" / "- id: 'crescendo'" / "- id: 'mischievous-user'"
- **Our assessment**: This is the concrete strategy set for multi-turn red-teaming
  of a stateful target, and it is mostly net-new to the corpus: `crescendo`
  (gradual escalation) is already named in the Promptfoo red-team blog notes
  (e.g. `blog-promptfoo-red-team-claude.md` Claim 7), but `goat` and
  `mischievous-user` are not documented in any existing note. The `stateful:
  true` flag is the operative detail — it signals the strategy may carry context
  across turns, which is only meaningful when the target itself maintains
  conversation state (i.e. when `conversationId` is threaded, Claim 3/4). A
  stateful strategy against a stateless adapter would have nothing to escalate
  across.

### Claim 7: The target body pins determinism for the run — `stream: false` and `temperature: 0`
- **Evidence**: The Chatbase target `body` map hardcodes `'stream': false` and
  `'temperature': 0` next to the message, chatbot, and model fields.
- **Confidence**: settled (documented config)
- **Quote**: (config block; see Concrete Artifacts → Chatbase target config) "'stream': false," and "'temperature': 0,"
- **Our assessment**: These are the reproducibility choices a red-team run wants:
  disabling streaming keeps the adapter's single-string `transformResponse:
  'json.text'` parse valid (a streamed response would not be a single JSON text
  field), and `temperature: 0` reduces per-run variance so a red-team verdict is
  more stable across reruns. The placement is notable — determinism is set on
  the *target request body*, not on a Promptfoo provider option, so it is a
  property of the foreign API call. This is the kind of concrete determinism
  detail the corpus's ASR/measurement discipline calls for when comparing runs.

### Claim 8: The documented third-party-integration failure taxonomy is two-way — connection failures point at credentials, garbled content points at the request/response parsers
- **Evidence**: "Common issues and solutions" gives exactly two branches mapped to
  the two failure surfaces introduced by the black-box adapter.
- **Confidence**: settled (documented troubleshooting guidance)
- **Quote**: "If tests fail to connect, verify your API credentials" and "If the message content is garbled, verify your request parser and response parser are correct."
- **Our assessment**: Thin but structurally correct, and it maps one-to-one onto
  the two pieces of the adapter contract: a *transport* failure (no connection)
  is an auth/credential problem, while a *content* failure (garbled messages) is
  a `transformRequest`/`transformResponse` bug. The gap the Prospector flagged is
  real: there is no severity data, no metrics, and no failure examples — so treat
  this as a naming of the two failure surfaces to check, not as an evidence-backed
  runbook. The guide can generalize it: for any third-party HTTP target, separate
  "can I reach and authenticate" from "did the payload survive translation."

### Claim 9: The page's red-team execution workflow is `redteam generate` → `redteam eval` → `view`
- **Evidence**: The "Test Execution" code block lists the three commands with
  inline comments (generate test cases, execute evaluation, view results in the
  web UI).
- **Confidence**: settled (documented CLI)
- **Quote**: (code block; see Concrete Artifacts → Test execution) "promptfoo redteam generate" / "promptfoo redteam eval" / "promptfoo view"
- **Our assessment**: Minor but worth recording because the command surface
  differs from the sibling red-team notes: the older blog guides use
  `init → run → report` (`blog-promptfoo-red-team-claude.md` Claim 8) and the
  Gemini note uses `init → generate → run → report`
  (`blog-promptfoo-red-team-gemini.md` Claim 6), whereas this page uses
  `eval` (not `run`) and `view` (not `report`). The CLI has drifted; the guide
  should cite command names as version-relative, not as fixed facts.

## Concrete Artifacts

All artifacts are copied verbatim from the source page's code blocks.

### Chatbase target config (verbatim from "Basic Configuration")

```
targets:
  - id: 'http'
    config:
      method: 'POST'
      url: 'https://www.chatbase.co/api/v1/chat'
      headers:
        'Content-Type': 'application/json'
        'Authorization': 'Bearer YOUR_API_TOKEN'
      body:
        {
          'messages': '{{prompt}}',
          'chatbotId': 'YOUR_CHATBOT_ID',
          'stream': false,
          'temperature': 0,
          'model': 'gpt-5-mini',
          'conversationId': '{{conversationId}}',
        }
      transformResponse: 'json.text'
      transformRequest: '[{ role: "user", content: prompt }]'
defaultTest:
  options:
    transformVars: '{ ...vars, conversationId: context.uuid }'
```

### Stateful strategy config (verbatim from "Strategy Configuration")

```
strategies:
  - id: 'goat'
    config:
      stateful: true
  - id: 'crescendo'
    config:
      stateful: true
  - id: 'mischievous-user'
    config:
      stateful: true
```

### Test execution (verbatim from "Test Execution")

```
# Generate test cases
promptfoo redteam generate

# Execute evaluation
promptfoo redteam eval

# View detailed results in the web UI
promptfoo view
```

### Prerequisites (verbatim from "Prerequisites")

- Node.js `>=22.22.0`
- promptfoo CLI (`npm install -g promptfoo`)
- Chatbase API credentials:
    - API Bearer Token (from your Chatbase dashboard)
    - Chatbot ID (found in your bot's settings)

## Cross-References

### Candidate paths from `miner-related-notes.md` (10 paths — cited or dismissed before writing)

- **Dismissed — unrelated**: `docs-google-sre-team-lifecycles.md` (SRE team
  org/first-SRE hiring); `docs-litellm-batches-api.md` (LiteLLM batch
  rate-limiting); `blog-pagerduty-sre-agent-triage.md` (AI incident triage);
  `docs-promptfoo-pi-scorer.md` (external model-graded scorer); `docs-langfuse-mcp-server.md`
  (documentation MCP server); `docs-google-sre-eliminating-toil.md` (toil
  definition/quantification); `docs-google-sre-reliable-product-launches.md`
  (launch coordination); `docs-promptfoo-deterministic-metrics.md`
  (deterministic assertions — no provider-transform or external-target content).
  None touch red-teaming a third-party HTTP target or its adapter config.
- **Dismissed — adjacent, no evidential overlap**:
  `docs-promptfoo-enterprise-findings-reports.md` (finding disposition, export
  formats, and the read-only findings surface — it is the *post-scan* reporting
  layer; this page is the *scan-configuration* layer and contains no findings or
  report content).
- **Cited**: `blog-promptfoo-owasp-red-teaming.md` — see Corroborates below.

### Cross-references with existing source notes

- **Corroborates**:
  - `blog-promptfoo-owasp-red-teaming.md` **Claim 5** — post-deployment,
    black-box testing "test[s] an application without prior knowledge of its
    internal workings" and should enumerate all exposed app information because
    "whatever information is exposed to users or the public can be exploited by
    attackers." This page is a concrete, runnable harness for exactly that
    black-box external-app test the OWASP note prescribes. (Verified: #555
    Claim 5 = post-deployment black-box testing / enumerate exposed surface ✓)
  - `blog-promptfoo-owasp-red-teaming.md` **Claim 8** — the OWASP guide's
    agent/multi-agent risk categories include "multi-turn attack chains within
    the same AI model." This page supplies the harness-level config (stateful
    strategies + `conversationId` threading) that materially exercises that risk
    category against a live external target. (Verified: #555 Claim 8 = five agent
    risk categories incl. multi-turn attack chains ✓)
  - `blog-promptfoo-red-team-claude.md` **Claim 7** — the red-team strategy list
    ("Strategies determine HOW attacks are delivered:") already names `crescendo`
    as "Gradual escalation." This page reuses that escalation strategy and adds
    the explicit `stateful: true` flag plus two sibling multi-turn strategies.
    (Verified: #689 Claim 7 = attack-strategy list incl. crescendo ✓)

- **Contradicts**: None that require a contradiction issue. The only apparent
  surfaces are non-conflicts: (a) this page's `conversationId`-in-the-request-body
  scheme vs. `docs-promptfoo-chat-threads.md` Claim 5's metadata-based
  `conversationId` isolation — these are the external-target and local-eval forms
  of the same state-key idea, both leading to the same guide advice (make the
  per-conversation identity explicit); (b) this page's `eval`/`view` command
  names vs. the blog notes' `run`/`report` — CLI version drift, not a
  disagreement (see Claim 9). CONTRADICTIONS.md has no open `C-NNN` entries and
  no open `contradiction`-labeled issue bears on this topic, so per MINER.md §4a
  no contradiction issue was filed.

- **Extends**:
  - Extends `docs-promptfoo-chat-threads.md` — that note (#1276) mines the
    *local* eval-harness conversation machinery: `conversationId` grouped via
    test `metadata` (Claim 5) and the `_conversation` built-in (Claim 1). This
    page extends it to an *external* target: the state key travels inside the
    HTTP request body and is generated per test from `context.uuid`, so the
    endpoint (not Promptfoo) holds conversation history. It is the black-box
    counterpart to the local `_conversation` replay surface.
  - Extends `docs-promptfoo-configuration-guide.md` — that note documents
    `transformVars` as the input-side transform whose returned keys merge into
    `vars` and can override existing keys (Claim 4), with the palette/volume
    example. This page is a second, independent application of the same
    transform: `'{ ...vars, conversationId: context.uuid }'` uses the documented
    spread pattern to inject a per-test session key, which corroborates the
    transform's intended use for derived per-test inputs. (Verified: #1513
    Claim 4 = `transformVars` input-side, merges/overrides keys ✓)
  - Extends `docs-promptfoo-configuration-tools.md` **Claim 9** — the HTTP
    provider's `transformToolsFormat` "escape hatch" translates `tools` /
    `tool_choice` for non-standard APIs. This page documents the *message- and
    response-shape* sibling of that escape hatch (`transformRequest` /
    `transformResponse`) for the same HTTP-provider adaptation problem. (Verified:
    `docs-promptfoo-configuration-tools.md` Claim 9 = `transformToolsFormat`
    converts both `tools` and `tool_choice` ✓)
  - Extends `docs-promptfoo-extension-hooks-and-sessions.md` **Claim 6** — the
    HTTP provider's session-id mechanism for stateful third-party endpoints is a
    `sessionParser` expression that extracts an id from the server *response*,
    with `response.sessionId` winning over `vars.sessionId`. This page solves the
    same "how does a stateful third-party target identify the conversation"
    problem from the opposite direction: rather than parsing an id out of the
    response, it *manufactures* the id client-side (`context.uuid`) and puts it
    in the request body. The two are complementary designs for third-party
    session identity. (Verified: `docs-promptfoo-extension-hooks-and-sessions.md`
    Claim 6 = session-id resolution precedence + HTTP `sessionParser` ✓)
  - Extends `docs-promptfoo-testing-llm-chains.md` — that note mines wrapping an
    external chain behind a script/custom provider (`exec:` / `callApi`) so
    Promptfoo can grade systems it does not host. This page is the config-only
    version of the same goal for an HTTP chatbot: no code, just `http` target +
    transforms. Both are "bring an external system under the eval/red-team
    harness" patterns.

- **Novel**:
  - **The black-box third-party chatbot red-team pattern** — red-teaming an
    external, opaque HTTP chatbot (Chatbase) that you do not control, rather
    than a model or app you host. The corpus has red-team method notes and
    local multi-turn machinery, but no note covers this distinct target class.
  - **The `context.uuid` → `conversationId` `transformVars` idiom** (Claim 4) —
    manufacturing a unique external session id per test via the input-side
    transform; a concrete, reusable session-identity recipe.
  - **`goat` and `mischievous-user` as named stateful multi-turn strategies**
    (Claim 6) — net-new strategy names (`crescendo` is already in the corpus).
  - **The two-layer `transformRequest`/`transformResponse` contract applied to a
    red-team target** (Claim 5) — the message-in / text-out adapter for a
    foreign API in an offensive-testing context.
  - **The two-branch third-party failure taxonomy** (Claim 8) — connection →
    credentials, garbled → parsers — as the diagnostic split for black-box
    integrations.

## Guide Impact

- **Chapter 06 (Security & Trust) — red-teaming external/third-party LLM
  applications**: Add a subsection for red-teaming a hosted chatbot you do not
  own, with this source as the concrete recipe:
  - State the target class explicitly: a third-party SaaS chatbot reached over
    its own HTTP API, where black-box enumeration (per OWASP, Claim 5) is the
    only option.
  - Give the adapter contract (Claim 5): a generic `http` target plus
    `transformRequest` (OpenAI-style messages → target wire shape) and
    `transformResponse` (extract the single response string, e.g. `json.text`)
    before any grader sees the output.
  - Give the session-identity rule (Claims 3-4): for a stateful target the
    conversation key is the endpoint's, not the harness's, so inject a per-test
    id (`conversationId` from `transformVars: '{ ...vars, conversationId:
    context.uuid }'`); otherwise tests bleed state into each other. Cross-link
    the local `docs-promptfoo-chat-threads.md` Claim 5 (`metadata.conversationId`)
    contrast and the `sessionParser` alternative
    (`docs-promptfoo-extension-hooks-and-sessions.md` Claim 6).
  - List the stateful multi-turn strategies (Claim 6: `goat`, `crescendo`,
    `mischievous-user`) as the attack set that requires a stateful target, and
    note `stateful: true` as the flag that says so.
  - Add the diagnostic split (Claim 8) as the first troubleshooting step:
    connection failure → credentials; garbled content → parsers.

- **Chapter 05 (LLM Ops Reliability) — reproducibility of red-team runs**: Add
  the determinism choices (Claim 7): pin `stream: false` (so the response is a
  single parseable JSON field) and `temperature: 0` in the target request body
  while red-teaming, so verdicts are stable across reruns. This is the concrete
  mechanism behind the corpus's report-the-run-context discipline; place it
  beside the ASR/measurement material from
  `blog-promptfoo-asr-not-portable-metric.md`.

- **Chapter 05 (LLM Ops Reliability) — third-party dependency surface**: The
  failure taxonomy (Claim 8) reinforces the existing external-dependency
  guidance: a red-team gate against a third-party endpoint has a transport layer
  (auth/connectivity) and a translation layer (parsers), and a green/red verdict
  is only meaningful once both are eliminated. No change to the existing
  dependency material, just a concrete LLM-op example to cite.

## Extraction Notes

- Source is a single Promptfoo docs page read in full via WebFetch
  (https://www.promptfoo.dev/docs/guides/chatbase-redteam). Footer shows "Last
  updated on **Oct 10, 2026** by **mldangelo-oai**"; no canonical first-published
  date, so `date_published` carries the last-updated date (same convention as the
  sibling promptfoo docs notes #1264, #1276).
- Two Prospector runs raced on this issue and both triaged it `triaged:text` with
  the same type, chapters, and key question; the reconciling comment settled on
  `priority:medium` and the miner guidance in the assessment stands. This note
  follows that guidance: extract the HTTP-provider-as-red-team-target wiring
  (session identity, the two-layer parser contract, the stateful strategy set,
  the failure split) and treat Chatbase product details (credentials, the
  `gpt-5-mini` placeholder, the one vendor's API shape) as noise.
- Per the Prospector's note, the page's CLI/Node prerequisites
  (`Node >= 22.22.0`) are treated as vendor-documented, not independently
  verified; the `model: 'gpt-5-mini'` string in the example body is a placeholder
  and is not a claim about Chatbase's model.
- No sub-pages followed: the "Additional Resources" links (Chatbase API docs, the
  Promptfoo HTTP Provider guide, and the Multi-turn Testing Strategies page) are
  tooling references; the two adapters they would deepen — HTTP provider
  transforms and session handling — are already covered in the corpus by
  `docs-promptfoo-configuration-tools.md` (Claim 9) and
  `docs-promptfoo-extension-hooks-and-sessions.md` (Claim 6), which this note
  cites rather than re-extracts.
- Cross-references: every cited claim number was re-read and verified per MINER.md
  §4b before citation — OWASP #555 Claims 5 & 8; red-team-claude #689 Claim 7;
  chat-threads #1276 Claim 5 (and Claim 1 by section context); configuration-guide
  #1513 Claim 4; configuration-tools Claim 9 and extension-hooks-and-sessions
  Claim 6 (cited by note + claim heading, both verified against the files). All 10
  candidate paths from `miner-related-notes.md` were cited or explicitly
  dismissed above.
- `confidence_overall` = `emerging`: first-party vendor documentation is
  authoritative for the documented config surface (individual claims graded
  `settled` where they are direct product facts), but the page is a thin recipe —
  no metrics, no run results, no severity data — and its operational value (the
  black-box target-class pattern) is our synthesis across the config and the
  surrounding corpus. Consistent with the sibling promptfoo notes.
- `registry/sources.json` and `registry/claims-index.json` were intentionally not
  edited: they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.
