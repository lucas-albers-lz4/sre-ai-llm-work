---
source_url: https://www.promptfoo.dev/docs/configuration/chat/
source_type: docs
title: "Promptfoo Docs — Chat Conversations and Multi-Turn Threads"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-11
date_extracted: 2026-09-11
last_checked: 2026-09-11
status: current
confidence_overall: emerging
issue: "#1276"
---

# Promptfoo Docs — Chat Conversations and Multi-Turn Threads

> Promptfoo's configuration reference for multi-turn / conversation-style eval
> suites. Its SRE-relevant payload is the conversational-state machinery a
> stateful regression gate is built on: a `_conversation` built-in that replays
> prior turns and **forces the whole eval to run single-threaded (concurrency 1)**
> — a silent parallelism loss with no equivalent of the explicit
> `--max-concurrency` knob the red-team notes carry — plus per-`conversationId`
> state isolation, `storeOutputAs`/`transform` chaining that serializes test
> cases, and a shared-history fixture pattern for testing follow-up questions
> against fixed prior turns.

## Source Context

- **Type**: docs (vendor configuration reference — Promptfoo "Chat threads"
  page under Evals → Configuration, auto-discovered from the registered
  `promptfoo-docs` site-crawl seed)
- **Author credibility**: Promptfoo, the LLM eval / security vendor (now part of
  OpenAI per the site banner). First-party documentation of the product's own
  config surface — authoritative about the documented syntax, the `_conversation`
  variable semantics, and the concurrency behavior, but vendor-positioned: no
  independent validation of the multi-turn pattern's production consequences
  (the cascade/cost claims below are our synthesis, flagged as such).
- **Scope**: Covers multishot message-array prompt files (JSON/YAML), simplified
  chat markup, the `defaultTest.vars.messages` shared-history fixture pattern,
  the built-in `_conversation` variable (`Completion[]` type signature,
  `completion.prompt` / `completion.input` accessors), the single-threaded
  execution consequence of referencing `_conversation`, `conversationId`-based
  history separation, JSON-in-`content` escaping, and `storeOutputAs` + `transform`
  output chaining. Does NOT cover: assertion/metric design, caching semantics
  (sibling #1275), dataset generation (sibling #1277), providers, or red-team
  tooling. The Nunjucks template mechanics for building message arrays are
  treated as prompt-file construction detail and are summarized, not extracted
  claim-by-claim (per Prospector's triage guidance).
- **Vendor caveat**: documented behavior is checkable against the installed
  `promptfoo eval`; the *operational consequences* (CI wall-clock, cascading
  failure attribution, cache interaction) are our interpretation of that
  documented surface, not vendor statements.

## Extracted Claims

### Claim 1: When a prompt references `_conversation` as a Nunjucks variable, the eval runs single-threaded (concurrency of 1) — a silent parallelism loss with no config knob to restore it
- **Evidence**: The page's `info` callout directly under the `_conversation`
  section states the constraint as documented behavior.
- **Confidence**: settled (documented product behavior)
- **Quote**: "When a prompt references `_conversation` as a Nunjucks variable, the eval will run single-threaded (concurrency of 1)."
- **Our assessment**: This is the page's one hard operational constraint and the
  reason it matters for SRE: a multi-turn suite that replays prior turns
  serialises the entire run, so CI wall-clock and provider concurrency limits
  scale with test count rather than parallelising. Unlike the red-team CLI's
  explicit `--max-concurrency 30` knob (sibling notes), there is no documented
  option to raise concurrency for a `_conversation`-driven eval — the serialization
  is forced and conditional on the prompt merely *referencing* `_conversation`.
  It is also invisible in the config at a glance; nothing marks a suite as
  serialized except the variable use, which the Prospector correctly flagged as
  this page's primary payload.

### Claim 2: The `_conversation` variable is typed as `Conversation = Completion[]`, where `Completion = {prompt, input, output}` — `prompt` holds the prior turns, `input` is the last user message, and `output` the prior assistant response
- **Evidence**: The page declares the type signature block verbatim and explains
  the accessors with `completion.prompt.length` / `completion.prompt[0]` and the
  `completion.input` shortcut.
- **Confidence**: settled (first-party type signature)
- **Quote**: "Use `completion.input` as a shortcut to get the last user message. In a chat-formatted prompt, `input` is set to the last user message, equivalent to `completion.prompt[completion.prompt.length - 1].content`."
- **Our assessment**: This is the concrete interface a suite author codes against:
  `completion.input` (last user turn) plus `completion.output` (prior assistant
  turn) are the two hand-holds for replaying history. The type signature also
  shows the surface is string-or-object prompts, which matters for
  chat-formatted (message-array) prompts where `input` aliases the last message's
  `content`.

### Claim 3: In a `_conversation`-driven suite, later turns are built from the model's own earlier outputs rather than fixture data, so a degraded or cached prior turn cascades into every subsequent turn
- **Evidence**: The `_conversation` example config (three `question` variables
  chained) with the page's note "each question assumes context from the previous
  output"; the paired prompt template injects `completion.output` from prior
  turns into each later request.
- **Confidence**: emerging (mechanism is documented; the failure-attribution
  consequence is our synthesis)
- **Quote**: "Here's an example test config. Note how each question assumes context from the previous output:"
- **Our assessment**: Test cases in this mode are not independent: one degraded
  turn feeds an old or wrong assistant response into the next live call, so a
  mid-suite failure corrupts every downstream verdict. That is a different
  failure-attribution problem from single-turn evals, where cases are
  independent and a red result localises itself. It also interacts with
  caching: a cached (or stale) prior turn replays an old assistant response into
  the next turn instead of what the model would produce fresh — the sibling
  caching surface (#1275) is the other half of that interaction and has not
  landed yet.

### Claim 4: `storeOutputAs` records an LLM output as a variable usable in subsequent test cases, and `transform` can mutate it before storage — an explicit mechanism that chains test cases into a sequential dependency
- **Evidence**: The `storeOutputAs` section's three-case config (fruit →
  reason → snarky rebuttal) and the `transform` subsection with the
  `transform: output.split(' ')[0]` example.
- **Confidence**: settled (documented behavior)
- **Quote**: "The `storeOutputAs` option makes it possible to reference previous outputs in multi-turn conversations. When set, it records the LLM output as a variable that can be used in subsequent chats." and "Outputs can be modified before storage using the `transform` property:" and "Transforms can be Javascript snippets or they can be entire separate Python or Javascript files."
- **Our assessment**: This is the second mechanism that prevents parallelisation —
  alongside `_conversation` serialization (Claim 1), `storeOutputAs` creates an
  explicit data dependency between test cases (case N's output is case N+1's
  `var`). Note the subtle interplay: `storeOutputAs` reuses outputs as *vars*,
  whereas `_conversation` reuses outputs as *chat turns*; a suite author who
  chains outputs without referencing `_conversation` may still inherit serial
  dependency through vars. `transform` (JS/Python) is the knob for sanitising
  extracted outputs before reuse — e.g. taking the first token rather than the
  full reply.

### Claim 5: Conversation history is isolated (or shared) by explicit config — each unique `conversationId` in test metadata maintains its own history, and scenarios isolate conversations by default, so unrelated tests without an id otherwise share one context
- **Evidence**: The "Separating Chat Conversations" section states the rule and
  gives a four-case config splitting `conversation1` / `conversation2` via
  `metadata.conversationId`.
- **Confidence**: settled (documented behavior)
- **Quote**: "Each unique `conversationId` maintains its own separate conversation history. Scenarios automatically isolate conversations by default."
- **Our assessment**: Turn isolation is opt-in via metadata, not implicit. A
  suite that omits `conversationId` leaves all cases sharing one context stream,
  which is the cross-contamination hazard if the intent was parallel isolated
  conversations. The isolation mechanism is the tool-visible side of the design:
  `conversationId` is the grouping key and scenarios give it to you for free —
  worth stating explicitly in the guide because the *default* (shared) is the
  surprising direction.

### Claim 6: A shared conversation-history fixture can be defined once in `defaultTest.vars` and reused across follow-up test cases — each case tests a different follow-up question against the same fixed prior turns
- **Evidence**: The "Creating a conversation history fixture" section: a
  `defaultTest.vars.messages` block (system_message + two exchange pairs) with
  three follow-up `question` cases, and the `{{ question | dump }}` template.
- **Confidence**: settled (documented pattern with a runnable example)
- **Quote**: "Using nunjucks templates, we can combine multiple chat messages. Here's an example in which the previous conversation is a fixture for *all* tests. Each case tests a different follow-up message:"
- **Our assessment**: The fixture-in-`defaultTest.vars` pattern is the
  deterministic, parallel-safe alternative to `_conversation` replaying live
  outputs: history is pinned data, so cases stay independent, reruns are
  reproducible, and the `_conversation` serialization trigger (Claim 1) is
  avoided. This is the natural shape for a conversational-agent regression gate
  when you want to test N follow-ups against a stable history rather than test
  the model's multi-turn *generation*.

### Claim 7: JSON prompt files auto-escape vars containing quotes/newlines, while non-JSON (Nunjucks) template files must use the built-in `dump` filter to stringify values — a silent-corruption class of bug for hand-written prompt configs
- **Evidence**: The `info` callout in the fixture section makes both the
  auto-escape and the `dump` requirement explicit, illustrated by the fixture's
  `{{ system_message | dump }}` / `{{ question | dump }}` and the
  `{{ input | trim | dump }}` JSON-content example.
- **Confidence**: settled (documented behavior)
- **Quote**: "Variables containing multiple lines and quotes are automatically escaped in JSON prompt files." and "If the file is not valid JSON (such as in the case above, due to the nunjucks `{% for %}` loops), use the built-in nunjucks filter `dump` to stringify the object as JSON."
- **Our assessment**: The trap is that escaping is silent and situational. In a
  valid-JSON file the template engine escapes for you; in a Nunjucks template
  file (which is most multi-turn prompts — they use `{% for %}` loops) it does
  not, and skipping `dump` inserts raw quotes/newlines that corrupt the prompt
  structure. A hand-written prompt template that omits `dump` produces subtly
  broken messages that are hard to spot because the eval still runs. This is the
  class of reproducible-but-invisible config bug worth a guide warning for teams
  hand-authoring multi-turn prompt files.

### Claim 8: Stateless multishot conversations (fixed `{role, content}` message lists rendered with `{{ messages | dump }}`) are the non-serializing alternative — only `_conversation` triggers single-threaded execution
- **Evidence**: The "Multishot conversations" section: "Most providers support
  full \"multishot\" chat conversations" with a `tests.vars.messages` list and a
  one-line `{{ messages | dump }}` prompt; the serialization note (Claim 1) is
  scoped specifically to prompts *referencing `_conversation`*.
- **Confidence**: settled (documented behavior)
- **Quote**: "Most providers support full \"multishot\" chat conversations, including multiple assistant, user, and system prompts."
- **Our assessment**: This boundary matters operationally: a suite where every
  turn's history is fixed data (multishot fixture) parallelises normally, while
  only the `_conversation`-replaying form is forced to concurrency 1. So the
  parallelisation decision for a multi-turn gate is really the decision of which
  history mechanism you use — fixed fixtures for parallel run, live replay for
  test-follow-up response quality. The same insight explains why the Prospector's
  red-team `--max-concurrency 30` (which parallelises attack generation, not
  conversation replay) is not in tension with this page's concurrency-1.

## Concrete Artifacts

All artifacts are copied verbatim from the source page's code blocks.

### `_conversation` type signature (verbatim from "Using the `_conversation` variable")

```
type Completion = {
  prompt: string | object;
  input: string;
  output: string;
};

type Conversation = Completion[];
```

### Multi-turn test config and prompt (verbatim from "Using the `_conversation` variable")

```
tests:
  - vars:
      question: Who founded Facebook?
  - vars:
      question: Where does he live?
  - vars:
      question: Which state is that in?
```

prompt.json:

```
[
  {% for completion in _conversation %}
    {
      "role": "user",
      "content": "{{ completion.input }}"
    },
    {
      "role": "assistant",
      "content": "{{ completion.output }}"
    },
  {% endfor %}
  {
    "role": "user",
    "content": "{{ question }}"
  }
]
```

### `conversationId` isolation config (verbatim from "Separating Chat Conversations")

```
tests:
  - vars:
      question: 'Who founded Facebook?'
    metadata:
      conversationId: 'conversation1'
  - vars:
      question: 'Where does he live?'
    metadata:
      conversationId: 'conversation1'
  - vars:
      question: 'Where is Yosemite National Park?'
    metadata:
      conversationId: 'conversation2'
  - vars:
      question: 'What are good hikes there?'
    metadata:
      conversationId: 'conversation2'
```

### Conversation-history fixture (verbatim from "Creating a conversation history fixture")

```
# Set up the conversation history
defaultTest:
  vars:
    system_message: Answer concisely
    messages:
      - user: Who founded Facebook?
      - assistant: Mark Zuckerberg
      - user: What's his favorite food?
      - assistant: Pizza

# Test multiple follow-ups
tests:
  - vars:
      question: Did he create any other companies?
  - vars:
      question: What is his role at Internet.org?
  - vars:
      question: Will he let me borrow $5?
```

### `storeOutputAs` + `transform` chaining (verbatim from "Using `storeOutputAs`")

```
prompts:
  - 'Respond to the user: {{message}}'
providers:
  - openai:gpt-5
tests:
  - vars:
      message: "What's your favorite fruit? You must pick one. Output the name of a fruit only"
    options:
      storeOutputAs: favoriteFruit
  - vars:
      message: 'Why do you like {{favoriteFruit}} so much?'
    options:
      storeOutputAs: reason
  - vars:
      message: 'Write a snarky 2 sentence rebuttal to this argument for loving {{favoriteFruit}}: "{{reason}}"'
```

## Cross-References

### Candidate paths from `miner-related-notes.md` (10 paths — cited or dismissed before writing)

- **Dismissed — unrelated**: `docs-google-sre-team-lifecycles.md` (team org /
  first-SRE hiring); `blog-pagerduty-sre-agent-triage.md` (AI incident triage
  pipeline); `docs-langfuse-mcp-server.md` (documentation MCP server);
  `docs-google-sre-eliminating-toil.md` (toil definition/quantification);
  `docs-google-sre-reliable-product-launches.md` (launch coordination);
  `docs-google-sre-prodcast-04-09-ai-agents.md` (agent spectrum / pre-oncaller,
  no eval-harness config content); `docs-google-sre-prodcast-03-06-incident-response-tooling.md`
  (IR tooling); `docs-google-sre-slo-engineering-case-studies.md` (SLO design
  cases). None touch LLM eval-harness conversation-state configuration.
- **Dismissed — adjacent but no evidential overlap**: `blog-promptfoo-red-team-claude.md`
  (red-team plugin catalog and compute-DoS methodology for Claude; no multi-turn
  eval-harness conversation-state content — the runtime attack-simulation arena
  is different from this page's regression-suite configuration surface).
- **Cited**: `blog-promptfoo-owasp-red-teaming.md` — see Corroborates below.

### Cross-references with existing source notes

- **Corroborates**:
  - `blog-promptfoo-red-team-gemini.md` **Claim 6** — the red-team CLI workflow
    runs with "a `--max-concurrency` parallel option" (`--max-concurrency 30`).
    This is the *explicit* parallelism knob whose multi-turn-eval counterpart is
    *absent* here: red-team attack generation parallelises via a flag, while a
    `_conversation` eval is forced to concurrency 1 with no equivalent control.
    The two notes are the two sides of the same eval-throughput tradeoff.
    (Verified: #690 Claim 6 = init→generate→run(`--max-concurrency`)→report ✓)
  - `blog-promptfoo-red-team-gpt.md` **Claim 7** — the red-team CLI workflow
    "with an optional `--max-concurrency 30`;" same explicit-parallelism-vs-forced-
    serialization contrast as the Gemini note. (Verified: #691 Claim 7 = CLI
    workflow + report fields; the `--max-concurrency` flag is also noted in that
    note's Claim 6 assessment ✓ — the Prospector's triage comment cited Claim 6;
    the verified location for the flag-carrying claim in that note is Claim 7.)
  - `blog-promptfoo-owasp-red-teaming.md` **Claim 8** — OWASP's agent/multi-agent
    risk categories include "Multi-turn attack chains within the same AI model" —
    the attack-surface reason such suites exist; this page supplies the
    harness-level configuration machinery (conversation replay, isolation,
    chaining) those red-team suites would be scored against. (Verified: #555
    Claim 8 = the five OWASP agent risk categories incl. multi-turn attack
    chains ✓)
  - `blog-promptfoo-model-upgrades-break-agent-safety.md` **Claim 2** (the
    upgrade checklist's step 2 re-runs a "multi-turn escalation set") and
    **Claim 7** ("If your agent has memory, RAG, or long workflows, test
    multi-turn attacks explicitly") — this page documents the config surface a
    team uses to actually build that multi-turn regression set. (Verified: #482
    Claim 2 = re-run safety suites incl. multi-turn escalation; Claim 7 = four
    shifted attack vectors incl. multi-turn ✓)

- **Contradicts**: None that require a contradiction issue. The one apparent
  surface — this page's forced `_conversation` concurrency-1 vs. the sibling
  notes' explicit `--max-concurrency 30` — is not a contradiction: they govern
  different surfaces of the same tool (test-case execution vs. red-team attack
  generation) and both point to the same guide advice (know whether your eval
  run parallelises; budget CI wall-clock accordingly). The fixture-based
  multishot configuration (Claim 8) is the documented, non-serializing
  alternative on the same page, not a disagreement. CONTRADICTIONS.md has no
  open `C-NNN` entries and the only open `contradiction`-labeled issue (#1150) is
  an unrelated LiteLLM-routing topic — so no contradiction issue was filed per
  MINER.md §4a. (The caching-interaction nuance in Claim 3 references sibling
  surface #1275, which has not landed as a note yet; nothing to contradict.)

- **Extends**:
  - Extends `docs-promptfoo-code-scan-cli.md` (#1264) — the sibling promptfoo
    docs-config note (same vendor-docs register, code-scanning surface). This
    note extends the register into eval-harness configuration: #1264 mined the
    operational interface of `promptfoo code-scans`; this note mines the
    operational interface of multi-turn conversation evals (concurrency,
    isolation, chaining, escaping).
  - Extends `blog-promptfoo-asr-not-portable-metric.md` (#261) — that note's
    discipline (report ASR with its K and attempt budget; "cost drives tooling
    decisions") transfers to multi-turn eval verdicts: when turn N's verdict
    depends on turn N-1's output (Claim 3), an aggregated multi-turn ASR needs
    the same per-run metadata (history source, chain length, budget) to be
    comparable — and the serialization cost (Claim 1) is exactly the kind of
    cost-per-run fact that note says to report. (Verified: #261 Claim 5 = report
    ASR/K/attempts/cost; Claim 13 = report both ASR values with their K ✓)
  - Extends `blog-promptfoo-model-upgrades-break-agent-safety.md` — #482
    prescribes *that* multi-turn suites be re-run on upgrades (Claim 2); this
    page shows *how* to author the suite (fixture vs `_conversation`, Claim 6 vs
    Claim 1) and the operational cost of each choice.

- **Novel**:
  - **The forced-serialization constraint** (Claim 1): the first eval-harness
    runtime/concurrency finding in the corpus — a documented trigger that flips
    a whole eval suite to single-threaded execution with no re-enable knob.
  - **The `_conversation` type signature and accessors** (Claim 2) as the concrete
    interface for stateful eval prompts.
  - **`conversationId`-based state isolation semantics** (Claim 5) — and
    specifically that the default is *shared* history, isolation is opt-in.
  - **`storeOutputAs`/`transform` as a sequential-chaining mechanism** (Claim 4)
    — outputs-as-vars linking test cases, distinct from outputs-as-turns.
  - **The JSON-escaping / `dump`-filter gotcha** (Claim 7) as a silent-corruption
    failure class in hand-authored prompt configs.
  - **The parallel-vs-serial authoring split** (Claim 6 vs Claim 1): fixture-driven
    multishot parallelises; `_conversation` replay does not — an operational
    choice no existing note articulates.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — evaluation and measurement methodology,
  stateful/multi-turn regression suites** (primary): Add two facts and two
  risks to the eval-methodology material:
  - Facts: a prompt that references `_conversation` forces concurrency 1 (Claim
    1); conversation history is grouped by `metadata.conversationId`, with
    scenarios isolating by default and the no-id default being *shared* history
    (Claim 5).
  - Risks: later turns embed the model's own earlier outputs, so a degraded or
    cached prior turn cascades into every subsequent verdict (Claim 3) — a
    failure-attribution difference from independent single-turn cases worth
    stating alongside the ASR measurement discipline from
    `blog-promptfoo-asr-not-portable-metric.md` (report chain/history context
    with any multi-turn score). And the CI cost consequence of Claim 1: suite
    wall-clock scales linearly with test count when serialized — budget timeouts
    accordingly.
  - Recommend the fixture-in-`defaultTest.vars` pattern (Claim 6) for
    deterministic, parallel-safe conversational gates, and document the
    `--max-concurrency` contrast with the red-team notes (per-flag parallelism in
    red-team runs — sibling #690/#691 — vs. forced serialization in multi-turn
    evals) so CI guidance is consistent.

- **Chapter 03 (Runbooks and Agents) — regression suites for conversational
  agents**: Add the concrete authoring recipe for a conversational-agent
  regression gate: `defaultTest.vars.messages` history fixture + follow-up
  `question` cases (Claim 6), explicit `conversationId` grouping for any
  stateful scenario (Claim 5), the `completion.input` interface for
  replay-based suites (Claim 2), and the `storeOutputAs`/`transform` chaining
  pattern for output-dependent follow-ups (Claim 4). Include the JSON-escaping /
  `dump`-filter warning (Claim 7) as a prompt-authoring gotcha, since
  multi-turn prompt files are usually non-JSON Nunjucks templates.

## Extraction Notes

- Source is a single promptfoo docs page read in full via WebFetch
  (https://www.promptfoo.dev/docs/configuration/chat/). "Last updated on Sep 11,
  2026" — no canonical first-published date, so `date_published` carries the
  last-updated date (same convention as the sibling #1264 docs note).
- Per the Prospector's authoritative triage (reconciled `priority:medium`,
  superseding the first run's "Novelty: low"): the Nunjucks message-array
  template mechanics (loops, `| dump` multishot markup) are summarized rather
  than extracted claim-by-claim; the JSON-escaping gotcha is kept because the
  reconciled triage explicitly listed it (item 5) as an extract target.
- No sub-pages followed: the "See Also" links (Prompt Parameters, Test
  Configuration → transforming outputs, Nunjucks templates, the
  `examples/config-multi-turn` GitHub repo) are tooling references to
  syntax/mechanics this page already states or that the Prospector marked as
  skip-scope. The GitHub example config would only add template syntax, not
  operational facts.
- Sibling #1275 (caching) and #1277 (datasets) have not landed in `source-notes/`
  yet (verified: no caching/datasets notes exist for promptfoo). The
  cache-of-prior-turn interaction in Claim 3 therefore references the sibling
  surface without citing a nonexistent note.
- Cross-references: every cited claim number was re-read and verified per
  MINER.md §4b before citation — #690 Claim 6, #691 Claim 7, #555 Claim 8,
  #482 Claims 2 & 7, #261 Claims 5 & 13; the code-scan-CLI sibling (#1264)
  is cited by note identity/section, not a claim number. Note: the Prospector's
  triage comment attributed the `--max-concurrency` content to
  `blog-promptfoo-red-team-gpt.md` Claim 6; the verified location is Claim 7
  (with Claim 6's assessment also mentioning the flag) — cited as Claim 7 here.
- `confidence_overall` = `emerging`, consistent with the sibling promptfoo
  notes (#1264, #690, #691): first-party tool documentation is authoritative for
  the documented surface (claims graded `settled` individually where they are
  direct product facts), but the operational consequences (claim 3 cascade, CI
  cost framing) are our synthesis, vendor-positioned, and the docs surface will
  drift.
- `registry/sources.json` and `registry/claims-index.json` were intentionally
  not edited: they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.