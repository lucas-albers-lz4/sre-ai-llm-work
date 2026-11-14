---
source_url: https://www.promptfoo.dev/docs/integrations/jest
source_type: docs
title: "Promptfoo: Testing prompts with Jest and Vitest"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-23
date_extracted: 2026-10-24
last_checked: 2026-10-24
status: current
confidence_overall: emerging
issue: "#1874"
---

# Promptfoo: Testing prompts with Jest and Vitest

> Promptfoo's assertion functions can be imported programmatically and wrapped as Jest/Vitest custom matchers so LLM-quality checks run inside a host test runner — but the recipe carries defaults, an argument-order gotcha for model-graded assertions, and a known example defect (missing imports in the JS snippet) that makes copy-paste risky.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Testing prompts with Jest and Vitest" integration page under `/docs/integrations/`)
- **Author credibility**: Promptfoo, the vendor (now part of OpenAI per site banner). First-party documentation of integrating its assertion library into test runners; no measured gate-failure rates, cost data, or independent validation. Authoritative for the API shape shown, but vendor-positioned.
- **Scope**: Embedding `promptfoo` assertions into Jest/Vitest via `expect.extend`. Covers creating matchers for `toMatchSemanticSimilarity`, `toPassLLMRubric`, `toMatchFactuality`, `toMatchClosedQA`, usage patterns, and final setup (`npm test`). Does NOT cover the full YAML eval harness, caching/tracing semantics in the CLI path, result export/JUnit/CI summary, or cost controls — those remain features of `promptfoo eval`.
- **Last updated**: Oct 23, 2026 by promptfoobot[bot].

## Extracted Claims

### Claim 1: Promptfoo assertion functions can be imported programmatically (`import { assertions } from 'promptfoo'`) and wrapped as Jest/Vitest custom matchers so eval gates ride an existing test suite instead of running `promptfoo eval` separately
- **Evidence**: The page shows creating `matchers.js`/`matchers.ts` that import `assertions` and call `expect.extend(...)`, then tests import `installMatchers()` and use `expect(...).toMatch*` / `expect(...).toPassLLMRubric(...)`.
- **Confidence**: settled
- **Quote**: "First, we'll create custom matchers:" followed by the list of matchers and the instruction to create `matchers.js` / `matchers.ts` importing from `'promptfoo'`.
- **Our assessment**: The key shift is moving the gate from the promptfoo CLI/YAML harness to the host test runner. This is a legitimate integration pattern for teams that already gate on `npm test`/CI unit tests, but as noted in Guide Impact it trades off eval-specific features (exports, traces, caching, structured reports) for test-runner ergonomics.

### Claim 2: `toMatchSemanticSimilarity` defaults `threshold = 0.8` when not specified; a bare equality short-circuit `received === expected || result.pass` causes exact string matches to pass without calling the model
- **Evidence**: JS matcher implementation shows `threshold = 0.8` default and `const pass = received === expected || result.pass;`
- **Confidence**: settled
- **Quote**: "`async toMatchSemanticSimilarity(received, expected, threshold = 0.8) { const result = await matchesSimilarity(received, expected, threshold); const pass = received === expected || result.pass;`"
- **Our assessment**: The silent 0.8 default is a \"read the assert's own defaults\" hazard (mirrors patterns in Ch05). The equality short-circuit is an optimization that avoids network calls for identical strings — useful, but it means the model judge is not consulted in the exact-match case (operators must not assume judge behavior on identical strings).

### Claim 3: For model-graded matchers, argument order differs by function — `matchesSimilarity(received, expected, threshold)` takes `(received, expected, ...)` while `matchesLlmRubric(expected, received, gradingConfig)` takes `(expected, received, ...)`; the matcher wrappers must pass arguments in the correct order
- **Evidence**: JS wrapper for `toPassLLMRubric` does `await matchesLlmRubric(expected, received, gradingConfig)` while `toMatchSemanticSimilarity` does `await matchesSimilarity(received, expected, threshold)`. TS snippet shows same pattern.
- **Confidence**: settled
- **Quote**: "`const gradingResult = await matchesLlmRubric(expected, received, gradingConfig);`" and "`const result = await matchesSimilarity(received, expected, threshold);`"
- **Our assessment**: This is easy to misread/copy-paste incorrectly. The triage explicitly flagged verifying argument order; the source confirms the asymmetry. Treat this as a footgun to document clearly.

### Claim 4: The judge is caller-supplied via `gradingConfig.provider` (example uses `'openai:chat:gpt-5-mini'`); a passing test only means the pinned judge passed, not that the judge is calibrated
- **Evidence**: Tests define `const gradingConfig = { provider: 'openai:chat:gpt-5-mini' };` and pass it to `toPassLLMRubric(...)`.
- **Confidence**: settled
- **Quote**: "`const gradingConfig = { provider: 'openai:chat:gpt-5-mini' };`" and usage in tests/matchers.
- **Our assessment**: No judge calibration step exists in the recipe. This directly intersects Ch05 guidance about judge trust/calibration.

### Claim 5: The JavaScript snippet has a copy-paste defect — it destructures only `matchesSimilarity` and `matchesLlmRubric` from `assertions` but the matcher set it installs includes `toMatchFactuality` and `toMatchClosedQA` which call `matchesFactuality` and `matchesClosedQa`; those identifiers are undefined and will throw `ReferenceError` at runtime
- **Evidence**: JS code block shows `const { matchesSimilarity, matchesLlmRubric } = assertions;` but later defines `async toMatchFactuality(...) { const gradingResult = await matchesFactuality(...); ... }` and `async toMatchClosedQA(...) { const gradingResult = await matchesClosedQa(...); ... }` with no imports/destructuring for them. TypeScript snippet only implements two matchers (different from the full JS listing).
- **Confidence**: settled (verifiable from the page as shown)
- **Quote**: "`const { matchesSimilarity, matchesLlmRubric } = assertions;`" followed by matcher methods calling `matchesFactuality` and `matchesClosedQa` without them being imported/destructured.
- **Our assessment**: Same class of broken vendor example as seen in the corpus (javascript-assertions note). Operators must either destructure all needed functions or import them differently; the page as written will fail on first use of the factuality/closed-qa matchers in the JS example.

### Claim 6: Running via `npm test` (Jest) executes LLM-graded assertions in-process against configured providers; the default providers require `OPENAI_API_KEY`. Embedding in a host test runner trades off eval-harness features (result export, JUnit/CI summary, trace, cache, explicit exit-code contract of `promptfoo eval`) for reuse of existing test infrastructure
- **Evidence**: "Add the following line to the `scripts` section in your `package.json`: `"test": "jest"`", "Now, you can run the tests with the following command: `npm test`", "Note that if you're using the default providers, you will need to set the `OPENAI_API_KEY` environment variable."
- **Confidence**: settled
- **Quote**: "`\"test\": \"jest\"`" and "`npm test`" and "Note that if you're using the default providers, you will need to set the `OPENAI_API_KEY` environment variable."
- **Our assessment**: This is important operationally — network calls, provider keys, nondeterminism, and potential CI flakiness/costs move into unit-test runs. The guide should treat \"Jest wrapper\" as a different trade-off than the dedicated eval harness.

## Concrete Artifacts

### JavaScript matcher skeleton (from source)
```javascript
import { assertions } from 'promptfoo';

const { matchesSimilarity, matchesLlmRubric } = assertions;

export function installMatchers() {
  expect.extend({
    async toMatchSemanticSimilarity(received, expected, threshold = 0.8) {
      const result = await matchesSimilarity(received, expected, threshold);
      const pass = received === expected || result.pass;
      if (pass) {
        return {
          message: () => `expected ${received} not to match semantic similarity with ${expected}`,
          pass: true,
        };
      } else {
        return {
          message: () =>
            `expected ${received} to match semantic similarity with ${expected}, but it did not. Reason: ${result.reason}`,
          pass: false,
        };
      }
    },

    async toPassLLMRubric(received, expected, gradingConfig) {
      const gradingResult = await matchesLlmRubric(expected, received, gradingConfig);
      if (gradingResult.pass) {
        return {
          message: () => `expected ${received} not to pass LLM Rubric with ${expected}`,
          pass: true,
        };
      } else {
        return {
          message: () =>
            `expected ${received} to pass LLM Rubric with ${expected}, but it did not. Reason: ${gradingResult.reason}`,
          pass: false,
        };
      }
    },

    async toMatchFactuality(input, expected, received, gradingConfig) {
      const gradingResult = await matchesFactuality(input, expected, received, gradingConfig);
      // ...
    },

    async toMatchClosedQA(input, expected, received, gradingConfig) {
      const gradingResult = await matchesClosedQa(input, expected, received, gradingConfig);
      // ...
    },
  });
}
```
(Note: in the published JS example, `matchesFactuality` and `matchesClosedQa` are used but not destructured/imported — see Claim 5.)

### Test usage (from source)
```javascript
import { installMatchers } from './matchers';

installMatchers();

const gradingConfig = {
  provider: 'openai:chat:gpt-5-mini',
};

describe('semantic similarity tests', () => {
  test('should pass when strings are semantically similar', async () => {
    await expect('The quick brown fox').toMatchSemanticSimilarity('A fast brown fox');
  });

  test('should fail when strings are not semantically similar', async () => {
    await expect('The quick brown fox').not.toMatchSemanticSimilarity('The weather is nice today');
  });

  test('should pass when strings are semantically similar with custom threshold', async () => {
    await expect('The quick brown fox').toMatchSemanticSimilarity('A fast brown fox', 0.7);
  });

  test('should fail when strings are not semantically similar with custom threshold', async () => {
    await expect('The quick brown fox').not.toMatchSemanticSimilarity(
      'The weather is nice today',
      0.9,
    );
  });
});

describe('LLM evaluation tests', () => {
  test('should pass when strings meet the LLM Rubric criteria', async () => {
    await expect('Four score and seven years ago').toPassLLMRubric(
      'Contains part of a famous speech',
      gradingConfig,
    );
  });

  test('should fail when strings do not meet the LLM Rubric criteria', async () => {
    await expect('It is time to do laundry').not.toPassLLMRubric(
      'Contains part of a famous speech',
      gradingConfig,
    );
  });
});
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-javascript-assertions.md` — documents the programmatic/assertion mechanics in the config/harness context; this note extends that to the Jest/Vitest test-runner embedding path.
  - `source-notes/docs-promptfoo-assertions-metrics.md` — catalog of assertion types/matchers; this note shows how to use them as Jest matchers.
  - `source-notes/docs-promptfoo-github-action.md`, `source-notes/docs-promptfoo-circleci-integration.md` — other CI gating patterns (separate from in-test-runner embedding).
- **Contradicts**: None identified.
- **Extends**:
  - `source-notes/docs-promptfoo-javascript-assertions.md` (Claim 2: fail-closed on throw; argument/usage patterns) — embedding into a general test runner makes assertion bugs look like test failures; the broken example pattern is consistent with \"execute examples\" warnings already in that note.
- **Novel**: The test-runner embedding pattern (`expect.extend` over `assertions`), the exact matcher API surface shown (`toMatchSemanticSimilarity` default 0.8 + equality short-circuit, `toPassLLMRubric` with caller-supplied `gradingConfig.provider`), the argument-order asymmetry between `matchesSimilarity` and `matchesLlmRubric`, and the concrete JS copy-paste defect (missing destructuring for `matchesFactuality`/`matchesClosedQa`) are not covered by existing notes.

## Guide Impact

- **Chapter 05 (Evaluation and measurement methodology / release gating)**: Treat \"evals in Jest/Vitest\" as a *different gating model* than `promptfoo eval`. When documenting CI gates, explicitly call out trade-offs: in-test-runner embedding reuses existing test infra but loses eval exports/JUnit/trace/cache and moves provider keys/network calls into unit tests (nondeterminism/cost). Add a footgun list: read defaults (semantic similarity 0.8), verify argument order for model-graded assertions, supply and calibrate judge config, and do not copy vendor snippets blindly (check imports). The equality short-circuit (`received === expected || result.pass`) is an optimization worth noting. 
- **Chapter 06 (Red-teaming as a CI gate)**: If using promptfoo assertions as gates, judge configuration and calibration remain necessary even when invoked via Jest matchers — same judge-trust concerns apply.

## Extraction Notes

- Deep-read the full page (installation, creating custom matchers for both JS and TS tabs, writing tests, final setup). Followed all code blocks and the \"Note that if you're using the default providers, you will need to set the `OPENAI_API_KEY` environment variable.\"
- Compared JS and TS snippets: TS implements only `toMatchSemanticSimilarity` and `toPassLLMRubric` while JS lists four matchers but has missing imports for `matchesFactuality`/`matchesClosedQa` — recorded as Claim 5 (copy-paste defect).
- Cross-referenced against existing promptfoo notes; no note covers Jest/Vitest integration path. Overlap checked with `docs-promptfoo-javascript-assertions.md`, `docs-promptfoo-assertions-metrics.md`, CI integration notes — incremental variant, not duplicate.
