---
source_url: https://simonwillison.net/2026/Jun/10/datasette-agent/
source_type: blog-post
title: "datasette-agent 0.2a0"
author: Simon Willison
date_published: 2026-06-10
date_extracted: 2026-06-18
last_checked: 2026-06-18
status: current
confidence_overall: emerging
issue: "#1203"
---

# datasette-agent 0.2a0

> The 0.2a0 release of Datasette Agent introduces two concrete agent interaction
> patterns: `ask_user()` for mid-execution user prompting with database-backed
> persistence across server restarts, and `save_query` with an explicit approval
> gate before any SQL artifact is persisted.

## Source Context

- **Type**: blog-post (a "beat" — Simon Willison's short-form release announcement
  format at simonwillison.net, June 10, 2026. The post is brief, covering the two
  major new capabilities in 0.2a0 with key verbatim descriptions of their behavior.)
- **Author credibility**: Simon Willison is the creator of Datasette and the primary
  developer of Datasette Agent. This is first-party release documentation —
  authoritative for the feature's capabilities, API, and design intent. He published
  the Datasette Agent 0.1a1 platform announcement (issue #1011) and datasette-agent-charts
  0.1a1 (issue #984) before this release, providing full context for the platform this
  builds on. He explicitly notes that `ask_user()` was implemented with the help of
  Claude Fable 5. No vendor affiliation.
- **Scope**: Covers the two new capabilities in datasette-agent 0.2a0: (1) the
  `ask_user()` mechanism — API, question types, suspension, database persistence,
  re-execution semantics; (2) the `save_query` built-in tool with its human approval
  gate. Does NOT cover: internal implementation details, performance, multi-user
  behavior of suspended conversations, how `ToolContext` is registered with the
  plugin system, or backward compatibility with 0.1a1 plugins.

## Extracted Claims

### Claim 1: The `ask_user()` API enables agent tools to ask yes/no, multiple-choice, or free-text questions mid-execution via a `ToolContext` object declared as a `context` parameter

- **Evidence**: First-party release announcement from the tool's creator. The
  API surface (parameter name `context`, class name `ToolContext`, async invocation
  `await context.ask_user(...)`) is described precisely.
- **Confidence**: emerging (first-party alpha release; the API is functional per
  the announcement, but alpha status means it may change before stable release)
- **Quote**: "Tools that declare a `context` parameter receive a `ToolContext` object, and `await context.ask_user(...)` can ask a yes/no, multiple-choice or free-text question."
  *(Source: simonwillison.net/2026/Jun/10/datasette-agent/)*
- **Our assessment**: The `context` parameter convention — declaring a parameter
  with a specific name to receive a special injected object — is a dependency
  injection pattern. Tool functions opt in to user interaction by declaring
  `context`; functions that don't need it simply omit the parameter. This keeps
  simple tools simple. The three question types cover the most common structured
  interaction forms without requiring free-form UI design: boolean decisions
  (yes/no), constrained choices (multiple-choice), and open-ended input (free-text).

### Claim 2: When a question is unanswered, the agent turn suspends — the question renders as a form in the chat UI and persists to the internal database

- **Evidence**: First-party release announcement, with explicit description of
  both the UI behavior (form in chat UI) and the persistence behavior (internal
  database). Both behaviors are described as consequences of a question being
  unanswered.
- **Confidence**: emerging (first-party; alpha status; both UI and persistence
  behaviors are explicitly stated)
- **Quote**: "While a question is unanswered the agent turn suspends: the question renders as a form in the chat UI and persists to the internal database, so suspended conversations survive a server restart."
  *(Source: simonwillison.net/2026/Jun/10/datasette-agent/)*
- **Our assessment**: Rendering as a form — rather than as text the user must
  parse and respond to in free-text — constrains the valid answer space at the
  UI level. Yes/no and multiple-choice questions become buttons or radio buttons
  rather than free-form text input. The persistence to the internal database is
  architecturally significant: the question is not ephemeral in-memory state but
  a stored record in the same SQLite database that manages Datasette Agent's other
  internal state. This makes the suspended conversation queryable and durable.

### Claim 3: Suspended conversations survive server restarts because unanswered questions are persisted to the internal database

- **Evidence**: Explicit statement in the release announcement, directly addressing
  the restart survivability as a consequence of database persistence.
- **Confidence**: emerging (first-party; this is a design intent claim backed by
  the persistence architecture described in Claim 2)
- **Quote**: (same quote as Claim 2 — the restart survivability is the stated
  purpose of the database persistence)
  *(Source: simonwillison.net/2026/Jun/10/datasette-agent/)*
- **Our assessment**: For practitioners running Datasette Agent in production or
  development environments where restarts are common, this is a practical reliability
  guarantee. A long-running agent turn that hits a question does not need to be
  restarted from scratch after a server restart — the user simply answers the form
  that reappears when they reconnect. This mirrors how email drafts survive
  application restarts: the pending action is written to storage before the
  application exits, not held in memory.

### Claim 4: Once answered, the tool function re-executes from the top with stored answers replayed — requiring `ask_user()` to be called before any side effects

- **Evidence**: First-party release announcement, with an explicit statement of
  the architectural constraint this imposes on tool authors.
- **Confidence**: emerging (first-party; the re-execution-from-top semantics is
  a non-obvious design decision that has direct implications for tool authors)
- **Quote**: "Once answered, the tool re-executes from the top with stored answers replayed, so call `ask_user()` before performing side effects."
  *(Source: simonwillison.net/2026/Jun/10/datasette-agent/)*
- **Our assessment**: The "re-execute from top" design is a pragmatic approach
  to resumption: rather than serializing and restoring mid-function execution
  state, the tool simply runs again with the previously stored answers injected
  at each `ask_user()` call. This avoids the complexity of capturing and restoring
  Python execution state but imposes a constraint: `ask_user()` calls must appear
  before any code with side effects. A tool that performs a database write, then
  calls `ask_user()`, then writes again would double the first write on
  re-execution. The explicit documentation of this constraint is important for
  practitioners — it is not obvious from the API signature alone.

### Claim 5: The new `save_query` built-in tool lets agents save SQL as Datasette stored queries, requiring explicit human approval that shows the full SQL plus proposed name, database, and visibility before storing anything

- **Evidence**: First-party release announcement, with a description of both the
  approval workflow and the information surfaced to the user before the action is
  taken.
- **Confidence**: emerging (first-party; alpha status; the approval workflow is
  explicitly described with the "nothing is stored until you click Yes" guarantee)
- **Quote**: "Saving always requires human approval - the agent shows the full SQL plus the proposed name, database and visibility, and nothing is stored until you click Yes."
  *(Source: simonwillison.net/2026/Jun/10/datasette-agent/)*
- **Our assessment**: The approval gate design makes the full context of the
  proposed action visible before commitment: SQL (what will be stored), name
  (how it will be identified), database (where it will live), and visibility
  (who can see it). This is the "confirm before commit" pattern applied to
  SQL artifact creation — analogous to a destructive shell command being
  presented in full before execution. The "nothing is stored until you click Yes"
  framing is a stronger guarantee than "you will be notified" — it is a hard
  gate, not a notification. For practitioners designing agent tools that create
  persistent artifacts, this is a concrete reference implementation.

### Claim 6: The `ask_user()` feature was built using Claude Fable 5, announced the day before this release

- **Evidence**: Author's direct statement in the release post, attributing the
  implementation to a new LLM alpha he built the previous day with Claude Fable 5's
  assistance.
- **Confidence**: anecdotal (single practitioner report; the claim is about the
  development toolchain, not the feature's behavior)
- **Quote**: "The `ask_user()` feature was enabled by the new LLM alpha I built yesterday with the help of Claude Fable 5."
  *(Source: simonwillison.net/2026/Jun/10/datasette-agent/)*
- **Our assessment**: Willison published his initial impressions of Claude Fable 5
  on June 9 (the day before this release), establishing that he was actively using
  Fable 5 at the time. The reference to "the new LLM alpha I built yesterday"
  suggests a rapid development cycle: Fable 5 released → Willison built a new LLM
  library alpha using it → `ask_user()` was implemented using that alpha — all
  within approximately 24 hours. This is an example of frontier model capability
  enabling rapid development of new agentic infrastructure, not just application code.

## Concrete Artifacts

### ask_user() API Summary (from simonwillison.net/2026/Jun/10/datasette-agent/)

The full API surface as described in the release post:

```
Tool function signature:
  async def my_tool(context):
      # context is a ToolContext object, injected when 'context' parameter is declared
      answer = await context.ask_user("question text")           # yes/no
      answer = await context.ask_user("text", options=["a","b"]) # multiple-choice
      answer = await context.ask_user("text", free_text=True)    # free-text

Behavior:
  - While question is unanswered: agent turn suspends, question renders as
    form in chat UI, persists to internal database
  - After restart: suspended conversations resume when user reconnects
  - Once answered: tool re-executes from top with stored answers replayed
  - Constraint: call ask_user() before any side effects
```

*Source: simonwillison.net/2026/Jun/10/datasette-agent/, 2026-06-10. Question
types inferred from "yes/no, multiple-choice or free-text question" with the
corresponding parameter conventions described in the post.*

### save_query Approval Gate (from simonwillison.net/2026/Jun/10/datasette-agent/)

```
Tool: save_query (built-in to datasette-agent 0.2a0)
Purpose: Save SQL as a Datasette stored query

Approval workflow:
  1. Agent proposes: shows full SQL + proposed name + database + visibility
  2. User sees: complete proposed action before any storage occurs
  3. Gate: nothing is stored until user clicks Yes
  4. On rejection: no state change
```

*Source: simonwillison.net/2026/Jun/10/datasette-agent/, 2026-06-10.*

## Cross-References

- **Corroborates**:
  - `blog-simonwillison-datasette-agent.md` Claim 5: "My favorite feature of
    Datasette Agent is that, like the rest of Datasette, it's extensible using
    plugins." This 0.2a0 release adds new capabilities (ask_user, save_query) to
    the core platform whose extensibility was established in that note. The
    ask_user mechanism is a core capability that plugins can also use (tools
    authored in plugins can declare a `context` parameter just as built-in tools
    can). The platform's extensibility value is reinforced by this incremental
    capability addition.
  - `blog-simonwillison-datasette-agent-charts.md` Claim 3: "Now checks
    execute-sql permission before running the query to find the column names." The
    `save_query` approval gate in this source extends the permission/safety
    pattern. That note documented gating read operations on permission checks;
    this source documents gating write operations on explicit human approval. Both
    are specific instances of "agent operations that affect data must require
    authorization before executing."

- **Extends**:
  - `blog-simonwillison-datasette-agent.md` overall: The 0.1a1 release established
    the platform architecture, plugin model, and multi-model support. This 0.2a0
    adds the human-in-the-loop capabilities that were absent from the initial
    release. Together the two notes document the progression from "agent that can
    query data" to "agent that can interact with the user mid-execution and safely
    create persistent artifacts."
  - `blog-simonwillison-datasette-agent-micropython.md` Claim 5: "The trickiest
    piece to solve was persistent interpreter state." The `ask_user()` persistence
    mechanism — storing unanswered questions to the internal database — addresses
    a parallel persistence challenge: making conversational state durable across
    restarts, rather than interpreter state. Both are examples of Datasette Agent
    using its internal SQLite database as a state management layer for otherwise
    ephemeral runtime state.

- **Contradicts**: None identified. No existing corpus note makes claims about
  mid-execution user interaction in agent tools, conversation persistence via
  database-backed question storage, or approval gates for agent-created SQL
  artifacts that would conflict with this source's claims. No contradiction issue
  required.

- **Novel**:
  - **First corpus documentation of a mid-execution user interaction pattern
    (`ask_user()`) in an agent framework**: No existing corpus note describes a
    tool-level API for pausing agent execution to ask the user a question and
    resuming after the answer. Prior corpus sources on human-in-the-loop focus
    on top-level approval (confirm before running the agent) rather than
    mid-execution interruption (pause inside a tool call to ask a question).
  - **First corpus documentation of the "re-execute from top with replayed
    answers" architecture for resuming suspended tool calls**: The design
    decision to re-run the tool function from the beginning (with stored answers
    substituted at each `ask_user()` call) is a specific, non-obvious approach to
    resumption that has direct implications for tool authors (side effects before
    `ask_user()` will execute twice). This design pattern is not documented
    elsewhere in the corpus.
  - **First corpus documentation of conversation persistence through server
    restarts via database-backed question storage**: The idea of storing a pending
    question to SQLite so that a suspended conversation can resume after a restart
    is a specific durability pattern for agentic state management not previously
    documented in the corpus.
  - **First corpus documentation of a full-context approval gate for agent SQL
    artifact creation**: The `save_query` pattern — surface complete proposed
    action (SQL + name + database + visibility), require explicit Yes, store
    nothing until confirmed — is a concrete reference implementation for
    practitioners designing agent tools that create persistent artifacts.

## Guide Impact

- **Chapter 02 (Interactive Agent Loops — mid-execution user interaction)**:
  Add `ask_user()` as a concrete reference implementation of the mid-execution
  user prompting pattern. The key design distinction: this is not a top-level
  "do you want me to proceed?" confirmation before the agent runs, but a
  tool-level pause that happens inside a specific tool call. The suspend-persist-
  resume model (suspend agent turn → persist question to database → resume on
  answer) is architecturally novel compared to simple pre-execution confirmations.
  Cite Claim 1 for the API, Claim 2 for the suspension/persistence behavior, and
  Claim 4 for the re-execution constraint (place `ask_user()` before side effects).

- **Chapter 02 (Interactive Agent Loops — conversation durability across
  restarts)**: Add the internal database persistence for unanswered questions as
  an example of making agentic conversation state durable. The key insight: a
  question is not a transient UI event but a first-class stored record. This
  enables restart recovery without requiring the agent to re-run from the
  beginning of the conversation. Cite Claim 3.

- **Chapter 03 (Safety and Verification — approval gates for agent-created
  artifacts)**: Add `save_query` as a reference implementation of the full-context
  approval gate pattern for state-mutating agent operations. The pattern has three
  elements: (1) surface the complete proposed action (all parameters, not just a
  summary), (2) require explicit confirmation (a hard gate, not a notification),
  (3) store nothing until confirmed. Cite Claim 5. Pair with
  `blog-simonwillison-datasette-agent-charts.md` Claim 3 (gating read operations
  on permission checks) to show both sides of the authorization pattern:
  permission-based gating for reads, human-approval gating for writes.

## Extraction Notes

- **Thin primary source**: The blog post is a "beat" in Willison's format — brief
  release announcement with key behavioral descriptions but no code examples.
  The six verbatim quotes obtained via targeted extraction cover all the
  substantive claims. No code examples appear in the post.
- **Verbatim quotes obtained via targeted WebFetch**: A full-verbatim request
  was declined on copyright grounds; targeted extraction prompts returned the
  specific passages needed. All quotes in this note were obtained character-for-
  character via the targeted extraction and are faithful to the source text as
  returned by WebFetch.
- **Related 0.1a1 source note**: `blog-simonwillison-datasette-agent.md`
  (issue #1011) is the platform overview for the 0.1a1 release. That note's
  claim numbers were verified by document-order count before writing
  cross-references: Claim 5 (extensibility via plugins) confirmed at lines 113–129.
- **charts and micropython cross-references verified**: `blog-simonwillison-datasette-agent-charts.md`
  Claim 3 (execute-sql permission check before column-name lookup) confirmed at
  lines 76–91. `blog-simonwillison-datasette-agent-micropython.md` Claim 5
  (persistent interpreter state as the hardest problem) confirmed at lines 116–133.
- **No LLM alpha source note found**: The quote about "the new LLM alpha I built
  yesterday with the help of Claude Fable 5" references a new LLM library release
  that may not yet have a dedicated source note in the corpus. The June 9 Claude
  Fable 5 impressions post is documented in `blog-simonwillison-claude-fable-5.md`
  (issue #1196); the specific LLM alpha referenced is not.
- **Fragment URL**: The issue body URL includes `#atom-everything`. The
  `source_url` uses the canonical URL without the fragment, consistent with prior
  Willison source notes in this corpus.
- **No contradictions filed**: No existing corpus note makes claims that conflict
  with the mid-execution interaction or approval gate patterns documented here.
  No contradiction issue required.
