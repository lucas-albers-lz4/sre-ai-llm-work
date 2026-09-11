---
source_url: https://www.promptfoo.dev/docs/configuration/datasets/
source_type: docs
title: "Promptfoo Configuration: Dataset Generation"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-11
date_extracted: 2026-09-11
last_checked: 2026-09-11
status: current
confidence_overall: emerging
issue: "#1277"
---

# Promptfoo Configuration: Dataset Generation

> The vendor reference for `promptfoo generate dataset` — the command that
> synthesizes eval test cases with an LLM instead of curating them from real
> traffic. Primary contribution: the concrete CLI/config surface (generation as a
> distinct design-time step, a synthesis provider explicitly separate from the
> providers under test, and the persona/count breadth knobs), plus a bounded
> reproducibility finding — generated fixtures are non-deterministic by
> construction ("new, unique test cases" per run) and the documented surface
> offers no pinning or versioning story, which sits in direct tension with the
> guide's hermetic-eval rule at `guide/05-llm-ops-reliability.md:167-170`.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo "Dataset generation" configuration page)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  `promptfoo generate dataset` command's own interface — authoritative for
  documented product behavior, but vendor-positioned: the page reports no
  metrics, failure data, or independent validation of the operational claims.
  The flag/default surface is directly checkable against an installed CLI.
- **Scope**: Covers the `promptfoo generate dataset` command only — prompts
  preparation, output modes (`stdout`/`-o`/`-w`), loading generated output back
  into `tests:`, the parameter table, and custom generation providers
  (`--provider`, `file://synthesis-provider.yaml`, Python providers). Does NOT
  cover the eval run itself (the `tests:`/`providers:` surface that consumes
  generated fixtures), red-team configuration, code scanning, or caching
  (covered by sibling pages and notes).
- **Last updated**: Sep 11, 2026 by renovate[bot]; the page is undated but the
  documented examples describe the current `gpt-5` / `gpt-5.2` era.

## Extracted Claims

### Claim 1: `promptfoo generate dataset` is a distinct, design-time step that reads the config's `prompts` and any existing `tests` and emits new, unique test cases — the resulting fixture must then be wired back into the `tests:` block before it gates anything
- **Evidence**: The "Run `promptfoo generate dataset`" intro sentence plus the
  "Loading from output files" section: output goes to stdout by default, to a
  file with `-o tests.yaml` / `-o tests.csv`, or into the config in-place with
  `-w`, and when `-o` is used the generated dataset must be referenced from the
  `tests:` block (shown as `- file://tests.csv`) to be used by the eval.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Dataset generation uses your prompts and any existing test cases to generate new, unique test cases that can be used for evaluation."
- **Our assessment**: This is the separation the Prospector flagged: generation
  is not the eval run, and only the eval run is what gates CI. The `-w` mode is
  the reliability-relevant variant — it rewrites the config's test set, so a
  regeneration between a canary and its control silently changes the eval
  inputs. The `-o` boundary is the safe path: emit a fixture, commit it, then
  reference it by file.

### Claim 2: The generation provider is explicitly separate from the providers under test — `--provider` selects the LLM that writes test cases while the config's `providers` block lists the targets being tested, and generation defaults to OpenAI via `OPENAI_API_KEY`
- **Evidence**: The "Using a custom provider" section's separation sentence and
  the default-OpenAI statement, plus the parameter-table entry for `--provider`
  ("Provider to use for the dataset generation. Eg: openai:chat:gpt-5").
- **Confidence**: settled (documented product behavior)
- **Quote**: "The `--provider` flag specifies the LLM used to generate test cases. This is separate from the providers in your config file (which are the targets being tested)." and "By default, dataset generation uses OpenAI (`OPENAI_API_KEY`)."
- **Our assessment**: This is the key coupling risk: your gate's input
  distribution is authored by a model you are not testing, on credentials and a
  cost/quota budget line that are distinct from the eval's. A synthesis-model
  upgrade silently reshapes the test-case distribution without touching the
  `providers` block — the same "model change masquerading as no change" hazard
  the corpus documents for the eval path itself
  (`blog-promptfoo-model-upgrades-break-agent-safety.md` and
  `docs-promptfoo-configuration-caching.md`).

### Claim 3: The generation provider can be given a full provider config via `file://synthesis-provider.yaml` (with `reasoning.effort` and `max_output_tokens`) or a Python provider via `file://synthesis-provider.py`
- **Evidence**: The "Custom provider" section's two `file://` invocations and the
  annotated `synthesis-provider.yaml` example (`id: openai:responses:gpt-5.2`
  with a `reasoning.effort: medium` config and `max_output_tokens: 4096`).
- **Confidence**: settled (documented product behavior)
- **Quote**: "For more control, create a provider config file:" and "You can also use a Python provider:" and "promptfoo generate dataset --provider file://synthesis-provider.yaml" (see Concrete Artifacts for the full example)
- **Our assessment**: The `file://` mechanism means the synthesis provider can be
  pinned to a specific model with bounded output tokens — the closest thing on
  this page to reproducibility control. Even so, the mechanism only pins the
  *authoring* model; it does not pin the emitted test cases themselves.

### Claim 4: The only documented breadth and cost levers are `--numPersonas` × `--numTestCasesPerPersona` plus free-text `--instructions` — nothing in the documented surface bounds generation toward failure modes the authoring model doesn't already anticipate
- **Evidence**: The parameter table entries for the three flags (verbatim in
  Concrete Artifacts) and the instructions example
  `--instructions "Consider edge cases related to international travel"`.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Number of personas to generate for the dataset." and "Number of test cases to generate per persona." and "Specific instructions for the LLM to follow when generating test cases."
- **Our assessment**: Persona/count is the only stated lever for coverage
  breadth, and case count is a direct spend multiplier on the generation budget
  line. There is no documented way to steer generation toward known
  failure-mode classes beyond free-text instructions — a model that cannot
  imagine the failure mode cannot be instructed to probe it.

### Claim 5: Generated test cases are non-deterministic by construction and the documented surface offers no pinning, versioning, or seed story for a generated dataset — the reproducibility-feature absence is itself the finding
- **Evidence**: The page's own wording that each run produces "new, unique test
  cases," combined with a full read of the page showing no mention of seeds,
  deterministic regeneration, versioning, or snapshot pinning anywhere in the
  documented surface.
- **Confidence**: emerging (mechanism wording is settled; the "no pinning exists"
  claim rests on absence and is the Miner's bounded finding)
- **Quote**: "Dataset generation uses your prompts and any existing test cases to generate new, unique test cases that can be used for evaluation."
- **Our assessment**: Two Eval runs on two separately-generated fixture files are
  not the same eval — regression or canary/control comparisons then conflate
  input-set drift with model-behavior deltas. There is no documented answer to
  "pin this generated dataset" on the page. This is in direct tension with the
  guide's hermetic rule (`guide/05-llm-ops-reliability.md:167-170`: "A prompt
  config that references a mutable external dataset is not hermetic and
  therefore not safely rollable"): the *generator* is the mutable external
  dataset, and nothing here makes it immutable. Contrast with
  `docs-langfuse-datasets.md` (Claims 4/5), which ships timestamp-pinned,
  versionable datasets as the reproducibility primitive.

### Claim 6: The vendor's own framing — the dataset "should closely represent true inputs into your LLM app" — sits in tension with a mechanism that synthesizes rather than samples inputs from production
- **Evidence**: The page's opening sentence (the framing claim) read against the
  whole documented mechanism, which generates cases from prompts plus existing
  tests — nothing on the page samples production traffic, unlike the trace-linked
  curation path in `docs-langfuse-datasets.md` (Claim 2).
- **Confidence**: emerging
- **Quote**: "Your dataset is the heart of your LLM eval. To the extent possible, it should closely represent true inputs into your LLM app."
- **Our assessment**: The aspiration and the mechanism part ways: LLM synthesis
  extrapolates from the prompts/tests you already have and is bounded by what
  the authoring model imagines — it cannot recover the distribution of real
  inputs unless it is told what those look like. Generated datasets belong in
  the breadth/edge-case role (per Claim 4), not as a substitute for
  production-derived evidence in a deploy-gate eval.

## Concrete Artifacts

### Command surface (verbatim from the "Run `promptfoo generate dataset`" and options sections)

```
promptfoo generate dataset

promptfoo generate dataset -o tests.yaml

promptfoo generate dataset -o tests.csv

promptfoo generate dataset -w
```

### Loading generated output back into the config (verbatim from the "Loading from output files" section) — the fixture is referenced from `tests:` as `file://tests.csv`

```yaml
prompts:
  - 'Act as a travel guide for {{location}}'
  - 'I want you to act as a travel guide. I will write you my location and you will suggest a place to visit near my location. In some cases, I will also give you the type of places I will visit. You will also suggest me places of similar type that are close to my first location. My current location is {{location}}'

tests:
  - file://tests.csv
  - vars:
      location: 'San Francisco'
  - vars:
      location: 'Wyoming'
  - vars:
      location: 'Kyoto'
  - vars:
      location: 'Great Barrier Reef'
```

### Parameter table (verbatim from the "Customize the generation process" section)

| Parameter | Description |
|---|---|
| `-c, --config` | Path to the configuration file. |
| `-i, --instructions` | Specific instructions for the LLM to follow when generating test cases. |
| `-o, --output [path]` | Path to output file. Supports CSV and YAML. |
| `-w, --write` | Write the generated test cases directly to the configuration file. |
| `--numPersonas` | Number of personas to generate for the dataset. |
| `--numTestCasesPerPersona` | Number of test cases to generate per persona. |
| `--provider` | Provider to use for the dataset generation. Eg: openai:chat:gpt-5 |

### Custom instructions example (verbatim)

```
promptfoo generate dataset --config path_to_config.yaml --output path_to_output.yaml --instructions "Consider edge cases related to international travel"
```

### Synthesis provider config (verbatim from the "Using a custom provider" section)

```yaml
id: openai:responses:gpt-5.2
config:
  reasoning:
    effort: medium
  max_output_tokens: 4096
```

```
promptfoo generate dataset --provider file://synthesis-provider.yaml
```

### Python provider and provider-string invocations (verbatim)

```
promptfoo generate dataset --provider file://synthesis-provider.py
```

```
promptfoo generate dataset --provider openai:chat:gpt-5-mini
```

Source for all artifacts: https://www.promptfoo.dev/docs/configuration/datasets/ — sections as noted. All copied character-for-character from the rendered page.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-langfuse-datasets.md` **Claim 9** (LLMs are good at
    generating synthetic examples to bootstrap a dataset) — two independent
    vendors document LLM-synthesis as a recognized dataset bootstrapping
    strategy; this page is the dedicated-command materialization of the pattern
    Langfuse describes as a feature section. (Verified: #196 Claim 9.)
  - `source-notes/blog-promptfoo-model-upgrades-break-agent-safety.md` **Claim 2**
    (model upgrades must be treated as changes — pin model IDs, do not ship
    "latest") — the dataset page's `--provider` / default-OpenAI surface is a
    second place the "pin your model" discipline applies: an unpinned synthesis
    provider is a drifting input-authoring model. Same vendor, same upgrade-risk
    doctrine, different invocation site. (Verified: #482 Claim 2.)
- **Contradicts**: None found, and no contradiction issue filed. The closest
  surface is the tension between this page's silent non-determinism (Claim 5)
  and `docs-langfuse-datasets.md`'s timestamp-pinned versioning (Claims 4/5) —
  but that is a *missing feature in one tool* versus a *shipped feature in
  another*, not an opposing claim on the same ground; both vendors would agree
  reproducibility of an eval fixture is desirable. It also opposes no source
  note claim: the hermetic rule it strains lives in `guide/05` and is cited as
  a guide-impact finding, not as a source-vs-source contradiction. Verified
  against `CONTRADICTIONS.md` (no open `C-NNN` entries beyond #1150, which is an
  unrelated LiteLLM-routing contradiction) and open `contradiction`-labeled
  issues (only #1150).
- **Extends**:
  - `source-notes/docs-langfuse-datasets.md` — extends the corpus's dataset
    sourcing coverage with the synthetic branch: #196 covers curated,
    trace-linked, timestamp-versioned datasets (Claims 2, 4, 5); this page
    covers LLM-generated, non-deterministic-by-default fixtures. Together they
    bound the "when is a dataset admissible as gate evidence" question —
    versioned-curated vs unversioned-synthesized. (Verified: #196 Claims 2/4/5.)
  - `source-notes/docs-promptfoo-configuration-caching.md` **Claim 4** (cached
    eval responses replay for up to 14 days after a silently changed provider
    behavior) — with #482 Claim 2, this is the third independent way a "passing"
    eval stops being evidence about the live system: model upgrade replay
    (#1275), prompt/config drift (#482), and dataset regeneration (this page).
    All three are config surfaces where "the gate is green" and "production is
    exercised" separate. (Verified: #1275 Claim 4.)
  - `source-notes/docs-langfuse-roadmap.md` **Claim 4** (Langfuse lists
    "synthetic data generation" among prioritized future workflows) — a
    competing vendor treating LLM-based data generation as roadmap work is a
    "vendor thinks this is hard" signal that tempers any reading of this page as
    a solved problem. (Verified: #320 Claim 4.)
  - `source-notes/docs-promptfoo-code-scan-cli.md` / `docs-promptfoo-chat-threads.md`
    — siblings in the same vendor docs family (#1264/#1276) with the same
    CI-gating framing; this page adds the input-fixture side behind an
    eval-driven CI gate, complementing the scanner and chat-thread surfaces.
- **Novel**: This is the first source note covering **synthetic eval-dataset
  generation** as an eval-harness workflow. The corpus's dataset material
  (`docs-langfuse-datasets.md`) is the curated half of the pattern only.
  Specifically new:
  1. **The synthesis-provider / target-provider separation** (Claim 2) — the
     gate's input distribution is authored by a model you are not testing, on a
     separate cost/budget line.
  2. **The by-construction non-determinism of generated fixtures with no
     documented pinning story** (Claim 5) — the first concrete counter-example
     surfaced against the guide's hermetic-eval rule.
  3. **The design-time / per-run split** — generation as a distinct step whose
     artifact must be committed and referenced (`- file://tests.csv`) before it
     can gate anything (Claim 1).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — evaluation and measurement methodology /
  the hermeticity rule**: `guide/05-llm-ops-reliability.md:167-170` states "A
  prompt config that references a mutable external dataset is not hermetic and
  therefore not safely rollable." Add a dataset-sourcing sub-rule: an eval gate
  must treat the *dataset itself* as a fixture with a version — either curated
  and pinned (as in `docs-langfuse-datasets.md` Claims 4/5) or, for synthetic
  generation, committed as a snapshot artifact (`-o tests.yaml` then
  `tests: - file://tests.yaml`) and never regenerated between canary and
  control; `-w` in-place regeneration is the anti-pattern that silently mutates
  the gate's inputs (Claim 1, Claim 5). Add generation logic to the eval cost
  accounting: `--numPersonas` × `--numTestCasesPerPersona` on the generation
  provider is a separate spend multiplier from eval cost (Claim 4), and record
  the synthesis model as part of eval provenance because it is a drifting input
  author (Claim 2, corroborating #482's pin-model-IDs rule).
- **Chapter 02 (Observability) — eval-input provenance**: Extend the
  coverage-gap rule at `guide/02-observability.md:161` ("cluster production LLM
  traffic by topic to find eval-coverage gaps"). Synthetic generation is the
  complement to traffic clustering: it manufactures breadth/rare-edge cases that
  observed traffic may not contain — but generated inputs are **not** evidence
  about the real production input distribution, so a gate fed only synthetic
  cases has a provenance gap (Claim 6). The guide should state: real-traffic
  clustering answers "what inputs are we missing"; synthesis answers "what inputs
  could exist"; only the former is evidence of what users actually send.
- **Chapter 03 (Runbooks and Agents) — agent-change replay / eval datasets**: When
  replaying historical trajectories or agent changes (the golden-label section at
  `guide/03-runbooks-and-agents.md:176-189`), generated test cases are suitable
  for edge-case *exploration* but must not be the deploy-gate for agent behavior,
  where versioned, trace-linked fixtures are the admissible evidence
  (contrasting `docs-langfuse-datasets.md` Claims 2/5).

## Extraction Notes

- Source read in full via direct fetch of the Docusaurus page. Single
  self-contained page (~1.4k words); the linked `tests`/`prompts` config pages and
  the next-page "HuggingFace Datasets" were not followed — they document the eval
  consumer surface, not the generation command this issue targets. Quotes were
  verified against the fetched rendered content character-for-character before
  writing; code blocks were copied verbatim.
- Per the Prospector's superseding instruction, the note deliberately avoids a
  general "promptfoo has a dataset generator" writeup and extracts only (a) the
  concrete flag/config surface as a checkable reference and (b) the
  reproducibility tension against the Ch05 hermetic rule as a bounded claim.
- The "no pinning/versioning story" finding (Claim 5) rests on absence: a full
  read of the page surfaced no mention of seeds, deterministic regeneration,
  versioning, or snapshot pinning for generated datasets. Only the synthesis
  *provider* is pinnable (via `file://synthesis-provider.yaml`), which pins the
  authoring model, not the emitted cases.
- `confidence_overall` is `emerging`: the documented mechanism/default claims
  (Claims 1-4) are settled-for-product-behavior, but the page carries no
  metrics or failure data, and the load-bearing findings (Claim 5's absence,
  Claim 6's tension) are the Miner's synthesis over vendor documentation.
  `date_published` uses the page's "Last updated Sep 11, 2026" date (undated page).
- **Candidate dismissal** (from `miner-related-notes.md`, read before
  Cross-References; candidates are suggestions only — cited or dismissed by name):
  - `docs-google-sre-team-lifecycles.md`, `docs-google-sre-eliminating-toil.md`,
    `docs-google-sre-reliable-product-launches.md` — Google SRE org/workflow
    chapters; unrelated to eval-dataset generation; dismissed.
  - `blog-promptfoo-owasp-red-teaming.md` — OWASP red-team methodology and SDLC
    phases; same vendor, testing-domain adjacency, but no dataset-generation
    surface; dismissed.
  - `blog-promptfoo-red-team-claude.md` — model red-team plugin config; no
    dataset-generation content; dismissed.
  - `blog-pagerduty-sre-agent-triage.md`, `docs-langfuse-mcp-server.md`,
    `docs-google-sre-prodcast-04-09-ai-agents.md`,
    `docs-google-sre-prodcast-04-05-furino-slos.md`,
    `docs-google-sre-prodcast-05-05-brady-operating-systems.md` — AI-incident
    triage, MCP tooling, agent spectrum, SLO construction, OS fleet mgmt; no
    dataset-generation content; dismissed.
  - The relevant cross-refs (`docs-langfuse-datasets.md`,
    `blog-promptfoo-model-upgrades-break-agent-safety.md`,
    `docs-promptfoo-configuration-caching.md`, `docs-langfuse-roadmap.md`,
    `docs-promptfoo-code-scan-cli.md`) were found by searching `source-notes/`
    per the Prospector's guidance; each cited claim was re-read and verified per
    MINER.md §4b before citation.
- No contradiction issue filed; see Cross-References → Contradicts for the
  reasoning (absence-vs-feature between tools, not an opposing claim).