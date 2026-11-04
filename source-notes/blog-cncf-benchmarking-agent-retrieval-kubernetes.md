---
source_url: https://www.cncf.io/blog/2026/05/08/benchmarking-ai-agent-retrieval-strategies-on-kubernetes-bug-fixes
source_type: blog-post
title: "Benchmarking AI agent retrieval strategies on Kubernetes bug fixes"
author: Brandon Foley
date_published: 2026-05-08
date_extracted: 2026-11-03
last_checked: 2026-11-03
status: current
confidence_overall: emerging
issue: "#2010"
---

# Benchmarking AI agent retrieval strategies on Kubernetes bug fixes

> A first-person controlled benchmark of RAG-only, hybrid RAG+local, and
> local-only coding agents on nine real Kubernetes PRs: retrieval changes how
> agents *find* code but not how they *reason* about it, scope discovery is the
> dominant failure mode, and call count — not token volume — drives cost and
> latency.

## Source Context

- **Type**: blog-post (CNCF Community Post; first-person empirical benchmark)
- **Author credibility**: Brandon Foley, writing as a practitioner who uses
  coding agents in his daily engineering workflow. The post names its full
  harness — Claude Opus 4.6 via OpenClaw, KAITO RAG Engine (Qdrant) indexing
  `kubernetes/kubernetes` at HEAD, isolated subagent sessions, April 2026 — and
  is candid about the limits of its own ground truth. It is not vendor
  marketing: the author's headline result (retrieval does not fix reasoning)
  argues against the value of the RAG tooling in the experiment. Evidence is
  still self-run and self-graded with no external replication.
- **Scope**: Covers a three-arm retrieval comparison on nine in-flight Kubernetes
  bug-fix PRs (kubelet, scheduler, networking, storage, apps), per-PR wall-clock
  timing, aggregate token/call economics, a five-dimension diff-grading rubric,
  a failure-mode taxonomy (local-not-systemic fixes, scope discovery, add-over-
  reuse), issue quality as a variance lever, and a caveat about coding skills.
  It does **not** cover SRE incident response, multi-model comparisons, repeated
  trials, or any statistical treatment of the n=9 sample.

## Extracted Claims

### Claim 1: The author's initial assumption — that finding the right code is the hard part — did not hold; agents that surfaced the right files still produced fixes that were locally plausible but globally incorrect
- **Evidence**: The opening narrative contrast between the stated hypothesis
  ("a model that finds the right code should be able to generate the right fix")
  and the observed failures across the benchmark.
- **Confidence**: emerging (directional finding from a single author-run study)
- **Quote**: "That assumption didn’t fully hold. Even when agents surfaced the right files, they often failed to connect changes across them, misidentified the true scope of the issue, or produced fixes that were locally plausible but globally incorrect. The bottleneck wasn’t just finding code, it was reasoning over it in context."
- **Our assessment**: This is the source's thesis and the reason it matters for
  the guide: it separates *discovery* from *reasoning over discovered context*.
  The claim is qualitative, but Claims 7-9 give concrete PR instances behind it,
  and Claim 6 shows the cost consequence. Treat it as an emerging finding that
  should be tested on your own repo rather than a settled law.

### Claim 2: The benchmark varied exactly one independent variable — how the agent could see code — while holding the model, timeout, output format, and session isolation constant, and gave the agent only the issue description (no PR body or diff leakage)
- **Evidence**: The "setup" section's three configuration definitions and its
  explicit control statement.
- **Confidence**: emerging (method is clearly stated and reproducible in shape;
  no harness code or prompts are published)
- **Quote**: "Each agent ran in a completely isolated session. Same model (Claude Opus 4.6), same timeout (5 minutes), same output format. The only variable was how they could see code."
- **Our assessment**: The control design is the most reusable artifact in the
  post. Giving the agent only the issue description is what prevents the PR diff
  from leaking the answer — the same leakage hazard an eval designer has to
  actively close. The caveat is that "same model" and "same timeout" are stated
  but the system prompts are not published, so exact reproduction is not
  possible from the post alone.

### Claim 3: The three configurations were RAG-only (KAITO/Qdrant hybrid BM25 + embedding retrieval over an indexed copy, no local files or web), hybrid (same index plus a full local clone, RAG-first then local reads), and local-only (full clone, grep/find/cat, no RAG or web)
- **Evidence**: The three-arm definition list, including the retrieval stack
  (KAITO RAG Engine with Qdrant, BM25 + semantic search, merged and ranked).
- **Confidence**: emerging (concrete tooling named; configuration details are
  descriptive, not a published config)
- **Quote**: "**RAG Only**: Hybrid retrieval over an indexed copy of the Kubernetes codebase via KAITO RAG Engine (Qdrant), combining BM25 for keyword matching with embedding based semantic search. KAITO also provides an auto-indexing controller which is perfect for indexing huge git repos with the capability of incremental indexing."
- **Our assessment**: The arm definitions make the result interpretable: the
  comparison is not "RAG vs no RAG" in the abstract but "indexed snippets only"
  vs "index + filesystem" vs "filesystem only." The auto-indexing controller
  detail matters for anyone copying the setup to a large, moving repo — keeping
  the index current is itself an operational system, which is the same
  maintenance argument the author later makes about skills (Claim 12).

### Claim 4: RAG and hybrid agents had to be *prompted* to query RAG before fixing, because early experiments showed hybrid agents would skip retrieval entirely when the issue named specific filenames
- **Evidence**: The "One critical constraint" paragraph after the setup.
- **Confidence**: emerging (observed in the author's own pilot runs; no counts)
- **Quote**: "One critical constraint: the RAG and Hybrid agents were prompted to make RAG queries before producing any fix. Early experiments showed that without this mandate, hybrid agents would skip RAG entirely when the issue mentioned specific filenames, defeating the whole point of the comparison."
- **Our assessment**: A high-value operational detail: agents route around
  retrieval when the issue text already anchors the search. This means a
  "hybrid" architecture's behavior depends on an enforcement prompt, not just on
  tool availability — a system that *can* retrieve is not a system that *will*
  retrieve. It also explains why the hybrid arm is slower (Claim 5): the mandate
  adds a phase that the agent would otherwise skip.

### Claim 5: RAG-only was consistently fastest (1m16s average), while hybrid was slowest (2m25s) and local-only matched hybrid (2m24s) for different reasons; retrieval reduces exploration overhead but also reduces structural exploration depth
- **Evidence**: The per-PR timing table and the three explanatory paragraphs
  that follow it.
- **Confidence**: emerging (single-run wall-clock numbers; no repeated trials or
  variance reported)
- **Quote**: "RAG is consistently the fastest. It doesn’t read files, navigate directories, or wait for grep results. It asks the index, gets snippets, and generates. Average wall-clock: **1 minute 16 seconds**. This suggests retrieval reduces exploration overhead but also reduces structural exploration depth."
- **Our assessment**: The directional comparison is useful, but the absolute
  times are single runs with a hard 5-minute ceiling, so at least one local run
  (#134540) hit the ceiling rather than finishing. The more durable insight is
  the trade-off the author names: less exploration overhead can mean less
  structural understanding, which lines up with the scope-discovery failures
  (Claim 8). Do not port the seconds as benchmarks.

### Claim 6: Call count, not token volume, is the primary driver of both cost and latency, because the stateless API replays the full conversation on every call; sessions under ~5 calls were consistently cheaper regardless of retrieval arm
- **Evidence**: The token-economics table (calls / new tokens / output / cached
  replay / total) and the three numbered observations beneath it.
- **Confidence**: emerging (internally consistent accounting from one harness;
  no per-model pricing or provider billing cross-check)
- **Quote**: "Claude’s API is stateless, so every call replays the full conversation. That makes call count the primary cost multiplier." and "Fewer calls beats fewer tokens. Sessions that stayed under ~5 calls were consistently cheaper, regardless of approach." and "Across all runs, call count was the biggest driver of both cost and latency."
- **Our assessment**: This is the most reusable cost model in the note, and it
  is mechanistically sound: with a stateless chat API, each extra turn re-sends
  the growing transcript, so the marginal cost of an additional call is
  superlinear in conversation length. The ~5-call heuristic is directional, not
  a threshold to hard-code, but the design implication is clear: budget *turns*,
  not just tokens. This is the empirical complement to LiteLLM's per-session
  iteration caps (Cross-References).

### Claim 7: Agents fix the problem in front of them, not the system around it — on #134540 every arm swallowed an error at the source instead of preserving the `%w` contract and updating the caller
- **Evidence**: A named PR instance with the correct fix described (preserve the
  error, then update the caller to tolerate that case) and the common failure
  (swallow at source), followed by the generalization.
- **Confidence**: emerging (concrete instance; one PR, no per-arm breakdown)
- **Quote**: "PR #134540 is a good example. The correct fix required preserving an error (%w) so the caller could handle it, and then updating the caller to tolerate that specific case. Every agent instead swallowed the error at the source. Functionally similar, but architecturally wrong." and "This shows up consistently: agents fix symptoms in isolation, but miss the contracts between components."
- **Our assessment**: The cleanest concrete failure in the post because the
  distinction is checkable in the diff: swallowing an error and propagating it
  can both make the immediate test pass, but only one preserves the caller's
  ability to handle the condition. This is the code-level analogue of the guide's
  "fixes are locally plausible but globally wrong" concern (Ch00), and it is a
  review question an agent-generated PR gate can ask directly.

### Claim 8: The dominant failure mode is incomplete scope, not incorrect fixes — agents stop at the first plausible fix and miss the second sort implementation (#138191), `proxier.go` and integration paths (#138000), or stop early because a partial fix already exists (#134540)
- **Evidence**: A three-instance bullet list under "Scope discovery is the real
  bottleneck," plus the explicit statement that the biggest failure mode was
  incompleteness.
- **Confidence**: emerging (three named PR instances; no completeness scores per
  arm shown in the post)
- **Quote**: "The biggest failure mode wasn’t incorrect fixes, it was incomplete ones." and "The common pattern that emerged was agents don’t ask “what else needs to change?” They stop once the immediate issue appears resolved. This is most visible in multi-file changes, where agents fix the local bug but fail to propagate required updates across integration points."
- **Our assessment**: This is the highest-value claim for agent design. It
  reframes the eval target from "did the agent produce a correct-looking patch?"
  to "did the agent enumerate every dependent call site?" — which the
  five-dimension rubric captures as Completeness (Claim 9). It also explains why
  retrieval improvements alone underperform: finding the first relevant file is
  not the same as enumerating the full change surface.

### Claim 9: The five-dimension 0-4 rubric — Files, Location, Mechanism, Tests, Completeness — grades against the real PR diff as a *proxy* ground truth, and the author explicitly states the proxy is imperfect
- **Evidence**: The rubric definitions and the paragraph immediately following
  them.
- **Confidence**: emerging (rubric is concrete and reusable; grading was
  author-run and the proxy limitation is acknowledged)
- **Quote**: "This evaluation uses the PR diff as the reference implementation. That isn’t a perfect ground truth. PRs reflect iterative discussion and may not represent the only or final correct solution. Here, it serves as a proxy for “what human contributors converged on under review constraints.”"
- **Our assessment**: The rubric is the part most worth copying: Files and
  Location grade discovery, Mechanism grades system-level correctness, Tests
  grades verification behavior, and Completeness grades scope propagation. The
  author's caveat is important and should travel with the rubric — a PR diff is
  "what reviewers accepted," not "the uniquely correct solution," so a
  mechanism-different but valid fix can be scored down. This is the same
  ground-truth problem every coding-agent eval faces.

### Claim 10: Retrieval changes discovery, not reasoning — mandatory RAG helped #138211 find the policy-evaluation layer, but once the code was found the agent still reasoned locally
- **Evidence**: The #138211 instance (forced retrieval led to a better
  architectural choice) contrasted with the persistent limitation.
- **Confidence**: emerging (one positive instance plus the general observation;
  no reasoning-quality metric)
- **Quote**: "RAG meaningfully affects how agents find code, but not how they reason about it." and "But the limitation remains, once the relevant code is found, the agent still reasons locally. Retrieval helps with navigation, not with understanding system-wide implications."
- **Our assessment**: This is the source's sharpest boundary claim and the one
  most likely to be over-read. It does not say retrieval is useless — #138211 is
  a counterexample where retrieval improved the architectural choice. It says
  retrieval moves the agent to the right starting point and then leaves the
  system-level reasoning problem untouched. For the guide, that argues for
  pairing retrieval investment with explicit scope-enumeration and cross-file
  review steps, not for abandoning retrieval.

### Claim 11: Agents prefer adding new abstractions over reusing existing ones — on #138191 all arms introduced a new `Attempt` field instead of reusing `RestartCount`, and they add new tests rather than updating existing assertions
- **Evidence**: The #138191 field instance plus the generalization to tests.
- **Confidence**: emerging (concrete instance; the test behavior is described
  but not counted)
- **Quote**: "On #138191, the correct fix used the existing `RestartCount` field. All agents instead introduced a new `Attempt` field. Functionally correct, but architecturally heavier." and "This pattern showed up repeatedly. Agents don’t reliably recognize when the system already contains the concept they need. They solve the problem in isolation rather than integrating with existing design. This also shows up in tests. Agents tend to add new tests rather than update existing ones, even when behavior changes require modifying assertions."
- **Our assessment**: A distinct failure axis from scope discovery: the agent
  found the right file but did not recognize the existing domain concept. This
  is exactly the kind of thing a repo-level instruction or a review rule
  ("prefer existing fields/helpers; do not introduce parallel concepts") can
  target, and it is checkable in the diff. The test half matters because adding
  a parallel test can mask a changed contract rather than assert it.

### Claim 12: Issue quality is the strongest lever — well-specified issues (#136013, #138269) collapsed the differences between retrieval strategies, while vague issues diverged widely
- **Evidence**: The named well-specified PRs and the contrast with vague issues,
  plus the "issue acts as a spec" framing.
- **Confidence**: emerging (directional, from the same n=9 study; no per-issue
  scores shown)
- **Quote**: "Well-specified issues flatten the differences between approaches." and "When the issue effectively acts as a spec, retrieval method matters far less. When the issue is vague, performance diverges significantly."
- **Our assessment**: This is the most actionable claim for SRE/ops work: the
  input spec, not the retrieval stack, is what reduces variance. It directly
  supports treating runbooks and issue descriptions as executable specifications
  (Ch03) and argues that effort spent sharpening the problem statement has a
  higher expected return than swapping retrieval tools. The evidence is
  directional and the sample is small, so present it as a strong hypothesis.

### Claim 13: Skills/playbooks may help, but in a large evolving repo they become another system to maintain and do not remove the scope-discovery bottleneck
- **Evidence**: The closing section's explicit statement that no skills were
  used, the hypothetical benefit, and the maintenance argument.
- **Confidence**: emerging (author's reasoned position; not tested in the
  experiment)
- **Quote**: "This experiment did not use any explicit coding “skills” or curated agent playbooks. Only prompts and tool access." and "However, in large, evolving codebases, these skills would need to be continuously maintained and updated to remain aligned with the actual repository structure. That makes them less like a one-time improvement and more like an additional system to operate and maintain." and "As a result, while skills may improve outcomes, they do not remove the core bottleneck observed in this study: scope discovery and system-level reasoning under scale."
- **Our assessment**: A useful counterweight to skill-centric agent advice. The
  argument is not that skills are worthless — the author concedes they could
  improve system-level reasoning — but that a repo-shaped skill is a live
  artifact with a maintenance cost and a staleness failure mode. This mirrors
  the corpus's warning that stale runbooks invite confident wrong action
  (Cross-References). Grade it as an argued position, not a measured result,
  since no skill arm was run.

## Concrete Artifacts

### Benchmark set — nine in-flight Kubernetes PRs (verbatim table from "The test cases (Benchmark)")

| PR | Bug | SIG | Size | Files |
| --- | --- | --- | --- | --- |
| #134540 | SubPath volume mount race condition (EEXIST) | sig/storage | XS | 3 |
| #138211 | Image pull record poisoning (preloaded images) | sig/node | M | 5 |
| #138244 | NUMA topology stall on GB200 systems (O(2^n)) | sig/node | L | 2 |
| #136013 | OOM score panic on zero memory capacity | sig/node | S | 2 |
| #138269 | Scheduler SchedulingGates missing Pod/Update event | sig/scheduling | S | 2 |
| #138158 | ServiceCIDR deletion race in allocator | sig/network | M | 3 |
| #135970 | Missing initializer in StatefulSet slice builder | sig/apps | M | 4 |
| #138000 | Windows kube-proxy stale remote endpoint cleanup | sig/network | XL | 5 |
| #138191 | Container status sort by attempt (clock rollback) | sig/node | M | 5 |

### Wall-clock per PR (verbatim table from "Timing")

| PR | RAG | Hybrid | Local |
| --- | --- | --- | --- |
| #134540 | 55s | 3m00s | 5m00s |
| #138211 | 2m30s | 3m30s | 2m30s |
| #138244 | 41s | 44s | 2m00s |
| #136013 | 31s | 55s | 41s |
| #138269 | 44s | 1m12s | 1m23s |
| #138158 | 1m41s | 1m48s | 52s |
| #135970 | 1m23s | 2m43s | 1m32s |
| #138000 | 1m28s | 4m03s | 4m57s |
| #138191 | 1m34s | 3m54s | 2m52s |
| **Average** | **1m16s** | **2m25s** | **2m24s** |

### Token economics — averages across all runs (verbatim table from "Token economics")

| Approach | Calls | New Tokens | Output | Cached (replay) | Total |
| --- | --- | --- | --- | --- | --- |
| **RAG** | 4 | 44k | 2k | 141k | 187k |
| **Hybrid** | 8 | 27k | 3k | 234k | 264k |
| **Local** | 6 | 23k | 4k | 162k | 189k |

### Five-dimension grading rubric (verbatim from "The test cases (Benchmark)")

```
- Files: Did the diff touch the correct files?
- Location: Was the fix applied in the correct function/layer?
- Mechanism: Did the fix preserve correct system-level invariants and layering, not just patch symptoms?
- Tests: Were existing tests updated or meaningful new tests added?
- Completeness: Did the patch propagate changes across all required call sites and dependent paths?
```

### Harness attribution (verbatim from the closing note)

```
The benchmark used Claude Opus via OpenClaw with KAITO RAG Engine indexing the
Kubernetes/Kubernetes repository at HEAD. All sessions ran in isolated subagents
with no shared state, April 2026. Ground truth was the actual PR difference from
each open pull request.
```

## Cross-References

- **Corroborates**: `source-notes/blog-cncf-4-body-problem-sre-context.md` — Claim 6
  ("When the context an agent reasons over is fragmented, it doesn't just fail. It
  plausibly fails, which is the kind of error that survives review.") is the
  mechanism behind this source's "locally plausible but globally incorrect"
  finding (Claim 1). The 4-body note predicts the failure shape from context
  fragmentation; this benchmark supplies nine concrete instances and shows the
  failures were incomplete scope rather than wrong-file lookup (Claim 8). Its
  Claim 8 taxonomy ("Agents that confidently fix the wrong thing") matches the
  #134540 `%w`-swallowing case (Claim 7).
- **Corroborates**: `source-notes/docs-promptfoo-model-graded-context-recall.md` —
  Claim 4 draws the retrieval-completeness vs output-fidelity distinction
  ("recall asks 'does the context contain what a correct answer needs?'
  (retrieval completeness) while faithfulness asks 'does the output stay within
  the context?' (output fidelity)"). This source's central finding is the
  codebase version of that split: RAG improved what the agent could *find*
  (Claim 10) but not whether it enumerated all affected call sites (Claim 8),
  i.e. retrieval completeness and reasoning completeness are different gates.
- **Extends**: `source-notes/docs-promptfoo-evaluate-coding-agents.md` — Claims 1
  (agent eval measures a system with emergent behavior, not a function), 7
  (assert the path, not just the final text), 9 (the agent's output is its
  self-report, not the files it changed), and 10 (cost/latency thresholds and
  `--repeat 3` for non-determinism) supply the methodology this post applies.
  The post is a concrete benchmark instance of that methodology and adds the
  five-dimension diff rubric (Claim 9) and a failure taxonomy (Claims 7-11). It
  also illustrates why the promptfoo note's "output is self-report" warning
  matters: grading against the PR diff is exactly the workspace/file-level
  verification that note recommends.
- **Extends**: `source-notes/docs-promptfoo-evaluate-rag.md` — Claim 1 prescribes
  evaluating retrieval and generation as *separately gated* stages so failures
  localize. This benchmark is a natural experiment on that decomposition: the
  three arms vary the retrieval stage while holding the model fixed, and the
  result (retrieval changes discovery, not reasoning — Claim 10) is precisely a
  stage-localization finding. It also shows the limit of a retrieval-only eval:
  a retrieval stage can look improved while the generation/reasoning stage still
  misses scope (Claim 8).
- **Extends**: `source-notes/docs-litellm-a2a-iteration-budgets.md` — Claim 1
  documents per-session `max_iterations` and `max_budget_per_session` caps, and
  Claim 6 warns the counters are TTL-windowed rather than lifetime. This source
  supplies the empirical reason to budget *calls*: call count dominated cost and
  latency because each stateless call replays the growing conversation
  (Claim 6). The two notes together argue for iteration budgets as the primary
  loop control, with the TTL caveat that a long session can silently get a fresh
  budget.
- **Extends**: `source-notes/blog-cncf-kubestellar-ai-agents-81-pr-acceptance.md` —
  Claim 3 measures PR acceptance (~81% over 82 days) but, as its own Source
  Context says, has no cost accounting and no controlled comparison against a
  baseline. This post supplies both: a three-arm controlled comparison (Claim 2)
  and a token/call economics table (Claim 6). KubeStellar's "loops around the
  model" thesis (Claim 2) is consistent with this source's finding that workflow
  and issue quality matter more than model/retrieval choice (Claims 10, 12), but
  this post localizes the remaining bottleneck to scope discovery rather than
  codebase feedback loops.
- **Extends**: `source-notes/blog-litellm-lap-internal-agent-30-percent.md` —
  Claim 6 reports 43 open / 160 closed PRs and ~30% ticket coverage after three
  weeks, a productivity-volume measure. This source measures the other side:
  whether the produced patches are *complete* (Claim 8) and what they cost in
  calls/tokens (Claim 6). Read together, volume without a completeness gate can
  overstate agent value; the LiteLLM note's Claim 8 ("technical risk is largely
  solved") is a different emphasis, not a contradiction, since this post scopes
  its claim to correctness under scale.
- **Extends**: `source-notes/blog-cncf-agent-doc-access-tool-mix.md` — Claim 5
  reports the docs retrieval tool being used for *planning* ("It was called so
  the agent could figure out what to do"), not just answering. This post is the
  codebase-retrieval analogue: retrieval helped the agent discover the policy
  evaluation layer on #138211 before implementing (Claim 10), i.e. retrieval
  changes the starting point for reasoning. The shared boundary is that
  retrieval can improve the *briefing* without improving the *system-level
  reasoning* that follows.
- **Contradicts**: none found. The post argues against a common assumption
  ("RAG fixes coding agents"), but no existing source note makes that assumption
  as a claim, so there is no source-note contradiction to file. The apparent
  tension with `docs-litellm-a2a-iteration-budgets.md` (call caps) or
  `blog-litellm-lap-internal-agent-30-percent.md` (technical risk largely
  solved) is a difference of scope, not a contradiction.
- **Novel**: First corpus source with a controlled three-arm retrieval benchmark
  on real PRs, and the first with a per-PR wall-clock plus call/token economics
  table for coding agents. It is also the first to name **scope discovery** as
  the dominant failure mode with concrete PR instances, and the first to argue
  that call count (stateless replay) rather than token volume is the primary
  cost driver in an agent loop.

## Guide Impact

- **Chapter 03 (Runbooks and Agents)**: Add the scope-discovery failure mode
  (Claim 8) as a named review dimension for agent-generated changes: the agent
  must enumerate dependent call sites and integration points, not just produce a
  locally correct patch. Pair it with the five-dimension rubric (Claim 9) as a
  concrete eval/review template, and with the "retrieval changes discovery, not
  reasoning" boundary (Claim 10) so the chapter does not present RAG as a
  correctness fix. Add the issue-quality finding (Claim 12) as support for
  treating runbooks/issue descriptions as executable specs: a well-specified
  issue collapsed variance across retrieval strategies.
- **Chapter 05 (LLM Ops Reliability)**: Use the call-count cost model (Claim 6)
  as the empirical basis for budgeting agent *turns* (not just tokens) and for
  per-session iteration caps. The concrete numbers — RAG 4 calls / 187k tokens /
  1m16s; Hybrid 8 / 264k / 2m25s; Local 6 / 189k / 2m24s — are a reusable
  illustration that a hybrid tool-switching loop can be both slower and more
  expensive. Add the caveat that these are single-run, n=9 figures.
- **Chapter 02 (Observability)**: Instrument retrieval as its own stage/span and
  measure retrieval completeness separately from output fidelity (Claims 8, 10),
  mirroring the promptfoo RAG stage-split guidance. The benchmark's finding that
  agents can find the right file yet miss the full change surface is an argument
  for a "scope coverage" signal in agent traces, not just a "did retrieval
  return results" signal.
- **Chapter 00 (verification over generation)**: Use Claim 7 (#134540 swallowing
  `%w` instead of preserving the caller contract) as a concrete example of a fix
  that passes the local test but is architecturally wrong. It is the code-level
  instance of the guide's "locally plausible, globally wrong" concern.
- **Do not add**: the ~5-call threshold (Claim 6) or the absolute wall-clock
  times (Claim 5) as universal rules. They are directional findings from one
  model, one repo, and single runs; present them as hypotheses to measure in
  your own harness.

## Extraction Notes

- Read the full article (single page). Followed no linked sub-pages: the
  outbound links are the Kubernetes repo, KAITO RAG docs, Qdrant hybrid-search
  docs, and OpenClaw — all tool references rather than additional evidence for
  these claims. The page is not paywalled.
- All quotes were copied character-for-character from the fetched article,
  including its curly apostrophes and the `%w` / `RestartCount` / `Attempt` code
  spans. Tables were copied row-for-row from the rendered post.
- **Candidate dispositions** (`miner-related-notes.md`, read before writing
  Cross-References):
  - `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md` — dismissed:
    SLO granularity and retail/gaming platform migration; no overlap with coding
    agents, retrieval, or call economics.
  - `source-notes/blog-cncf-cloud-native-agentic-ai-security-platform.md` —
    dismissed: multi-agent security-platform architecture (mTLS, policy-as-code,
    anomaly gating); not retrieval strategy or scope discovery.
  - `source-notes/docs-promptfoo-model-audit.md` — dismissed: model artifact
    scanning/CI gate; unrelated to code retrieval or agent reasoning.
  - `source-notes/docs-google-sre-prodcast-03-13-imperative-declarative.md` —
    dismissed: imperative vs declarative change workflows; no retrieval/agent-eval
    overlap.
  - `source-notes/docs-google-sre-ai-engineering-reliable-operations.md` —
    dismissed: Google's L0-L4 autonomy model and production AI-SRE systems; the
    autonomy framing is adjacent but the source has no retrieval benchmark or
    scope-discovery evidence to corroborate.
  - `source-notes/blog-cncf-inspektor-gadget-security-audit.md` — dismissed:
    eBPF security audit; unrelated.
  - `source-notes/docs-promptfoo-enterprise-audit-logging.md` — dismissed:
    audit-log taxonomy; unrelated.
  - `source-notes/blog-litellm-auto-router-v2.md` — dismissed: model routing by
    request complexity; this source is about *code* retrieval, not model
    selection, and its cost finding is about call count rather than routing.
  - `source-notes/blog-cncf-agent-doc-access-tool-mix.md` — cited (Extends,
    Claim 5: retrieval used for planning) as the docs-retrieval analogue.
  - `source-notes/blog-cncf-kubernetes-integration-tax-prometheus-cilium.md` —
    dismissed: CNCF project integration/wiring failures; unrelated.
- Additional cross-refs were found by searching `source-notes/` (`retrieval`,
  `RAG`, `scope discovery`, `call count`, `context`):
  `docs-promptfoo-evaluate-rag.md`, `docs-promptfoo-model-graded-context-recall.md`,
  `blog-cncf-4-body-problem-sre-context.md`,
  `docs-promptfoo-evaluate-coding-agents.md`,
  `docs-litellm-a2a-iteration-budgets.md`,
  `blog-cncf-kubestellar-ai-agents-81-pr-acceptance.md`, and
  `blog-litellm-lap-internal-agent-30-percent.md` (all cited above). Claim
  numbers were re-read and verified against each note's `### Claim:` headings
  before writing (MINER §4b).
- `confidence_overall: emerging` rather than `settled`: the harness and rubric
  are concrete and the findings are internally consistent, but this is one
  author's self-run, self-graded benchmark on n=9 PRs with a single model, one
  repository, single (not repeated) timings, and an acknowledged imperfect
  ground truth. The author's own caveats are preserved rather than smoothed
  over.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited; they
  are derived indexes rebuilt after merge.
