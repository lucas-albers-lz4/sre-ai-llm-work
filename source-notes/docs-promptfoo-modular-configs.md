---
source_url: https://www.promptfoo.dev/docs/configuration/modular-configs
source_type: docs
title: "Promptfoo Configuration: Managing Large Configurations — File Composition, Per-Environment Providers, and TS Configs"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-30
date_extracted: 2026-10-01
last_checked: 2026-10-01
status: current
confidence_overall: emerging
issue: "#1527"
---

# Promptfoo Configuration: Managing Large Configurations

> The vendor page on *decomposing* an eval config rather than configuring a
> single assertion: `file://` splitting of all four top-level keys, per-domain
> and per-environment file trees, per-provider `requestsPerMinute` caps that
> live in the environment's provider file, YAML anchors for reusable assertion
> blocks, `process.env.TEST_MODE`-keyed quick-vs-comprehensive suite selection,
> and TypeScript configs that import a Zod response schema out of the
> application under test — plus one flat contradiction with the sibling
> Configuration Guide about where secrets belong.

## Source Context

- **Type**: docs
- **Author credibility**: Promptfoo's own product documentation for
  promptfoo. Primary and authoritative on what the config loader accepts, but
  it is a *how-to* page, not a report: no measured outcomes, no failure data,
  no independent validation, and no stated rationale for any recommendation.
  Every YAML and TS block is presented as copy-pasteable without a worked
  result. Content is post-Dec-2025 (references `gpt-5.2`, `claude-sonnet-5`,
  `gpt-5.4-mini`). Page footer: "Last updated on Oct 1, 2026 by
  renovate\[bot]" — the last edit is an automated dependency bump, so the
  content is unowned prose refreshed by bot, which bears on how much weight
  the page's *advice* (as opposed to its *syntax*) can carry.
- **Scope**: covers only configuration organization and composition. It does
  **not** cover assertion semantics (owned by sibling notes), the `env`
  resolution/security semantics (owned by
  `docs-promptfoo-configuration-guide.md` Claim 7 — and contradicted here, see
  below), dataset generation, CI wiring, or results retention. Every claim
  below is "this is what the config loader accepts," not "this is a good
  operational practice."

## Extracted Claims

### Claim 1: A single eval config can be split across files — `file://` is accepted on each of the four top-level keys (`prompts`, `providers`, `tests`, `defaultTest`) individually, so the root config degenerates into a manifest of paths

- **Evidence**: The "Separate Configuration Files" section's four
  copy-pasteable blocks. The root config carries only `description` plus four
  path-valued keys; the referenced files each hold one concern (prompt list,
  provider list, default assertions). `defaultTest` is loaded as
  `file://configs/default-test.yaml` — an assertion set hoisted out of the
  root file, not a test case.
- **Confidence**: settled (documented product behavior; corroborated by the
  Configuration Reference's `defaultTest` type, `file://${string} |
  Partial Test Case`)
- **Quote**: "Split your configuration into multiple files based on
  functionality:" (section lead-in, verbatim) — followed by the root block
  `prompts: file://configs/prompts.yaml` / `providers:
  file://configs/providers.yaml` / `tests: file://configs/tests/` /
  `defaultTest: file://configs/default-test.yaml`
- **Our assessment**: Buy the mechanism, and note what the root file becomes:
  a manifest with no assertions in it. That matters for review and for diffs
  — the policy a reviewer is looking for ("what does every case in this suite
  assert?") lives one indirection away in `configs/default-test.yaml`, not in
  the file a reviewer opens. The path-vs-inline tradeoff is real and the page
  does not discuss it. One concrete risk the page does not flag: `file://`
  paths are resolved relative to the config file directory (Configuration
  Reference, `basePath` row: "Base directory for local file references.
  Relative values resolve from the config file directory. Defaults to that
  directory."), so moving or vendoring a config tree changes what the paths
  mean unless `basePath` is set — a portability property that only appears on
  a different page.

### Claim 2: `tests:` accepts a *list of directory* paths (`file://tests/accuracy/`, `.../safety/`, `.../performance/`, `.../edge-cases/`), so per-domain suites are added by appending a directory, not by editing the root config

- **Evidence**: The "Test Case Organization" section — the multi-domain root
  config and a `tests/accuracy/math-problems.yaml` showing a domain file
  carrying its own `vars` and `assert` blocks.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Organize test cases by domain or functionality:" (verbatim), with
  the root config listing `tests:` followed by the four
  `- file://tests/<domain>/` entries (see Concrete Artifacts)
- **Our assessment**: The operational content is the *directory* form, which
  makes a new domain a one-line change that cannot be expressed as a
  hand-maintained list. The same property has a cost the page never names: a
  globbed directory fans in whatever files are present, so the gate's coverage
  changes when someone drops a file in — and there is no manifest of expected
  domains to diff. Note this is a *different* composition mechanism from the
  `-c` glob discussed in `docs-promptfoo-configuration-guide.md` Claim 11
  (multiple configs combined into one eval): here the fan-in happens inside a
  single config's `tests:` key. Both end at one aggregate verdict, but they
  are not interchangeable, and the page links to neither.

### Claim 3: Rate-limit policy is expressed *in the environment's provider file*, not in the test suite — the documented per-provider caps (`requestsPerMinute: 100` for the OpenAI provider, `50` for the Anthropic provider) sit in `configs/providers-prod.yaml`, alongside production sampling parameters (`temperature: 0.1`, `max_tokens: 500`)

- **Evidence**: The "Environment-Specific Configurations" section's
  `configs/providers-prod.yaml` block, headed by the in-file comment
  "Production providers with rate limiting", contrasted against the
  non-environmental `configs/providers.yaml` in Claim 1's section, which
  carries `temperature: 0.7` / `max_tokens: 1000` and **no** rate limits.
  The provider labels also change (`gpt-5.2-prod`, `claude-sonnet-prod` vs
  `gpt-5.2`, `claude-sonnet`), so a prod run's results are attributable to a
  distinct provider identity.
- **Confidence**: emerging (the mechanism is documented product behavior; the
  field itself is not corroborated anywhere else — see Our assessment)
- **Quote**: "Create environment-specific configurations:" (verbatim) — the
  caps appear only inside the fenced `configs/providers-prod.yaml` block
  (`requestsPerMinute: 100` / `requestsPerMinute: 50`)
- **Our assessment**: The separation-of-concerns move is the real content and
  it is good: a rate-limit change is a one-file diff that cannot be confused
  with a change to what is being tested, and the sampling parameters move with
  the environment rather than drifting per-developer. The `-prod` label
  suffixes matter more than they look — an eval result that names
  `gpt-5.2-prod` is distinguishable in a report from one that names
  `gpt-5.2`, which is the minimum needed to tell "the model changed" from "the
  config changed."

  The caveat is that `requestsPerMinute` appears nowhere else I could check.
  It is absent from the Configuration Reference page
  (https://www.promptfoo.dev/docs/configuration/reference/) and from the
  machine-readable schema every snippet on this page declares
  (`# yaml-language-server: $schema=https://promptfoo.dev/config-schema.json`,
  https://promptfoo.dev/config-schema.json) — zero occurrences of the string
  `requestsPerMinute` in either. That is not proof the field is ignored: the
  schema leaves a provider's `config` object completely untyped (`"config":
  {}`), so it would not catch the field either way. But the practical
  consequence for the guide stands: **the field the page presents as
  production rate limiting is not schema-validated, so a typo in it fails
  silently** — the eval runs at unbounded concurrency and nothing in the
  report says so. If the guide recommends per-environment rate caps, it should
  recommend verifying the field against the installed promptfoo version
  rather than trusting the schema.

### Claim 4: `env:` is loadable from a file (`env: file://configs/env-prod.yaml`) and its entries are templated from the process environment (`OPENAI_API_KEY: '{{ env.OPENAI_API_KEY_PROD }}'`) — the documented per-environment credential indirection

- **Evidence**: The `configs/env-prod.yaml` block plus the root config line
  that loads it. The mechanism is corroborated by the Configuration
  Reference's `env` row, quoted below.
- **Confidence**: settled (documented product behavior — but see
  **Contradicts** below; the pattern is settled as *mechanism* and contested
  as *recommendation*)
- **Quote**: "Create environment-specific configurations:" (verbatim), with
  `configs/env-prod.yaml` containing, verbatim: "OPENAI_API_KEY: '{{
  env.OPENAI_API_KEY_PROD }}'" and "ANTHROPIC_API_KEY: '{{
  env.ANTHROPIC_API_KEY_PROD }}'" and "LOG_LEVEL: info". Corroboration from
  the Configuration Reference `env` row (verbatim): "Environment variables to
  set for the test run. These values will override existing environment
  variables. Can be used to set API keys and other configuration values needed
  by providers."
- **Our assessment**: Do not use this pattern; the vendor's other page warns
  against it explicitly, and the warning is filed as a contradiction
  (**Contradicts** below). The load-bearing detail for the guide is *why*:
  `{{ env.X }}` resolves at config load time, and `env:` entries then
  **override the process environment for the run** — so the template's output
  is not a reference to a secret, it *is* the secret, held in the parsed
  config. A team following this page will build a per-environment credential
  file and reasonably believe it holds references.

  One legitimate reason to split out `env-prod.yaml` survives the
  contradiction: non-secret per-environment settings. `LOG_LEVEL: info` in
  that same block is the pattern that holds up. If the guide needs
  environment separation, it should split the *provider policy* file
  (`requestsPerMinute`, sampling params — Claim 3) and source credentials from
  the process environment, which is what the Configuration Guide prescribes.

### Claim 5: Reusable assertion blocks can be defined with plain YAML anchors and referenced with aliases inside the same file (`&lengthCheck` / `*qualityCheck`), applied at `defaultTest` level and per test case

- **Evidence**: The "YAML References and Templates" section — three named
  assertion anchors declared under `assertionTemplates:`, then `*qualityCheck`
  / `*safetyCheck` aliased into `defaultTest.assert` and `*lengthCheck` /
  `*qualityCheck` into one test case, while the other test case inlines its own
  `javascript` assertion and still aliases `*qualityCheck`.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Use YAML references to avoid repetition:" (verbatim)
- **Our assessment**: Extract as a *file-organization* mechanism and nothing
  more, per the triage scope: `assertionTemplates` + `$ref` reuse is already
  owned by `docs-promptfoo-assertions-metrics.md` Claim 13, and the
  `$ref`-specific caveat by `docs-promptfoo-configuration-guide.md` Claim 9.
  The genuinely distinct fact here is that this page uses **YAML anchors and
  aliases**, which are resolved by the YAML parser itself and are a different
  mechanism from promptfoo's `$ref`. That distinction has a concrete
  consequence the corpus should record: the "tools/functions values in
  providers config are not dereferenced" caveat
  (`docs-promptfoo-configuration-guide.md` Claim 9) is scoped to `$ref` and
  does not describe anchors, so an assertion policy factored via anchors is
  immune to that gap. Also note the anchors are declared *under a config key*
  named `assertionTemplates` but used with YAML `*` syntax, so a reader could
  reasonably assume this is the `$ref` feature wearing different syntax — the
  page never disambiguates them, which is a real trap for a guide that
  recommends a reuse mechanism and would otherwise name only one.

### Claim 6: A JS config is a program, so the test matrix can be *generated* — the documented example loops 4 categories × 3 difficulties and, per generated case, string-interpolates difficulty-dependent assertion thresholds into the `javascript` assertion source itself (`minWords` / `maxWords` = 5/20, 15/50, 30/100)

- **Evidence**: The "Dynamic Configuration with JavaScript" section's full
  `promptfooconfig.js`, which builds `tests` in a nested `for` loop over
  `categories` and `difficulties` and exports `{...baseConfig, tests}`.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Use JavaScript configurations for complex logic:" (verbatim);
  the code comment in the example reads, verbatim: "// Generate test cases
  programmatically"
- **Our assessment**: The generation mechanism is unremarkable; what is
  load-bearing is *what gets generated* — the **assertion code**, not just the
  vars. The example embeds a multi-line JS body as a template string with
  `${}` interpolation of the difficulty tier, so the graded contract for a
  "basic" case and an "advanced" case are different source text generated at
  config-load time. Two consequences the page does not draw: (1) coverage
  becomes a function of the two arrays, so adding a difficulty tier silently
  multiplies the whole matrix and the spend with it — the same cartesian
  growth `docs-promptfoo-configuration-guide.md` Claim 12 documents from the
  `vars`-array side, here arriving with no `vars` arrays at all; (2) a
  generated assertion body is *code under generation*, so a bug in the
  generator produces a wrong gate rather than a missing one. This is the
  mechanism most worth pairing with `docs-promptfoo-dataset-generation.md`
  Claim 5 (non-deterministic generation has no pinning/versioning story) —
  except that here generation is deterministic given the config, which is the
  property that makes it safe to commit.

### Claim 7: TypeScript configs need an external loader — Node "currently requires external loaders to run TypeScript files directly", invoked as `NODE_OPTIONS="--import tsx" promptfoo eval -c promptfooconfig.ts` after `npm install tsx`

- **Evidence**: The "TypeScript Configuration" and "Running TypeScript
  Configs" sections, plus the linked upstream example the page points to
  (`examples/config-ts`).
- **Confidence**: settled (documented product behavior, corroborated
  upstream)
- **Quote**: "Promptfoo configs can be written in TypeScript:" (verbatim),
  "Install a TypeScript loader:" (verbatim), "Run with NODE_OPTIONS:"
  (verbatim), and the command block, verbatim:
  `NODE_OPTIONS="--import tsx" promptfoo eval -c promptfooconfig.ts`. From the
  linked `examples/config-ts` README (GitHub, promptfoo/promptfoo main),
  verbatim: "Node.js currently requires external loaders to run TypeScript
  files directly" and, listing prerequisites, "Node.js >=22.22.0 (Node.js 24
  LTS recommended)".
- **Our assessment**: The CI-relevant fact is that this is a **process-level
  `NODE_OPTIONS` requirement**, not a flag on the eval command — so any CI job,
  Makefile target, or wrapper script that shells out to `promptfoo eval` must
  export `NODE_OPTIONS` or the config fails to load, and the failure mode is a
  loader error rather than an assertion failure. The upstream README also
  pins a floor (Node >=22.22.0), which makes the eval harness a
  Node-runtime dependency of the pipeline whether or not the team is writing
  TypeScript service code. Worth noting the benefit the page actually claims
  for TS is IDE autocompletion against the `UnifiedConfig` type (upstream
  README: "Type-safe configuration with IDE autocompletion"), i.e. a
  developer-experience argument, not a runtime one.

### Claim 8: The app/eval shared-schema pattern is OpenAI-SDK-specific at the seam — the eval config imports the application's Zod schema module and converts it with `zodResponseFormat` from `openai/helpers/zod.mjs`, so sharing one schema with the app also binds the eval's structured-output enforcement to a single provider's SDK

- **Evidence**: The "Dynamic Schema Generation" section's two blocks — the
  app-side `src/schemas/response.ts` exporting `ResponseSchema`, and the
  eval-side `promptfooconfig.ts` importing it plus `zodResponseFormat` from
  `openai/helpers/zod.mjs`, attaching it as `config.response_format` on the
  `openai:gpt-5.2` provider.
- **Confidence**: settled (documented product behavior) for the mechanism;
  emerging for the portability reading
- **Quote**: "Share Zod schemas between your application and promptfoo:"
  (verbatim)
- **Our assessment**: This is the highest-value pattern on the page and the
  page undersells it. The schema is the one artifact where the app's own
  output promise and the eval's graded contract are literally the same
  committed file, so a contract change becomes a compile error in the eval
  rather than a silent coverage gap — that is the strongest answer in the
  corpus to the evidence-integrity problem raised in
  `docs-promptfoo-configuration-guide.md` Claim 10 (scripted vars fetching
  live context make the eval's input unreproducible): here the *output*
  contract is pinned to a committed file.

  Two honest limits. First, the seam is not provider-neutral: the conversion
  is `zodResponseFormat(...)` from the **OpenAI** SDK, so a suite that also
  runs Gemini or Anthropic providers has no documented path from the same Zod
  schema to their structured-output formats on this page. The upstream example
  README claims more than this page shows — it says the example covers
  "Automatic schema adaptation for different providers (OpenAI and Gemini)"
  and that "Both OpenAI and Gemini support strict schema enforcement" — but
  the adaptation mechanism is not shown on this page, so the guide should not
  assert provider-neutrality on this source alone. Second, and sharper: the
  only assertion in the example is `assert: [{ type: 'is-json' }]`. The
  provider enforces the schema; the eval only checks the output parses as
  JSON. So a model that returns valid JSON with a **missing or
  wrong-typed** `confidence` field passes the gate. The shared schema is not
  validated by the harness here, and `is-json` is a weaker check than it
  looks next to a schema that is right there in the imports.

### Claim 9: Suite *scope* is selected by an environment variable read inside the config (`process.env.TEST_MODE`), and the two documented branches differ in provider set, test directory, log level, and result retention — a smoke-vs-full CI gate expressed as config branching

- **Evidence**: The "Conditional Configuration Loading" section's
  `promptfooconfig.js`, keyed on `TEST_MODE === 'quick'` /
  `TEST_MODE === 'comprehensive'`.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Create configurations that adapt based on environment:"
  (verbatim); the quick branch's provider entry carries the comment,
  verbatim: "Faster, cheaper for quick testing"
- **Our assessment**: This is the concrete CI-gating mechanism the triage was
  looking for, and it is worth naming precisely because it is a *config*
  switch rather than a CLI flag: the same committed config yields two
  materially different suites, and which one ran is determined by the
  environment of the runner. Three differences beyond provider cost are easy
  to miss. `tests:` is `'file://tests/quick/'` vs
  `'file://tests/comprehensive/'` — so quick mode is a strict coverage
  subset by directory, which is the only defensible way to run a cheaper
  suite (a filtered copy of the same cases would drift). `env.LOG_LEVEL`
  flips `debug` vs `info`, so a green quick run and a green comprehensive run
  do not emit comparable logs. And `writeLatestResults: true` appears **only**
  on the comprehensive branch, meaning by the documented example the quick run
  does not push results to promptfoo storage for the web UI
  (Configuration Reference: "Write latest results to promptfoo storage so
  they can be viewed in the web UI") — so the cheap gate is also the one with
  no stored artifact to inspect after the fact. A team shipping this pattern
  should be told that explicitly.

  The hermeticity cost is the real finding and belongs with
  `docs-google-sre-configuration-design.md` Claim 13 (a config change is only
  safely rollable if it is hermetic): the effective gate is a function of the
  runner's environment, so "what did CI evaluate?" is not answerable from the
  committed config alone, and the same commit gates differently on a laptop
  than in CI. The mitigation is cheap and worth the guide stating it — have
  CI be the only thing that sets `TEST_MODE`, and record the resolved mode
  with the results.

### Claim 10: The page's own directory-layout advice and its own worked examples disagree — the recommended tree uses `configs/providers/{development,staging,production}.yaml`, while every environment example in the page uses a flat sibling file (`configs/providers-prod.yaml`, `configs/env-prod.yaml`)

- **Evidence**: The "Directory Structure" section's `project/` tree
  (environments as files *inside* `configs/providers/`) versus the
  "Environment-Specific Configurations" blocks, which load
  `file://configs/providers-prod.yaml` and `file://configs/env-prod.yaml` —
  no `providers/` subdirectory anywhere in the page's runnable examples. The
  tree also introduces `configs/defaults/` and `scripts/config-generators/`
  that no example references.
- **Confidence**: settled (both artifacts are on the page, verbatim; the
  inconsistency is directly observable)
- **Quote**: "Organize your configuration files in a logical hierarchy:"
  (verbatim, introduces the tree)
- **Our assessment**: Small, but it is the kind of thing that costs a team an
  hour and is worth one line in a guide section: the page's normative layout
  is a directory of per-environment files, its examples are flat
  hyphenated siblings, and a follower who reorganizes to match the tree must
  also rewrite every `file://` path in the configs. Recorded so the guide
  picks one convention deliberately instead of inheriting whichever snippet a
  reader copied first.

## Concrete Artifacts

All blocks below are verbatim from the source page
(https://www.promptfoo.dev/docs/configuration/modular-configs), in page
order.

### Root config reduced to a manifest of paths (Claim 1)

```yaml
# yaml-language-server: $schema=https://promptfoo.dev/config-schema.json
description: Main evaluation configuration
prompts: file://configs/prompts.yaml
providers: file://configs/providers.yaml
tests: file://configs/tests/
defaultTest: file://configs/default-test.yaml
```

### Per-domain test directories, fanned in by list (Claim 2)

```yaml
# yaml-language-server: $schema=https://promptfoo.dev/config-schema.json
description: Multi-domain evaluation
prompts: file://prompts/
providers: file://providers.yaml
tests:
  - file://tests/accuracy/
  - file://tests/safety/
  - file://tests/performance/
  - file://tests/edge-cases/
```

### Per-environment provider policy — rate caps live here, not in the suite (Claim 3)

```yaml
# yaml-language-server: $schema=https://promptfoo.dev/config-schema.json
description: Production evaluation
prompts: file://prompts/
providers: file://configs/providers-prod.yaml
tests: file://tests/
env: file://configs/env-prod.yaml
```

```yaml
# Production providers with rate limiting
- id: openai:gpt-5.2
  label: gpt-5.2-prod
  config:
    temperature: 0.1
    max_tokens: 500
    requestsPerMinute: 100
- id: anthropic:claude-sonnet-5
  label: claude-sonnet-prod
  config:
    max_tokens: 500
    requestsPerMinute: 50
```

### The contested credential indirection (Claim 4) — see **Contradicts**

```yaml
# Production environment variables
OPENAI_API_KEY: '{{ env.OPENAI_API_KEY_PROD }}'
ANTHROPIC_API_KEY: '{{ env.ANTHROPIC_API_KEY_PROD }}'
LOG_LEVEL: info
```

### YAML-anchor assertion templates, aliased at two levels (Claim 5)

```yaml
# yaml-language-server: $schema=https://promptfoo.dev/config-schema.json
description: Evaluation with reusable components
prompts: file://prompts/
providers: file://providers.yaml

# Define reusable assertion templates
assertionTemplates:
  lengthCheck: &lengthCheck
    type: javascript
    value: output.length > 20 && output.length < 500

  qualityCheck: &qualityCheck
    type: llm-rubric
    value: Response should be clear, helpful, and well-structured

  safetyCheck: &safetyCheck
    type: llm-rubric
    value: Response should not contain harmful or inappropriate content

defaultTest:
  assert:
    - *qualityCheck
    - *safetyCheck

tests:
  - description: Short response test
    vars:
      input: What is AI?
    assert:
      - *lengthCheck
      - *qualityCheck

  - description: Long response test
    vars:
      input: Explain machine learning in detail
    assert:
      - type: javascript
        value: output.length > 100 && output.length < 2000
      - *qualityCheck
```

### Generated test matrix with difficulty-interpolated assertion source (Claim 6)

```javascript
const baseConfig = {
  description: 'Dynamic configuration example',
  prompts: ['file://prompts/base-prompt.txt'],
  providers: ['openai:gpt-5.2', 'anthropic:claude-sonnet-5'],
};

// Generate test cases programmatically
const categories = ['technology', 'science', 'history', 'literature'];
const difficulties = ['basic', 'intermediate', 'advanced'];

const tests = [];
for (const category of categories) {
  for (const difficulty of difficulties) {
    tests.push({
      vars: {
        category,
        difficulty,
        question: `Generate a ${difficulty} question about ${category}`,
      },
      assert: [
        {
          type: 'contains',
          value: category,
        },
        {
          type: 'javascript',
          value: `
            const wordCount = output.split(' ').length;
            const minWords = ${difficulty === 'basic' ? 5 : difficulty === 'intermediate' ? 15 : 30};
            const maxWords = ${difficulty === 'basic' ? 20 : difficulty === 'intermediate' ? 50 : 100};
            return wordCount >= minWords && wordCount <= maxWords;
          `,
        },
      ],
    });
  }
}

module.exports = {
  ...baseConfig,
  tests,
};
```

### `TEST_MODE` suite selection — cheap branch and full branch (Claim 9)

```javascript
const isQuickTest = process.env.TEST_MODE === 'quick';
const isComprehensive = process.env.TEST_MODE === 'comprehensive';

const baseConfig = {
  description: 'Test mode adaptive configuration',
  prompts: ['file://prompts/'],
};

// Quick test configuration
if (isQuickTest) {
  module.exports = {
    ...baseConfig,
    providers: [
      'openai:gpt-5.4-mini', // Faster, cheaper for quick testing
    ],
    tests: 'file://tests/quick/', // Smaller test suite
    env: {
      LOG_LEVEL: 'debug',
    },
  };
}
```

*Extraction note: the quick branch lists one provider (`openai:gpt-5.4-mini`)
while the comprehensive branch lists three; the page shows the two branches
with a shared `baseConfig` and separate `module.exports` assignments. The
comprehensive branch additionally sets `writeLatestResults: true`, which the
quick branch does not.*

### Shared Zod schema: app module and eval config (Claim 8)

`src/schemas/response.ts` (the page's caption for the first block):

```typescript
import { z } from 'zod';

export const ResponseSchema = z.object({
  answer: z.string(),
  confidence: z.number().min(0).max(1),
  sources: z.array(z.string()).nullable(),
});
```

`promptfooconfig.ts` (the page's caption for the second block):

```typescript
import { zodResponseFormat } from 'openai/helpers/zod.mjs';
import type { UnifiedConfig } from 'promptfoo';
import { ResponseSchema } from './src/schemas/response';

const responseFormat = zodResponseFormat(ResponseSchema, 'response');

const config: UnifiedConfig = {
  prompts: ['Answer this question: {{question}}'],
  providers: [
    {
      id: 'openai:gpt-5.2',
      config: {
        response_format: responseFormat,
      },
    },
  ],
  tests: [
    {
      vars: { question: 'What is TypeScript?' },
      assert: [{ type: 'is-json' }],
    },
  ],
};

export default config;
```

### TS config invocation (Claim 7)

```bash
npm install tsx
```

```bash
NODE_OPTIONS="--import tsx" promptfoo eval -c promptfooconfig.ts
```

## Cross-References

**Candidates screened** from `miner-related-notes.md` (10 lexical candidates);
each is cited below or explicitly dismissed in Extraction Notes.

- **Contradicts**: `docs-promptfoo-configuration-guide.md` **Claim 7** — that
  note records the vendor's explicit warning that `{{ env.X }}` templates in
  `config.env` "resolves the secret into the eval config object and may appear
  in exported results", and prescribes reading credentials from process env
  or `--env-file` instead. This page's "Environment-Specific Configurations"
  section (Claim 4) presents that exact pattern as the recommended
  per-environment structure. Filed as **contradiction issue #1534**; no
  verdict is picked here per MINER.md §4a.
- **Corroborates**: `docs-promptfoo-configuration-guide.md` **Claim 11** —
  decomposition of an eval suite converges on one aggregate verdict: that note
  documents multiple configs combined via `-c` globbing into a single eval;
  this page's per-domain `tests:` directory fan-in (Claim 2) reaches the same
  single-verdict shape by a different mechanism. Together they say "splitting
  configs is not the same as gating per split."
- **Extends**: `docs-promptfoo-configuration-guide.md` **Claim 9** — that note
  scopes its caveat about `tools`/`functions` provider-config values not being
  dereferenced to `$ref`. Claim 5 here records that this page's reuse mechanism
  is plain YAML anchors/aliases, a different resolver, so the caveat does not
  transfer.
- **Extends**: `docs-promptfoo-assertions-metrics.md` **Claim 13** — that note
  owns `assertionTemplates` + `$ref` as the assertion-reuse layer; per the
  triage scope, only the YAML-anchor mechanism is new here (Claim 5), not the
  feature.
- **Extends**: `docs-promptfoo-javascript-assertions.md` **Claim 1** — every
  reusable assertion on this page is a `javascript` assertion whose
  pass/fail semantics are user code. Worth noting for the guide: this page's
  reusable `lengthCheck` and `default-test.yaml` both write `output.length`,
  i.e. they assume `output` is a string — the contested reading identified in
  that note's **Claim 4** — so this page's config patterns inherit that
  ambiguity rather than resolving it.
- **Corroborates**: `docs-google-sre-configuration-design.md` **Claim 9** —
  that claim's prescription to separate the configuration interface from the
  resulting data, with users on a higher-level interface compiling to plain
  static data. This page's JS/TS configs are exactly that interface over
  YAML/JSON, and the vendor frames the payoff as IDE autocompletion rather
  than queryability.
- **Corroborates**: `docs-google-sre-configuration-design.md` **Claim 12** —
  configuration must be versioned regardless of ingestion path. Splitting
  `providers-prod.yaml` out means a rate-limit policy change is a versioned
  file diff with an attributable owner, which is the property that note
  requires.
- **Corroborates**: `docs-google-sre-configuration-design.md` **Claim 11** —
  commit-time semantic validation of config. The page's snippets carry a
  `$schema` header pointing at a JSON schema, but Claim 3 finds that schema
  leaves provider `config` untyped, which is a concrete instance of the
  validation gap that claim describes.
- **Extends**: `docs-promptfoo-dataset-generation.md` **Claim 5** — that note
  records that generated test cases have no pinning, versioning, or seed story.
  Claim 6 here is the deterministic counterpart: generation from arrays in a
  committed config, which is reproducible, but whose generated *assertion
  code* makes a generator bug a wrong gate rather than a missing one.
- **Corroborates**: `blog-promptfoo-owasp-red-teaming.md` **Claim 4** — that
  note records the vendor's "integrate into CI/CD pipelines and run on a
  recurring schedule" recommendation. Claim 9 here is the mechanism that
  recommendation has been missing: a config-level switch between a cheap
  pre-merge suite and a full scheduled one.
- **Novel**: (1) per-provider rate limits and sampling parameters carried in an
  *environment-specific* provider file, with `-prod`-suffixed provider labels
  making environment attribution visible in results (Claim 3); (2) suite scope
  selected by `process.env.TEST_MODE` inside the config, including
  `writeLatestResults` differing by branch so the cheap gate leaves no stored
  artifact (Claim 9); (3) an app-side Zod schema imported directly into the
  eval config as the shared output contract, with the seam being
  OpenAI-SDK-specific and the only assertion being `is-json` (Claim 8);
  (4) the corpus's first record that `requestsPerMinute` — the field this page
  presents as production rate limiting — is absent from both the
  Configuration Reference and the JSON schema its own snippets declare
  (Claim 3).

## Guide Impact

- **Ch05 (§config-change safety / hermeticity)**: The existing
  three-property test cites `docs-google-sre-configuration-design` Claim 13
  and requires a config change to be hermetic. This source supplies the
  eval-harness half of that argument from the opposite direction: the
  `TEST_MODE` pattern (Claim 9) makes the effective gate a function of the
  *runner's* environment, and the `env:` file pattern (Claim 4) makes it a
  function of the runner's *credentials*. Recommend adding: an eval config
  whose scope or keys vary by environment is non-hermetic and therefore not
  safely rollable, mirroring the existing `-w` dataset anti-pattern. The
  concrete rule to add: CI is the only thing that sets `TEST_MODE`, and the
  resolved mode travels with the results.
- **Ch05 (new eval-harness config subsection)**: Nothing in the corpus tells
  a reader how to organize a large promptfoo suite across environments. This
  source supports a short subsection with three concrete prescriptions and
  their costs: split `providers-<env>.yaml` for non-secret environment policy
  (Claim 3), split `tests/` by domain so coverage is additive (Claim 2), and
  **do not** use `env: file://...` for API keys — cite contradiction #1534 and
  the Configuration Guide's process-env remedy rather than this page's example.
- **Ch05 (eval as a versioned artifact)**: The shared-Zod-schema pattern
  (Claim 8) is the strongest available answer to the evidence-integrity
  problem Ch05 already raises from the dataset side: it makes the app's output
  contract and the eval's graded contract the same committed file. Recommend
  adding it as the positive counterpart to the `-w` warning — with the honest
  caveat that the harness does not validate the schema (only `is-json` is
  asserted), so a guide recommendation must include asserting fields, not just
  parseability.
- **Ch03 (agent evaluation in production)**: Ch03 currently argues eval
  coverage degrades unless data is deliberately preserved. This source's
  directory-per-domain layout (Claim 2) plus `TEST_MODE` branch selection
  (Claim 9) is the concrete file-layout form of "preserve a cheap tier and a
  full tier deliberately" — worth one sentence pointing Ch03 readers at a
  layout that makes the two tiers reviewable as directories.
- **Ch06 (secret handling in eval configs)**: If a credential-handling rule for
  eval configs exists or is added, it must cite `docs-promptfoo-configuration-guide`
  Claim 7 and **not** this page. Contradiction #1534 is unresolved; the Smith
  should treat the `env:` example as `**Debated:**` rather than as a
  recommendation.

## Extraction Notes

- Followed 4 links from the page per MINER.md §1, all read in full:
  Configuration Reference (`/docs/configuration/reference/`) — used for the
  `env`, `basePath`, `writeLatestResults`, and `defaultTest` corroborations;
  Configuration Guide (`/docs/configuration/guide/`) — used to verify the
  contradicting secret-handling warning verbatim; the linked upstream example
  `promptfoo/promptfoo/examples/config-ts` (`README.md` and
  `promptfooconfig.ts` on `main`) — source of the Node-loader and
  provider-adaptation quotes; and the machine-readable schema the page's own
  snippets declare, `https://promptfoo.dev/config-schema.json`, fetched to
  test the `requestsPerMinute` claim (Claim 3). The `/docs/providers/` page was
  also fetched while testing that same claim.
- Two artifacts in this note are **absence** findings, and are labeled as
  such: `requestsPerMinute` appears in neither the Configuration Reference
  nor `config-schema.json`, and the page's directory tree disagrees with its
  own runnable examples (Claim 10). Both were checked directly rather than
  inferred.
- **Candidates dismissed** from `miner-related-notes.md` (all verified as to
  topic, none cited above because the claims do not reach):
  `docs-promptfoo-classifier-grading.md` — its env-var indirection is for a
  gated HuggingFace endpoint URL (Claim 3 there), not credential or
  environment management; different concern, no shared mechanism.
  `docs-promptfoo-pi-scorer.md` — its Claim 5 cross-page threshold
  corroboration is about `0.5` default values in config comments; this page
  uses no numeric thresholds.
  `docs-promptfoo-llm-rubric.md` — it appears in two of this page's reusable
  anchors as a `type: llm-rubric` string value, but every one of that note's
  ten claims is about grading semantics (audio, judge selection, negation
  fail-closed), none of which this page touches.
  `docs-langfuse-mcp-server.md` — MCP endpoint/transport configuration;
  unrelated to eval config composition.
  `docs-litellm-batches-api.md` — its Claims 1-5 concern gateway-side
  per-minute token/request accounting and enqueued-token allowances, which is
  a different enforcement layer from a client-side per-provider concurrency
  cap; no shared mechanism.
  `blog-pagerduty-sre-agent-triage.md` — Claim 1's eval-alert triage signal is
  about consuming eval results as an alert, not about producing or composing
  them; the boundary is downstream of this page.
- Confidence is `emerging` overall: every claim here is settled *as
  documented product behavior* (it is the vendor's own config surface, and
  the sibling notes grade that class of claim `settled`), but this page
  supplies **no measured outcomes, no rationale for any of its advice, and no
  independent validation**, and it directly contradicts a sibling page on the
  one recommendation a guide is most likely to act on. That combination is
  what keeps it at `emerging` rather than `settled`.