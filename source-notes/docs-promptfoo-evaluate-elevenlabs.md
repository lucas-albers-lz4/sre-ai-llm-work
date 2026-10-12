---
source_url: https://www.promptfoo.dev/docs/guides/evaluate-elevenlabs
source_type: docs
title: "Promptfoo Guide: Evaluating ElevenLabs Voice AI — Numeric Gates for a Non-Text Modality, Provider-Computed WER, and Tool Mocking for Agent Evals"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-12
date_extracted: 2026-10-12
last_checked: 2026-10-12
status: current
confidence_overall: emerging
issue: "#1682"
---

# Promptfoo Guide: Evaluating ElevenLabs Voice AI

> The corpus's first worked example of **gating a non-text
> modality**: where a text eval compares strings, this page compares
> **latency (3000/2000/60000 ms) and cost ($0.01)** for TTS, asserts a
> **provider-computed word-error-rate** (`calculateWER: true` +
> `referenceText`, gated at `metadata.wer.wer < 0.05`) for the STT leg of a
> TTS → STT round trip, delegates conversational quality to the provider's
> own **weighted `evaluationCriteria` with per-criterion
> `passingThreshold`**, and introduces **`toolMockConfig`** — the first
> corpus source on stubbing a tool's return value so an agent's tool
> trajectory can be evaluated deterministically and without live side
> effects. It is vendor guide documentation with no CI/CD pipeline, no SLO,
> and no measured data, so the extractable value is the **metric-definition
> mechanics**, not operational doctrine.

## Source Context

- **Type**: docs (vendor guide — a nine-step how-to page under
  `/docs/guides/` in promptfoo's documentation, "Evaluating ElevenLabs voice
  AI"; it carries runnable YAML for every step).
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of *its
  own* harness behavior (assertion types, `--no-cache`, config shapes), and
  the ElevenLabs model IDs and voice-settings keys it documents are the
  provider's public API surface. Vendor-positioned: no measured WER,
  latency, cost, or judge-agreement figures are reported, the sample result
  table (847 ms / $0.003 vs 1,234 ms / $0.004) is illustrative rather than
  measured, and there is no independent practitioner validation.
- **Scope**: A hands-on tutorial covering TTS model comparison (Part 1),
  voice-settings customization (Part 2), a TTS → STT transcription-accuracy
  round trip gated on WER (Part 3), a conversational-agent eval with weighted
  criteria (Part 4), and tool mocking for agent evals (Part 5), plus a
  troubleshooting section. It is **product-specific**: the provider IDs
  (`elevenlabs:tts`, `elevenlabs:stt`, `elevenlabs:agents`), model IDs
  (`eleven_flash_v2_5`, `eleven_turbo_v2_5`, `scribe_v2`), and voice IDs
  (`21m00Tcm4TlvDq8ikWAM`) are ElevenLabs-specific. Per the Prospector's
  caveat, the eval-harness mechanics are the transferable signal; the
  provider IDs are not.
- **Last updated**: the page footer reads "Last updated on **Oct 12, 2026**
  by **renovate[bot]**" (the page is otherwise undated). The triage comment
  recorded an Oct 11 footer; this extraction reads the Oct 12 revision.
- **Issue provenance**: auto-filed from the `promptfoo-docs` site-crawl seed
  (`https://www.promptfoo.dev/docs/getting-started/`); no human deep-read
  preceded extraction.

## Extracted Claims

### Claim 1: For a text-to-speech provider, "quality" is gated by **numeric latency and cost assertions** — `type: latency threshold: 3000` (ms) and `type: cost threshold: 0.01` ($) — because there is no text output to string-match
- **Evidence**: Part 1 Step 2's config places two `tests:` entries whose
  sole assertion is `latency` (3000) or `cost` (0.01); Step 3's sample result
  table then reports per-provider latency (`847ms` / `1,234ms`) and cost
  (`$0.003` / `$0.004`) against the pass marks.
- **Confidence**: settled as documented config (the YAML is runnable); the
  sample numbers are illustrative, not measured
- **Quote**: "Both models complete within 3 seconds" and "Cost is under $0.01
  per greeting" (the two test `description` values, each paired with the
  matching `latency`/`cost` assertion)
- **Our assessment**: This is the guide's cleanest illustration of the Ch05
  rule the Prospector flagged — **metrics without a unit are noise**. An
  audio output has no `equals`/`contains` to assert against, so the page
  substitutes two *unit-bearing* numbers (milliseconds, dollars) and makes
  them first-class pass/fail gates. The transferable pattern is
  "when the artifact under test is not text, gate the measurable envelope —
  latency, cost — and the one domain metric you can compute (WER, Claim 3)."
  Deliberately **not** re-deriving the cache-coupling footgun these budget
  assertions carry (latency/cost require `--no-cache` or they measure
  replay): that mechanism is already extracted in
  `docs-promptfoo-deterministic-metrics.md` (Claims 6, 14) and is cited, not
  restated, below.

### Claim 2: The page's only check that audio was actually produced is a **custom `javascript` assertion reading `context.providerResponse.audio`** for a `data` or `blobRef` field — the corpus has no declarative "audio exists" assertion type, and a **blob reference counts as valid audio**
- **Evidence**: The Step 5 formal-scenario test and the Step 6
  audio-generation test both use the same inline JS guard; there is no
  `type:` assertion for audio anywhere on the page.
- **Confidence**: settled (documented code, verbatim)
- **Quote**:
  ```
  const audio = context.providerResponse.audio;
  return Boolean(audio?.data || audio?.blobRef);
  ```
- **Our assessment**: Two things worth carrying. First, **presence is the
  floor, not the gate**: the assertion says an audio object exists; it says
  nothing about whether the audio is intelligible, on-voice, or the right
  length. Second, the `blobRef` branch is a subtle provider-contract point —
  it treats an out-of-band blob reference as proof of audio, whereas the
  sibling `llm-rubric` audio-grading contract errors on blob references
  (`docs-promptfoo-llm-rubric.md` Claim 2: "Blob references and other
  formats produce a grading error"). That is **complementary, not
  contradictory**: "an audio blob exists" and "the blob is gradeable by the
  judge" are two different capabilities, and a voice eval needs both
  assertions to claim anything about quality.

### Claim 3: Speech-to-text accuracy is gated on a **provider-computed word-error-rate** — `calculateWER: true` plus a `referenceText` makes the provider return the score, and a custom JS assertion requires `context.providerResponse.metadata.wer.wer < 0.05`
- **Evidence**: Part 3's `stt-accuracy.yaml` provider block
  (`id: elevenlabs:stt`, `modelId: scribe_v2`, `calculateWER: true`,
  `referenceText: '<the prompt text>'`) and its one test's JS assertion
  reading `metadata.wer.wer`.
- **Confidence**: settled as documented behavior; the `0.05` threshold is
  the page's chosen pass bar, not a benchmarked figure
- **Quote**:
  ```
  // Transcription text is output; WER is in response metadata.
  const wer = context.providerResponse.metadata?.wer?.wer;
  return typeof wer === 'number' && wer < 0.05;
  ```
- **Our assessment**: This is the strongest contribution on the page and the
  concrete instance of "metric-definition-before-gating" for a speech
  modality. WER is a **defined unit** (word error rate against a known
  reference), and the gate states its tolerance numerically instead of
  asking a judge whether the transcript "looks right." Two honest caveats
  the page does not state: (a) the reference is a fixed, known phrase and
  the audio was synthesized by the same system under test, so this measures
  **round-trip fidelity of a pinned sentence**, not open-domain ASR; and
  (b) unlike the deterministic assertion note's client-side checks, the
  number here is **provider-computed** — `calculateWER` asks ElevenLabs to
  return the score, so the gate trusts the provider's arithmetic. For Ch05
  that is a third category of metric: not deterministic-local (a string
  check), not judge-graded (an opinion), but **vendor-reported** — a number
  whose meaning is defined by, and whose value comes from, the provider
  under test.

### Claim 4: The TTS → STT round trip is a **manual two-config pipeline joined by a filesystem handoff** — `saveAudio: true` + `audioOutputPath: audio` writes a file on a `--no-cache` run, the operator copies it, and a second config consumes it through an `audioFile` variable
- **Evidence**: Part 3 Step 6 runs `promptfoo eval -c transcription-test.yaml
  --no-cache` to emit `audio/tts-<timestamp>.mp3`, instructs copying it to
  `audio/generated-speech.mp3`, then defines `stt-accuracy.yaml` whose prompt
  is `'{{audioFile}}'` with `audioFile: audio/generated-speech.mp3`.
- **Confidence**: settled (documented procedure, verbatim)
- **Quote**: "Run `promptfoo eval -c transcription-test.yaml --no-cache` to
  save `audio/tts-<timestamp>.mp3`, then copy the generated file to
  `audio/generated-speech.mp3`. Add STT to verify accuracy in a second
  config, `stt-accuracy.yaml`:"
- **Our assessment**: A **chained eval with no chaining primitive** — the
  "pipeline" is two independent runs and a `cp`. That is fine for a
  tutorial and reproducible for a human, but it is an operational fact: to
  run this in CI you must script the timestamped-file discovery and copy,
  because the child config hard-codes a filename the parent emits with a
  timestamp. The `--no-cache` requirement is explicit on the parent run —
  consistent with the sibling note's rule that budget/latency-sensitive
  stages must opt out of the cache
  (`docs-promptfoo-deterministic-metrics.md` Claim 14). The page also
  confirms the corpus's separate "chain testing" material
  (`docs-promptfoo-testing-llm-chains.md`): promptfoo chains are assembled
  from files and vars, not a first-class DAG.

### Claim 5: Conversational-agent quality is **delegated to the provider's own weighted criteria** — `evaluationCriteria[]` with per-criterion `weight` and `passingThreshold` — and the eval asserts on `metadata.evaluationResults` in custom JS, so promptfoo never applies its own scoring model to the criteria
- **Evidence**: Part 4's `agentConfig` block defines five criteria
  (`greeting` w0.8/th0.8, `information_gathering` w1.0/th0.9, `empathy`
  w0.9/th0.7, `next_steps` w1.0/th0.9, `professionalism` w0.8/th0.8); the
  test asserts `metadata.evaluationResults` via a `required` subset.
- **Confidence**: settled (documented config, verbatim)
- **Quote**:
  ```
  const results = context.providerResponse.metadata?.evaluationResults;
  const required = ['information_gathering', 'next_steps', 'professionalism'];
  return Array.isArray(results) && required.every(id =>
    results.some(result => result.criterion === id && result.passed === true)
  );
  ```
- **Our assessment**: A sharp boundary point for the guide. The
  `weight`/`passingThreshold` fields here are **ElevenLabs-agent semantics
  surfaced in metadata**, *not* promptfoo's weighted-average-plus-threshold
  gate (`docs-promptfoo-assertions-metrics.md` Claim 1) — so Ch05's
  "read the assert's own defaults" and "a gate that cannot fail" material
  does not govern this verdict. The pass/fail is computed *inside the
  provider*; promptfoo sees only the result array. Also note the worked
  example gates on **three of five** criteria, so a five-criteria rubric can
  be gated on a chosen critical subset — the same "not every criterion must
  pass" shape as `assert-set` thresholds (Claim 5 there), but expressed
  provider-side.

### Claim 6: `maxTurns` limits **newly simulated turns excluding the supplied history**, while the returned `conversationHistory` **includes** the supplied turns — so any turn-count assertion on the history is off by the supplied turn count
- **Evidence**: The `maxTurns: 8` config comment and the explanatory
  sentence printed directly under the `agent-test.yaml` block.
- **Confidence**: settled (documented behavior, stated outright)
- **Quote**: "maxTurns limits newly simulated turns. The returned
  conversation history can also include the supplied turns." — with the
  config comment "# Limit newly simulated turns, excluding the supplied
  conversation history"
- **Our assessment**: A concrete, documented counting trap, and the sibling
  of the corpus's conversation-history hazards
  (`docs-promptfoo-chat-threads.md` Claim 3 — later turns are built from the
  model's own earlier outputs; Claim 5 — history grouping is opt-in). The
  rule this implies: never assert on `history.length` as a proxy for turns
  simulated under `maxTurns`; count only the newly simulated turns, or gate
  on a criterion instead. The page supplies the exact wording that makes the
  discrepancy reviewable.

### Claim 7: `toolMockConfig` stubs a named tool's return value — `order_lookup` returns `{order_number, status, tracking_number}` — enabling a **deterministic, side-effect-free agent tool trajectory**, with the eval verifying the mock indirectly through provider criteria (`uses_tool`, `provides_tracking`)
- **Evidence**: Part 5 Step 9 targets an existing agent (`agentId:`) and
  mocks `order_lookup`'s response under `toolMockConfig.returnValue`, then
  asserts two criteria requiring the agent to call the tool and surface the
  mocked tracking number.
- **Confidence**: settled (documented config, verbatim)
- **Quote**: "Use an existing ElevenLabs agent configured with an
  `order_lookup` tool that accepts an `order_number` string. Set its ID in
  `agentId` below; this example mocks that tool's response." — with the
  config comment "# Mock tool responses for testing"
- **Our assessment**: **First corpus source on tool mocking for evals** —
  distinct from the corpus's two adjacent surfaces: the tool-*definition*
  notes (`docs-promptfoo-configuration-tools.md` Claim 1: tool calling is a
  loop where the model emits a name/arguments and "the harness ... is the
  thing that runs code") and the coding-agent notes where tools run for real
  (`docs-promptfoo-evaluate-coding-agents.md`). This is the third leg of the
  tool-testing story: **do not run the tool, stub its result**, so the
  trajectory is testable without a live order database and without the
  nondeterminism of a real backend. Note the verification is *indirect*:
  the page asserts the agent *claimed* to use the tool and *stated* the
  mocked tracking number via natural-language criteria, **not** a direct
  tool-call assertion such as the `trajectory:tool-used` /
  `trajectory:tool-args-match` family
  (`docs-promptfoo-deterministic-metrics.md` Claims 10-11). A stronger gate
  would pair this mock with those assertions; the page's own `agentId`-based
  design leaves the mock unverified at the call level.

### Claim 8: The eval harness can **provision its own agent target** — `agentConfig` with `name`, `prompt`, `voiceId`, and `llmModel` creates an ephemeral agent for testing, versus `agentId` to point at an existing one
- **Evidence**: Part 4's `agentConfig` block is headed by the comment
  "# Create an ephemeral agent for testing"; Part 5's config instead sets
  `agentId: your-agent-id-with-order-lookup` for a pre-existing agent.
- **Confidence**: settled (documented config, verbatim)
- **Quote**: "# Create an ephemeral agent for testing" (the Part 4
  `agentConfig` comment), contrasted with Part 5's "Set its ID in
  `agentId` below"
- **Our assessment**: A test-isolation pattern worth naming for Ch03: the
  eval creates a throwaway target so runs do not mutate a shared agent, then
  tears it down. Two operational consequences the page does not state:
  provisioning an agent is a **provider-side side effect** (and a cost), and
  an ephemeral agent drifts from the production agent whose behavior you
  actually care about — the same "test in the environment you ship"
  conditioning variable as Ch05's staging guidance.

### Claim 9: The page asserts **nothing about voice quality** — voice settings (`stability`, `similarity_boost`, `style`, `speed`) are provider knobs, the only audio assertion is presence-check, and the page routes quality judgment back to **human listening** in the web UI
- **Evidence**: Part 2 sets three `voiceSettings` profiles but its tests only
  check audio presence, latency, and cost; Step 4 says "Open the web UI to
  listen to the audio"; the troubleshooting bullet for audio quality is
  "Adjust voice settings (stability, similarity_boost)".
- **Confidence**: settled (the absence is observable across the page; the
  vendor's own recommended quality check is human listening)
- **Quote**: "Open the web UI to listen to the audio:" and "Adjust voice
  settings (stability, similarity_boost)"
- **Our assessment**: An important scope discipline so the guide does not
  over-claim. The page's title is "quality testing," but the automated gates
  measure **envelope** (latency, cost, presence) and **transcription
  fidelity** (WER) — never tone, pacing, or naturalness. Voice quality is
  evaluated by a human ear in the UI. If the guide ever wants an automated
  *voice-quality* gate it must reach for the model-graded audio path
  (`docs-promptfoo-llm-rubric.md` Claims 1-3), not this page — and that path
  has its own silent-degradation trap (`transform` drops the audio).

### Claim 10: The page offers **no CI/CD merge gate** — "Regression testing" and "Production monitoring" appear only as Next-Steps bullets, with no pipeline, merge-gating example, alerting, or SLO content
- **Evidence**: The "Explore More" list's three bullets and the absence of
  any CI/runbook section across all nine steps.
- **Confidence**: settled (absence, consistent with the Prospector's caveat)
- **Quote**: "**Regression testing**: Track agent performance over time" and
  "**Production monitoring**: Set up continuous testing"
- **Our assessment**: Per the triage guidance, mine this as **provider-eval
  methodology, not operational doctrine**. The page teaches how to *define*
  the gates; it makes no claim about *wiring* them into a release process.
  A guide citing this source for a CI gate would be extrapolating beyond the
  source. Contrast with the corpus's actual CI-bridge material
  (`docs-promptfoo-configuration-outputs.md` — JUnit XML, exit codes).

### Claim 11: The page's **cost-control guidance** for agent evals — use `gpt-5-mini` instead of `gpt-5`, enable caching, implement LLM cascading, test with shorter prompts — sits in **tension with the `--no-cache` requirement** its own latency/cost gates and STT pipeline impose
- **Evidence**: The "High costs during testing" troubleshooting bullets, read
  against Step 6's explicit `--no-cache` and the latency/cost assertions of
  Claims 1 and 5.
- **Confidence**: settled that both pieces of guidance are on the page; the
  tension is the Miner's reading of two contexts, not a vendor-stated
  conflict
- **Quote**: "Use `gpt-5-mini` instead of `gpt-5`", "Enable caching for
  repeated tests", "Implement LLM cascading", "Test with shorter prompts
  first"
- **Our assessment**: The agent's own `llmModel` is a first-class **cost
  dial** for an agent eval, and this is a cheap-model recommendation for the
  *simulator under test* (not just the judge). The caveat is real though:
  "enable caching" saves money on repeated runs but contradicts the
  `--no-cache` needed for a meaningful `latency`/`cost` verdict — a cached
  run measures replay (`docs-promptfoo-deterministic-metrics.md` Claims 6,
  14). The page never reconciles the two. I treat this as a
  **context-conditioned** pair (cache to *save* on smoke iterations;
  `--no-cache` to *measure* a budget gate), not a filed contradiction — the
  existing budget-cache coupling is already documented and filing a second
  contradiction would duplicate it. Worth a one-line warning in Ch05: do not
  enable caching on the suite whose latency/cost gate you trust.

### Claim 12: ElevenLabs voice IDs must be real IDs — **display names such as `rachel` are not resolved** — and the page's example uses a placeholder ID the reader must replace
- **Evidence**: Step 2's note about replacing the example voice ID, linked to
  the ElevenLabs voice list.
- **Confidence**: settled (documented behavior, stated outright)
- **Quote**: "Display names such as `rachel` are not resolved to IDs"
- **Our assessment**: A small but concrete config footgun in the same family
  as the corpus's other "identifier must be exact" traps (e.g. the
  deterministic note's metric-name-typo-to-0, `docs-promptfoo-assertions-metrics.md`
  Claim 7). It matters to a gate because a voice mismatch silently changes
  what was tested, not whether the eval ran.

## Concrete Artifacts

All artifacts copied character-for-character from
https://www.promptfoo.dev/docs/guides/evaluate-elevenlabs (the section each
comes from is named). The source page's code blocks arrive as token streams
after HTML extraction; line breaks were restored at YAML/program boundaries
only — no wording, values, or comments were changed.

### TTS latency/cost gate (verbatim from Part 1, Step 2)

```yaml
description: 'Compare ElevenLabs TTS models for customer service greetings'
prompts:
  - "Thank you for calling TechSupport Inc. My name is Alex, and I'll be assisting you today. How can I help?"
providers:
  - label: Flash Model (Fastest)
    id: elevenlabs:tts:21m00Tcm4TlvDq8ikWAM
    config:
      modelId: eleven_flash_v2_5
      outputFormat: mp3_44100_128
  - label: Turbo Model (Legacy Comparison)
    id: elevenlabs:tts:21m00Tcm4TlvDq8ikWAM
    config:
      modelId: eleven_turbo_v2_5
      outputFormat: mp3_44100_128
tests:
  - description: Both models complete within 3 seconds
    assert:
      - type: latency
        threshold: 3000
  - description: Cost is under $0.01 per greeting
    assert:
      - type: cost
        threshold: 0.01
```

### Voice-settings profiles and the audio-presence check (verbatim from Part 2, Step 5; profiles abbreviated)

```yaml
providers:
  - label: Professional Voice
    id: elevenlabs:tts:21m00Tcm4TlvDq8ikWAM
    config:
      modelId: eleven_flash_v2_5
      voiceSettings:
        stability: 0.8 # Consistent tone
        similarity_boost: 0.85
        speed: 0.95
  - label: Friendly Voice
    id: elevenlabs:tts:21m00Tcm4TlvDq8ikWAM
    config:
      modelId: eleven_flash_v2_5
      voiceSettings:
        stability: 0.4 # More variation
        similarity_boost: 0.75
        speed: 1.1 # Slightly faster
  - label: Empathetic Voice
    id: elevenlabs:tts:21m00Tcm4TlvDq8ikWAM
    config:
      modelId: eleven_flash_v2_5
      voiceSettings:
        stability: 0.5
        similarity_boost: 0.7
        style: 0.8 # More expressive
        speed: 0.9 # Slower, calmer
tests:
  - vars:
      scenario: formal
    assert:
      - type: javascript
        value: |
          const audio = context.providerResponse.audio;
          return Boolean(audio?.data || audio?.blobRef);
  - vars:
      scenario: casual
    assert:
      - type: latency
        threshold: 2000
  - vars:
      scenario: empathy
    assert:
      - type: cost
        threshold: 0.01
```

### TTS → STT pipeline, stage 1 — generate audio (verbatim from Part 3, Step 6, `transcription-test.yaml`)

```yaml
description: 'Test TTS → STT accuracy pipeline'
prompts:
  - |
    The quarterly sales meeting is scheduled for Thursday, March 15th at 2:30 PM.
    Please bring your laptop, quarterly reports, and the Q4 projections spreadsheet.
    Conference room B has been reserved for this meeting.
providers:
  # Step 1: Generate audio
  - label: tts-generator
    id: elevenlabs:tts:21m00Tcm4TlvDq8ikWAM
    config:
      modelId: eleven_flash_v2_5
      saveAudio: true
      audioOutputPath: audio
tests:
  - description: Generate audio and verify quality
    assert:
      - type: javascript
        value: |
          // Verify audio was generated
          const audio = context.providerResponse.audio;
          return Boolean(audio?.data || audio?.blobRef);
```

### TTS → STT pipeline, stage 2 — WER gate (verbatim from Part 3, Step 6, `stt-accuracy.yaml`)

```yaml
description: 'Test STT accuracy'
prompts:
  - '{{audioFile}}'
providers:
  - id: elevenlabs:stt
    config:
      modelId: scribe_v2
      calculateWER: true
      referenceText: 'The quarterly sales meeting is scheduled for Thursday, March 15th at 2:30 PM. Please bring your laptop, quarterly reports, and the Q4 projections spreadsheet. Conference room B has been reserved for this meeting.'
tests:
  - vars:
      audioFile: audio/generated-speech.mp3 # File path from the previous eval
    assert:
      - type: javascript
        value: |
          // Transcription text is output; WER is in response metadata.
          const wer = context.providerResponse.metadata?.wer?.wer;
          return typeof wer === 'number' && wer < 0.05;
```

### Conversational-agent criteria and metadata assertion (verbatim from Part 4, Step 7, `agent-test.yaml`; `prompt` and some criteria abbreviated)

```yaml
providers:
  - id: elevenlabs:agents
    config:
      # Create an ephemeral agent for testing
      agentConfig:
        name: Support Agent
        prompt: |
          You are a helpful customer support agent for TechCorp.
          ...
        voiceId: 21m00Tcm4TlvDq8ikWAM # Rachel
        llmModel: gpt-5-mini
      # Define evaluation criteria
      evaluationCriteria:
        - id: greeting
          name: greeting
          description: Agent greets the user warmly
          weight: 0.8
          passingThreshold: 0.8
        - id: information_gathering
          name: information_gathering
          description: Agent asks for email or account details
          weight: 1.0
          passingThreshold: 0.9
        - id: empathy
          name: empathy
          description: Agent acknowledges user frustration
          weight: 0.9
          passingThreshold: 0.7
        - id: next_steps
          name: next_steps
          description: Agent provides clear next steps
          weight: 1.0
          passingThreshold: 0.9
        - id: professionalism
          name: professionalism
          description: Agent maintains professional tone
          weight: 0.8
          passingThreshold: 0.8
      # Limit newly simulated turns, excluding the supplied conversation history
      maxTurns: 8
      timeout: 60000
tests:
  - description: Agent passes all critical evaluation criteria
    assert:
      - type: javascript
        value: |
          const results = context.providerResponse.metadata?.evaluationResults;
          const required = ['information_gathering', 'next_steps', 'professionalism'];
          return Array.isArray(results) && required.every(id =>
            results.some(result => result.criterion === id && result.passed === true)
          );
  - description: Agent returns a conversation history
    assert:
      - type: javascript
        value: |
          const history = context.providerResponse.metadata?.conversationHistory;
          return Array.isArray(history) && history.length > 0;
  - description: Agent responds within reasonable time
    assert:
      - type: latency
        threshold: 60000
```

### Tool mocking (verbatim from Part 5, Step 9, `agent-with-tools.yaml`)

```yaml
providers:
  - id: elevenlabs:agents
    config:
      agentId: your-agent-id-with-order-lookup
      # Mock tool responses for testing
      toolMockConfig:
        order_lookup:
          returnValue:
            order_number: 'ORDER-12345'
            status: 'Shipped'
            tracking_number: '1Z999AA10123456784'
      evaluationCriteria:
        - id: uses_tool
          name: uses_tool
          description: Agent calls order_lookup for ORDER-12345.
          weight: 1.0
          passingThreshold: 0.9
        - id: provides_tracking
          name: provides_tracking
          description: Agent tells the user that tracking number is 1Z999AA10123456784.
          weight: 1.0
          passingThreshold: 0.9
tests:
  - description: Agent successfully looks up order
    assert:
      - type: javascript
        value: |
          const results = context.providerResponse.metadata?.evaluationResults;
          const required = ['uses_tool', 'provides_tracking'];
          return Array.isArray(results) && required.every(id =>
            results.some(result => result.criterion === id && result.passed === true)
          );
```

### Troubleshooting: cost and timeouts (verbatim bullets from "Common Issues")

```
Agent conversations timeout:
- Increase maxTurns and timeout in config
- Simplify evaluation criteria
- Use faster LLM models

High costs during testing:
- Use gpt-5-mini instead of gpt-5
- Enable caching for repeated tests
- Implement LLM cascading
- Test with shorter prompts first

Evaluation criteria always failing:
- Start with simple, objective criteria
- Lower passing thresholds during development
- Review agent transcript to understand behavior
- Add more specific criteria descriptions

Audio quality issues:
- Try different outputFormat settings
- Adjust voice settings (stability, similarity_boost)
- Test with different models
- Compare eleven_multilingual_v2 with Flash for your speech-quality requirements
```

Source for all artifacts:
https://www.promptfoo.dev/docs/guides/evaluate-elevenlabs — sections as
noted.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 6** (the
    `cost` assertion can only gate provider-reported cost, and fresh-cost
    gating requires `--no-cache`) and **Claim 14** (`latency` "requires that
    the cache is disabled"). This page's `latency`/`cost` gates (Claim 1) are
    an applied instance of those two assertions over a new provider type; the
    cache coupling is cited, not re-derived. (Verified: #1289 Claims 6, 14.)
  - `source-notes/docs-promptfoo-javascript-assertions.md` **Claim 5** (the
    `AssertionValueFunctionContext` surface, which includes `providerResponse`
    and `metadata`). Every custom assertion on this page reads
    `context.providerResponse.audio` (Claim 2) or
    `context.providerResponse.metadata.*` (Claims 3, 5, 6) — the exact fields
    that note enumerates. (Verified: #1304 Claim 5.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 10** (the
    deterministic/programmatic vs model-assisted boundary). This page's WER
    gate (Claim 3) is a programmatic metric; its agent criteria (Claim 5) are
    provider-computed and sit outside promptfoo's own catalogue, a boundary
    case that note's two-family split does not cover. (Verified: #1287
    Claim 10.)
  - `source-notes/docs-promptfoo-chat-threads.md` **Claim 3** (later turns are
    built from the model's own earlier outputs, so a degraded prior turn
    cascades) and **Claim 5** (history grouping is opt-in per
    `conversationId`). This page's supplied-conversation-history agent config
    and its `maxTurns`/`conversationHistory` discrepancy (Claim 6) are the
    same "history is data you must account for" family. (Verified: #1276
    Claims 3, 5.)
  - `source-notes/docs-litellm-audio-transcription.md` **Claim 1**
    (`mock_testing_fallbacks` is stripped from Proxy requests so synthetic
    fallback tests "exercise nothing"). Both this page and that note treat a
    **test-only mock** as a first-class surface: the LiteLLM note documents a
    mock silently ceasing to work, this page documents a mock
    (`toolMockConfig`) that works — the two together bound "a mock is only as
    good as its written-through-ness." (Verified: #1401 Claim 1.)

- **Contradicts**: None filed, and no contradiction issue opened. Checked
  against `CONTRADICTIONS.md` (no `C-NNN` entries) and the open
  `contradiction`-labeled issues. Two candidate tensions were assessed per
  MINER.md §4a and both are **context-conditioned, not opposing**:
  1. **In-page cache tension** — the troubleshooting section advises
     "Enable caching for repeated tests" while the latency/cost gates and the
     STT pipeline require `--no-cache` (Claim 11). This is the
     save-on-smoke-iterations vs measure-a-gate distinction, and the
     underlying budget/cache coupling is already documented in
     #1289 Claims 6/14; filing would duplicate existing coverage.
  2. **Blob-reference handling** — this page's presence check treats
     `audio.blobRef` as valid audio (Claim 2) while
     `docs-promptfoo-llm-rubric.md` **Claim 2** says blob references produce
     a *grading error* for the audio judge. These are two different
     operations (presence vs gradeability), so they complement rather than
     conflict.

- **Extends**:
  - `source-notes/docs-promptfoo-llm-rubric.md` **Claim 1** (the first
    non-text judge input surface — the target's `response.audio` attached to
    the grading request) and **Claim 3** (`transform` silently drops the
    audio so the judge grades text while the rubric names audio). This page
    is the **pre-judge, deterministic** half of voice evaluation: where
    `llm-rubric` grades *quality* with a model, this page gates *envelope*
    (latency/cost) and *transcription fidelity* (WER). Together they cover
    both the judge and non-judge options for an audio artifact, and the
    `llm-rubric` note's silent-degradation trap is the reason a voice-quality
    gate (which this page does not provide, Claim 9) must be configured
    carefully. (Verified: #1471 Claims 1, 3.)
  - `source-notes/docs-promptfoo-evaluate-coding-agents.md` **Claim 7** ("the
    path, not just the output, is assertable" — `trajectory:step-count`,
    `trajectory:tool-used`, `trajectory:tool-sequence`) and **Claim 10**
    (regression gates are cost/latency thresholds plus `--no-cache` and
    `--repeat 3`). This page's tool-mocking pattern (Claim 7) is the
    deterministic *input* side of trajectory testing that note's
    assertions verify on the *output* side; and its `latency: 60000` agent
    gate is a cost/latency release threshold in the same family. (Verified:
    the coding-agents note's Claims 7 and 10.)
  - `source-notes/docs-promptfoo-configuration-tools.md` **Claim 1** (tool
    calling is a loop where the model emits a name/arguments and executes
    nothing; the harness runs code). `toolMockConfig` (Claim 7 here) is what
    you substitute at the "harness runs the tool" step for a test — the
    mocking counterpart to that note's definition/translation surface.
    (Verified: docs-promptfoo-configuration-tools Claim 1.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 5**
    (`assert-set` groups assertions under one pass condition with its own
    threshold). The page's per-criterion `passingThreshold` set (Claim 5
    here) is a provider-side analogue of partial-pass gating — same idea
    (gate on a subset/threshold rather than all), different implementation
    location. (Verified: #1287 Claim 5.)

- **Novel**: First corpus coverage of **voice / TTS / STT / audio-provider
  evaluation**. Specifically new:
  1. **Numeric-envelope gating for a non-text modality** (Claim 1) —
     latency and cost as the substitution for string matching.
  2. **A provider-computed WER quality gate** (Claim 3) — the corpus's first
     worked non-text *quality* metric with an explicit unit and threshold,
     and its first example of a **vendor-reported metric** as a gate input
     (distinct from the deterministic-local and judge-graded categories).
  3. **Audio presence via custom JS** over
     `context.providerResponse.audio` (`data`/`blobRef`), with no declarative
     audio assertion type (Claim 2).
  4. **A filesystem-handoff TTS → STT chain** with no chaining primitive
     (Claim 4).
  5. **Provider-side weighted `evaluationCriteria` with per-criterion
     `passingThreshold`**, asserted through `metadata.evaluationResults`
     (Claim 5).
  6. **The `maxTurns`-excludes-history vs `conversationHistory`-includes-it
     trap** (Claim 6).
  7. **`toolMockConfig`** — the corpus's first tool-mocking surface (Claim 7).
  8. **Ephemeral in-config agent provisioning** (`agentConfig`) as an eval
     target (Claim 8).

  Not novel (deliberately not re-extracted): the latency/cost assertion
  mechanics and their cache coupling (#1289 Claims 6/14); the
  `context.providerResponse` field surface (#1304 Claim 5).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — "Metrics without a unit are noise"
  (`guide/05-llm-ops-reliability.md:388`)**: add a non-text worked example.
  Where the section currently defines ASR's unit (attempt budget K), this
  source shows the alternative for a modality with no text to compare: gate
  the envelope (`latency`, `cost`) and a **defined error metric** — "Test STT
  accuracy with WER calculation" gated at `wer < 0.05` [source:
  docs-promptfoo-evaluate-elevenlabs, Claim 3]. State the vendor-reported-
  metric caveat: the number comes from the provider under test, so its trust
  is the provider's, unlike a client-side string check.
- **Chapter 05 — "A gate that cannot fail is not a gate"
  (`guide/05-llm-ops-reliability.md:655`)**: add a row for audio/voice
  suites — the only built-in check this page shows for generated audio is a
  **custom JS presence test** over `providerResponse.audio`, and the page
  asserts **nothing** about tone/pacing/naturalness (Claim 9); quality is
  judged by a human "listen in the web UI." Rule to state: on a non-text
  modality, "the artifact exists" and "the artifact is good" are separate
  assertions, and a presence check is not a quality gate. Do **not** cite
  this page for an automated voice-quality gate — that requires the
  model-graded audio path (`docs-promptfoo-llm-rubric.md`) with its own
  `transform` trap.
- **Chapter 05 — "Multi-turn evals serialize, and their failures do not
  localise" (`guide/05-llm-ops-reliability.md:610`)**: add the turn-count
  trap — `maxTurns` "limits newly simulated turns" while the returned
  "conversation history can also include the supplied turns"
  [source: docs-promptfoo-evaluate-elevenlabs, Claim 6] — so a
  `history.length` assertion over-counts by the supplied turns. This extends
  the section's existing history-composition hazards
  (`docs-promptfoo-chat-threads`, Claims 3, 5).
- **Chapter 05 — "Grade the route, not just the reply"
  (`guide/05-llm-ops-reliability.md:742`)**: add **tool mocking** as the
  deterministic-input complement to the trajectory assertions. The
  trajectory family verifies the route *after the fact* from span data; this
  source shows how to make the route reproducible in the first place by
  stubbing the tool's return value — `toolMockConfig: order_lookup:
  returnValue: {...}` [source: docs-promptfoo-evaluate-elevenlabs, Claim 7].
  Note the page verifies the mock **indirectly** through natural-language
  criteria (`uses_tool`, `provides_tracking`), so a stronger gate pairs the
  mock with a direct `trajectory:tool-used` / `trajectory:tool-args-match`
  assertion (`docs-promptfoo-deterministic-metrics`, Claims 10-11).
- **Chapter 03 (Runbooks and Agents) — "Agent evaluation in production"
  (`guide/03-runbooks-and-agents.md:268`)**: the ephemeral-agent pattern
  (`agentConfig` creates a throwaway target per run, vs `agentId` for an
  existing one, Claim 8) belongs with the section's "evaluate the trajectory
  before it acts" material — it is how you get an isolated, side-effect-free
  target. Also carry the cost dial: the agent's own `llmModel` is part of the
  eval budget (the page recommends `gpt-5-mini` over `gpt-5`, Claim 11), so
  the simulator model is a release-cost variable, not only the judge model.
- **Chapter 05 — eval cost budgeting (near the "Evaluation and measurement
  methodology" material)**: add the cost-cache warning from Claim 11 — do
  not enable caching on the suite whose `latency`/`cost` gate you trust, since
  a cached run measures replay (`docs-promptfoo-deterministic-metrics`,
  Claims 6, 14). The page's "enable caching for repeated tests" advice and its
  own `--no-cache` gates are the two contexts the guide must keep separate.

## Extraction Notes

- Source read in full: the rendered page was fetched over HTTP, converted to
  text, and every prose passage and code block used above was checked
  character-for-character against that extraction. The page's code blocks
  arrive as token streams (each YAML key/value on its own line) after HTML
  extraction; they were reassembled into YAML with line breaks restored at
  key/value boundaries only — no values, comments, or IDs were altered. The
  Part 4 `prompt` block was abbreviated (marked `...`) purely to keep the
  Concrete Artifacts readable; nothing else was abridged.
- **Delta over existing corpus**, per the Prospector's "mine the transferable
  metric-definition pattern; do not inflate the tutorial into an ops claim it
  does not make": the note leads with the metric-definition mechanics (WER
  gate, provider criteria, `maxTurns` trap, tool mocking) and explicitly
  records that the page has **no CI/CD pipeline, no merge gate, and no
  alerting** (Claim 10) and **no automated voice-quality metric** (Claim 9).
  The latency/cost/cache coupling was **not** re-extracted — it is cited to
  #1289 Claims 6/14.
- The page's provider IDs (`elevenlabs:tts`, `elevenlabs:stt`,
  `elevenlabs:agents`), model IDs (`eleven_flash_v2_5`,
  `eleven_turbo_v2_5`, `scribe_v2`), and voice ID
  (`21m00Tcm4TlvDq8ikWAM`) are ElevenLabs-specific and are treated as
  illustrative config, not vendor-independent claims. The
  "Turbo is retained here for comparison; ElevenLabs recommends Flash over
  Turbo for new configurations" sentence is the page relaying ElevenLabs's
  own deprecation guidance; it is recorded in the TTS artifact context but
  not elevated to a claim because it is a provider-model recommendation, not
  an eval-mechanics finding.
- **Candidate handling** (from `miner-related-notes.md`, read before writing
  Cross-References; candidates are suggestions only — each cited or dismissed
  by name; the file was not committed):
  1. `docs-promptfoo-enterprise-guardrails.md` — runtime guardrail
     enforcement/placement; no eval-provider or modality-gating surface;
     **dismissed**.
  2. `docs-promptfoo-enterprise-findings-reports.md` — red-team finding
     disposition and export formats; no eval or provider surface;
     **dismissed**.
  3. `docs-google-sre-reliable-product-launches.md` — Google launch-process
     chapter; no LLM-eval content; **dismissed**.
  4. `docs-litellm-batches-api.md` — batch request/rate-limit accounting; no
     eval modality or provider-gating content; **dismissed**.
  5. `blog-pagerduty-sre-agent-triage.md` — LLM-as-judge incident triage; no
     eval-provider configuration surface; **dismissed**.
  6. `docs-promptfoo-llm-rubric.md` — **cited** (Extends, Claims 1 and 3;
     Contradicts discussion): the corpus's other audio surface (the
     model-graded audio input and its `transform` degradation) — the
     judge-side counterpart to this page's deterministic gates.
  7. `docs-langfuse-mcp-server.md` — Langfuse docs MCP server; unrelated
     vendor; **dismissed**.
  8. `docs-google-sre-team-lifecycles.md` — SRE org/hiring chapter;
     **dismissed**.
  9. `docs-google-sre-prodcast-04-05-furino-slos.md` — SLO fundamentals
     podcast; no eval-provider surface; **dismissed**.
  10. `docs-promptfoo-evaluate-coding-agents.md` — **cited** (Extends, Claims
      7 and 10, verified): the coding-agent eval note whose trajectory
      assertions and cost/latency regression gates this page's tool mocking
      and agent-latency gate complement.
  Additional cross-references found by searching `source-notes/` directly
  (not in the candidate list), each verified per MINER.md §4b by re-reading
  the cited note and locating the claim:
  `docs-promptfoo-deterministic-metrics.md` (Claims 6, 14; Claims 10-11 in
  the tool-assertion discussion), `docs-promptfoo-javascript-assertions.md`
  (Claim 5), `docs-promptfoo-assertions-metrics.md` (Claims 5, 10),
  `docs-promptfoo-chat-threads.md` (Claims 3, 5),
  `docs-promptfoo-configuration-tools.md` (Claim 1),
  `docs-litellm-audio-transcription.md` (Claim 1). Also checked and not
  cited: `docs-promptfoo-configuration-outputs.md` (its
  `providerResponse.metadata`/export material is about result serialization,
  not eval-provider gating; the triage's note that it "dismissed" an
  audio-grading contract is about the judge path already carried by
  `docs-promptfoo-llm-rubric.md`) and `docs-promptfoo-answer-relevance.md`
  (embedding-backed relevance; no audio/provider surface).
- **Cross-ref verification (§4b)**: every cited claim number was located in
  the cited note before writing — #1289 Claims 6, 14 (and 10-11 in
  discussion); #1304 Claim 5; #1287 Claims 5, 10; #1276 Claims 3, 5;
  `docs-litellm-audio-transcription` Claim 1; `docs-promptfoo-llm-rubric`
  Claims 1, 3; `docs-promptfoo-configuration-tools` Claim 1. Each claim's
  content was checked against what it is cited for. No claim numbers invented
  and no quotes attributed to other notes.
- **No contradiction issue filed**: verified against `CONTRADICTIONS.md` (no
  `C-NNN` entries) and the open `contradiction`-labeled issues. The two
  candidate tensions (in-page cache advice vs `--no-cache`; `blobRef`
  presence vs grading error) were assessed per MINER.md §4a and both are
  context-conditioned, not real contradictions (details in Cross-References).
- `confidence_overall` is `emerging`, matching the sibling promptfoo config
  notes (#1287, #1289, #1304, #1471): the config mechanics and IDs are
  settled-for-product-behavior and checkable against an installed CLI and the
  ElevenLabs API, but this is vendor documentation with **no measured WER,
  latency, cost, or judge-agreement figures**, an illustrative result table,
  and no independent practitioner validation — the framing (vendor-reported
  metric trust, presence-vs-quality, the tool-mock verification gap) is the
  Miner's analysis on top of documented behavior.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.
