---
source_url: https://docs.litellm.ai/docs/claude_code_compatibility
source_type: docs
title: "Claude Code × LiteLLM compatibility matrix — LiteLLM Documentation"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-09-24)
date_extracted: 2026-09-24
last_checked: 2026-09-24
status: current
confidence_overall: emerging
issue: "#1444"
---

# Claude Code × LiteLLM compatibility matrix (LiteLLM Docs)

> LiteLLM's continuously-regenerated compatibility matrix machine-tests the
> Claude Code CLI against the newest final LiteLLM release across nine provider
> columns (Anthropic, Bedrock Invoke/Converse, Vertex AI, Azure Foundry,
> openai, azure_openai, bedrock_mantle, vertex_ai_gpt) with Haiku 4.5 /
> Sonnet 4.6 / Opus 4.7 in parallel, and is the first corpus source that
> answers *which Claude Code features silently vary by gateway route* — a
> version-pinned, four-state (pass / fail / untested / n/a) parity map whose
> methodology (three-tier gate, daily regeneration, committed JSON + harness
> path) is a transferable release-engineering pattern for an automated,
> published compatibility gate.

## Source Context

- **Type**: docs (single-page LiteLLM gateway compatibility reference, part of
  the `litellm-docs` site-crawl seed; site breadcrumb "AI Tools → Claude Code →
  Claude Code Compatibility"). The page is auto-discovered and
  auto-discovered-by-site-crawl per the issue body.
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  The matrix is **machine-generated output**, not marketing prose: the page
  states it is regenerated daily by an automated populator that runs the real
  Claude Code CLI against the newest final LiteLLM release, and it publishes
  the harness path (`tests/e2e/claude_code/cron_vm/`) and backing JSON
  (`src/data/compatibility-matrix.json`) so the artifact is reproducible.
  Caveat carried per the Prospector: LiteLLM runs the harness against its own
  gateway, so this is vendor-generated machine output, not independent
  third-party validation — and the page is version-pinned (see Claims 2, 9).
- **Scope**: 16 features × 9 provider columns of Claude Code feature parity
  when Claude Code is pointed at a LiteLLM gateway, plus the methodology,
  legend, version stamp, and provenance. Does **not** cover: failure
  narratives (the current snapshot has zero failing cells, Claim 4), latency,
  cost, rate limits, or any per-cell upstream error text (that text exists only
  as hover on failed cells, and there are none in the current snapshot). The
  backing JSON (`docs.litellm.ai/src/data/compatibility-matrix.json` and the
  `BerriAI/litellm` raw path) both 404, so extraction is from the rendered
  table per the Prospector.

## Extracted Claims

### Claim 1: The page is a machine-regenerated compatibility matrix — an automated populator runs the Claude Code CLI against the newest final LiteLLM release across each supported provider, with Haiku 4.5, Sonnet 4.6, and Opus 4.7 in parallel, and a cell goes green only if all three model tiers pass
- **Evidence**: The page's intro sentence states the regeneration cadence, the
  harness, and the three-model-tier gate; the three-tier gate makes a green cell
  an *all-tiers* claim, not a single-model result.
- **Confidence**: settled (the methodology is the page's own description and is
  machine-checkable via the published harness/JSON paths in Claim 10)
- **Quote**: "This table is regenerated daily by an automated populator that runs the Claude Code CLI against the newest final LiteLLM release (the latest bare `vX.Y.Z` tag) across each supported provider, with Haiku 4.5, Sonnet 4.6, and Opus 4.7 in parallel. A cell goes green only if all three model tiers pass."
- **Our assessment**: This is the transferable design contribution, not the
  checkmarks themselves: a daily, CLI-driven, three-model-tier compatibility
  gate published as documentation. The "all three tiers must pass" rule is what
  makes each green cell meaningful — it collapses model-specific flakiness into
  a single per-(feature, provider) verdict.

### Claim 2: The matrix is a point-in-time snapshot pinned to one gateway version, one Claude Code version, and one generation time — `litellm v1.102.0`, `claude code 2.1.228`, generated `2026-09-23T06:11:56Z` — so no cell is a durable support claim
- **Evidence**: The version stamp rendered directly above the table at extract
  time (the page regenerates daily, so the stamp will advance).
- **Confidence**: settled (observed stamp on the fetched page; the drift
  property is the page's own "regenerated daily" statement from Claim 1)
- **Quote**: "litellm `v1.102.0` claude code `2.1.228` generated `2026-09-23T06:11:56Z`"
- **Our assessment**: The triage's core caveat, carried forward: any cell this
  note cites is a snapshot against `v1.102.0` / `2.1.228` as of
  `2026-09-23T06:11:56Z`. The Smith must not cite a cell as permanently true —
  the version stamp (and "regenerated daily") must travel with any per-cell
  claim. The stamp also makes the matrix evidential for *that* release pair
  only: a gateway upgrade can silently change a green to a fail.

### Claim 3: Cell semantics are four-state, not pass/fail — ✅ all three model tiers pass, ❌ at least one tier failed (hover for the upstream error), — no test ran for this combination, n/a not applicable (provider doesn't expose the feature; hover for the reason) — so an empty/untested cell must not be read as "broken"
- **Evidence**: The legend table on the page defines all four glyphs.
- **Confidence**: settled (verbatim legend; this is the page's explicit reading
  contract)
- **Quote**: "All three model tiers pass for this `(feature, provider)` cell." / "At least one model tier failed. Hover for the upstream error." / "No test ran for this combination." / "Not applicable (e.g. provider doesn't expose this feature). Hover for the reason."
- **Our assessment**: The distinction between "untested" (—) and "not
  applicable" (n/a) — and between both and "failed" (❌) — is exactly what a
  reader needs to avoid misreading. In this corpus, the operational version of
  the trap is: a row full of `—` says *nothing* about support; only a green ✅
  is a tested claim, and only red ❌ is a tested failure. This legend is the
  disciplined-reading counterpart to the corpus's standing "✅ = surface
  support, not per-provider parity" caveat — here the matrix *is* the per-cell
  parity evidence, with the four states making coverage gaps visible as gaps.

### Claim 4: The current snapshot has zero failing cells — no `(feature, provider)` cell is ❌; the only ❌ glyph on the page is the legend swatch — so there is no upstream error text to harvest in this snapshot
- **Evidence**: Full read of the rendered table this session (all 16 rows × 9
  columns in the HTML fetch): every cell is ✅, —, or n/a; no cell carries the
  failing state.
- **Confidence**: settled (observed table state as of the claimed generation
  stamp)
- **Quote**: (no failing-cell text exists to quote; the ❌ row of the legend is
  the only occurrence: "At least one model tier failed. Hover for the upstream error.")
- **Our assessment**: Confirms the Prospector's verification ("no failing
  cells, so there is **no failure-report content here**"). This makes the page
  a parity map rather than a failure narrative: the value is the *coverage
  surface* (which features ran green where), not a postmortem. Snapshot-bound —
  the daily regeneration means the zero-fail state is not a guarantee for the
  next day's run.

### Claim 5: The twelve core features are green across the five principal routes — Anthropic, Bedrock (Invoke), Bedrock (Converse), Vertex AI, and Azure (Foundry) — while three of the nine columns never ran any test (openai and bedrock_mantle are entirely `—`; azure_openai ran only the core chat surface and is `—` on every other feature)
- **Evidence**: The rendered table: rows "Basic messaging (non-streaming)",
  "Basic messaging (streaming)", "Tool use", "Prompt caching (5m TTL)",
  "Vision", "Thinking", "Tool use (streaming / fine-grained)", "Extended
  thinking + tool use", "PDF document input", "Prompt caching (1h TTL)",
  "Web search (server tool)", and "Structured outputs" are all
  ✅ on Anthropic / Bedrock (Invoke) / Bedrock (Converse) / Vertex AI /
  Azure (Foundry); the openai and bedrock_mantle columns carry `—` in every
  row; azure_openai is ✅ only on basic messaging (both) and tool use (both /
  fine-grained) and `—` elsewhere.
- **Confidence**: settled (observed table, snapshot-bound)
- **Quote**: (feature-row cells; see the full matrix in Concrete Artifacts)
- **Our assessment**: For a Claude Code operator the headline is: all twelve
  features tested are green on every principal route — except the `openai`
  family, whose columns are entirely untested. Critically, `openai` — the
  column whose zero tests include the Responses-translation surface Claude Code
  can also be routed through — tells us nothing about
  actual OpenRouter/openai-backend behavior; it is a coverage gap, not a pass.
  These are the "silently missing depending on route" facts at the feature
  level, and they are exactly why the four-state legend matters.

### Claim 6: `count_tokens` endpoint parity is partial — green only on Anthropic, Bedrock (Invoke), Bedrock (Converse), and Azure (Foundry); `—` (no test ran) on Vertex AI, openai, azure_openai, bedrock_mantle, and vertex_ai_gpt — supplying the "which providers" answer for the corpus's count_tokens note
- **Evidence**: The "count_tokens endpoint" row (see Concrete Artifacts).
- **Confidence**: settled (observed cell states, snapshot-bound)
- **Quote**: (row cells; no prose quote exists — this is table data)
- **Our assessment**: This is the *provider-dimension* answer the triage asked
  for and the corpus's `docs-litellm-anthropic-count-tokens` note does not
  have: the counting endpoint's tested parity under the actual Claude Code CLI.
  Note the careful reading required — Vertex AI is `—` (untested), not ❌, so
  it is *not* documented as broken there; it is simply outside the test set for
  this snapshot.

### Claim 7: `Tool search (MCP discovery)` parity is green only on Anthropic, Bedrock (Invoke), and Bedrock (Converse) — every other column is `—`, so the MCP tool-search cost lever has machine-tested Claude Code parity on exactly three routes
- **Evidence**: The "Tool search (MCP discovery)" row (see Concrete Artifacts);
  the cost-lever context is `blog-litellm-save-claude-code-costs` Claim 4.
- **Confidence**: settled (observed cell states, snapshot-bound)
- **Quote**: (row cells; no prose quote exists)
- **Our assessment**: The triage's "MCP tool search (token-cost lever) is green
  only on Anthropic + two Bedrock columns" reading is confirmed. The three
  columns are exactly the Anthropic-wire-native family; for a team that adopts
  MCP tool search (Claim 4 of the save-costs note) as a token-reduction lever,
  this matrix says the *tested* parity surface is those three routes — Azure
  Foundry, Vertex AI, and every other column are `—` (untested), not verified.

### Claim 8: `Native API passthrough` is green on Anthropic, Bedrock (Invoke), and Vertex AI, and structurally **n/a** on Bedrock (Converse) — Claude Code's Bedrock mode speaks only the InvokeModel wire (`/model/{id}/invoke-with-response-stream`) and has no Converse-wire client, a documented instance where the client constrains the gateway surface
- **Evidence**: The "Native API passthrough" row plus the hover reason on the
  Bedrock (Converse) n/a cell.
- **Confidence**: settled (observed cells plus the cell's own verbatim tooltip)
- **Quote**: "Claude Code's bedrock mode speaks only the InvokeModel wire (/model/{id}/invoke-with-response-stream); it has no Converse-wire client, so there is no Claude Code surface for Converse passthrough."
- **Our assessment**: The one non-coverage tooltip with real mechanism: the
  n/a is not a gap in LiteLLM's harness — it is structurally insoluble from the
  client side. A Claude Code binary pointed at a gateway in Bedrock mode will
  never exercise a Converse-format passthrough because the CLI itself only
  speaks the Invoke wire. This is a concrete "the client constrains the gateway
  surface" datum (and the corroboration the corpus's Bedrock /converse note
  could not offer, see Cross-References). Operators considering a
  Converse-passthrough route for Claude Code get a first-party reason it is
  not reachable.

### Claim 9: `Long context (1M)` is `—` (no test ran) on every provider column, including Anthropic — a known-untested cell, not a supported/unsupported claim
- **Evidence**: The "Long context (1M)" row: all nine columns carry the no-test
  state.
- **Confidence**: settled (observed table state)
- **Quote**: (row cells; "no test ran for this combination" is the cell's
  hover text)
- **Our assessment**: The Prospector flagged this explicitly, and it holds in
  the fetched snapshot. Even Anthropic — native home of 1M-context — carries
  `—`, so the matrix makes **no** 1M-context claim in either direction. Anyone
  using this page to source a "1M context works through a LiteLLM gateway"
  statement has no basis here.

### Claim 10: The page publishes its own reproducibility provenance — the matrix JSON lives at `src/data/compatibility-matrix.json` and the populator at `tests/e2e/claude_code/cron_vm/` on the main repo — making the matrix a machine-checked, published artifact rather than a hand-maintained support table
- **Evidence**: The "Source" section of the page links both paths.
- **Confidence**: settled (explicit provenance; links resolve to the specified
  repo paths)
- **Quote**: "The matrix JSON lives at `src/data/compatibility-matrix.json`. The populator is in `tests/e2e/claude_code/cron_vm/` on the main repo."
- **Our assessment**: This is what elevates the page above a vendor support
  table for the guide: the artifact is reproducible and refreshable. The guide
  can cite "a machine-checked, daily-regenerated parity artifact (harness at
  `tests/e2e/claude_code/cron_vm/`, data at
  `src/data/compatibility-matrix.json`)" rather than "LiteLLM says so" — with
  the vendor-provenance caveat that the harness is LiteLLM's own (Claim 1 +
  Source Context).

### Claim 11: The `vertex_ai_gpt` column is n/a across the four Anthropic-wire chat features because GCP Vertex AI does not offer OpenAI's closed-weight GPT-5.6 family (Sol / Terra / Luna) — Model Garden carries only open-weight `gpt-oss` MaaS models — and the vendor marks the column to convert to live tests if Google adds those models
- **Evidence**: The hover reason on the four n/a cells in the `vertex_ai_gpt`
  column ("Basic messaging (non-streaming)", "Basic messaging (streaming)",
  "Tool use", "Tool use (streaming / fine-grained)"); the same reason text is
  applied to all four.
- **Confidence**: settled (verbatim cell tooltip)
- **Quote**: "GCP Vertex AI does not offer OpenAI's closed-weight GPT-5.6 family (Sol / Terra / Luna); Model Garden carries only the open-weight gpt-oss MaaS models. Convert this column's cells to live tests if Google adds the GPT-5.6 models."
- **Our assessment**: A second structural n/a, this one provider-side: the
  `vertex_ai_gpt` route cannot host the OpenAI-wire models the matrix's harness
  would test, so its exclusion is "not applicable," not untested. The vendor's
  conditional ("Convert ... to live tests if Google adds the GPT-5.6 models")
  is a designed-in future-proofing behavior worth noting as part of the matrix
  methodology's handling of provider-capability changes.

## Concrete Artifacts

All artifacts verbatim from https://docs.litellm.ai/docs/claude_code_compatibility
(fetched 2026-09-24; snapshot stamp `litellm v1.102.0` / `claude code 2.1.228` /
generated `2026-09-23T06:11:56Z`). Column order: Anthropic, Bedrock (Invoke),
Bedrock (Converse), Vertex AI, Azure (Foundry), openai, azure_openai,
bedrock_mantle, vertex_ai_gpt.

### Version stamp (verbatim)

> litellm `v1.102.0` claude code `2.1.228` generated `2026-09-23T06:11:56Z`

### Compatibility matrix (rendered from the page's feature table, verbatim cells)

| Feature | Anthropic | Bedrock (Invoke) | Bedrock (Converse) | Vertex AI | Azure (Foundry) | openai | azure_openai | bedrock_mantle | vertex_ai_gpt |
|---|---|---|---|---|---|---|---|---|---|
| Basic messaging (non-streaming) | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | — | n/a |
| Basic messaging (streaming) | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | — | n/a |
| Tool use | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | — | n/a |
| Prompt caching (5m TTL) | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — | — |
| Vision | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — | — |
| Thinking | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — | — |
| Tool use (streaming / fine-grained) | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | — | n/a |
| Extended thinking + tool use | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — | — |
| PDF document input | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — | — |
| Prompt caching (1h TTL) | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — | — |
| Web search (server tool) | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — | — |
| Structured outputs | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — | — |
| count_tokens endpoint | ✅ | ✅ | ✅ | — | ✅ | — | — | — | — |
| Tool search (MCP discovery) | ✅ | ✅ | ✅ | — | — | — | — | — | — |
| Native API passthrough | ✅ | ✅ | n/a | ✅ | — | — | — | — | — |
| Long context (1M) | — | — | — | — | — | — | — | — | — |

### Legend (verbatim)

| Glyph | Meaning |
|---|---|
| ✅ | All three model tiers pass for this `(feature, provider)` cell. |
| ❌ | At least one model tier failed. Hover for the upstream error. |
| — | No test ran for this combination. |
| n/a | Not applicable (e.g. provider doesn't expose this feature). Hover for the reason. |

### n/a cell hover reasons (verbatim tooltips)

- Bedrock (Converse) / Native API passthrough:
  "Claude Code's bedrock mode speaks only the InvokeModel wire (/model/{id}/invoke-with-response-stream); it has no Converse-wire client, so there is no Claude Code surface for Converse passthrough."
- `vertex_ai_gpt` / the four Anthropic-wire chat features:
  "GCP Vertex AI does not offer OpenAI's closed-weight GPT-5.6 family (Sol / Terra / Luna); Model Garden carries only the open-weight gpt-oss MaaS models. Convert this column's cells to live tests if Google adds the GPT-5.6 models."

### Provenance (verbatim)

> The matrix JSON lives at `src/data/compatibility-matrix.json`. The populator is in `tests/e2e/claude_code/cron_vm/` on the main repo.

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every path
listed in the candidates file is addressed):

- `source-notes/docs-litellm-batches-api.md` — **Dismissed**: batch input-file
  TPM/RPM limiting and enqueued-token reservations (its Claims 1-5); a
  rate-limit surface with no Claude Code feature-parity content.
- `source-notes/docs-litellm-bedrock-invoke.md` — **Cited** (see Corroborates
  and Extends): the `/invoke` passthrough route family this matrix machine-tests
  in its "Bedrock (Invoke)" column.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Dismissed**: A2A
  session cost/iteration caps; a different gateway surface, nothing on Claude
  Code feature parity.
- `source-notes/docs-litellm-bedrock-converse.md` — **Cited** (see Corroborates
  and Extends): the `/converse` route family that Claim 8 here marks n/a for
  native passthrough.
- `source-notes/docs-langfuse-mcp-server.md` — **Dismissed**: docs-as-MCP
  coding-agent intake; unrelated to provider feature parity.
- `source-notes/docs-litellm-audio-transcription.md` — **Dismissed**:
  transcription-endpoint support matrix (its Claims 5-6 share the
  "Feature/Supported/Notes" genre but cover a non-chat endpoint); the
  compatibility matrix is the Claude Code CLI parity map, not the same matrix
  genre's endpoint surface.
- `source-notes/blog-litellm-save-claude-code-costs.md` — **Cited** (see
  Corroborates and Extends): MCP tool search and prompt-caching as Claude Code
  cost levers; this matrix supplies their per-provider parity surface.
- `source-notes/blog-litellm-auto-router-v2.md` — **Dismissed**: routing-flavor
  collapse and LLM classifier; no parity-matrix or Claude Code feature content.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **Dismissed**: A2A
  flat/token per-agent cost ledger; unrelated.
- `source-notes/docs-litellm-helicone-integration.md` — **Dismissed**: Helicone
  telemetry integration (in-path vs `success_callback`); no feature-parity
  content.

**Primary cross-references (verified per MINER §4b — cited claims re-read in
the cited notes before writing):**

- **Corroborates**:
  - `source-notes/docs-litellm-anthropic-count-tokens.md` **Claim 1** (the
    `/v1/messages/count_tokens` endpoint is a pre-flight, Anthropic-format
    counting call). The matrix's "count_tokens endpoint" row (Claim 6 here)
    answers that note's open provider question at the Claude Code CLI level:
    the endpoint's *tested* parity is green on Anthropic, Bedrock (Invoke),
    Bedrock (Converse), and Azure (Foundry), and untested (`—`) on Vertex AI
    and the other four columns. Same endpoint, two evidence classes: the
    count-tokens note documents the wire contract; this matrix machine-tests
    the Claude Code client against it per provider. (Verified in full read.)
  - `source-notes/docs-litellm-bedrock-invoke.md` **Claim 1** and
    `source-notes/docs-litellm-bedrock-converse.md` **Claim 1** — both document
    the `/bedrock/model/{model_name}/invoke` and `/converse` route surfaces on
    first-party pages. The matrix independently runs the real Claude Code CLI
    against "Bedrock (Invoke)" and "Bedrock (Converse)" and reports green across
    the core feature set, machine-testing the very surfaces those notes document
    as vendor routes. Claim 8 here adds the client-constraint detail the
    Converse note could not: Claude Code has no Converse-wire client, so Converse
    *passthrough* is structurally n/a. (Verified: both Claims 1 read in full.)
  - `source-notes/blog-litellm-save-claude-code-costs.md` **Claim 4** (MCP Tool
    Search collapses the full tool catalog to two virtual tools). The matrix's
    "Tool search (MCP discovery)" row (Claim 7 here) is the tested-parity
    surface for that lever: green on Anthropic, Bedrock (Invoke), Bedrock
    (Converse) only — so the cost lever's machine-tested Claude Code parity is
    exactly those three routes; every other column is untested. (Verified:
    Claim 4 read in full.)
  - `source-notes/docs-litellm-anthropic-unified.md` **Claim 2** — `/v1/messages`
    asserts a surface-support feature table ("all supported providers")
    *without* per-backend granularity; the matrix is precisely a per-provider
    parity map (Claude Code client × provider × feature), giving that note's
    "treat ✅ as surface support, not per-provider parity" reading a
    machine-generated, per-cell instantiation. Same stance, complementary
    evidence class. (Verified: Claim 2 read in full.)
  - `source-notes/blog-litellm-claude-fable-5-day-0.md` **Claim 12** — the
    vendor's "feature parity across backends" claim (rated `emerging` there);
    the matrix is a different, finer-grained evidence class for the
    Haiku/Sonnet/Opus tiers and shows parity is *not* total even in machine
    output (native passthrough n/a on Converse). Not a contradiction — the Fable
    note's claim concerns a different model set and is explicitly
    over-stated-by-its-own-author — but the pair should travel together so the
    Smith never cites "full parity across backends" without the per-cell caveat.
    (Verified: Claim 12 read in full.)
- **Contrasts** (same surface, different layer — not a contradiction):
  - `source-notes/docs-litellm-claude-code-context-management.md` **Claim 1**
    — the sibling Claude Code page (#1445) documents that `context_management`
    is routed natively vs polyfilled depending on target. That feature **is
    absent from this matrix's 16 rows** — the matrix does not (yet) test the
    context-management polyfill — so feature parity for that surface must come
    from that note, not this page. The two notes are complementary slices of the
    same "Claude Code × LiteLLM" surface: this one is the tested feature-parity
    map; that one is the runtime behavior of one specific feature's different
    routes. (Verified: Claim 1 read in full.)
- **Contradicts**: None filed (MINER §4a). Candidate tensions checked and
  resolved as non-contradictions: (1) the matrix shows `count_tokens` untested
  on Vertex AI while `docs-litellm-anthropic-count-tokens` documents the
  endpoint auto-routing to Vertex AI's counting API — a *coverage* delta
  (untested ≠ unsupported), not an opposing claim, and the two notes agree on
  the endpoint's existence; (2) the Fable 5 note's parity claim vs the matrix's
  per-cell gaps — conditioning/different-model, and the Fable note itself
  disclaims total parity; (3) `context_management` absent from the matrix vs
  present in the sibling note — complementary scope, both directions consistent.
  Verified against the open `contradiction`-labeled issues (#1408/#1352/#1338/
  #1322/#1307/#1150) and `CONTRADICTIONS.md` (no `C-NNN` entries): none touch
  this surface. No contradiction issue filed.
- **Extends**:
  - `source-notes/docs-litellm-anthropic-count-tokens.md` — extends with the
    provider-dimension parity datum the triage flagged: green on the four routes
    in Claim 6 here vs `—` on the rest, snapshot-pinned.
  - `source-notes/blog-litellm-save-claude-code-costs.md` **Claim 4** — extends
    the MCP tool-search cost lever with its tested-parity surface (Claim 7
    here); **Claim 3** (auto-injected `cache_control` markers) similarly gains a
    parity surface from the matrix's "Prompt caching (5m TTL)" / "Prompt caching
    (1h TTL)" rows (green on all five principal routes).
  - `source-notes/docs-litellm-bedrock-converse.md` — extends with the
    client-wire mechanism (Claim 8 here) explaining why Converse *passthrough*
    is n/a for Claude Code — a first-party answer to the Converse note's
    "no Converse statements" gap, at the client layer.
  - `source-notes/docs-litellm-anthropic-unified.md` **Claim 2** — operationalizes
    its "surface support ≠ per-provider parity" reading with a machine-generated
    parity map for the Claude Code client specifically.
- **Novel**: First corpus coverage of a **continuously-regenerated,
  machine-tested Claude Code feature-parity matrix.** Re-checked this session:
  `compatibility-matrix`, `claude_code_compatibility`, and the per-feature gap
  surface appear nowhere else in `source-notes/` or `guide/`. Specifically new:
  (1) the methodology (three-model-tier gate, daily regeneration, committed
  JSON + harness provenance) as a transferable release-engineering pattern
  (Claims 1, 10); (2) the four-state legend semantics — pass / fail / **untested
  vs n/a** — as a reading contract (Claim 3); (3) the feature-level gap surface
  for a Claude Code client: count_tokens (Claim 6), tool search (Claim 7),
  native passthrough with the Converse-wire client constraint (Claim 8), long
  context (1M) untested everywhere (Claim 9), and the openai / bedrock_mantle
  entirely-untested columns (Claim 5); (4) the version-pinning discipline for
  citing any cell (Claim 2).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability), "Provider parity in the shared forwarding
  path" (`guide/05-llm-ops-reliability.md:343-384`)**: The chapter's rule —
  "test the non-default provider — not just the one the change was written for"
  (:383-384) — is currently illustrated by one incident (the vLLM embedding
  regression). Add the compatibility matrix as a live, published companion to
  that rule: a per-(feature, provider) parity map for the Claude Code client,
  machine-tested daily against the nine columns [Claim 1, 5] [settled]. The
  four-state legend [Claim 3] [settled] is the chapter's missing
  careful-reading discipline at the parity-table level — an operator must not
  read `—` (no test ran) as "broken" nor n/a as "untested"; only ✅ is a tested
  claim and only ❌ a tested failure. Pair the chapter's existing per-backend
  conditioning-variable guidance (:304-325) with Claim 8's client-constraint
  datum: a Claude Code session on Bedrock speaks only the InvokeModel wire, so
  Converse-format passthrough is structurally unreachable from that client
  (:343-384).
- **Chapter 05, "Release engineering for LLM infrastructure"
  (`guide/05-llm-ops-reliability.md:7-122`)**: The staging-gated/live-API-test
  material documents how LiteLLM protects its own releases; the compatibility
  matrix is the *published output* form of the same discipline — a daily,
  automated compatibility gate that runs the real Claude Code CLI against the
  newest final release across every provider and ships the result (data at
  `src/data/compatibility-matrix.json`, harness at
  `tests/e2e/claude_code/cron_vm/`) as live docs [Claim 1, 10] [settled].
  Recommend the chapter add it as the worked example of an *automated,
  published compatibility gate rather than a hand-maintained support table*,
  carrying the vendor-provenance caveat (LiteLLM tests its own gateway) from
  this note's Source Context and the version-pinning rule from Claim 2 [settled]
  — the artifact is evidential *for the release pair it stamps* only.
- **Chapter 05 (usage-metering / model-enablement material)**: Where the chapter
  cites the `count_tokens` surface (via `docs-litellm-anthropic-count-tokens`)
  or the MCP tool-search cost lever (via `blog-litellm-save-claude-code-costs`),
  add the per-provider parity caveat from Claims 6-7 [settled, snapshot-bound]:
  `count_tokens` is machine-tested green only on Anthropic, Bedrock (Invoke),
  Bedrock (Converse), and Azure (Foundry), and tool search only on Anthropic +
  the two Bedrock columns — with the other columns *untested*, not verified.
- **Chapter 02 (Observability) — continuous verification as an observability
  artifact**: The matrix is a continuously-regenerated, version-stamped parity
  artifact an operator can consult (and re-check daily) before choosing a
  Bedrock / Vertex / Azure route over Anthropic direct for Claude Code [Claim 1,
  2, 5] [settled]. Recommend the chapter treat such published, regenerated
  compatibility artifacts as a first-class input to the pre-deployment parity
  check — with the standing "untested vs n/a vs failed" legend [Claim 3] as the
  reading contract, and with no 1M-context claim sourced from this page
  [Claim 9].

## Extraction Notes

- Source read in full via WebFetch in two passes (markdown and raw HTML) on the
  canonical URL (`https://docs.litellm.ai/docs/claude_code_compatibility`,
  HTTP 200, no paywall). The HTML pass was required to capture the n/a-cell
  hover tooltips, which do not render in the markdown transform; both passes
  agree on every cell state. Version stamp on the fetched page:
  `litellm v1.102.0` / `claude code 2.1.228` / generated `2026-09-23T06:11:56Z`.
- The Prospector's triage comment states the page renders 75 ✅ cells; my count
  of the fetched table is **70** ✅ (60 across the twelve all-green rows, plus 4
  count_tokens, 3 tool-search, 3 native-passthrough), zero ❌, and five n/a
  cells. The exact count is snapshot-dependent and I record mine rather than
  repeating the triage figure; the load-bearing facts (no failing cells; which
  features are green on which columns) are identical across both readings.
- No sub-pages followed: the page is self-contained (matrix + legend + source),
  and the Prospector verified the backing JSON is not fetchable
  (`docs.litellm.ai/src/data/compatibility-matrix.json` and the `BerriAI/litellm`
  raw path both 404), so extraction is from the rendered table as instructed.
- All `Quote` fields and Concrete Artifacts are character-for-character from the
  fetched page text or cell tooltips; table cells are quoted as single cells;
  the version stamp is quoted as it renders on the page. No splicing across
  non-adjacent sentences; where a claim is table data rather than prose ("no
  prose quote exists") the cell states are given in Concrete Artifacts instead
  of a fabricated quote.
- Cross-reference verification (MINER §4b) re-read the cited claims before
  writing: `docs-litellm-anthropic-count-tokens.md` (Claim 1),
  `docs-litellm-bedrock-invoke.md` (Claim 1), `docs-litellm-bedrock-converse.md`
  (Claim 1), `blog-litellm-save-claude-code-costs.md` (Claims 3, 4),
  `blog-litellm-claude-fable-5-day-0.md` (Claim 12),
  `docs-litellm-claude-code-context-management.md` (Claim 1), and
  `docs-litellm-anthropic-unified.md` (Claim 2). All numbered claims verified in
  full text; no claim numbers invented.
- No contradiction issue filed (MINER §4a): the candidate tensions resolve as
  coverage deltas / conditioning variables / complementary scope (see
  Cross-References → Contradicts). Verified the open `contradiction`-labeled
  issues (#1408, #1352, #1338, #1322, #1307, #1150) and `CONTRADICTIONS.md`
  (no `C-NNN` entries) — none cover this surface.
- `confidence_overall` set to `emerging`: the version-pinned cell values, the
  legend, the version stamp, and the provenance (Claims 1-5, 8, 9, 10, 11) are
  settled as *observed snapshot data*, but the whole artifact is
  vendor-generated machine output (no independent third-party validation), it
  regenerates daily (every cell claim is therefore snapshot-bound), and the
  highest-value synthesis (the per-feature gap surface for a gateway operator,
  the four-state reading contract, the client-constraint mechanism) is the
  Miner's reading of that documented surface. Consistent with the sibling
  LiteLLM docs notes (#1381, #1382, #1390, #1416, #1417, #1445).
- `date_published` unknown (undated living docs); `date_extracted` and
  `last_checked` both 2026-09-24 (UTC). `miner-related-notes.md` was read for
  candidates and left uncommitted.
- Live trial #571 (OpenCode Action, Zen free `big-pickle` backend) —
  production-shaped drain for issue #1444.