---
source_url: https://www.cncf.io/blog/2026/07/22/i-made-a-policy-engine-think-it-was-in-production
source_type: blog-post
title: "I made a policy engine think it was in production"
author: "Sargam Puram (Kyverno Project Maintainer; Spring 2026 LFX Mentee)"
date_published: 2026-07-22
date_extracted: 2026-10-15
last_checked: 2026-10-15
status: current
confidence_overall: emerging
issue: "#1735"
---

# I made a policy engine think it was in production

> A Kyverno maintainer's first-person account of making the offline CLI
> produce trustworthy policy results by **conforming the test input to the
> production shape at the boundary**, rather than teaching the engine to
> accept test-shaped data. The transferable pattern — *match the production
> shape at the seam where the distinction stops mattering; do not fork the
> engine* — is the guide's missing second resolution to environment
> divergence (the first being Ch05's artifact-parity rule). The source also
> supplies concrete silent-failure evidence: wildcard rules panicking on a
> fake client missing GVK registrations, and ruleless CEL policy types whose
> results were silently swallowed — a green test that verified nothing.

## Source Context

- **Type**: blog-post (CNCF "Project Maintainer Post").
- **Author credibility**: First-person engineering account by Sargam Puram, a
  final-year Computer Engineering undergraduate and the Spring 2026 LFX
  Mentee on Kyverno's Unified CLI project (#15264), mentored by Kyverno
  maintainers Shuting Zhao and Frank Jogeleit. The post names the exact
  functions (`policy_processor.go`, `resolveResource()`,
  `resolveResourcesMockData`), the exact Go types (`runtime.RawExtension`,
  `[]interface{}`, `unstructured.Unstructured.Object`), the exact error text,
  and a dozen PR numbers. High credibility for *what the author built and
  observed*; it is a self-report with no independent verification and no
  benchmarks.
- **Scope**: Covers the Kyverno CLI's offline evaluation of
  `kubernetesResource`-backed `GlobalContextEntry` objects — the pre-existing
  crash/silent-failure bugs, the rejected first approach (multi-object →
  single-object CEL input), the boundary-adapter fix in `resolveResourcesMockData`,
  two landing PRs, a community backport request, and an enumerated list of the
  twelve weeks' other contributions. Does NOT cover LLM/GPU/AI operations of
  any kind (the domain is Kubernetes admission policy), any measured
  reliability/cost/latency numbers, or the internals of the CEL/JMESPath
  compilers beyond the input shape they expect.
- **Prospector framing**: Three concurrent triage runs routed this as
  `triaged:text`, novelty medium, priority `medium`. Relevant chapters
  proposed were Ch05 (release engineering / reproducible fixtures), Ch00
  (principles), and Ch06 (policy enforcement). The intended value is the
  *test-double fidelity pattern* and the silent-failure mechanism, not
  Kyverno-specific CLI detail.

## Extracted Claims

### Claim 1: The offline evaluation gap was not theoretical — without a live API server the CLI panicked, silently skipped rules, and produced policy reports disconnected from production outcomes
- **Evidence**: Stated as the framing problem, with the three symptoms named
  in sequence.
- **Confidence**: settled (first-person description of the engine's documented
  open state at the start of 2026)
- **Quote**: "In a real cluster, this works perfectly. In CI/CD, without a live API server, the CLI has nowhere to resolve those lookups. Tests panic. Rules are silently skipped. Policy reports show results that bear no relationship to what will actually happen in production."
- **Our assessment**: Buy it. The three symptoms are the whole motivation and
  they map directly onto the guide's recurring theme that a green offline
  signal is not evidence of production behavior. The sharp part is
  "reports ... bear no relationship to what will actually happen" — the
  failure mode is not "the test failed," it is "the test passed while
  verifying the wrong thing."

### Claim 2: A hard panic came from wildcard `mutateExisting` rules calling `.List()` against a fake dynamic client whose scheme was missing `*List` GVK registrations
- **Evidence**: Names the exact panic string and the triggering rule shape.
- **Confidence**: settled (concrete error text, later fixed in PR #15746)
- **Quote**: "The CLI was crashing with `panic: coding error: you must register resource to list kind` when wildcard `mutateExisting` rules triggered"
- **Our assessment**: Buy it. This is a real, verbatim Go error — not a
  paraphrase — and it is the "fails loudly at the boundary" half of the story.
  The fake test double (a dynamic client) was structurally incomplete: it
  could not serve list operations a real cluster serves, so any policy path
  that lists resources died. The lesson is that a test double's *capability
  surface* must match the real dependency's, or a whole class of tests never
  runs.

### Claim 3: Modern CEL policy types had their test results silently swallowed because the engine applied rule-name matching to policy types that have no named rules by design
- **Evidence**: Names the three affected types and the mechanism.
- **Confidence**: settled (fixed in PR #15757)
- **Quote**: "Modern CEL policy types (`ValidatingPolicy, MutatingPolicy, GeneratingPolicy`) were having their test results silently swallowed because the engine was applying rule-name matching logic to policy types that don’t have named rules by design."
- **Our assessment**: Buy it, and this is the highest-value failure class in
  the post — the *silent* counterpart to Claim 2's panic. A result that is
  dropped rather than errored is the exact shape of "a gate that cannot fail
  is not a gate" (`guide/05-llm-ops-reliability.md:655`): the suite is green
  because nothing was evaluated, not because everything passed. In LLM-eval
  terms it is the same failure as an assertion that matches nothing
  (cf. `docs-promptfoo-deterministic-metrics.md` Claim 12).

### Claim 4: `MutatingPolicy`/`GeneratingPolicy`/`DeletingPolicy` had been added to the engine without updating the surrounding CLI lookup plumbing, producing six interlocking bugs in a single PR
- **Evidence**: Names the affected types, the reference behavior they should
  have matched, and the bug count.
- **Confidence**: settled (fixed in PR #15784)
- **Quote**: "And `MutatingPolicy`, `GeneratingPolicy`, and `DeletingPolicy` had all been added to the engine without the surrounding CLI plumbing ever being updated to match `ValidatingPolicy's` resource lookup behavior — which manifested as six distinct, interlocking bugs in a single PR."
- **Our assessment**: Buy it. The general pattern is *feature-parity drift
  between a new code path and the plumbing that was written for the old one*
  — new types reused the engine but not the CLI's resource-lookup contract.
  For the guide the transferable point is that "the new thing works in
  production" does not imply "the offline/CI path works," because the two
  share an interface that silently diverges.

### Claim 5: The author's first approach — unmarshalling a mock YAML into a plain map and passing it to the CEL global context — failed immediately with `no such overload` on any access to `object.metadata.namespace`
- **Evidence**: A concrete failed first attempt with the exact CEL error.
- **Confidence**: settled (first-person account of a reproduction that failed
  deterministically)
- **Quote**: "The moment any policy expression tried to access `object.metadata.namespace` or traverse the resource structure, the CEL engine threw no such overload."
- **Our assessment**: Buy it. This is the documented *wrong path* that makes
  the eventual fix meaningful. The intuitive move (a mocked single object is
  "close enough" data) produced a type error because the engine was built
  around a different shape. The guide-relevant lesson: when a test double
  fails against production code, the first instinct is often to loosen the
  code; here that instinct was wrong.

### Claim 6: Making the engine accept test-shaped data would have diverged offline behavior from production — the point of offline testing is that it is *identical* to what runs in the cluster
- **Evidence**: Stated explicitly as the reason the first approach was
  abandoned, before the boundary-adapter fix was found.
- **Confidence**: settled (a stated design principle, not an empirical result)
- **Quote**: "Modifying the core policy engine to accommodate CLI test files would have risked diverging offline behavior from production behavior. The point of offline testing is that it should be *identical* to what runs in the cluster. Any special-casing in the engine would have undermined that guarantee entirely."
- **Our assessment**: Buy it. This is the **central transferable rule** of the
  source and the thing the Prospector flagged. It generalizes directly to
  LLM eval harnesses: an eval that runs against a modified code path is
  testing the modified path, not production. The discipline is to keep the
  engine (the system under test) byte-for-byte the production engine and
  put any adaptation strictly on the test side of the seam.

### Claim 7: The Kubernetes informer cache always returns a slice of unstructured objects (`[]interface{}`), not a single JSON object — that is the shape the CEL engine and JMESPath projections are built to expect
- **Evidence**: The author's examination of the real cluster path that
  resolved the first-approach failure.
- **Confidence**: settled (a described property of Kyverno's production
  resolution path)
- **Quote**: "When Kyverno runs in a real cluster and resolves a `kubernetesResource` lookup, the cache does not return a single JSON object. It always returns a slice of unstructured objects `— []interface{},` where each element is a map\[string\]interface{} mirroring unstructured.Unstructured.Object. That is the shape the CEL engine and JMESPath projections are built to expect. That is the shape they have always received in production."
- **Our assessment**: Buy it. This is the diagnostic insight: the divergence
  was in the *input's container shape* (one object vs. a list of objects),
  and the same CEL expression that throws on a bare map succeeds on a list it
  can iterate. It is a concrete reminder that "same data" is not the same as
  "same shape," and production contracts are frequently about shape.

### Claim 8: The fix was a CLI-side translation layer (`resolveResourcesMockData`) that decodes each manifest with `runtime.RawExtension`, forces it into an unstructured map, and wraps it in an `[]interface{}` slice
- **Evidence**: Names the function and the three transformation steps.
- **Confidence**: settled (the shipped implementation; landed in PRs #15948
  and #16123)
- **Quote**: "When a user declares mock resources in their `kyverno-test.yaml`, this function uses `runtime.RawExtension` to decode each manifest, forces it into an unstructured map, and wraps the result into an `[]interface{}` slice."
- **Our assessment**: Buy it. This is the *boundary adapter* the pattern is
  named for. The adapter lives entirely in the CLI (the test harness), decodes
  the fixture with the same decoder production uses, and reshapes it to the
  production container type before handing it to the engine. Nothing in the
  policy engine changes — the fidelity is achieved by construction on the
  test side.

### Claim 9: After the adapter, the engine receives a structurally identical input and "has no idea it’s running offline" — it is disguising test data as live cluster data at the exact layer where the distinction stops mattering
- **Evidence**: The author's summary of the resulting property.
- **Confidence**: settled for the stated design intent
- **Quote**: "By the time the mock data reaches the CEL compilers or the JMESPath projections, its shape is structurally identical to what a live Kubernetes informer cache would have returned. The policy engine has no idea it’s running offline."
- **Quote**: "The CLI is not simulating offline testing — it is disguising offline test data as live cluster data, at the precise layer where the distinction stops mattering."
- **Our assessment**: Buy it. This is the cleanest statement of the pattern in
  the corpus: the adapter is not an emulation layer that approximates
  production, it is a normalization layer that makes the fixture
  indistinguishable to the consumer. "At the precise layer where the
  distinction stops mattering" is the design instruction — choose the seam
  where conformance is total and cheap.

### Claim 10: The offline mock layer landed in two PRs — #15948 introduced `apiCallResponses`/`globalContextEntries` plus HTTP mock infrastructure, and #16123 extended `GlobalContextEntryValue` with `resources`/`resourceFiles` for Kubernetes-resource-backed entries
- **Evidence**: PR numbers and the fields each added, stated by the author.
- **Confidence**: settled (named, public PRs)
- **Quote**: "This landed in two PRs: [#15948](https://github.com/kyverno/kyverno/pull/15948), which introduced `apiCallResponses` and `globalContextEntries` fields to kyverno-test.yaml along with the HTTP mock infrastructure, and [#16123](https://github.com/kyverno/kyverno/pull/16123), which extended GlobalContextEntryValue with `resources and resourceFiles` fields specifically for Kubernetes resource-backed entries — completing the offline mock layer end to end."
- **Our assessment**: Buy it. Useful as the concrete implementation trail:
  the fix is not one clever function but a small surface of new config fields
  (`apiCallResponses`, `globalContextEntries`, `resources`, `resourceFiles`,
  and later `generatedResources`, `jsonPayloads`) that let a test manifest
  declare the production-side data the engine depends on. The design lesson is
  that boundary-fidelity work shows up as *new test-fixture schema*, not as
  engine changes.

### Claim 11: A community member reported that the missing offline capability had blocked his team's CI/CD since Kyverno v1.17 and asked for a v1.18 backport — offline testability was an operational dependency, not a nicety
- **Evidence**: A public comment on the in-memory fake dynamic client PR
  (#15846), described with the versions and the requested backport.
- **Confidence**: settled (a described, public community report)
- **Quote**: "He explained that the issue had been blocking his team’s offline tests since Kyverno v1.17, and asked whether the fix could be backported to v1.18 because their CI/CD pipelines had an active dependency on it."
- **Our assessment**: Buy it. This is the strongest argument that offline
  evaluation fidelity belongs in the reliability chapter rather than the
  tooling footnote: real teams had a pipeline-level dependency on the engine
  being testable offline, and the gap silently persisted across release
  cycles. It corroborates the corpus's "offline testability is an operational
  dependency" framing (cf. `failure-litellm-server-root-path-regression.md`
  Claim 3 on the default-path CI blindspot).

### Claim 12: The in-memory fake dynamic client enabled cross-resource offline evaluation for `kyverno apply`, including LIST-style API paths
- **Evidence**: Named PR (#15846) and the LIST capability.
- **Confidence**: settled
- **Quote**: "Built the in-memory fake dynamic client for `kyverno apply`, enabling cross-resource offline evaluation including LIST-style API paths — [#15846](https://github.com/kyverno/kyverno/pull/15846)"
- **Our assessment**: Buy it. This is the enabling mechanism behind Claim 2:
  once the fake client supported `*List` GVK registrations, the wildcard panic
  disappeared and cross-resource policies became evaluable offline. The
  general point is that test-double capability coverage is a prerequisite for
  the adapter pattern to work — you cannot normalize input to a shape the
  double cannot serve.

### Claim 13: The author's stated mentorship discipline — trace a bug to a named function before asking for help, so a maintainer can unblock you in sixty seconds
- **Evidence**: Stated as the "most important lesson" from the mentorship,
  with a concrete example question.
- **Confidence**: anecdotal (a personal working practice, not a measured
  outcome)
- **Quote**: "when you ask a senior maintainer for help, don’t ask “how does this work?” Ask “I traced this to resolveResource() — is this where the offline RESTMapping fails for MutatingPolicy?” Make it possible for them to unblock you in sixty seconds."
- **Our assessment**: Buy it as a practice, grade it `anecdotal`. It is a
  transferable runbook/agent-collaboration norm — narrow an investigation to a
  named function and a specific hypothesis before escalating — but it is one
  person's advice with no measured effect, so it should not be stated as a
  settled reliability technique.

### Claim 14: The author's closing advice — do not try to comprehend a production-grade codebase whole; find one broken thing and become the domain expert of that one function
- **Evidence**: Stated as the post's closing recommendation to new
  contributors.
- **Confidence**: anecdotal (advice from one mentorship experience)
- **Quote**: "Stop trying to understand the whole repository. You will never fully comprehend a production-grade CNCF codebase in your first month, and trying to before writing a single line will paralyze you. Find one broken thing, a panic, a silent failure, a missing flag, and become the domain expert of that one specific function."
- **Our assessment**: Buy the practice, grade `anecdotal`. It mirrors the
  corpus's toil/scope-reduction habit (narrow the unit of work), but it is
  career advice, not an operational claim, and should be cited only as a
  practice note.

## Concrete Artifacts

All artifacts below are verbatim from
https://www.cncf.io/blog/2026/07/22/i-made-a-policy-engine-think-it-was-in-production.

### The rejected first approach (verbatim)

```
A user provides a YAML file mocking a Deployment. I unmarshal that YAML into a
standard map[string]interface{} and pass it into the CEL engine's global
context. Simple. It blew up instantly. The moment any policy expression tried to
access object.metadata.namespace or traverse the resource structure, the CEL
engine threw no such overload.
```

### The production input shape and the boundary adapter (verbatim)

```
I stopped looking at the CLI and started looking at the Kubernetes informer
cache. When Kyverno runs in a real cluster and resolves a kubernetesResource
lookup, the cache does not return a single JSON object. It always returns a
slice of unstructured objects — []interface{}, where each element is a
map[string]interface{} mirroring unstructured.Unstructured.Object. That is the
shape the CEL engine and JMESPath projections are built to expect. That is the
shape they have always received in production.
```

```
The breakthrough was realizing I should not touch the policy engine at all.
Instead of forcing the engine to understand my test files, I needed to make my
test files look exactly like what the engine had always seen. I built
resolveResourcesMockData: a translation layer that lives entirely in the CLI.
When a user declares mock resources in their kyverno-test.yaml, this function
uses runtime.RawExtension to decode each manifest, forces it into an
unstructured map, and wraps the result into an []interface{} slice.
```

### Failure classes and fixes (verbatim, condensed from "Clearing the ground" and "What else I shipped")

```
- Fixed hard CLI panic caused by missing *List GVK registrations in the fake
  dynamic client scheme — #15746
- Fixed silent test result swallowing for ruleless CEL policy types when a rule
  name was specified in the test manifest — #15757
- Fixed six interlocking resource lookup bugs for MutatingPolicy,
  GeneratingPolicy, and DeletingPolicy, including a missing DynamicTypeResolver
  in the DeletingPolicy CEL compiler — #15784

- Built the in-memory fake dynamic client for kyverno apply, enabling
  cross-resource offline evaluation including LIST-style API paths — #15846
- Added generatedResources plural field to TestResultData, enabling
  multi-resource verification for ruleless GeneratingPolicy tests — #16034
- Added CleanupPolicy and ClusterCleanupPolicy support to kyverno apply,
  enabling dry-run policy reports without touching the Kubernetes delete API —
  #15732

- Added --http-payload and --envoy-payload flags to kyverno apply, enabling
  offline testing of HTTP and Envoy authorization policies — #15645
- Added processor-level unit tests achieving 100% patch coverage for HTTP and
  Envoy authz evaluation paths — #15721
- Added jsonPayloads array field to the CLI test manifest, eliminating test file
  duplication for multi-payload scenarios, with full backward compatibility —
  #15584
```

## Cross-References

**Candidates from `miner-related-notes.md`** (all ten listed paths evaluated;
eight dismissed as lexically-but-not-thematically adjacent, two cited):

- `source-notes/docs-promptfoo-evaluate-openai-agents-python.md` — **cited**
  (Extends): **Claim 3** ("If you skip this exporter, Promptfoo will not see
  the SDK's tool and handoff spans, so `trajectory:*` assertions will not have
  the trace data they need") is the closest structural analogue in the corpus —
  a producer-side translation layer (the OTLP bridge) whose absence silently
  degrades a strong gate to a weaker one. That note also documents the bridge's
  job as *reshaping SDK spans into the eval's expected vocabulary*
  (`sandbox.operation`, `command`, `process.exit.code`), which is the same
  "normalize the producer's output into the consumer's expected shape" move as
  `resolveResourcesMockData`. Both are boundary adapters; that one is
  telemetry-shaped, this one is input-data-shaped.
- `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md` — **dismissed**:
  retail/gaming SLOs and user-experience alignment; no test-fidelity content.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  taxonomy. Its Claim 2 (runbook content is "essentially pseudocode") is
  thematically about automation, not test doubles; no shared claim.
- `source-notes/docs-google-sre-on-call.md` — **dismissed**: pager load and
  alerting hygiene. Unrelated.
- `source-notes/docs-google-sre-prodcast-03-13-imperative-declarative.md` —
  **dismissed**: imperative vs. declarative change workflows. No test or
  fidelity content.
- `source-notes/docs-google-sre-reliable-data-processing-minimal-toil.md` —
  **dismissed**: batch-job reliability and haunted graveyards. Unrelated.
- `source-notes/docs-google-sre-reliable-product-launches.md` — **dismissed**:
  launch coordination and gating. Unrelated.
- `source-notes/docs-google-sre-slo-engineering-case-studies.md` —
  **dismissed**: SLO adoption case studies. Unrelated.
- `source-notes/docs-google-sre-team-lifecycles.md` — **dismissed**: first-SRE
  adoption and team structure. Unrelated.
- `source-notes/blog-cncf-securing-cicd-credentials-verification.md` —
  **dismissed**: CNCF CI/CD credential isolation and signing — same publisher
  and same "CI reliability" umbrella, but the subject is supply-chain
  credentials, not test-input fidelity. No shared claim; citing it would be
  thematic, not evidential.

**Additional cross-references found by searching `source-notes/` and `guide/`:**

- `source-notes/blog-litellm-april-townhall-updates.md` — **cited**
  (Corroborates/Extends): **Claim 5** is the guide's existing environment-
  divergence resolution — "all UI QA will be performed in the built Docker
  image that users run" — i.e. **artifact parity** (the test runs the shipped
  artifact). This source is **input parity** (the test feeds the artifact
  production-shaped data). Both resolve "test env ≠ production env," but on
  opposite sides of the boundary; the two together give the guide both
  resolution strategies. The guide's rule at
  `guide/05-llm-ops-reliability.md:47` currently cites only that note's Claim 5.
- `source-notes/failure-litellm-server-root-path-regression.md` — **cited**
  (Corroborates): **Claim 3** ("No automated test verified that `root_path` was
  set on the FastAPI app. No manual test procedure existed for
  `SERVER_ROOT_PATH` functionality. Default deployments ... were unaffected, so
  most CI tests passed.") is the equivalent "green suite, untested path"
  failure class in the LLM-gateway domain, and **Claim 5** is the analogous
  remedy — a PR-gated CI workflow that boots the real artifact **under the
  non-default config** and asserts the user-visible surface. That is the same
  "gate the production-shaped case, not the convenient one" instruction this
  source applies to input shape.
- `source-notes/docs-litellm-mock-requests.md` — **cited** (Contrasts/Extends):
  **Claim 10** places three test-only mocking knobs at three layers and finds
  that `mock_response` "is the cheapest and the most destructive" — a green
  mocked suite is "evidence about your parsing and branching, and is silent
  evidence about your gateway." That is the *opposite design philosophy* to
  this source: LiteLLM's mock deliberately bypasses the gateway for cost;
  Kyverno's adapter deliberately preserves the engine for fidelity. Both
  answers to the same question — *what does a green test prove?* — make the
  fidelity-vs-cheapness tradeoff explicit and are worth cross-linking.
- `source-notes/docs-promptfoo-deterministic-metrics.md` — **cited**
  (Corroborates, fail-closed precedent): **Claim 12** — the trace/trajectory
  assertion family throws when trace data is absent rather than silently
  passing — is the corpus's fail-closed counterexample to this source's
  silent-drop failure class (Claim 3). Together they bound the design space:
  a gate should fail when its required input is missing, not pass green.
- `source-notes/docs-promptfoo-guardrails-assertions.md` — **cited**
  (Corroborates): **Claim 1** establishes the `guardrails` assertion as "a
  verdict reader, not a guardrail runner ... It reads the normalized
  `guardrails` field on the provider response," with a documented silent
  fail-open when the field is omitted (cited in the guide's
  "A gate that cannot fail is not a gate" table,
  `guide/05-llm-ops-reliability.md:671`). Same shape as this source's
  silently-swallowed results: a gate that reads a signal that may be absent
  passes when the signal never arrived.

**Primary cross-references:**

- **Corroborates**:
  - `blog-litellm-april-townhall-updates.md` **Claim 5** — artifact parity vs.
    this source's input parity; both are "make the test exercise the
    production thing." See above.
  - `failure-litellm-server-root-path-regression.md` **Claim 3** — "most CI
    tests passed" while the regressed non-default path had zero coverage. This
    source's silently-swallowed results (Claim 3) are the same class: a green
    signal over an untested path.
  - `failure-litellm-server-root-path-regression.md` **Claim 5** — the durable
    fix is a gate that boots the real artifact under the non-default config;
    this source's durable fix is a boundary adapter that feeds the real engine
    production-shaped input. Both are "gate the production case."
  - `docs-promptfoo-deterministic-metrics.md` **Claim 12** — the fail-closed
    precedent: assertions throw when their required input is absent rather
    than passing. This source's silent drop is the fail-open anti-pattern.
  - `docs-promptfoo-guardrails-assertions.md` **Claim 1** — the
    verdict-reader-with-a-missing-signal pass (already in the guide's
    cannot-fail table) is the same structural hazard as a policy result that
    is silently dropped.

- **Contradicts**: None. No existing source note claims that forking the
  engine to accept test-shaped input preserves fidelity, or that silently
  dropped results are acceptable. Checked `CONTRADICTIONS.md` and the
  candidate list; nothing opposes this source. No contradiction issue filed.

- **Extends**:
  - `docs-promptfoo-evaluate-openai-agents-python.md` **Claim 3** — the OTLP
    bridge as a producer-side translation layer; extends the "boundary
    normalization" idea from telemetry spans (that note) to policy-engine
    input data (this note).
  - `blog-litellm-april-townhall-updates.md` **Claim 5** — extends the guide's
    single environment-divergence rule (artifact parity) with its input-side
    complement (input parity).
  - `docs-litellm-mock-requests.md` **Claim 10** — the three-layer mocking
    taxonomy (SDK stub / Router flag / httpx transport) is the corpus's map of
    *where* a test double sits; this source adds the design constraint that
    governs *how faithful* it must be at that layer.

- **Novel**: First source note in the corpus covering:
  1. The **boundary-adapter / "disguise the fixture as production data"**
     pattern: conform the test *input* to the production shape at a seam,
     never fork the system under test.
  2. The **input-parity** resolution to environment divergence (the guide
     currently carries only artifact parity).
  3. The specific Kyverno offline failure classes: a `*List` GVK
     panic on wildcard `mutateExisting` rules, silent result swallowing for
     ruleless CEL policy types, and six interlocking lookup bugs across the
     newer policy types.
  4. The concrete boundary-adapter implementation (`resolveResourcesMockData`
     decoding via `runtime.RawExtension`, forcing an unstructured map,
     wrapping in `[]interface{}`) and the fixture-schema fields it added.
  5. A documented community report that missing offline testability blocked a
     team's CI/CD across release cycles.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**, `### Test in the environment you ship`
  (`guide/05-llm-ops-reliability.md:47`): The section currently resolves
  environment divergence only one way — gate QA on the built artifact,
  citing `blog-litellm-april-townhall-updates` Claim 5. Add the **input-parity**
  counterpart as a second, explicit strategy: when an offline harness must
  call production code, conform the *input* to the production shape at the
  boundary rather than special-casing the engine. Cite this source's Claims
  6–9. Suggested rule text: **"Match the production shape at the seam where
  the distinction stops mattering; never fork the engine to accept test-shaped
  data — that divergence is exactly what offline testing exists to prevent."**
- **Chapter 05**, `### A gate that cannot fail is not a gate`
  (`guide/05-llm-ops-reliability.md:655`): The table lists config properties
  that make a gate incapable of failing. Add the **silently-swallowed-input**
  row class: a gate that drops results it cannot evaluate passes green while
  verifying nothing (this source's Claim 3; corroborated by
  `failure-litellm-server-root-path-regression` Claim 3 and
  `docs-promptfoo-deterministic-metrics` Claim 12). Contrast with the
  fail-closed precedent (trace assertions that throw). This is a *data-shape*
  property, not a config property, so it belongs alongside the config table as
  a second mechanism for a non-discriminating gate.
- **Chapter 03 (Runbooks and Agents)**: The triage flagged executable-spec /
  policy-as-code artifacts. The `kyverno-test.yaml` fixture-schema fields
  (`apiCallResponses`, `globalContextEntries`, `resources`, `resourceFiles`,
  `generatedResources`, `jsonPayloads`) are a concrete example of a test
  manifest that declaratively supplies the production-side data an
  evaluator needs — a pattern transferable to LLM-eval fixtures that must
  declare their own dependencies. Cite Claim 10.
- **Chapter 06 (Security and Trust)**: Adjacent only. The policy engine
  enforces admission control, but this source's AI/LLM content is nil; do
  **not** add Kyverno CLI detail. If the chapter already discusses
  enforcement gates with integrity preconditions (e.g.
  `docs-promptfoo-guardrails-assertions` Claim 1), this source can supply the
  "gate reads a signal that may be silently absent" example (Claim 3).
- **Chapter 00 (Principles)**: The "do not special-case the engine" rule
  (Claim 6) and the "make the test indistinguishable at the boundary"
  instruction (Claim 9) are clean statements of the test-fidelity principle
  and usable as a Ch00 example. Cite Claims 6 and 9.

## Extraction Notes

- Source read in full: the CNCF Project Maintainer Post page (published
  2026-07-22, ~11 KB of extractable body text). The author's external links —
  the Unified CLI project issue (#15264), the twelve Kyverno PRs, the website
  docs PR (#1979), the LFX Mentorship Program, and the two linked flow-chart
  images — were **not** fetched: they are forks/artifacts of the described
  work, and the post summarizes each in one line. No sub-page was needed to
  extract the claims. All quoted passages were copied character-for-character
  from the fetched page text; where the page's rendered text interleaved
  emphasis or link markup inside a sentence, only the contiguous fragment was
  quoted.
- `date_published` set to 2026-07-22 (page dateline). `date_extracted` and
  `last_checked` set to 2026-10-15 UTC.
- `confidence_overall` set to `emerging`: this is a first-person,
  self-reported engineering account. The failure classes are backed by exact
  error strings and named public PRs, and the fix is described at the function
  level, but there are no benchmarks, no independent verification, and the
  post's adopters are inferred from one community comment. Claims 13 and 14
  are explicitly graded `anecdotal` (personal practice/career advice). The
  overall posture is therefore emerging rather than settled.
- The `miner-related-notes.md` candidates list was read per MINER.md §4. All
  ten listed paths were evaluated: two cited
  (`docs-promptfoo-evaluate-openai-agents-python.md`) and eight explicitly
  dismissed (see Cross-References). The useful cross-references
  (`blog-litellm-april-townhall-updates`, `failure-litellm-server-root-path-regression`,
  `docs-litellm-mock-requests`, `docs-promptfoo-deterministic-metrics`,
  `docs-promptfoo-guardrails-assertions`) were discovered by searching
  `source-notes/` and `guide/` directly; each cited claim was re-read and
  verified per MINER.md §4b against the named note (Claim 5 of the townhall
  note; Claims 3 and 5 of the server-root-path note; Claim 10 of the
  mock-requests note; Claim 12 of the deterministic-metrics note; Claim 1 of
  the guardrails note; Claim 3 of the evaluate-openai-agents-python note).
- The Prospector's caveats were respected: (1) no quantitative metrics were
  reported by the source, so no measured reliability improvement is implied
  anywhere in this note; (2) the domain is Kubernetes policy-as-code, not LLM
  serving, so the guide-impact recommendations carry the transferable
  *testing-fidelity pattern* and explicitly warn against importing
  Kyverno-specific CLI detail (see Ch06).
- No contradiction issue filed: verified against `CONTRADICTIONS.md` (no
  relevant open entries) and the overlapping notes. The near neighbours
  (`blog-litellm-april-townhall-updates`, `docs-litellm-mock-requests`) are
  complementary resolution designs, not opposing claims.
