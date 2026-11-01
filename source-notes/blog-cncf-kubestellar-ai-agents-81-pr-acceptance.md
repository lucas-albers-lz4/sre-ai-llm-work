---
source_url: https://www.cncf.io/blog/2026/05/14/when-ai-agents-become-contributors-how-kubestellar-reached-81-pr-acceptance
source_type: blog-post
title: "When AI agents become contributors: How KubeStellar reached 81% PR acceptance"
author: Andy Anderson, Chief Maintainer of KubeStellar Console
date_published: 2026-05-14
date_extracted: 2026-11-01
last_checked: 2026-11-01
status: current
confidence_overall: emerging
issue: "#1980"
---

# When AI agents become contributors: How KubeStellar reached 81% PR acceptance

> A solo maintainer's 82-day record of rebuilding a codebase around coding agents:
> measured PR acceptance, deterministic tests as the trust layer, and
> measure-before-automate as a hard ordering rule.

## Source Context

- **Type**: blog-post (CNCF Project Post; first-person practitioner experience report)
- **Author credibility**: Andy Anderson is the Chief Maintainer of KubeStellar
  Console, a multi-cluster Kubernetes management dashboard inside the KubeStellar
  CNCF Sandbox project. The report is first-person and names specific artifacts
  (`CLAUDE.md`, `.github/copilot-instructions.md`, `auto-qa-tuning.json`), cadences,
  and counts, so it is more checkable than a vendor thought-leadership piece — but
  the author runs the project solo, the metrics are self-reported, and no external
  validation is offered. He explicitly flags that scalability beyond a
  solo-maintained Sandbox project is untested.
- **Scope**: Covers the failure-and-rebuild arc of one Go/React/TypeScript project
  built from scratch (mid-December onward) with two coding agents in parallel
  terminal sessions, over roughly four months. It covers instruction files, test
  suites, acceptance-rate measurement, self-adjusting QA rotation weights,
  operational automation loops, and one prompting habit. It does **not** cover
  multi-maintainer coordination, security review of agent code, cost accounting,
  model selection benchmarks, or any controlled comparison against a baseline.

## Extracted Claims

### Claim 1: The initial agent productivity surge collapsed within two weeks into cascading breakage, overwritten architecture, and scope creep, leaving the author spending more time reverting than reviewing
- **Evidence**: First-person narrative of the first two weeks on a new repo: builds broke in hard-to-trace ways, prior-day architectural choices were silently overwritten, scope expanded unprompted, the agent touched unpointed-at files, and each fix broke three other things. The author says he scrapped the approach.
- **Confidence**: anecdotal (single project, self-reported; no logs or diffs shown)
- **Quote**: "Builds broke in ways that were hard to trace. Architectural choices from the day before quietly got overwritten. Scope expanded without being asked. The agent kept touching files I hadn’t pointed it toward, and the cascade problem was the worst of it—fix one thing, then three others broke. I started spending more time reverting than reviewing."
- **Our assessment**: This is the failure half of the report and the reason the source is useful: it is a concrete description of the *integration* failure mode, not a model-capability failure. The author's own framing is that the code was being produced faster than it could be absorbed. We buy the shape of the story (it matches other agent-adoption reports in the corpus); the magnitudes are unverifiable.

### Claim 2: The leverage in an AI-assisted codebase lives in the loops the codebase wraps around the model, not in the model — and giving the agent more autonomy makes the failure mode worse
- **Evidence**: The author's stated conclusion after abandoning the first approach, contrasted against "the usual industry advice" to let the agent run longer and touch more files.
- **Confidence**: emerging (a practitioner thesis, later instantiated by the five loops below; no controlled comparison)
- **Quote**: "The leverage runs in the opposite direction. The intelligence in an AI-assisted codebase lives less in the model and more in the loops the codebase wraps around it. If you want the agent to do more, the surrounding code has to measure more."
- **Our assessment**: The article's central thesis and its most transferable claim. It reframes the reliability question from "which model?" to "what feedback does the repo give the agent?" The pull-quote above the body states the same idea: "The surprise in building KubeStellar Console with coding agents was not the extent of the model’s capabilities, but the heavy lifting the surrounding codebase had to perform." This is a directional claim, not a measured one, but it is consistent with the concrete mechanisms in Claims 6-9.

### Claim 3: Across 82 days the project reached ~81% PR acceptance, with 63 CI/CD workflows, 32 nightly suites, 91% coverage across 12 shards, ~30-minute bug-to-merge, and ~1-hour feature-request-to-PR — attributed to measurement, not a better model
- **Evidence**: Self-reported counts and times in the article's summary paragraph and loop 2. No dashboard, query, or definition of the acceptance population is provided.
- **Confidence**: anecdotal (self-reported; "81% PR acceptance" is not defined, e.g. accepted vs. opened, per agent or per category)
- **Quote**: "There are 63 CI/CD workflows, 32 nightly test suites, and coverage sitting at 91% across twelve shards. Across 82 days, PR acceptance settled around 81%. Community bug reports are moving to merged fixes in roughly thirty minutes. Feature requests are landing as pull requests in about an hour. None of that was the result of a better model. What changed was what the code itself had learned to measure."
- **Our assessment**: Treat these as directional operational figures, not benchmarks. The 82-day window is narrower than the roughly four-month project span the article describes, and the acceptance rate's denominator is unspecified. Still, the numbers are specific and internally consistent with the loop descriptions, and the "none of that was a better model" sentence is the claim the rest of the article is built to support.

### Claim 4: The author's "AI Codebase Maturity Model" has five rungs — Assisted, Instructed, Measured, Adaptive, Self-Sustaining — and he claims they cannot be reordered
- **Evidence**: Author's own naming and ordering, walked through in the order they appeared in his project.
- **Confidence**: anecdotal (author's framing; no external corroboration)
- **Quote**: "Five tightening loops got me there. I think of them as the rungs of what I’ve been calling the AI Codebase Maturity Model—Assisted, Instructed, Measured, Adaptive, and Self-Sustaining. I’ll walk through them in the order they appeared, because I don’t think they can be reordered."
- **Our assessment**: The ladder is the weakest part of the article — a naming scheme with n=1 behind it — but the *ordering argument* is the useful part and is independently supported by Claims 5-9. Use the sequence as a hypothesis to test, not as a standard. The names "Assisted" and "Instructed" also overlap confusingly with Google's L0-L4 autonomy levels (see Cross-References), so the guide should not merge the two vocabularies.

### Claim 5: The cheapest, highest-return intervention was externalizing the maintainer's preferences into instruction files — a `CLAUDE.md`, a `.github/copilot-instructions.md`, and a rejection-criteria guide that covered ~90% of rejection reasons
- **Evidence**: The author names all three artifacts and says the rejection-criteria guide accounted for about 90% of the reasons he was rejecting AI-generated PRs. He explicitly says this was not measurement.
- **Confidence**: anecdotal (the ~90% figure is a self-estimate; no rejection log is shown)
- **Quote**: "I started with a CLAUDE.md at the root of the repo, followed by a .github/copilot-instructions.md file for pull request conventions. Next came a card-level development guide that cataloged the top reasons I was rejecting AI-generated PRs." and "That one guide wound up covering about 90% of my rejection criteria. Sessions became more consistent. The same mistakes stopped recurring across agents."
- **Our assessment**: The concrete form of "write down what you keep correcting." The 90% number is unverifiable, but the mechanism — converting recurring review comments into durable repo instructions — is cheap and low-risk, and the author's honesty that this stage was "still running on intuition" is what makes the later measurement claims credible. This is the least controversial claim in the article.

### Claim 6: Tests are the trust layer for an autonomous workflow, because they are the only signal the agent has about whether it is improving or degrading the system
- **Evidence**: The author's loop-2 framing, backed by 32 nightly suites across 12 shards covering compliance, performance, nil safety, accessibility, internationalization, and visual regression, plus per-category acceptance logging into `auto-qa-tuning.json`.
- **Confidence**: emerging (operational practice with named artifacts; single project)
- **Quote**: "Testing for an autonomous workflow differs from testing for a human workflow. It’s the only signal the agent has to know whether it’s making the system better or worse."
- **Our assessment**: This is the eval-side claim that the rest of the article operationalizes. It is stronger than "write tests" because it scopes the purpose: the suite is not just a correctness net for humans, it is the agent's *feedback channel*. The named suite categories also show breadth was treated as part of the signal, not an afterthought.

### Claim 7: An ~85%-passing Playwright drag-and-drop test was tolerable for humans but catastrophic when test results gated autonomous merges — it blocked good PRs at random, let weak ones through, and took three days to trace to an animation-completion timing issue in CI
- **Evidence**: A specific incident: one Playwright E2E test, ~85% pass rate, three days of investigation, root cause identified as animation-completion timing in CI. The author generalizes to "you can't build automation on top of an unreliable signal."
- **Confidence**: emerging (single incident, but specific root cause and mechanism; the generalization matches the eval-methodology notes)
- **Quote**: "A flaky test in a human workflow is an annoyance. In an autonomous one, it’s a slow, quiet erosion of the entire trust model." and "One Playwright end-to-end test for drag-and-drop passed about 85% of the time. In a human workflow, that’s tolerable; you re-run it, you move on. In an autonomous workflow where test results gate merges, an 85% test is a disaster. Good PRs were being blocked at random, and weak ones were being let through. I spent three days on that single test, and it turned out to be an animation-completion timing issue in CI."
- **Our assessment**: The article's sharpest transferable claim, and the inverse of the guide's existing "a gate that cannot fail is not a gate": here the gate cannot *pass* reliably, so it destroys the agent's ability to distinguish good work from bad. The 85% figure is the threshold that matters — a failure rate low enough for a human to shrug at is high enough to corrupt an autonomous decision loop. Buy this as an operational rule: test determinism is a precondition for merge-gating, not test hygiene.

### Claim 8: Once per-category acceptance was logged, QA rotation weights self-adjusted from the data — accessibility at 62% acceptance was up-weighted to 0.93, while operator-category work at 8% (11 merges vs 129 closed) was down-weighted to zero and its CI cycles redirected
- **Evidence**: The author describes auto-QA running four times a day across eight quality layers, with rotation weights adjusted from acceptance data. The two examples include the acceptance rates and the resulting weights/merges-closed counts.
- **Confidence**: emerging (specific numbers and a named tuning file; self-reported, and the adjustment policy itself is not shown)
- **Quote**: "With acceptance rates being logged, automation became a safer proposition. Auto-QA started running four times a day across eight layers of quality checks. The rotation weights that decide which categories of work the system focuses on began adjusting themselves based on the data. Accessibility PRs were landing at 62% acceptance, so their weight went up to 0.93. Operator-category PRs were landing at 8% (11 merges against 129 closed), so that weight dropped to zero and CI cycles got redirected."
- **Our assessment**: The most concrete "adaptive" mechanism in the corpus: acceptance rate is not just a dashboard metric, it is a *scheduling input*. The operator example is especially useful because it shows the loop is willing to stop investing in a category entirely (weight zero) rather than keep retrying it. What the article does not show is the policy that maps 62% → 0.93 or 8% → 0, so treat the weights as illustrative, not a formula to copy.

### Claim 9: The ordering rule is measurement first, automation second — "Automation without measurement isn't maturity — it's failure at scale"
- **Evidence**: The author's stated generalization across the loops, plus a counterfactual ("inverting the order is how autonomous systems go off the rails").
- **Confidence**: emerging (practitioner rule supported by the concrete loop sequence; no controlled trial)
- **Quote**: "Automation without measurement isn’t maturity — it’s failure at scale." and "The pattern across all of these is the same: measurement first, automation second. Inverting the order is how autonomous systems go off the rails."
- **Our assessment**: This is the article's normative contribution and it is directly usable as guide advice: instrument acceptance and gate reliability *before* widening agent autonomy. The slogan is memetic but the supporting evidence is the preceding claims (the flaky gate, the acceptance weights), not the slogan itself. We buy the ordering rule for merge-gated agent work; whether it generalizes to non-code agents is untested.

### Claim 10: Operational loops close around the measurement core — triage of four repos every 15 minutes, PR build-status polling every 60 seconds, exponential backoff for stuck agents, and an hourly GA4 query that files GitHub issues for production error spikes before users report them
- **Evidence**: A four-item bullet list of running automation, with cadences. No coverage, false-positive, or incident-yield numbers.
- **Confidence**: anecdotal (described as running; no outcome data)
- **Quote**: "A triage process scanned four repositories every 15 minutes." and "A PR monitor polled build status every 60 seconds." and "An error-recovery workflow used exponential backoff to handle stuck agents." and "A GA4 query ran hourly against production analytics and filed GitHub issues for error spikes before users reported them."
- **Our assessment**: Useful as a concrete cadence menu for the guide's toil-reduction chapter, especially the proactivity inversion (file the issue on the error spike rather than wait for a user report). But these are one-line descriptions, not designs: the article gives no dedup, threshold, or escalation logic, so cite them as patterns, not reference implementations.

### Claim 11: In the self-sustaining stage, the system's behavior was determined by its artifacts — instruction files, tests, workflow rules, and acceptance-rate history — enough that community issues were triaged, fixed, tested, and queued before the maintainer woke up
- **Evidence**: The author's description of the fourth loop, with a rough transition ("I can’t point to a specific day"). No overnight log is shown.
- **Confidence**: anecdotal (self-reported transition; no artifact inventory or trace)
- **Quote**: "At some point, and I can’t point to a specific day, the system stopped needing me in the loop to operate. Its behavior was being determined by its artifacts: the instruction files, the tests, the workflow rules, and the acceptance rate history." and "The community started opening issues at all hours, and those issues were being triaged, assigned, fixed, tested, and queued for review before I even woke up."
- **Our assessment**: The strongest form of the article's thesis — the codebase, not the maintainer, becomes the carrier of judgment. The honest "I can’t point to a specific day" is a good sign that this is a retrospective, not a product demo. The claim is plausible given the mechanisms, but the absence of any trace means it should be carried as an aspiration pattern rather than evidence that self-sustainment is achieved.

### Claim 12: A user bug report about a cluster marked "healthy" while pods sat in ImagePullBackOff was answered by the system as a design decision, not a bug — infrastructure health vs. workload health were already encoded in tests, health-check logic, and docs
- **Evidence**: A named April incident. The system reportedly explained that cluster health (node readiness, API reachability) is architecturally separate from workload health before the maintainer looked at it.
- **Confidence**: anecdotal (single anecdote; the explanation is the author's account of the agent's answer)
- **Quote**: "In April, a user filed a bug reporting that a cluster was marked “healthy” while pods were stuck in ImagePullBackOff. Before I looked at it, the system had already answered that cluster health reflects infrastructure health (node readiness, API reachability), which is architecturally separate from workload health. It wasn’t a bug. It was a Kubernetes mental model that didn’t quite map to what the dashboard was showing. The design decision was already encoded in the tests, in the health-check logic, and in the docs; the agent could explain it because the codebase already knew it."
- **Our assessment**: The cleanest illustration in the corpus of the difference between "the model knows Kubernetes" and "the repo knows this project's decisions." The agent's answer is only trustworthy because the distinction was already written into tests/docs/health checks. For the guide this is a Ch02/Ch00 example: observed "health" is a modelling choice, and encoding that choice is what lets an agent explain it without inventing a story.

### Claim 13: Asking "Why didn't you catch this?" instead of "fix this" yields root-cause analysis plus a durable test, instruction, or rule that blocks a whole class of failures, so questioning compounds while commanding does not
- **Evidence**: The author's account of changing his prompting habit; no A/B test or before/after count is given.
- **Confidence**: anecdotal (practitioner heuristic; plausible mechanism, unmeasured)
- **Quote**: "Instead of “fix this bug,” I started asking, “Why didn’t you catch this?” The first phrasing produces a patch. The second tends to produce a root-cause analysis and, as a side effect, a new test, instruction, or rule that blocks an entire class of similar failures." and "Commanding gets you a sequence of isolated fixes. Questioning compounds."
- **Our assessment**: The prompting pattern is a natural complement to the measurement loops: each "why" question is supposed to leave behind an artifact that changes future behavior. This is the mechanism by which the loop ladder is supposed to ratchet rather than oscillate. Buy it as a heuristic worth trying; the "compounds" claim is not measured.

### Claim 14: For engineering leaders, the model is a commodity — swapping it is a weekend, rebuilding the surrounding feedback system is a quarter — so the differentiator is the intelligence infrastructure, though the author concedes scale beyond a solo Sandbox project is untested
- **Evidence**: The author's closing advice to maintainers and leaders, plus an explicit caveat that broader applicability is for the community to test.
- **Confidence**: anecdotal (opinion/advice, not measured; the caveat is the author's own)
- **Quote**: "The model is a commodity component, and swapping one for another is a weekend of work. Rebuilding the surrounding feedback system is a quarter of the work. The differentiation is the intelligence infrastructure: the instruction files, the test suites, the metrics, and the workflow rules." and "Whether it scales beyond a solo-maintained Sandbox project is something the broader community will need to test."
- **Our assessment**: The recommendation is directionally consistent with the rest of the article and with Ch03's harness framing, but the effort ratios ("a weekend", "a quarter") are rhetorical, not measured. The self-imposed scalability caveat is the most important line in the article for the Assayer: this is not evidence that the model works for teams, only that it worked for one solo maintainer.

## Concrete Artifacts

### Reported operating figures (tabulated from the article's summary and loop descriptions)

```
Project:        KubeStellar Console (Go backend, React/TypeScript frontend, Helm)
Staffing:       1 maintainer + 2 AI coding agents (parallel terminal sessions)
Window:         ~82 days of PR-acceptance measurement; ~4 months total build

CI/CD workflows:              63
Nightly test suites:          32
Coverage:                     91% across 12 parallel shards
PR acceptance:                ~81% over 82 days
Community bug -> merged fix:  ~30 minutes
Feature request -> PR:        ~1 hour

Suite categories named: compliance, performance, nil safety, accessibility,
                        internationalization, visual regression
```

### Auto-QA acceptance-weight examples (from loop 3)

```
auto-QA cadence:        4x/day across 8 quality-check layers
Tuning source:          PR acceptance rates per category, logged to auto-qa-tuning.json

Category        Acceptance   Outcome
accessibility   62%          weight raised to 0.93
operator        8%           weight dropped to 0
                (11 merges vs 129 closed)  CI cycles redirected
```

### Operational automation loops (from loop 3)

```
Triage:          scan 4 repositories every 15 minutes
PR monitor:      poll build status every 60 seconds
Agent recovery:  exponential backoff for stuck agents
Production:      hourly GA4 query; file GitHub issues for error spikes
                 before users report them
```

### The five-loop ladder (author's framing)

```
1. Instructed       CLAUDE.md + .github/copilot-instructions.md + rejection-criteria guide
2. Measured         tests as the trust layer; per-category acceptance logging
3. Adaptive         measure -> automate; self-adjusting QA rotation weights
4. Self-Sustaining  behavior determined by repo artifacts; overnight issue handling
5. (Prompting)      "Why didn't you catch this?" -> root cause + new test/rule
```

## Cross-References

- **Corroborates**: `source-notes/docs-promptfoo-evaluate-coding-agents.md` — Claim 1
  ("non-determinism compounds" across an agent's tool calls and decisions, so "you're
  evaluating the system, not just the model") supplies the eval-side theory for this
  article's production-side observation that an unreliable test corrupts an agent's
  only feedback signal. Claim 10's rule that a prompt failing ~50% of the time is an
  ambiguous prompt to fix rather than a retry target is the same instinct applied to
  eval runs instead of merge gates; this source adds the sharper case where a gate
  fails ~15% of the time and is tolerated for humans but cannot be tolerated for
  agents.
- **Corroborates**: `source-notes/docs-google-sre-ai-engineering-reliable-operations.md`
  — Claim 3 defines Google's SRE AI Autonomy Levels (L0-L4) as a maturity model with
  explicit gating criteria, and Claim 2's "Progressive Authorization" pillar gates
  autonomy on proven reliability. KubeStellar's five-rung model is the same
  evidence-gated-progression shape at codebase scope rather than operational scope.
  The two ladders should be cited as complementary, not interchangeable: one governs
  what an agent may do in production, the other governs how much autonomy a codebase
  is allowed to give an agent over its own changes.
- **Extends**: `source-notes/blog-litellm-lap-internal-agent-30-percent.md` — Claim 6
  reports 43 open / 160 closed PRs and ~30% ticket coverage after three weeks, i.e.
  the same acceptance-counting measurement style. This source adds the feedback half:
  acceptance is not just a scoreboard, it is fed back into which categories of work
  the QA rotation prioritizes. Note the different emphasis in LiteLLM's Claim 8
  ("technical risk is largely solved") versus KubeStellar's "None of that was the
  result of a better model." These are not contradictory — both agree models are
  adequate; they disagree on where the remaining work lives (scale/reliability/security
  of the agent platform vs. the codebase's feedback loops).
- **Extends**: `source-notes/blog-cncf-platform-engineering-agentic-enterprise-three-entities.md`
  — Claim 3 argues context (deployment history, ownership, policies, organizational
  knowledge) is becoming a first-class platform capability that humans and agents
  reason over. KubeStellar's instruction files, tests, workflow rules, and
  acceptance history are a repo-scoped instance of that idea: the "context" is
  versioned in the repository and the agent reads it as operating instructions.
  The platform note is broader and more speculative; this one is concrete but
  single-repo.
- **Extends**: `source-notes/blog-cncf-cloud-native-agentic-ai-security-platform.md`
  — Claim 8 puts every agent's system prompt, tool list, and output schema in a
  Kubernetes Custom Resource reconciled from Git, so "promoting a change is a pull
  request: code-reviewed, audited, reversible." KubeStellar's `CLAUDE.md` /
  `.github/copilot-instructions.md` / rejection-criteria guide are the lighter-weight
  version of the same principle — agent behavior config is a reviewed repo artifact.
  The security-platform note is about runtime safety policy; this one is about
  contribution quality, but both depend on the artifact being in Git.
- **Extends**: `source-notes/docs-google-sre-prodcast-04-06-fletcher-vibe-coding.md` —
  Claim 1 observes that vibe-coded apps generate fine but the reliability work
  begins at deploy, leaving a human to debug "a bunch of TypeScript." This source is
  the counter-move: the reliability expertise that Fletcher says a human must supply
  at deploy can be encoded into tests, health-check logic, and docs so the agent can
  apply it. Different contexts (throwaway vibe-coded app vs. a maintained repo with
  63 workflows), so not a contradiction — but worth pairing in the guide as the two
  ends of the "where does the human expertise live?" question.
- **Contradicts**: none found. No existing note makes a claim this source materially
  opposes. The LiteLLM emphasis difference noted above is a context difference, not
  a contradiction, so no contradiction issue was filed.
- **Novel**: This is the corpus's first source with a *closed-loop acceptance-to-
  scheduling* mechanism (`auto-qa-tuning.json` driving rotation weights), and the
  first quantified treatment of flaky tests as a trust-model defect for autonomous
  merges rather than a CI annoyance. The five-rung "AI Codebase Maturity Model"
  naming is new but is a framing, not evidence.

## Guide Impact

- **Chapter 03 (agent harnesses / automation-safety baseline)**: Add the
  measure-before-automate ordering rule (Claim 9) as a precondition for widening
  agent autonomy, and the "loops around the model" framing (Claim 2) alongside the
  existing harnesses-layer discussion. The concrete support is Claim 7: a test that
  gates agent merges must be deterministic, because a ~15% flake rate silently
  corrupts the agent's feedback signal. Add instruction files (`CLAUDE.md`,
  `copilot-instructions`, rejection-criteria guide) as the cheapest first artifact
  (Claim 5), with the caveat that they are not measurement.
- **Chapter 05 (evaluation methodology / release engineering)**: Pair this source
  with Ch05's "A gate that cannot fail is not a gate." This is the inverse failure
  mode: a gate that cannot *pass* reliably (Claim 7). Recommend that agent-gated
  pipelines measure and publish flake rate per gate, and that per-category PR
  acceptance be used as an eval metric (Claim 3) and a scheduling input (Claim 8),
  not merely a dashboard.
- **Chapter 04 (toil reduction)**: Use Claim 10's cadence menu as concrete examples
  of agent-appropriate operational loops — 15-minute cross-repo triage, 60-second PR
  polling, exponential backoff for stuck agents — while noting the source gives no
  false-positive or yield data. Use Claim 13's "why didn't you catch this?" prompt
  as the pattern that converts one incident into a durable rule.
- **Chapter 02 (observability / proactive signal)**: Use the ImagePullBackOff
  anecdote (Claim 12) as an example that observed health is a modelling decision:
  infrastructure health (node readiness, API reachability) is separate from workload
  health, and encoding that distinction in tests/docs is what lets an agent explain
  it without hallucinating. Also cite the hourly GA4 error-spike-to-issue loop
  (Claim 10) as proactive signal-to-issue filing.
- **Chapter 00 (publishing criteria / system self-recovery)**: The source is a
  useful but bounded data point for "what would have to be true for the system to
  self-recover?" — the author claims overnight triage/fix/test/queue (Claim 11),
  but supplies no trace, and explicitly limits applicability to a solo-maintained
  Sandbox project (Claim 14). Present it as a hypothesis with a stated test, not as
  a demonstrated property.
- **Do not add**: the five-rung ladder as a canonical maturity framework. It is the
  author's n=1 framing (Claim 4) and overlaps confusingly with Google's L0-L4
  autonomy levels. Cite it as a practitioner heuristic only.

## Extraction Notes

- Read the full article (single page; no substantive linked sub-pages followed —
  the only linked pages were a KubeStellar project page and a Playwright explainer,
  neither of which carries additional evidence for these claims). The page is not
  paywalled.
- All quotes were copied character-for-character from the fetched article, including
  its curly apostrophes and the em dashes in "Maturity Model—Assisted" and
  "failure at scale —".
- **Candidate dispositions** (`miner-related-notes.md`):
  - `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md` — dismissed: SLO
    granularity and retail/gaming platform migrations; no overlap with agent merge
    gating or codebase maturity.
  - `source-notes/blog-cncf-cloud-native-agentic-ai-security-platform.md` — cited
    (Extends, Claim 8: agent behavior config as reviewed Git artifacts).
  - `source-notes/docs-google-sre-prodcast-03-13-imperative-declarative.md` —
    dismissed: declarative/imperative change-workflow taxonomy; no overlap.
  - `source-notes/docs-litellm-anthropic-advisor-tool.md` — dismissed: within-request
    model composition; unrelated to merge gating.
  - `source-notes/docs-litellm-completion-function-call.md` — dismissed: function-
    calling capability predicates; unrelated.
  - `source-notes/docs-promptfoo-evaluate-openai-agents-python.md` — dismissed:
    OpenAI Agents Python tracing/OTLP bridge; eval plumbing, not merge-gate
    determinism.
  - `source-notes/docs-langfuse-roadmap.md` — dismissed: observability vendor
    roadmap; its "auto-optimizing agents" vision is adjacent but too speculative to
    cite as corroboration.
  - `source-notes/docs-litellm-batches-api.md` — dismissed: batch rate limiting;
    unrelated.
  - `source-notes/docs-promptfoo-splunk-integration.md` — dismissed: red-team-to-SIEM
    pipeline and supply-chain hazards; unrelated.
  - `source-notes/docs-langfuse-mcp-server.md` — dismissed: docs MCP server; unrelated.
- Additional cross-refs were also checked beyond the candidate list:
  `docs-promptfoo-evaluate-coding-agents.md`, `docs-google-sre-ai-engineering-reliable-operations.md`,
  `blog-litellm-lap-internal-agent-30-percent.md`,
  `blog-cncf-platform-engineering-agentic-enterprise-three-entities.md`, and
  `docs-google-sre-prodcast-04-06-fletcher-vibe-coding.md` (all cited above).
  `blog-pagerduty-sre-agent-architecture.md` was reviewed and dismissed: it is about
  multi-agent incident-investigation architecture, not codebase feedback loops or
  merge gating.
- Claim numbers in every cited note were re-read and verified against the notes'
  `### Claim:` headings before writing (MINER §4b).
- `confidence_overall: emerging` rather than `settled`: the mechanisms are concrete
  and partially corroborated, but the evidence is one solo maintainer's self-reported
  project, with no independent validation, no defined acceptance denominator, and an
  explicit author caveat about scalability.
- Internal-consistency note (not a cross-source contradiction): the article says
  "Four months on" but reports "Across 82 days" for PR acceptance; the 82-day window
  is narrower than the full project span, which is plausible but means the acceptance
  rate is a windowed figure, not a project-lifetime one. Recorded here so the Assayer
  does not read it as a misquote.
